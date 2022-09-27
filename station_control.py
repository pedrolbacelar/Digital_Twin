#--- Import 
from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random

#--- declaring optical sensors
station_sensor=ColorSensor(INPUT_1)
station_sensor.mode='COL-COLOR'
conveyor_sensor=ColorSensor(INPUT_2)
conveyor_sensor.mode='COL-COLOR'
blocking_sensor=ColorSensor(INPUT_3)
blocking_sensor.mode='COL-COLOR'
colors=('unknown','black','blue','green','yellow','red','white''brown')

#--- declaring & initiating conveyors and the pusher
motor_station_A = LargeMotor('outA')
motor_station_C = LargeMotor('outC')
#Conveyor runs
motor_station_A.run_forever(speed_sp = -500)
# pusher is engaged and blocks the part from entering the station
pusher_D = MediumMotor('outD')
pusher_D.run_forever(speed_sp=-200) 
sleep(1)
pusher_D.stop(stop_action='hold')