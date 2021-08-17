#!/usr/bin/python2

import minimalmodbus
import sys
import time

pz0 = minimalmodbus.Instrument("/dev/ttyUSB0", 1,debug=False)
pz0.serial.timeout = 0.1 # had to bump this up from the default of 0.05
pz0.serial.baudrate = 9600
pz1 = minimalmodbus.Instrument("/dev/ttyUSB1", 1,debug=False)
pz1.serial.timeout = 0.1 # had to bump this up from the default of 0.05
pz1.serial.baudrate = 9600


for i in range(5):
   WHRS = pz0.read_register(5, 0, 4) 
   print("WHrs0: %0.3f" % WHRS);
   if WHRS == 0:
       print ("Whrs = 0.  Done.")
       break

   pz0._performCommand(66,'')
   time.sleep( 1 ) 

for i in range(5):
   WHRS = pz1.read_register(5, 0, 4) 
   print("WHrs1: %0.3f" % WHRS);
   if WHRS == 0:
       print ("Whrs = 0.  Done.")
       break

   pz1._performCommand(66,'')
   time.sleep( 1 ) 
    
