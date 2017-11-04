#!/usr/bin/env python

import sys, time
import subprocess
from daemon import Daemon

import ConfigParser

class MyDaemon(Daemon):
	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
		self.time_since_motion = 0
		self.ticks_until_print = 0

	def run(self):
		print "Deamon in run"

		config = ConfigParser.ConfigParser()
		config.read("config.txt")
		MOTION_PIN = int(config.get('main','MOTION_PIN'))
		subprocess.Popen("echo " + str(MOTION_PIN) + " > /sys/class/gpio/export", shell=True)
		
		while True:
			if self.ticks_until_print  < 1:
				print "main loop time since motion = %d" % self.time_since_motion
				self.ticks_until_print = 120
			self.ticks_until_print -= 1
			motionStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(MOTION_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
			if motionStatus == 1:
				self.time_since_motion = 0
			else:
				self.time_since_motion += 1
			time.sleep(1)

			f = open('/dev/shm/motion','w')
			f.write("%d\n" % self.time_since_motion)


if __name__ == "__main__":
	daemon = MyDaemon('/tmp/daemon-motion.pid', stdout='/tmp/daemon-motion.out', stderr='/tmp/daemon-motion.err')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
			daemon.ticks = 4
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
