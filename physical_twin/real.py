#!/usr/bin/env python3

# import required packages

"""
change machine id "mc_id" if required
change ip address of mqtt if required
"""

# import libraries 
from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import paho.mqtt.client as mqtt
import json
# from influx import InfluxDB


#--- Global variables
mc_id=8 # change machine id
delta_max = 300
part_max = 20

pusher_speed = 500
station_speed = 500
conveyor_speed = 500

pusher_time = 0.5
station_delay = 4

process_time = 5
unloading_time = 2

flag_done = True # for verification of part in the station.
counter=0
message_flag = "idle"

# declaring optical sensors
station_sensor=ColorSensor(INPUT_1)
station_sensor.mode='COL-COLOR'
conveyor_sensor=ColorSensor(INPUT_2)
conveyor_sensor.mode='COL-COLOR'
blocking_sensor=ColorSensor(INPUT_3)
blocking_sensor.mode='COL-COLOR'
colors=['unknown','black','blue','green','yellow','red','white','brown'] # do not change the color name or order

# declaring conveyors and the pusher
motor_conveyor = LargeMotor('outA')
motor_station = LargeMotor('outC')
pusher_D= MediumMotor('outD')

# initiating simulation
T_start = time.time() # time of simulation start
print ("simulation started at ",datetime.now())
i=0
i_part=0

# declaring pusher functions
def Pusher_back():
    #--- Pusher: Coming back
    pusher_D.run_forever(speed_sp=pusher_speed)
    sleep(pusher_time)

    pusher_D.stop(stop_action='coast')
    sleep(pusher_time)

def Pusher_push():
    #--- Pusher: Go Ahead
    pusher_D.run_forever(speed_sp=-pusher_speed)
    sleep(pusher_time)
    pusher_D.stop(stop_action='coast')
# declaring subscribe functions

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic="STATUS")
    

def on_message(client, userdata, msg):
    # define global variables
    #print(msg.payload) 
    global message_flag

    print(str(msg.payload.decode("utf-8")))     # to print the message string
    message_flag = msg.payload.decode()


    
try:
    # client connect
    client = mqtt.Client()
    client.connect("192.168.0.50",1883,60) # change ip address if required

    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()

    while True:
        if message_flag == "idle":
            pass

        elif message_flag == '"start"':
            while True:

                T_now = time.time()
                delta = T_now - T_start
                #--- get color of the sensors
                print("station_sensor = ", station_sensor.value())
                print("conveyor_sensor = ", conveyor_sensor.value())

                color_st_sensor = colors[station_sensor.value()]
                color_conv_sensor = colors[conveyor_sensor.value()]

                #--- Pusher
                if flag_done == True:
                    if (color_st_sensor == "black" or color_st_sensor == "unknown") and ((color_conv_sensor != "black")):
                        print("part in the buffer. Arrival time is ", datetime.now())
                        i_part = i_part + 1

                        #--- Station_conveyor on
                        motor_station.run_forever(speed_sp = station_speed) 

                        #--- Pusher: Coming back
                        Pusher_back()

                        #--- Pusher push
                        Pusher_push()

                        flag_done = False


                #--- Loading and Unloading
                if (colors[station_sensor.value()] == "red"): #something is on the station
                    #-- Simulating Processing 
                    motor_station.stop(stop_action = "coast") 
                    sleep(process_time)

                    #-- Simulating Unloading
                    motor_station.run_forever(speed_sp = station_speed)
                    sleep(unloading_time)
                    motor_station.stop(stop_action = "coast") 

                    flag_done = True
                    counter = counter + 1
                    payload = {
                        "counter": counter,
                        "id": mc_id,
                        "ts": time.time()
                    }              
                    client.publish(topic = "OUTPUT", payload= json.dumps(payload))

                if message_flag == '"stop"':
                    motor_conveyor.stop(stop_action = "coast")
                    motor_station.stop(stop_action = "coast")
                    Pusher_back()

                    print("simulation stopped at ", datetime.now())
                                

# emergency stop <ctrl+c>
except KeyboardInterrupt as f:

    print('-----INTERRUPTED FROM PC-----')
    client.loop_stop()    
    client.disconnect()
    #stop all coveyors and pusher motors
    motor_conveyor.stop(stop_action = "coast")
    motor_station.stop(stop_action = "coast")
    pusher_D.stop(stop_action='coast')
