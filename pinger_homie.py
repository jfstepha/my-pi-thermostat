#!/usr/bin/python3

# and the mqtt library:
# sudo pip install paho-mqtt

# create the startup file
# /etc/systemd/system/pinger_homie.service

# start with sudo systemctl start pinger_homie

import sys
import time
import os
from statistics import mean

import paho.mqtt.publish as pub
from datetime import datetime

ip_list=[ '192.168.1.1' , '8.8.8.8', 'kitchen-thermo', 'sf-thermo', 'as-thermo', 'mbr-thermo' ]
name_list=[ 'router', 'google' ]
did='basement-pc-pinger'


result = None
retry = 0
N = 10

# MQTT settings
MQTT_HOST="basement-pc"
MQTT_PORT=1883
DEBUG=False
loop=0

def publish_raw(topic_sub, msg, printit, will=None):
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    topic = "homie/"+did+"/"+topic_sub
    if printit:
        print("[" + dt_string + "] temp_sensor_homie: Publishing MQTT topic {} value {} ".format(topic, msg ) )
    pub.single(topic , msg, qos=2, hostname=MQTT_HOST, port=MQTT_PORT, retain=True, will=will)


will={'topic':"homie/"+did+"/$state", 'payload':'lost', 'qos':2,'retain':True}

publish_raw("$homie","3.0.1", True);
publish_raw("$name", did, True);
#publish_raw("$localip", "192.168.1.105", True);
#publish_raw("$mac", "00:13:ef:c0:17:4f", True);
publish_raw("$fw-name", "pinger_homie.py", True);
publish_raw("$fw-version", "0.0.0", True);
publish_raw("$nodes", ','.join( ip_list ), True);

ping_history = []

for ip in ip_list:
    publish_raw( ip+"/$name", "thermostat", True);
    publish_raw( ip+"/$type", "pinger", True);
    publish_raw( ip+"/$properties", "ping,avg", True);
    publish_raw( ip+"/$name", "ping", True);
    publish_raw( ip+"/ping/$datatype", "float", True);
    publish_raw( ip+"/ping/$format", "0:200", True);
    publish_raw( ip+"/ping/$unit", "ms", True);
    publish_raw( ip+"/ping/$settable", "false", True);
    publish_raw( ip+"/ping/$retained", "true", True);
    publish_raw( ip+"/avg/$datatype", "float", True);
    publish_raw( ip+"/avg/$format", "-2:1000", True);
    publish_raw( ip+"/avg/$unit", "ms", True);
    publish_raw( ip+"/avg/$settable", "false", True);
    publish_raw( ip+"/avg/$retained", "true", True);
    this_history = [];
    ping_history.append( this_history );

publish_raw("$state","init",True,will);
publish_raw("$stats","lastupdate,loop",True,will);

#time.sleep(10)
        
while 1:
  result = None
  loop += 1
  ip_no=0
  for ip in ip_list:

#    try:
    if True:
        stream = os.popen("./pingit2.sh " + ip)
        retval= stream.read() 
        #print("Got ping %s" % (retval) )
        ping = float( retval ) 
        #print("Got ping %0.3f on %s" % (ping, ip) )
        if loop < 2:
            printit = True
        else:
            printit = False
            #printit = True
        now=datetime.today()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        #print("[" + dt_string + "] pinger: got ping %0.1f on ip %s" % (ping, ip) );

        result = 1

        ping_history[ ip_no ].append( ping )
        if len( ping_history[ ip_no ] ) > 10:
             ping_history[ ip_no ] =  ping_history[ ip_no ][1:11]
        avg = mean( ping_history[ ip_no ] )
        # print ("ping_history: %s len %d mean %f" % (str(ping_history), len( ping_history[ ip_no ] ), avg ) )
        ip_no += 1
        if loop % N == 0:
            print("[" + dt_string + "] pinger: publishing topics loop # " + str(loop) );
            publish_raw( ip+"/ping", "{0:.1f}".format(ping), printit);
            publish_raw("$stats/lastupdate", dt_string, printit)
            publish_raw("$stats/loop", str(loop), printit)
            publish_raw("$state","ready",True,will);
            publish_raw( ip+"/avg", "{0:.1f}".format(avg), printit);
    else:   
#    except:
        print('Failed to get reading. Try again!')

        print("Unexpected error:", sys.exc_info()[0])
        print("*** Exception, trying again, try %d ****" % retry);
        time.sleep(1)

        pass
  time.sleep(10)



