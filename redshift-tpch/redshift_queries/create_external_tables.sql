create external schema spectrum
from data catalog
database 'spectrumdb'
iam_role '___'
create external database if not exists;


create external table spectrum.customer(
  c_custkey int ,
  c_name varchar(64) ,
  c_address varchar(64) ,
  c_nationkey int ,
  c_phone varchar(64) ,
  c_acctbal decimal(13, 2) ,
  c_mktsegment varchar(64) ,
  c_comment varchar(120) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/customer/';


create external table spectrum.lineitem(
  l_orderkey int ,
  l_partkey int ,
  l_suppkey int ,
  l_linenumber int ,
  l_quantity int ,
  l_extendedprice decimal(13, 2) ,
  l_discount decimal(13, 2) ,
  l_tax decimal(13, 2) ,
  l_returnflag varchar(64) ,
  l_linestatus varchar(64) ,
  l_shipdate datetime ,
  l_commitdate datetime ,
  l_receiptdate datetime ,
  l_shipinstruct varchar(64) ,
  l_shipmode varchar(64) ,
  l_comment varchar(64) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/lineitem/';

create external table spectrum.nation(
  n_nationkey int ,
  n_name varchar(64) ,
  n_regionkey int ,
  n_comment varchar(160) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/nation/';

create external table spectrum.orders(
  o_orderkey int ,
  o_custkey int ,
  o_orderstatus varchar(64) ,
  o_totalprice decimal(13, 2) ,
  o_orderdate datetime ,
  o_orderpriority varchar(15) ,
  o_clerk varchar(64) ,
  o_shippriority int ,
  o_comment varchar(80) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/order/';

create external table spectrum.part(
  p_partkey int ,
  p_name varchar(64) ,
  p_mfgr varchar(64) ,
  p_brand varchar(64) ,
  p_type varchar(64) ,
  p_size int ,
  p_container varchar(64) ,
  p_retailprice decimal(13, 2) ,
  p_comment varchar(64) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/part/';

create external table spectrum.partsupp(
  ps_partkey int ,
  ps_suppkey int ,
  ps_availqty int ,
  ps_supplycost decimal(13, 2) ,
  ps_comment varchar(200) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/partsupp/';

create external table spectrum.region(
  r_regionkey int ,
  r_name varchar(64) ,
  r_comment varchar(160) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/region/';

create external table spectrum.supplier(
  s_suppkey int ,
  s_name varchar(64) ,
  s_address varchar(64) ,
  s_nationkey int ,
  s_phone varchar(18) ,
  s_acctbal decimal(13, 2) ,
  s_comment varchar(105) ,
  skip varchar(64)
)
row format delimited
fields terminated by '|'
stored as textfile
location 's3://tpch-spec/10GB/supplier/';
