import paho.mqtt.client as mqtt
import json
from dtwinpylib.dtwinpy.tester import Tester
from dtwinpylib.dtwinpy.helper import Helper
from time import sleep

helper = Helper()
test = Tester()
test.exp_db_path = "databases/5s_stho/exp_database.db"
myip = "127.0.0.1"
factory_ip = "192.168.0.50"

#--- set mqtt ip address
mqtt_ip = factory_ip

#--- create table if not created
test.create_rt_process_time_log()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    pass


client = mqtt.Client()
client.connect(mqtt_ip,1883,60) # verify the IP address before connect
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()



#----------------------------------- INPUT DATA ----------------------------------------
wait_interval = 1
process1 = [40,'NULL','NULL','NULL',40]  #--- process _time_vector default= [11,17,60,38,10]
matrix_process = [
    process1
]
#---------------------------------------------------------------------------------------

load_unload_time = [9,8,10,8,8]



process_counter = 0

print(f"Automatic Change of Process time activated...")
print(f"|--- Process times to be send:")
for process in matrix_process:
    print(f"|------ process: {process}")

while process_counter < len(matrix_process):
    # --------------------------------- WAITING TIME --------------------------------------
    helper.printer(f"Sleeping for {wait_interval}...", 'purple')
    sleep(wait_interval)
    helper.printer(f" ---------- Waking up and preparing payloads... ----------", 'purple')
    #---------------------------------------------------------------------------------------

    #----------------- CURRENT PROCESS TO SEND -----------------
    process = matrix_process[process_counter]
    #-----------------------------------------------------------

    #---- User interface
    print(f"Current process counter: {process_counter}")
    print(f"Process to be send: {process}")

    if process[0] != 'NULL':
        payload = {"machine_id" : "1", "process_time":process[0]-load_unload_time[0]}
        client.publish(topic = "process_time", payload= json.dumps(payload))
        print(f"Published new process time for machine_1: {process[0]}")

    if process[1] != 'NULL':
        payload = {"machine_id" : "2", "process_time":process[1]-load_unload_time[1]}
        client.publish(topic = "process_time", payload= json.dumps(payload))
        print(f"Published new process time for machine_2: {process[1]}")

    if process[2] != 'NULL':
        payload = {"machine_id" : "3", "process_time":process[2]-load_unload_time[2]}
        client.publish(topic = "process_time", payload= json.dumps(payload))
        print(f"Published new process time for machine_3: {process[2]}")

    if process[3] != 'NULL':
        payload = {"machine_id" : "4", "process_time":process[3]-load_unload_time[3]}
        client.publish(topic = "process_time", payload= json.dumps(payload))
        print(f"Published new process time for machine_4: {process[3]}")

    if process[4] != 'NULL':
        payload = {"machine_id" : "5", "process_time":process[4]-load_unload_time[4]}
        client.publish(topic = "process_time", payload= json.dumps(payload))
        print(f"Published new process time for machine_4: {process[4]}")

    test.write_rt_process_time_log(process_time_vector=process)

    process_counter += 1

print(f"ALL CHANGES MADE! exiting....")