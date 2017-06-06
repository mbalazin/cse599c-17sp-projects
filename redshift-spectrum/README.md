# Loading, Scaling, and Query Processing on Amazon Redshift and Amazon Spectrum  

Amazon Redshift, a service that began back in 2013, is a fairly new database warehouse service that supports storing and managing structured data. Internally, the service stores the data in a columnar format to facilitate data compression. The system's features are primarily like any other RDBMS, supporting the ability to run transactions and high-performance analysis on large datasets. In fact, it supports all Postgres features up to version 8.0.2, but then branches off to support other features including (but not limited to) the ability to define table distribution functions and the ability to ingest data directly from S3.

More recently, Amazon released a new service called Amazon Redshift Spectrum. Spectrum can read and process data directly from S3, without having to store the data directly on Redshift.  This enables users to run queries that span across different storage backends. For example, we can read data from S3 and process it along with data stored in Redshift. 

Reading data from S3 provides an interesting benefit in place of scaling. If I/O is the main bottleneck, Spectrum can take care of pre-processing S3 data in parallel before sending the data directly to Redshift's compute nodes. We discuss the query performance for these types of queries in Section 4. 

For this project, we focus on three main components. First, we consider the time it takes to load data into the system. We describe how to create relations and the pre-processing steps required. Second, we consider the amount of time it takes for Redshift to scale by adding or removing nodes. Third, we run queries that access relations from different backends, including Redshift, Spectrum or a combination of both which we call *hybrid* queries.  

## Section 1. The Redshift Architecture
To get the most out of performance (as we will see in the next few sections), it is important to understand the system architecture. As a user, you will spend most of the time sending commands to to the leader node through either a standard JDBC/ODBC client. The leader node parses queries and sends execution plans to the workers. Workers are only selected to run a query if they contain a portion of the data being read. Leader nodes are also responsible for managing the catalog.

<figure>
<img src="figures/redshiftArchitecture.png" width="50%" height="50%">
<figcaption>Figure 1: Redshift Architecture</figcaption>
</figure>

Each compute node is partitioned by node slices which have access to a portion of the node's memory and disk space. The number of slices available on the node is dependent on the type of instance selected. For example, the cheapest instance available has two slices in each node. If a 4-node cluster is launched, you would have 8 node slices available. When the leader node issues a query execution plan, it will issue commands to each individual node slice. 

In Figure 1, we illustrate an example of a Redshift cluster with a leader node and a set of compute nodes. Each compute node contains 2 slices, and through Amazon Spectrum, compute nodes are able to access data that lives directly in S3. For this project, we treat Spectrum as a black box service. Based on their documentation, Spectrum is a service that *applies sophisticated query optimization, scaling processing across thousands of nodes*. The details of how data is processed on their service are not given to users.


## Section 2: Experimental Setup 

When starting up a cluster for the first time, the user must specify whether they're interested in running a single-node or multi-node deployment. There are extra steps involved, including installing the recommended client and opening the leader's port to allow external connections. Overall, it was simple to get started, as all steps in the setup process are well documented.

For the dataset, we use the TPC-H SSB dataset on SF=100. On Redshift, we did not have many options available when selecting between the different instance types. The cheapest ones are dc1.large at $.25/hour and spot instances are not available for this service. This instance type includes 2 cores, 15 GB memory and 160GB of SSD storage. For all the experiments, we scaled the cluster from 1 node up to 5 nodes (10 node slices).

## Section 3. Loading Data

Loading data primarily applies to Redshift, not the Spectrum service. For Spectrum, the only information required is providing metadata about the table. The metadata should specify the schema, file delimiter and the location in S3.

For Redshift, there are many more steps. Before loading data into the Redshift cluster, we need to declare a schema for each table. Redshift supports many standard datatypes. Overall, the `CREATE TABLE` is really similar to other database systems except that the user is given an option to specify a distribution key. During data ingest, Redshift will reshuffle the data and store it according to this key. Available options for this key include: `EVEN`, `KEY` and `ALL`. Where `EVEN` represents a round-robin partitioning, `KEY` represents hashing by a specific column (multi-key hashing is not supported), and `ALL` represents a broadcast.  Given our data, we partitioned the lineorder relation (the largest table) based on a distribution key, while all the other smaller dimension tables are broadcast across the cluster. 

Before ingesting the data, we needed to split the data in S3 into many small chunks. The number of chunks does not need to match the number of node slices available, as Redshift handles the mapping between chunks and node slices. Also, when generating the chunks, we need to make sure to split the file based on lines, and not bytes. Otherwise, we end up having chunks with partial rows. 

Once the pre-processing is finished, we can load the data with the following command, where the S3 path points to the chunks:

```
copy lineorder from 's3://path/to/data/chunks/lineorder' 
iam_role '' 
delimiter '|' region 'us-west-2';
```

In Figure 2, we show the amount of time it takes to load the Lineorder relation for different number of node slices. As expected, there is a large performance difference between using 2 and 4 node slices, and less of a difference between 8 to 10 slices. 

<figure>
<img src="figures/fig-ingest.png" width="40%" height="40%">
<figcaption>Figure 2: Parallel ingest for the Lineorder Relation</figcaption>
</figure>

For the rest of the dimension tables, the ingest time is much shorter, where runtimes ranged in the span of seconds. Although the ingest times are fast, we still took a closer look at the query plan for loading these smaller dimension tables. It was interesting to see that although we initially specified that these tables should be broadcast, Redshift only assigned one node slice to read the file from S3 before broadcasting to all the workers. Based on our specification, it seems more intuitive to have each worker independently read the broadcast table directly from S3 instead of having one slice reading and shuffling/broadcasting it to all the other workers. In Figure 3, we show the scan portion of this query plan. Notice how only one slice (node slice 7) is reading the table. The rest of the query plan (not shown) describes how this slice broadcasts the data to the rest of the slices.

<figure>
<img src="figures/fig-broadcast.png" width="30%" height="30%">
<figcaption>Figure 3: Query plan for dimension table loading </figcaption>
</figure>


After ingest, the data is compressed automatically. After using a `COPY` command, Redshift will automatically try to find the best encoding for each column. If a user prefers to keep data in the RAW format, they can specify this in the COPY command during ingest. Redshift can support up to 8 different types of compression encodings. In Figure 4, we show an example of the automatic compression commands in the log (first 3 entries).

Encoding is important, as it affects the amount of data being transferred during scaling, which we discuss in the next section.  

<figure>
<img src="figures/compression2.png" width="60%" height="60%">
<figcaption>Figure 4: Automated compression commands</figcaption>
</figure>



## Section 3. Scaling up and down

Redshift also offers the ability to scale the cluster up or down, or even scale to a different instance type. The only requirement they have is that the data should be able to fit in the new configuration. 

When deciding to resize, which only requires a couple clicks on the dashboard, Amazon Redshift immediately launches a new cluster at the new requested size. Then, the data from the old cluster is moved over to the new one. During this time, the old cluster is in a *read-only* mode, meaning that transactions or ingest queries (any writes) are not allowed. Once all the data has finished transferring, all client connections now point to the new cluster.

What is surprising is that provisioning the new target cluster seems to take a long time. When the user initially sends a request, it takes approximately 10 minutes to create a new cluster. This seems long, as starting up a new cluster from scratch only takes about 5 minutes. After the new cluster is provisioned, the data transfer begins. After ~20 minutes (this is based on our dataset), the cluster finishes resizing.    

In Figure 5, we have two graphs. On the left graph, we display the time it takes to scale up by one node at a time. On the x-axis, we show the number of slices. We started with 2 node slices and incrementally added more slices. Each time we switched to a different configuration, we kept migrating the same amount of data. From this graph, it does seem like having more node slices as readers and writers (see 6-to-8 and 8-to-10) is slightly faster than 2-to-4 and 4-to-6. Note, we did try to look at the documentation to see if there was any more information about available on how this transfer actually happens. Currently, there does not seem to be any documentation that details this step. Also, we cannot view the cluster resource utilization during this step. 

On the right figure, we do not see the same trend. It was surprising to see that switching from 4-to-2 node slices turned out to be faster than some of the other migrations. In general, because we do not know how the transfer happens internally, it's not clear if there is a trend we should look out for or if these runtime variances are due to other factors in the system.  

<figure>
<img src="figures/fig-scaling-up.png" width="400"/> <img src="figures/fig-scaling-down.png" width="400"/> 
<figcaption>Figure 5: Time to scale up or down</figcaption>
</figure>


### Section 4. Query Processing

For the final part of this project, we also benchmark the runtimes for queries specified in the TPC-H SSB [paper](http://www.cs.umb.edu/~poneil/StarSchemaB.PDF). There are a total of 13 queries, inspired by the original TPC-H queries.  

Our goal was to try three variants of these queries. One variant would consider the case where all tables scanned are located on Redshift (Redshift Only). The second variant assumes that all tables are only on S3 (Spectrum Only). Last, we consider the case where some tables are read from Redshift and others are read from S3 (Hybrid). For Hybrid, we had the Lineorder read from Redshift and all other dimension tables read from S3. The reasoning for this was to minimize the amount of data being read from S3. 

Recall, when we initially ingested data for Redshift, we specified the distribution style for each relation. In addition, since the data on Redshift is also compressed, this gives Redshift-Only queries a large advantage. Between Spectrum-Only and Hybrid queries, it seems intuitive to think that Hybrid queries should perform slightly better -- as a subset of the relations are read from Redshift. As we see in the next figure, this is not the case (at least not initially). 

In Figure 6, we show the runtimes for the queries on all variants for 10 node slices. Note, the y-axis is in log scale, as Redshift-Only queries are quite fast. We ran each query variant 4 times, omitted the first cold run, and plotted the average as well as the standard deviation for the rest of the runs.  There are a couple things to note. One, there is high variance in performance for Spectrum-Only queries. This might be due to S3 or the Spectrum service, but this is not clear. Second, it was surprising to see how expensive the hybrid queries were. 

<figure>
<img src="figures/fig-queries-bad-log.png" width="70%" height="70%">
<figcaption>Figure 6: Query Runtimes for all Storage Variants (log-scale) </figcaption>
</figure>

We took a closer look at the query plans for the bad queries, starting with Q4. When looking at the query plan, we noticed that the query optimizer was not assigning costs as we would expect. 
In Figure 7, we see a portion of the query plan. Any table scanned from S3 is assigned a very high cost of 10 billion (see the red cost for the Part relation). As a result, the optimizer sees Lineorder as the smallest table, and decides to broadcast this table before joining it with the Part table. This step causes the queries to slowdown considerably.

<figure>
<img src="figures/queryplan.png" width="70%" height="70%">
<figcaption>Figure 7: Query Runtimes for all Storage Variants</figcaption>
</figure>

Instead of having the smaller dimension tables being read from S3, we instead had Hybrid queries read Lineorder from S3 and all other dimension tables from S3. In Figure 8, we show the same graph as Figure 6 but we no longer use a log scale. We do this to make it simpler to compare to the new Figure 9...

<figure>
<img src="figures/fig-queries-bad.png" width="70%" height="70%">
<figcaption>Figure 8: Query Runtimes for all Storage Variants</figcaption>
</figure>

In the figure below, we show the runtime for the new version of the Hybrid queries (v2). In general, the runtimes improve considerably now that the Lineorder relation is no longer being broadcast to all the nodes. Although in some cases, we still do see a large variance -- consider query 11. 

<figure>
<img src="figures/fig-queries-better.png" width="70%" height="70%">
<figcaption>Figure 9: Query Runtimes for all Storage Variants (Hybrid Version 2)</figcaption>
</figure>


## Section 5. Conclusion
In conclusion, in this work we demonstrated data loading, scaling and query processing in Redshift and the newer Spectrum service. This work is preliminary, and there are still many optimizations that could be done to improve performance. For example, if the data was stored in S3 in a Parquet format, this would improve performance as Spectrum will only read the necessary columns for each query. Second other optimizations include the ability to create indexes or running statistics on the relations (although, running statistics on S3 data is not an option). 

### Acknowledgements: Special thanks to the UW HPCC club for providing AWS credits for this project. 