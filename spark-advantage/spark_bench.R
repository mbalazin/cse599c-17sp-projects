library(sparklyr)
library(dplyr)

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
  data_MD = "s3n://AKIAINKOQJAZEEJUID2A:njJVnsdYym7t0oRwPshgHv8VjUOr30ago8x1CxXD@sparkclim/Tair_output_shade-0_height-3_interval-hourly_aggregation-inst_times-19810101-19901231_created-2017-05-23-2341.csv"
  data_LG = "s3n://AKIAINKOQJAZEEJUID2A:njJVnsdYym7t0oRwPshgHv8VjUOr30ago8x1CxXD@sparkclim/largedata"
}
 

print("Starting Spark experimentation...")

sc = spark_connect(master=MASTER, spark_home = "~/Dropbox/Projects/UW/cse599c-17sp-projects/spark-advantage/spark-2.0.0-bin-hadoop2.4/", 
                   version = '2.0.0')

for (datafile in list("small", "medium", "large")){
  if (datafile == 'small') next;
  
  print(paste("loading file:", datafile))
  starttime = proc.time()
  sparkTable = spark_read_csv(sc, 'table', data_MD, memory=F)
  print((proc.time() - starttime))
  
  print(paste("counting rows file:", datafile))
  starttime = proc.time()
  print(nrow(sparkTable))
  print(proc.time() - starttime)
  
  
  sparkTable %>% 
    mutate(unixtime = unix_timestamp(as.character(datetime), "YYYYmmddhh")) %>%
    filter(unixtime < unix_timestamp('1981010101', 'YYYYmmddhh'), unixtime > unix_timestamp('1981020101', 'YYYYmmddhh')) %>% 
    count()
    

  

}

spark_disconnect_all()


