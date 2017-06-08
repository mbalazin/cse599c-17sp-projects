-- q6
select
	sum(l_extendedprice * l_discount) as revenue
from
	lineitem
where
	l_shipdate >= date '1994-01-01'
	and l_shipdate < date '1996-01-01'
	and l_discount between 0.06 - 0.01 and 0.06 + 0.01
	and l_quantity < 24;

select * from orders
where o_totalprice < 1000.0
limit 100000;

select * from part
where p_retailprice < 1000.0
limit 100000;

select * from partsupp
where ps_availqty < 1000
limit 100000;

select * from supplier
where s_acctbal < 1000.0
limit 100000;