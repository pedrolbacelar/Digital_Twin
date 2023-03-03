#!/usr/bin/env python3

#--- import required packages

import paho.mqtt.client as mqtt
import json
#import datetime
import time
from time import sleep
# from ev3dev.ev3 import *

# #--- declaring optical sensors
# sensor=ColorSensor(INPUT_4)
# sensor.mode='COL-COLOR'
# colors=('unknown','black','blue','green','yellow','red','white','brown')

# #--- initializing pusher
# pusher = MediumMotor('outD')
# pusher.reset()
# pos_neutral = 0
# pusher_speed = 400
# pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
# sleep(1)
# pusher.stop(stop_action='coast')
# print("pusher program Activated")
#--- other variables
system_status = "stop"
next_station = "station_2"
policy = ["-/-"]
part_count = 0
# pusher_speed = 400
# pos_neutral = 0
# pos_station_2 = 180
# pos_station_3 = -180

#--- defining topics to subscribe
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic = "system_status")
    client.subscribe(topic = "dispatch_policy")

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
    #--- payload expected a. {"part_num":"1","policy":"default"}
    #--- payload expected b. {"part_num":"1","policy":"station_2"}
    #--- payload expected c. {"part_num":"1","policy":"station_3"}
    if msg.topic == "dispatch_policy":
        message = json.loads(msg.payload.decode("utf-8"))
        part_count += 1
        policy.append(message["policy"])
        


def open_station_2():
    print("ok. moving to station 2")
    # pusher.run_to_abs_pos(position_sp = pos_station_2, speed_sp = pusher_speed)
    # sleep(2)
    # pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
    # sleep(1)
    # pusher.stop(stop_action='coast')

def open_station_3():
    print("ok. moving to station 3")
    # pusher.run_to_abs_pos(position_sp = pos_station_3, speed_sp = pusher_speed)
    # sleep(2)
    # pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
    # sleep(1)
    # pusher.stop(stop_action='coast')


# color = sensor.value()
color = 5

client = mqtt.Client()
client.connect("localhost",1883,60) # verify the IP address before connect
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()
try:
    while True:
        if system_status == "start":
            if part_count > 0:
                #--- default policy
                if color > 1 and policy[len(policy) - part_count] == "default":
                    if next_station == "station_2":
                        open_station_2()
                        part_count -= 1
                        print("default2")
                        next_station = "station_3"
                    
                    elif next_station == "station_3":
                        open_station_3()
                        part_count -= 1
                        print("default3")
                        next_station = "station_2"

                #--- policy: towards station 2
                elif color > 1 and policy[len(policy) - part_count] == "station_2":
                    open_station_2()
                    part_count -= 1
                    print("policy2")
                    next_station = "station_3"

                #--- policy: towards station 3
                elif color > 1 and policy[len(policy) - part_count] == "station_3":
                    open_station_3()
                    part_count -= 1
                    print("policy3")
                    next_station = "station_2"

except KeyboardInterrupt:
  print('INTERRUPTED FROM PC')
  print('Pusher program is killed.')
#   pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
#   pusher.stop(stop_action='coast')    
  client.loop_stop()    
  client.disconnect()
    
#===============================================================================================================

#!/usr/bin/env python3

#--- import required packages

import paho.mqtt.client as mqtt
import json
#import datetime
import time
from time import sleep
# from ev3dev.ev3 import *

# #--- declaring optical sensors
# station_sensor=ColorSensor(INPUT_2)
# station_sensor.mode='COL-COLOR'
# queue_sensor=ColorSensor(INPUT_1)
# queue_sensor.mode='COL-COLOR'
# blocking_sensor=ColorSensor(INPUT_4)
# blocking_sensor.mode='COL-COLOR'

# colors=('unknown','black','blue','green','yellow','red','white','brown')

# #--- initializing station
# pusher = MediumMotor('outD')
# pusher.reset()
# pos_neutral = 0
# pusher_speed = 400
# pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
# sleep(1)
# pusher.stop(stop_action='coast')

# station = LargeMMotor('outA')
# conveyor = LargeMotor ('outC')

# print("Station 1 program Activated")

# #--- declaring variables
# station_speed = 500
# conveyor_speed = 500
# pusher_speed = 400
# pos_neutral = 0
# pos_extend = 180

# station.run_forever(speed_sp = station_speed)
# conveyor.run_forever(speed_sp = -conveyor_speed)

system_status = "stop"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic = "system_status")
    client.subscribe(topic = "RCT-server")

def on_message(client, userdata, msg):
    # define global variables
    global system_status
    global advice

    # print(msg.payload)
    print(str(msg.payload.decode("utf-8")))     #-- to print the message string

    #--- start/stop of system
    if msg.topic == "system_status":
        message = str(msg.payload.decode("utf-8"))
        if message == "start":
            system_status = message
            print("Station 1 is started")
        if message == "stop":
            system_status = message
            print("Station 1 is stopped")

    #--- RCT-server
    #--- payload expected: a. station_2 b. station_3
    if msg.topic == "RCT-server":
        advice = str(msg.payload.decode("utf-8"))
        # when releasing a part, variable for next part (first part in the queue) is assigned and made ready to write
           

