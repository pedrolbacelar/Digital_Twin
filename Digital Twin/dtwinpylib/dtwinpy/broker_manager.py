#--- Import Modules
from .interfaceDB import Database

#--- Normal Libraries
import paho.mqtt.client as mqtt
import json
from time import sleep
import datetime



#--- Reload Package
import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)

class Broker_Manager():
    def __init__(self, ip_address, real_database_path, ID_database_path, port= 1883, keepalive= 60, topics = ['trace', 'part_id', 'RCT_server'], client = None):
        #--- Connect to the Broker
        self.ip_address= ip_address
        self.port = port
        self.keepalive = keepalive

        #--- MQTT
        self.topics = topics
        self.condition = True # Condition to stop listening topics
        if client == None:
            #--- Create the client object
            self.client = mqtt.Client()
        self.UID_to_PID_dict = {}
        self.PID_to_UID_dict = {}
        self.PID_counter = 1

        #--- Database
        self.real_database_path = real_database_path
        self.ID_database_path = ID_database_path
        self.real_database = Database(database_path= self.real_database_path, event_table= "real_log")
        self.ID_database = Database(database_path= self.ID_database_path, event_table= "ID")

    def part_ID_creator(self, unique_ID, current_time_str):
        """
        This function takes a UID (unique ID of a RFID sticker) and creates a Part ID number (PID). This function
        is only used by the first machine of the system. If a UID repears it re-assign it a new PID.

        TODO:
        1) Add the UID into the dictionary (if it already exists it just re-assign the value)
        2) Increase the PID counter
        """
        #--- Add the UID with the current PID counter in the dictionary
        self.UID_to_PID_dict[unique_ID] = f"Part {self.PID_counter}"

        #----- Add the PID with the current UID to the dictionary
        self.PID_to_UID_dict[f"Part {self.PID_counter}"] = unique_ID

        #----- Add the PID and UID into the PID_UID database
        self.ID_database.add_UID_partid(
            table_name= "ID",
            uid= unique_ID,
            partid= f"Part {self.PID_counter}",
            current_time_str= current_time_str

        )

        #--- Increase the part id counter
        self.PID_counter += 1
    
        #--- DEBUGING
        """for key in self.UID_to_PID_dict:
            print(f"{key} | {self.UID_to_PID_dict[key]}")"""
    
    def part_ID_translator(self, unique_ID):
        """
        This function takes a UID and searches in the PID dictionary for the related PID. The function returns
        this PID. This is used for all the machines.
        """

        #--- Searches in the dictionary for the related PID to the UID and return it
        try:
            part_id = self.UID_to_PID_dict[unique_ID]
            return part_id
        except KeyError:
            print(f"[BROKER][broker_manager.py/part_ID_translator()] Unique ID '{unique_ID}' not found in the Dictionary!")
            print("printing the dicitionary....")
            for key in self.UID_to_PID_dict:
                print(f"{key} | {self.UID_to_PID_dict[key]}")
    
    def traces_handler(self, message_translated, current_timestamp, current_time_str):
        """
        This functions is used when a MQTT message of the topic 'traces' is received by the broker.
        The functions simply need to take the message and write it into the database. Note: When it's
        the "Started" event, the message always have 'part_id': 0, because it didn't read the id from
        the MQTT that the reader sent.

        Format of the message:
        {'machine_id': str, 'status': str, 'part_id': str, queue_id': str}
        """
        #--- Get each part of the message
        machine_id = f"Machine {(message_translated['machine_id'])}"
        status = message_translated['status']
        unique_id = message_translated['part_id']
        queue_id = f"Queue {(message_translated['queue_id'])}"

        if status == "Finished":
            #--- When the machine sends a finished trace, it sends the UID that it read from the RFID reader
            try: 
                #--- Translate the given UID in the related PID
                part_id = self.part_ID_translator(unique_id)
            except KeyError:
                #--- ERROR: unique_ID was not found in the dictionary
                print(f"[ERROR][broker_manager.py/traces_handler()] The Unique ID {unique_id} was not found in the PID dictionary")
                print("printing the current dictionary....")
                for key in self.UID_to_PID_dict:
                    print(f"{key} | {self.UID_to_PID_dict[key]}")
                print("If this is not the Machine 1 handling the first part, STOP THE SIMULATION")
        
        if status == "Started":
            #--- When a machine sends Started, it didn't have the time yet to read the RFID, so it assigns Part 0
            # this id is going to be replaced by the topic 'part_id'
            part_id = "Part 0"

        #--- Write the information into the real database
        self.real_database.write_event('real_log', current_timestamp, machine_id, status, part_id, queue_id, current_time_str)



    def part_id_handler(self, message_translated):
        """
        This functions is used when a MQTT message of the topic 'part_id' is received by the broker.
        When the broker receive this message, it means that a new part arrive in one of the machines
        and at this point the machine already had sent the message to the broker with "Started", but in
        the database we have the part id for that event as 0. So the mission here is to take the id 
        received and update for the right machine (given by the reader as well) in the Started event.
        The finish event is correct, so we don't need to care about it.
        
        Format of the message:
        {'machine_id': str, 'part_id': str}

        TODO:
        1) Store the machine id and the part id from the message
        2) Search in the database for a the machine id where the part id is 0 and take the line id
        3) Assign the part id for that line id
        """
        #--- Take the current time
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%d %B %H:%M:%S")

        #--- Read the message
        
        machine_id = f"Machine {(message_translated['machine_id'])}"
        unique_ID = message_translated['part_id']
        
        #--- If machine 1, (re)create the PID for that given UID
        if machine_id == "Machine 1":
            #--- Create the PID related to the UID and assign it in the PID dict
            self.part_ID_creator(unique_ID, current_time_str)

        #--- For all the machines (including machine 1)
        # Take the corresponded PID of the given UID
        part_id = self.part_ID_translator(unique_ID)


        #--- Search in the database for line id of the given machine with 0 in the part id
        line_id_ltuple = self.real_database.findLine_2conditions(
            table= "real_log",
            column1= "machine_id",
            column2= "part_id",
            condition1= machine_id,
            condition2= "Part 0"
        )

        
        try:
            #--- Take only the number
            line_id = line_id_ltuple[0][0]

            #--- UPDATE the part id started for the specific machine into the Real Database
            self.real_database.update_column(
                table= "real_log",
                column= "part_id",
                line_id= line_id,
                new_value= part_id
            )

        except IndexError:
            print(f"{current_time_str} | [ERROR][BROKER]: Your Broker Manager didn't find {machine_id} with 'Part 0' in the database ({self.real_database_path})")
        
    def rct_handler(self, message_translated):
        """
        For time being, do nothing...
        """
        pass
        
    def translate_message(self, message):
        """
        This function receives the message from the MQTT and translate it into a dictionary.
        """
        #--- Decode the message received from the MQTT
        message_decoded = str(message.payload.decode())

        #--- Replace ' to "
        message_replaced = message_decoded.replace("'", "\"")

        #print(f"Message raplaced: {message_replaced}")

        #--- Convert the message received in to a dictionary
        message_translated = json.loads(message_replaced)

        return message_translated

    def on_connect(self, client, userdata, flags, rc):
        #--- Little drama
        for i in range(2):
            print(".")
            sleep(1)
        if rc == 0:
            print(f"----- Connected with {self.ip_address} Successfully -----")
        else:
            print(f"----- Connected with {self.ip_address} FAILED -----")

        #--- Subscribe to the topics
        print("Subscribed Topics:")
        for topic in self.topics:
            client.subscribe(topic = topic)
            print(f"|-- '{topic}'")

    def on_message(self,client, userdata, message):
        #--- Message Topic
        message_topic = message.topic

        #--- Translate the message into a Dictionary
        message_translated = self.translate_message(message)

        #--- Get the timestemp and translate it
        current_timestamp = datetime.datetime.now().timestamp()
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%d %B %H:%M:%S")

        #--- Print the payload received
        print(f"{current_time_str} | Topic: {message_topic} | Payload Received: {message_translated}")


        # -------------- Topic: 'traces' --------------
        if message_topic == 'trace':
            self.traces_handler(message_translated, current_timestamp, current_time_str)

        # -------------- Topic: 'part_id' --------------
        if message_topic == 'part_id':
            self.part_id_handler(message_translated)

        # -------------- Topic: 'RCT_server' -------------
        if message_topic == 'RCT_server':
            self.rct_handler(message_translated)

    def connect(self):
        """
        This function creates the object client and returns it. The function also
        make the connection with the broker 
        """
        #--- Connect the client to the broker
        self.client.connect(self.ip_address, self.port, self.keepalive)

        #--- Submitte the right function
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def run(self):
        """
        This function is the main function of the broker manager. It will make the connection with
        the broker given the ip address configurations. With the success connection, the broker
        manager will start listening different topics and write the messages into the Database.
        The manager is also capable of receiving message from the stations and from the RFID
        readers. Using the reading of RFID, the manager can assign the which part is in which machines.

        TODO:
        1) Make the connection with the broker
        2) Start to listening to the topics
            3) on message: For each new message write into the database
            4) Part ID assigning:
                5) for the received message from the reader, identify the machine id
                6) For that machine id, look into the database to see if the line still with zero in part id
                7) if yes, replace it with the right part id

        """
        #--- Make the connection with the broker
        self.connect()

        #--- Start the communication to listening topics
        self.client.loop_start()
        self.condition = True

        #--- Inifinity loop to listening messages
        while self.condition:
            try:
                sleep(1)
            except KeyboardInterrupt:
                self.condition = False
                print(f"---- Communication with {self.ip_address} killed manually----")
        
        #--- Stop the connection and disconnect the client
        self.client.loop_stop()
        self.client.disconnect()

    def publishing(self, machine_id, part_id, queue_id, topic= "RCT_server"):
        """
        This is a simple function to publish a topic into the Broker
        """
        #--- Make the connection with the Broker
        self.client.connect(self.ip_address, self.port, self.keepalive)

        #--- Create the payload variables
        machineid = machine_id
        partid = part_id
        queueid = queue_id

        #--- Inverse translation: Take the part id number and return the UID
        unique_ID = self.ID_database.get_PID(
            table_name= "ID",
            partid= f"Part {partid}"
        )

        #--- Create the payload
        payload= {
            "machine_id": machineid,
            "part_id": unique_ID,
            "queue_id": queueid
        }

        #--- Translate the payload
        payload_translated = json.dumps(payload)

        #--- Publish the payload
        self.client.publish(
            topic = topic, 
            payload= payload_translated
        )

        #--- Take the current time
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%d %B %H:%M:%S")

        #--- Print the payload received
        print(f"[BROKER] {current_time_str} | Topic: {topic} | Payload Published: {payload_translated}")

        
