#!/usr/bin/python

import minimalmodbus
import sys

if len(sys.argv) <= 1:
    s = '-a'
else:
    s = sys.argv[1]

pz = minimalmodbus.Instrument("/dev/ttyUSB0", 1,debug=False)
pz.serial.timeout = 0.1 # had to bump this up from the default of 0.05
pz.serial.baudrate = 9600

VOLT = pz.read_register(0, 0, 4) * 0.1
AMPS = pz.read_register(1, 0, 4) * 0.001
WATT = pz.read_register(3, 0, 4) * 0.1
WHRS = pz.read_register(5, 0, 4) 
FREQ = pz.read_register(7, 0, 4) * 0.1
PWRF = pz.read_register(8, 0, 4) * 0.01

if s == '-v':
   print("Volts %0.3f" % VOLT);
elif s ==  '-w':
   print("Watts %0.3f" % WATT)
elif s ==  '-c':
   print("Amps %0.8f" % AMPS)
elif s == '-h':
   print("WHrs %0.3f" % WHRS);
elif s == '-f':
   print("Freq %0.3f" % FREQ);
elif s == '-p':
   print("Pwrf %0.3f" % PWRF);
else:
    print("Volts %0.3f" % VOLT);
    print("Watts %0.3f" % WATT)
    print("Amps %0.3f" % AMPS)
    print("WHrs %0.3f" % WHRS);
    print("Freq %0.3f" % FREQ);
    print("Pwrf %0.3f" % PWRF);

        


