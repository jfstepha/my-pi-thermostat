#!/usr/bin/python
# Example using a character LCD connected to a Raspberry Pi or BeagleBone Black.
import time
from subprocess import *
import Adafruit_CharLCD as LCD
from datetime import datetime
from time import sleep, strftime
import requests

# Raspberry Pi pin configuration:
lcd_rs        = 25  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 4
lcd_d6        = 26
lcd_d7        = 22
lcd_backlight = 27

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                                   lcd_columns, lcd_rows, lcd_backlight)

lcd.message('Starting...')
print("backlight off")
lcd.set_backlight(1)
time.sleep(0.5)
print("backlight on")
lcd.set_backlight(0)
time.sleep(0.5)
print("Clearing")
lcd.clear()
time.sleep(0.5)
print("Sending hello world:")
lcd.message('Starting...')

cmd = "iwconfig | grep Quality | awk '{print $2}' | cut -d= -f2"

def get_web_val(url):
    retval = -1
    try:
        r = requests.get( url )
        retval = float(r.content)
    except:
        print "live temp request failed"
    return retval


def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

while 1:
    temp = -1
    rh = -1
    lcd.clear()
    wifi = run_cmd(cmd)
    temp = get_web_val("http://localhost/_liveTemp")
    rh = get_web_val( "http://localhost/_liveSensorValue/thermo_BR/rh")
    setpt = get_web_val( "http://lr-thermo/_liveTargetTemp")
    lcd.message('T:%0.1f rh:%0.1f%%' % ( temp, rh ) )
    lcd.message("\nS:%0.1f W:%s" % (setpt, wifi) )
    sleep(10)
