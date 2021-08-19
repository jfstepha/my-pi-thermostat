#!/usr/bin/python

# for the old pi-based thermostats, for some reason, i can't get the Adafruit libraries to install
# I can't get anything to install with PIP on python3
# so i have to stick with the old library.

# and the mqtt library:
# sudo pip install paho-mqtt

# create the startup file
# /etc/systemd/system/temp_sensor_mqtt.service

# start with sudo systemctl start temp_sensor_mqtt

import sys
import time
import os

import paho.mqtt.publish as pub
from datetime import datetime

result = None
retry = 0

# MQTT settings
MQTT_HOST="basement-pc"
MQTT_PORT=1883
MQTT_TOPIC="tate-thermo/"
DEBUG=False
loop=0

# adafruit stuff 
#dhtDevice = adafruit_dht.DHT22(board.D4)

def publish_value(reg_name, reg_val, loop_no):
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    topic = MQTT_TOPIC + reg_name
    if DEBUG or loop_no < 2:
        print("[" + dt_string + "] temp_sensor_mqtt: Publishing MQTT topic {} value {} on loop {}".format(topic, reg_val, loop_no ) )
        print("topic=" + topic)
    pub.single(topic , "{0:.1f}".format(reg_val), qos=2, hostname=MQTT_HOST, port=MQTT_PORT, client_id="sdm630_mqtt")

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
        print("Got DHT string: " + dht_str);
        # string should be "temp:74.120,rh:41.500"
        if dht_str.find("temp:") == 0:
            print("Found temp");
            ary = dht_str.split(",");
            temp_part = ary[0]
            rh_part = ary[1]
            ary = temp_part.split(":");
            temperature_f = float( ary[1] );
            art = temp_part.split(":");
            humidity = float( ary[1] );
            print("Temperature=%0.3f, RH=%0.3f" % (temperature_f, humidity) )
            print(
                "Temp: {:.1f} F /     Humidity: {}% ".format(
                    temperature_f, humidity
                )
            )
            now=datetime.today()
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
            print("[" + dt_string + "] thermo: publishing topics loop # " + str(loop) );
            if DEBUG or loop < 2:
                print("[" + dt_string + "] thermo: publishing topic " + MQTT_TOPIC + "lastdatasent " + dt_string)
            pub.single(MQTT_TOPIC + "lastdatasent" , dt_string, qos=2, hostname=MQTT_HOST, port=MQTT_PORT, client_id="sdm630_mqtt")

            publish_value("humidity", humidity, loop);
            publish_value("temperature", temperature_f, loop);

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



