""" 
store.py
created by: Pedro Bacelar
date: 04-10-2022

First the Digital Twin sends a message to start running the Physical Twin. The digital twin code is a 
small feature that request last data from the measurement 'machine' of the database 'poc_db' and print
the data for the user. When the maximun number of workpieces is achived  than DT publish a MQTT payload 
sending a message to stop the physical system.
"""
#--- Importing libraries
from unittest import expectedFailure
import paho.mqtt.client as mqtt
import json
from influx import InfluxDB
import time

#--- Global variables
max_parts_list = [10,10] #number os maximun counting pieces for stations
condition = True #condition for while loop
DATABASE_IP = "http://127.0.0.1:8086" #localhost IP
DATABASE_NAME = "poc_db"
request_delay = 5 #seconds

#===============================================================
#--- Connect to the Client
client = mqtt.Client() #create a client object
client.connect("192.168.0.50",1883,60) #connect to the Broker
print("== Connected to the Broker ==")

#--- Connect to Database
db = InfluxDB(DATABASE_IP,precision='ms')
print("== Connected to the database at: ", DATABASE_IP, " ==")
#==============================================================

#--- Publish the payload to start the Digital Twin
payload = "start"
client.publish(topic = "STATUS", payload= json.dumps(payload))

try:
    while condition:
        #--- Extract data from Database
        temp = db.select_recent(DATABASE_NAME, 'machine_state')

        print("testing...")
        time.sleep(request_delay)


except:
    print("XXX Digital Twin killed XXX")
