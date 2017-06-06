# How well can SnappyData handle approximate queries?
***Important: This experiment was run in May of 2017, and at the time of the experiments, SnappyData was a newer system still being heavily developed. Therefore, the documentation did not have a ton of examples and did not explain the configuration options well. A lot of the problems I experience with SnappyData could likely have been fixed with help and tuning from someone more knowledgeable about the system.

### Overview
[SnappyData](http://snappydatainc.github.io/snappydata/) is a database management system that combines [Apache Spark](https://spark.apache.org/) with an in-memory database system to provide a database system that can provide OLAP and OLTP support. In particular, they combine the OLAP system, Apache Spark, with the OLTP system, [Pivotal GemFile](https://pivotal.io/pivotal-gemfire) (open source version is [Apache Geode](http://geode.apache.org/)).

Their main idea is to extend Spark's RDDs to be mutable and stored in-memory to allow for fast query processing. They further optimize the processing by utilizing vectorization and code generation. They support three types of tables: column, row, and probabilistic. Column tables extend Spark's RDDs, row tables extend GemFire's tables, and probabilistic tables are for samples. These sample table are our main focus because they are used in SnappyData's [Synopsis Data Engine](http://snappydatainc.github.io/snappydata/aqp/).

SnappyData's SDE is an AQP system that automatically chooses which sample to use during query processing in order to satisfy an accuracy contract provided by the user (based off of the [BlinkDB](https://sameeragarwal.github.io/blinkdb_eurosys13.pdf) system). In particular, the user creates stratified samples where each sample is stratified on a specific Query Column Set (QCS). The QCS is typically one of the most commonly used set of dimensions in the GroupBy, Where, and Having clauses of your queries. In addition to the QCS, the user provides a sampler percent.

After the samples are creates, the user simply has to add the keywords ``WITH ERROR <fraction> [CONFIDENCE <fraction>] [BEHAVIOR <string>]`` to the end of a query to invoke the SDE. The error and confidence fractions create the accuracy contract the system must meet. The system then chooses the best sample to use that satisfies the contract. If no such sample exists, the system, by default, runs the query on the original table. That behavior, however, can be modified with the ``BEHAVIOR`` clause at the end of the query.

For more details, see their [paper](http://cidrdb.org/cidr2017/papers/p28-mozafari-cidr17.pdf).

## Experiments

### Experiment Plan
To test the accuracy and runtime of SnappyData, we utilized Amazon AWS to run SnappyData using a m4.xlarge (15 GB RAM) single node setup. We used two 100 GB versions of TPCH stored in Amazon S3: one that is uniform and one that is skewed (theta of 1.0). We generated three different samples on the LINEITEM table using the following QCSs and option clauses:
* L_RECEIPTDATE bucketized on month: ```(qcs 'month(L_RECEIPTDATE)', fraction '0.01')```
* L_EXTENDEDPRICE bucketized into 10 buckets: ```(buckets '10', qcs 'month(L_EXTENDEDPRICE)', fraction '0.01')```
* L_ORDERKEY bucketized into 10 buckets: ```(buckets '10', qcs 'month(L_ORDERKEY)', fraction '0.01')```
* L_RECEIPTDATE, L_EXTENDEDPRICE bucketized into 10 buckets: ```(buckets '10', qcs 'month(L_RECEIPTDATE, L_EXTENDEDPRICE)', fraction '0.01')```
We then issued the following 5 queries 5 times each:

1. ```SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_COST, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM WITH ERROR 0.1 BEHAVIOR 'do_nothing';```

2. ```SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_COST, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM  WHERE month(L_RECEIPTDATE) = 8 WITH ERROR 0.1 BEHAVIOR 'do_nothing';```

3. ```SELECT month(L_RECEIPTDATE) AS MONTH, COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM  GROUP BY month(L_RECEIPTDATE) ORDER BY month(L_RECEIPTDATE) WITH ERROR 0.1 BEHAVIOR 'do_nothing';```

4. ```SELECT S_NATIONKEY AS NATION, COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM , SUPPLIER WHERE L_SUPPKEY = S_SUPPKEY GROUP BY S_NATIONKEY ORDER BY S_NATIONKEY WITH ERROR 0.1 BEHAVIOR 'do_nothing';```

5. ```SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM LINEITEM , ORDERS WHERE L_ORDERKEY = O_ORDERKEY AND O_ORDERPRIORITY = '1-URGENT' WITH ERROR 0.1 BEHAVIOR 'do_nothing';```

The 'do_nothing' indicates that we want SnappyData to return the estimated answer even if they can't satisfy the accuracy contract.

### Experiment Reality
This is where we ran into the most problems with SnappyData. There are three main ways to start a SnappyData cluster. One is by using their [iSight CloudBuilder](http://www.snappydata.io/cloudbuilder) tool that does most of the work for you and gives you a Zeppelin notebook to run queries. The other is to use an EC2 launch script to start everything via Amazon AWS and use the command line or a Zeppelin notebook to run queries. The third is to launch your own cluster and do the installation manually.

We first tried the Zeppelin notebook. It was great for the initial use, but it does __not__ have an import notebook feature, meaning all queries had to be copied into the notebook. Additionally, to comment out lines in the SQL interpreter, the EOL character must be removed. As this was not ideal for running multiple tests, we then tried to use their EC2 launch script. This was also unsuccessful because even after adding in some necessary jar files, the SQL shell could not access S3. We lastly tried to launch our own cluster, download SnappyData on the cluster, and use SnappyData's local launch script. This was, again, unsuccessful. For one, we could not use the SQL shell because it did not having timing capabilities. Also, when we ran the queries though the Scala shell, all the approximate query results came back empty. We knew an empty result was incorrect because we had tested one of the queries on Zeppelin. In the end, we ended up using Zeppelin to do the experiments, which was not ideal. Therefore, because all of the queries had to be run manually, we were only able to do one run of the true queries rather than the planned 5.

Another problem came when trying to make the samples. Samples 2 through 4 could not be created because the system ran out of memory. We are not sure why this happened, and maybe we needed to have some parameter set or to specify we wanted the sample to be column-stored (we were using the default storage). However, the documentation was not clear on this. Therefore, we only had the first sample in our experiment.

The last problem we dealt with was that we couldn't create two SnappyData clusters using iSight in the same zone on Amazon AWS. We believe this had something to do with the security groups.

## Results

### Query Accuracy
(Skewed: Yellow (S), Uniform: Green (U))

![][skewed-err] ![][uniform-err]

These graphs show the percent error versus the query for the skewed data (yellow and with S) versus the uniform data (green and with U). As you can see, SnapyData does extremely well in terms of percent error, achieving less than 0.2 percent error (that is 0.2 percent error and not 20 percent error). They did worst on SUM and COUNT of the 4th query, likely because that query involves a join. The interesting aspect is that SnappyData does slightly worse on the uniform data rather than the skewed. The reason for this is likely because of how TCH is skewed. TPCH is skewed in the order it is stored. This is the same order of L_RECEIPTDATE, which means that each distinct value in L_RECEIPTDATE will likely have the same or similar values for the aggregates. Therefore, the uniform TPCH will actually have more variation for each bucket in the L_RECEIPTDATE sample; therefore, SnappyData will do better on the stratified data.

### Runtime
(Skewed: Yellow (S), Uniform: Green (U))

![][skewed-sample-time] ![][uniform-sample-time]
![][skewed-true-time] ![][uniform-true-time]

These graphs show the average runtime of the 5 queries in seconds. The graphs for the sample runtime versus the true runtime are separated because the axis are so different. SnappyData's AQP queries are about 10x faster than the non-approximate queries run on the full data. As explained before, we did not run all 5 trials for the non-approximate queries, but for the approximate queries, the standard deviation was approximately 0.42 seconds for query 5 and under 0.15 seconds for the other queries for both the uniform and skewed data.

The other aspect to note is that query 5 never finished for the uniform data. It ran for 3 hours, and then the Zeppelin notebook froze. For the skewed data, after 50 minutes of running, it returned a ``java.lang.reflect.InvocationTargetException`` error. We are not sure what this meant but were able to determine the accuracy because our experiments on Postgres used the same queries.

### Conclusion
While SnappyData did perform well once we got it working, the time spent getting everything running was painful. Further, it would likely not perform as well with other datasets that aren't artificially skewed since it could not generate stratified samples on continuous attributes (at least, we could not get it to generate those samples). However, we think this system has a lot of promise and could become a major contender in the AQP landscape, but for now, we'll stick to Postgres. It is also worth mentioning that SnappyData has a Slack channel that can be used to contact developers.

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
[skewed-true-time]: https://docs.google.com/spreadsheets/d/1PFZNqnnJA9q70StIDHL72mY9iiHRIiD0XsiaEEexU00/pubchart?oid=797789770&format=image
[uniform-true-time]: https://docs.google.com/spreadsheets/d/1QYPETzK2Rc33zE416WKV0qFrDQDfQ_AtJ2d-mvlE_5o/pubchart?oid=958007450&format=image

