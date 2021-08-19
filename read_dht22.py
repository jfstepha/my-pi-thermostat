#!/usr/bin/python

#import urllib2
#import re
import time
import datetime
import sys
#import json
#import subprocess
#import os
import Adafruit_DHT

sensor = 22
pin = 17
rh, tempC = Adafruit_DHT.read_retry(sensor, pin)
if rh is not None and tempC is not None:
        temp = tempC * 1.8 + 32;
        print "temp:%0.3f,rh:%0.3f" % (temp, rh)
        f = open('indoortemp2','w')
        f.write("%0.3f" % temp)
        f.close()
else:   
        print 'Failed to get reading. Try again!'
