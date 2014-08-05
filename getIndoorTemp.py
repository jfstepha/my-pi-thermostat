#!/usr/bin/python
#Based off the tutorial by adafruit here:
# http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software

import subprocess
import glob
import time
import urllib2
import json

def getIndoorTemp():
    jsonurl = urllib2.urlopen("http://localhost/_liveSensorValue/sum_LR/temp")
    return float(json.loads(jsonurl.read()))

def getIndoorTemp2():
    jsonurl = urllib2.urlopen("http://localhost/_liveSensorValue/thermo_LR/temp")
    return float(json.loads(jsonurl.read()))
