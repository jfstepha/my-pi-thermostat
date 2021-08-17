#!/usr/bin/python3
# adafruit librarys need to be installed from PIP now:
# pip3 install adafruit-circuitpython-dht
# sudo apt-get install libgpiod2

# and the mqtt library:
# sudo pip3 install paho-mqtt

# create the startup file
# /etc/systemd/system/temp_sensor_mqtt.service

# start with sudo systemctl start temp_sensor_mqtt

import sys
import argparse
import time
import board
import adafruit_dht

import paho.mqtt.publish as pub
from datetime import datetime

parser = argparse.ArgumentParser(description='Read the power values from the pzem power meter')
args = parser.parse_args()

result = None
retry = 0

# MQTT settings
MQTT_HOST="basement-pc"
MQTT_PORT=1883
MQTT_TOPIC="lexi-thermo/"
DEBUG=False
loop=0

# adafruit stuff 
dhtDevice = adafruit_dht.DHT22(board.D4)

def publish_value(reg_name, reg_val, loop_no):
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    topic = MQTT_TOPIC + reg_name
    if DEBUG or loop_no < 2:
        print("[" + dt_string + "] pzem: Publishing MQTT topic {} value {} on loop {}".format(topic, reg_val, loop_no ) )
        print("topic=" + topic)
    pub.single(topic , "{0:.1f}".format(reg_val), qos=2, hostname=MQTT_HOST, port=MQTT_PORT, client_id="sdm630_mqtt")

while 1:
  result = None
  loop += 1
  retry = 1

  while result == None and retry < 5:

    retry += 1
    try:
#    if True:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        print(
            "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                temperature_f, temperature_c, humidity
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
        time.sleep(30)
#    else:   
    except:
        print('Failed to get reading. Try again!')

        print("Unexpected error:", sys.exc_info()[0])
        print("*** Exception, trying again, try %d ****" % retry);
        time.sleep(1)

        pass



