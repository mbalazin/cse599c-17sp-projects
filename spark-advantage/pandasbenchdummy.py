
# coding: utf-8

# In[1]:

import pandas as pd
import time
from sys import argv

logfile = argv[1]


# # Python Pandas Benchmark

# In[3]:
open(logfile, 'w')
exit()

prefix = "file:////Users/tony/Dropbox/Projects/UW/cse599c-17sp-projects/spark-advantage/data/"

tairfname = "Tair_WA_nohead"
tsoilfname = "Tsoil_nohead.csv"
tsurfacefname = "Tsurface_WA_nohead.csv"



startTime = time.time()



tair = pd.read_csv(prefix+tairfname)
tsoil = pd.read_csv(prefix+tsoilfname)
tsurface = pd.read_csv(prefix+tsurfacefname)

joined = tair.merge(tsoil, on=["datetime", " lat", " lon"]).merge(tsurface, on=["datetime", " lat", " lon"])

joined.columns = [name.strip() for name in joined.columns]
joined[['lat', 'lon']] = joined[['lat', 'lon']].apply(pd.to_numeric)

seattle = joined[(joined['lon'] > -125.52) & \
                 (joined['lon'] < -120.2)  & \
                 (joined['lat'] > 49.0)    & \
                 (joined['lat'] < 51.0)]

seattle.groupby(by=['lat', 'lon'])['Tair'].mean()

exptime = time.time() - startTime
with open(logfile, 'a') as log:
    log.write(str(exptime)+'\n')