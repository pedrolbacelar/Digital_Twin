from time import sleep
from datetime import datetime
import time
import paho.mqtt.client as mqtt
import json

message_flag = '"idle"'


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic="STATUS")
    

def on_message(client, userdata, msg):
    # define global variables
    #print(msg.payload) 
    global message_flag
    print(str(msg.payload.decode("utf-8")))     # to print the message string
    message_flag = (msg.payload.decode())


# client connect
client = mqtt.Client()
client.connect("192.168.0.50",1883,60) # change ip address if required

client.on_connect = on_connect
client.on_message = on_message
client.loop_start()

while True:

    if message_flag == '"idle"':
        print("idle")
        time.sleep(2)

    elif message_flag == '"start"':
        print("STARTED")

        while True:
            if message_flag == '"stop"':
                print("STOPPED")
                break
