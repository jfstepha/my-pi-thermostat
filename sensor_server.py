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

FNULL = open(os.devnull,'w')


class loopThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.loopcount=0
        self.msgcount = 0;
        # lsu = loops since update  (how long since we've received an update from this sensor)
        # lsp = loops since ping (how long this sensor thinks it's been since it heard from us)
        self.sensors = {
            'spark': { 'temp' : 0, 'rh' : 0, 'lsu':100000, 'domain':'LR', 'uptime':0, 'lsp':0  },
            'thermo_lr' : { 'temp' : 0, 'rh' : 0, 'lsu':100000, 'domain':'LR', 'uptime':0, 'lsp':0 },
            'sum_LR' : { 'temp' : 0, 'rh' : 0, 'lsu':100000, 'domain':'LR', 'uptime':0, 'lsp':0 },
        }
        self.domains = ['LR']

        print "[%s]sensor array: %s " % (datetime.datetime.now(), str(self.sensors))

    def getSparkVal(self,varname):
        jsonurl = urllib2.urlopen("https://api.spark.io/v1/devices/normal_dentist/%s?access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6" % varname)
        text = json.loads(jsonurl.read())
        retval = text['result']
        return(retval)

    def run(self):
        while 1:
            if 1:
                for s in self.sensors:
                    self.sensors[s]['lsu'] += 1
            try:
                #####################################################
                # read spark core
                #####################################################
                self.sensors['spark']['temp'] = self.getSparkVal("temperature")
                self.sensors['spark']['rh'] = self.getSparkVal("humidity")
                self.sensors['spark']['uptime'] = self.getSparkVal("uptime")
                self.sensors['spark']['lsp'] = self.getSparkVal("lsp")
                self.sensors['spark']['lsu'] = 0
                r = subprocess.call(["curl", "https://api.spark.io/v1/devices/normal_dentist/ping", "-d", "access_token=36026ae69dd3f99acdc53e8183087d4df8c48ab6", "-d", "args=1"], stdout=FNULL, stderr=subprocess.STDOUT)

                print "[%s] spark: %s " % (datetime.datetime.now(), str(self.sensors['spark']))
            except KeyboardInterrupt:
                print "Keyboard interrupt"
                exit()
            except:
                print "[%s] exception:  " % (datetime.datetime.now() ), sys.exc_info()[0]

            try:
                #########################################################
                # read local pi thermostat 
                #########################################################
                
                sensor = 22
                pin = 17
                rh, tempC = Adafruit_DHT.read_retry(sensor, pin)
                if rh is not None and tempC is not None:
                    temp = tempC * 1.8 + 32;
                    self.sensors['thermo_lr']['temp'] = temp
                    self.sensors['thermo_lr']['rh'] = rh
                    self.sensors['thermo_lr']['uptime'] = self.loopcount
                    self.sensors['thermo_lr']['lsp'] = 0
                    self.sensors['thermo_lr']['lsu'] = 0

                print "[%s] thermo_lr: %s " % (datetime.datetime.now(), str(self.sensors['thermo_lr']))

                self.loopcount += 1
            except KeyboardInterrupt:
                print "Keyboard interrupt"
                exit()
            except:
                print "[%s] exception:  " % (datetime.datetime.now() ), sys.exc_info()[0]

            if 1:
                #########################################################
                # calculate sum
                #########################################################
                t_sum = {}
                rh_sum = {}
                N = {}
                for d in self.domains:
                    t_sum[d] = 0
                    rh_sum[d] = 0
                    N[d] = 0
                for s in self.sensors:
                    #print " checking sensor %s (lsu=%d)" % (s, self.sensors[s]['lsu'] )
                    if self.sensors[s]['lsu'] < 120 and s.find("sum") == -1 :
                        # print " lsu is %d " % self.sensors[s]['lsu']
                        t_sum[ self.sensors[s]['domain'] ]  += self.sensors[s]['temp']
                        rh_sum[ self.sensors[s]['domain'] ]  += self.sensors[s]['rh']
                        N[ self.sensors[s]['domain'] ] += 1
                for d in self.domains:
                    if N[d] > 0:
                        sumname = "sum_%s" % d 
                        print " setting %s temp to %0.3f" % (sumname , t_sum[d] / N[d])
                        self.sensors[sumname]['temp'] = t_sum[ d ] / N [ d ]
                        self.sensors[sumname]['rh' ] = rh_sum[ d ] / N [ d ]
                        self.sensors[sumname]['uptime'] = self.loopcount
                        self.sensors[sumname]['lsu'] = 0

                f = open('indoortemp','w')
                f.write("%0.3f" % self.sensors['sum_LR']['temp'] )
                f.close()

            time.sleep(10)
                

################################################################################
class clientThread(threading.Thread):
################################################################################
    # created each time a client connects
    # destroyed on disconnect.
    def __init__(self, serv):
        threading.Thread.__init__(self)
        self.server = serv
        self.clientList = []
        self.running = True
        print("Client thread created. . .")
        
    def run(self):
        print("Beginning client thread loop. . .")
        while self.running:
            for client in self.clientList:
                client.loopThread = self.loopThread
                message = client.sock.recv(self.server.BUFFSIZE)
                if message != None and message != "":
                    client.update(message)

class clientObject(object):
    def __init__(self,clientInfo):
        self.sock = clientInfo[0]
        self.address = clientInfo[1]
    def update(self,message):
        # called for every message recieved from a client
        self.loopThread.msgcount += 1
        message = message.strip()
        try:
            if message == "dump_sensors":
                self.sock.send( str(self.loopThread.sensors).encode())
            elif message.find("liveVal") == 0 and message.count(".") == 2:
                x, sensor, param = message.split(".") 
                self.sock.send( str(self.loopThread.sensors[sensor][param]).encode() )
            else:
                self.sock.send("unrecognized command".encode())
        except:
            self.sock.send( str(sys.exc_info()[0]).encode() )


class Server(object):
    def __init__(self):
        self.HOST = 'localhost'
        self.PORT = 22085
        self.BUFFSIZE = 1024
        self.ADDRESS = (self.HOST,self.PORT)
        self.clientList = []
        self.running = True
        self.serverSock = socket.socket()
        self.serverSock.bind(self.ADDRESS)
        self.serverSock.listen(2)

        self.loopThread = loopThread(self)
        print "Starting loop thread..."
        self.loopThread.start()

        self.clientThread = clientThread(self)
        self.clientThread.loopThread = self.loopThread

        print("Starting client thread. . .")
        self.clientThread.start()
        print("Awaiting connections. . .")
        while self.running:
            clientInfo = self.serverSock.accept()
            print("Client connected from {}.".format(clientInfo[1]))
            self.clientThread.clientList.append(clientObject(clientInfo))

        self.serverSock.close()
        print("- end -")

#serv = Server()
