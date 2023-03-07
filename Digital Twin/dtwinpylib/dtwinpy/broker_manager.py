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
    def __init__(self, ip_address, real_database_path, port= 1883, keepalive= 60, topics = ['trace', 'part_id', 'RCT-server'], client = None):
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

        #--- Database
        self.real_database_path = real_database_path
        self.real_database = Database(database_path= self.real_database_path, event_table= "real_log")

    def traces_handler(self, message_translated, current_timestamp):
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
        part_id = f"Part {message_translated['part_id']}"
        queue_id = f"Queue {(message_translated['queue_id'])}"

        #--- Write the information into the real database
        self.real_database.write_event('real_log', current_timestamp, machine_id, status, part_id, queue_id)

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
        current_time_str = current_time.strftime("%d %B %Y %H:%M:%S")

        #--- Read the message
        machine_id = f"Machine {(message_translated['machine_id'])}"
        part_id = f"Part {message_translated['part_id']}"

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
        #--- Decode the message received from the MQTT
        message_decoded = message.payload.decode()

        #--- Message Topic
        message_topic = message.topic

        #--- Get the timestemp and translate it
        current_timestamp = datetime.datetime.now().timestamp()
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%d %B %Y %H:%M:%S")


        #--- Convert the message received in to a dictionary
        message_translated = json.loads(message_decoded)
        
        #--- Print the payload received
        print(f"{current_time_str} | Topic: {message_topic} | Payload Received: {message_translated}")

        # -------------- Topic: 'traces' --------------
        if message_topic == 'traces':
            self.traces_handler(message_translated, current_timestamp)

        # -------------- Topic: 'part_id' --------------
        if message_topic == 'part_id':
            self.part_id_handler(message_translated)

        # -------------- Topic: 'RCT-server' -------------
        if message_topic == 'RCT-server':
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

    def publishing(self, machine_id, part_id, queue_id, topic= "RCT-server"):
        """
        This is a simple function to publish a topic into the Broker
        """
        #--- Make the connection with the Broker
        self.client.connect(self.ip_address, self.port, self.keepalive)

        #--- Create the payload
        machineid = machine_id
        partid = part_id
        queueid = queue_id

        payload= {
            "machine_id": machineid,
            "part_id": partid,
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
        current_time_str = current_time.strftime("%d %B %Y %H:%M:%S")

        #--- Print the payload received
        print(f"[BROKER] {current_time_str} | Topic: {topic} | Payload Published: {payload_translated}")

        
