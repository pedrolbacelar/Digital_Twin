#!/usr/bin/env python3
# so that script can be run from Brickman

from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random

"""
# motor test
motor_station_A = LargeMotor('outA')
motor_station_A.run_forever(speed_sp = -500)
sleep(2)
motor_station_A.stop(stop_action = "hold")

motor_station_C = LargeMotor('outC')
motor_station_C.run_forever(speed_sp = 500)
sleep(2)
motor_station_C.stop(stop_action = "hold")
sleep(3)

motor_station_A.run_forever(speed_sp = -500)
motor_station_C.run_forever(speed_sp = 500)
sleep(6)
motor_station_A.stop(stop_action = "hold")
motor_station_C.stop(stop_action = "hold")

print("Conveyor test Done!")

# pusher test (negative speed for push, positive speed for pull)
pusher_D = MediumMotor('outD')
pusher_D.run_forever(speed_sp=-200)
sleep(1)
pusher_D.stop(stop_action='coast')

sleep(2)

pusher_D.run_forever(speed_sp=200)
sleep(1)
pusher_D.stop(stop_action='coast')

print("Pusher testing executed")
"""

# declaring optical sensors
station_sensor=ColorSensor(INPUT_1)
station_sensor.mode='COL-COLOR'
conveyor_sensor=ColorSensor(INPUT_2)
conveyor_sensor.mode='COL-COLOR'
blocking_sensor=ColorSensor(INPUT_3)
blocking_sensor.mode='COL-COLOR'
colors=('unknown','black','blue','green','yellow','red','white''brown')

# declaring & initiating conveyors and the pusher
motor_station_A = LargeMotor('outA')
motor_station_C = LargeMotor('outC')
motor_station_A.run_forever(speed_sp = -500) # Queue_conveyor on
pusher_D = MediumMotor('outD')
pusher_D.run_forever(speed_sp=-200) # pusher is engaged and blocks the part from entering the station
sleep(1)
pusher_D.stop(stop_action='hold')

# initiating simulation
T_start = time.time() # time of simulation start
print ("simulation started at ",datetime.now())
sim_length=1000000 # very big number! how to determine?
i=0
i_part=0

while i < sim_length
  color_st_sensor=colors[station_sensor.value()]
  color_conv_sensor=colors[conveyor_sensor.value()]
  if (color_st_sensor == "black") and (color_conv_sensor == "red"):
    print("part in the buffer. Arrival time is ", datetime.now())
    i_part=i_part+1
    motor_station_C.run_forever(speed_sp = 500) # Station_conveyor on
    pusher_D.run_forever(speed_sp=200)
    sleep(1)
    pusher_D.stop(stop_action='hold')
    sleep(2)
    pusher_D.run_forever(speed_sp=-200)
    sleep(1)
    pusher_D.stop(stop_action='hold')
    sleep(4)
    motor_station_C.stop(stop_action = "hold") # station conveyor stops after 4 seconds
  i=i+0.00000001
  
  if i_part>=1:
    print("simulation performed for 1 part")
    break
  
  # if simulation time is too long, program breaks after 2 minutes
  if (time.time()-T_start)>=120: # datetime format?
    motor_station_A.stop(stop_action = "hold")
    motor_station_C.stop(stop_action = "hold")
    pusher_D.run_forever(speed_sp=200)
    sleep(1)
    pusher_D.stop(stop_action='coast')
    print("simulation breaked after 2 minutes")
    break
    

motor_station_A.stop(stop_action = "hold")
motor_station_C.stop(stop_action = "hold")
print("simulation stopped at ", datetime.now())








