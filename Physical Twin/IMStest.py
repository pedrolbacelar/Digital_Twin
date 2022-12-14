#!/usr/bin/env python3

import sys
sys.path.append("/home/robot/Lib/site-packages/paho.mqtt.python/src/")

from ev3dev.ev3 import *
from time import sleep
from datetime import datetime
import time
import random
import json
import traceback
import paho.mqtt.client as mqtt

############################################################################
# MQTT RELATED
############################################################################

def on_connect(client, userdata, flags, rc):
  print("CONNECTED: result code "+str(rc))
  client.subscribe("topic/activity")
  client.subscribe("topic/states")
  client.subscribe("topic/buffers")
  client.subscribe("topic/operators")
  
  
def on_message(client, userdata, msg):

  #print("message received")
          
  global start
  global cond_while
  global op
  global op_pos
  global buffer_levels

  if msg.payload.decode() == "stop":
  
    print("STOPPING AS REQUESTED")
    cond_while = False
    
  if msg.payload.decode() == "start":
  
    print("STARTING!")
    start = True
    
    
  # UPDATE MY KNOWLEDGE ABOUT OPERATORS POSITION
  if msg.topic == "topic/operators":
    
    op = json.loads(msg.payload.decode())
    op_pos[ op['station'] -1 ] = op['operator']
      
  # UPDATE MY KNOWLEDGE ABOUT BUFFER LEVELS
  if msg.topic == "topic/buffers":
    
    bl = json.loads(msg.payload.decode())
    buffer_levels[bl["station"]-1] = bl["buffer"]

############################################################################
# GENERAL (NOT REPEATED AFTER EXCEPTIONS)
############################################################################

Sound.set_volume(100)
btn = Button()

Leds.all_off()
sleep(0.5)
Leds.set_color(Leds.LEFT, Leds.GREEN)
Leds.set_color(Leds.RIGHT, Leds.GREEN)
trials = 0 # NUMERO DI VOLTE CHE PROVO A FAR GIRARE IL CODICE

cond_while = True
start = False

try:

  while cond_while:  # NOTE, can also be interrupted by CTRL+C (raises KeiboardInterrupt)
    
    with open('ims_config.json', 'r') as f:
      json_str = f.read()
      ims_config = json.loads(json_str)
    
    ############################################################################
    # MQTT RELATED
    ############################################################################
    
    client = mqtt.Client()
    client.connect("192.168.0.104",1883,60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()
    
    ############################################################################
    # USER DEFINED PARAMETERS
    ############################################################################
    
    Product_A = ims_config['Product_A']   # Types of Product definition
    station = ims_config['station'] # STATION NUMBER
    next_station = ims_config['next_station'] # FOLLOWING STATION (FOR BLOCKING!)
    failure_prob = ims_config['failure_prob'] # FAILURE PROBABILITY
    
    # MOTORS SPEED
    conveyor_speed = ims_config['conveyor_speed']
    pusher_speed = ims_config['pusher_speed']
    station_speed = ims_config['station_speed']
    
    # PUSHER POSITIONS
    pos_wait = ims_config['pos_wait']
    pos_pass = ims_config['pos_pass']
    pos_push = ims_config['pos_push']
    pos_init = 0
    
    # WAITING TIMES
    pusher_pass_time = ims_config['pusher_pass_time']
    unload_time = ims_config['unload_time']
    station_timeout = ims_config['station_timeout']
    
    # PROCESSING AND FAILURE TIMES DISTRIBUTIONS
    w_distribution_type = ims_config['w_distribution_type']
    f_distribution_type = ims_config['f_distribution_type']
    
    w_distribution_par = ims_config['w_distribution_par']
    f_distribution_par = ims_config['f_distribution_par']
    
    Tw_Amin = ims_config['w_minimum_time'] # minimum processing time 
    Tf_Amin = ims_config['f_minimum_time'] # minimum failure time
    
    # RANDOM NUMBER GENERATION 
    seed = ims_config['seed']
    
    # TIMEOUTS
    timeout_restart = ims_config['timeout_restart']
    
    # REFRESH INTERVALS
    refresh_main = ims_config['refresh_main'] # MAIN PROGRAM REFRESH INTERVAL (STANDARD IS 0.1 s)
    refresh_support = ims_config['refresh_support'] # SUPPORT OPERATIONS REFRESH INTERVAL (STANDARD IS 1 s)
    
    # PART SEEN THRESHOLDS (COL-REFLECT MODE)
    threshold_low = ims_config['threshold_low'] # DEFAULT 10
    threshold_high = ims_config['threshold_high']  # DEFAULT 20
    
    # MAX SAMPLES FOR BLOCKING (DEFAULT 10)
    max_samples_blocking = ims_config['max_samples_blocking']
    
    
    ############################################################################
    # INITIALIZATION EV3
    ############################################################################

    motor_conveyor = LargeMotor('outA')
    motor_block = MediumMotor('outD')
    motor_station = LargeMotor('outC')
    
    conveyor_opticalsensor = ColorSensor(INPUT_2)
    conveyor_opticalsensor.mode = 'COL-REFLECT'
    
    station_opticalsensor = ColorSensor(INPUT_1)
    station_opticalsensor.mode = 'COL-REFLECT'
    
    blocking_opticalsensor = ColorSensor(INPUT_3)
    blocking_opticalsensor.mode = 'COL-COLOR'
    
    motor_block.stop_action = 'hold'
    motor_station.stop_action = 'coast'
    motor_conveyor.stop_action = 'coast'

    btn = Button()
    colors = ('unknown', 'black', 'blue', 'green', 'yellow', 'red', 'white', 'brown')
    
    ############################################################################
    # INITIALIZATION 4 CODE
    ############################################################################
    
    random.seed(seed)
    
    # Performance Initialization
    number_Product_A = 0
    in_p = 0
    out_p = 0
    workingA = 0 # processing time
    
    # OPERATORS POSITION INIT (ALL OPS ARE AVAILABLE)
    op_pos = [1, 1, 1, 1, 1, 1] # operators are present in all stations
    
    # BUFFER LEVELS (ALL BUFFERS ARE NOT FULL)
    buffer_levels = ["NF","NF","NF","NF","NF","NF"]     

    
    ############################################################################
    # MAIN
    ############################################################################
    
    Leds.set_color(Leds.LEFT, Leds.GREEN)
    Leds.set_color(Leds.RIGHT, Leds.GREEN)
    motor_block.reset()
    
    # publish idle state
    print('IDLE')
    a = {"activity" : station, "state" : 1}
    data_out = json.dumps(a, indent = 4)
    client.publish("topic/states", data_out)
    
    
    # start conveyor in opposite direction (so to free up pieces in front of charger)
    motor_conveyor.run_forever(speed_sp = -conveyor_speed)
    motor_station.run_forever(speed_sp=-station_speed)
    sleep(refresh_support/2)
    motor_conveyor.stop()
    motor_station.stop()
    # set pusher in waiting position
    motor_block.run_to_abs_pos(position_sp = pos_wait, speed_sp=pusher_speed)
    
    
    # wait for start signal:
    while not start:
      sleep(refresh_support)
      print("WAITING FOR START SIGNAL")

    motor_conveyor.run_forever(speed_sp = conveyor_speed) # start conveyor in NOMINAL SPEED
    
    try:
      while cond_while:
            
          sleep(refresh_main)
          
          #print(op_pos)
          #print(buffer_levels)
      		
          color_stat_available = station_opticalsensor.value()
          color_conv_entering = conveyor_opticalsensor.value()
          color_stat_ent = 'unknown'
          
      
          if color_stat_available < threshold_low  and color_conv_entering > threshold_high:
          
              print('PRODUCT AVAILABLE')
              in_p = in_p + 1
              
              a = {"activity" : station, "id" : in_p, "ts" : time.time(), "tag" : "s" }
              data_out = json.dumps(a, indent = 4)
              client.publish("topic/activity", data_out)
              
              #PUBLISH WORKING STATE
              a = {"activity" : station, "state" : 0}
              data_out = json.dumps(a, indent = 4)
              client.publish("topic/states", data_out)
      
              # A piece has been detected, hence we remove the block
              motor_block.run_to_abs_pos(position_sp = pos_pass, speed_sp = pusher_speed)
              sleep(pusher_pass_time)
              motor_block.run_to_abs_pos(position_sp= pos_push, speed_sp=pusher_speed) # Now, we close the block, in order to avoid the entering of too many pieces into the station
              
              motor_station.run_forever(speed_sp=station_speed)  # start station motor
              sleep(pusher_pass_time)
              motor_block.run_to_abs_pos(position_sp= pos_wait, speed_sp = pusher_speed)  # closing PUSHER
              
              #CHECK WHEN PIECE IS ENTERED
              T_check_input = time.time() # serve per timeout
              Entered = False
              Timeout = False
              
              while not Entered:
              
                  sleep(refresh_main) 
                  color_stat_ent = station_opticalsensor.value()
                  #print("STATION: "+ str(color_stat_ent))
                  
                  if color_stat_ent > threshold_high:
                      Entered = True
                      
                  elif (time.time() - T_check_input) > station_timeout:
                      Entered = True
                      Timeout = True
                      in_p = in_p - 1
      
              motor_station.stop()  # piece is entered into the station
              
              if not Timeout:
                  
                  print('Product is being worked by the Station ')
                  
                  number_Product_A = number_Product_A + 1
                  
                  print('N: ', number_Product_A)
                  
                  #Decide time (depending on dist type)
                  if w_distribution_type == 'triangular' or w_distribution_type == 'Triangular':
                    Tw_Astoc = random.triangular(w_distribution_par[0], w_distribution_par[1], w_distribution_par[2])  # random.triangular(low, high, mode)
                    
                  elif w_distribution_type == 'weibull' or w_distribution_type == 'Weibull':
                    Tw_Astoc = random.weibullvariate(w_distribution_par[0], w_distribution_par[1])  
                  
                  elif w_distribution_type == 'uniform' or w_distribution_type == 'Uniform':
                    Tw_Astoc = random.uniform(w_distribution_par[0], w_distribution_par[1]) 
                  
                  elif w_distribution_type == 'deterministic' or w_distribution_type == 'Deterministic':
                    Tw_Astoc = w_distribution_par 
                    
                  elif w_distribution_type == 'normal' or w_distribution_type == 'Normal':
                    Tw_Astoc = random.normalvariate(w_distribution_par[0], w_distribution_par[1]) 
                  
                  elif w_distribution_type == 'exponential' or w_distribution_type == 'Exponential':
                    Tw_Astoc = random.expovariate(w_distribution_par)
                  
                  
                  if random.random() <= (1- failure_prob):   # WORKING STATE
                  
                    print('WORKING')
                    workingA = max(Tw_Amin, Tw_Astoc)
                    sleep(workingA)  # Operation time assignment of Product A
                  
                  else: # FAILURE state
                    
                    Sound.speak('FAILURE!').wait()
                    Leds.set_color(Leds.LEFT, Leds.RED)
                    Leds.set_color(Leds.RIGHT, Leds.RED)
                    print('FAILURE')
                    
                    #publish failure state
                    a = {"activity" : station, "state" : 2}
                    data_out = json.dumps(a, indent = 4)
                    client.publish("topic/states", data_out)
                    
                    
                    # WAIT FOR OPERATOR!
                    print("WAITING FOR OPERATOR!")
                    
                    while op_pos[station - 1] == False:
                      
                      sleep(refresh_main)    
                      
                    print("OPERATOR ARRIVED!")           
                                         
                    #Decide failure time (depending on dist type)
                    if f_distribution_type == 'triangular' or f_distribution_type == 'Triangular':
                      Tf_Astoc = random.triangular(f_distribution_par[0], f_distribution_par[1], f_distribution_par[2])  # random.triangular(low, high, mode)
                    
                    elif f_distribution_type == 'weibull' or f_distribution_type == 'Weibull':
                      Tf_Astoc = random.weibullvariate(f_distribution_par[0], f_distribution_par[1])  
                  
                    elif f_distribution_type == 'uniform' or f_distribution_type == 'Uniform':
                      Tf_Astoc = random.uniform(f_distribution_par[0], f_distribution_par[1]) 
                  
                    elif f_distribution_type == 'deterministic' or f_distribution_type == 'Deterministic':
                      Tf_Astoc = f_distribution_par 
                      
                    elif f_distribution_type == 'normal' or f_distribution_type == 'Normal':
                      Tf_Astoc = random.normalvariate(f_distribution_par[0], f_distribution_par[1])   
                      
                    elif f_distribution_type == 'exponential' or f_distribution_type == 'Exponential':
                      Tf_Astoc = random.expovariate(f_distribution_par)                             
                                                   
            				#total FAILURE + WORKING TIME
                    workingA = Tw_Astoc + max(Tf_Amin, Tf_Astoc)
                    
                    sleep(workingA)  # Operation time assignment of Product A
            				
            				#exit FAILURE state
                    Sound.speak('REPAIRED!').wait()
                    Leds.set_color(Leds.LEFT, Leds.GREEN)
                    Leds.set_color(Leds.RIGHT, Leds.GREEN)
    
          
                  #publish idle state
                  a = {"activity" : station, "state" : 1}
                  data_out = json.dumps(a, indent = 4)
                  client.publish("topic/states", data_out)
                  
                  a = {"activity" : station, "id" : in_p, "ts" : time.time() , "tag" : "f" }
                  data_out = json.dumps(a, indent = 4)
                  client.publish("topic/activity", data_out)
          
                  # Verify if the Bocking Condition happens
                  color_block = colors[blocking_opticalsensor.value()]
                  
                  if color_block == Product_A:
                      Blocked = True
                      set = False
                      last_seen = []
                      
                      #publish buffer level next_station
                      a = {"station" : next_station, "buffer": "F"}
                      data_out = json.dumps(a, indent = 4)
                      client.publish("topic/buffers", data_out)
                      
                      while Blocked:
                          
                          count = 0
                          i = 0
          
                          while not set:
                            #SET BLOCKING LEDS ----------------- (only once!)
                            Leds.set_color(Leds.LEFT, Leds.RED)
                            Leds.set_color(Leds.RIGHT, Leds.GREEN)
                            # -----------------------------------
                            print("BLOCKED")
                            set = True
                          
                          
                          while i < max_samples_blocking:
                            color_block = colors[blocking_opticalsensor.value()]
                            last_seen.append(color_block)
                            sleep(refresh_main)
                            i = i + 1
                            
                          for element in last_seen[-9:]:
                            #print(element)
                            if element == Product_A:
                              count = count + 1
                          #print(count)
                          
                          if count > 1:
                              Blocked = True
          
                          else:
                              Blocked = False
                              #SET STABLE LEDS -----------------
                              Leds.set_color(Leds.LEFT, Leds.GREEN)
                              Leds.set_color(Leds.RIGHT, Leds.GREEN)
                              # -----------------------------------
          
                      # publish buffer level 5
                      a = {"station" : next_station, "buffer": "NF"}
                      data_out = json.dumps(a, indent = 4)
                      client.publish("topic/buffers", data_out)
                      
                  # UNLOADING
                  motor_station.run_forever(speed_sp = station_speed)
                  sleep(unload_time)
                  out_p = out_p + 1
                  motor_station.stop()
                  
                  # PUBLISH IDLE STATE
                  print("IDLE")
                  a = {"activity" : station, "state" : 1}
                  data_out = json.dumps(a, indent = 4)
                  client.publish("topic/states", data_out)
      
            
    ############################################################################
    # EXCEPTIONS
    ############################################################################
    
    except Exception as e:
    
      print(e)
    
      a = {"activity" : station, "state" : 1}
      data_out = json.dumps(a, indent = 4)
      client.publish("topic/states", data_out)
      
      print('EXCEPTION STATION '+str(station)+': STOPPING MOTORS')
      
      #stop all motors
      motor_block.run_to_abs_pos(position_sp = pos_init, speed_sp=pusher_speed)
      motor_conveyor.stop(stop_action = 'coast')
      motor_station.stop(stop_action = 'coast')
      
      sleep(refresh_support)
      
      # set leds to yellow
      Leds.set_color(Leds.LEFT, Leds.YELLOW)
      Leds.set_color(Leds.RIGHT, Leds.YELLOW)
      
      # timeout restart
      t = timeout_restart 
      while t > 0:
        print('EXCEPTION STATION '+str(station)+':STARTING OVER IN ', t, ' SECONDS')
        sleep(1) # HERE IS OK 1
        t = t-1
        
      sleep(refresh_support)
      
      Leds.all_off()
      sleep(refresh_main)
      Leds.set_color(Leds.LEFT, Leds.GREEN)
      Leds.set_color(Leds.RIGHT, Leds.GREEN)
          
      trials = trials + 1
    
    # AFTER MAIN CODE
    #stop all motors
    motor_block.run_to_abs_pos(position_sp = pos_pass, speed_sp=pusher_speed)
    motor_conveyor.stop(stop_action = 'coast')
    motor_station.stop(stop_action = 'coast')
    
    sleep(refresh_support)
    
    
except KeyboardInterrupt as f:

  print('INTERRUPTED FROM PC')

  #publish idle state
  a = {"activity" : station, "state" : 1}
  data_out = json.dumps(a, indent = 4)
  client.publish("topic/states", data_out)

  #Set leds to yellow
  Leds.all_off()
  sleep(0.1)
  Leds.set_color(Leds.LEFT, Leds.YELLOW)
  Leds.set_color(Leds.RIGHT, Leds.YELLOW)
    
  #stop all motors
  motor_block.run_to_abs_pos(position_sp = pos_init, speed_sp=pusher_speed)
  motor_conveyor.stop(stop_action = 'coast')
  motor_station.stop(stop_action = 'coast')
  
  client.loop_stop()