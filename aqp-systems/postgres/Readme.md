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
*objectives*

### Experimental Setup
*aws instance types, etc.* 

### Query 1
```sql 
SELECT COUNT(*) AS NUM_ITEMS, 
       SUM(L_QUANTITY) AS TOT_COST, 
       AVG(L_QUANTITY) AS AVG_QTY 
FROM LINEITEM;
```
![][q1-skewed] ![][q1-skewed-time]
![][q1-uniform] ![][q1-uniform-time]
***
### Query 2
```sql
SELECT COUNT(*) AS NUM_ITEMS, 
       SUM(L_QUANTITY) AS TOT_COST, 
       AVG(L_QUANTITY) AS AVG_QTY 
FROM LINEITEM  
WHERE DATE_PART('month', L_RECEIPTDATE) = 8;
```
![][q2-skewed] ![][q2-skewed-time]
![][q2-uniform] ![][q2-uniform-time]
***
### Query 3
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
