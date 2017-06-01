## runs Pandas benchmark
## arguments: <number of trials> <filesize: small, medium, original>

set -x FILESIZE $argv[2]
set -x RUNID (date "+%F-%T").$FILESIZE.pandastest 
set -x PROF_INTERVAL 0.5

mkdir $RUNID

for run in (seq $argv[1])
	if test $FILESIZE -eq 'small' 
		set -x PROF_INTERVAL 0.01
	end
	./Syrupy/scripts/syrupy.py -i $PROF_INTERVAL --no-raw-process-log -c 'python3 pandasbench.py' -t {$RUNID}/{$RUNID}_{$run}.profile > /dev/null 2>&1 &
	set LOGPID %1
	echo -n Run $run started...
	python3 pandasbench.py $RUNID/$RUNID.results $FILESIZE
	echo complete.
	sleep 2
	kill -SIGINT $LOGPID

end

./Syrupy/scripts/syrupy-peak.py (ls {$RUNID}/{$RUNID}_*.profile.ps.log) > "$RUNID/$RUNID.profile.aggregate"

echo Time Data in $RUNID.results

