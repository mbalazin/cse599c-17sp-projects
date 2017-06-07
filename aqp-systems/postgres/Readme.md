# How well can POSTGRES handle approximate queries?
[POSTGRES](https://www.postgresql.org/) is an open source database that has been developed and maintained both by industry and academia for the last two decades. From release 9.5, postgres started supporting sampling in order to enable approximate query processing. There is a huge body of work in the database community relating to estimation of query results from a sample of the database. 

## Sampling Support
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
We see that skew does have more effect over queries with select predicates. The maximum error percentage is up to 3% from 1% for system sampling of 0.1 percentage. However, a system sampling of 1% or 5% which runs in (10-20s) will still provide an error percentage of 1%. Uniform data performs almost as good as in a query without select predicate i.e. within 1% error. 

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
***
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
