import simpy
import json
import matplotlib.pyplot as plt

#--- Import simulation components
from .components import Part
from .components import Machine
from .components import Queue
from .components import Generator
from .components import Terminator
from .components import Conveyor
from .components import Branch

#--- Importing Database components
from .interfaceDB import Database
from .helper import Helper

#--- Reload Package

import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.components)
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)
# This is different from when you're importing the package direct because here the module has the same
# name as the library, so we start importing from the library root for the software understand that we are 
# importing the folder and not the library

#--- Class Model
class Model():
    def __init__(self, name, model_path, database_path, initial= False, until= None, part_type= "A", loop_type= "closed", maxparts = None, targeted_part_id= None, targeted_cluster= None):
        #-- Main Model Properties
        self.name = name
        self.model_path = model_path
        self.env = simpy.Environment()
        self.helper = Helper()

        #--- Stop conditions
        self.until = until
        self.exit = self.env.event()
        self.maxparts = maxparts
        self.targeted_part_id = targeted_part_id
        self.targeted_cluster = targeted_cluster

        #-- Database Properties
        self.database_path = database_path
        self.event_table = "digital_log"
        self.Database = Database(self.database_path, self.event_table)
        
        #-- Flags and Secondary Properties
        self.loop_type = loop_type       
        self.part_type = part_type       
        self.initial = initial
        self.last_part_id = 0
        self.all_part_in_model = []


        #--- Vectors to store main components
        # Create an empty list to store Machine objects
        self.machines_vector = []
        # Create an empty list to store Queue objects
        self.queues_vector = []
        # Initial Part of the Model
        self.initial_parts = []
        # Link the Terminator
        self.terminator = Terminator(env= self.env, loop_type= "closed")

    # ==================== SETTING FUNCTIONS ====================

    # ----- Link the Queues with the Machines -----
    def queue_allocation(self):
        """
        Allocate each queue for the right machine base on the 
        arcs configurations from the json model
        """
        #Loop through each queue
        for queue in self.queues_vector:
            current_links = queue.get_arc_links()

            #Indentify the starting and ending point of the arc (minos 1 to match with python notation)
            arc_start = current_links[0] - 1
            arc_end = current_links[1] -1 

            #Arc start point (going out of the previous machine) -> Queue Out
            self.machines_vector[arc_start].add_queue_out(queue) #add current queue

            #Arc endind point (going in of the next machine) -> Queue In
            self.machines_vector[arc_end].add_queue_in(queue) #add current queue      
    
    # ----- Allocate the initial parts into the Queues ----- 
    def initial_allocation(self):
        """
        Allocate the Working in Progress (WIP) parts of the beginning 
        of the simulation in each respective queue
        """
        with open(self.model_path) as json_file:
            # Load the json data
            data = json.load(json_file)

        """
            #### OLD: before syncing be assigning the ids
            #Create the initial parts
            part_id = 1
            for n_queues in range(len(data['initial'])):
                for n_parts in range(data['initial'][n_queues]):
                    self.initial_parts.append(Part(id= part_id, type= self.part_type, location=n_queues, creation_time=0))
                    part_id += 1
            
        generator_initial = Generator(env= self.env, loop_type="closed", part_vector= self.initial_parts, queue_vector= self.queues_vector)
        self.queues_vector = generator_initial.allocate_part()
        """

        #--- New Implementation with the IDs already assigned
        #--- For each queue look for assigned part ids
        queue_index = 0
        for queue_parts in data['initial']:
            #--- For each part within the queue being analyzed
            try:
                for part_in_queue in queue_parts:
                    #--- Extract the part id
                    part_name = part_in_queue
                    part_id = int(''.join(filter(str.isdigit, part_name)))

                    #--- Create the Part object
                    part_created = Part(id= part_id, type= self.part_type, location= queue_index, creation_time=0)

                    #--- Assign the created parts in the vector for initial parts (not used anymore)
                    self.initial_parts.append(part_created)

                    #--- Find the right queue according to the index
                    queue = self.queues_vector[queue_index]

                    #--- Assign the part into the queue
                    queue.put(part_created)

                    #--- Add the part to the global vector of parts
                    self.all_part_in_model.append(part_created)
                    
            except TypeError:
                print(f"[ERROR][digital_model.py/initial_allocation()] Initial conditions of Queue {queue_index} is not a vector!")
                print("Assign Queue as empty...")


            #--- Update the queue_index to go for the next queue
            queue_index += 1

    # ----- Find parts alreayd working within machine -----
    def discovery_working_parts(self):

        #--- Open the json file
        with open(self.model_path) as json_file:
            #--- Import json data
            data = json.load(json_file)

            #--- For each node in the simulation
            for node in data['nodes']:
                # --- Check if there is any initial part
                if node["worked_time"] != 0:
                    #-- Create the initial part
                    ## not sure if location matters here ##
                    ## part created in the past in relation with the current simulation ##
                    # ASSUMPTION: In terms of RCT, it's better to just consider the remaining time for production
                    # So, consider creation time= 0...
                    
                    #--- Get the part id assigned
                    part_name = node["worked_time"][1]
                    part_id= int(''.join(filter(str.isdigit, part_name)))
                    initial_part = Part(id= part_id, type= "A", location= None, creation_time= 0) 

                    #--- Get the right machine
                    machine = self.machines_vector[(node["activity"] - 1)]

                    #--- Assign the part to the rigth machine
                    machine.set_initial_part(initial_part)

                    #--- Add the part to the global vector of parts
                    self.all_part_in_model.append(initial_part)

                    #--- Get the worked time value
                    if type(node['worked_time']) == list:
                        worked_time= node['worked_time'][0]
                    else:
                        worked_time = node['worked_time']

                    #--- Assign the Worked Time into the machine
                    machine.set_worked_time(worked_time)

    # ----- Find the part with highest id -----
    def find_last_part_id(self):
        """
        This function looks through all the parts in the simulation and searches
        for the part with the highest ID to be the last_part_id.
        """
        #--- Started id
        highest_id = 0
        
        #--- For all the parts in the model
        for part in self.all_part_in_model:
            part_id = part.get_id()

            #--- If the current part id is higher than the last highest value, we have a new high value
            if part_id > highest_id:
                highest_id = part_id

        #--- Assign the last part id with the highest value
        #self.last_part_id = int(''.join(filter(str.isdigit, highest_id)))
        self.last_part_id = highest_id

        #--- Assign the last part id to all the machines
        for machine in self.machines_vector:
            machine.set_last_part_id(self.last_part_id)

    # ----- Merge overlaping queues in the input of machines -----
    def merge_queues(self):
        """
        Function to merge existing queues in the input of a machines.
        """

        # 1) Look through all the input queues of all the machines and stop when find
        # a machine with multiple queues in the input.

        # 2) Record the id of thoses queues and replace it (summing up the properties)
        # for a new merged queue

        # 3) With the IDs in hands, look through all the output queues of the machines
        # and if find one of the previous selected queues, replace it for the merged queue

        #--- Loop through all the machines to MERGE input queues
        queue_to_merge_all = []
        merged_queues_all = []

        for machine in self.machines_vector:
            #--- Machine with multiple queues
            if len(machine.get_queue_in()) > 1:
                #--- Create the vectors with Queues to be merge
                queues_to_merge = machine.get_queue_in()
                queue_to_merge_all.append(queues_to_merge)
        
                #--- Properties of the selected queues 
                capacity = 0 # Queue capacity
                merged_id = "merged_"
                #--- ASSUMPTION: In a merging queue, the incoming conveyors have the same transportation time
                transp_time = queues_to_merge[0].get_transp_time()

                #--- Loop through the selected queues to merge to update properties
                for queue in queues_to_merge:
                    #-- Increment Queue Capacity
                    capacity += queue.get_capacity()
                    merged_id += str(queue.get_id())


                # ----- Create Merged Queue -----
                Merged_Queue = Queue(env= self.env, id= merged_id, capacity= capacity, transp_time= transp_time)
                merged_queues_all.append(Merged_Queue)
                #-- Set the new merged queue as list in the Queue In
                machine.set_queue_in([Merged_Queue])
        
                #--- Loop through the output queues to replace for the merged queue
                for machine_out in self.machines_vector:
                    
                    #--- For each machine, verify if the one of the output queues is between 
                    # one of the selected queues
                    new_queues_out = []
                    
                    for queue_out in machine_out.get_queue_out():
                        #-- Keep adding queues out in a new vector
                        new_queues_out.append(queue_out)
                        #--- compare the queue with all the selected queues
                        for queue_merged in queues_to_merge:
                            #-- This machine has an output queue that was merged
                            if queue_out.get_name() == queue_merged.get_name():
                                # Remove this existing queue and replace for the new merged queue
                                #-- Since this queue was merged, we remove the last added
                                new_queues_out.pop()
                                #-- Add the new queue
                                new_queues_out.append(Merged_Queue)
                    
                    #--- Finished checking the queues out of this machines, add the updated queues out
                    machine_out.set_queue_out(new_queues_out)


        #--- From now all the machines should have the correct queues, so update the queue vector
        updated_queues = []
        for machine in self.machines_vector:
            #--- each machine has just one queue input now
            for queue in machine.get_queue_in():
                updated_queues.append(queue)
        
        #--- Update queue vector
        self.queues_vector = updated_queues

        #--- Update Queues ID
        for i in range(len(self.queues_vector)):
            self.queues_vector[i].set_id(i+1)
    
    # ----- Identify the clusters and assign into the machines -----
    def cluster_discovery(self):
        """
        Discovery the cluster of each machine and assign it for the
        related machine. Is important for a machine to know in each 
        cluster it belongs for Trace Driven Simulations that starts 
        with parts in the middle of the layout, such as inside of 
        working machines or not in the first queue.
        """
        # ASSUMPTION: The first machines is always not parellized

        for machine in self.machines_vector:
            #--- Machine's output queues
            out_queues = machine.get_queue_out()
            in_queues = machine.get_queue_in()

            #--- First machine, first cluster
            if machine.get_id() == 1:
                machine_cluster = 1
                machine.set_cluster(machine_cluster)

                #-- Increment for the next cluster
                next_cluster = machine_cluster + 1
                
                #-- For each out Queue, set the "next" cluster
                for queue in out_queues:
                    queue.set_cluster(next_cluster)
            
            #--- Not first, cluster checking by Queues
            else:
                # 1. It first look to the property of its queue in (where it has their own cluster counter)
                # 2. increment the cluster counter
                # 3. Look for my output queues and assigned the queues as the cluster counter

                #--- If the machine is not the first one, the cluster
                # is given by the Queue cluster of the input
                for queue in in_queues:
                    #--- Take the cluster from the machine queue in
                    machine_cluster = queue.get_cluster()

                #--- Set the machine cluster
                machine.set_cluster(machine_cluster)
                
                #-- Increment for the next cluster
                next_cluster = machine_cluster + 1
                
                #-- For each out Queue, set the "next" cluster
                for queue in out_queues:
                    queue.set_cluster(next_cluster)
    
    # ----- Identify the branching machines -----
    def branch_discovery(self):
        """
        ## Description
        This fucntions is able to discovery where are the branch points in the model,
        create an object for each branch point and assigned it to matching machine.
        To do so, the function uses self.machines and creates the vector with the branch
        objects (self.branches). IMPORTANT: This Function should be implemented after
        the machine object is completedly finished (including the assign of the conveyors).
        
        #### TO-DO:
        1) Loop through the machines
            2) If a machine has multiple conveyors out (or queues out):
                3) This is a branching machine
                4) Create a Branch Object
                5) Assign the object to the machine 
        """
        #--- Global Branch parameters
        branch_id_counter = 1
        self.branches = []

        #--- Loop through the machines
        for machine in self.machines_vector:
            #--- If a machine has multiple conveyors out-> Branching machine
            if len(machine.get_conveyors_out()) > 1:
                #--- Get some properties from the branching machine
                machine_conveyors_out = machine.get_conveyors_out()
                machine_queues_in = machine.get_queue_in()

                #--- CREATE Branch point
                new_branch = Branch(id= branch_id_counter, branch_conveyors= machine_conveyors_out, branch_machine= machine, branch_queue_in=machine_queues_in)

                #--- add branch in the machine
                machine.set_branch(new_branch)

                #--- add branch in the branch vector
                self.branches.append(new_branch)

                #--- Increase branch counter
                branch_id_counter += 1
    
    # ----- Create conveyors objects -----
    def create_conveyors(self):
        """
        Create conveyor based on the existing queues and assign them
        to the related machine. This is important because the machine will 
        first add the part in the conveyor and the conveyor (after the transportation time)
        will add the part to the queue related to the conveyor.
        """
        #--- Create a global vector of conveyors
        self.conveyors_vector = []
        #--- For each machine, assign the right conveyors
        for machine in self.machines_vector:
            #--- Each queue out is a conveyor to be use by the machine
            machine_conveyors = []
            for queue in machine.get_queue_out():
                #--- Get the transportation time stored in the queue
                transp_time = queue.get_transp_time()

                #--- Create the Conveyor
                current_conveyor = Conveyor(env= self.env, transp_time= transp_time, queue_out= queue)

                #--- Add the current conveyor to the conveyor list of the machine
                machine_conveyors.append(current_conveyor)

                #--- Add the conveyor in the global vector as well
                self.conveyors_vector.append(current_conveyor)

            #--- After creating the conveyors for each queue out of this machine
            #--- Assign the conveyor vector for the machine
            machine.set_conveyors_out(machine_conveyors)

        #--- Assign the Conveyors In for a machine by matching conveyors queue and machine queue in
        # For each machine ...
        for machine in self.machines_vector:
            # Look through all the existing conveyors ...
            for conveyor in self.conveyors_vector:
                # Find a conveyor that is delivering to the machine queue in
                convey_queue = conveyor.get_convey_queue()
                machine_queue_in = machine.get_queue_in()[0]
                machine_conveyors_in = []

                # Check if they have the same queue
                if convey_queue.get_id() == machine_queue_in.get_id():
                    machine_conveyors_in.append(conveyor)
                
            machine.set_conveyors_in(machine_conveyors_in)

    # ----- Stopd condition in a specific machine -----
    def setting_stop_machines(self):
        """
        For the specific selected machine (targeted_cluster) specify what is the id of the
        part that the machine shoudl stop when it arrives. 
        """
        #--- For each existing machine
        for machine in self.machines_vector:
            #--- If the machines has the same ID of the selected machine
            if machine.get_cluster() == self.targeted_cluster:
                #--- Tells for that specific machine for which part id it should stop
                machine.set_stop_for_id(self.targeted_part_id)
    
    # ----- Getting and updating the model with last allocation counter -----
    def changing_allocation_counter(self):
        """
        This function is used after a simulation is runned. The goal here is to get the last
        alternating policy used by branching machines and set it for that machine. Thus, in this way,
        when the machine starts the simulation again it's going to remember what was the last selected machine.
        """
        #--- For each branching machine (where the allocation policy make sense)
        for branch in self.branches:
            machine = branch.get_branch_machine()

            #--- Get the last allocation counter of that machine
            last_allocation_counter = machine.get_allocation_counter()

            #--- Set in the model this allocation for that machine
            #--- Open the json file
            with open(self.model_path, 'r+') as model_file:
                #--- Import json data
                data = json.load(model_file)
                for node in data['nodes']:
                    #--- Macth the node with the current machine
                    if node['activity'] == machine.get_id():
                        # Found the right machine
                        node['allocation_counter'] = last_allocation_counter

                        #---- Write Back the Changes
                        # Move the file pointer to the beginning of the file
                        model_file.seek(0)
                        # Write the modified data back to the file
                        json.dump(data, model_file)
                        # Truncate any remaining data in the file
                        model_file.truncate()
    
    # ----- Setting the last allocation counter for branching machines -----
    def setting_allocation_counter(self):
        """
        This function is used before the simulation. It reads the json model and updated
        for branching machine the last value used in the alternation policy for allocation counter
        """
        #--- For each branching machine (where the allocation policy make sense)
        for branch in self.branches:
            machine = branch.get_branch_machine()

            #--- Open the json file
            with open(self.model_path) as model_file:
                #--- Import json data
                data = json.load(model_file)
                for node in data['nodes']:
                    #--- Macth the node with the current machine
                    if node['activity'] == machine.get_id():
                        # Found the right machine
                        #-- Get the counter from the model
                        allocation_counter = node['allocation_counter']
                        
                        #-- Set the counter into the machine
                        machine.set_allocation_counter(allocation_counter)


    # =======================================================

    # ================== TRANSLATOR ==================
    def model_translator(self):
        """
        THE model trasnlator
        """
        #--- Open the json file
        with open(self.model_path) as json_file:
            #========================= Setup =========================
            #--- Import json data
            data = json.load(json_file)

            """ OLD: BEFORE ID ASSIGNED BY SYNC
            #--- Load the json data
            
            if self.initial == True:
                #--- Calculate the number of part initially in the model
                for i in range(len(data['initial'])):
                    self.last_part_id += data['initial'][i]
            """
            
            #====================================================================


            #========================= Create Machines =========================
            # Loop through the nodes in the json data
            """ OLD: BEFORE ID ASSIGNED BY SYNC
            for node in data['nodes']:
                # --- Check if there is any initial part
                if node["worked_time"] != 0:
                    #-- Update part ID
                    self.last_part_id += 1

                    #-- Create the initial part
                    ## not sure if location matters here ##
                    ## part created in the past in relation with the current simulation ##
                    # ASSUMPTION: In terms of RCT, it's better to just consider the remaining time for production
                    # So, consider creation time= 0...
                    initial_part = Part(id= self.last_part_id, type= "A", location= None, creation_time= 0) # TODO: Create the part id according to the tuple of worked time
                
                else:
                    initial_part = None
            
            """
            for node in data['nodes']:
                # Create a new Machine object for each node and add it to the list
                self.machines_vector.append(Machine(env= self.env, id= node['activity'],freq= node['frequency'],capacity= node['capacity'], 
                process_time= node['contemp'], database= self.Database, cluster= node['cluster'],
                terminator= self.terminator, loop= self.loop_type, exit= self.exit, maxparts= self.maxparts,
                targeted_part_id= self.targeted_part_id, until= self.until))
            
            self.machines_vector[-1].set_final_machine(True)
            #====================================================================


            #========================= Create Queues =========================
            # Loop through the arcs in the json data
            queue_id = 0
            for arc in data['arcs']:
                queue_id += 1
                # Create a new Queue object for each arc and add it to the list
                self.queues_vector.append(Queue(env= self.env, id= queue_id, arc_links= arc['arc'],
                capacity= arc['capacity'],freq= arc['frequency'],transp_time= arc['contemp']))
            #====================================================================


            #========================= Link Queues & Machines ===================
            #--- Allocate the Queues for each machine
            self.queue_allocation()
            #====================================================================

        #========================= Merge Input Queues =========================
        #--- Merge existing Input Queue and re-assign Output Queues
        self.merge_queues()
        #======================================================================

        #========================= Initial Allocation ===================
        if self.initial == True:
            #--- Allocate the initial Parts for each Queue
            self.initial_allocation()

        # --- Discover parts already being processed by machines and create them 
        self.discovery_working_parts()

        # --- Discover the last part id and assign to the machines
        self.find_last_part_id()

        
        #====================================================================


        #========================= Cluster Discovery =========================
        #--- Set the cluster for each machine
        self.cluster_discovery()
        #====================================================================

        #========================= Conveyors Assigning =========================
        #--- Create and Assing the conveyor for each Machine base on the Queues
        self.create_conveyors()
        #========================================================================

        #========================= Branch Discovery =========================
        #--- Discovery Branching machines, create Branch object and assigned it
        self.branch_discovery()
        #=====================================================================

        #========================== Setting Targeted Part ID ==================
        # --- Setting the part id to stop the simulation for the right machine
        self.setting_stop_machines()
        #======================================================================

        #========================== Setting Allocation Counter ================
        # --- Setting the last allocation counter for branching machines
        self.setting_allocation_counter()
        #======================================================================

    # ================================================

    # =================== RUNNING ===================
    def run(self):
        """
        Run the digital model simulation. Here is where the stop conditions and 
        simpy processes are set.
        """
        print("### ============ Simulation Started ============ ###")
        # ==== DataBase Management ====
        #-- Clean database
        self.Database.clear(self.event_table)

        #-- Initialize digital_log table
        self.Database.initialize(self.event_table)

        #--- Initialize each machine process
        for machine in self.machines_vector:
            self.env.process(machine.run())

        #--- Initialize each conveyor process
        for conveyor in self.conveyors_vector:
            self.env.process(conveyor.run())

        #--- Run the Simulation
        if self.loop_type == "closed":
            if self.maxparts != None or self.targeted_part_id != None:
                self.env.run(until= self.exit)
            else:
                self.env.run(until= self.until)
        elif self.loop_type == "open":
            self.env.run(until= self.exit)

        #--- Print the database with all the events
        self.Database.read_all_events(self.event_table)

        print("### ============ Simulation Done ============ ###")

        # Note: Since we run multiple internal simulations, like TDS and qTDS, we can not
        # change the model json for ever run. Only Sync and Model update should be allowed
        # to change the model!

        #--- Getting the last allocation counter of the branching machines and updating the json file
        #self.changing_allocation_counter()
    # ===============================================

    # ================== ANALYSES ==================

    # ----- Calculate Cycle Time and Plot -----
    def analyze_results(self, options = ["all"]):
        """
        Get the parts finalized and stored in the Terminator and make some
        analyses such as cycle time, throughput and also plot some graphs
        """
        #--- Get the finished Parts and each Time
        parts_finished = self.terminator.get_all_items()

        if len(parts_finished) >= 3:
            #--- Number of finished parts in the simulation
            number_parts = len(parts_finished)

            #--- create empty lists
            parts_finished_time = []
            parts_finished_id = []
            parts_finished_id_ASIS = []
            parts_creation_time = []

            #---Create the list with parts ID
            for part in parts_finished:
                parts_finished_id.append(part.get_id())
                parts_finished_id_ASIS.append(part.get_id())
            
            #--- Sort the list in ascending
            parts_finished_id.sort()

            #--- Adjust the sort of other variables following the ID sort
            for id in parts_finished_id:
                for part in parts_finished:
                    if part.get_id() == id:
                        parts_finished_time.append(part.get_termination())
                        parts_creation_time.append(part.get_creation())
                        break
                

            print("================ Running Analysis ================")
            print(f"Number of Parts finished: {len(parts_finished)}")
            print(f"Total time of Simulation: {parts_finished[-1].get_termination()}")
            #print(f"List of IDs (AS IS): {parts_finished_id_ASIS}")
            #print(f"List of IDs (sorted): {parts_finished_id}")

            def plot_finished():
                plt.plot(parts_finished_id, parts_finished_time, '-o')
                plt.title("Lead Time per Part ID")
                plt.xlabel("Parts ID")
                plt.ylabel("Finish Time")
                plt.show()
                plt.savefig(f"figures/{self.name}_plot_finished.png")

            #-- Function to calculate the throughput
            def throughput():
                th = number_parts / parts_finished[-1].get_termination()
                print(f">>> System Throughput: {th} [parts / time unit] ")

                return th
            #-- Function to calculate the average cycle time
            def avg_cycle_time():
                sum_ct = 0
                parts_cycle_time = []
                for i in range(number_parts):
                    #-- calculate individual CT
                    parts_cycle_time.append(parts_finished_time[i] - parts_creation_time[i])
                    #-- Sum up every CT
                    sum_ct += parts_cycle_time[i]

                #-- Print cycle time of each part
                #print(">>> Cycle Time of each part:")
                #print(parts_cycle_time)
                    
                #-- Maximum and Minimum CT
                max_CT = max(parts_cycle_time)
                min_CT = min(parts_cycle_time)
                print(f"- Maximum Cycle Time: {max_CT}")
                print(f"- Minimum Cycle Time: {min_CT}")

                #-- Avereage Cycle Time
                avg_CT = sum_ct / number_parts
                print(f">>> Average system cycle time: {avg_CT} [time unit]***")

                #-- Plot the Cycle Time for each Part
                plt.plot(parts_finished_id,parts_cycle_time, '-x')
                plt.title("Cycle Time per Part ID")
                plt.xlabel("Parts ID")
                plt.ylabel("Cycle Time")
                plt.show()
                plt.savefig(f"figures/{self.name}_cycle_time.png")           

                return avg_CT

            #--- Running everything
            plot_finished()
            avg_cycle_time()
            throughput()
        
        else:
            self.helper.printer("[WARNING][digital_model.py / analyze_result()] No parts finished in the simulation or less than 2", "yellow")
        
    
    # ----- Calculate the RCT from the previous simulation -----
    def calculate_RCT(self, part_id_selected= None, batch= None):
        """
        DESCRIPTION:
        Function to calculate the RCT of a part or a batch for a given scenario
        (current status of the model.json). The function uses the results of the
        simulation stored in the Terminator. If part_id is given the function 
        calculate the RCT for the id of the part given. If batch is given, the 
        function calculate the amount of time (RCT) needed to finished the first
        number of parts given. The function return the RCT. 
        TO-DO:
        # 1) Indentify if it's to calculate for a part or for a batch
        # 2) If part, search in the Terminator the part given by the id
            # 2.1) return the cycle time needed for that part
        # 3) If batch, count in the terminator until achive the requested number of
        parts. Take as RCT the cycle time of the last part

        NOTES:
        # n1) We don't need to stop the simulation when the selected part is finish, because
        since we're calculating the CT for a specifc time we just need to run the simulation for
        the amount of parts of the ID selected plus some error. This is adjust outside of the RCT 
        calculation

        Backlog:
        # b1) Before batch: Maybe the user will like to know the amount of time need
        to finish a certain number of parts after another amount of parts were already
        finished. Thus, the RCT of batch after previous batch is done. So let's say
        I want to calculate the RCT to produce 7 parts, after being finished with 3 parts.
            # b1.1) For that we would need to receive this new variable before_batch and
            take from starts count in the terminator only after the before_batch.
        
        # b2) Run the simulation precisely until the resquested part(s) is finished, not more than
        that. Thus, reducing the computational waste
        """
        #--- Get the finished Parts in the ordered that was finished
        parts_finished = self.terminator.get_all_items()
        
        #--- Part ID calculation resquested
        if part_id_selected != None and batch == None:
            print(f"> Predicting RCT for Part {part_id_selected}...")
            #--- Loop through the finalized parts
            for part in parts_finished:
                #--- Check if the current part is the selected part
                if part.get_id() == part_id_selected:
                    part_RCT = part.get_CT()
                    print(f"> RCT for Part {part_id_selected}: {part_RCT}")
                    return part_RCT
                
            print(f"[ERROR] Part {part_id_selected} not fund as finished in the simulation")

        #--- Bacth calculation resquested
        if part_id_selected == None and batch != None:
            print(f"> Predicting RCT for Batch of {batch} parts...")
            batch_parts = []
            #--- Loop until get the amount needed of parts
            for i in range(len(parts_finished)):
                #--- Add parts in the batch 
                batch_parts.append(parts_finished[i])

                #--- Stop adding when achive the desire amount
                if (i+1) == batch: # i starts in 0, batch starts in 1
                    last_part = batch_parts[-1]
                    last_part_RCT = last_part.get_CT()

                    #--- Return the batch RCT and the batch itself
                    print(f"> RCT for Batch of {batch} parts: {last_part_RCT}")
                    print(f"> Parts in the batch:")
                    for part in batch_parts:
                        print(f"|-- {part.get_name()}")
                    return (last_part_RCT)

            print(f"[ERROR] Number of parts in batch higher than the number of parts simulated")
    # ==============================================

    # ================= GETS =======================
    def get_model_components(self):
        return (self.machines_vector, self.queues_vector)
    def get_model_database(self):
        return self.Database
    def get_model_path(self):
        return self.model_path
    def get_branches(self):
        return self.branches
    def get_all_parts(self):
        self.parts_vector = []
        for queue in self.queues_vector:
            parts_in_queue = queue.get_all_items()
            for part in parts_in_queue:
                self.parts_vector.append(part)
        return self.parts_vector
    def get_model_constrains(self):
        return (self.until, self.maxparts, self.targeted_part_id, self.targeted_cluster)
    # ==============================================

    # ================= SETs =================
    def set_targeted_part_id(self, value):
        self.targeted_part_id = value
    def set_targeted_cluster(self, value):
        self.targeted_cluster= value

    def verbose(self):
        print(f"==========  Reading the Model: {self.name}  ==========")


        print(f"===> Big Picture")
        print(f"Total number of Machines: {len(self.machines_vector)}")
        print(f"Total number of Queues: {len(self.queues_vector)}")
        print()

        
        print("===>Detailed view of Queues:")
        for queue in self.queues_vector:
            queue.verbose()
        print()
        
        
        print("===>Detailed view of Machines:")
        for machine in self.machines_vector:
            machine.verbose()




