#!/usr/bin/env python3
# so that script can be run from Brickman

from concurrent.futures import process
from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random


#--- Global
delta_max = 90
part_max = 3

pusher_speed = 500
station_speed = 500
conveyor_speed = 500

pusher_time = 0.5
station_delay = 4

process_time = 5
unloading_time = 2

flag_done = False


# declaring optical sensors
station_sensor=ColorSensor(INPUT_1)
station_sensor.mode='COL-COLOR'
conveyor_sensor=ColorSensor(INPUT_2)
conveyor_sensor.mode='COL-COLOR'
blocking_sensor=ColorSensor(INPUT_3)
blocking_sensor.mode='COL-COLOR'
colors=['unknown','black','blue','green','yellow','red','white','brown']

# declaring & initiating conveyors and the pusher
motor_conveyor = LargeMotor('outA')
motor_station = LargeMotor('outC')
motor_conveyor.run_forever(speed_sp = -conveyor_speed) # Queue_conveyor on
pusher_D = MediumMotor('outD')
pusher_D.run_forever(speed_sp=-pusher_speed) # pusher is engaged and blocks the part from entering the station
sleep(pusher_time)
pusher_D.stop(stop_action='hold')

# initiating simulation
T_start = time.time() # time of simulation start
print ("simulation started at ",datetime.now())
sim_length=1000000 # very big number! how to determine?
i=0
i_part=0

#--- Functions
def Pusher_back():
    #--- Pusher: Coming back
    pusher_D.run_forever(speed_sp=pusher_speed)
    sleep(pusher_time)

    pusher_D.stop(stop_action='hold')
    sleep(pusher_time)

def Pusher_push():
    #--- Pusher: Go Ahead
    pusher_D.run_forever(speed_sp=-pusher_speed)
    sleep(pusher_time)
    pusher_D.stop(stop_action='hold')
    


try:
  while True:
    T_now = time.time()
    delta = T_now - T_start
    #--- get color of the sensors
    print("station_sensor = ", station_sensor.value())
    print("conveyor_sensor = ", conveyor_sensor.value())

    color_st_sensor = colors[station_sensor.value()]
    color_conv_sensor = colors[conveyor_sensor.value()]

    #--- Pusher
    if flag_done == True:
      if (color_st_sensor == "black" or color_st_sensor == "unknown") and ((color_conv_sensor != "black")):
        print("part in the buffer. Arrival time is ", datetime.now())
        i_part = i_part + 1

        #--- Station_conveyor on
        motor_station.run_forever(speed_sp = station_speed) 

        #--- Pusher: Coming back
        Pusher_back()

        #--- Pusher push
        Pusher_push()

        flag_done = False


    #--- Loading and Unloading
    if (colors[station_sensor.value()] == "red"): #something is on the station
      #-- Simulating Processing 
      motor_station.stop(stop_action = "hold") 
      sleep(process_time)

      #-- Simulating Unloading
      motor_station.run_forever(speed_sp = station_speed)
      sleep(unloading_time)
      motor_station.stop(stop_action = "hold") 

      flag_done = True



    
    
    if i_part> part_max:
      print("simulation performed for 1 part")

      break
    
    # if simulation time is too long, program breaks after 2 minutes
    if (delta > delta_max): # datetime format?
      print("==== Timeout ====")
      motor_conveyor.stop(stop_action = "hold")
      motor_station.stop(stop_action = "hold")
      pusher_D.run_forever(speed_sp=pusher_speed)
      sleep(pusher_time)
      pusher_D.stop(stop_action='coast')
      print("simulation breaked after 2 minutes")
      break
      

  motor_conveyor.stop(stop_action = "hold")
  motor_station.stop(stop_action = "hold")
  Pusher_back()

  print("simulation stopped at ", datetime.now())

except KeyboardInterrupt as f:

  print('INTERRUPTED FROM PC')

  #stop all motors
  motor_conveyor.stop(stop_action = "hold")
  motor_station.stop(stop_action = "hold")
  pusher_D.stop(stop_action='hold')









