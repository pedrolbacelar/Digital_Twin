#--- Import DT Features
from .validator import Validator
import json
import sqlite3

#--- Reload Package

import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.validator)



class Zone():
    def __init__(self, machine, queue_list):
        self.name = "Zone of " + machine.get_name()
        self.machine = machine
        self.queue_list = queue_list
        self.zoneInd = None
        #--- Counters for in and out number of parts
        self.inZone = 0
        self.outZone = 0
        self.Zone_initial = 0
        self.NumParts = 0
        self.machine_working = 0
        self.last_started_time = 0

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
    def Mstarted(self):
        self.machine_working += 1
    def Mfinished(self):
        self.machine_working -= 1
    

    def self_validation(self, Verbose = True):
        #--- Use the data from the simulation (digital log)
        self_counter = 0
        #--- Check the number of parts in the queues ins
        for queue in self.queue_list:
            self_counter += queue.get_len()

        #--- Check if the machine is working (zone is parts in the queues ins and + machine)
        if self.machine.get_working() == True:
            self_counter += 1
        
        if Verbose == True:
            print(f"[{self.name}] NumParts = {self_counter}, Machine Working = {self.machine.get_working()}")

        #--- Take the last time that a part was started by the machine
        part_started_time = self.machine.get_part_started_time()

        #--- Return the number of parts in the zone, if the machine is processing, and the time that the processing started
        return (self_counter)

    #--- Basic Sets and Gets
    #--- GETs
    def get_name(self):
        return self.name
    def get_queue_list(self):
        return self.queue_list
    def get_machine_is_final(self):
        return self.machine.get_final_machine()
    def get_machine_working(self):
        if self.machine_working == 1:
            return True
        if self.machine_working == 0:
            return False
    def get_zoneInd(self):
        return self.zoneInd
    def get_NumParts(self):
        return self.NumParts
    def get_last_started_time(self):
        return self.last_started_time
    def get_machine(self):
        return self.machine
    #--- SETs
    def set_zoneInd(self, indicador):
        self.zoneInd = indicador
    def set_last_started_time(self, started_time):
        self.last_started_time = started_time

class Synchronizer():
    def __init__(self, digital_model, real_database):
        #--- Basic Information
        self.digital_model = digital_model
        self.zones_dict = {}
        self.Tnow = 0

        #--- Database
        self.real_database = real_database
        self.real_database_path = self.real_database.get_database_path()
        with sqlite3.connect(self.real_database_path) as db:
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            if len(tables) == 1 and tables[0][0] == "digital_log":
                self.real_database.rename_table("digital_log", "real_log")
        
        self.full_database = self.real_database.read_store_data_all("real_log")
        

        #--- Digital Model
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()
        
    def create_zones(self):
        for machine in self.machines_vector:
            #--- Basic information from the machine
            machine_name = machine.get_name()
            machine_queues_in_list = machine.get_queue_in()

            #--- create a temp Zone object
            new_zone = Zone(machine= machine, queue_list= machine_queues_in_list)

            #--- add the Zone object in the dictionary of zones
            self.zones_dict[machine_name] = new_zone
                
    def positioning_discovery(self):
        #--- Find the Positioning
        for event in self.full_database:
            #--- Extract the important informations
            (time, machine_name, status, queue_name) = (event[0], event[1], event[2], event[4]) 
            
            # We just care about the events with status "Finished",
            # because this in the only moment when we subtract some part from the current
            # zone and add it to the next zone
            current_zone = self.zones_dict[machine_name]

            if status == "Finished":
                # For the current zone a part was finished, so we increment the Out
                current_zone.addOut()
                current_zone.Mfinished()

                #--- Discovery in which zone the part was putted based on the queues and machines
                for key in self.zones_dict:
                    #--- For every zone in the zone dictionary
                    zone = self.zones_dict[key]

                    #--- For every queue of a Zone
                    for queue in zone.get_queue_list():

                        #--- Found a zone if the selected next queue
                        if queue.get_name() == queue_name:
                            next_zone = zone
                        
                #--- For the next zone, increment the In since we're adding a part to that zone
                next_zone.addIn()

            if status == "Started":
                current_zone.Mstarted()
                current_zone.set_last_started_time(time)
        
        #--- Assign Tnow according the last event of the real log
        self.Tnow = self.full_database[-1][0]
    
    def sync_TDS(self):
        print("======================= Running TDS for Sync =======================")
        validator_sync = Validator(digital_model= self.digital_model, simtype= "TDS", real_database= self.real_database)

        #-------- Runnin TDS --------
        # (same implementation used in logic validation)
        # IMPROVE: give the object validator for the machine to be able to update the ptime_TDS for new parts
        
        #--- Get the components of the simulation
        (machines_vector, queues_vector) = self.digital_model.get_model_components()
        for machine in machines_vector:
            machine.set_validator(validator_sync)
        
        #--- Allocate the traces
        validator_sync.allocate()

        #--- Run the TDS
        validator_sync.run()
        #-----------------------------
        print("=====================================================================")
    
    def sync_indicator(self):
        for key in self.zones_dict:
            #--- For each Zone
            current_zone = self.zones_dict[key]

            #--- Take the number of parts in the zone according to the real log (real zone)
            NumParts_real = current_zone.calculate_parts()

            #--- Take the information from the digital perspective (digital zone)
            (NumParts_digital) = current_zone.self_validation(Verbose = False)

            #--- Calculate the Indicator for that Zone

            #--- Check for zeros
            if NumParts_real != 0:
                error = (NumParts_real - NumParts_digital) / max(NumParts_real, NumParts_digital)
                syncInd = 1 - error
                current_zone.set_zoneInd(syncInd)
            
            if NumParts_real == 0:
                if NumParts_real == NumParts_digital:
                    error = 0
                else:
                    error = 1

                syncInd = 1 - error
                current_zone.set_zoneInd(syncInd)
            
    def sync_aligment(self):
        #--- Loop through each zone (machine and queue in)
        for key in self.zones_dict:
            #--- For each Zone
            current_zone = self.zones_dict[key]
            current_NumParts = current_zone.get_NumParts()
            parts_in_queues = current_NumParts
            current_Queues_In = current_zone.get_queue_list()
            current_machine = current_zone.get_machine()


            #--- Verify if the Zone is working or not
            if current_zone.get_machine_working() == True:
                #-- Machine is working
                # So from all the parts in the Zone, I need to subtract one to have the
                # number of parts in the queues
                parts_in_queues = current_NumParts - 1

                #--- Calculate the Delta T between the last started time of the machine and
                # the current time of the real world (Tnow)
                Delta_T_started = self.Tnow - current_zone.get_last_started_time()

                #--- Positioning a part within the working machine
                # ============= Update Model.json =============
                model_path = self.digital_model.get_model_path()
                with open(model_path, 'r+') as model_file:
                    data = json.load(model_file)
                    #--- For each machine (node)
                    for node in data['nodes']:
                        if node['activity'] == current_machine.get_id():
                            node['worked_time'] = Delta_T_started

                            #---- Write Back the Changes
                            # Move the file pointer to the beginning of the file
                            model_file.seek(0)
                            # Write the modified data back to the file
                            json.dump(data, model_file)
                            # Truncate any remaining data in the file
                            model_file.truncate()

                            break

            # ================== Positioning of Parts in Queues ==================
            #--- Loop through the Queues to allocate the parts
            for queue in current_Queues_In:
                queue_len = queue.get_len()

                #-- Check if we have more parts than space in the current queue
                # ----------- Not happing with Merged Queues Ins -----------
                if parts_in_queues > queue_len:

                    parts_to_allocate = queue_len
                    # ============= Update Model.json =============
                    model_path = self.digital_model.get_model_path()
                    with open(model_path, 'r+') as model_file:
                        data = json.load(model_file)
                        
                        # Where should I positioned the part? 
                        #=====================================
                        data['initial'][queue.get_id() - 1] = parts_to_allocate
                        #=====================================

                        # Move the file pointer to the beginning of the file
                        model_file.seek(0)
                        # Write the modified data back to the file
                        json.dump(data, model_file)
                        # Truncate any remaining data in the file
                        model_file.truncate()
                    
                    #--- Update the remaining parts to be allocate
                    parts_in_queues = parts_in_queues - parts_to_allocate

                
                #--- Queue has capacity to allocate the remaining parts
                if parts_in_queues <= queue_len:
                    # ============= Update Model.json =============
                    model_path = self.digital_model.get_model_path()
                    with open(model_path, 'r+') as model_file:
                        data = json.load(model_file)
                        
                        #=====================================
                        data['initial'][queue.get_id() - 1] = parts_in_queues
                        #=====================================

                        # Move the file pointer to the beginning of the file
                        model_file.seek(0)
                        # Write the modified data back to the file
                        json.dump(data, model_file)
                        # Truncate any remaining data in the file
                        model_file.truncate()
                    
                    # Since the number of parts to positioned is less than what i can, i'm done
                    break


    def show(self):
        
        #--- Running Self Validation
        print("=========== Self Validation ===========")
        for key in self.zones_dict:
            current_zone = self.zones_dict[key]
            zone_NumParts = current_zone.self_validation()
        print("=========================================")
        

        #--- Print the Zones Occupation
        print("=========== Zones Occupations ===========")
        for key in self.zones_dict:
            current_zone = self.zones_dict[key]
            zone_NumParts = current_zone.calculate_parts()
            machine_working = current_zone.get_machine_working()
            indicator = current_zone.get_zoneInd()
            print(f"[{current_zone.get_name()}] NumParts = {zone_NumParts}, Machine Working = {machine_working}, Zone Indicador = {indicator}")
        print("=========================================")
    
    def run(self, repositioning = True):
        #--- Create the Zones for the Initial Conditions
        self.create_zones()

        #--- Find the Positioning for the parts in the real log
        self.positioning_discovery()

        #--- Run the Trace Driven Simulation
        self.sync_TDS()

        #--- Calculate the Indicator
        self.sync_indicator()

        #--- Aligment (re-positioning)
        if repositioning == True:
            self.sync_aligment()

        #--- Show the results
        self.show()