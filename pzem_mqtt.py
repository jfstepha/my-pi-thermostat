#!/usr/bin/python3

import minimalmodbus
import sys
import argparse
import time

import paho.mqtt.publish as pub
from datetime import datetime

parser = argparse.ArgumentParser(description='Read the power values from the pzem power meter')
args = parser.parse_args()

result = None
retry = 0

# MQTT settings
MQTT_HOST="localhost"
MQTT_PORT=1883
MQTT_TOPIC="pzem/"
DEBUG=False
loop=0


def publish_value(slave, reg_name, reg_val, loop_no):
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    topic = MQTT_TOPIC + slave + "/" + reg_name
    if DEBUG or loop_no < 2:
        print("[" + dt_string + "] pzem: Publishing MQTT topic {} value {} on loop {}".format(topic, reg_val, loop_no ) )
        # print("topic=" + topic)
    pub.single(topic , "{0:.1f}".format(reg_val), qos=2, hostname=MQTT_HOST, port=MQTT_PORT, client_id="sdm630_mqtt")

while 1:
  result = None
  loop += 1
  retry = 1

  while result == None and retry < 5:

    retry += 1
    try:
#    if True:
        pz0 = minimalmodbus.Instrument("/dev/ttyUSB0", 1,debug=False)
        pz1 = minimalmodbus.Instrument("/dev/ttyUSB1", 1,debug=False)
        pz0.serial.timeout = 0.1 # had to bump this up from the default of 0.05
        pz1.serial.timeout = 0.1 # had to bump this up from the default of 0.05
        pz0.serial.baudrate = 9600
        pz1.serial.baudrate = 9600

        #print("USB port 0")
        VOLT0 = pz0.read_register(0, 0, 4) * 0.1
        AMPS0 = pz0.read_register(1, 0, 4) * 0.001
        WATT0 = pz0.read_register(3, 0, 4) * 0.1
        WHRS0 = pz0.read_register(5, 0, 4) 
        FREQ0 = pz0.read_register(7, 0, 4) * 0.1
        PWRF0 = pz0.read_register(8, 0, 4) * 0.01

        #print("USB port 1")
        VOLT1 = pz1.read_register(0, 0, 4) * 0.1
        AMPS1 = pz1.read_register(1, 0, 4) * 0.001
        WATT1 = pz1.read_register(3, 0, 4) * 0.1
        WHRS1 = pz1.read_register(5, 0, 4) 
        FREQ1 = pz1.read_register(7, 0, 4) * 0.1
        PWRF1 = pz1.read_register(8, 0, 4) * 0.01

        #print("both ports combined")
        VOLT = (pz0.read_register(0, 0, 4) + pz1.read_register(0, 0, 4) ) * 0.1
        AMPS = (pz0.read_register(1, 0, 4) + pz1.read_register(1, 0, 4) ) * 0.001
        WATT = (pz0.read_register(3, 0, 4) + pz1.read_register(3, 0, 4) ) * 0.1
        WHRS = (pz0.read_register(5, 0, 4) + pz1.read_register(5, 0, 4) )
        FREQ = (pz0.read_register(7, 0, 4) + pz1.read_register(7, 0, 4) ) * 0.1
        PWRF = (pz0.read_register(8, 0, 4) + pz1.read_register(8, 0, 4) ) * 0.01

        now=datetime.today()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        print("[" + dt_string + "] pzem: publishing topics loop # " + str(loop) );
        if DEBUG or loop < 2:
            print("[" + dt_string + "] pzem: publishing topic " + MQTT_TOPIC + "lastdatasent " + dt_string)
        pub.single(MQTT_TOPIC + "lastdatasent" , dt_string, qos=2, hostname=MQTT_HOST, port=MQTT_PORT, client_id="sdm630_mqtt")

        publish_value("0","volts",VOLT0, loop);
        publish_value("0","watts",WATT0, loop);
        publish_value("0","amps",AMPS0, loop);
        publish_value("0","whrs",WHRS0, loop);
        publish_value("0","freq",FREQ0, loop);
        publish_value("0","pwrf",PWRF0, loop);

        publish_value("1","volts",VOLT1, loop);
        publish_value("1","watts",WATT1, loop);
        publish_value("1","amps",AMPS1, loop);
        publish_value("1","whrs",WHRS1, loop);
        publish_value("1","freq",FREQ1, loop);
        publish_value("1","pwrf",PWRF1, loop);

        publish_value("2","volts",VOLT, loop);
        publish_value("2","watts",WATT, loop);
        publish_value("2","amps",AMPS, loop);
        publish_value("2","whrs",WHRS, loop);
        publish_value("2","freq",FREQ, loop);
        publish_value("2","pwrf",PWRF, loop);

        result = 1
        time.sleep(30)
        del pz0
        del pz1
#    else:
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print("*** Exception, trying again, try %d ****" % retry);
        del pz0
        del pz1
        time.sleep(1)

        pass



