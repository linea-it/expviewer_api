#!/bin/bash

python app.py &

sleep 5

echo 'IMAGEDIR: '$IMAGEDIR
echo 'WATCHERDIR: '$WATCHERDIR

mkdir -p $WATCHERDIR'/tmp';

n=0

find $WATCHERDIR'/tmp' -mindepth 1 -type d -exec rm -rf {} \;

while true
do

    n=$(( n+1 ))

    echo 'EXP: '$n
    sleep 2;

    for i in `ls $IMAGEDIR/*.tif | sort -R`
    do
        filename=`basename $i`;
        exp=$(printf %03d $n);
       	
        mkdir -p $WATCHERDIR'/tmp/'$exp;
        ln $i $WATCHERDIR'/tmp/'$exp'/exp-'$exp'-'$filename;
        # cp $i $WATCHERDIR'/'$exp'/exp-'$exp'-'$filename;
    done

    echo 'copy pass'

    sleep 5;

    if [ $n -eq 10 ]
    then
        n=0
        echo 'restarting simulation...'
        
        sleep 5;
        find $WATCHERDIR'/tmp' -mindepth 1 -type d -exec rm -rf {} \;
        
        echo 'removed directories'
        echo 'done'
    fi

done
