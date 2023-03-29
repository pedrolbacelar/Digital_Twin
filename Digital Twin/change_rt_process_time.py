import paho.mqtt.client as mqtt
import json
from dtwinpylib.dtwinpy.tester import Tester
test = Tester()
test.exp_db_path = "databases/5s_determ/exp_database.db"
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
process = [54,45,60,45,10]  #--- process _time_vector default= [11,17,60,38,10]
#---------------------------------------------------------------------------------------

load_unload_time = [9,8,10,8,8]

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