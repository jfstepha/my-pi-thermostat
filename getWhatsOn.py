#!/usr/bin/python
import os
import subprocess
import re
import ConfigParser

def getWhatsOn():                                                                                                                                            
    heatStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(0) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())    
    coolStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(1) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())        
    fanStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(4) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())        
                                                                                                                                                            
    print "heatStatus: %d" % heatStatus
    print "coolStatus: %d" % coolStatus
    print "fanStatus: %d" % fanStatus

if __name__ == "__main__":
    getWhatsOn()
