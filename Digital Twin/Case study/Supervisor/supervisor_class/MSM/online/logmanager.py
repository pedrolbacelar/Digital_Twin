# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 15:43:28 2020

@author: giova
"""
from threading import Thread
import paho.mqtt.client as mqtt
import json

class LogManager(Thread):
    
    def __init__(self, name = 'LogManager', duration = None):
        Thread.__init__(self)
        self.name = name
        self.name = duration
        
    def stop(self):
        client.publish("disc", "topic/activity")
    
# This is the Subscriber
    def run(self):
        
        self.activity_log = []
        
        def on_connect(client, userdata, flags, rc):
          print("Connected with result code "+str(rc))
          client.subscribe("topic/activity")    
        
        def on_message(client, userdata, msg):
          if msg.payload.decode() == "disc":
            print("Disconnecting...")
            client.disconnect()
          else:
            json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
#            print("station",json_value['station'])
#            print("id",json_value['part_ID'])
#            print("time",json_value['time'])
#            print("activity",json_value['activity'])  
#            print(json_value)
#            a = json_value['activity'] 
#            json_value['activity'] = str(json_value['station']) + '-' + a
        #    json_value['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            json_value['time'] = time.time()
            self.activity_log.append(json_value)
            b = str(json_value['station']) +  '-' + json_value['activity'] + ',' +   str(json_value['part_ID']) + ',' + str(json_value['time']) 
#
            with open('log_new.csv', 'a') as file:
                file.write(b +'\n')
            
        
        client = mqtt.Client()
        client.connect("localhost",1883,60)
        
        client.on_connect = on_connect
        client.on_message = on_message
        
        client.loop_forever()