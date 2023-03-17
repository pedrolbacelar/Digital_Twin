#--- code to imitate a physical system based on the data in a real_log databse


#--- import libraries
import sqlite3
import paho.mqtt.client as mqtt
import json
from time import sleep

#--- database path
database_path = "databases/database_replicator/real_database.db"


#--- mqtt broker ip address
ip_address = "127.0.0.1"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


#--- mqtt connect
client = mqtt.Client()
client.connect(ip_address,1883,60,) # verify the IP address before connect

client.on_connect = on_connect
client.loop_start()

while True :
    #--- database connect
    with sqlite3.connect(database_path) as db:
        last_event_id = db.execute(f"""SELECT MAX(event_id) FROM real_log""").fetchone()[0]
        print(f"total number of traces = {last_event_id}")

        print("====== Starting database replicator ======")

        for ii in range(last_event_id):
            event_id = ii + 1
            current_event = db.execute(f"""SELECT * FROM real_log WHERE event_id = ?""",(event_id,)).fetchone()
            if event_id == last_event_id:
                break
            else:
                next_event_time = db.execute(f"""SELECT * FROM real_log WHERE event_id = ?""",(event_id+1,)).fetchone()[7]
                wait = next_event_time - current_event[7]

            #--- replace "Machine 11" to "10" in the machine_id
            machine_id = current_event[2].replace("Machine ","")

            #--- publish trace
            payload_finish ={"machine_id" : machine_id, "status":current_event[3],"part_id":current_event[4], "queue_id":current_event[5]}
            client.publish(topic = "trace", payload= json.dumps(payload_finish))
            print(f"current event_id : {current_event[0]}, machine_id : {machine_id}, status : {current_event[3]}, part_id : {current_event[4]}, queue_id : {current_event[5]}")

            #--- we sleep between the traces
            print(f"Next trace in {wait} seconds")
            sleep(wait)


        print("====== Database replicator executed ======")



