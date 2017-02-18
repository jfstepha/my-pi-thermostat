#!/usr/bin/python

import socket
import threading
import struct
import string
import time
import urllib2
import time
import datetime
import sys
import subprocess
import os
import datetime
import ConfigParser
import urllib2
import requests
import Queue
import datetime
import fcntl


FNULL = open(os.devnull,'w')
INIT = 70

SLEEP_PERIOD = 0.1
UPDATE_STATE_PERIOD = 5
OVERRIDE_INCREMENT = 60
MAX_OVERRIDE = 480
HOUR_DAY_START = 5
HOUR_NIGHT_START = 23

config = ConfigParser.ConfigParser()
config.read("config.txt")
servername = config.get('sensorhub','name')
serverdomain = config.get('sensorhub','domain')
hasmotion = config.get('motion', 'hasmotion')
motion_url = config.get('motion','url')
idle_threshold = int(config.get('motion','idle_threshold'))
url = "http://localhost:80"


############################################################################
############################################################################
class smartLoopThread(threading.Thread):
############################################################################
############################################################################
    STATE_NO_SENSOR =    [0,"No sensor"]
    STATE_DAY_IDLE =     [1,"Day idle"]
    STATE_DAY_MOTION =   [2, "Day motion"]
    STATE_DAY_AWAY =     [3, "Day away"]
    STATE_DAY_ACTIVE =   [4, "Day active"]
    STATE_NIGHT_IDLE =   [5, "Night idle"]
    STATE_NIGHT_MOTION = [6, "Night motion"]
    STATE_NIGHT_AWAY =   [7, "Night away"]
    STATE_NIGHT_ACTIVE = [8, "Night active"]
    loops_since_motion = 0

    ################################################################
    def __init__(self, pending_state):
    ################################################################
        print("SMART_THERMO: __init__")
        threading.Thread.__init__(self)
        self.smart_state = self.STATE_NO_SENSOR
        self.override_remaining = 0 # in minutes
        self.override_end = time.time()
        self.pending_state = pending_state
        self.open_debug_file()
        self.idle_threshold = idle_threshold
        self.printdebug("idle threshold: %d" %self.idle_threshold)

        if hasmotion.lower()[0] == "t" :
            self.printdebug("Initializing motion")
            self.getSetpoints()
            self.hasmotion = True
            self.smart_state = self.STATE_DAY_IDLE
            self.update_state()
        else:
            self.hasmotion = False
            
        self.printdebug("__init__ complete")

    ################################################################
    def open_debug_file(self):
    ################################################################
       now = datetime.datetime.now()
       fn = "logs/smart%02d-%02d-%02d-%02d%02d%02d.log" % (now.year, now.month, now.day, now.hour, now.minute,now.second)
       self.debugfile = open( fn, "a", 0)
        

    ################################################################
    def printdebug(self, str):
    ################################################################
        now = datetime.datetime.now()
        logstr = "[%02d:%02d:%02d] SMART_THERMO: %s" % (now.hour, now.minute,now.second, str)
        self.debugfile.write( logstr+"\n" )
        print(logstr)

    ################################################################
    def update_state(self):
    ################################################################
        self.printdebug("update_state current state: %s " % str( self.smart_state ) )
        if self.hasmotion != True or self.smart_state == self.STATE_NO_SENSOR:
            self.printdebug("no motion sensor")
            return
        
        self.writeSetpoints()
        now = datetime.datetime.now()
        if (now.hour >= HOUR_NIGHT_START or now.hour < HOUR_DAY_START) and self.smart_state[0] <= 4:
            if self.smart_state == self.STATE_DAY_ACTIVE:
                self.smart_state = self.STATE_NIGHT_ACTIVE
            if self.smart_state == self.STATE_DAY_AWAY:
                self.smart_state = self.STATE_NIGHT_AWAY
            if self.smart_state == self.STATE_DAY_IDLE:
                self.smart_state = self.STATE_NIGHT_IDLE
            if self.smart_state == self.STATE_DAY_MOTION:
                self.smart_state = self.STATE_NIGHT_MOTION
        elif now.hour >= HOUR_DAY_START and self.smart_state[0] > 4:
            if self.smart_state == self.STATE_NIGHT_ACTIVE:
                self.smart_state = self.STATE_DAY_ACTIVE
            if self.smart_state == self.STATE_NIGHT_AWAY:
                self.smart_state = self.STATE_DAY_AWAY
            if self.smart_state == self.STATE_NIGHT_IDLE:
                self.smart_state = self.STATE_DAY_IDLE
            if self.smart_state == self.STATE_DAY_MOTION:
                self.smart_state = self.STATE_NIGHT_MOTION
        self.printdebug("checking overrides") 
        # check to see if overrides are on and need to be turned off:
        if self.smart_state == self.STATE_NIGHT_ACTIVE or self.smart_state == self.STATE_DAY_ACTIVE or self.smart_state == self.STATE_NIGHT_AWAY  or self.smart_state == self.STATE_DAY_AWAY:
            self.printdebug("overrides on")
            self.override_remaining = (self.override_end - time.time()) / 60
            if self.override_remaining <= 0:
                self.remove_override()
            self.setTemperatureFromState()
            return

        # we should only get here if we're not overriding  

        self.printdebug("getting motion") 
        self.getMotion()        

        self.printdebug("checking to see if its idle") 
        # check to see if we need to change state based on motion
        if self.loops_since_motion > self.idle_threshold:
            if self.smart_state == self.STATE_DAY_MOTION:
                self.smart_state = self.STATE_DAY_IDLE
                self.setTemperatureFromState()
                self.printdebug("update_state new state: %s " % str( self.smart_state ) )
            if self.smart_state == self.STATE_NIGHT_MOTION:
                self.smart_state = self.STATE_NIGHT_IDLE
                self.setTemperatureFromState()
                self.printdebug("update_state new state: %s " % str( self.smart_state ) )
        else:
            if self.smart_state == self.STATE_DAY_IDLE:
                self.smart_state = self.STATE_DAY_MOTION
                self.setTemperatureFromState()
                self.printdebug("update_state new state: %s " % str( self.smart_state ) )
            if self.smart_state == self.STATE_NIGHT_IDLE:
                self.smart_state = self.STATE_NIGHT_MOTION
                self.setTemperatureFromState()
                self.printdebug("update_state new state: %s " % str( self.smart_state ) )
        self.printdebug("update_state done.  State:%s" % str(self.smart_state))
                
    ################################################################
    def setTemperatureFromState(self):
    ################################################################
        # if overrides are on, set the temperature
        if self.smart_state == self.STATE_NIGHT_ACTIVE:
            self.setTemperature( self.set_night_active )
            
        if self.smart_state == self.STATE_DAY_ACTIVE:
            self.setTemperature( self.set_day_active )
            
        if self.smart_state == self.STATE_NIGHT_AWAY:
            self.setTemperature( self.set_night_idle )

        if self.smart_state == self.STATE_DAY_AWAY:
            self.setTemperature( self.set_day_idle )

        if self.smart_state == self.STATE_NIGHT_MOTION:
            self.setTemperature( self.set_night_idle)

        if self.smart_state == self.STATE_DAY_MOTION:
            self.setTemperature( self.set_day_active )
            
        if self.smart_state == self.STATE_DAY_IDLE:
            self.setTemperature( self.set_day_idle)
        
        if self.smart_state == self.STATE_NIGHT_IDLE:
            self.setTemperature( self.set_night_idle )
                
            
    ################################################################
    def setTemperature(self, temp):
    ################################################################
        self.printdebug("Setting temperature to %0.1f" % temp)
        try:
            r = requests.get(url + "/_setTarget/%0.1f" % float(temp))
        except KeyboardInterrupt:
            self.printdebug("Keyboard interrupt")
            exit()
        except:
            self.printdebug("submit temp failed")
            return -1

        return (r)
                
    ################################################################
    def getMotion(self):
    ################################################################
        print("SMART_THERMO: getting motion")
        self.printdebug("in getMotion")
        try:
            f = open("/dev/shm/motion", "r")
            # make it a non-blocking read:
            fd = f.fileno()
            flag = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
            self.printdebug("file opened")
            motion = f.readline()
            self.printdebug("read file motion = %s" % str(motion))
            f.close()
            if motion != None:
                self.loops_since_motion = int( motion )
                self.printdebug("loops since motion: %d" % self.loops_since_motion)
            else:
                self.printdebug("motion was none.  leaving lsm alone")
        except IOError:
            self.printdebug("ERROR: error reading motion state (leaving lsm unchanged)")
        except:
            self.printdebug("ERROR: Unexpected error: (leaving lsm unchanged) %s " % sys.exc_info()[0])

    ################################################################
    def getSetpoints(self):
    ################################################################
        self.printdebug("getting setpoints")
        try:
            file = open("smart_setpoints", "r")
            line = file.readline()
            file.close()
            vals = line.split(',')
            self.set_day_active = float( vals[0] )
            self.set_day_idle = float( vals[1] )
            self.set_night_active = float( vals[2] )
            self.set_night_idle = float( vals[3] )
            self.smart_state = self.smartStateFromInt( int( vals[4] ) )
            self.printdebug("read setpoints %0.1f,%0.1f,%0.1f,%0.1f,%s" % (self.set_day_active, self.set_day_idle, 
                                                      self.set_night_active, self.set_night_idle, str(self.smart_state)))


        except IOError:
            self.set_day_active = 70
            self.set_day_idle = 70
            self.set_night_active = 70
            self.set_night_idle = 70
            self.smart_state = self.STATE_DAY_ACTIVE
            self.printdebug("error reading smart setpoints")
            
    ################################################################
    def smartStateFromInt(self, i):
    ################################################################
        if i == self.STATE_DAY_ACTIVE[0]:
            return self.STATE_DAY_ACTIVE
        if i == self.STATE_DAY_IDLE[0]:
            return self.STATE_DAY_IDLE
        if i == self.STATE_DAY_AWAY[0]:
            return self.STATE_DAY_AWAY
        if i == self.STATE_DAY_MOTION[0]:
            return self.STATE_DAY_MOTION

        if i == self.STATE_NIGHT_ACTIVE[0]:
            return self.STATE_NIGHT_ACTIVE
        if i == self.STATE_NIGHT_IDLE[0]:
            return self.STATE_NIGHT_IDLE
        if i == self.STATE_NIGHT_AWAY[0]:
            return self.STATE_NIGHT_AWAY
        if i == self.STATE_NIGHT_MOTION[0]:
            return self.STATE_NIGHT_MOTION

    ################################################################
    def smartStateInt(self):
    ################################################################
        return self.smart_state[0]

    ################################################################
    def smartStateStr(self):
    ################################################################
        return self.smart_state[1]

    ################################################################
    def setSmartState(self, mode):
    ################################################################
        self.printdebug("setting state to %d" % mode)
        if mode == self.STATE_DAY_ACTIVE[0]:
            if self.smart_state == self.STATE_DAY_ACTIVE:
                self.increaseOverrideTime()
            else:
                self.initialOverrideTime()
            self.smart_state = self.STATE_DAY_ACTIVE

        if mode == self.STATE_DAY_AWAY[0]:
            if self.smart_state == self.STATE_DAY_AWAY:
                self.increaseOverrideTime()
            else:
                self.initialOverrideTime()
            self.smart_state = self.STATE_DAY_AWAY

        if mode == self.STATE_NIGHT_ACTIVE[0]:
            if self.smart_state == self.STATE_NIGHT_ACTIVE:
                self.increaseOverrideTime()
            else:
                self.initialOverrideTime()
            self.increaseOverrideTime()

        if mode == self.STATE_NIGHT_AWAY[0]:
            if self.smart_state == self.STATE_NIGHT_AWAY:
                self.increaseOverrideTime()
            else:
                self.initialOverrideTime()
            self.smart_state = self.STATE_NIGHT_AWAY
        
        if mode == self.STATE_DAY_IDLE[0]:
            self.smart_state = self.STATE_DAY_IDLE
            self.clearOverrideTime()

        if mode == self.STATE_DAY_MOTION[0]:
            self.smart_state = self.STATE_DAY_MOTION
            self.clearOverrideTime()

        if mode == self.STATE_NIGHT_IDLE[0]:
            self.smart_state = self.STATE_NIGHT_IDLE
            self.clearOverrideTime()

        if mode == self.STATE_NIGHT_MOTION[0]:
            self.smart_state = self.STATE_NIGHT_MOTION
            self.clearOverrideTime()
            
        self.printdebug("done, set state to %s" % str( self.smart_state ))
            
            
    ################################################################
    def clearOverrideTime(self):
    ################################################################
        self.override_remaining = 0
        self.override_end = time.time() 

    ################################################################
    def initialOverrideTime(self):
    ################################################################
        self.override_remaining = OVERRIDE_INCREMENT
        self.override_end = time.time() + OVERRIDE_INCREMENT * 60

    ################################################################
    def increaseOverrideTime(self):
    ################################################################
        if self.override_remaining <= 0:
            self.override_remaining = OVERRIDE_INCREMENT
            self.override_end = time.time() + OVERRIDE_INCREMENT * 60
        if self.override_remaining + OVERRIDE_INCREMENT > MAX_OVERRIDE:
            self.override_remaining = MAX_OVERRIDE 
            self.override_end = time.time() + MAX_OVERRIDE * 60
        else:
            self.override_end += OVERRIDE_INCREMENT * 60
            self.override_remaining = (self.override_end - time.time()) / 60
            
        
    ################################################################
    def writeSetpoints(self):
    ################################################################
        try:
            self.printdebug("writing setpoints")
            file = open("smart_setpoints", "w")
            file.write("%0.1f,%0.1f,%0.1f,%0.1f,%d" % (self.set_day_active, self.set_day_idle, 
                                                      self.set_night_active, self.set_night_idle, self.smart_state[0]))
            file.close()

            self.printdebug("writing setpoints done")
        except IOError:
            self.printdebug("error writing smart setpoints")
    
    ################################################################
    def remove_override(self):
    ################################################################
        self.printdebug("removing overrides")
        if self.smart_state == self.STATE_DAY_ACTIVE:
            self.smart_state = self.STATE_DAY_MOTION
        else:
            self.smart_state = self.STATE_NIGHT_MOTION
        
        self.override_remaining = 0
        self.writeSetpoints()

    ################################################################
    def run(self):
    ################################################################
        self.last_update_state_time = 0
        self.printdebug( "in run")
        while 1:
            #print("SMART_THERMO: checking pending states")
            try:
                new_state = self.pending_state.get_nowait()
                self.printdebug("got new state %d" % new_state)
                self.setSmartState( new_state )
            except Queue.Empty:
                #Eprint("SMART_THERMO: no pending state")
                pass

            if time.time() - self.last_update_state_time > UPDATE_STATE_PERIOD:
                self.update_state()
                self.last_update_state_time = time.time()
            time.sleep(SLEEP_PERIOD)


