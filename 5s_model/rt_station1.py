#!/usr/bin/env python3

#-- change st_num for each code depending on the machine_id.
#-- take care of conveyor, pusher and station motor directions.
#-- change branching policy for branching machines.
#-- you send the start message to initiate the whole system.
#-- The station sends machine_id, activity_type, queue_id to database by mqtt using trace topic
#-- Processing trace includes loading and unloading time inside the processing period.
#-- unloading time is considered to be as a part of tranportation time.
#-- expected mqtt from part_id: {"machine_id":"1","part_id":"12345"}
#-- expected mqtt from RCT-server: {"machine_id":"1","part_id":"12345","policy":"2"}
#-- trace mqtt published: {"machine_id" : "1", "activity_type":"start","queue_id":"1"}
#-- default dispatch policy is alternating. machine initiates with station 2.
#-- blocking condition: BAS
#-- failures are not included
#-- processing times are deterministic
#-- part is recieved is the updated part number and not the RFID Tag ID.

#--- import required packages
import paho.mqtt.client as mqtt
import json
import datetime
import time
from time import sleep
from ev3dev.ev3 import *
import random

################################
#--- Declaration and initiation
################################


st_num = "1"      #--- change st_num for each code depending on the machine_id
next_queue = "2"  #--- change next queue id if it is not a branching station # we start with 2. to change to 2, we initaite it as 3 for station 1
   


#--- declaring optical sensors
station_sensor=ColorSensor(INPUT_1)
station_sensor.mode='COL-REFLECT'
queue_sensor=ColorSensor(INPUT_2)
queue_sensor.mode='COL-REFLECT'
blocking_sensor_1=ColorSensor(INPUT_3)
blocking_sensor_1.mode='COL-REFLECT'
btn = Button()
Leds.set_color(Leds.LEFT, Leds.GREEN)
Leds.set_color(Leds.RIGHT, Leds.GREEN)
Sound.set_volume(100)

colors=('unknown','black','blue','green','yellow','red','white','brown')

#--- initializing station
pusher = MediumMotor('outD')
pusher.reset()
pos_neutral = 0
pusher_speed = 400


conveyor = LargeMotor('outA')
station = LargeMotor ('outC')

#--- declaring variables
conveyor_speed = 300
station_speed = 100
pusher_speed = 400
pos_neutral = 0
pos_extend = 180

#--- process time of station excluding the loading and unloading time
process_time = 2    # advised to have no less than 5s of gap between two parts in the downstream conveyor to not have problems with pusher.
standard_deviation = 2
process_distribution = 'norm'
failure_probability = 0.00000001 # percent
mttr = 4 # mean time to repair

manual_failure = False
system_status = "stop"
advice_list = dict()
station_status = "idle"
start_status = 0
stop_status = 0
advice_status = 0
current_station = next_queue  # replacing the next queue variable
current_part_id = "unknown part"
print("Station ",st_num," program Activated")


################################
#--- main functions
################################
def translate_message(message):
        """
        This function receives the message from the MQTT and translate it into a dictionary.
        """
        #--- Decode the message received from the MQTT
        message_decoded = str(message.payload.decode("utf-8"))

        #--- Replace ' to "
        message_replaced = message_decoded.replace("'", "\"")


        #--- Convert the message received in to a dictionary
        message_translated = json.loads(message_replaced)

        return message_translated
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #--- subscribe topics
    client.subscribe(topic = "system_status")
    client.subscribe(topic = "RCT_server")
    client.subscribe(topic = "part_id")
    client.subscribe(topic = "process_time")

def on_message(client, userdata, msg):
    # define global variables
    global system_status
    global start_status
    global stop_status
    global current_part_id
    global process_time
    # print(msg.payload)
    print(str(msg.payload.decode("utf-8")))     #-- to print the message string

    #--- start/stop of system
    if msg.topic == "system_status":
        message = str(msg.payload.decode("utf-8"))
        if message == "start":
            system_status = message
            start_status = 1
        if message == "stop":
            system_status = message
            stop_status = 1

    #--- RCT-server
    #--- payload expected: a. station_2 b. station_3
    if msg.topic == "RCT_server":
        message = translate_message(msg)
        if message["machine_id"] == st_num:    # we enter the policy advice into json dictionay for future use. You can send the part policy whenever you want.
            advice_list[message["part_id"]] = message["queue_id"]
            print("\033[32m#############################################################################")
            print("==== MQTT advice for station ",st_num," is : part id - ", message["part_id"], "dispatch to Queue ID - ", advice_list[message["part_id"]], "====")
            print("#############################################################################\033[0m")

    if msg.topic == "part_id":
        # listening to current part id for dispath policy
        message = translate_message(msg)
        # print("message[machine_id]", message["machine_id"])
        if message["machine_id"] == st_num:
            current_part_id = message["part_id"]
            print("========== current part id :", current_part_id,"========== ")

    if msg.topic == "process_time":
        #-- replace ' with " and do json.loads
        message = translate_message(msg)    #-- expected: {"macihne_id":"1","process_time":"10"}
        if message["machine_id"] == st_num: 
            process_time = message['process_time']  #-- effective only in the next processing as the present processing will be done by the current_process_time set.
            Leds.set_color(Leds.LEFT, Leds.ORANGE)
            Leds.set_color(Leds.RIGHT, Leds.ORANGE)


################################
#--- Program execution
################################
       
        
client = mqtt.Client()
client.connect("192.168.0.50",1883,60) # verify the IP address before connect
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()
try:
    while True:
        if system_status == "start":

            if start_status > 0:
                pusher.run_forever(speed_sp=-pusher_speed)
                sleep(0.8)
                pusher.stop(stop_action='coast')
                start_status = 0
                print("Station ",st_num," is started")
                
                sleep(1)
                
                conveyor.run_forever(speed_sp = -conveyor_speed)
                station.run_forever(speed_sp = -station_speed)


            if btn.down:
                manual_failure = True
                print("\033[31mMachine failed\033[0m")
                Leds.set_color(Leds.LEFT, Leds.RED)
                Leds.set_color(Leds.RIGHT, Leds.RED)
                Sound.speak('FAILURE').wait()

            if btn.up:
                manual_failure = False
                print("\033[32mMachine serviced\033[0m")
                Leds.set_color(Leds.LEFT, Leds.GREEN)
                Leds.set_color(Leds.RIGHT, Leds.GREEN)
                Sound.speak('REPAIRED').wait()

            if queue_sensor.value() > 20 and station_status == "idle":
                pusher.run_forever(speed_sp=pusher_speed)
                payload_start = {"machine_id" : st_num, "status":"Started","part_id":"0","queue_id":"1"}
                client.publish(topic = "trace", payload= json.dumps(payload_start))
                
                print("\033[34m---------- part entering station ", st_num,"----------\033[0m")
                #--- part entry time
                time_entry = datetime.datetime.now().timestamp()
                
                sleep(0.8)
                pusher.stop(stop_action='coast')
                sleep(1)
                pusher.run_forever(speed_sp = -pusher_speed)
                sleep(0.8)
                pusher.stop(stop_action='coast')
                station_status = "busy"

            #--- manual failure
            if btn.down:
                manual_failure = True
                print("\033[31mMachine failed\033[0m")
                Leds.set_color(Leds.LEFT, Leds.RED)
                Leds.set_color(Leds.RIGHT, Leds.RED)
                Sound.speak('FAILURE').wait()

            if btn.up:
                manual_failure = False
                print("\033[32mMachine serviced\033[0m")
                Leds.set_color(Leds.LEFT, Leds.GREEN)
                Leds.set_color(Leds.RIGHT, Leds.GREEN)
                Sound.speak('REPAIRED').wait()    
                
            if station_status == "busy" and time_entry != None:
	              if (datetime.datetime.now().timestamp() - time_entry) > 7:
                             time_entry = datetime.datetime.now().timestamp()
                             print("\033[31m[Station Fault] Part didn't enter the station after Started trace.\033[0m")
                
            if station_sensor.value() > 20 and station_status == "busy" and system_status == "start":
                time_entry = None
                station.stop(stop_action = 'hold') 
                
                #--- sleep for process time
                worked_time = 0
                if process_distribution == 'norm':
                    current_process_time = random.normalvariate(process_time, standard_deviation)
                elif process_distribution == 'expon':
                    current_process_time = random.expovariate(process_time, standard_deviation)
                else:
                    print("\033[31m Wrong distribution type \033[0m")
                print("current_process_time: ", current_process_time)
                
                while True:
                    if system_status == "stop" or worked_time >= current_process_time:
                        break
                    elif manual_failure == False:
                        sleep(1)
                        worked_time += 1
                        # print("worked_time: ",worked_time,", reaming time = ",process_time - worked_time)

                    #--- manual failure
                    if btn.down:
                        manual_failure = True
                        print("\033[31mMachine failed\033[0m")
                        Leds.set_color(Leds.LEFT, Leds.RED)
                        Leds.set_color(Leds.RIGHT, Leds.RED)
                        Sound.speak('FAILURE').wait()

                    if btn.up:
                        manual_failure = False
                        print("\033[32mMachine serviced\033[0m")
                        Leds.set_color(Leds.LEFT, Leds.GREEN)
                        Leds.set_color(Leds.RIGHT, Leds.GREEN)
                        Sound.speak('REPAIRED').wait()


                #--- automatic failure
                if random.random() <= (failure_probability/100) and manual_failure == False:
                    print("\033[31mAutmatic Machine failure\033[0m")
                    automatic_failure_time = random.normalvariate(mttr, 2)
                    print("Mean time to repair: ", round(automatic_failure_time))
                    for ii in range(round(automatic_failure_time)):
                        if system_status == "stop":
                            break
                        else:
                            sleep(1)
                    Sound.speak('REPAIRED').wait()
                    print("\033[32mMachine Repaired\033[0m")


                release = True
                while release:
                    #--- manual failure
                    if btn.down:
                        manual_failure = True
                        print("\033[31mMachine failed\033[0m")
                        Leds.set_color(Leds.LEFT, Leds.RED)
                        Leds.set_color(Leds.RIGHT, Leds.RED)
                        Sound.speak('FAILURE').wait()

                    if btn.up:
                        manual_failure = False
                        print("\033[32mMachine serviced\033[0m")
                        Leds.set_color(Leds.LEFT, Leds.GREEN)
                        Leds.set_color(Leds.RIGHT, Leds.GREEN)
                        Sound.speak('REPAIRED').wait()

                    if blocking_sensor_1.value() < 20 and manual_failure == False:
                        #--- dispatch the part from the station
                        station.run_forever(speed_sp = -station_speed)
    
                        #--- policy assignment: branching machine #--- defualts to: alternating policy
                        #if current_part_id in advice_list:
                            #current_station = advice_list[current_part_id]
                            #print("\033[32m Part dispatch policy of ",current_part_id, " set to ",advice_list[current_part_id],"\033[0m")
                            #del advice_list[current_part_id]  # delete the part policy from the list so that the policy is not repeated during a default condition.
                        #elif current_station ==  "2":
                            #current_station = "3"
                        #elif current_station == "3":
                            #current_station = "2"
                        
                        if system_status == "start":
                          #--- unloading time. Also a part of processing time.
                          for ii in range(3):
                              sleep(1)    #--- delay for the part to move to grey conveyor.
                              if system_status == "stop":
                                  break
                            
                        
                        if system_status == "start":
    
                        #--- publish topics
                            payload_finish ={"machine_id" : st_num, "status":"Finished","part_id":current_part_id, "queue_id":current_station}
                            client.publish(topic = "trace", payload= json.dumps(payload_finish))
                            print("\033[34m----------",current_part_id," proceeding to station ", current_station,"----------\033[0m")
                        current_part_id = "0"
                        sleep(1)
                        
                        station_status = "idle" # set status to idle for allowing the next part
                        release = False

        elif system_status == "stop" and stop_status > 0:
            conveyor.stop(stop_action = 'coast')
            station.stop(stop_action = 'coast')
            pusher.run_forever(speed_sp=pusher_speed)
            sleep(0.8)
            pusher.stop(stop_action='coast')
            process_time = 2
            stop_status = 0
            advice_list = dict()
            current_station = next_queue
            if station_status != "idle":
                station_status = "idle" # set status to idle for allowing the next part  # we discard the part being processed currently.
                print("Station force reset to idle. Current part is discarded.")
            Leds.set_color(Leds.LEFT, Leds.GREEN)
            Leds.set_color(Leds.RIGHT, Leds.GREEN)
            print("Station ",st_num," is stopped")

except KeyboardInterrupt:
    print('INTERRUPTED FROM PC')
    conveyor.stop(stop_action = 'coast')
    station.stop(stop_action = 'coast')
    pusher.stop(stop_action='coast')
    Leds.set_color(Leds.LEFT, Leds.GREEN)
    Leds.set_color(Leds.RIGHT, Leds.GREEN)
    print('Station ',st_num,' program is killed.')
