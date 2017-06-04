# How well can POSTGRES handle approximate queries?
### Query 0

** Skewed Data **
![][q0-skewed] ![][q0-skewed-time]
** Uniform Data **
![][q0-uniform] ![][q0-uniform-time]

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
