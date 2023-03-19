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

################################
#--- Declaration and initiation
################################


st_num = "1"      #--- change st_num for each code depending on the machine_id
next_queue = "3"  #--- change next queue id if it is not a branching station # we start with 2. to change to 2, we initaite it as 3 for station 1
   


#--- declaring optical sensors
station_sensor=ColorSensor(INPUT_1)
station_sensor.mode='COL-REFLECT'
queue_sensor=ColorSensor(INPUT_2)
queue_sensor.mode='COL-REFLECT'
blocking_sensor_1=ColorSensor(INPUT_3)
blocking_sensor_1.mode='COL-REFLECT'

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
process_time = 15    # advised to have no less than 5s of gap between two parts in the downstream conveyor to not have problems with pusher.

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
    client.subscribe(topic = "RCT-server")
    client.subscribe(topic = "part_id")

def on_message(client, userdata, msg):
    # define global variables
    global system_status
    global start_status
    global stop_status
    global current_part_id
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
            print("#############################################################################")
            print("==== MQTT advice for station ",st_num," is :", message["part_id"], " : ", advice_list[message["part_id"]], "====")
            print("#############################################################################")

    if msg.topic == "part_id":
        # listening to current part id for dispath policy
        message = translate_message(msg)
        # print("message[machine_id]", message["machine_id"])
        if message["machine_id"] == st_num:
            current_part_id = message["part_id"]
            print("========== current part id :", current_part_id,"========== ")


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

            if queue_sensor.value() > 20 and station_status == "idle":
                pusher.run_forever(speed_sp=pusher_speed)
                payload_start = {"machine_id" : st_num, "status":"Started","part_id":"0","queue_id":"1"}
                client.publish(topic = "trace", payload= json.dumps(payload_start))
                print("---------- part entering station ", st_num,"----------")

                time_entry = datetime.datetime.now().timestamp()
                
                sleep(0.8)
                pusher.stop(stop_action='coast')
                sleep(1)
                pusher.run_forever(speed_sp = -pusher_speed)
                sleep(0.8)
                pusher.stop(stop_action='coast')
                station_status = "busy"
            
                
            if station_status == "busy" and time_entry != None:
                if datetime.datetime.now().timestamp() - time_entry > 10:
                    print("[Station Fault] Part didn't enter the station after Started trace.")

            if station_sensor.value() > 20 and system_status == "start":
                time_entry = None
                station.stop(stop_action = 'hold')
                
                for ii in range(process_time):
                    sleep(1)
                    if system_status == "stop":
                        break

                release = True
                while release:
                    if blocking_sensor_1.value() < 20:
                        #--- dispatch the part from the station
                        station.run_forever(speed_sp = -station_speed)

                        #--- policy assignment: branching machine #--- defualts to: alternating policy
                        if current_part_id in advice_list:
                            current_station = advice_list[current_part_id]
                        elif current_station ==  "2":
                            current_station = "3"
                        elif current_station == "3":
                            current_station = "2"

                        #--- unloading time. Also a part of processing time.
                        for ii in range(3):
                            sleep(1)    #--- delay for the part to move to grey conveyor.
                            if system_status == "stop":
                                break    
                        
                        if system_status == "start":

                        #--- publish topics
                            payload_finish ={"machine_id" : st_num, "status":"Finished","part_id":current_part_id, "queue_id":current_station}
                            client.publish(topic = "trace", payload= json.dumps(payload_finish))
                            print("----------",current_part_id," proceeding to station ", current_station,"----------")
                        current_part_id = "0"
                        sleep(1)
                        
                        # delete the part policy from the list so that the policy is not repeated during a default condition.
                        if current_part_id in advice_list:
                            del advice_list[current_part_id]
                        station_status = "idle" # set status to idle for allowing the next part
                        release = False

        elif system_status == "stop" and stop_status > 0:
            conveyor.stop(stop_action = 'coast')
            station.stop(stop_action = 'coast')
            pusher.run_forever(speed_sp=pusher_speed)
            sleep(0.8)
            pusher.stop(stop_action='coast')
            stop_status = 0
            current_station = "3"
            if station_status != "idle":
                station_status = "idle" # set status to idle for allowing the next part  # we discard the part being processed currently.
                print("Station force reset to idle. Current part is discarded.")
            print("Station ",st_num," is stopped")

except KeyboardInterrupt:
    print('INTERRUPTED FROM PC')
    conveyor.stop(stop_action = 'coast')
    station.stop(stop_action = 'coast')
    pusher.stop(stop_action='coast')
    print('Station ',st_num,' program is killed.')
