# How well can POSTGRES handle approximate queries?
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
