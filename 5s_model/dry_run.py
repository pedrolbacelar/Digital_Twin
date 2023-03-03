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

conveyor_motor_speed=300
station_motor_speed=300
pusher_motor_speed=400

try:
  queue_sensor = ColorSensor(INPUT_2)
  queue_sensor.mode = 'COL-COLOR'
  
  motor_station_A = LargeMotor('outA')
  motor_station_C = LargeMotor('outC')
  pusher_D = MediumMotor('outD')
  
  motor_station_A.run_forever(speed_sp = -conveyor_motor_speed)
  motor_station_C.run_forever(speed_sp = -station_motor_speed)
  pusher_D.run_forever(speed_sp=-pusher_motor_speed)
  sleep(1)
  pusher_D.stop(stop_action='coast')
  
  print("==== Executing dry run. Press Ctrl + C to stop ====")
  
  while True:
    if queue_sensor.value() > 1:
      pusher_D.run_forever(speed_sp=pusher_motor_speed)
      sleep(1)
      pusher_D.stop(stop_action='coast')
      sleep(2)
      pusher_D.run_forever(speed_sp=-pusher_motor_speed)
      sleep(1)
      pusher_D.stop(stop_action='coast')
    sleep(4)

# emergency stop <ctrl+c>
except KeyboardInterrupt as f:

  #stop all coveyors and pusher motors
  motor_station_A.stop(stop_action = 'coast')
  motor_station_C.stop(stop_action = 'coast')
  pusher_D.run_forever(speed_sp=pusher_motor_speed)
  sleep(1)
  pusher_D.stop(stop_action='coast')

  print('-----INTERRUPTED FROM PC-----')
