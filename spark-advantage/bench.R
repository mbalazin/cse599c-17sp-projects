library(sparklyr)
library(dplyr)
library(methods)

#args = commandArgs(trailingOnly = T)

args = list('away')

if (args[1] == 'local'){
  local = TRUE
} else {
  local = FALSE
}

if (local){
  MASTER = 'local[*]' # local, all cores
  data_SM = ""
  data_MD = "file:///Users/tony/Dropbox/Projects/UW/cse599c-17sp-projects/spark-advantage/data/climfile"
  data_LG = "file:///Users/tony/Dropbox/Projects/UW/cse599c-17sp-projects/spark-advantage/data/largedata"
} else {
  MASTER = 'spark://ec2-54-186-44-97.us-west-2.compute.amazonaws.com:7077'
  data_MD = "s3n://AKIAINKOQJAZEEJUID2A:njJVnsdYym7t0oRwPshgHv8VjUOr30ago8x1CxXD@sparkclim/file_nohead"
  data_LG = "s3n://AKIAINKOQJAZEEJUID2A:njJVnsdYym7t0oRwPshgHv8VjUOr30ago8x1CxXD@sparkclim/largedata"
}
 

print("Starting Spark experimentation...")

sc = spark_connect(master=MASTER, spark_home = "~/Dropbox/Projects/UW/cse599c-17sp-projects/spark-advantage/spark-2.0.0-bin-hadoop2.4/", 
                   version = '2.0.0')

for (datafile in list("small", "medium", "large")){
  if (datafile == 'small') continue();
  
  print(paste("loading file:", datafile))
  starttime = proc.time()
  sparkTable = spark_read_csv(sc, 'table', data_MD)
  print((proc.time() - starttime))
  
  print(paste("counting rows file:", datafile))
  starttime = proc.time()
  print(nrow(sparkTable))
  print(proc.time() - starttime)
  
  print(paste("done file ", datafile))
}

spark_disconnect_all()


