# -*- coding: utf-8 -*-
"""
----MQTT subscribe code----

Runs on Mosquitto broker
InfluxDB database not included
Ip address available from CMD command: ipconfig all
"""

#!/usr/bin/env python3

# import required packages

import paho.mqtt.client as mqtt
import json
import pandas as pd
#import datetime
import time
from time import sleep
import numpy as np
from influx import Influxdb

# connect to influx
db = InfluxDB('http://localhost:8086',precision='ms')  # select server ip address
NOME_DATABASE = "test"  # select database name

# defining topics to subscribe

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe(topic="activity")

# manipulation of subscribed message data
def on_message(client, userdata, msg):
    # define global variables
    #print(msg.payload) 
    print(str(msg.payload.decode("utf-8")))     # to print the message string
    json_value = json.loads(msg.payload.decode())  #converting message string to python dictionary
    # print("time",json_value['time'])   # calling individual data in the json dictionary
    # print(json_value)
    db.write(NOME_DATABASE,'throughput', fields={"thput":json_value['thput']}, tags={"event":json_value['event']})



client = mqtt.Client()
client.connect("127.0.0.1",1883,60,) # verify the IP address before connect

client.on_connect = on_connect
client.on_message = on_message


client.loop_start()
condition = True

while condition:        # the system stays connected as long as the condition is "True"
    sleep(1)
    
client.loop_stop()    
client.disconnect()