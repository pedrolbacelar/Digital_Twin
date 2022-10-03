# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 16:52:00 2021

@author: giova
"""

#!/usr/bin/env python3

# %% 
import json
import pandas as pd
import time
from time import sleep
import numpy as np
#from influx import InfluxDB    
from influxdb import InfluxDBClient

# %% MQTT

import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("topic/control-production")
    client.subscribe("topic/control-pushers")
  
def on_message(client, userdata, msg): 
    print("message received: ")
    print(msg.payload.decode())


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost",1883,60)

client.loop_start()

# %% INFLUX DB

# db = InfluxDBClient(host='192.168.0.50', port=8086)
# db.switch_database('lego')


# %% STEP 1 check number in
#number_in = 1 # this must result from the Influx Query

sleep(5)

data_out = json.dumps({ "station": 2, "control": "pass"}, indent = 4)
client.publish("topic/control-pushers", data_out)

sleep(2)

data_out = json.dumps({ "station": 2, "control": "push"}, indent = 4)
client.publish("topic/control-pushers", data_out)

sleep(1)

data_out = json.dumps({ "station": 2, "control": "pass"}, indent = 4)
client.publish("topic/control-pushers", data_out)


client.loop_stop()


