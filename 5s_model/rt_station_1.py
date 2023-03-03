#!/usr/bin/env python3

#--- you send the start message to initiate the whole system.
#--- import required packages

import paho.mqtt.client as mqtt
import json
#import datetime
import time
from time import sleep
from ev3dev.ev3 import *

#--- declaring optical sensors
station_sensor=ColorSensor(INPUT_4)
station_sensor.mode='COL-COLOR'
queue_sensor=ColorSensor(INPUT_2)
queue_sensor.mode='COL-COLOR'
blocking_sensor=ColorSensor(INPUT_3)
blocking_sensor.mode='COL-COLOR'

colors=('unknown','black','blue','green','yellow','red','white','brown')

#--- initializing station
pusher = MediumMotor('outD')
pusher.reset()
pos_neutral = 0
pusher_speed = 400

conveyor = LargeMotor('outA')
station = LargeMotor ('outC')

#--- declaring variables
conveyor_speed = 300
station_speed = 100
pusher_speed = 400
pos_neutral = 0
pos_extend = 180

process_time = 4    # advised to have no less than 5s of gap between two parts in the downstream conveyor to not have problems with pusher.

system_status = "stop"
advice = "--"  # advised control policy for the pusher
advice_list = ["default"]
station_status = "idle"
start_status = 0
stop_status = 0
advice_status = 0
print("Station 1 program Activated")

#--- main functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #--- subscribe topics
    client.subscribe(topic = "system_status")
    client.subscribe(topic = "RCT-server")

def on_message(client, userdata, msg):
    # define global variables
    global system_status
    global advice
    global advice_status
    global start_status
    global stop_status

    # print(msg.payload)
    print(str(msg.payload.decode("utf-8")))     #-- to print the message string

    #--- start/stop of system
    if msg.topic == "system_status":
        message = str(msg.payload.decode("utf-8"))
        if message == "start":
            system_status = message
            start_status = 1
        if message == "stop":
            system_status = message
            stop_status = 1

    #--- RCT-server
    #--- payload expected: a. station_2 b. station_3
    if msg.topic == "RCT-server":
        advice = str(msg.payload.decode("utf-8"))
        advice_status = 1
        print("on message, advice :", advice)
        # when releasing a part, variable for next part (first part in the queue) is assigned and made ready to write
        
client = mqtt.Client()
client.connect("192.168.0.50",1883,60) # verify the IP address before connect
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()
try:
    while True:
        if system_status == "start":
            conveyor.run_forever(speed_sp = -conveyor_speed)
            station.run_forever(speed_sp = -station_speed)
            if start_status > 0:
                pusher.run_forever(speed_sp=-pusher_speed)
                sleep(1)
                pusher.stop(stop_action='coast')
                start_status = 0
                print("Station 1 is started")

            if queue_sensor.value() > 1 and station_status == "idle":
                pusher.run_forever(speed_sp=pusher_speed)
                sleep(1)
                pusher.stop(stop_action='coast')
                sleep(1)
                pusher.run_forever(speed_sp=-pusher_speed)
                sleep(1)
                pusher.stop(stop_action='coast')
                station_status = "busy"
                
            if station_sensor.value() > 4:
                station.stop(stop_action = 'hold')
                advice_list.append("default")
                
                sleep(process_time)

                station.run_forever(speed_sp = -station_speed)
                #--- publish topics
                print(advice_list[len(advice_list)-2])
                payload ={"part_type" : "1", "policy":advice_list[len(advice_list)-2]}
                client.publish(topic = "dispatch_policy", payload= json.dumps(payload))
                print("in loop, advice_status: ", advice_status)
                if advice_status > 0:
                    advice_list[len(advice_list)-1] = advice
                    advice_status = 0
                station_status = "idle"
                sleep(3)

        elif system_status == "stop" and stop_status > 0:
            conveyor.stop(stop_action = 'coast')
            station.stop(stop_action = 'coast')
            pusher.run_forever(speed_sp=pusher_speed)
            sleep(1)
            pusher.stop(stop_action='coast')
            stop_status = 0
            print("Station 1 is stopped")

except KeyboardInterrupt:
    print('INTERRUPTED FROM PC')
    conveyor.stop(stop_action = 'coast')
    station.stop(stop_action = 'coast')
    print('Station 1 program is killed.')
