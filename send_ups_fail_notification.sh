#!/bin/bash
# NOTE: the monuser user runs this, so it gets run out of the local directory on that account
tmpfile="/tmp/ups_"`date  +'%Y-%m-%d-%H%M%S.txt'`
echo "dumping to $tmpfile"
echo "***** UPS Power Status Change event *****" > $tmpfile
echo "***** Message: $1 " >> $tmpfile
echo "Date:" >> $tmpfile
date >> $tmpfile
echo "** UPS Status **" >> $tmpfile
upsc apc >> $tmpfile

cat $tmpfile | mailx -v -r "jfstepha@gmail.com" -s "UPS State Changed: $1" -S smtp="smtp.gmail.com:587" -S smtp-use-starttls -S smtp-auth=login -S smtp-auth-user="jfstepha@gmail.com" -S smtp-auth-password="xrkamtoyyflxrseo" -S ssl-verify=ignore jfstepha@gmail.com
