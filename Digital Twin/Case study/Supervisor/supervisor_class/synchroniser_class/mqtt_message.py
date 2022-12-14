# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 16:54:06 2021

@author: franc
"""
from influx import InfluxDB
import json

#TBN this function, acces to the broker and save messages to the Database chosen 




def on_message(client, userdata, msg):
    print("message arrive")
    
    global start_time
    global count
    
    global b3
    global b4
    global b5
   
    global condition   

    #eventlog
    
    if msg.topic == "topic/activity":
        json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
        print("ok")
        #    influx write senza timestamp
        db.write(NOME_DATABASE,'eventlog', fields={"id":json_value['id'],"type":json_value['tag']}, tags={"activity":json_value['activity']})
        
             
    
    #machine_states
    
    if msg.topic == "topic/states":
        
        json_value = json.loads(msg.payload.decode())  #conversione da stringa a dizionario python
        json_value['ts'] = time.time() #change timestamp!           
#        influx write        
        db.write(NOME_DATABASE,'machine_state', fields={"activity":json_value['activity'], "state":json_value['state']})
    
  
    if msg.topic =="disc":
        print("Disconnecting...")
        client.disconnect()
        condition = False
        
    if msg.topic == "start":
        print("STARTED!")
        
        start_time  = time.time()
