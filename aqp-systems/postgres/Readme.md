# How well can POSTGRES handle approximate queries?
[POSTGRES](https://www.postgresql.org/) is an open source database that has been developed and maintained both by industry and academia for the last two decades. From release 9.5, postgres started supporting sampling in order to enable approximate query processing. There is a huge body of work in the database community relating to estimation of query results from a sample of the database. 

## Support for Approxiate Query Processing
Postgres supports two simple sampling techniques, namely **bernoulli** and **system** sampling. In Bernoulli sampling, the complete relation is scanned and individual tuples are randomly chosen (imagine a coin flip). The key bottleneck here is that the even if the query runs on a sample of data, we pay the cost of scanning the whole relation once. In some cases, this in itself could be a heavy operation.  
  
To overcome this, postgres supports an additional form of sampling called system sampling. System sampling operates at the granularity of pages instead of tuples. A random number is generated for each physical page in a relation. Based on this number and the sampling percentage specified it is either included or excluded from the sample. If a page is included, all tuples that occur in that physical page is included in the sample.  

The syntax to sample from a relation in postgres is very simple. The relation name contains additional `TABLESAMPLE` clause that specifies the sampling technique (`BERNOULLI` or `SYSTEM`) and sampling percentage. Here is an example aggregate query on a sample of the `LINEITEM` table from TPC-H benchmark.

```sql
SELECT COUNT(*) AS CNT 
FROM LINEITEM TABLESAMPLE BERNOULLI(0.1);
```
Additionally, postgres admits a `REPEATABLE` clause that specifies a seed for the random generator used in sampling. This enables the user to obtain the same sample from the table, which is important for some queries that are required to be *repeatable*. Following is the syntax for repeatable sampling:

```sql
SELECT COUNT(*) AS CNT 
FROM LINEITEM TABLESAMPLE BERNOULLI(0.1) REPEATABLE(200);
```

For further details on the `TABLESAMPLE` feature implementation, refer the official documentation [page](https://wiki.postgresql.org/wiki/TABLESAMPLE_Implementation). 

## Theoretical Guarantees
A bernoulli sample of the database allows for unbiased estimates of 3 aggregate functions, namely `COUNT`, `SUM` and `AVERAGE`. If the size of the relation is *n*, sample size is *s* and aggregate functions computed from the sample are *count*, *sum* and *avg* then we can compute an estimate of these aggregates on the overall relation as follows:
* COUNT = *count* * *n* / *s*  
* SUM = *sum* * *n* / *s*
* AVERAGE = *average*
  
Further, the above estimators are said to be unbiased, which means that the expected value of the estimator is the exact value of the aggregate on the complete relation. 
  
On the other hand, similar estimates from a system sample of the relation does not come with any theoretical guarantees. In practice, system sampling is seen to yield quite good accuracy for slighly large sample sizes. However, skewed distributions (both in value and organization on disk) can increase estimation errors. 

## Experiments
In the rest of the report, we aim to compare the features that postgres supports quantitatively and analyze the scope of approximate query processing that can be performed using just these standard features available to any user. 

### Experimental Setup
We perform all our experiments on Amazon AWS instances for purposes of interpretability and future extensibility. Specifically, we use a single node of `ic3.large` instance type. Following is a brief summary of the important configuration parameters of interest:

| Configuration | Value  | 
|---------------|:------:|
| vCPU          | 2      |
| Memory        | 15.25  |
| Storage       | 500GB SSD|

Further, we use the TPC-H benchmark to generate data. The data generator that is provided by TPCC generates a uniformly distributed data using a random generator. Aggregate estimates from samples drawn from a uniformly distributed data generally have low error rates. 
  
In cases where the population is skewed, the error rates can potentially shoot up. We perform all our experiments both on uniform and skewed data. We used the skewed TPC-H data generator made available [here](https://www.microsoft.com/en-us/download/details.aspx?id=52430) by Microsoft Research. The skew data generator uses a zipfian distribution with a user-specified value of theta. Higher the value of theta, more the skew in data. We use a skew parameter (theta) of 1. 
  
We generated 10GB and 100GB of uniform and skewed TPC-H relations and ingested them into postgres 9.5 on a single node AWS instance. 

| Data Size             | Ingestion Time  | 
|-----------------------|:---------------:|
| Skewed data (10GB)    | 9m 25s          |
| Uniform data (10GB)   | 8m 23s          |
| Skewed data (100GB)   | 99m 22s         |
| Uniform data (100GB)  | 100m 54s        |

All experiments below are performed 5 times and the results reported are mean, along with the standard deviations in our observations.

### Query 1
We start with a very simple aggregate query on the largest table `LINEITEM` in the TPC-H benchmark. We compute all the three aggregates `count`, `sum` and `average` that are supported by Bernoulli sampling. We present the error percentage in the estimate and the corresponding runtimes for both uniform and skewed data in the graphs below.

```sql 
SELECT COUNT(*) AS NUM_ITEMS, 
       SUM(L_QUANTITY) AS TOT_COST, 
       AVG(L_QUANTITY) AS AVG_QTY 
FROM LINEITEM;
```
![][q1-skewed] ![][q1-skewed-time]
![][q1-uniform] ![][q1-uniform-time]
  
Runtime profiles are similar for both skewed and uniform relations in each experiment, as we know that postgres does not do anything extra to handle skews. The exact query takes around 4-5 mins. Even the least accurate estimate from system sampling of 0.1% is within 1% error rate and that is encouraging. In essense, we can get an estimate within 1% error rate almost instantaneously even for a relation of 100GB. On the other hand, bernoulli sampling seems to provide much better accuracies but incurs a minimum of 1 min overhead to scan through the entire relation. We can also see that the error percentage in uniform is lesser than for skewed data, as expected. Please note that this difference can be higher with increasing skew. 

***
### Query 2
Now, we add a select predicate to our aggregate query. The main objective of this query is to understand how skew can affect such queries.

```sql
SELECT COUNT(*) AS NUM_ITEMS, 
       SUM(L_QUANTITY) AS TOT_COST, 
       AVG(L_QUANTITY) AS AVG_QTY 
FROM LINEITEM  
WHERE DATE_PART('month', L_RECEIPTDATE) = 8;
```
![][q2-skewed] ![][q2-skewed-time]
![][q2-uniform] ![][q2-uniform-time]
  
We see that skew does have more effect over queries with select predicates. The maximum error percentage is up to 3% from 1% for system sampling of 0.1 percentage. However, a system sampling of 1% or 5% will still provide an error percentage of 1% and runs in 10-20s. Uniform data performs almost as good as in a query without select predicate i.e. within 1% error. 

***
### Query 3
In query 3, we compute a group-by aggregate query on the `LINEITEM` 
```sql
SELECT DATE_PART('month', L_RECEIPTDATE) AS MONTH, 
       COUNT(*) AS NUM_ITEMS, 
       SUM(L_QUANTITY) AS TOT_QTY, 
       AVG(L_QUANTITY) AS AVG_QTY 
FROM LINEITEM  
GROUP BY MONTH 
ORDER BY MONTH;
```
![][q3-skewed] ![][q3-skewed-time]
![][q3-uniform] ![][q3-uniform-time]
  
In case of group-by aggregate, we report the maximum error percentage across groups. The results here are not much different from that of query 2. The exact query seems to take around 10 mins. So, a system sampling of 1% or 5% seems to be a great compromise in the erorr-vs-performance trade-off spectrum. 
*** 
### Query 4
Now, compute a group-by aggregate on the join of two tables. Note that we join a sample of `LINEITEM` with the complete `SUPPLIER` table. 

```sql
SELECT S_NATIONKEY AS NATION, 
       COUNT(*) AS NUM_ITEMS, 
       SUM(L_QUANTITY) AS TOT_QTY, 
       AVG(L_QUANTITY) AS AVG_QTY 
FROM LINEITEM, SUPPLIER 
WHERE L_SUPPKEY = S_SUPPKEY 
GROUP BY NATION 
ORDER BY NATION;
```
![][q4-skewed] ![][q4-skewed-time]
![][q4-uniform] ![][q4-uniform-time]
  
The key issue with sampling-based techniques is joins. We cannot join a sample of two tables especially because we cannot provide any guarantees about the hit-rate between tuples that match. There are more advanced forms of sampling that can handle this such as *universal sampling*, but postgres does not support them yet.
  
In this query, we join a sample of the `LINEITEM` table with the complete `SUPPLIER` table. Usually in star schemas, fact tables are joined with dimension tables and the dimension tables are smaller in size compared to fact tables. The observations here again are quite similar to above queries. 

***
### Query 5
Query 5, computes an aggregate over join of two tables along with a select predicate:
```sql
SELECT COUNT(*) AS NUM_ITEMS, 
       SUM(L_QUANTITY) AS TOT_QTY, 
       AVG(L_QUANTITY) AS AVG_QTY 
FROM LINEITEM , ORDER
WHERE L_ORDERKEY = O_ORDERKEY AND 
      O_ORDERPRIORITY = '1-URGENT';
```
![][q5-skewed] ![][q5-skewed-time]
![][q5-uniform] ![][q5-uniform-time]
  
Not much difference in observations here. One key issue to notice is that since there is a one-to-many map between `ORDER` and `LINEITEM`, we observe that a select predicate on `ORDER` table is not very much influenced by the skew and hence the error rates are better. Similarly, we observe that the runtime for this query is smaller than query 4, even though `ORDER` is much bigger than `SUPPLIER` : this is because the select predicate has been pushed down to the `ORDER` table before join and hence even for the exact query, the runtime is almost 0.5x. 

***
## Conclusion
On the whole, postgres is a very good choice for simple aggregates on single large tables. In case of selection conditions or group-by aggregates, it is better to increase the sampling percentage in order to contain the error percentage. System sampling seems to provide good error percentages (< 1%) with higher sampling percentages (like 5% or 10%) in most queries. Bernoulli sampling works is able to achieve it with as small as sample as 1% but incurs the additional overhead of complete relation scan. 
  
Support for queries on joins of tables is poor. Implementing a more advanced sampling technique such as universal sampling is a good step in that direction. 

## Results
Following are the links to Google Sheets that contain accuracy and runtime measurements for the above experiments. Each document contains multiple sheets, one for each of the above queries.

* [Skewed Benchmark Results](https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/edit?usp=sharing)
* [Uniform Benchmark Results](https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/edit?usp=sharing)

## Author Notes
The experiments and analysis was done by [Guna Prasaad](http://gunaprsd.github.io). Feel free to [mail](mailto:guna@cs.uw.edu) him for any further details. 

[q1-skewed]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-error-1.png
[q1-uniform]:https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-error-1.png
[q1-skewed-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-time-1.png
[q1-uniform-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-time-1.png

[q2-skewed]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-error-2.png
[q2-uniform]:https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-error-2.png
[q2-skewed-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-time-2.png
[q2-uniform-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-time-2.png

[q3-skewed]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-error-3.png
[q3-uniform]:https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-error-3.png
[q3-skewed-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-time-3.png
[q3-uniform-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-time-3.png

[q4-skewed]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-error-4.png
[q4-uniform]:https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-error-4.png
[q4-skewed-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-time-4.png
[q4-uniform-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-time-4.png

[q5-skewed]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-error-5.png
[q5-uniform]:https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-error-5.png
[q5-skewed-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/skewed-time-5.png
[q5-uniform-time]: https://github.com/mbalazin/cse599c-17sp-projects/raw/master/aqp-systems/postgres/plots/uniform-time-5.png
