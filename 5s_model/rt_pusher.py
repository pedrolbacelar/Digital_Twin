#!/usr/bin/env python3

#--- dispatch policy is always send by the station 1
#--- dispatch plicy is send by the station, when the part leaves the station

#--- import required packages

import paho.mqtt.client as mqtt
import json
#import datetime
import time
from time import sleep
from ev3dev.ev3 import *

#--- declaring optical sensors
sensor=ColorSensor(INPUT_4)
sensor.mode='COL-REFLECT'
colors=('unknown','black','blue','green','yellow','red','white','brown')

#--- other variables
system_status = "stop"
next_station = "station_3"
policy = ["-/-"]
part_count = 0
pos_station_3 = 180
pos_neutral = 0
pos_station_4 = "-180"
pusher_speed = 400

#--- initializing pusher
pusher = MediumMotor('outD')
pusher.reset()

print("pusher program Activated")
stop_status = 0


#--- defining topics to subscribe
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic = "system_status")
    client.subscribe(topic = "trace")

#--- manipulation of subscribed message data
def on_message(client, userdata, msg):
    # define global variables
    global system_status
    global policy
    global part_count
    # print(msg.payload)
    print(str(msg.payload.decode("utf-8")))     #-- to print the message string
    

    #--- start/stop of system
    if msg.topic == "system_status":
        message = str(msg.payload.decode("utf-8"))
        if message == "start":
            system_status = message
            print("Pusher is started")
        if message == "stop":
            system_status = message
            print("Pusher is stoped")

    #--- part dispatch policy
    #--- payload expected a. {"part_id":"1","policy":"3"}
    #--- payload expected b. {"part_id":"1","policy":"4"}
    if msg.topic == "trace":
        message = json.loads(msg.payload.decode("utf-8"))
        if message["machine_id"] == "2" and message["status"] == "Finished":
            part_count += 1
            print("in message",part_count)
            policy.append(message["queue_id"])
        


def open_station_3():
    print("ok. moving to station 3")
    sleep(1)
    pusher.run_to_abs_pos(position_sp = -180, speed_sp = pusher_speed)
    sleep(2)
    pusher.run_to_abs_pos(position_sp = 0, speed_sp = pusher_speed)
    sleep(1)
    pusher.stop(stop_action='coast')

def open_station_4():
    print("ok. moving to station 4")
    pusher.run_to_abs_pos(position_sp = -360, speed_sp = pusher_speed)
    sleep(2)
    pusher.run_to_abs_pos(position_sp = 0, speed_sp = pusher_speed)
    sleep(1)
    pusher.stop(stop_action='coast')



client = mqtt.Client()
client.connect("192.168.0.50",1883,60) # verify the IP address before connect
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()
try:
    while True:
        if system_status == "start":
            stop_status = 1
            if part_count > 0:
                #--- policy: towards station 3
                if sensor.value() > 20 and policy[len(policy) - part_count] == "3":
                    open_station_3()
                    part_count -= 1
                    print("policy to 3")
                    next_station = "station_4"

                #--- policy: towards station 4
                elif sensor.value() > 20 and policy[len(policy) - part_count] == "4":
                    open_station_4()
                    part_count -= 1
                    print("policy to 4")
                    next_station = "station_3"
        elif system_status == "stop":
            if stop_status == 1:
              pusher.run_to_abs_pos(position_sp = 0, speed_sp = pusher_speed)
              pusher.stop(stop_action='coast')
              policy = ["-/-"]
              part_count = 0
              print("pusher stopped")
              stop_status = 0
            
except KeyboardInterrupt:
    print('INTERRUPTED FROM PC')
    print('Pusher program is killed.')
    # pusher.run_to_abs_pos(position_sp = 0, speed_sp = pusher_speed)
    pusher.stop(stop_action='coast')    
    client.loop_stop()    
    client.disconnect()
    



            

