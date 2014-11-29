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
INIT = 70
SENSOR_READ_PERIOD = 10
SERIAL_CHECK_PERIOD = 0.1

############################################################################
############################################################################
class SensorHub():
############################################################################
############################################################################
    ################################################################
    def __init__(self):
    ################################################################
        try:
            self.port = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=3.0)
        except serial.serialutil.SerialException:
            self.port = serial.Serial("/dev/ttyUSB1", baudrate=57600, timeout=3.0)
            
        print "serial port initial status:"
        for i in range(0,5):
            rcv = self.port.read(100);
            print rcv;
        self.sensor_list = {};
        self.lsu = 0
    ################################################################
    def setSetpoint(self, setpoint, mode):
    ################################################################
        try:
            f = open("status", "w")
            f.write(str(setpoint) + "\n" + mode)
            f.close()
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "[%s] %s exception reading target file:  " % (self.name, datetime.datetime.now() ), sys.exc_info() 
            return None
    ################################################################
    def getSetpoint(self):
    ################################################################
        try:
            file = open("status", "r")
            oldTargetTemp = float(file.readline())
            mode = file.readline()
            file.close()
            return oldTargetTemp, mode;
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "[%s] %s exception reading target file:  " % (self.name, datetime.datetime.now() ), sys.exc_info() 
            return None
    ################################################################
    def my_re(self, re_str, str):
    ################################################################
        m = re.search( re_str, str)
        if m != None:
            return m.group(1)
        else:
            return None

    ################################################################
    def update(self):
    ############################ ####################################
        #try:
        if True:
            #print "[%s] updating hub" % datetime.datetime.now()
            self.lsu += 1

            while self.port.inWaiting() > 1:
                #print "DEBUG: waiting: %d" %self.port.inWaiting()
                oldTargetTemp, mode = self.getSetpoint()
                if oldTargetTemp == None:
                    return 0
                
                rcv = self.port.readline();
                print "[%s] hub received: %s" % (datetime.datetime.now(), str(rcv).strip())
                if str( rcv ).find("radio data available got") > -1:
                    id = int( self.my_re( "id:\s*(\d+)", rcv) )
                    #print "[%s] hub received a valid line id: %s in list: %s" % (datetime.datetime.now(),str(id), str( int(id) in self.sensor_list))
                    if id != None and int(id) in self.sensor_list:
                        #print "DEBUG: hub in list"
                        t_regex = " t:\\s*(\\d+\\.?\\d*)"
                        temp = self.my_re( t_regex, rcv)
                        #print "DEBUG: temp recieved: %s regex: %s string: %s" % (str(temp), t_regex, str(rcv).strip())
                        if temp != None: self.sensor_list[id].temp = float( temp )
                        
                        rh = self.my_re( "h:\s*(\d+\.?\d*)", rcv)
                        if rh != None: self.sensor_list[id].rh = float( rh )
                        
                        lsp = self.my_re( "lsp:\s*(\d+)", rcv)
                        if lsp != None: self.sensor_list[id].lsp = int( lsp )

                        lastmotion = self.my_re( "lastmotion:\s*(\d+)", rcv)
                        if lastmotion != None: self.sensor_list[id].lastmotion = int( lastmotion )
                        
                        uptime = self.my_re( "uptime:\s*(\d+)", rcv)
                        if uptime != None: 
                            self.sensor_list[id].uptime = int( uptime )
                            if self.sensor_list[id].uptime != self.sensor_list[id].prev_uptime:
                                self.sensor_list[id].prev_uptime = uptime
                                self.sensor_list[id].lsu = 0
                        
                        treq = self.my_re( "treq_pending:\s*(\d+)", rcv)
                        if treq != None: self.treq = int( treq )

                        treq_ack = self.treq
                        if self.treq > 50 and self.treq < 100:
                            newTargetTemp = self.treq
                            self.setSetpoint(newTargetTemp, mode)
                            self.port.write("%d %0.1f\r\n" % (id, newTargetTemp));
                        else:
                            self.port.write("%d %0.1f\r\n" % (id, oldTargetTemp));

                        #print "[%s] hub: id: %d treq: %s : %s" % (datetime.datetime.now(), id, str(self.treq), str(self.sensor_list[id]))
        try:
           pass
        except KeyboardInterrupt:
           print "Keyboard interrupt"
           exit()
        except:
           print "[%s] hub exception: %s  " % (datetime.datetime.now() , sys.exc_info() )
        
        


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
        self.prev_uptime = 0
        self.domain = domain
        self.lsu = 10000
        self.lsp = 0
        self.hw_type = hw_type
        self.name = name
        self.port = None
        # only valid for summaries:
        self.N = 0
        self.total = 0
        self.sensor_type = sensor_type
            
    ################################################################
    def __str__(self):
    ################################################################
    # default for sensor type of temp
           return ( "%s : { temp: %0.1f rh: %0.1f lsu: %d domain: %s uptime: %d lsp: %d sensor_type: %s hw_type: %s } " % (self.name, self.temp, self.rh, self.lsu, self.domain, self.uptime, self.lsp, self.sensor_type, self.hw_type) )
       
    ################################################################
    def getSetpoint(self):
    ################################################################
        try:
            file = open("status", "r")
            oldTargetTemp = float(file.readline())
            mode = file.readline()
            file.close()
            return oldTargetTemp, mode;
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "[%s] %s exception reading target file:  " % (self.name, datetime.datetime.now() ), sys.exc_info() 
            return None
    ################################################################
    def setSetpoint(self, setpoint, mode):
    ################################################################
        try:
            f = open("status", "w")
            f.write(str(setpoint) + "\n" + mode)
            f.close()
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "[%s] %s exception reading target file:  " % (self.name, datetime.datetime.now() ), sys.exc_info() 
            return None


############################################################################
############################################################################
class SensorLocalDHT(Sensor):
############################################################################
############################################################################
#    A local DHT22 sensor connected to the pi
    def __init__(self, name, domain="blank"):
        self.temp = INIT
        self.rh = INIT
        self.valid_temps = []
        self.valid_rhs = []
        self.all_temps = []
        self.all_rhs = []
        self.tolerance = 3.0
        self.history = 5
        Sensor.__init__(self, name, "local_dht", domain, "temp")

    ################################################################
    def get_dict(self):
    ################################################################
           return ( { 'temp' : self.temp, 'rh' : self.rh, 'lsu' : self.lsu, 'domain' : self.domain, 'uptime' : self.uptime, 'lsp' : self.lsp } )

    ################################################################
    def update(self):
    ################################################################

            #########################################################
            # read local pi thermostat 
            #########################################################
            #try:
                sensor = 22
                pin = 17
                humidity, tempC = Adafruit_DHT.read_retry(sensor, pin)
                if humidity is not None and tempC is not None:
                    this_temp = tempC * 1.8 + 32;
                    this_rh = humidity
                    self.uptime += 1
                else:
                    print "invalid local DHT read"
                    return

                if len(self.valid_temps) < self.history:
                    # we're still filling up the initial array
                    self.valid_temps.append(this_temp)
                    self.valid_rhs.append(this_rh)
                    self.all_temps.append(this_temp)
                    self.all_rhs.append(this_rh)
                    self.temp = this_temp
                    self.rh = this_rh
                    print "filling up array.  This temp: %.1f this rh: %.1f temps: %s" % (this_temp, this_rh, str(self.valid_temps) )
                else:
                    # the array is full enough
                    self.all_temps.append(this_temp)
                    self.all_rhs.append(this_temp)
                    self.all_temps = self.all_temps[1:]
                    self.all_rhs = self.all_rhs[1:]
                    tave = sum( self.valid_temps ) / len( self.valid_temps )
                    trh = sum( self.valid_rhs ) / len( self.valid_rhs )
                    tave_all = sum( self.all_temps ) / len( self.all_temps )
                    trh_all = sum( self.all_rhs ) / len( self.all_rhs )
                    if abs( tave - this_temp ) < self.tolerance: 
                        # the point is valid
                        self.valid_temps.append(this_temp)
                        self.valid_temps = self.valid_temps[1:]
                        self.lsp = 0
                        self.lsu = 0
                        self.temp = this_temp
                        self.rh = this_rh
                    elif abs( tave_all - this_temp ) < self.tolerance:
                        # if we're closer to the average of all the temps, then 
                        # we probably started with an incorrect value and should start over again
                        self.valid_temps = []
                        self.all_temps = []
                        self.valid_rhs = []
                        self.all_rhs = [] 
                    else: 
                        # the point is invalid
                        print "Invalid temp point! Temp: %.1f tave:%.1f prev:%s" % ( self.temp, tave, str(self.valid_temps))

                    if abs( trh - this_rh ) < self.tolerance:
                        self.valid_rhs = self.valid_rhs[1:]
                        self.valid_rhs.append(self.rh)
                        self.rh = this_rh
                    elif abs( trh_all - this_rh ) < self.tolerance:
                        # if we're closer to the average of all the temps, then 
                        # we probably started with an incorrect value and should start over again
                        self.valid_temps = []
                        self.all_temps = []
                        self.valid_rhs = []
                        self.all_rhs = [] 
                    else:
                        # the point is invalid
                        print "Invalid rh point! rh: %.1f  prev:%s" % ( self.rh, str(self.valid_rhs))
                    

                print "[%s] thermo_lr: %s " % (datetime.datetime.now(), str(self))

                self.uptime += 1
            #except KeyboardInterrupt:
            #    print "Keyboard interrupt"
            #    exit()
            #except:
            #    print "[%s] exception:  " % (datetime.datetime.now() ), sys.exc_info()[0]

############################################################################
############################################################################
class SensorRemoteDisp(Sensor):
############################################################################
############################################################################
#    A remote sensor with a thermostat display
    def __init__(self, name, domain="blank"):
        self.temp = INIT
        self.rh = INIT
        self.lastmotion = 0
        self.treq = 0
        self.treq_ack = 0
        Sensor.__init__(self, name, "remote_disp", domain, "remote_disp")

    ################################################################
    def get_dict(self):
    ################################################################
           return ( { 'temp' : self.temp, 'rh' : self.rh, 'lsu' : self.lsu, 'domain' : self.domain, 'uptime' : self.uptime, 'lsp' : self.lsp, 'lastmotion' : self.lastmotion} )

    ################################################################
    def __str__(self):
    ################################################################
           return ( "%s : { temp: %0.1f rh: %0.1f lsu: %d domain: %s uptime: %d lsp: %d sensor_type: %s hw_type: %s lastmotion: %d } " % (self.name, self.temp, self.rh, self.lsu, self.domain, self.uptime, self.lsp, self.sensor_type, self.hw_type, self.lastmotion) )

    ################################################################
    def update(self):
    ################################################################
        # update done in the sensor hub code
        self.lsu += 1
        
        
############################################################################
############################################################################type filter text
class SensorSpark(Sensor):
############################################################################
############################################################################
#    A sesnor built from the spark
    def __init__(self, name, domain="blank"):
        self.temp = INIT
        self.rh = INIT
        Sensor.__init__(self, name, "spark", domain, "temp")

    ################################################################
    def get_dict(self):
    ################################################################
           return ( { 'temp' : self.temp, 'rh' : self.rh, 'lsu' : self.lsu, 'domain' : self.domain, 'uptime' : self.uptime, 'lsp' : self.lsp } )

    ################################################################
    def getSparkVal(self,varname):
    ################################################################
        jsonurl = urllib2.urlopen("https://api.spark.io/v1/devices/normal_dentist/%s?access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6" % varname)
        text = json.loads(jsonurl.read())
        retval = text['result']
        return(retval)

    ################################################################
    def update(self):
    ################################################################
            try:
                #####################################################
                # read spark core
                #####################################################
                print "[%s] updating spark:  " % (datetime.datetime.now())
                self.temp = self.getSparkVal("temperature")
                self.rh = self.getSparkVal("humidity")
                self.uptime = self.getSparkVal("uptime")
                if self.uptime != self.prev_uptime:
                    self.prev_uptime = self.uptime
                    self.lsu = 0
                    
                self.lsp = self.getSparkVal("lsp")

                r = subprocess.call(["curl", "https://api.spark.io/v1/devices/normal_dentist/ping", "-d", "access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6", "-d", "args=1"], stdout=FNULL, stderr=subprocess.STDOUT)

                print "[%s] spark: %s " % (datetime.datetime.now(), str(self))
            except KeyboardInterrupt:
                print "Keyboard interrupt"
                exit()
            except:
                print "[%s] spark exception:  " % (datetime.datetime.now() ), sys.exc_info() 

############################################################################
############################################################################
class SensorSum(Sensor):
############################################################################
############################################################################
#   not actually a physical sensor, just a summary of other sensors
    def __init__(self, name, domain="blank"):
        self.temp = INIT
        self.rh = INIT
        Sensor.__init__(self, name, "sum", domain, "temp")
    ################################################################
    def get_dict(self):
    ################################################################
           return ( { 'temp' : self.temp, 'rh' : self.rh, 'lsu' : self.lsu, 'domain' : self.domain, 'uptime' : self.uptime, 'lsp' : self.lsp } )

    ################################################################
    def update(self):
    ################################################################
        pass
        

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
        self.sensorHub = SensorHub()
        
        # lsu = loops since update  (how long since we've received an update from this sensor)
        # lsp = loops since ping (how long this sensor thinks it's been since it heard from us)
        self.sensors = {}
        # self.sensors['spark'] = SensorSpark('spark', 'LR') 
        self.sensors['thermo_LR'] = SensorLocalDHT('thermo_lr', 'LR' )
        self.sensors['remote_MBR'] = SensorRemoteDisp('remote_MBR', 'LR')
        self.sensors['sum_LR'] = SensorSum('sum_LR', 'LR')
        self.domains = ['LR']
        
        self.sensorHub.sensor_list[1] = self.sensors['remote_MBR']
        print "Sensor hub sensor list: %s" % (self.sensorHub.sensor_list)

        for keys in self.sensors:
            print "[%s] initial: %s: %s " % (datetime.datetime.now(), keys, str(self.sensors[keys]))
    ################################################################
    def init_sums(self):
    ################################################################
        # initialize the average calc stats 
        for d in self.domains:
            self.sensors[ "sum_%s" % d ].N = 0
            self.sensors[ "sum_%s" % d ].total = 0

    ################################################################
    def calc_averages(self):
    ################################################################
            # update the averages
            for keys in self.sensors:
                d = self.sensors[keys].domain
                if keys.find("sum") == -1 and (self.sensors[keys].sensor_type == "temp" or self.sensors[keys].sensor_type == "remote_disp"):
                    if self.sensors[keys].lsu < 60:
                        self.sensors[ "sum_%s" % d ].N += 1
                        self.sensors[ "sum_%s" % d ].total += self.sensors[keys].temp
 
            # calculate the averages
            for d in self.domains:
                t = self.sensors[ "sum_%s" % d ].total 
                N = self.sensors[ "sum_%s" % d ].N
                if N > 0:
                    self.sensors[ "sum_%s" % d ].temp = t / N
                else:
                    self.sensors[ "sum_%s" % d ].temp = t
                self.sensors[ "sum_%s" % d ].lsu = 0
                self.sensors[ "sum_%s" % d ].uptime += 1
                
            # update the humidity averages
            for keys in self.sensors:
                d = self.sensors[keys].domain
                if keys.find("sum") == -1 and self.sensors[keys].sensor_type == "temp":
                    if self.sensors[keys].lsu < 60:
                        self.sensors[ "sum_%s" % d ].N += 1
                        self.sensors[ "sum_%s" % d ].total += self.sensors[keys].rh

            # calculate the averages
            for d in self.domains:
                t = self.sensors[ "sum_%s" % d ].total 
                N = self.sensors[ "sum_%s" % d ].N
                if N > 0:
                    self.sensors[ "sum_%s" % d ].rh = t / N
                else:
                    self.sensors[ "sum_%s" % d ].rh = t 
                print "[%s] rh sum: %s " % (datetime.datetime.now(), str(self.sensors['sum_LR']))

    
    ################################################################
    def read_sensors(self):
    ################################################################
            for keys in self.sensors:
                # update the sensors
                self.sensors[keys].lsu += 1
                self.sensors[keys].update()

    ################################################################
    def run(self):
    ################################################################
        self.last_update_serial_time = 0
        self.last_check_sensor_time = 0
        while 1:
            self.init_sums()
            if time.time() - self.last_update_serial_time > SERIAL_CHECK_PERIOD:
                #print "DEBUG: updating hub"
                self.sensorHub.update()
                self.last_update_serial_time = time.time()
            if time.time() - self.last_check_sensor_time > SENSOR_READ_PERIOD:
                #print "DEBUG: Reading sensors"
                self.read_sensors()
                self.calc_averages()
                self.last_check_sensor_time = time.time()

            #f = open('indoortemp','w')
            #f.write("%0.3f" % self.sensors['sum_LR'].temp)
            #f.close()

