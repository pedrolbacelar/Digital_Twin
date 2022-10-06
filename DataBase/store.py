""" 
store.py
created by: Pedro Bacelar
date: 04-10-2022

Code receive data from the physical twin using MQTT and store the data on the influx database
"""
import paho.mqtt.client as mqtt
import json
from influx import InfluxDB
import time

#--- Global Variables
DATABASE_IP = "http://127.0.0.1:8086" #localhost IP
DATABASE_NAME = "poc_db"
BROKER_IP = "192.168.0.50" #Factory computer
PORT = 1883 #default

#--- connect to influx (in this case the local host)
db = InfluxDB(DATABASE_IP,precision='ms')
print("== Connected to the database at: ", DATABASE_IP)

#--- Define MQTT functions
def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code "+str(rc))
    client.subscribe("OUTPUT")

def on_message(client, userdata, msg):

    if msg.topic == "OUTPUT":
        json_value = json.loads(msg.payload.decode())  #convert json to dictionary
        json_value['ts'] = time.time() #change timestamp!

        print("= New payload received on -OUTPUT- =")
        print("payload = ")
        print(json_value)

        #-- Write the message into the database
        db.write(DATABASE_NAME,'machine', fields={"counter":json_value['counter']}, tags={"id":json_value['id']})

        print("payload written to Database")
try: 
    #--- Connect to the Client
    client = mqtt.Client() #create a client object
    client.connect("192.168.0.50",1883,60) #connect to the Broker
    print("== Connected to the Broker ==")

    #-- Declare MQTT functions
    client.on_connect = on_connect
    client.on_message = on_message

    #-- Start comunication loop
    client.loop_start()
    print("== Client loop started ==")

    #-- Infinite loop to keep connected
    condition = True
    while condition:
        time.sleep(1)

    #-- close loop and disconnect    
    client.loop_stop()    
    client.disconnect()

except:
    client.loop_stop()    
    client.disconnect()
    print("Client desconnected successful!")