#!/usr/bin/env python3
# so that script can be run from Brickman

from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random


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
