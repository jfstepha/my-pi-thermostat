#!/usr/bin/python

# for the old pi-based thermostats, for some reason, i can't get the Adafruit libraries to install
# I can't get anything to install with PIP on python3
# so i have to stick with the old library.

# and the mqtt library:
# sudo pip install paho-mqtt

# create the startup file
# /etc/systemd/system/temp_sensor_mqtt_homie.service

# start with sudo systemctl start temp_sensor_mqtt

import sys
import time
import os
import ConfigParser

import paho.mqtt.publish as pub
from datetime import datetime

result = None
retry = 0

config = ConfigParser.ConfigParser()
config.read("config.txt")
did = config.get('homie','did')

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


degree_sign = u'\N{DEGREE SIGN}'.encode('utf-8')

will={'topic':"homie/"+did+"/$state", 'payload':'lost', 'qos':2,'retain':True}
publish_raw("$homie","3.0.1", True);
publish_raw("$name", did, True);
#publish_raw("$localip", "192.168.1.105", True);
#publish_raw("$mac", "00:13:ef:c0:17:4f", True);
publish_raw("$fw-name", "temp_sensor_mqtt_homie.py", True);
publish_raw("$fw-version", "0.0.0", True);
publish_raw("$nodes", "thermostat", True);
publish_raw("thermostat/$name", "thermostat", True);
publish_raw("thermostat/$type", "PiB", True);
publish_raw("thermostat/$properties", "temperature,humidity", True);
publish_raw("thermostat/temperature/$name", "temperature", True);
publish_raw("thermostat/temperature/$datatype", "float", True);
publish_raw("thermostat/temperature/$format", "-30:130", True);
publish_raw("thermostat/temperature/$unit", degree_sign+"F", True);
publish_raw("thermostat/temperature/$settable", "false", True);
publish_raw("thermostat/temperature/$retained", "true", True);
publish_raw("thermostat/humidity/$name", "humidity", True);
publish_raw("thermostat/humidity/$unit", "%", True);
publish_raw("thermostat/humidity/$datatype", "float", True);
publish_raw("thermostat/humidity/$format", "-30:130", True);
publish_raw("thermostat/humidity/$settable", "false", True);
publish_raw("thermostat/humidity/$retained", "true", True);

publish_raw("$state","init",True,will);
publish_raw("$stats","lastupdate,loop",True,will);

#time.sleep(10)
        
while 1:
  result = None
  loop += 1
  retry = 1

  while result == None and retry < 5:

    retry += 1
#    try:
    if True:
        stream = os.popen('./read_dht22.py')
        dht_str = stream.read()
        #print("Got DHT string: " + dht_str);
        # string should be "temp:74.120,rh:41.500"
        if dht_str.find("temp:") == 0:
            if loop < 2:
                printit = True
            else:
                printit = False
            #print("Found temp");
            ary = dht_str.split(",");
            temp_part = ary[0]
            rh_part = ary[1]
            ary = temp_part.split(":");
            temperature_f = float( ary[1] );
            ary = rh_part.split(":");
            humidity = float( ary[1] );
            #print("Temperature=%0.3f, RH=%0.3f" % (temperature_f, humidity) )
            #print(
            #    "Temp: {:.1f} F /     Humidity: {}% ".format(
            #        temperature_f, humidity
            #    )
            #)
            now=datetime.today()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            print("[" + dt_string + "] thermo: got temp=%0.1f humidity=%0.1f" % (temperature_f, humidity) );
            now=datetime.today()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            print("[" + dt_string + "] thermo: publishing topics loop # " + str(loop) );
            publish_raw("thermostat/humidity", "{0:.1f}".format(humidity), printit);
            publish_raw("thermostat/temperature", "{0:.1f}".format(temperature_f), printit);
            publish_raw("$stats/lastupdate", dt_string, printit)
            publish_raw("$stats/loop", str(loop), printit)
            publish_raw("$state","ready",True,will);

            result = 1
            time.sleep(10)
        else:
            print("failed to get reading, trying again");
    else:   
#    except:
        print('Failed to get reading. Try again!')

        print("Unexpected error:", sys.exc_info()[0])
        print("*** Exception, trying again, try %d ****" % retry);
        time.sleep(1)

        pass



