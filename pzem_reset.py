#!/usr/bin/python

import minimalmodbus
import sys
import time

pz = minimalmodbus.Instrument("/dev/ttyUSB0", 1,debug=False)
pz.serial.timeout = 0.1 # had to bump this up from the default of 0.05
pz.serial.baudrate = 9600


for i in range(5):
   WHRS = pz.read_register(5, 0, 4) 
   print("WHrs %0.3f" % WHRS);
   if WHRS == 0:
       print ("Whrs = 0.  Done.")
       break

   pz._performCommand(66,'')
   time.sleep( 1 ) 
    
