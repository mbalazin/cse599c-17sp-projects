## runs Pandas benchmark
## arguments: <number of trials> <filesize: small, medium, original>

set -x FILESIZE $argv[2]
set -x MASTER $argv[3]
set -x LOCALITY 'placeholder'
if contains 'local' $MASTER
	set LOCALITY local
else
	set LOCALITY remote
end
set -x RUNID (date "+%F-%T").$FILESIZE.$LOCALITY.sparktest 

set -x PROF_INTERVAL 0.5


mkdir $RUNID


for run in (seq $argv[1])
	if [ $FILESIZE = 'small' ]
		set -x PROF_INTERVAL 0.01
	end
	./Syrupy/scripts/syrupy.py -i $PROF_INTERVAL --no-raw-process-log --poll-command='python3.5|java' -t {$RUNID}/{$RUNID}_{$run}.profile > /dev/null 2>&1 &
	set LOGPID %syrupy
	echo -n Run $run started...
	./spark-2.0.0-bin-hadoop2.4/bin/spark-submit --master $MASTER sparkbench.py /Users/tony/Dropbox/Projects/UW/cse599c-17sp-projects/spark-advantage/$RUNID/$RUNID.results $FILESIZE
	echo complete.
	sleep 2
	kill -SIGINT $LOGPID

end

./Syrupy/scripts/syrupy-peak.py (ls {$RUNID}/{$RUNID}_*.profile.ps.log) > "$RUNID/$RUNID.profile.aggregate"

Echo Time Data in $RUNID.results

