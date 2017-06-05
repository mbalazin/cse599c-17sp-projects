# How well can SnappyData handle approximate queries?
***Important: This experiment was run in May of 2017, and at the time of the experiments, SnappyData was a newer system still being heavily developed. Therefore, the documentation did not have a ton of examples and did not explain the configuration options well. A lot of the problems I experience with SnappyData could likely have been fixed with help and tuning from someone more knowledgeable about the system.

### Overview
[SnappyData](http://snappydatainc.github.io/snappydata/) is a database management system that combines [Apache Spark](https://spark.apache.org/) with an in-memory database system to provide a database system that can provide OLAP and OLTP support. In particular, they combine the OLAP system, Apache Spark, with the OLTP system, [Pivotal GemFile](https://pivotal.io/pivotal-gemfire) (open source version is [Apache Geode](http://geode.apache.org/)).

Their main idea is to extend Spark's RDDs to be mutable and stored in-memory to allow for fast query processing. They further optimize the processing by utilizing vectorization and code generation. They support three types of tables: column, row, and probabilistic. Column tables extend Spark's RDDs, row tables extend GemFire's tables, and probabilistic tables are for samples. These sample table are our main focus because they are used in SnappyData's [Synopsis Data Engine](http://snappydatainc.github.io/snappydata/aqp/).

SnappyData's SDE is an AQP system that automatically chooses which sample to use during query processing in order to satisfy an accuracy contract provided by the user (based off of the [BlinkDB](https://sameeragarwal.github.io/blinkdb_eurosys13.pdf) system). In particular, the user creates stratified samples where each sample is stratified on a specific Query Column Set (QCS). The QCS is typically one of the most commonly used set of dimensions in the GroupBy, Where, and Having clauses of your queries. In addition to the QCS, the user provides a sampler percent.

After the samples are creates, the user simply has to add the keywords ``WITH ERROR <fraction> [CONFIDENCE <fraction>] [BEHAVIOR <string>]`` to the end of a query to invoke the SDE. The error and confidence fractions create the accuracy contract the system must meet. The system then chooses the best sample to use that satisfies the contract. If no such sample exists, the system, by default, runs the query on the original table. That behavior, however, can be modified with the ``BEHAVIOR`` clause at the end of the query.

For more details, see their [paper](http://cidrdb.org/cidr2017/papers/p28-mozafari-cidr17.pdf).

### Experiment Set Up
To test the accuracy and runtime of SnappyData, we utilized Amazon AWS to run SnappyData using a m4.xlarge (15 GB RAM) single node setup. We used two 100 GB versions of TPCH stored in Amazon S3: one that is uniform and one that is skewed. We generated three different samples on the LINEITEM table using the following QCSs and option clauses:
* L_RECEIPTDATE bucketized on month: ```(qcs 'month(L_RECEIPTDATE)', fraction '0.01')```
* L_EXTENDEDPRICE bucketized into 10 buckets: ```(buckets '10', qcs 'month(L_EXTENDEDPRICE)', fraction '0.01')```
* L_ORDERKEY bucketized into 10 buckets: ```(buckets '10', qcs 'month(L_ORDERKEY)', fraction '0.01')```
* L_RECEIPTDATE, L_EXTENDEDPRICE bucketized into 10 buckets: ```(buckets '10', qcs 'month(L_RECEIPTDATE, L_EXTENDEDPRICE)', fraction '0.01')```
We then issued the following 5 queries 5 times each:

1. '''SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_COST, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM WITH ERROR 0.1 BEHAVIOR 'do_nothing';'''

2. '''SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_COST, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM  WHERE month(L_RECEIPTDATE) = 8 WITH ERROR 0.1 BEHAVIOR 'do_nothing';'''

3. '''SELECT month(L_RECEIPTDATE) AS MONTH, COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM  GROUP BY month(L_RECEIPTDATE) ORDER BY month(L_RECEIPTDATE) WITH ERROR 0.1 BEHAVIOR 'do_nothing';'''

4. '''SELECT S_NATIONKEY AS NATION, COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM , SUPPLIER WHERE L_SUPPKEY = S_SUPPKEY GROUP BY S_NATIONKEY ORDER BY S_NATIONKEY WITH ERROR 0.1 BEHAVIOR 'do_nothing';'''

5. '''SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM , ORDERS WHERE L_ORDERKEY = O_ORDERKEY AND O_ORDERPRIORITY = '1-URGENT' WITH ERROR 0.1 BEHAVIOR 'do_nothing';'''


This is where I ran into the most problems with SnappyData. 

### Query Accuracy 
![][skewed-err] ![][uniform-err]

### Runtime
![][skewed-sample-time] ![][uniform-sample-time]
![][skewed-true-time] ![][uniform-true-time]
***
## Result Data
Following are the links to Google Sheets that contain accuracy and runtime measurements for the above experiments. Each document contains multiple sheets, one for each of the above queries.

* [Skewed Benchmark Results](https://docs.google.com/a/cs.washington.edu/spreadsheets/d/1PFZNqnnJA9q70StIDHL72mY9iiHRIiD0XsiaEEexU00/edit?usp=sharing)
* [Uniform Benchmark Results](https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/edit?usp=sharing)

## Author Notes
The experiments and analysis was done by [Laurel Orr](https://homes.cs.washington.edu/~ljorr1/). For any further details or questions, please email [mail](mailto:ljorr1@cs.uw.edu) Laurel Orr. 

[skewed-err]: https://docs.google.com/spreadsheets/d/1PFZNqnnJA9q70StIDHL72mY9iiHRIiD0XsiaEEexU00/pubchart?oid=588497708&format=image
[uniform-err]:https://docs.google.com/spreadsheets/d/1QYPETzK2Rc33zE416WKV0qFrDQDfQ_AtJ2d-mvlE_5o/pubchart?oid=899616445&format=image
[skewed-sample-time]: https://docs.google.com/spreadsheets/d/1PFZNqnnJA9q70StIDHL72mY9iiHRIiD0XsiaEEexU00/pubchart?oid=721090478&format=image
[uniform-sample-time]: https://docs.google.com/spreadsheets/d/1QYPETzK2Rc33zE416WKV0qFrDQDfQ_AtJ2d-mvlE_5o/pubchart?oid=898811322&format=image
[skewed-true-time]: https://docs.google.com/spreadsheets/d/1PFZNqnnJA9q70StIDHL72mY9iiHRIiD0XsiaEEexU00/pubchart?oid=721090478&format=image
[uniform-true-time]: https://docs.google.com/spreadsheets/d/1QYPETzK2Rc33zE416WKV0qFrDQDfQ_AtJ2d-mvlE_5o/pubchart?oid=1138185761&format=image

