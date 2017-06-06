load_str = """DROP TABLE IF EXISTS PART CASCADE;
CREATE TABLE PART (

    P_PARTKEY       BIGINT PRIMARY KEY,
    P_NAME          VARCHAR(55),
    P_MFGR          CHAR(25),
    P_BRAND         CHAR(10),
    P_TYPE          VARCHAR(25),
    P_SIZE          INTEGER,
    P_CONTAINER     CHAR(10),
    P_RETAILPRICE   DECIMAL,
    P_COMMENT       VARCHAR(23)
);

DROP TABLE IF EXISTS SUPPLIER CASCADE;
CREATE TABLE SUPPLIER (
    S_SUPPKEY       BIGINT PRIMARY KEY,
    S_NAME          CHAR(25),
    S_ADDRESS       VARCHAR(40),
    S_NATIONKEY     BIGINT NOT NULL, -- references N_NATIONKEY
    S_PHONE         CHAR(15),
    S_ACCTBAL       DECIMAL,
    S_COMMENT       VARCHAR(101)
);

DROP TABLE IF EXISTS CUSTOMER CASCADE;
CREATE TABLE CUSTOMER (
    C_CUSTKEY       BIGINT PRIMARY KEY,
    C_NAME          VARCHAR(25),
    C_ADDRESS       VARCHAR(40),
    C_NATIONKEY     BIGINT NOT NULL, -- references N_NATIONKEY
    C_PHONE         CHAR(15),
    C_ACCTBAL       DECIMAL,
    C_MKTSEGMENT    CHAR(10),
    C_COMMENT       VARCHAR(117)
);

DROP TABLE IF EXISTS ORDERORDER CASCADE;
CREATE TABLE ORDERORDER (
    O_ORDERKEY      BIGINT PRIMARY KEY,
    O_CUSTKEY       BIGINT NOT NULL, -- references C_CUSTKEY
    O_ORDERSTATUS   CHAR(1),
    O_TOTALPRICE    DECIMAL,
    O_ORDERDATE     DATE,
    O_ORDERPRIORITY CHAR(15),
    O_CLERK         CHAR(15),
    O_SHIPPRIORITY  INTEGER,
    O_COMMENT       VARCHAR(79)
);

DROP TABLE IF EXISTS LINEITEM CASCADE;
CREATE TABLE LINEITEM (
    L_ORDERKEY      BIGINT NOT NULL, -- references O_ORDERKEY
    L_PARTKEY       BIGINT NOT NULL, -- references P_PARTKEY (compound fk to PARTSUPP)
    L_SUPPKEY       BIGINT NOT NULL, -- references S_SUPPKEY (compound fk to PARTSUPP)
    L_LINENUMBER    INTEGER,
    L_QUANTITY      DECIMAL,
    L_EXTENDEDPRICE DECIMAL,
    L_DISCOUNT      DECIMAL,
    L_TAX           DECIMAL,
    L_RETURNFLAG    CHAR(1),
    L_LINESTATUS    CHAR(1),
    L_SHIPDATE      DATE,
    L_COMMITDATE    DATE,
    L_RECEIPTDATE   DATE,
    L_SHIPINSTRUCT  CHAR(25),
    L_SHIPMODE      CHAR(10),
    L_COMMENT       VARCHAR(44),
    PRIMARY KEY (L_ORDERKEY, L_LINENUMBER)
);

DROP TABLE IF EXISTS NATION CASCADE;
CREATE TABLE NATION (
    N_NATIONKEY     BIGINT PRIMARY KEY,
    N_NAME          CHAR(25),
    N_REGIONKEY     BIGINT NOT NULL,  -- references R_REGIONKEY
    N_COMMENT       VARCHAR(152)
);

DROP TABLE IF EXISTS REGION CASCADE;
CREATE TABLE REGION (
    R_REGIONKEY BIGINT PRIMARY KEY,
    R_NAME      CHAR(25),
    R_COMMENT   VARCHAR(152)
);

copy CUSTOMER from 's3://uwdb/tpch/skewed/{}GB/customer.tbl'
iam_role 'arn:aws:iam::417102298890:role/RedshiftCopyUnload'
delimiter '|';

copy LINEITEM from 's3://uwdb/tpch/skewed/{}GB/lineitem.tbl'
iam_role 'arn:aws:iam::417102298890:role/RedshiftCopyUnload'
delimiter '|';

copy NATION from 's3://uwdb/tpch/skewed/{}GB/nation.tbl'
iam_role 'arn:aws:iam::417102298890:role/RedshiftCopyUnload'
delimiter '|';

copy ORDERORDER from 's3://uwdb/tpch/skewed/{}GB/order.tbl'
iam_role 'arn:aws:iam::417102298890:role/RedshiftCopyUnload'
delimiter '|';

copy PART from 's3://uwdb/tpch/skewed/{}GB/part.tbl'
iam_role 'arn:aws:iam::417102298890:role/RedshiftCopyUnload'
delimiter '|';

copy REGION from 's3://uwdb/tpch/skewed/{}GB/region.tbl'
iam_role 'arn:aws:iam::417102298890:role/RedshiftCopyUnload'
delimiter '|';

copy SUPPLIER from 's3://uwdb/tpch/skewed/{}GB/supplier.tbl'
iam_role 'arn:aws:iam::417102298890:role/RedshiftCopyUnload'
delimiter '|';

"""

load_str_10 = load_str.format(10, 10, 10, 10, 10, 10, 10)
load_str_100 = load_str.format(100, 100, 100, 100, 100, 100, 100)


approx_queries = []

approx_queries.append('''SELECT APPROXIMATE COUNT (DISTINCT L_PARTKEY) FROM LINEITEM;''')
approx_queries.append('''SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, APPROXIMATE COUNT(DISTINCT L_PARTKEY) FROM LINEITEM GROUP BY MONTH ORDER BY MONTH;''')
approx_queries.append('''SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, APPROXIMATE COUNT(DISTINCT L_PARTKEY) FROM LINEITEM, ORDERORDER WHERE L_ORDERKEY = O_ORDERKEY GROUP BY MONTH ORDER BY MONTH;''')
approx_queries.append('''SELECT APPROXIMATE PERCENTILE_DISC (0.5) WITHIN GROUP (ORDER BY L_EXTENDEDPRICE) FROM LINEITEM;''')
approx_queries.append('''SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, APPROXIMATE PERCENTILE_DISC (0.5) WITHIN GROUP (ORDER BY L_EXTENDEDPRICE) FROM LINEITEM GROUP BY MONTH ORDER BY MONTH;''')
approx_queries.append('''SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, APPROXIMATE PERCENTILE_DISC (0.5) WITHIN GROUP (ORDER BY L_EXTENDEDPRICE) FROM LINEITEM, ORDERORDER WHERE L_ORDERKEY = O_ORDERKEY GROUP BY MONTH ORDER BY MONTH;''')

exact_queries = []

exact_queries.append('''SELECT COUNT (DISTINCT L_PARTKEY) FROM LINEITEM;''')
exact_queries.append('''SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, COUNT(DISTINCT L_PARTKEY) FROM LINEITEM GROUP BY MONTH ORDER BY MONTH;''')
exact_queries.append('''SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, COUNT(DISTINCT L_PARTKEY) FROM LINEITEM, ORDERORDER WHERE L_ORDERKEY = O_ORDERKEY GROUP BY MONTH ORDER BY MONTH;''')
exact_queries.append('''SELECT MEDIAN(L_EXTENDEDPRICE) FROM LINEITEM;''')
exact_queries.append('''SELECT DATE_PART(mon, L_RECEIPTDATE) AS MONTH, MEDIAN(L_EXTENDEDPRICE) FROM LINEITEM GROUP BY MONTH ORDER BY MONTH;''')
exact_queries.append('''SELECT DATE_PART(mon, O_ORDERDATE) AS MONTH, MEDIAN(L_EXTENDEDPRICE) FROM LINEITEM, ORDERORDER WHERE L_ORDERKEY = O_ORDERKEY GROUP BY MONTH ORDER BY MONTH;''')


import sys
import psycopg2
import time
import numpy as np

def deploy(cur, q_str, repeats, display):
  times = np.zeros(repeats)
  answers = ()
  for i in range(repeats):
    toc = time.time()
    cur.execute(q_str)
    tic = time.time()
    if i == repeats - 1:
        answers = cur.fetchall()
    
    times[i] = tic - toc
    
    if display:
      print cur.fetchall()
  return [times, answers]


con = psycopg2.connect(dbname='tpch',
                       host='aqp599.ch4marptuzyj.us-west-2.redshift.amazonaws.com',
                       port='5439',
                       user='walter',
                       password='password')
cur = con.cursor()
cur.execute(load_str_10)
con.commit()


approx_runtimes = []
exact_runtimes = []
        
with open('exact_results_10.txt', 'a+') as f:
    results_100 = []
    for q in exact_queries:
        x = deploy(cur=cur, q_str=q, repeats=6, display=False)
        results_100.append(x)
        f.write(str(q) + '\n')
        f.write("{}".format(x))
        f.write('\n\n')

with open('approx_results_10.txt', 'a+') as f:
    results_100 = []
    for q in approx_queries:
        x = deploy(cur=cur, q_str=q, repeats=6, display=False)
        results_100.append(x)
        f.write(str(q) + '\n')
        f.write("{}".format(x))
        f.write('\n\n')

con.close()





con = psycopg2.connect(dbname='tpch',
                       host='aqp599.ch4marptuzyj.us-west-2.redshift.amazonaws.com',
                       port='5439',
                       user='walter',
                       password='password')
cur = con.cursor()
cur.execute(load_str_100)
con.commit()

approx_runtimes = []
exact_runtimes = []
        
with open('exact_results_100.txt', 'a+') as f:
    results_100 = []
    for q in exact_queries:
        x = deploy(cur=cur, q_str=q, repeats=6, display=False)
        results_100.append(x)
        f.write(str(q) + '\n')
        f.write("{}".format(x))
        f.write('\n\n')

with open('approx_results_100.txt', 'a+') as f:
    results_100 = []
    for q in approx_queries:
        x = deploy(cur=cur, q_str=q, repeats=6, display=False)
        results_100.append(x)
        f.write(str(q) + '\n')
        f.write("{}".format(x))
        f.write('\n\n')

con.close()






