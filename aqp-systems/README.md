## Approximate Query Processing (AQP)

AQP systems take advantage of the tradeoff available between accuracy and runtime in aggregation queries. With the explosion in database instance sizes, AQP offers a tractable if not exact solution to large scale analytic tasks. We wish to explore some of these systems and the AQP capabilities they offer. Please note, these experiments were done as a class project and the results should be taken with a grain of salt.

## The Systems

In order to offer a broad view of the landscape we have opted to benchmark the following systems:
* [Postgres](https://www.postgresql.org/)
  * Popular open source DBMS offering sampling schemes for the purposes of AQP
* [Amazon Redshift](https://aws.amazon.com/redshift/)
  * Commercial data warehousing solution available on Amazon's ec2 cloud
* [SnappyData](https://www.snappydata.io/)
  * Open source startup DBMS combining transactional and analytical processing
