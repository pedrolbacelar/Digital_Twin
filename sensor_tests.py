
"""
--- Code to test optical sensor working ---
Code prints the value collected by the sensor
ev3dev library is already installe din ev3 lego machine
"""

#--- Import 
from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random

#--- Global
delta_max = 60 #seconds
interval = 1 #seconds


#--- declaring optical sensors
station_sensor=ColorSensor(INPUT_1)
station_sensor.mode='COL-COLOR'
conveyor_sensor=ColorSensor(INPUT_2)
conveyor_sensor.mode='COL-COLOR'
blocking_sensor=ColorSensor(INPUT_3)
blocking_sensor.mode='COL-COLOR'
colors=('unknown','black','blue','green','yellow','red','white','brown')

#-- initial time
t_ini = time.time()

while True:
    t_now = time.time()
    delta = t_now - t_ini
    if delta > delta_max:
        break  # to break the code automatically if there is no input from the sensor
    else:
        # printing the acquired sensor values
        print("=============")
        print("station_sensor = ", station_sensor.value())
        print("conveyor_sensor = ", conveyor_sensor.value())
        print("blocking_sensor = ", blocking_sensor.value())
        print("=============")
        
        time.sleep(interval)