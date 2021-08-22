#!/usr/bin/python


import sys
import time
import os
import ConfigParser

import paho.mqtt.client as mqtt
from datetime import datetime

import I2C_LCD_driver
from time import *

config = ConfigParser.ConfigParser()
config.read("config.txt")
did = config.get('homie','did')


mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_display_string("Starting up..", 1)
temp=""
rh=""

result = None
retry = 0

# MQTT settings
MQTT_HOST="basement-pc"
MQTT_PORT=1883
DEBUG=False
loop=0

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe( "homie/" + did + "/thermostat/temperature")
    client.subscribe( "homie/" + did + "/thermostat/humidity")


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.

    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    global temp
    global rh
    if msg.topic ==  "homie/" + did + "/thermostat/temperature" :
        print("setting temp to " + str(msg.payload) )
        temp = msg.payload
    if msg.topic ==  "homie/" + did + "/thermostat/humidity" :
        print("setting humidity to " + str(msg.payload) )
        rh = msg.payload
    now=datetime.today()
    dt_string = now.strftime("%m/%d %I:%M %p")
    mylcd.lcd_display_string(dt_string, 1)
    mylcd.lcd_display_string("%sF %s%%" % (temp, rh), 2)

client = mqtt.Client( did + "-gui")
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect( MQTT_HOST, MQTT_PORT )
client.loop_forever()  # Start networking daemon
