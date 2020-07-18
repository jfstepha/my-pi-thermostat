#!/usr/bin/python2

import minimalmodbus
import sys
import argparse
import time

parser = argparse.ArgumentParser(description='Read the power values from the pzem power meter')
parser.add_argument('-u','--usbport', help='select which usb port (0 or 1.  2=both)', type=int)
parser.add_argument('-a','--all', help='print all measurable values', action="store_true")
parser.add_argument('-v','--volts', help='print voltage', action="store_true")
parser.add_argument('-w','--watts', help='print wattage', action="store_true")
parser.add_argument('-c','--current', help='print current', action="store_true")
parser.add_argument('-t','--watthours', help='print watt hours', action="store_true")
parser.add_argument('-f','--frequency', help='print frequency', action="store_true")
parser.add_argument('-p','--power', help='print power', action="store_true")
args = parser.parse_args()

result = None
retry = 0


while result == None and retry < 5:
    retry += 1
    try:
        pz0 = minimalmodbus.Instrument("/dev/ttyUSB0", 1,debug=False)
        pz1 = minimalmodbus.Instrument("/dev/ttyUSB1", 1,debug=False)
        pz0.serial.timeout = 0.1 # had to bump this up from the default of 0.05
        pz1.serial.timeout = 0.1 # had to bump this up from the default of 0.05
        pz0.serial.baudrate = 9600
        pz1.serial.baudrate = 9600

        if args.usbport == 0:
            #print("USB port 0")
            VOLT = pz0.read_register(0, 0, 4) * 0.1
            AMPS = pz0.read_register(1, 0, 4) * 0.001
            WATT = pz0.read_register(3, 0, 4) * 0.1
            WHRS = pz0.read_register(5, 0, 4) 
            FREQ = pz0.read_register(7, 0, 4) * 0.1
            PWRF = pz0.read_register(8, 0, 4) * 0.01

        elif args.usbport == 1:
            #print("USB port 1")
            VOLT = pz1.read_register(0, 0, 4) * 0.1
            AMPS = pz1.read_register(1, 0, 4) * 0.001
            WATT = pz1.read_register(3, 0, 4) * 0.1
            WHRS = pz1.read_register(5, 0, 4) 
            FREQ = pz1.read_register(7, 0, 4) * 0.1
            PWRF = pz1.read_register(8, 0, 4) * 0.01
        elif args.usbport == 2:
            #print("both ports combined")
            VOLT = (pz0.read_register(0, 0, 4) + pz1.read_register(0, 0, 4) ) * 0.1
            AMPS = (pz0.read_register(1, 0, 4) + pz1.read_register(1, 0, 4) ) * 0.001
            WATT = (pz0.read_register(3, 0, 4) + pz1.read_register(3, 0, 4) ) * 0.1
            WHRS = (pz0.read_register(5, 0, 4) + pz1.read_register(5, 0, 4) )
            FREQ = (pz0.read_register(7, 0, 4) + pz1.read_register(7, 0, 4) ) * 0.1
            PWRF = (pz0.read_register(8, 0, 4) + pz1.read_register(8, 0, 4) ) * 0.01

        else:
            raise Exception("invalid usb port: %s" % args.usbport)


        if args.volts:
           print("Volts %0.3f" % VOLT);
        elif args.watts:
           print("Watts %0.3f" % WATT)
        elif args.current:
           print("Amps %0.8f" % AMPS)
        elif args.watthours:
           print("WHrs %0.3f" % WHRS);
        elif args.frequency:
           print("Freq %0.3f" % FREQ);
        elif args.power:
           print("Pwrf %0.3f" % PWRF);
        else:
            print("Volts %0.3f" % VOLT);
            print("Watts %0.3f" % WATT)
            print("Amps %0.3f" % AMPS)
            print("WHrs %0.3f" % WHRS);
            print("Freq %0.3f" % FREQ);
            print("Pwrf %0.3f" % PWRF);
        result = 1
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print "*** Exception, trying again, try %d ****" % retry
        del pz0
        del pz1
        time.sleep(0.1)

        pass



            


