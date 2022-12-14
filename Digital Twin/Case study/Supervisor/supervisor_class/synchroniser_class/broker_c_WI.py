# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 23:03:29 2021

@author: franc
"""
import paho.mqtt.client as mqtt

import json
import pandas as pd
import pickle

#import datetime
import time
import datetime
from time import sleep
import numpy as np

# ADDED to query
# from influx import InfluxDB
from influxdb import InfluxDBClient
from influxdb import DataFrameClient




class broker():

    def __init__(self,host,port,keepalive,DB_name=None):

        self.host=host
        self.port=port
        self.keepalive=keepalive
        self.client=mqtt.Client()
        self.DB_name=DB_name



    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("topic/activity")
        client.subscribe("topic/states")
        client.subscribe("topic/config")
        client.subscribe("disc")
        client.subscribe("start")




    # def on_message(self,client, userdata, msg):
    #
    #     #db = InfluxDB("http://"+str(self.host)+":" +str(self.port),precision='s')
    #     # db = InfluxDB('http://192.168.0.50:8086',precision='s')
    #
    #     global start_time
    #     global count
    #     global condition
    #
    #     #eventlog
    #
    #     if msg.topic == "topic/activity":
    #         json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
    #         print("ok")
    #         #    influx write senza timestamp
    #         db.write(self.DB_name,'eventlog', fields={"id":json_value['id'],"type":json_value['tag']}, tags={"activity":json_value['activity']})
    #
    #
    #
    #     #machine_states
    #
    #     if msg.topic == "topic/states":
    #
    #         json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
    #         json_value['ts'] = time.time() #change timestamp!
    # #        influx write
    #         db.write(self.DB_name,'machine_state', fields={"activity":json_value['activity'], "state":json_value['state']})
    #
    #
    #     if msg.topic =="disc":
    #         print("Disconnecting...")
    #         client.disconnect()
    #         condition = False
    #
    #     if msg.topic == "start":
    #         print("STARTED!")
    #
    #         start_time  = time.time()




    def active(self):

        self.client.connect(self.host,self.port,self.keepalive)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.loop_start()

    def feedback(self, config, topic):
        self.client.connect(self.host, self.port, self.keepalive)
        configJSON = json.dumps(config, indent=4)
        self.client.publish(topic, configJSON)









