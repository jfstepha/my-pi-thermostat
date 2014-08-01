#!/usr/bin/python
#Based off the tutorial by adafruit here:
# http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software

import subprocess
import glob
import time

def getIndoorTemp():
    file = open("indoortemp", "r")
    indoorTemp = float(file.readline())
    file.close()
     
    return indoorTemp

def getIndoorTemp2():
    file = open("indoortemp2", "r")
    indoorTemp = float(file.readline())
    file.close()
     
    return indoorTemp
