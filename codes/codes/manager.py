# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 16:37:07 2019

@author: giova
"""

#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import pandas as pd
#import datetime
import time
from time import sleep
import numpy as np
from influx import InfluxDB

# connect to influx
db = InfluxDB('http://192.168.0.50:8086',precision='ms')
NOME_DATABASE = "lego"

# This is the Subscriber

activity_log = []
states_log = []

count = 0
start_time = 0
th = 0

b3 = 1
b4 = 1
b5 = 0

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("topic/activity")
  client.subscribe("topic/states")
  client.subscribe("topic/buffers")
  client.subscribe("topic/operators")
  

def on_message(client, userdata, msg):
    
    global start_time
    global count
    global th
    global b3
    global b4
    global b5
    global th
    
    if msg.payload.decode() == "start" or msg.payload.decode() == "stop":
        pass
    
    elif msg.topic == "topic/activity":
        
        # print(msg.payload) 
        # print(msg.payload.decode())
        # print(json.loads(msg.payload))
        # print(msg.payload.decode())
        
        json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
          
        # print("activity",json_value['activity'])
        # print("id",json_value['id'])
        # print("ts",json_value['ts'])
        # print("tag",json_value['tag'])    
        #  json_value['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #change timestamp!
        json_value['ts'] = time.time() #change timestamp!
        activity_log.append(json_value)
        #    influx write senza timestamp
        db.write(NOME_DATABASE,'eventlog', fields={"id":json_value['id'],"type":json_value['tag']}, tags={"activity":json_value['activity']})
    
#        evaluate THROUGHPUT
        if json_value['tag'] =='f' and json_value['activity'] == 1:
            
            try:
                thput = 1/(time.time() - start_time) 
                db.write(NOME_DATABASE,'throughput', fields={"th": thput}, tags={"activity":6})
                start_time = time.time()
            except: 
                pass
            
#            if len(th)<5:
#                th.append(time.time())
#            
#            if len(th)>=5:
#                th = th[1:] +[time.time()] 
#                thput = len(th)/(th[-1] - th[0])
#            
##                thput = count / (time.time() - start_time)
#    #            print("THROUGHPUT: "+str(th))
#                db.write(NOME_DATABASE,'throughput', fields={"th": thput}, tags={"activity":6})

    elif msg.topic == "topic/states":
        
        json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python

#        print("activity",json_value['activity'])
#        print("state",json_value['state'])
        json_value['ts'] = time.time() #change timestamp!
        
        states_log.append(json_value)

#        influx write        
        db.write(NOME_DATABASE,'machine_state', fields={"activity":json_value['activity'], "state":json_value['state']})
    
    
    elif msg.topic == "topic/operators":
        
#        print('message received')
        
        json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
#        print("BUFFER MESSAGE:"+ str(json_value))
#        MAPPING VALUES FOR DASHBOARD

        if json_value['operator'] == True:
            db.write(NOME_DATABASE,'operators', fields={"pos": json_value['station'] })
    
    
    elif msg.topic == "topic/buffers":
        
        json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
#        print("BUFFER MESSAGE:"+ str(json_value))
#        MAPPING VALUES FOR DASHBOARD

        
        if json_value['station'] == 3:
        
            if json_value['buffer'] == 'L':
                b3 = 1
                
            if json_value['buffer'] == 'M':
                b3 = 2
                
            if json_value['buffer'] == 'H':
                b3 = 3
                
        if json_value['station'] == 4:
            
            if json_value['buffer'] == 'L':
                b4 = 1
                
            if json_value['buffer'] == 'M':
                b4 = 2
                
            if json_value['buffer'] == 'H':
                b4 = 3
        
        if json_value['station'] == 5:
            
            if json_value['buffer'] == 'NF':
                b5 = 0
                
            if json_value['buffer'] == 'F':
                b5 = 4
                       
#        print("3: " + json_value['3'] + "4: "+str(json_value['4']))
#        print("3: " + str(b3)+ "4: "+str(b4))

#        states_log.append(json_value)

#        influx write        
        db.write(NOME_DATABASE,'buffers', fields={"b3": b3, "b4": b4, "b5": b5})
    
    if msg.payload.decode() == "disc":
        
        print("Disconnecting...")
        client.disconnect()
        
    elif msg.payload.decode() == "start":
        print("STARTED!")
        start_time  = time.time()
    
client = mqtt.Client()
client.connect("192.168.0.50",1883,60)

client.on_connect = on_connect
client.on_message = on_message

th = []

client.loop_start()


condition = True

while condition:
    sleep(1)
    
client.loop_stop()    
client.disconnect()


#DEBUGGING
#json_value = {"time": 123}
#json_value['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#activity_log.append(json_value)

df = pd.DataFrame(activity_log)       # pass to pandas df

for a in df.activity.unique().tolist():

    # processing times
    pt = np.array([])
    # tutti gli id che hanno fatto questa attivita
    for i in df.id.unique().tolist():
#        print(i)
        try:
            pt = np.append(pt, (df[(df.activity == a) & (df.id == i) & (df.tag == 'f')].ts.values  - df[(df.activity == a) & (df.id == i) & (df.tag == 's')].ts.values).tolist()  )
        except:
            continue    
    
    np.savetxt('processing'+str(a)+'.txt', pt, delimiter='\n', fmt='%f')
    
    #arrival times:
    # tutti gli id che hanno fatto questa attivita
    #for i in df.id.unique().tolist():
    
    at = np.diff(df[ (df.activity == a) & (df.tag == 'f')].ts)
    np.savetxt('arrivals'+str(a)+'.txt', at, delimiter='\n', fmt='%f')


df = df.sort_values(by ='ts')
df.to_csv(r'log.csv')


# PARTE SU EV3
#activity_log.append({"activity" : 6, "id" : 1, "ts" : 6, "tag" : "f" })
#
#data_out = json.dumps(a, indent = 4)
#client.publish("topic/test", data_out)