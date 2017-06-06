# How well can POSTGRES handle approximate queries?
[POSTGRES](https://www.postgresql.org/) is an open source database that has been developed and maintained both by industry and academia for the last two decades. From release 9.5, postgres started supporting sampling in order to enable approximate query processing. There is a huge body of work in the database community relating to estimation of query results from a sample of the database. There are several types of sampling techniques that are prevelant and each is known to provide unbiased estimators for different types of queries. 

## Sampling Support
Postgres supports two simple sampling techniques, namely **bernoulli** and **system** sampling. In Bernoulli sampling, the complete relation is scanned and individual tuples are randomly chosen (imagine a coin flip). The key bottleneck here is that the even if the query runs on a sample of data, we pay the cost of scanning the whole relation once. In some cases, this in itself could be a heavy operation.  
  
To overcome this, postgres supports an additional form of sampling called system sampling. System sampling operates at the granularity of pages instead of tuples. A random number is generated for each physical page in a relation. Based on this number and the sampling percentage specified it is either included or excluded from the sample. If a page is included, all tuples that occur in that physical page is included in the sample.  

The syntax to sample from a relation in postgres is very simple. The relation name contains additional `TABLESAMPLE` clause that specifies the sampling technique (`BERNOULLI` or `SYSTEM`) and sampling percentage. Here is an example aggregate query on a sample of the `LINEITEM` table from TPC-H benchmark.

```sql
SELECT COUNT(*) AS CNT 
FROM LINEITEM TABLESAMPLE BERNOULLI(0.1);
```

### Query 1
![][q1-skewed] ![][q1-skewed-time]
![][q1-uniform] ![][q1-uniform-time]
***
### Query 2
![][q2-skewed] ![][q2-skewed-time]
![][q2-uniform] ![][q2-uniform-time]
***
### Query 3
![][q3-skewed] ![][q3-skewed-time]
![][q3-uniform] ![][q3-uniform-time]
***
### Query 4
![][q4-skewed] ![][q4-skewed-time]
![][q4-uniform] ![][q4-uniform-time]
***
### Query 5
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
