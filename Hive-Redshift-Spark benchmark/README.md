## Introduction:
With big data technologies present as a pervasive necessity in today’s world, there’s no shortage of tools but there definitely is a lack of understanding around how to select the perfect big data tool, and which tool would be the most optimum as per an individual’s or an organization’s very specific requirements. This lead us to explore and evaluate 3 of the most prominent big data technologies, Apache Hive, Apache Spark and Amazon Redshift and take a look at how they stack up against each other under different conditions.

The questions that come within the scope of the project are:

What is the load time we would be expecting to load the data into the systems?
What is the Querying time for basic queries such as select, going up to aggregate queries and join queries for the three systems?
What is the change in performance of the three systems under different cluster sizes?

The experiments gave us some very interesting results giving us a fair idea of the loading and processing times of the three tools when used for analytics of big data under a Business Intelligence umbrella.

We found out that Spark does really well as compared to Hive and Redshift when it comes to loading the data onto the disk or caching onto the memory in case of Spark, but Redshift outperforms Spark and Hive in terms of the querying times of the large amount of data. Hive scales very well but the querying time tends to be much slower as compared to Spark and Redshift. 

## Data:
The experiments to perform system benchmarking were carried out using a 100GB TPC-H uniform dataset.

## Task/Workload used in Evaluation:
Hive, Spark and Redshift, all three tools were used to query the TPC-H 100GB dataset where the benchmarking queries ranges from simple select clauses to more complicated queries including a select with where clauses, aggregate queries, join queries, aggregate plus join queries and also queries with case statements. Thus, evaluating under a variety of complex queries helped us to understand the query plans of all the three systems, the approach used by all the three tools to evaluate the queries and execute them on a cost-based factor.

The set of queries include 3 to 7 aggregate columns, 3 to 7 where attributes, along with joins on 2 to 5 tables. The design decision and benchmarking results of these queries along with a graphical comparisons of the runtimes for each of the three tools, Apache Hive, Apache Spark and Amazon Redshift are specified in the subsequent sections
These queries were executed under different system configurations across the three tools, the aim of which was to investigate the improvement in the querying time of these tools along with the ability to parallelize the tasks as compared to the other systems.

## Configurations and experimental setup:
Amazon provides up to 750 hours of free fully functional 1 single node dc1.large cluster for first 2 months. This gives enough time to experiment with Redshift. In order to experiment with higher number of nodes, the free consumption hours would be proportionate to the number of nodes. Amazon recommends using SQL Workbench to use Redshift for creating Business Intelligence solutions, but for the experimental purpose where we were supposed to run the queries multiple times over multiple configurations, we performed experiments over Jupyter Notebook. The configurations used were 4 Nodes and 6 Nodes in single dc1.large cluster that has 7 EC2 compute units, 15 GiB of memory and 160 SSD storage space on each node.

For this project Apache Spark was used and run on Databricks, which offers cloud based big data service. The spark query processing was also carried out under 4 nodes followed by a 6 nodes cluster. Each of the nodes in both the combination had a 15GiB of memory along, 4 cores per node along with a per node disk size of 160 GB SSD. Thus the total computational resources used for the benchmarking by 4 node cluster has a 60 GiB of RAM and  a total of 24 cores available to carry out all the tasks. The 6 node cluster thus has a total of 90 GiB of memory along with 48 cores.

Amazon Elastic MapReduce (EMR) was used to to create clusters with 4 nodes and 6 nodes respectively, and the master for each cluster was connected using SSH, enabling us to run Apache Hive interactively on HDFS. Each node, in both combinations, had 15GiB of memory, 8 vCPUs, and 80 GiB of SSD. Thus, the total computational resources used for benchmarking on 4 nodes was 60 GiB of RAM, and 32 vCPUs on that cluster, and for 6 nodes had a total of 90 GiB of memory along with 48 vCPUs on that cluster. These instances were m3.xlarge instances, where the default resources are set as mentioned above. 

## Amazon Redshift - Key Design Features:
Amazon rolled out a data-warehousing solution, that is built upon various services of Amazon including Amazon S3, and Amazon EC2. Amazon is a fast, fully managed, petabyte-scale DWH solution. It can very easily be connected to existing BI tools. 
Amazon is built out on Postgres 8.0.2. The data is stored in the column oriented format.The linkage between the columns of an individual row is derived by calculating the logical offset within each column chain. This linkage is stored as metadata. The architecture comprises of a single leader node and multiple compute nodes. The leader node is responsible for all kind of activities that include accepting connection from client programs, parsing requests, compiles query plan and execution of final aggregation and results. The heavy lifting of query processing and data manipulation.

Optimization and subsequent trade-offs:
Redshift offers various compression types and this can be applied to each column separately. Our choice of compression were delta for primary keys, dates, bytedict for controlled vocabulary, text255 for text fields. We choose appropriate container size for other integers that varied based on the bytes they occupy so like 8,16,32. This was recommended by the Amazon themselves to assign the data types based on the variable requirements. Redshift does not support any kind of constraints such as primary keys and foreign keys, but we can explicitly mention them in our definitions. Hence, for each table in the TPCH schema we choose the keys that were incremental, for example, lineitem key for lineitem table and so on. Based on the queries that we expect to perform, Redshift offers sort keys so that we can store the data in a sorted manner. Apart from simple sort key if we choose compound keys, then the columns should be chosen in the order of the importance. On the other hand if we choose Interleaved, then it gives importance to all the keys independently. So mostly we choose the primary keys as the sort keys. But for Nation and Customer, where the individual entity was identified by several keys, we used interleaved keys. Distribution style is basically how do we want to distribute the data on our nodes. An Even Distribution would store the data in a round robin fashion, an All distribution would be for smaller dimensions that can be copied and is required several times. Key distribution is based on the sort keys, this is recommended for the bigger fact tables where the joins are made almost with every query.

## Apache Spark - Key Design Features:
Benchmarking for BI and Analytics, we use Spark’s dataframes since data is organized into named columns, like a table in a relational database. This allows to create a structure of the large amount of data. Dataframe is a programming abstraction used by SparkSQL, acting as a SQL querying engine. Spark SQL provides the capability to run SQL like queries on Spark data using traditional BI and visualization tools.

Apart from the in-built optimizations provided by Apache Spark over its Dataframe API, some additional design decisions were used to further optimize the querying and processing of Apache Spark. Firstly, the main advantage of working with Spark is its ability to do in-memory analytics. We cache the TPC-H data onto the memory of the nodes in the cluster, where the system holds as much data into the memory as possible and then spills over the remaining memory onto a disk. Caching a table Spark SQL represents the data in an in-memory columnar format. Besides that we also set Broadcast joins and it’s threshold, which helps us to broadcast the smaller join tables across all the nodes in the cluster to speed up the performance.

## Apache Hive - Key Design Features:
Apache Hive is a data warehousing solution that has been built on top of Hadoop in order to integrate HDFS and a SQL like interface to query the data. Hive implements traditional SQL queries using the MapReduce Java API. Apache Hive supports analysis of large datasets, which can be stored either on HDFS as well as compatible file systems like Amazon S3. For this project, I pulled the data from the S3 bucket to the local HDFS. The reason for this was that Hive, while loading tables from a path, will automatically detect the first file in the folder and load the table using the contents it finds in there. The S3 bucket we used contained all the tables’ data in one folder, and so I needed to pull each .tbl file into a separate folder onto the local HDFS. 

The features of Hive which makes it absolutely conducive to performing business intelligence tasks on large data sets, other than it is a data warehousing solution, are:
It has extensive support for SQL and its features through HiveQL which makes adoption easier, and they are continuously adding more functionality e.g. merge doesn’t exist in the current HiveQL but will be added soon. 
It has a cost based query optimizer which uses join cardinality to calculate cost and assumes the rest of the functions have minimal cost. This also enables any BI tools to be used as front ends to Hive. 
It is possible to plug in custom mapreduce scripts to optimize the performance of the SQL queries. 
Hive supports a lot of file formats like RCFile, text file, sequence file, logfiles, csv files, parquet, and avro. 
It supports column oriented storage in the form of ORC file format, which enhances query performance. 
The method of optimization used in this project for Apache Hive was vectorization. Vectorization allows for the processing of batches of rows instead of one row at a time. This greatly enhances query performance in terms of the runtimes (I actually saw my first query run for 22 mins without vectorization, and then 8.7 mins with!). Vectorization is used mainly for queries using aggregate functions and joins (both of which were the major part of all the queries we used) and currently only supports ORC file format. So the tables need to be created and loaded in the ORC format. While this is time consuming, it aides performance in the long run. 

It is extremely easy to implement the vectorization itself. It can be done using the following two statements:
set hive.vectorized.execution.enabled = true;
set hive.vectorized.execution.reduce.enabled = true;


## Result:

During the study, it was very easy to setup the entire Data Warehousing Solution of Amazon Redshift, starting from setting up clusters, creating connections to the clusters using JDBC and ODBC connection string. Amazon offers good number of hours to experiment and decide whether the user should opt for it or not.

Choice of sort keys and distribution styles cannot be decided for each of the queries that will possibly run on the Business Intelligence system built on the Amazon Redshift. The BI solution needs to studied and requirements should be gathered well enough to choose the sort keys and distribution styles as it cannot be changed later.

Apache Spark being open source, it is very readily available on the web. Another advantage of using Spark is the possibility to use Spark either on local machines or over the cloud using Databricks, which is a very attractive option if the users don't want to parse over the installation process. Once we setup Spark clusters, we can use it in Scala in which it was originally written, but it also provides APIs to the many of the languages like Python, R and Java, which makes Spark easy to use by a number of developers, without focusing very much on a specific language. Languages can be chosen based on the requirements of tge projects to be developed. 

Apache Hive was easy to set up as well, once I figured out how to use the EMR. There were issues with bucket access policies and other policies which needed to be set to provide the correct permissions to be able to run Hive interactively or through ‘steps’ on EMR. Once the clusters were set up, I could connect the master node using SSH (a very simple process) and then could begin the data loads and querying.



#### Runtimes-

![Graphs](https://github.com/mbalazin/cse599c-17sp-projects/blob/master/Hive-Redshift-Spark%20benchmark/load%20times.png)

![Graphs](https://github.com/mbalazin/cse599c-17sp-projects/blob/master/Hive-Redshift-Spark%20benchmark/aggregate%20functions.png)

![Graphs](https://github.com/mbalazin/cse599c-17sp-projects/blob/master/Hive-Redshift-Spark%20benchmark/Aggregate%20functions%2Bjoin.png)

![Graphs](https://github.com/mbalazin/cse599c-17sp-projects/blob/master/Hive-Redshift-Spark%20benchmark/Aggregate%20functions%2Bjoin%2Bsubqueries.png)

![Graphs](https://github.com/mbalazin/cse599c-17sp-projects/blob/master/Hive-Redshift-Spark%20benchmark/aggregate%20functions%2Bwhere%20clause.png)

![Graphs](https://github.com/mbalazin/cse599c-17sp-projects/blob/master/Hive-Redshift-Spark%20benchmark/Case%20statement%2Bjoin.png)


As we can see, the load times for Redshift are comparably high, with Hive shaving a close second. This can be attributed to the compression Redshift performs. Spark’s load time is the shortest. 


Redshift does not disappoint on any query when compared to Spark and Hive. It works blazingly fast as compared to the other two systems. Few drawbacks such as it does not enforce constraints. It expects the stakeholders to be aware of the fact and load the data responsibly. Failing to do so, can give unreliable results for even simple queries such as select distinct query can return repeated results.

Overall, we can see that Spark does really well as compared to Hive and Redshift when it comes to loading the data onto the disk or caching onto the memory in case of Spark, but Redshift outperforms Spark and Hive in terms of the querying times of the large amount of data. Hive scales very well but the querying time tends to be much slower as compared to Spark and Redshift.

The results of Hive seem surprising seeing as to how it has been built as a data warehousing solution, but remember that it is built on top of HDFS so that integration is expected to slow things down to a certain extent. 

Our overall winner, hands down, was Amazon Redshift! 

#### Disclaimer:

This is a class project, and we were dealing with a few constraints such as time, limited Amazon credits and an absolute beginner level of knowledge for all three systems as well as Amazon AWS. 
Gosuddin Siddiqui performed the experiments on Amazon Redshift. You can email him at gosuddin@uw.edu
Jay Chauhan performed the experiments on Apache Spark. You can mail him at jchauhan@uw.edu
Shrija Priyanil performed the experiments on Apache Hive. You can mail her at shrijap@uw.edu
