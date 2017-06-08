# Benchmarking Amazon Redshift with TPC-H
Jingchen Hu (jingchen@uw.edu)

## Introduction
Amazon Redshift is a fully managed dataware housing solution launched in 2013, optimized for analytics queries on large scale datasets. In this project I benchmarked Redshift against the standard TPC-H dataset to explore the performance and scalibility it provides, and try out the newly released Redshift Spectrum service.


### Redshift
Redshift follows the typical shared-nothing archetecture of a parallel database system. It separate different types workflows into data plane and control plane. Apart from distributing the data to the worker nodes, Redshift also partitions the data on each worker node to be consumed by "node slices", each representing a processing core in a multi-core processor, in order to reduce contention. The datablocks are replicated in both the database and in S3 for durability, and is automatically backed up through asynchtrouns tasks in the control plane.

![s](https://i.imgur.com/gcCXBez.png)

Redshift used standard techniques for improving performance for OLAP queries, including columnar storage, per-column compression, co-locating compute and data, compilation to machine code, etc. It also uses multidimensional z-curves instead of traditional indexes.

As Gupta et. al. describted in [their paper on Redshift](http://dl.acm.org/citation.cfm?id=2742795),  one of the key design goal of Redshift is simplicity: to make it easy to experiment with, to tune, and to manage. As a result Redshift has few tuning knobs compared to other database engines. The default/automatic setting is designed to be sufficient for most use cases. As for the query interface, it supports declarative ANSI-SQL and python UDF. 

In April 2017, Amazon released Redshift Spectrum, a service that allows Redshift to directly scan and process data residing on S3. This enables a flexible combination of “larger fact tables in S3 and smaller dimension tables in Redshift”, as described in Redshift best practices.

### TPC-H
The TPC Benchmark™H (TPC-H) is a standard decision support benchmark for big data analytics. It contains syntetic data and 22 default queries, representing a generlaized complex analytics workload that answers critial bussiness questions. The queries are intentionally made computational heavy, typically invloving multiple joins, complex aggregations, and subqueries. The data size and distribution can be controlled via arguments while generating the synthetic data. Below is the schema of the benchmark database. The configuration and queries I used will be described in the next section.

![schema](https://i.imgur.com/iYNKTWh.png)

## Experiment Setup

### Data and Queries
To test out how Redshift scales on various data sizes, I used generated TPC-H datasets of sizes 10GB, 100GB, and 300GB, all with uniform data distributions. To see how data skew affects query performance, I also incorporated a skewed version of the 100GB dataset, generated using a Zipfian Distributaion with theta = 1. These data are published on S3: s3://uwdb/tpch and s3://tpch-300 (Special thanks for Shrainik Jain and Guna Prasaad for posting these online).

The queries I evaluated consist of both TPC-H queries (with constants in predicates randomly generated), and some simpler queries I made up. 2 out of the 22 queries (q4 and q20) contain correlated subqueries that are not supported by Redshift, and therefore were omitted in this experiment. The simpler queries I wrote contain scanning on predicates, aggregation and sorting (on 2-3 attributes), and simple multiway joins (3-5 way joins). I also limited the final number of rows returned by scan and joins.

### Cluster Configuration
Amazon provides specialized instance types for Redshift cluters. Although they are just EC2 instances, there are no direct equivalent instance types available in EC2. I used the default type "dc1.large" (which is convered by the Redshift free trial). Each such node contains 15GB memory, 2 cores and 160GB SSD. Its network IO performance is "moderate" by AWS's term. To see how redshift scales, I used 2, 6, and 18 compute nodes for comparison (so that's 4, 12, and 36 node slices, plus one leader node in each cluster). I used a growth factor of 3 since it helps with the evaluation of the scale-up and speed-up on the 100GB and 300GB TPC-H data.


### Setup and Data Loading
Redshift extends Postgres's COPY command to allow copying data conveniently from S3 into database tables. For instance:
```
copy customer from 's3://uwdb/tpch/uniform/10GB/customer.tbl'
credentials 'aws_access_key_id=<...>;aws_secret_access_key=<...>'
delimiter '|';
```
Note that when executing these loading queries, Redshift automatically injects queries for data sampling and analyzing (such as "count(*)"s and "analyze compression"s seen in the query logs), in order to do compression scheme selection and query optimization. These post-processing are also counted as parts of data loading time in the experiment.


## Evaluation results
In this section I presents the results of my experiments. Unless specified, all time unit are in seconds.
### 1. Data loading
![loading](https://i.imgur.com/rNvmToc.png)

First I measured the data loading time using the COPY command. Here the time includes the post-processing/analyzing time, but not the cluster start up time. Increasing the number of nodes reduces the time needed only slightly.

Later I realized that I was not using the most efficient way of loading the data. I loaded the whole data file all at once, whereas it would be better to split it into smaller chuncks to allow more parallelism and reduce the bottleneck at the master node.


### 2. Cold vs. warm start
![start](https://i.imgur.com/UFgakHC.png)

The distinction of cold and warm start affect the queries' performance greatly. Here warm start only uses 1/3 of the cold start's run time. Warm start and cold start can represent different style of query workloads. For instance, frequently-running ad hoc reporting queries should expect a "warm" cache environment.

All later results reported are for warm start only, where I preheat the database with 1 or 2 runs and measure the runtime of two subsequent queries.


### 3. Runtime of queries
![total](https://i.imgur.com/1X1wylV.png)
![query](https://i.imgur.com/QuVDM5l.png)

The figures above show the run time of different types of queries. A closer look at the TPC-H queries' performance shows that the total TPC-H's runtime is ususally dominated by complex multiway joins.

The Redshift dashboard provides detailed monitoring of CPU usages and disk/network IO during query execution. One observation I found is that the slowest queries are ususally the ones that spill intermeidate results to disk. The ones with in-memory execution are much faster on average. The disk usage shown below is for one of the slower TPC-H queries.

![disk](https://i.imgur.com/l5TO6mc.png)

### 4. Speed up and Scale up
![speedup](https://i.imgur.com/bczWSyp.png)

Speed up and scale up are two important metrics for a database's scalablity. I first measured speed up by fixing the dataset size, and add more nodes to see if the query time reduces porportionally. First we notice that the speed up is highly query dependent - aggregates and joins see larger improvements. Also, the difference from 6 to 18 nodes is much smaller than growing from 2 to 6 nodes, showing diminishing return for adding more nodes.


![scaleup](https://i.imgur.com/6EG4pUw.png)

Scale up, on the other hand, is slightly more consistent across query types, although also sub-linear. Again, queries invovling complicated joins benifits less from the increased number of workers.

### 5. Skewed data
![skew](https://i.imgur.com/bKxHgHm.png)

I was surprised to find out that the queries I used actually ran faster on the skewed data (Zipf's distribution, theta = 1). I was aware that another project group saw similar trends. I'm not sure about what causes the improvement (it could be due to the randomly generated predicates), but at least it shows that Redshift is not particularly sensitive to highly skewed data.

### 6. Redshift Spectrum
![spectrum](https://i.imgur.com/Dizlwjq.png)

To use Spectrum, one need to first create an "external table" to specify the table in S3 and its extraction mechanism. For instance:

```
create external table spectrum.nation(...)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/nation/';
```
Then in later SQL queries the table could be referenced just as "spectrum.nation" as normal. In the query plan, Redshift will then replace "sequential scan" with "Spectrum read from S3".

Here I measured the runtime of aggregates and scans on 10GB data (the others take longer). Reading from S3 is much slower as expected, but it could be ideal for large static relations that are less frequently read from.


## Discussions
### Administrative workflow
I think Redshift succeeded in providing an easy-to-use administrative interface. Database snapshots are taken automatically at a regular basis, completely transparent to the database users (therefore they might affect the measurements in this experiment). Snapshots are saved in S3 and can be managed in the dashboard. Reconfiguration and snapshot rstoration is rather straightforward in the console UI. However since it's a fully managed service, sometimes the user might have a hard time understanding the exact behaviours underlying the status changes in the console, especially during reconfigurations such as resizing and rebooting.
### Limitations and future work

The measurements in thie experiment are very corase-grained, and only aim to provide a high level intuition of Redshift's performance. For instance, I only measured the average of two runs per query after "preheating" with one run. As mentioned earlier, the way I load the data from S3 could be improved as well. Further things that could potentially be benchmarked includes operations on encrypted data, and loading compressed data.

### Conclusion
Redshift works great out-of-the-box. It's very easy to get a Redshift up and running on AWS (compared to other systems I tried this quarter). Also it fits nicely into AWS's ecosystem, and intergrate nicely with S3, especially with the new Spectrum service. The declarative SQL with Python UDF gives some degree of flexibility, but not at the level as a general purpose computation engine such as Spark. However the plus side is that it should be very easy for people who are writing SQL to migrate to Redshift, from Amazon's own RDS, or other standard RDBMS. Under my configuation, Redshift shows near-linear scale-up and less-so-linear speed-up, and the results are both highly query dependent.

