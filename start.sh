#!/bin/bash

python app.py &

sleep 5

echo 'IMAGEDIR: '$IMAGEDIR
echo 'WATCHERDIR: '$WATCHERDIR

mkdir -p $WATCHERDIR'/tmp';

n=0

#function rm_tmp {
#    find $WATCHERDIR'/tmp' -mindepth 1 -type d -exec rm -rf {} \;
#}

while true
do
    #last_exp=$(printf %03d $n);

    n=$(( n+1 ))

    exp=$(printf %03d $n);

    echo 'EXP: '$n
    sleep 2;

    for i in `ls $IMAGEDIR/*.tif | sort -R`
    do
        mkdir -p $WATCHERDIR'/tmp/'$exp;

        filename=`basename $i`; 
	file=$WATCHERDIR'/tmp/'$exp'/exp-'$exp'-'$filename;

	if [ -f "$file" ]
	then
	    rm -r $file
	fi

        ln $i $file;
        # cp $i $file;
    done

    echo 'copy pass'
    # to allow 5 seconds of navigation
    sleep 5;

    # remove last exposure
    #if [ $last_exp != "000" ]
    #then
    # 	rm -r $WATCHERDIR'/tmp/'$last_exp;
    #fi

    if [ $n -eq 10 ]
    then
        n=0
        echo 'restarting simulation...'
        echo 'done'
    fi

done
