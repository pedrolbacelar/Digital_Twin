#!/usr/bin/env python3

# import required packages

import paho.mqtt.client as mqtt
import json
#import datetime
import time
from time import sleep
from ev3dev.ev3 import *

#--- initializing pusher
pusher = MediumMotor('outD')
pusher.reset()
pos_neutral = 0
pusher_speed = 400
pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
sleep(1)
pusher.stop(stop_action='coast')
print("pusher program Activated")
system_status = "stop"

# defining topics to subscribe
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe(topic = "pusher_status")
  client.subscribe(topic="system_status")

# manipulation of subscribed message data
def on_message(client, userdata, msg):
  # define global variables
  global system_status
  
  #print(msg.payload) 
  print(str(msg.payload.decode("utf-8")))     # to print the message string
  message=str(msg.payload.decode("utf-8"))
  #--- absolute positions of the pusher
  pos_station_2 = 180
  pos_neutral = 0
  pos_station_3 = "-180"
  
  #--- pusher motor speed
  pusher_speed = 400     
  if msg.topic == "system_status":
    if message == "start":
      system_status = message
      print("Pusher is started")

      
    if message == "stop":
      system_status = message
      print("Pusher is stoped")
  
    
  print("1",system_status)
    
  if msg.topic == "pusher_status" and system_status == "start":
    print("2",system_status)
    print("moving to : ",message)
    
    if message == "station_2":
      print("ok. moving to station 2")
      pusher.run_to_abs_pos(position_sp = pos_station_2, speed_sp = pusher_speed)
      sleep(2)
      pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
      sleep(1)
      pusher.stop(stop_action='coast')
     
    elif message == "station_3":
      print("ok. moving to station 3")
      pusher.run_to_abs_pos(position_sp = pos_station_3, speed_sp = pusher_speed)
      sleep(2)
      pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
      sleep(1)
      pusher.stop(stop_action='coast')
    
    else:
      print("Pusher: Wrong choice of selection or wrong MQTT payload.")
      
  elif msg.topic == "pusher_status" and system_status == "stop":
    print("System not started !")


try:
  client = mqtt.Client()
  client.connect("192.168.0.50",1883,60) # verify the IP address before connect
  
  client.on_connect = on_connect
  client.on_message = on_message
  
  
  client.loop_start()
  condition = True
  
  while condition:        # the system stays connected as long as the condition is "True"
      sleep(1)

except KeyboardInterrupt:
  print('INTERRUPTED FROM PC')
  print('Pusher program is killed.')
  pusher.run_to_abs_pos(position_sp = pos_neutral, speed_sp = pusher_speed)
  pusher.stop(stop_action='coast')    
  client.loop_stop()    
  client.disconnect()