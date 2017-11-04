#!/bin/bash
# Setup:
#sudo adduser jfstepha
# log in as jfstepha
#mkdir bin
#cd bin
#git clone https://github.com/jfstepha/my-pi-thermostat.git
#cd my-pi-thermo
#mkdir logs
# change the autologin user in /etc/lightdm/lightdm.conf
# add this to .config/autostart/.desktop:
#[Desktop Entry]
#Type=Application
#Exec=/home/jfstepha/bin/my-pi-thermostat/startup.sh

# also:
#   - sudo adduser jfstepha gpio
#   - copy /etc/network/interfaces for wpa
#   - install python-flask
#   - install python-wxgtk2.8
#   - sudo apt-get install python-wxgtk2.8
#   - add "jfstepha ALL=(ALL) NOPASSWD: ALL" to sudoers file
#   - install AdafruitDHT: https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
#   - install Adafruit Pi TFT drivers: https://learn.adafruit.com/adafruit-2-8-pitft-capacitive-touch/easy-install
#   - Edit config file
#   - sudo usermod -a -G gpio jfstepha
#   - add wifi ssid and password in /etc/network/interfaces
#   = how to change the theme?
#   - make a "status" file that looks like this:
#71.0
#heat


cd /home/jfstepha/bin/my-pi-thermostat
# DISPLAY=:0.0 ./my_gui.py &
sudo ./gui_lcd.py &
#sudo sh -c './rubustat_daemon.py start > logs/daemonlog_`date +%F`.log 2>&1'
sh -c ./pinger.sh &
sudo sh -c './motion_daemon.py start > logs/motionlog_`date +%F`.log 2>&1'
sudo sh -c './rubustat_web_interface.py > logs/log`date +%F`.log 2>&1'
