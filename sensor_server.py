#!/usr/bin/python

import socket
import threading
import struct
import string
import time
import urllib2
import re
import time
import datetime
import sys
import json
import subprocess
import os
import Adafruit_DHT
import datetime
import serial

FNULL = open(os.devnull,'w')
############################################################################
############################################################################
class Sensor():
############################################################################
############################################################################

    ################################################################
    def __init__(self, name, hw_type, domain="blank", sensor_type="temp"):
    ################################################################
        # sensor type is temp or thermo_disp.  (What kind of sensors are on the sensor)
        # hw_tyoe is spark, local_dht, sum or thermo_disp (what kind or hardware is driving the sensor) 
        self.name = name
        self.uptime = 0
        self.domain = domain
        self.lsu = 10000
        self.lsp = 0
        self.hw_type = hw_type
        self.name = name
        self.port = None
        # only valid for summarys:
        self.N = 0
        self.total = 0
        self.sensor_type = sensor_type
        if sensor_type == "temp" or sensor_type == "remote_disp":
            self.temp = -100
            self.rh = -100
        if sensor_type == "remote_disp":
            self.lastmotion = 0
            self.port = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=3.0)
            print "serial port initial status:"
            for i in range(0,5):
                rcv = self.port.read(100);
                print rcv;

            

    ################################################################
    def get_dict(self):
    ################################################################
       if self.sensor_type == "temp":
           return ( { 'temp' : self.temp, 'rh' : self.rh, 'lsu' : self.lsu, 'domain' : self.domain, 'uptime' : self.uptime, 'lsp' : self.lsp } )
       if self.sensor_type == "remote_disp":
           return ( { 'temp' : self.temp, 'rh' : self.rh, 'lsu' : self.lsu, 'domain' : self.domain, 'uptime' : self.uptime, 'lsp' : self.lsp, 'lastmotion' : self.lastmotion} )


    ################################################################
    def __str__(self):
    ################################################################
       if self.sensor_type == "temp":
           return ( "%s : { temp: %0.1f rh: %0.1f lsu: %d domain: %s uptime: %d lsp: %d sensor_type: %s hw_type: %s } " % (self.name, self.temp, self.rh, self.lsu, self.domain, self.uptime, self.lsp, self.sensor_type, self.hw_type) )
       elif self.sensor_type == "remote_disp":
           return ( "%s : { temp: %0.1f rh: %0.1f lsu: %d domain: %s uptime: %d lsp: %d sensor_type: %s hw_type: %s lastmotion: %d } " % (self.name, self.temp, self.rh, self.lsu, self.domain, self.uptime, self.lsp, self.sensor_type, self.hw_type, self.lastmotion) )


    ################################################################
    def update(self):
    ################################################################
        if self.hw_type == "spark":
            self.updateSpark()
        elif self.hw_type == "local_dht":
            self.updateLocalDHT()
        elif self.hw_type == "remote_disp":
            self.updateRemoteDisp()

    ################################################################
    def getSparkVal(self,varname):
    ################################################################
        jsonurl = urllib2.urlopen("https://api.spark.io/v1/devices/normal_dentist/%s?access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6" % varname)
        text = json.loads(jsonurl.read())
        retval = text['result']
        return(retval)

    ################################################################
    def updateSpark(self):
    ################################################################
            try:
                #####################################################
                # read spark core
                #####################################################
                self.temp = self.getSparkVal("temperature")
                self.rh = self.getSparkVal("humidity")
                self.uptime = self.getSparkVal("uptime")
                self.lsp = self.getSparkVal("lsp")
                self.lsu = 0

                r = subprocess.call(["curl", "https://api.spark.io/v1/devices/normal_dentist/ping", "-d", "access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6", "-d", "args=1"], stdout=FNULL, stderr=subprocess.STDOUT)

                print "[%s] spark: %s " % (datetime.datetime.now(), str(self))
            except KeyboardInterrupt:
                print "Keyboard interrupt"
                exit()
            except:
                print "[%s] spark exception:  " % (datetime.datetime.now() ), sys.exc_info() 

    ################################################################
    def updateRemoteDisp(self):
    ################################################################
        self.lsu += 1
        retries = 0
        rcv = ""
        while ( str( rcv ).find("ok... got") == -1 and retries < 10):
            self.port.write("1 80\r\n");
            rcv = self.port.readline();
            print "[%s] %s received: %s" % (datetime.datetime.now(), self.name, str(rcv).strip())
            self.port.flush()
            retries += 1
        if str(rcv).find("ok... got") > -1:      
            l = str(rcv).split()
            self.temp = float( l[9].split(":")[1] )
            self.rh = float( l[10].split(":")[1] )
            self.lsu = int( l[12] )
            self.lastmotion = int( l[14] )
            self.uptime = int( l[16] )
            self.lsu = 0
            print "[%s] %s: %s" %(datetime.datetime.now(), self.name, str(self))
        else:
            print "[%s] failed after retries: %d" % (datetime.datetime.now(), retries)
        


    ################################################################
    def updateLocalDHT(self):
    ################################################################

            #########################################################
            # read local pi thermostat 
            #########################################################
            try:
                sensor = 22
                pin = 17
                humidity, tempC = Adafruit_DHT.read_retry(sensor, pin)
                if humidity is not None and tempC is not None:
                    self.temp = tempC * 1.8 + 32;
                    self.rh = humidity
                    self.uptime += 1
                    self.lsp = 0
                    self.lsu = 0

                print "[%s] thermo_lr: %s " % (datetime.datetime.now(), str(self))

                self.uptime += 1
            except KeyboardInterrupt:
                print "Keyboard interrupt"
                exit()
            except:
                print "[%s] exception:  " % (datetime.datetime.now() ), sys.exc_info()[0]


############################################################################
############################################################################
class loopThread(threading.Thread):
############################################################################
############################################################################

    ################################################################
    def __init__(self):
    ################################################################
        threading.Thread.__init__(self)
        self.loopcount=0
        self.msgcount = 0;
        # lsu = loops since update  (how long since we've received an update from this sensor)
        # lsp = loops since ping (how long this sensor thinks it's been since it heard from us)
        self.sensors = {}
        self.sensors['spark'] = Sensor('spark', 'spark', 'LR') 
        self.sensors['thermo_LR'] = Sensor('thermo_lr', 'local_dht', 'LR' )
        self.sensors['remote_MBR'] = Sensor('remote_MBR', 'remote_disp', 'LR', "remote_disp")
        self.sensors['sum_LR'] = Sensor('sum_LR', 'sum', 'LR')
        self.domains = ['LR']

        for keys in self.sensors:
            print "[%s] initial: %s: %s " % (datetime.datetime.now(), keys, str(self.sensors[keys]))
        


    ################################################################
    def run(self):
    ################################################################
        while 1:
           
            # initialize the average calc stats 
            for d in self.domains:
                self.sensors[ "sum_%s" % d ].N = 0
                self.sensors[ "sum_%s" % d ].total = 0
             
            for keys in self.sensors:

                # update the sensors
                self.sensors[keys].lsu += 1
                self.sensors[keys].update()

                # update the averages
                d = self.sensors[keys].domain
                if keys.find("sum") == -1 and self.sensors[keys].sensor_type == "temp":
                    self.sensors[ "sum_%s" % d ].N += 1
                    self.sensors[ "sum_%s" % d ].total += self.sensors[keys].temp
 
            # calculate the averages
            for d in self.domains:
                t = self.sensors[ "sum_%s" % d ].total 
                N = self.sensors[ "sum_%s" % d ].N
                self.sensors[ "sum_%s" % d ].temp = t / N
                self.sensors[ "sum_%s" % d ].lsu = 0
                self.sensors[ "sum_%s" % d ].uptime += 1

                print "[%s] sum: %s " % (datetime.datetime.now(), str(self.sensors['sum_LR']))

                f = open('indoortemp','w')
                f.write("%0.3f" % self.sensors['sum_LR'].temp)
                f.close()

            time.sleep(10)
                

