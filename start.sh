#!/bin/bash

python app.py &

#python app.py

sleep 5

echo 'IMAGEDIR: '$IMAGEDIR
echo 'WATCHERDIR: '$WATCHERDIR

n=0

while true
do
    find $WATCHERDIR -name 'exp-*.tif' -type f -exec rm -f {} \;
    echo 'remove pass'

    n=$(( n+1 ))

    echo 'EXP: '$n
    sleep 2;

    # pids=""

    for i in `ls $IMAGEDIR/*.tif | sort -R`
    do
        filename=`basename $i`;
        exp=$(printf %03d $n);
       	# cp $i $WATCHERDIR'/exp-'$exp'-'$filename; # & pids="$pids $!";
        ln $i $WATCHERDIR'/exp-'$exp'-'$filename; # & pids="$pids $!";
    done

    #for pid in $pids; do
    #  wait "$pid"
    #done

    echo 'copy pass'

    sleep 5;

    if [ $n -eq 100 ]
    then
	#find $WATCHERDIR -name 'exp-*.tif' -type f -exec rm -fv {} \;

	#pids=""

    	#for i in `ls $WATCHERDIR/*.tif`
    	#do
    	#    rm -rf $i; # & pids="$pids $!";
    	#done

    	#for pid in $pids; do
    	#    wait "$pid"
    	#done

        n=0

    	#echo 'remove pass'
    fi

    # sleep 5;
done
