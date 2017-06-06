# How well can [REDSHIFT](https://aws.amazon.com/redshift/) handle approximate queries?

We investigate the effectivness of the AQP functions exposed in Redshift. We remind the reader that Redshift is not a system designed for approximation. Nevertheless, we seek to benchmark their results as part of the class project.

Redshift offers approximation on two aggregation operations: 'COUNT(DISTINCT(...))' and 'PERCENTILE_DISC'. We find this narrow selection surprising since omitted operators such as 'SUM', 'COUNT', and 'AVG' would seem more natural and commonly sought after aggregator functions. We are also dissapointed that there is no way for the DBMS user to tune the runtime-accuracy tradeoff. While this manner of tuning is not generally available for the [Hyperloglog](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) algorithm used by the 'COUNT DISTINCT', the process used to approximate percentiles is not clearly described in the the documentation but known algorithms can offer this parametric tuning. In order to test these functions we run a collection of 6 queries (listed in detail below) on a 100GiB uniform (unmodified) TPC-H dataset, 100GiB skewed TPC-H dataset. We also include the raw results for 10GiB uniform and skewed TPC-H in the accompanying documentation but do not discuss them here. Queries 1-3 are count distinct queries while queries 4-6 use percentile. Each of queries 1-3 and 4-6 are comprised by a single table query, a single table query with a group-by, and finally a join followed by a group-by.

## Runtimes
(Zipfian: Yellow, Uniform: Green)
### Average Runtime

![][zipf100-avg] ![][unif100-avg]

***
### Runtime Stardard Deviation

![][zipf100-std] ![][unif100-std]

***
### Runtime Stardard Deviation (minus outliers)
Please refer to the takeaways section for an explanation of the outlier runtimes.

![][zipf100-std-outliers] ![][unif100-std-outliers]

***
### Approximate Query Error
(average error taken over group-by cells if applicable)

|Query | Zipf 10         | Zipf 100       | Unif 10         | Unif 100        |
| -----| --------------- | -------------- | --------------- | --------------- |
| q1   | 0.0001446217715 | 0.005755668202 | 0.000106        | 0.00537945      |
| q2   | 0.002897582032  | 0.001415359489 | 0.0002587521649 | 0.003686796976  |
| q3   | 0.004168386307  | 0.001030289057 | 0.0002134292575 | 0.00421623532   |
| q4   | 0.0002548925203 | 0.000820815891 | 0.000517471471  | 0.0006265493476 |
| q5   | 0.0002548925203 | 0.000820815891 | 0.000517471471  | 0.0006265493476 |
| q6   | 0.002108891085  | 0.001907817179 | 0.008647518662  | 0.008351887156  |

***
### Key Takeaways
* Runtimes for both the exact and approximate form of the query takes longer on the uniformly distributed version of TPC-H.
* Approximate queries do better relative to exact counterparts in the uniform setting. That is, the performance of the approximate form of the queries tends to suffer in the skewed setting.
* 'PERCENTILE_DISC' approximation does worse relative to exact counterpart than 'COUNT DISTINCT'. The speedup is generally worse than a factor of two, and for the simple single table percentile query (q4) the approximate version takes longer than the exact. Given these results, we cannot recommend the approximte percentile function as an effective speedup solution to general percentile queries.
* In most cases, the variability of runtime is insignificant w.r.t. total runtime. However, the exact form of the 'COUNT DISTINCT' query has displayed slow down by over a factor 2. These anomalies were generally observed during the first or second repetition for these queries which does not fully coroborate the warm-cache versus cold-cache theory. We do not currently have a satisfactory explanation for these results.
* While Redshift does not offer any control of the execution of the aproximation to the user, they state the guaratee that error will be below 2%. Our result corroborate this claim. In fact, at no point in our study did any error exceed 1%.

## Raw Results
Following are the links to Google Sheets for the raw runtimes for the Zipfian and Uniform Benchmark Results

* [Zipfian Benchmark Results](https://docs.google.com/spreadsheets/d/1SnzAy3DHXxXw4LXwEG8gyT7TX4orwsZ50hI2_Xgmy4s/pubhtml)
* [Uniform Benchmark Results](https://docs.google.com/spreadsheets/d/1LC7m6qt47X9XNNe8b3bl-m9JwAVov924DV-b17X2mlw/pubhtml)

## Author Notes
The experiments and analysis was done by [Walter Cai](wzcai.github.io). Feel free to [mail](mailto:walter[at]cs[dot]washington[dot]edu) him for any further details.

## Queries
q1:
```
SELECT COUNT (DISTINCT L_PARTKEY)
FROM LINEITEM;
```
q2:
```
SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, COUNT(DISTINCT L_PARTKEY)
FROM LINEITEM
GROUP BY MONTH
ORDER BY MONTH;
```
q3:
```
SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, COUNT(DISTINCT L_PARTKEY)
FROM LINEITEM, ORDERORDER
WHERE L_ORDERKEY = O_ORDERKEY
GROUP BY MONTH
ORDER BY MONTH;
```
q4:
```
SELECT MEDIAN(L_EXTENDEDPRICE)
FROM LINEITEM;
```
q5:
```
SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, MEDIAN(L_EXTENDEDPRICE)
FROM LINEITEM
GROUP BY MONTH
ORDER BY MONTH;
```
q6:
```
SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, MEDIAN(L_EXTENDEDPRICE)
FROM LINEITEM, ORDERORDER
WHERE L_ORDERKEY = O_ORDERKEY
GROUP BY MONTH
ORDER BY MONTH;
```

[zipf100-avg]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=1036452611&format=image
[unif100-avg]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=37376812&format=image

[zipf100-std]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=79636558&format=image
[unif100-std]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=348046484&format=image

[zipf100-std-outliers]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=720421779&format=image
[unif100-std-outliers]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=871301525&format=image
