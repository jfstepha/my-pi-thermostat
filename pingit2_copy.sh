#!/bin/bash

if ping -c1 -W1 $1 > /tmp/ping.$1.txt 2>&1
then 
    { time ping -c1 -w1 $1 > /dev/null; }  2>&1 | grep -Po 'stddev = \K\d+\.\d+' /tmp/ping.$1.txt
else 
    echo 2000
fi


