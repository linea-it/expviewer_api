#!/bin/bash

#python simulate.py &
python app.py &

#python app.py

sleep 3

echo 'IMAGEDIR: '$IMAGEDIR
echo 'WATCHERDIR: '$WATCHERDIR

n=1
pids=""

find $WATCHERDIR -name 'exp-*.tif' -type f -exec rm -fv {} \;

while true
do
    echo 'EXP: '$n

    for i in `ls $IMAGEDIR/*.tif | sort -R`
    do
        filename=`basename $i`;
        exp=$(printf %03d $n);
        cp $i $WATCHERDIR'/exp-'$exp'-'$filename & pids="$pids $!";
    done

    for pid in $pids; do
      wait "$pid"
    done

    echo 'pass wait...'

    #sleep 10;

    n=$(( n+1 ))

    if [ $n -eq 4 ]
    then
        sleep 5
    	find $WATCHERDIR -name 'exp-*.tif' -type f -exec rm -fv {} \;
        n=1
    fi

    #sleep 10
done
