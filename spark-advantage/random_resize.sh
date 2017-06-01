## utility for randomly selection a percentage of a set of files using AWK. 
## produces .SMALL and .MEDIUM files which represent 1% and 50% of the original files, 
## respectively

set -x files $argv

for file in $files
	# 1%
	awk 'BEGIN {srand()} !/^$/ { if (rand() <= .01 || FNR==1) print $0}' $file > "$file.SMALL"
	# 50%
	awk 'BEGIN {srand()} !/^$/ { if (rand() <= .5 || FNR==1) print $0}' $file > "$file.MEDIUM"
end