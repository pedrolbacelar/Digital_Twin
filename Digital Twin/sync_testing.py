from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.interfaceDB import Database


import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.interfaceDB) #reload this specifc module to upadte the class


"""
class Zone():
    def __init__(self, machine, queue_list):
        self.name = "Zone of " + machine.get_name()
        self.machine = machine
        self.queue_list = queue_list
        #--- Counters for in and out number of parts
        self.inZone = 0
        self.outZone = 0
        self.Zone_initial = 0
        self.NumParts = 0

        #--- Initial Conditions
        # Multiple Queues
        if len(self.queue_list) > 1:
            ini_count = 0
            for queue in self.queue_list:
                ini_count += queue.get_len()
            self.Zone_initial = ini_count
        
        # Single Queue
        if len(self.queue_list) == 1:
            queue = self.queue_list[0]
            self.Zone_initial = queue.get_len()
    
    #--- A part entered the Zone
    def addIn(self):
        self.inZone += 1
    #--- A part leaves the Zone
    def addOut(self):
        self.outZone += 1
    def calculate_parts(self):
        #--- Calculate the number of parts in the machine considering the initial conditions and the delta changes
        self.NumParts = (self.Zone_initial + self.inZone - self.outZone) 
        return  self.NumParts
    
    def self_validation(self):
        self_counter = 0
        #--- Check the number of parts in the queues ins
        for queue in self.queue_list:
            self_counter += queue.get_len()

        #--- Check if the machine is working (zone is parts in the queues ins and + machine)
        if self.machine.get_working() == True:
            self_counter += 1
        
        print(f"[{self.name}] NumParts = {self_counter}")
    

    #--- Basic Sets and Gets
    def get_name(self):
        return self.name
    def get_queue_list(self):
        return self.queue_list
    def get_machine_is_final(self):
        return self.machine.get_final_machine()
    
    
#-------------------------------------------------------------------------------------------------------


digital_twin = Digital_Twin(name= "model_2stations_closed",until= 2001, initial=True )
digital_model = digital_twin.generate_digital_model()

#--- Initial conditions
(machines_vector, queues_vector) = digital_model.get_model_components()

#--- Create the Zones and its dictionary
zones_dict = {}
for machine in machines_vector:
    #--- Basic information from the machine
    machine_name = machine.get_name()
    machine_queues_in_list = machine.get_queue_in()

    #--- create a temp Zone object
    new_zone = Zone(machine= machine, queue_list= machine_queues_in_list)

    #--- add the Zone object in the dictionary of zones
    zones_dict[machine_name] = new_zone


#--- Run the simulation to update the database
digital_model.run()

#--- Extract Events from the database
database = Database(database_path= "databases/digital_model_2stations_closed_db.db", event_table= "digital_log")
full_database = database.read_store_data_all("digital_log")

#--- Find the Positioning
for event in full_database:
    #--- Extract the important informations
    (machine_name, status, queue_name) = (event[1], event[2], event[4]) 
    
    # We just care about the events with status "Finished",
    # because this in the only moment when we subtract some part from the current
    # zone and add it to the next zone

    if status == "Finished":
        # For the current zone a part was finished, so we increment the Out
        current_zone = zones_dict[machine_name]
        current_zone.addOut()

        #--- Discovery in which zone the part was putted based on the queues and machines
        for key in zones_dict:
            #--- For every zone in the zone dictionary
            zone = zones_dict[key]

            #--- For every queue of a Zone
            for queue in zone.get_queue_list():

                #--- Found a zone if the selected next queue
                if queue.get_name() == queue_name:
                    next_zone = zone
                
        #--- For the next zone, increment the In since we're adding a part to that zone
        next_zone.addIn()

#--- Running Self Validation
print("=========== Self Validation ===========")
for key in zones_dict:
    current_zone = zones_dict[key]
    zone_NumParts = current_zone.self_validation()
print("=========================================")


#--- Print the Zones Occupation
print("=========== Zones Occupations ===========")
for key in zones_dict:
    current_zone = zones_dict[key]
    zone_NumParts = current_zone.calculate_parts()
    print(f"[{current_zone.get_name()}] NumParts = {zone_NumParts}")
print("=========================================")
"""


name = "5s_allocation"
digital_twin = Digital_Twin(name= name,maxparts=5, initial=True )
digital_twin.run_digital_model()
digital_twin.run_sync()