#!/bin/bash

if ping -c1 -W1 $1 > /tmp/ping.$1.txt 2>&1
then 
    grep -Po 'time=\K\d+\.*\d*' /tmp/ping.$1.txt
else 
    echo 2000
fi


