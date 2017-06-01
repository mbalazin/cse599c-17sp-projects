
# coding: utf-8

# In[24]:

import pandas as pd
from sys import argv
import time

logfile = argv[1]
filesize = argv[2]


from pyspark import SparkConf, SparkContext, sql
from pyspark.sql import SQLContext

conf = SparkConf().setAppName("bench")
sc = SparkContext(conf=conf)

spark = sql.SparkSession(sc)



# 
# 
# # Spark Python Benchmark: Climate Data

# Get filenames together:

# In[15]:



# In[16]:

localprefix = "file:////Users/tony/Dropbox/Projects/UW/cse599c-17sp-projects/spark-advantage/data/"
s3prefix = "s3n://AKIAINKOQJAZEEJUID2A:njJVnsdYym7t0oRwPshgHv8VjUOr30ago8x1CxXD@sparkclim/"

if (sc.master.startswith('local')):
    prefix = localprefix
else:
    prefix = s3prefix


if(filesize == 'original'):
    tairfname     = "Tair_WA_nohead.csv"
    tsoilfname    = "Tsoil_WA_nohead.csv"
    tsurfacefname = "Tsurface_WA_nohead.csv"
elif (filesize == 'medium'):
    tairfname     = "Tair_WA_nohead.MEDIUM.csv"
    tsoilfname    = "Tsoil_WA_nohead.MEDIUM.csv"
    tsurfacefname = "Tsurface_WA_nohead.MEDIUM.csv"
elif (filesize == "small"):
    tairfname     = "Tair_WA_nohead.SMALL.csv"
    tsoilfname    = "Tsoil_WA_nohead.SMALL.csv"
    tsurfacefname = "Tsurface_WA_nohead.SMALL.csv"

startTime = time.time()

# Load into RDDs:
# 

# In[17]:

tairRDD = spark.read.csv(prefix+tairfname, header=True)
tsoilRDD = spark.read.csv(prefix+tsoilfname, header=True)
tsurfaceRFF = spark.read.csv(prefix+tsurfacefname, header=True)


# Join together the 

# In[18]:

tsurfaceRDD = tsurfaceRFF
joined = tairRDD.join(tsoilRDD, on=["datetime", " lat", " lon"]).join(tsurfaceRDD, on=["datetime", " lat", " lon"])

joined = joined.withColumn('lat', joined[' lat'].cast('float'))
joined = joined.drop(" lat")

joined = joined.withColumn('lon', joined[' lon'].cast('float'))
joined = joined.drop(" lon")

joined = joined.withColumn('Tair', joined[' Tair'].cast('float'))
joined = joined.drop(" Tair")

joined = joined.withColumn("Tsoil", joined[' Tsoil'].cast('float'))
joined = joined.drop(" Tsoil")

joined = joined.withColumn("Tsurface", joined[' Tsurface'].cast('float'))
joined = joined.drop(" Tsurface")

joined.printSchema()


# In[19]:

# uw bbox: -122.3236656189,47.6452100479,-122.2936248779,47.6640578596
seattle = joined.filter(joined.lon > -125.52)                .filter(joined.lon < -120.2)                .filter(joined.lat > 49.0)                .filter(joined.lat < 51.0)

mean = seattle.groupBy(['lon', 'lat']).agg({'Tair':'mean'})

data = mean.collect()


# In[20]:

data


# In[21]:

exptime = time.time()-startTime
with open(logfile, 'a') as log:
    log.write(str(exptime)+'\n')


# In[ ]:



