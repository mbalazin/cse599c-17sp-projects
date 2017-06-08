create table customer(
  c_custkey int ,
  c_name varchar(64) ,
  c_address varchar(64) ,
  c_nationkey int ,
  c_phone varchar(64) ,
  c_acctbal decimal(13, 2) ,
  c_mktsegment varchar(64) ,
  c_comment varchar(120) ,
  skip varchar(64)
);

create table lineitem(
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
);
create table nation(
  n_nationkey int ,
  n_name varchar(64) ,
  n_regionkey int ,
  n_comment varchar(160) ,
  skip varchar(64)
);
create table orders(
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
);

create table part(
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
);
create table partsupp(
  ps_partkey int ,
  ps_suppkey int ,
  ps_availqty int ,
  ps_supplycost decimal(13, 2) ,
  ps_comment varchar(200) ,
  skip varchar(64)
);
create table region(
  r_regionkey int ,
  r_name varchar(64) ,
  r_comment varchar(160) ,
  skip varchar(64)
);
create table supplier(
  s_suppkey int ,
  s_name varchar(64) ,
  s_address varchar(64) ,
  s_nationkey int ,
  s_phone varchar(18) ,
  s_acctbal decimal(13, 2) ,
  s_comment varchar(105) ,
  skip varchar(64)
);
