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

# db = InfluxDBClient(host='localhost', port=8086)
# db.switch_database('lego')



# temp = db.query("SELECT number FROM ArUco_N ORDER BY DESC LIMIT 3",epoch='s')                   

# print(temp)

# number_in = max([row[1] for row in temp.raw['series'][0]['values']]) # check hard coding