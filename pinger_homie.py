#!/usr/bin/python3

# and the mqtt library:
# sudo pip install paho-mqtt

# create the startup file
# /etc/systemd/system/pinger_homie.service

# start with sudo systemctl start pinger_homie

import sys
import time
import os
import configparser
from statistics import mean

import paho.mqtt.publish as pub
import paho.mqtt.client as mqtt
from datetime import datetime

# /homie/basement-pc-pinger/kitchenthermo/ping : basment-pc ping time to kitchen-thermo
# /homie/basement-pc-pinger/recping : keep alive ping from master
# /homie/basement-pc-pinger/lsp : return back from client to master.

# /homie/kitchen-thermo-pinger/google/ping : kitchen-thermo ping time to google
# /homie/kitchen-thermo-pinger/recping : kitchen-thermo keep alive ping from master
# /homie/kitchen-thermo-pinger/lsp : return back from client to master

# master has to publish all the recpings, but the LSPs just go to openhab
# client has to sub to it's own recping and publish 

config = configparser.ConfigParser()
config.read("config.txt")
iplist_str = config.get('pinger','iplist')
namelist_str = config.get('pinger','namelist')
did = config.get('pinger','did')
pinglist_str = config.get('pinger','pinglist',fallback="None")

rec_ping = True
if pinglist_str == "None":
    rec_ping = False


print("got config did=%s" % did)
print("got config uplist " + iplist_str)
print("got config namelist " + namelist_str)

iplist = iplist_str.split(',')
namelist = namelist_str.split(',')
pinglist = pinglist_str.split(',')

print(" iplist: %s" % str(iplist) )
print(" namelist: %s" % str(namelist) )
print(" pinglist: %s" % str(pinglist) )


result = None
retry = 0
N = 10

# MQTT settings
MQTT_HOST="basement-pc"
MQTT_PORT=1883
DEBUG=False
loop=0
lsp = 0

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    print( "subscribing to homie/"+did+"/recping")  
    client.subscribe("homie/"+did+"/recping")  

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    print("[" + dt_string + "] Message received-> " + msg.topic + " " + str(msg.payload) + " resetting lsp")  # Print a received msg
    global lsp
    lsp = 0

def publish_raw(topic_sub, msg, printit, will=None):
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    topic = "homie/"+did+"/"+topic_sub
    if printit:
        print("[" + dt_string + "] temp_sensor_homie: Publishing MQTT topic {} value {} ".format(topic, msg ) )
    pub.single(topic , msg, qos=2, hostname=MQTT_HOST, port=MQTT_PORT, retain=True, will=will)

def publish_recping(topic_sub, msg, printit, will=None):
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    topic = "homie/"+topic_sub
    if printit:
        print("[" + dt_string + "] temp_sensor_homie: Reciping publishing MQTT topic {} value {} ".format(topic, msg ) )
    pub.single(topic , msg, qos=2, hostname=MQTT_HOST, port=MQTT_PORT, retain=True, will=will)

client = mqtt.Client(did) # Create instance of client with client ID did
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect(MQTT_HOST,MQTT_PORT)

will={'topic':"homie/"+did+"/$state", 'payload':'lost', 'qos':2,'retain':True}

publish_raw("$homie","3.0.1", True);
publish_raw("$name", did, True);
#publish_raw("$localip", "192.168.1.105", True);
#publish_raw("$mac", "00:13:ef:c0:17:4f", True);
publish_raw("$fw-name", "pinger_homie.py", True);
publish_raw("$fw-version", "0.0.0", True);
publish_raw("$nodes", (','.join( namelist )) + ",lsp", True);

ping_history = []
ping_history_long = []

publish_raw( "lsp/$name", "lsp", True);
publish_raw( "lsp/$type", "pinger", True);
publish_raw( "lsp/$properties", "lsp,lsp10,lsp100", True);

publish_raw( "lsp/lsp/$datatype", "integer", True);
publish_raw( "lsp/lsp/$format", "0:1000", True);
publish_raw( "lsp/lsp/$unit", "loops", True);
publish_raw( "lsp/lsp/$settable", "false", True);
publish_raw( "lsp/lsp/$retained", "true", True);

publish_raw( "lsp/lsp10/$datatype", "integer", True);
publish_raw( "lsp/lsp10/$format", "0:1000", True);
publish_raw( "lsp/lsp10/$unit", "loops", True);
publish_raw( "lsp/lsp10/$settable", "false", True);
publish_raw( "lsp/lsp10/$retained", "true", True);

publish_raw( "lsp/lsp100/$datatype", "integer", True);
publish_raw( "lsp/lsp100/$format", "0:1000", True);
publish_raw( "lsp/lsp100/$unit", "loops", True);
publish_raw( "lsp/lsp100/$settable", "false", True);
publish_raw( "lsp/lsp100/$retained", "true", True);

for i in range( 0, len( iplist ) ):
    ip = iplist[ i ]
    name = namelist[ i ]

    publish_raw( name+"/$name", name, True);
    publish_raw( name+"/$type", "pinger", True);
    publish_raw( name+"/$properties", "ping,avg,max10,max100", True);
    publish_raw( name+"/$name", "ping", True);

    publish_raw( name+"/ping/$datatype", "float", True);
    publish_raw( name+"/ping/$format", "0:200", True);
    publish_raw( name+"/ping/$unit", "ms", True);
    publish_raw( name+"/ping/$settable", "false", True);
    publish_raw( name+"/ping/$retained", "true", True);
    
    publish_raw( name+"/avg/$datatype", "float", True);
    publish_raw( name+"/avg/$format", "-2:1000", True);
    publish_raw( name+"/avg/$unit", "ms", True);
    publish_raw( name+"/avg/$settable", "false", True);
    publish_raw( name+"/avg/$retained", "true", True);

    publish_raw( name+"/max10/$datatype", "float", True);
    publish_raw( name+"/max10/$format", "-2:1000", True);
    publish_raw( name+"/max10/$unit", "ms", True);
    publish_raw( name+"/max10/$settable", "false", True);
    publish_raw( name+"/max10/$retained", "true", True);

    publish_raw( name+"/max100/$datatype", "float", True);
    publish_raw( name+"/max100/$format", "-2:1000", True);
    publish_raw( name+"/max100/$unit", "ms", True);
    publish_raw( name+"/max100/$settable", "false", True);
    publish_raw( name+"/max100/$retained", "true", True);


    this_history = [];
    ping_history.append( this_history );
    ping_history_long.append( this_history );

publish_raw("$state","init",True,will);
publish_raw("$stats","lastupdate,loop",True,will);

#time.sleep(10)

lsp_history = []
lsp_history_long = []
        
while 1:
  result = None
  loop += 1
  lsp += 1
  if loop < 2:
        printit = True
  else:
        #printit = False
        printit = True

  lsp_history.append( lsp )
  lsp_history_long.append( lsp )
  if len( lsp_history ) > 10:
    lsp_history = lsp_history[1:11]
  if len( lsp_history_long ) > 100:
    lsp_history_long = lsp_history_long[1:101]
  lsp10 = max( lsp_history )
  lsp100 = max( lsp_history_long )
  if loop % N == 0:
      publish_raw( "lsp/lsp", "{0:d}".format(lsp), printit);
      publish_raw( "lsp/lsp10", "{0:d}".format(lsp10), printit);
      publish_raw( "lsp/lsp100", "{0:d}".format(lsp100), printit);

  for i in range( 0, len( iplist ) ):
    ip = iplist[ i ]
    name = namelist[ i ]

#    try:
    if True:
        stream = os.popen("./pingit2.sh " + ip)
        retval= stream.read() 
        #print("Got ping %s" % (retval) )
        ping = float( retval ) 
        #print("Got ping %0.3f on %s" % (ping, ip) )
        now=datetime.today()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        #print("[" + dt_string + "] pinger: got ping %0.1f on ip %s" % (ping, ip) );

        result = 1

        ping_history[ i ].append( ping )
        ping_history_long[ i ].append( ping )

        if len( ping_history[ i ] ) > 10:
             ping_history[ i ] =  ping_history[ i ][1:11]
        if len( ping_history_long[ i ] ) > 100:
             ping_history[ i ] =  ping_history[ i ][1:101]


        avg = mean( ping_history[ i ] )
        max10 = max( ping_history[ i ] )
        max100 = max( ping_history_long[ i ] )
        # print ("ping_history: %s len %d mean %f" % (str(ping_history), len( ping_history[ ip_no ] ), avg ) )
        if loop % N == 0:
            print("[" + dt_string + "] pinger: publishing topics loop # " + str(loop) );
            publish_raw( name+"/ping", "{0:.1f}".format(ping), printit);
            publish_raw("$stats/lastupdate", dt_string, printit)
            publish_raw("$stats/loop", str(loop), printit)
            publish_raw("$state","ready",True,will);
            publish_raw( name+"/avg", "{0:.1f}".format(avg), printit);
            publish_raw( name+"/max10", "{0:.1f}".format(max10), printit);
            publish_raw( name+"/max100", "{0:.1f}".format(max100), printit);
    else:   
#    except:
        print('Failed to get reading. Try again!')

        print("Unexpected error:", sys.exc_info()[0])
        print("*** Exception, trying again, try %d ****" % retry);
        time.sleep(1)

        pass
  if rec_ping:
      for i in range( 0, len( pinglist ) ):
          publish_recping( pinglist[i]+"-pinger/recping",loop,printit)
  client.loop_start()
  time.sleep(10)
  client.loop_stop()



