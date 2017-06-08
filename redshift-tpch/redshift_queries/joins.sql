--- joining spectrum.parts of q 3 & 5

--------- q3 ----------
select *
from
	spectrum.customer,
	spectrum.orders,
	spectrum.lineitem
where
	c_mktsegment = 'BUILDING'
	and c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and o_orderdate < date '1995-03-02'
	and l_shipdate > date '1995-03-02'
limit 1000;

-------------- q5 --------------
select *
from
	spectrum.customer,
	spectrum.orders,
	spectrum.lineitem,
	spectrum.supplier,
	spectrum.nation,
	spectrum.region
where
	c_custkey = o_custkey
	and l_orderkey = o_orderkey
	and l_suppkey = s_suppkey
	and c_nationkey = s_nationkey
	and s_nationkey = n_nationkey
	and n_regionkey = r_regionkey
	and r_name = 'AFRICA'
	and o_orderdate >= date '1994-01-01'
	and o_orderdate < date '1995-01-01'
limit 1000;