#!/usr/bin/python3
# this requires the pylittterbot library
# it came from https://pypi.org/project/pylitterbot/
# and from github https://github.com/natekspencer/pylitterbot

# note that I have only one command channel, so any command is sent to all robots.
# if there were multiple robots, the set_name would be dangerous, so I've commented that out.

import asyncio
import time
from datetime import datetime

from pylitterbot import Account

from pylitterbot.enums import LitterBoxCommand, LitterBoxStatus
from pylitterbot.exceptions import InvalidCommandException, LitterRobotException
from pylitterbot.robot import UNIT_STATUS 

topic="litterrobot"

# Set email and password for initial authentication.
username = "jfstepha@gmail.com"
password = "A#1f201e59e7"

import paho.mqtt.client as mqtt

def do_subscribe( client, topicp ):
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    print("[" + dt_string + "] pylitter_mqtt: subscribing to topic:" + topicp );
    client.subscribe( topicp )

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    do_subscribe( client, topic+"/cmd/reset_settings" )
    do_subscribe( client, topic+"/cmd/start_cleaning" )
    do_subscribe( client, topic+"/cmd/set_night_light" )
    do_subscribe( client, topic+"/cmd/set_panel_lockout" )
    do_subscribe( client, topic+"/cmd/set_power_status" )
    do_subscribe( client, topic+"/cmd/set_wait_time" )
#    do_subscribe( client, topic+"/cmd/set_name" )
    do_subscribe( client, topic+"/cmd/set_sleep_mode" )
    do_subscribe( client, topic+"/cmd/reset_waste_drawer" )

# The callback for when a PUBLISH message is received from the server.

async def on_message_async(client, userdata, msg):
    print("recieved:"+msg.topic+" "+str(msg.payload))
    ary = msg.topic.split("/")
    if len(ary) < 2:
        print("  message format not enough nodes");
    cmd = ary[2];
    pyld = str(msg.payload);
    print("  cmd="+cmd);
    print("  payload="+pyld);
    loop = 0 # loop is required to publish a message, but it's not really used in this context


    if cmd in ['reset_settings','start_cleaning', 'set_night_light','set_panel_lockout','set_power_status','set_wait_time','set_sleep_mode','reset_waste_drawer']:
        print("  got a valid command");
        account = Account()
        # Connect to the API and load robots
        
        await account.connect(username=username, password=password, load_robots=True)
        client.loop_start()
        await asyncio.sleep(2)
        client.loop_stop()

        # Print robots associated with account.
        print("Robots:")
        irobot=1
        for robot in account.robots:
            print("robot#:%d" % irobot);
            print(robot)
            if cmd == "reset_settings":
                print("  resetting settings");
                await( robot.reset_setting() );
            if cmd == "set_night_light":
                print("  setting night light");
                if pyld.upper() == "TRUE":
                   await( robot.set_night_light( LitterBoxCommand.NIGHT_LIGHT_ON) );
                elif pyld.upper() == "FALSE":
                   await( robot.set_night_light( LitterBoxCommand.NIGHT_LIGHT_OFF) );
                publish_value(client, irobot, "night_light_mode_enabled",  robot.night_light_mode_enabled, loop);
            if cmd == "set_panel_lockout":
                if pyld.upper() == "TRUE":
                   await( robot.set_night_light( LitterBoxCommand.LOCK_ON) );
                if pyld.upper() == "FALSE":
                   await( robot.set_night_light( LitterBoxCommand.LOCK_ON) );
            if cmd == "set_power_status:":
                if pyld.upper() == "ON":
                   await( robot.set_power_status( LitterBoxCommand.POWER_ON) );
                if pyld.upper() == "OFF":
                   await( robot.set_power_status( LitterBoxCommand.POWER_OFF) );
            if cmd == "set_wait_time":
                   await( robot.set_wait_time( pyld ) );
            if cmd == "set_name":
                   await( robot.set_name( pyld ) );
            if cmd == "set_sleep_mode":
                   await( robot.set_sleeop_mode( pyld ) );
            if cmd == "reset_waste_drawer":
                   await( robot.reset_waste_drawer( pyld ) );

            client.loop_start()
            await asyncio.sleep(1)
            client.loop_stop()
            
            await publish_states( client, irobot, robot, 0 )
            irobot += 1

            client.loop_start()
            await asyncio.sleep(2)
            client.loop_stop()



    else:
        print("  message topic " + msg.topic + " not recognized");

def on_message(client, userdata, msg):
    asyncio.run( on_message_async(client, userdata, msg) )

def publish_value( client, irobot, topic_sub, value, loop):
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    topicp = topic +"/" + str(irobot) + "/status/" + topic_sub
    if loop < 2:
        print("[" + dt_string + "] pylitter_mqtt: publishing topic:" + topicp + " value:" + str(value) + " for bot %d" % irobot);
    client.publish(topicp, str(value) );

async def publish_states( client, irobot, robot, loop ): 
    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    print("[" + dt_string + "] pylitter_mqtt: refreshing data:");
    await( robot.refresh() );

    now=datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    print("[" + dt_string + "] pylitter_mqtt: publishing topics:");
    publish_value(client, irobot, "status", robot.status, loop );
    publish_value(client, irobot, "status_code", robot.status_code, loop );
    publish_value(client, irobot, "status_text", robot.status_text, loop );
    publish_value(client, irobot, "waste_drawer_level",  robot.waste_drawer_level, loop ); 
    publish_value(client, irobot, "clean_cycle_wait_time_minutes",  robot.clean_cycle_wait_time_minutes, loop);
    publish_value(client, irobot, "cycle_capacity",  robot.cycle_capacity, loop);
    publish_value(client, irobot, "cycle_count",  robot.cycle_count, loop);
    publish_value(client, irobot, "cycles_after_drawer_full",  robot.cycles_after_drawer_full, loop);
    publish_value(client, irobot, "device_type",  robot.device_type, loop);
    publish_value(client, irobot, "did_notify_offline",  robot.did_notify_offline, loop);
    publish_value(client, irobot, "drawer_full_indicator_cycle_count",  robot.drawer_full_indicator_cycle_count, loop);
    publish_value(client, irobot, "is_drawer_full_indicator_triggered",  robot.is_drawer_full_indicator_triggered, loop);
    publish_value(client, irobot, "is_onboarded",  robot.is_onboarded, loop);
    publish_value(client, irobot, "is_sleeping",  robot.is_sleeping, loop);
    publish_value(client, irobot, "is_waste_drawer_full",  robot.is_waste_drawer_full, loop);
    publish_value(client, irobot, "last_seen",  robot.last_seen, loop);
    publish_value(client, irobot, "model",  robot.model, loop);
    publish_value(client, irobot, "name",  robot.name, loop);
    publish_value(client, irobot, "night_light_mode_enabled",  robot.night_light_mode_enabled, loop);
    publish_value(client, irobot, "panel_lock_enabled",  robot.panel_lock_enabled, loop);
    publish_value(client, irobot, "power_status",  robot.power_status, loop);
    publish_value(client, irobot, "setup_date",  robot.setup_date, loop);
    publish_value(client, irobot, "sleep_mode_enabled",  robot.sleep_mode_enabled, loop);
    publish_value(client, irobot, "sleep_mode_start_time",  robot.sleep_mode_start_time, loop);
    publish_value(client, irobot, "sleep_mode_end_time",  robot.sleep_mode_end_time, loop);



async def lr_main(client):
    loop = 0
    while(1):
        try:
            loop += 1
            # should be able to loop forever, and the asych will allow mqtt callbacks to happen
            # Create an account.
            account = Account()
            # Connect to the API and load robots
            await account.connect(username=username, password=password, load_robots=True)

            # Print robots associated with account.
            print("Robots:")
            irobot=1
            for robot in account.robots:
                now=datetime.today()
                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                print("[" + dt_string + "] pylitter_mqtt: robot#:%d loop %d" % (irobot,loop));
                print(robot)

                #print("robot insight:")
                insight = await( robot.get_insight() );
                print( str( insight ) )
                publish_value(client, irobot, "insights",  str(insight), loop);
                #print("getting activity history:");

                # this is long:
                # history = await( robot.get_activity_history() );
                # print( str( history ) );

                await publish_states( client, irobot, robot, loop )

                irobot += 1;
        except KeyboardInterrupt:
             print("Keyboard interrupt")
             exit()
        except:
             print("[%s] %s exception " % (self.name, datetime.datetime.now() ), sys.exc_info() ) 

        client.loop_start()
        await asyncio.sleep(60)
        client.loop_stop()



def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    asyncio.run(lr_main(client))




if __name__ == "__main__":
    main()
