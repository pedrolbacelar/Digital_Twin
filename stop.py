#!/usr/bin/env python3
# so that script can be run from Brickman

from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random

# declaring & initiating conveyors and the pusher
motor_station_A = LargeMotor('outA')
motor_station_C = LargeMotor('outC')
pusher_D = MediumMotor('outD')


motor_station_A.stop(stop_action = "hold")
motor_station_C.stop(stop_action = "hold")