#!/usr/bin/env python3
# so that script can be run from Brickman

"""
--- Code for testing the conveyor and station motor speed ---
Testing logic
    1. check conveyor motor
    2. check station motor
    3. check pusher motor
    4. run all three together

"""

#--- Import 
from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random

conveyor_motor_speed=500
station_motor_speed=500
pusher_motor_speed=200

try:
    #Run conveyor 
    motor_station_A = LargeMotor('outA')
    # speed for conveyor_motor negated for motion towards the queue
    motor_station_A.run_forever(speed_sp = -conveyor_motor_speed) 
    sleep(2)
    motor_station_A.stop(stop_action = 'coast')

    sleep(2)

    #Run Station 
    motor_station_C = LargeMotor('outC')
    # speed for station_motor is positive for motion towards the station
    motor_station_C.run_forever(speed_sp = station_motor_speed)
    sleep(2)
    motor_station_C.stop(stop_action = 'coast')

    sleep(2)

    # pusher test (negative speed for push, positive speed for pull)
    pusher_D = MediumMotor('outD')
    pusher_D.run_forever(speed_sp=-pusher_motor_speed)
    sleep(1)
    pusher_D.stop(stop_action='coast')
    sleep(2)
    pusher_D.run_forever(speed_sp=pusher_motor_speed)
    sleep(1)
    pusher_D.stop(stop_action='coast')
    print("=== Pusher testing executed ===")

    sleep(2)

    #Run all three
    motor_station_A.run_forever(speed_sp = -conveyor_motor_speed)
    motor_station_C.run_forever(speed_sp = station_motor_speed)
    pusher_D.run_forever(speed_sp=-pusher_motor_speed)
    sleep(1)
    pusher_D.stop(stop_action='coast')
    sleep(6)
    pusher_D.run_forever(speed_sp=pusher_motor_speed)
    sleep(1)
    pusher_D.stop(stop_action='coast')
    motor_station_A.stop(stop_action = 'coast')
    motor_station_C.stop(stop_action = 'coast')
    print("=== All three motors tested succesfully! ===")

# emergency stop <ctrl+c>
except KeyboardInterrupt as f:

  #stop all coveyors and pusher motors
  motor_conveyor.stop(stop_action = 'coast')
  motor_station.stop(stop_action = 'coast')
  pusher_D.stop(stop_action='coast')

  print('-----INTERRUPTED FROM PC-----')
