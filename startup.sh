#!/bin/bash
# change the autologin user in /etc/lightdm/lightdm.conf
# add this to .config/autostart/.desktop:
#[Desktop Entry]
#Type=Application
#Exec=/home/jfstepha/bin/my-pi-thermostat/startup.sh

# also:
#   - install python flask
#   - add "jfstepha ALL=(ALL) NOPASSWD: ALL" to sudoers file
#   - install AdafruitDHT
#   - make a "status" file that looks like this:
#71.0
#heat


cd /home/jfstepha/bin/my-pi-thermostat
DISPLAY=:0.0 ./my_gui.py &
sudo sh -c './rubustat_daemon.py start > logs/daemonlog_`date +%F`.log 2>&1'
sudo sh -c './rubustat_web_interface.py > logs/log`date +%F`.log 2>&1'
