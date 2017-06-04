# How well can POSTGRES handle approximate queries?
### Query 0
**Skewed Data**  
![][q0-skewed] ![][q0-skewed-time]
**Uniform Data**  
![][q0-uniform] ![][q0-uniform-time]
---
### Query 1
**Skewed Data**  
![][q1-skewed] ![][q1-skewed-time]
**Uniform Data**  
![][q1-uniform] ![][q1-uniform-time]
---
### Query 2
**Skewed Data**  
![][q2-skewed] ![][q2-skewed-time]
**Uniform Data**  
![][q2-uniform] ![][q2-uniform-time]
---
### Query 3
**Skewed Data**  
![][q3-skewed] ![][q3-skewed-time]
**Uniform Data**  
![][q3-uniform] ![][q3-uniform-time]
---
### Query 4
**Skewed Data**  
![][q4-skewed] ![][q4-skewed-time]
**Uniform Data**  
![][q4-uniform] ![][q4-uniform-time]
---
## Results
Following are the links to Google Sheets that contain accuracy and runtime measurements for the above experiments. Each document contains multiple sheets, one for each of the above queries.

* [Skewed Benchmark Results](https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/edit?usp=sharing)
* [Uniform Benchmark Results](https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/edit?usp=sharing)

## Author Notes
The experiments and analysis was done by [Guna Prasaad](http://gunaprsd.github.io). Feel free to [mail](mailto:guna@cs.uw.edu) him for any further details. 

[q0-skewed]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=549228374&format=image
[q0-uniform]:https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=1800207603&format=image
[q0-skewed-time]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=2077408150&format=image
[q0-uniform-time]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=20323704&format=image

[q1-skewed]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=870834951&format=image
[q1-skewed-time]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=990419999&format=image
[q1-uniform]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=2143604874&format=image
[q1-uniform-time]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=988380215&format=image

[q2-skewed]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=1353138985&format=image
[q2-skewed-time]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=413149780&format=image
[q2-uniform]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=1182604302&format=image
[q2-uniform-time]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=1022779726&format=image

[q3-skewed]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=2040716245&format=image
[q3-skewed-time]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=2119941661&format=image
[q3-uniform]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=1182604302&format=image
[q3-uniform-time]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=336570212&format=image

[q4-skewed]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=1618147876&format=image
[q4-skewed-time]: https://docs.google.com/spreadsheets/d/16ZAVpPt78mrzYB0bd0ZVl-fSTfQSxy79HAKNYEkjQSs/pubchart?oid=51920860&format=image
[q4-uniform]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=2124247202&format=image
[q4-uniform-time]: https://docs.google.com/spreadsheets/d/1lp3EyTpnfglM-PnFhAou8NZJ-xKikJfB_P0hXnUYuQw/pubchart?oid=534708547&format=image

