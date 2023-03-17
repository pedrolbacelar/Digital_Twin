
"""

#--- code to imitate a physical system based on the data in a real_log databse


#--- import libraries
import sqlite3
# import paho.mqtt.client as mqtt
# import json
from time import sleep
import datetime
import os
import sys
from dtwinpylib.dtwinpy.interfaceDB import Database

#--- database path
name = "5s_determ"

old_database_path = "databases/database_replicator/real_database.db"

real_database_path = f"databases/{name}/real_database.db"


#--- removing old database
try:
    os.remove(real_database_path)
    print(f"--- real Database deleted successfuly from {real_database_path} ---")

except FileNotFoundError:
    print(f"[WARNING][broker_manager.py/delete_databases()] The real Database doesn't exist yet in the path '{real_database_path}', proceding without deleting...")
except PermissionError:
    print(f"[ERROR][broker_manager.py/delete_databases()] The real Database is busy somewhere, please close and try again.")
    sys.exit()

#--- create database
real_database = Database(database_path= real_database_path, event_table= "real_log")


# #--- mqtt broker ip address
# ip_address = "127.0.0.1"

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code "+str(rc))


# #--- mqtt connect
# client = mqtt.Client()
# client.connect(ip_address,1883,60,) # verify the IP address before connect

# client.on_connect = on_connect
# client.loop_start()

# while True :


#--- database connect
with sqlite3.connect(old_database_path) as old_db:
    last_event_id = old_db.execute(f"""SELECT MAX(event_id) FROM real_log""").fetchone()[0]
    print(f"total number of traces = {last_event_id}")

    print("====== Starting database replicator ======")

    for ii in range(last_event_id):
        event_id = ii + 1
        current_event = old_db.execute(f"""SELECT * FROM real_log WHERE event_id = ?""",(event_id,)).fetchone()
        if event_id == last_event_id:
            break
        else:
            next_event_time = old_db.execute(f"""SELECT * FROM real_log WHERE event_id = ?""",(event_id+1,)).fetchone()[7]
            wait = next_event_time - current_event[7]

        #--- replace "Machine 11" to "10" in the machine_id
        # machine_id = current_event[2].replace("Machine ","")

        # #--- publish trace
        # payload_finish ={"machine_id" : machine_id, "status":current_event[3],"part_id":current_event[4], "queue_id":current_event[5]}
        # client.publish(topic = "trace", payload= json.dumps(payload_finish))
        print(f"current event_id : {current_event[0]}, machine_id : {current_event[2]}, status : {current_event[3]}, part_id : {current_event[4]}, queue_id : {current_event[5]}")

        #--- we sleep between the traces
        print(f"Next trace in {wait} seconds")
        sleep(wait)


    print("====== Database replicator executed ======")

"""

