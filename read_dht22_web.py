#!/usr/bin/python

import urllib2
import re
import time
import datetime
import sys
import json
import subprocess
import os
import Adafruit_DHT

def getVal(varname):
    jsonurl = urllib2.urlopen("https://api.spark.io/v1/devices/normal_dentist/%s?access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6" % varname)
    text = json.loads(jsonurl.read())
    retval = text['result']
    return(retval)

FNULL = open(os.devnull,'w')
while 1:
    try:
        temp = getVal("temperature")
        rh = getVal("humidity")
        uptime = getVal("uptime")
        lsp = getVal("lsp")
        dht_fails = getVal("dht_fails")
        print "[%s] spark temp: %0.3f rh:%0.3f uptime:%0.0f lsp:%d dht:%d" % (datetime.datetime.now(), temp, rh, uptime, lsp, dht_fails)
        r = subprocess.call(["curl", "https://api.spark.io/v1/devices/normal_dentist/ping", "-d", "access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6", "-d", "args=1"], stdout=FNULL, stderr=subprocess.STDOUT)
        f = open('indoortemp','w')
        f.write("%0.3f" % temp)
        f.close()
    except KeyboardInterrupt:
        print "Keyboard interrupt"
        exit()
    except:
        print "[%s] exception:  " % (datetime.datetime.now() ), sys.exc_info()[0]

    try:
        sensor = 22
        pin = 17
        rh, tempC = Adafruit_DHT.read_retry(sensor, pin)
        if rh is not None and temp is not None:
                temp = tempC * 1.8 + 32;
                print "[%s] thermostat temp: %0.3f rh:%0.3f" % (datetime.datetime.now(), temp, rh)
                f = open('indoortemp2','w')
                f.write("%0.3f" % temp)
                f.close()
                time.sleep(30)
        else:   
                print 'Failed to get reading. Try again!'
    except KeyboardInterrupt:
        print "Keyboard interrupt"
        exit()
    except:
        print "[%s] exception:  " % (datetime.datetime.now() ), sys.exc_info()[0]
    time.sleep(30)
