# How well can REDSHIFT handle approximate queries?
### Average Runtime
![][zipf10-avg] ![][zipf100-avg]
![][unif10-avg] ![][unif100-avg]
***
### Runtime Stard Deviation
![][zipf10-std] ![][zipf100-std]
![][unif10-std] ![][unif100-std]
***
### Approximate Query Error
(average error taken over group-by cells if applicable)

|Query | Zipf 10         | Zipf 100       | Unif 10         | Unif 100        |
| -----| --------------- | -------------- | --------------- | --------------- |
| q1   | 0.0001446217715 | 0.005755668202 | 0.000106        | 0.00537945      |
| q2   | 0.002897582032  | 0.001415359489 | 0.0002587521649 | 0.003686796976  |
| q3   | 0.004168386307  | 0.001030289057 | 0.0002134292575 | 0.00421623532   |
| q4   | 0.0002548925203 | 0.000820815891 | 0.000517471471  | 0.0006265493476 |
| q5   | 0.0002548925203 | 0.000820815891 | 0.000517471471  | 0.0006265493476 |
| q6   | 0.002108891085  | 0.001907817179 | 0.008647518662  | 0.008351887156  |
***

## Results
Following are the links to Google Sheets for the raw runtimes for the Zipfian and Uniform Benchmark Results

* [Zipfian Benchmark Results](https://docs.google.com/spreadsheets/d/1SnzAy3DHXxXw4LXwEG8gyT7TX4orwsZ50hI2_Xgmy4s/pubhtml)
* [Uniform Benchmark Results](https://docs.google.com/spreadsheets/d/1LC7m6qt47X9XNNe8b3bl-m9JwAVov924DV-b17X2mlw/pubhtml)

## Author Notes
The experiments and analysis was done by [Walter Cai](wzcai.github.io). Feel free to [mail](mailto:walter@cs.washington.edu) him for any further details.

## Queries
q1:
```
SELECT COUNT (DISTINCT L_PARTKEY)
FROM LINEITEM;
```
q2:
```
SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, COUNT(DISTINCT L_PARTKEY)
FROM LINEITEM
GROUP BY MONTH
ORDER BY MONTH;
```
q3:
```
SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, COUNT(DISTINCT L_PARTKEY)
FROM LINEITEM, ORDERORDER
WHERE L_ORDERKEY = O_ORDERKEY
GROUP BY MONTH
ORDER BY MONTH;
```
q4:
```
SELECT MEDIAN(L_EXTENDEDPRICE)
FROM LINEITEM;
```
q5:
```
SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, MEDIAN(L_EXTENDEDPRICE)
FROM LINEITEM
GROUP BY MONTH
ORDER BY MONTH;
```
q6:
```
SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, MEDIAN(L_EXTENDEDPRICE)
FROM LINEITEM, ORDERORDER
WHERE L_ORDERKEY = O_ORDERKEY
GROUP BY MONTH
ORDER BY MONTH;
```

[zipf10-avg]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=530882143&format=image
[zipf100-avg]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=1036452611&format=image
[unif10-avg]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=44203486&format=image
[unif100-avg]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=37376812&format=image

[zipf10-std]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=1222793937&format=image
[zipf100-std]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=79636558&format=image
[unif10-std]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=123212141&format=image
[unif100-std]: https://docs.google.com/spreadsheets/d/1_VVatAB6AlGAifh-LYmf4iHSqPC8uFsRMbdJsv7M4kE/pubchart?oid=348046484&format=image
