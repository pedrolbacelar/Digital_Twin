#--- Import DT Features
from .validator import Validator
from .interfaceDB import Database
from .helper import Helper

#--- Normal libraries
import json
import sqlite3
import sys


#--- Reload Package

"""import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.validator)"""



class Zone():
    def __init__(self, machine, queue_list, digital_model= None):
        self.helper = Helper()
        self.digital_model = digital_model
        self.name = "Zone of " + machine.get_name()
        self.machine = machine
        self.zoneID = self.machine.get_id()
        self.queue_list = queue_list
        self.zoneInd = None
        #--- Counters for in and out number of parts
        self.inZone = 0
        self.outZone = 0
        self.Zone_initial = 0
        self.NumParts = 0
        self.machine_working = 0
        self.last_started_time = 0
        self.flag_initial_working = False
        self.first_zone_event = True
        self.event_type = "Started"
        self.next_queue_position = None

        #--- Storing Parts ID
        self.parts_ids_in_queue = []
        self.parts_ids_in_machine = []

        #---------- Initial Conditions ----------
        # Multiple Queues
        if len(self.queue_list) > 1:
            ini_count = 0
            for queue in self.queue_list:
                ini_count += queue.get_len()
                
                #-- Initial counter
                self.Zone_initial = ini_count

                #-- Initial conditions of the parts already in the Queue
                initial_parts_in_queue = queue.get_all_items()
                for part in initial_parts_in_queue:
                    self.parts_ids_in_queue.append(part.get_name())

        # Single Queue
        if len(self.queue_list) == 1:
            queue = self.queue_list[0]
            self.Zone_initial = queue.get_len()

            #-- Initial conditions of the parts already in the Queue
            initial_parts_in_queue = queue.get_all_items()
            for part in initial_parts_in_queue:
                self.parts_ids_in_queue.append(part.get_name())

        #--- Initial Condition machine
        if self.machine.get_initial_part() != None:
            #-- Add a part in the list of parts workings
            initial_part = self.machine.get_initial_part()
            self.parts_ids_in_machine.append(initial_part.get_name())

            #-- Increment the counter to let it know that we started with a part working
            self.machine_working = 1

            #-- Set the last time that the machine started working 
            self.last_started_time = self.machine.get_worked_time()

            #-- Rase the flag that this machine started the simulation with a part
            self.flag_initial_working = True

            #-- Increment the initial condition indicator
            self.Zone_initial += 1

            print(f"[SYNC] {self.machine.get_name()} started with part already been processed!")
            print(f"--- From the Digital Mode: ---")
            print(f"machine_working: {self.machine_working}")
            print(f"last_started_time: {self.last_started_time}")
            print(f"initial_part: {initial_part.get_name()}")


        # ------- DOUBLE CHECK -------
        self.check_inital_working_machine()



    #--- A part entered the Zone
    def addIn(self, part_id):
        self.inZone += 1
        
        #--- Everytime a part is ADD to the zone we add it to the queue
        self.parts_ids_in_queue.append(part_id)



    #--- A part leaves the Zone
    def addOut(self, part_id):
        self.outZone += 1

        #--- Everytime a part is REMOVE to the zone we add it to the queue
        """if self.get_first_zone_event() == False and len(self.parts_ids_in_queue)>0:
            #--- I just remove if is not the first event (Finished). If something never
            # entered the zone and it's leaveing, I don't care about it.
            self.parts_ids_in_queue.remove(part_id)
        """
    def calculate_parts(self):
        #--- Calculate the number of parts in the machine considering the initial conditions and the delta changes
        self.NumParts = (self.Zone_initial + self.inZone - self.outZone) 
        return  self.NumParts
    def Mstarted(self, part_id):
        self.machine_working += 1

        #--- ADD the part into the machine vector everytime the machine starts processing
        self.parts_ids_in_machine.append(part_id)

        #--- REMOVE from the previous Queue (following the order of the simulation)
        #--- Everytime a part is REMOVE to the zone we add it to the queue
        # OLD: if self.get_first_zone_event() == False and len(self.parts_ids_in_queue)>0:
        #--- Moda a caralha
        if part_id in self.parts_ids_in_queue:
            #--- I just remove if is not the first event (Finished). If something never
            # entered the zone and it's leaveing, I don't care about it.
            self.parts_ids_in_queue.remove(part_id)
        else:
            self.helper.printer(f"[WARNING][synchronizer.py/Mstarted()] {part_id} was not found in elements vector of the queue", "yellow")
            #print(f"[WARNING][synchronizer.py/Mstarted()] {part_id} was not found in elements vector of the queue")
            print("This might happen if the element is an initial part. If that not the case, CHECK IT OUT!")
            print(f"printing the list of parts in the queue: {self.parts_ids_in_queue}")    
    def Mfinished(self, part_id):
        #-- In the case that this was the part that the machine started the simulation
        if self.flag_initial_working == True:
            self.flag_initial_working = False
        
        #-- Decrease the machine counter
        self.machine_working -= 1

        """#--- REMOVE the part from the machine vector everytime the machine finished the processing
        if self.get_first_zone_event() == False and len(self.parts_ids_in_machine)>0:
            #--- I just remove if is not the first event (Finished). If something never
            # entered the zone and it's leaveing, I don't care about it.
            self.parts_ids_in_machine.remove(part_id)"""
        
        if part_id in self.parts_ids_in_machine:
            self.parts_ids_in_machine.remove(part_id)
        else:
            self.helper.printer(f"[WARNING][synchronizer.py/Mstarted()] {part_id} was not found in elements vector of the machine", "yellow")     
    def next_allocation(self, queue_allocated):
            # --- Check if it's a branching machine
            if self.machine.get_branch() != None:
                machine_queues = self.machine.get_queue_out()

                # Create a vector with the names of the queues
                machine_queues_name = []
                for queue in machine_queues:
                    machine_queues_name.append(queue.get_name())

                # Find the position of the current selected queue
                queue_position = machine_queues_name.index(queue_allocated)

                # Verify if it's the last position
                if queue_position == len(machine_queues_name) - 1:
                    # If it was the last, the next is the first
                    self.next_queue_position = 0
                # Incase it was not the last
                else:
                    self.next_queue_position = queue_position + 1

    def check_inital_working_machine(self):
        model_path = self.digital_model.get_model_path()
        with open(model_path, 'r+') as model_file:
            data = json.load(model_file)
            #--- For each machine (node)
            for node in data['nodes']:
                if node['activity'] == self.machine.get_id():
                    self.machine_worked_time = node['worked_time']
        
        if self.machine_worked_time != 0:
            self.machine_worked_time_initial = self.machine_worked_time[0]
            self.machine_working_initial_part = self.machine_worked_time[1]

        # ---------- CHECK ------------
        if (self.machine_working == 0 and self.machine_worked_time != 0):
            self.helper.printer(f"[ERROR][synchronizer.py/check_inital_working_machine()] The Sync thinks that there is no part in the machine, but actually the worked time in the model is different than 0", 'red')
            print(f"--- From the Digital Mode: ---")
            print(f"machine_working: {self.machine_working}")
            print(f"last_started_time: {self.last_started_time}")

            print(f"--- From the Model JSON: ---")
            print(f"machine_worked_time_initial: {self.machine_worked_time_initial}")
            print(f"machine_working_initial_part: {self.machine_working_initial_part}")


    def self_validation(self, Verbose = True):
        #--- Use the data from the simulation (digital log)
        self_counter = 0
        #--- Check the number of parts in the queues ins
        for queue in self.queue_list:
            self_counter += queue.get_len()

        #--- Check if the machine is working (zone is parts in the queues ins and + machine)
        if self.machine.get_working() == True:
            self_counter += 1
        
        #--- Check if there is any part in the Conveyor
        # Since each machie has one queue in and also one conveyor 
        # delivering a part to that queue, we can do this.
        
        #-- Take the conveyors in of that machine
        machine_conveys_in = self.machine.get_convey_ins()

        #-- Parts being transported within the Conveyor when the Sync was done
        parts_in_convey_counter = 0

        # For each conveyor within the machine conveyors ...
        for conveyor in machine_conveys_in:
            parts_in_convey = len(conveyor.get_all_items())
            parts_in_convey_counter += parts_in_convey 

        #--- Update the overall counter of the Zone
        self_counter += parts_in_convey_counter

        if Verbose == True:
            print(f"[{self.name}] NumParts = {self_counter}, Machine Working = {self.machine.get_working()}, Parts in Conveyor = {parts_in_convey_counter}")

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
    def get_Zone_initial(self):
        return self.Zone_initial
    def get_first_zone_event(self):
        return self.first_zone_event
    def get_part_id_in_queue(self):
        return self.parts_ids_in_queue
    def get_part_id_in_machine(self):
        return self.parts_ids_in_machine
    def get_flag_initial_working(self):
        return self.flag_initial_working
    def get_id(self):
        return self.zoneID
    def get_allocation_counter(self):
        return self.next_queue_position
    #--- SETs
    def set_zoneInd(self, indicador):
        self.zoneInd = indicador
    def set_last_started_time(self, started_time):
        self.last_started_time = started_time
    def set_first_zone_event(self, status):
        self.first_zone_event = status
    def set_event_type(self, type):
        self.event_type = type
    def set_Zone_initial(self, ini):
        self.Zone_initial = ini

class Synchronizer():
    def __init__(self, digital_model, real_database_path, start_time, end_time, generate_digital_model, copied_realDB = False, delta_t_treshold= 100):
        self.helper = Helper()
        #--- Basic Information
        self.digital_model = digital_model
        self.generate_digital_model= generate_digital_model
        self.zones_dict = {}
        self.Tnow = 0
        self.start_time = start_time
        self.end_time = end_time
        self.copied_realDB = copied_realDB
        self.delta_t_treshold = delta_t_treshold

        #--- Database
        #self.real_database = real_database
        self.real_database_path = real_database_path
        self.real_database = Database(database_path=real_database_path, event_table= "real_log", feature_usingDB= 'sync', start_time= start_time, end_time= end_time, copied_realDB= copied_realDB)        
        self.full_database = self.real_database.read_store_data_all("real_log")
        

        #--- Digital Model
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()
        
        #--- Last part id according to the digital model
        # Assuming that no parts were added into the system or removed, this assumption works fine
        # But if some part was added to the system, the sync will create repetitive part.
        # If some part were removed of the system, we're going to have it stuck in some queue.
        # Given that, ASSUMPTION: No parts are ADD or REMOVE from the system

        self.last_part_id = self.machines_vector[-1].get_last_part_id()

    def create_zones(self):
        for machine in self.machines_vector:
            #--- Basic information from the machine
            machine_name = machine.get_name()
            machine_queues_in_list = machine.get_queue_in()

            #--- create a temp Zone object
            new_zone = Zone(machine= machine, queue_list= machine_queues_in_list, digital_model= self.digital_model)

            #--- add the Zone object in the dictionary of zones
            self.zones_dict[machine_name] = new_zone

    def count_total_parts(self):
        """
        This function counts the total number of part in the system. This function is used
        to measure if there is any added or removed part.
        """
        total_number_parts = 0
        #--- Loop through each zone
        for key in self.zones_dict:
            #--- Take the zone object
            zone = self.zones_dict[key]

            #--- Add the number of parts in queue
            nparts_queue = len(zone.get_part_id_in_queue())
            total_number_parts += nparts_queue

            #--- Add the number of parts in machine
            nparts_machine = len(zone.get_part_id_in_machine())
            total_number_parts += nparts_machine
        
        #--- Return the amount of parts in simulation
        return total_number_parts


    def positioning_discovery(self):

        #--- Initial counting of parts in the system
        parts_in_system = self.count_total_parts()

        #--- Big picture after calculations
        self.helper.printer("-----------------------------------------------------------------", 'brown')
        self.helper.printer("Big picture BEFORE Sync", 'brown')
        for key in self.zones_dict:
            zone = self.zones_dict[key]
            print(f" ------------ ZONE ID: {zone.get_id()} ------------")
            print(f"Parts in Queue: {zone.get_part_id_in_queue()}")
            print(f"Part in Machine: {zone.get_part_id_in_machine()}")
        self.helper.printer("-----------------------------------------------------------------", 'brown')

        #--- Find the Positioning
        print("--------- Step by Step Sync ---------")
        for event in self.full_database:
            
            #--- Extract the important informations
            (time, machine_name, status, part_id, queue_name) = (event[0], event[1], event[2], event[3], event[4]) 

            # We just care about the events with status "Finished",
            # because this in the only moment when we subtract some part from the current
            # zone and add it to the next zone
            current_zone = self.zones_dict[machine_name]

            #--- Figure out what machine object it's
            for machine in self.machines_vector:
                if machine.get_name() == machine_name:
                    #-- Found it!
                    machine_obj = machine

            if status == "Finished":
                #--- Updated the event type
                current_zone.set_event_type("Finished")
                #--- Verify if it's the first event:
                if current_zone.get_first_zone_event() == True:
                    # It's the first event and the it was finished, so the machine had a part
                    # [OLD]current_zone.set_Zone_initial(current_zone.get_Zone_initial() + 1)
                    # already it had in the queue plus one of the machine
                    # Theorically this condition is already been done when creating the zones
                    # because now we check if the machine had a part in it.
                    pass

                #--- For the current zone a part was finished, so we increment the Out
                current_zone.addOut(part_id)
                current_zone.Mfinished(part_id)

                #--- Implement the next allocation based on queue
                current_zone.next_allocation(queue_name)

                #--- Discovery in which zone the part was putted based on the queues and machines
                for key in self.zones_dict:
                    #--- For every zone in the zone dictionary
                    zone = self.zones_dict[key]

                    #--- For every queue of a Zone
                    for queue in zone.get_queue_list():

                        #--- Found a zone if the selected next queue
                        if queue.get_name() == queue_name:
                            next_zone = zone
                
                #--- Before Assigned the part for the next zone, check if the machine is final machine ---
                if machine_obj.get_final_machine() == True:
                    # [OLD]
                    #--- Increment the ID of the new part going back to the system
                    self.last_part_id += 1
                    new_part_id = f"Part {self.last_part_id}"

                    print(f"{machine_obj.get_name()} (final machine) just finisehd a part, adding a new one: {new_part_id} to {next_zone.get_name()}")
                    
                    #--- Add to the next zone
                    next_zone.addIn(new_part_id)


                #--- Machines that are not the final machine
                else:
                    #--- For the next zone, increment the In since we're adding a part to that zone
                    next_zone.addIn(part_id)

            if status == "Started":
                #--- Set first event as false, because if it's started, it means that it took some part
                # from a Queue and we are not in the case where the first trace of the machine is finish becuase
                # it had already a part inside
                current_zone.set_first_zone_event(False)
                
                #--- Update starter counter and flags
                current_zone.Mstarted(part_id)
                current_zone.set_last_started_time(time)

                #--- Updated the event type
                current_zone.set_event_type("Started")

            #--- Counting of parts in the system
            new_parts_in_system = self.count_total_parts()

            # ------------- Verbose -------------
            self.helper.printer(f"Event - machine_name: {machine_name}, status: {status}, part_id: {part_id}, queue_name: {queue_name}", 'brown')
            for key in self.zones_dict:
                zone = self.zones_dict[key]
                print(f" ------------ ZONE ID: {zone.get_id()} ------------")
                print(f"Parts in Queue: {zone.get_part_id_in_queue()}")
                print(f"Part in Machine: {zone.get_part_id_in_machine()}")


            #--- Erro when different numbers of parts are registered in the traces
            if new_parts_in_system != parts_in_system:
                (tstr, t) = self.helper.get_time_now()
                self.helper.printer(f"[ERROR][synchronizer.py/positioning_discovery()] A different number of parts in the system was detected. Check for parts duplications or external interference!", 'red')
                self.helper.printer(f"|-- Previous number: {parts_in_system}, New number: {new_parts_in_system}", 'red')

                #--- Updated the amount of parts in the system
                parts_in_system= new_parts_in_system

                self.helper.printer(f"---- Digital Twin was killed ----", 'red')
                sys.exit()


        #--- Assign Tnow according the last event of the real log
        self.Tnow = self.full_database[-1][0]

        #--- Big picture after calculations
        self.helper.printer("-----------------------------------------------------------------", 'brown')
        self.helper.printer("Big picture AFTER Sync", 'brown')
        for key in self.zones_dict:
            zone = self.zones_dict[key]
            print(f" ------------ ZONE ID: {zone.get_id()} ------------")
            print(f"Parts in Queue: {zone.get_part_id_in_queue()}")
            print(f"Part in Machine: {zone.get_part_id_in_machine()}")        
        self.helper.printer("-----------------------------------------------------------------", 'brown')


    def sync_TDS(self):
        print("======================= Running TDS for Sync =======================")
        validator_sync = Validator(digital_model= self.digital_model, simtype= "TDS", real_database_path= self.real_database_path, start_time= self.start_time, end_time= self.end_time, copied_realDB=self.copied_realDB, generate_digital_model= self.generate_digital_model, delta_t_treshold= self.delta_t_treshold)

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

            # ========================== COMMON VARIABLES ==========================
            #--- For each Zone
            current_zone = self.zones_dict[key]
            current_NumParts = current_zone.get_NumParts()
            parts_in_queues = current_NumParts
            current_Queues_In = current_zone.get_queue_list()
            current_machine = current_zone.get_machine()

            #--- Get the ID of the parts
            #-- Parts within the queue
            parts_id_in_queues = current_zone.get_part_id_in_queue()

            # ========================== UPDATE WORKED TIME ==========================
            #-- Parts within the machine
            if len(current_zone.get_part_id_in_machine()) > 0:
                parts_id_in_machine = current_zone.get_part_id_in_machine()[0]
            else:
                parts_id_in_machine = 0

            #--- Verify if the Zone is working or not
            if current_zone.get_machine_working() == True:
                #-- Machine is working
                # So from all the parts in the Zone, I need to subtract one to have the
                # number of parts in the queues
                parts_in_queues = current_NumParts - 1

                #--- Calculate the Delta T between the last started time of the machine and
                # the current time of the real world (Tnow)

                #-- Case when the zone didn't finished the part that it already started producing
                if current_zone.get_flag_initial_working() == True:
                    Delta_T_started = self.Tnow + current_zone.get_last_started_time()
                #-- Case when the machine started a part in the middle of the simulation
                if current_zone.get_flag_initial_working() == False:
                    Delta_T_started = self.Tnow - current_zone.get_last_started_time() 
                
                #- Avoid the case when the machine is working and just received the part
                if Delta_T_started == 0: Delta_T_started = 1

                #--- Positioning a part within the working machine
                # ============= Update Model.json =============
                model_path = self.digital_model.get_model_path()
                with open(model_path, 'r+') as model_file:
                    data = json.load(model_file)
                    #--- For each machine (node)
                    for node in data['nodes']:
                        if node['activity'] == current_machine.get_id():
                            # ISSUE #278: Sometimes Sync was not updating, maybe the flag initial was being updated wrong somewhere
                            # because it came from the digital model, and we're running Sync very fast or even some change in
                            # validation that change this property of the machine object

                            # [OLD]
                            node['worked_time'] = (Delta_T_started, parts_id_in_machine) 
 
                            #---- Write Back the Changes
                            # Move the file pointer to the beginning of the file
                            model_file.seek(0)
                            # Write the modified data back to the file
                            json.dump(data, model_file)
                            # Truncate any remaining data in the file
                            model_file.truncate()

                            break

            #--- If the Zone is not working, assign zero anyways to clear previous work
            if current_zone.get_machine_working() == False:
                # ============= Update Model.json =============
                model_path = self.digital_model.get_model_path()
                with open(model_path, 'r+') as model_file:
                    data = json.load(model_file)
                    #--- For each machine (node)
                    for node in data['nodes']:
                        if node['activity'] == current_machine.get_id():
                            node['worked_time'] = 0
 
                            #---- Write Back the Changes
                            # Move the file pointer to the beginning of the file
                            model_file.seek(0)
                            # Write the modified data back to the file
                            json.dump(data, model_file)
                            # Truncate any remaining data in the file
                            model_file.truncate()

                            break

            # ========================== Positioning of Parts in Queues ==========================
            #--- Loop through the Queues to allocate the parts
            for queue in current_Queues_In:
                queue_len = queue.get_capacity()

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
                        #-- OLD without the ID, just quantity
                        #data['initial'][queue.get_id() - 1] = parts_to_allocate

                        #-- NEW with part id
                        data['initial'][queue.get_id() - 1] = parts_id_in_queues
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
                        #-- OLD without the ID, just quantity
                        #data['initial'][queue.get_id() - 1] = parts_to_allocate

                        data['initial'][queue.get_id() - 1] = parts_id_in_queues
                        #=====================================

                        # Move the file pointer to the beginning of the file
                        model_file.seek(0)
                        # Write the modified data back to the file
                        json.dump(data, model_file)
                        # Truncate any remaining data in the file
                        model_file.truncate()
                    
                    # Since the number of parts to positioned is less than what i can, i'm done
                    break

            # ========================== Updated Allocation Counter ==========================
            current_allocation_counter = current_zone.get_allocation_counter()
            if current_allocation_counter != None:
                zone_machine = current_zone.get_machine()
                machine_id = zone_machine.get_id()

                # ============= Update Model.json =============
                model_path = self.digital_model.get_model_path()
                with open(model_path, 'r+') as model_file:
                    data = json.load(model_file)

                    for node in data['nodes']:
                        if node['activity'] == machine_id:

                            #=====================================
                            node['allocation_counter'] = current_allocation_counter
                            #=====================================

                            # Move the file pointer to the beginning of the file
                            model_file.seek(0)
                            # Write the modified data back to the file
                            json.dump(data, model_file)
                            # Truncate any remaining data in the file
                            model_file.truncate()


    def show(self):
        
        #--- Running Self Validation
        """
        print("=========== Self Verification (Digital-Based) ===========")
        for key in self.zones_dict:
            current_zone = self.zones_dict[key]
            zone_NumParts = current_zone.self_validation()
        print("=========================================")
        """
        #--- Create vectors to extract status from Sync (and send to API)
        # (don't need to be a dictionary because the ID of the zones)

        machines_status = []
        queues_status = []

        #--- Print the Zones Occupation
        for key in self.zones_dict:
            current_zone = self.zones_dict[key]
            zone_NumParts = current_zone.calculate_parts()
            machine_working = current_zone.get_machine_working()
            indicator = current_zone.get_zoneInd()
            #print(f"[{current_zone.get_name()}] NumParts = {zone_NumParts}, Machine Working = {machine_working}, Zone Indicador = {indicator}")

            #--- Update Status vector
            machines_status.append(machine_working)
            queues_status.append(zone_NumParts)

        #--- Return the Status Vector
        return (machines_status, queues_status)
    
    def run(self, repositioning = True):
        #--- Create the Zones for the Initial Conditions
        self.create_zones()

        #--- Find the Positioning for the parts in the real log
        self.positioning_discovery()

        #--- Run the Trace Driven Simulation
        #self.sync_TDS()

        #--- Calculate the Indicator
        #self.sync_indicator()

        #--- Aligment (re-positioning)
        if repositioning == True:
            #--- Change the positioning of the parts in the json model
            self.sync_aligment()

            #--- Change the allocation counter of the branching machine in the json model
            #self.digital_model.changing_allocation_counter()

        #--- Show the results
        (machine_status, queue_status) = self.show()

        #--- Return Status Vectors
        return (machine_status, queue_status)