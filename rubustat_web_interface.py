#!/usr/bin/python
import os
import subprocess
import re
import ConfigParser
import Queue
import sys
import fcntl



from getIndoorTemp import getIndoorTemp
from getIndoorTemp import getIndoorTemp2
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify

from sensor_server import loopThread 
from smart_thermo import smartLoopThread

pending_state = Queue.Queue()

loopThread= loopThread()
smartLoopThread = smartLoopThread( pending_state )


app = Flask(__name__)
#hard to be secret in open source... >.>
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

config = ConfigParser.ConfigParser()
config.read("config.txt")
ZIP = config.get('weather','ZIP')
HEATER_PIN = int(config.get('main','HEATER_PIN'))
AC_PIN = int(config.get('main','AC_PIN'))
FAN_PIN = int(config.get('main','FAN_PIN'))
MOTION_PIN = int(config.get('main','MOTION_PIN'))
weatherEnabled = config.getboolean('weather','enabled')
hubname = config.get('sensorhub','name')
hubdomain = config.get('sensorhub','domain')
hubishub = int(config.get('sensorhub', 'ishub'))

# to pass state change requests into the smartThermo

#start the daemon in the background
#subprocess.Popen("/usr/bin/python rubustat_daemon.py start", shell=True)

if weatherEnabled == True:
    import pywapi
    def getWeather():
        result = pywapi.get_weather_from_yahoo( str(ZIP), units = 'imperial' )
        string = result['html_description']
        string = string.replace("\n", "")

        #You will likely have to change these strings, unless you don't mind the additional garbage at the end.
        string = string.replace("(provided by <a href=\"http://www.weather.com\" >The Weather Channel</a>)<br/>", "")
        string = string.replace("<br /><a href=\"http://us.rd.yahoo.com/dailynews/rss/weather/Nashville__TN/*http://weather.yahoo.com/forecast/USTN0357_f.html\">Full Forecast at Yahoo! Weather</a><BR/><BR/>", "")
        return string

def getWhatsOn():
    heatStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(HEATER_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
    coolStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(AC_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
    fanStatus = int(subprocess.Popen("cat /sys/class/gpio/gpio" + str(FAN_PIN) + "/value", shell=True, stdout=subprocess.PIPE).stdout.read().strip())

    heatString = "<p id=\"heat\"> heat OFF </p>"
    coolString = "<p id=\"cool\"> cool OFF </p>"
    fanString = "<p id=\"fan\"> fan OFF </p>"
    if heatStatus == 1:
        heatString = "<p id=\"heatOn\"> heat ON </p>"
    if coolStatus == 1:
        coolString = "<p id=\"coolOn\"> cool ON </p>"
    if fanStatus == 1:
        fanString = "<p id=\"fanOn\"> fan ON </p>"

    return heatString + coolString + fanString

def getDaemonStatus():

    try:
        with open('rubustatDaemon.pid'):
            pid = int(subprocess.Popen("cat rubustatDaemon.pid", shell=True, stdout=subprocess.PIPE).stdout.read().strip())
            try:
                os.kill(pid, 0)
                return "<p id=\"daemonRunning\"> Daemon is running. </p>"
            except OSError:
                return "<p id=\"daemonNotRunning\"> DAEMON IS NOT RUNNING. </p>"
    except IOError:
        # automatically restart daemon
        print "restarting daemon"
        subprocess.Popen("/usr/bin/python rubustat_daemon.py start", shell=True)
        return "<p id=\"daemonNotRunning\"> DAEMON IS NOT RUNNING. </p>"

@app.route('/')
def my_form():
    f = open("status", "r")
    targetTemp = f.readline().strip()
    mode = f.readline()
    f.close()
    weatherString = ""
    if weatherEnabled == True:
        try:
            weatherString = getWeather()
        except:
            weatherString = "Couldn't get remote weather info! <br><br>"

    whatsOn = getWhatsOn()

    #find out what mode the system is in, and set the switch accordingly
    #the switch is in the "cool" position when the checkbox is checked

    daemonStatus=getDaemonStatus()

    if mode == "heat":
        checked = ""
    elif mode == "cool":
        checked = "checked=\"checked\""
    else:
        checked = "Something broke"
    return render_template("form.html", targetTemp = targetTemp, \
                                        weatherString = weatherString, \
                                        checked = checked, \
                                        daemonStatus = daemonStatus, \
                                        whatsOn = whatsOn)

@app.route("/_setTarget/<target>", methods=['GET'])
def my_set_form_get(target):
    file = open("status", "r")
    oldTargetTemp = float(file.readline())
    mode = file.readline()
    file.close()

    f = open("status", "w")
    f.write(str(target) + "\n" + mode)
    f.close()
    return "success" 

@app.route("/_setMode/<mode>", methods=['GET'])
def setMode(mode):
    file = open("status", "r")
    TargetTemp = float(file.readline())
    oldMode = file.readline()
    file.close()

    f = open("status", "w")
    f.write(str(TargetTemp) + "\n" + mode)
    f.close()
    return "success" 

@app.route("/", methods=['POST'])
def my_form_post():

    text = request.form['target']
    mode = "heat"

    #default mode to heat 
    #cool if the checkbox is returned, it is checked
    #and cool mode has been selected

    if 'onoffswitch' in request.form:
        mode = "cool"
    newTargetTemp = text.upper()
    match = re.search(r'^\d{2}$',newTargetTemp)
    if match:
        f = open("status", "w")
        f.write(newTargetTemp + "\n" + mode)
        f.close()
        flash("New temperature of " + newTargetTemp + " set!")
        return redirect(url_for('my_form'))
    else:
        flash("That is not a two digit number! Try again!")
        return redirect(url_for('my_form'))


#the flask views for the incredible and probably
#not at all standards compliant live data

@app.route('/_liveTemp', methods= ['GET'])
def updateTemp():

    return "%0.3f" % loopThread.sensors['sum_'+hubdomain].temp

@app.route('/_liveTemp2', methods= ['GET'])
def updateTemp2():

    return "%0.3f" % loopThread.sensors[hubname].temp

@app.route('/_liveWhatsOn', methods= ['GET'])
def updateWhatsOn():

    return getWhatsOn()

@app.route('/_liveDaemonStatus', methods= ['GET'])
def updateDaemonStatus():

    return getDaemonStatus()

@app.route('/_liveTargetTemp', methods= ['GET'])
def getTargetTemp():
    try:
        file = open("status", "r")
        targetTemp = float(file.readline())
        mode = file.readline()
        file.close()
        return str(targetTemp)
    except IOError:
        return "error"

@app.route('/_liveMode', methods= ['GET'])
def getMode():
    try:
        file = open("status", "r")
        targetTemp = float(file.readline())
        mode = file.readline()
        file.close()
        return str(mode)
    except IOError:
        return "error"

@app.route('/_liveMotion', methods= ['GET'])
def getMotion():
    try:
        f = open("/dev/shm/motion", "r")
        # make it a non-blocking read:
        fd = f.fileno()
        flag = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
        motion = int(f.readline())
        f.close()
        return str(motion)
    except IOError:
        return "IOerror"
    except:
        return "error: %s" % str( sys.exec_info()[0] )


@app.route('/_liveSensor/<sensorname>', methods= ['GET'])
def getSensorAll(sensorname):
    try:
        return str(loopThread.sensors[sensorname])
    except IOError:
        return "error"

@app.route('/_liveSensorValue/<sensorname>/<paramname>', methods= ['GET'])
def getSensor(sensorname, paramname):
    try:
        return str(loopThread.sensors[sensorname].get_dict()[paramname])
    except IOError:
        return "error"

@app.route('/_liveSmartState', methods= ['GET'])
def getSmartState():
    try:
        return str(smartLoopThread.smartStateInt())
    except IOError:
        return "error"

@app.route('/_liveSmartStateString', methods= ['GET'])
def getSmartStateString():
    try:
        return str(smartLoopThread.smartStateStr())
    except IOError:
        return "error"

@app.route('/_liveTargetDayActive', methods= ['GET'])
def getTargetDayActive():
    try:
        return str(smartLoopThread.set_day_active)
    except IOError:
        return "error"

@app.route('/_liveTargetDayIdle', methods= ['GET'])
def getTargetDayIdle():
    try:
        return str(smartLoopThread.set_day_idle)
    except IOError:
        return "error"

@app.route('/_liveTargetNightActive', methods= ['GET'])
def getTargetNightActive():
    try:
        return str(smartLoopThread.set_night_active)
    except IOError:
        return "error"

@app.route('/_liveTargetNightIdle', methods= ['GET'])
def getTargetNightIdle():
    try:
        return str(smartLoopThread.set_night_idle)
    except IOError:
        return "error"

@app.route('/_liveOverrideRemaining', methods= ['GET'])
def getOverrideRemaining():
    try:
        return str(smartLoopThread.override_remaining)
    except IOError:
        return "error"

@app.route("/_setTargetDayActive/<target>", methods=['GET'])
def setTargetDayActive(target):
    smartLoopThread.set_day_active = float(target)
    return "success" 

@app.route("/_setTargetDayIdle/<target>", methods=['GET'])
def setTargetDayIdle(target):
    smartLoopThread.set_day_idle = float(target)
    return "success" 

@app.route("/_setTargetNightActive/<target>", methods=['GET'])
def setTargetNightActive(target):
    smartLoopThread.set_night_active = float(target)
    return "success" 

@app.route("/_setTargetNightIdle/<target>", methods=['GET'])
def setTargetNightIdle(target):
    smartLoopThread.set_night_idle = float(target)
    return "success" 

@app.route("/_setSmartState/<mode>", methods=['GET'])
def setSmartState(mode):
    print("Setting smart state to %d" % int(mode))
    pending_state.put( int( mode ) )
    #smartLoopThread.pending_state.append(int(mode))
    return "success" 

@app.route('/_dumpSensors/', methods= ['GET'])
def dumpSensors():
    try:
        s = ""
        for key in loopThread.sensors:
            s = s + str( loopThread.sensors[key] ) + "<br>" 
        return s
    except IOError:
        return "error"

@app.route('/_dumpSmartThermo/', methods= ['GET'])
def dumpSmartThermo():
    try:
        s = ""
        s = s + str( smartLoopThread.smart_state[1] ) + "<br>" 
        s = s + str( smartLoopThread.set_day_active ) + "<br>" 
        s = s + str( smartLoopThread.set_day_idle ) + "<br>" 
        s = s + str( smartLoopThread.set_night_active ) + "<br>" 
        s = s + str( smartLoopThread.set_night_idle ) + "<br>" 
        s = s + str( smartLoopThread.loops_since_motion ) + "<br>" 
        s = s + str( smartLoopThread.override_remaining ) + "<br>" 
        return s
    except IOError:
        return "error"

if __name__ == "__main__":
    loopThread.setDaemon(True)
    loopThread.start() 
    smartLoopThread.setDaemon(True)
    smartLoopThread.start()
    app.run("0.0.0.0", port=80)
