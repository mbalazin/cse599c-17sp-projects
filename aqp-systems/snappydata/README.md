# How well can SnappyData handle approximate queries?
***Important Notice: This experiment was run in May of 2017, and at the time of the experiments, SnappyData was a newer system still being heavily developed. Therefore, the documentation did not have a ton of examples and did not explain the configuration options well. A lot of the problems I experience with SnappyData could likely have been fixed with help and tuning from someone more knowledgeable about the system.

### Overview
SnappyData

### Experiment Set Up
This is where I ran into the most problems with SnappyData. 

### Query Accuracy 
![][skewed-err] ![][unifrom-err]

### Runtime
![][skewed-sample-time] ![][unifrom-sample-time]
![][skewed-true-time] ![][unifrom-true-time]
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

