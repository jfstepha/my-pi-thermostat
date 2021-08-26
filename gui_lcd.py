#!/usr/bin/python3


import sys
import time
import os

from datetime import datetime

import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_display_string("Starting up..", 1)
temp=""
rh=""

result = None
retry = 0

while 1:
	stream = os.popen('./read_dht22.py')
	dht_str = stream.read()
	now=datetime.today()
	dt_string = now.strftime("%m/%d %I:%M %p")
	print("[" + dt_string + "]" + "  Got DHT string: " + dht_str);
	# string should be "temp:74.120,rh:41.500"
	if dht_str.find("temp:") == 0:
	    ary = dht_str.split(",");
	    temp_part = ary[0]
	    rh_part = ary[1]
	    ary = temp_part.split(":");
	    temperature_f = float( ary[1] );
	    ary = rh_part.split(":");
	    humidity = float( ary[1] );


	now=datetime.today()
	dt_string = now.strftime("%m/%d %I:%M %p")
	mylcd.lcd_display_string(dt_string, 1)
	mylcd.lcd_display_string("%sF %s%%" % (temperature_f, humidity), 2)
	time.sleep(10)

