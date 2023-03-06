#!/usr/bin/env python3


#-- you send the start message to initiate the whole system.
#-- The station sends machine_id, activity_type, queue_id to database by mqtt using trace topic
#-- Processing trace includes loading and unloading time inside the processing period.
#-- unloading time is considered to be as a part of tranportation time.
#-- expected mqtt from part_id: {"machine_id":"1","part_id":"12345"}
#-- expected mqtt from RCT-server: {"machine_id":"1","part_id":"12345","policy":"2"}
#-- trace mqtt published: {"machine_id" : "1", "activity_type":"start","queue_id":"1"}
#-- default dispatch policy is alternating. machine initiates with station 2.
#-- blocking condition: BAS
#-- failures are not included
#-- processing times are deterministic
#-- part is recieved is the updated part number and not the RFID Tag ID.

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

#--- process time of station excluding the loading and unloading time
process_time = 4    # advised to have no less than 5s of gap between two parts in the downstream conveyor to not have problems with pusher.

system_status = "stop"
advice_list = dict()
station_status = "idle"
start_status = 0
stop_status = 0
advice_status = 0
current_station = "3"   # we start with 2. to change to 2, we initaite it as 3
print("Station 1 program Activated")

#--- main functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #--- subscribe topics
    client.subscribe(topic = "system_status")
    client.subscribe(topic = "RCT-server")
    client.subscribe(topic = "part_id")

def on_message(client, userdata, msg):
    # define global variables
    global system_status
    global start_status
    global stop_status
    global current_part_id
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
        message = json.loads(msg.payload.decode("utf-8"))
        if message["macihne_id"] == "1":    # we enter the policy advice into json dictionay for future use. You can send the part policy whenever you want.
            advice_list[message["part_id"]] = message["policy"]
            print("on message, advice :-", message["part_id"], " : ", advice_list[message["part_id"]])


    if msg.topic == "part_id":      # listening to current part id for dispath policy
        message = json.loads(msg.payload.decode("utf-8"))
        if message["machine_id"] == 1:
            current_part_id = message["part_id"]

        
        
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
                payload = {"machine_id" : "1", "activity_type":"start","queue_id":"1"}
                client.publish(topic = "trace", payload= json.dumps(payload))
                sleep(1)
                pusher.stop(stop_action='coast')
                sleep(1)
                pusher.run_forever(speed_sp = -pusher_speed)
                sleep(1)
                pusher.stop(stop_action='coast')
                station_status = "busy"
                
            if station_sensor.value() > 4:
                station.stop(stop_action = 'hold')
                advice_list.append("default")
                
                sleep(process_time)

                if blocking_sensor.value() < 4:
                    #--- dispatch the part from the station
                    station.run_forever(speed_sp = -station_speed)

                    #--- policy assignment #--- defualts to: alternating policy
                    if current_part_id in advice_list:
                        current_station = advice_list[current_part_id]
                    elif current_station ==  "2":
                        current_station = "3"
                    elif current_station == "3":
                        current_station = "2"

                    #--- unloading time. Also a part of processing time.
                    sleep(3)    #--- delay for the part to move to grey conveyor.

                    #--- publish topics
                    payload ={"machine_id" : "1", "activity_type":"finish", "queue_id":current_station}
                    client.publish(topic = "trace", payload= json.dumps(payload))
                    print("current part proceeding to station ", current_station)
                    
                    # delete the part policy from the list so that the policy is not repeated during a default condition.
                    del advice_list[current_part_id]
                    station_status = "idle" # set status to idle for allowing the next part

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
