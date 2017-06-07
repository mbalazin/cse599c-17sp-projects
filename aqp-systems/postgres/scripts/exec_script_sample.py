import sys
import psycopg2
import time
import numpy as np

def tbl_clause(sample_type, sample_size):
    table = "LINEITEM "
    if sample_type is not None:
        table += "TABLESAMPLE " + sample_type + "(" + str(sample_size) + ")"
    return table

# A simple count query on the fact table
def query0(st=None, sp=None):
    return "SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_COST, AVG(L_QUANTITY) AS AVG_QTY FROM " + tbl_clause(st, sp) + ";"

# Here is a query with a filter on month
def query1(st=None, sp=None):
    return "SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_COST, AVG(L_QUANTITY) AS AVG_QTY FROM " + tbl_clause(st, sp) + " WHERE DATE_PART('month', L_RECEIPTDATE) = 8;"

# A simple group by count query on the fact table. Note that we have chose to
# group by month where the number of groups are known-apriori
def query2(st=None, sp=None):
    return "SELECT DATE_PART('month', L_RECEIPTDATE) AS MONTH, COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM " + tbl_clause(st, sp) + " GROUP BY MONTH ORDER BY MONTH;"

# Another group by query, but with join on SUPPLIER and LINEITEM tables
def query3(st=None, sp=None):
    return "SELECT S_NATIONKEY AS NATION, COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM " + tbl_clause(st, sp) + ", SUPPLIER WHERE L_SUPPKEY = S_SUPPKEY GROUP BY NATION ORDER BY NATION;"

def query4(st=None, sp=None):
    return "SELECT COUNT(*) AS NUM_ITEMS, SUM(L_QUANTITY) AS TOT_QTY, AVG(L_QUANTITY) AS AVG_QTY FROM " + tbl_clause(st, sp) + ", ORDERORDER WHERE L_ORDERKEY = O_ORDERKEY AND O_ORDERPRIORITY = '1-URGENT';"


def deploy(cur, q_str, answers_file, print_new_line=False):
  toc = time.time()
  cur.execute(q_str)
  tic = time.time()
  answers = cur.fetchall()
  for row in answers:
      for col in row:
          answers_file.write(str(col) + ", ")
      answers_file.write("\n")
  if print_new_line:
    answers_file.write("\n")
  return tic - toc;

dbname = 'skewed_big'
con = psycopg2.connect(dbname=dbname,
                       host='localhost',
                       port='5432',
                       user='guna',
                       password='guna')
sample_sizes = [0.1]
sample_types = ['BERNOULLI', 'SYSTEM']
query_answer_files = []
query_functions = [query0, query1, query2, query3, query4]

def open_answer_files():
    for query in range(0, 5):
        answer_file = open('results_' + dbname + '_' + str(query) + '.txt', 'w+')
        query_answer_files.append(answer_file)

def close_answer_files():
    for answer_file in query_answer_files:
        answer_file.close()

def deploy_all_queries(time_file):
    cur = con.cursor()
    for st in sample_types:
        for sp in sample_sizes:
            for qid in range(0, 5):
                query = query_functions[qid]
                query_str = query(st, sp)
                if qid == 2 or qid == 3:
                    time = deploy(cur, query_str, query_answer_files[qid], True)
                else:
                    time = deploy(cur, query_str, query_answer_files[qid])
                time_file.write(st + ", " + str(sp) + ", " + str(qid) + ", " + str(time) + "\n")
    cur.close()

open_answer_files()
with open('performance_' + dbname + '.txt', 'w+') as f:
    deploy_all_queries(f)
close_answer_files()
