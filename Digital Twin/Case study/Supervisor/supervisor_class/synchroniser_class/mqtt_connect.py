# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 18:38:20 2021

@author: franc
"""

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("topic/activity")
  client.subscribe("topic/states")
  client.subscribe("disc")
  client.subscribe("start")