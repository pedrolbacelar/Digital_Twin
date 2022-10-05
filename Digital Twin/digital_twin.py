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
max_parts_list = [10,5] #number os maximun counting pieces for stations
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

#--- Write dumb data into the database
# db.write(DATABASE_NAME,'machine', fields={"counter":10, "message": "14:26"}, tags={"id":1})



# try:
while condition:
    print("=================================================")

    recent_raw_data = db.select_recent(DATABASE_NAME, 'machine', relative_time= "5m")

    #--- Extract data from Database
    tags = db.show_tags(DATABASE_NAME, 'machine')
    fields = db.show_fields(DATABASE_NAME, 'machine')

    #--- Show tags and fields
    print("Show Tags: ", tags)
    print("Show Fields: ", fields)

    #--- Show recent data
    print()
    print("--")
    print("Raw Data stored in the last minute: ")
    print(recent_raw_data)
    print("--")
    print()


    #--- Show the last Value
    machine_id = int(recent_raw_data['results'][0]['series'][0]['values'][-1][2])
    machine_counter = recent_raw_data['results'][0]['series'][0]['values'][-1][1]

    print("Last Value from:")
    print("     Machine ID: ", machine_id)
    print("     Machine Counter: ", machine_counter)

    #--- Verify stop conditions
    for i in range(len(max_parts_list)): #loop to check all machines
        if machine_counter >= max_parts_list[i] and (machine_id) == (i + 1):

            print("---")
            print("Machine ID [", machine_id,"] counter exceeded the maximun: ", max_parts_list[machine_id - 1])

            #--- Payload message to stop (with assigned machine)
            payload = {
                "message" : "stop",
                "id" : machine_id,
            }     

            #--- Publish the new status
            client.publish(topic = "STATUS", payload= json.dumps(payload))
            print("Stop message sent to the Physical Twin")
            print("---")



    print("=================================================")
    time.sleep(request_delay)

# except:
#     print("XXX Digital Twin killed XXX")
