#--- Common Libraries
import simpy
import sys

#--- Import Features
from .helper import Helper


#--- Import distributions
from scipy.stats import norm
from scipy.stats import expon
from scipy.stats import lognorm


class Part():
    def __init__(self, id, type, location, creation_time, termination_time = None, ptime_TDS = None, part_queue = None):
        self.helper = Helper()
        self.id = id
        self.name = "Part " + str(self.id)
        self.type = type
        self.location = location
        self.creation_time = creation_time
        self.termination_time = termination_time

        #--- (quasi) Trace Driven Simulation (qTDS or TDS)
        self.ptime_TDS = ptime_TDS # process time for Trace Driven Simulation
        self.finished_clusters = 0
        self.part_queue = part_queue

        #--- Conveyor
        self.convey_entering_time = None
        self.branching_path = None

    def quick_TDS_fix(self, current_cluster):
        try:
            #--- Count the number of theoretical finished clusters
            finished_clusters = current_cluster - 1
            #--- create a new vector with zero for the finished clusters
            new_ptime_TDS = [0] * finished_clusters + self.ptime_TDS
            print(f"new_ptime_TDS= {new_ptime_TDS}")
            #--- Updated old vector with the new vector
            self.ptime_TDS = new_ptime_TDS
        except TypeError:
            pass

    def calculate_CT(self):
        self.CT = self.termination_time - self.creation_time
        

    
    #------- Get methods -------
    def get_name(self):
        return self.name
    def get_id(self):
        return self.id
    def get_type(self):
        return self.type
    def get_location(self):
        return self.location
    def get_creation(self):
        return self.creation_time
    def get_termination(self):
        return self.termination_time
    
    def get_all_ptime_TDS(self):
        return self.ptime_TDS
    def get_ptime_TDS(self, cluster):
        try:
            return self.ptime_TDS[cluster]
        except:
            print(f"In {self.name}, Trying to get process time from TDS traces of the cluster {cluster + 1}, but the part don't have traces for that cluster!")
            print(f"Printing existing traces for each cluster:")
            print(f"ptime_TDS: {self.get_all_ptime_TDS()}")
            return False
            
    def get_finished_clusters(self):
        return self.finished_clusters
    def get_part_queue(self):
        return self.part_queue
    
    def get_convey_entering_time(self):
        return self.convey_entering_time
    def get_CT(self):
        self.calculate_CT()
        return self.CT
    def get_branching_path(self):
        return self.branching_path
    #------------------------------


    #------- Set Methdos -------
    def set_id(self, id):
        self.id = id
    def set_type(self, type):
        self.type = type
    def set_location(self, location):
        self.location = location
    def set_termination(self, termination_time):
        self.termination_time = termination_time
    def set_finished_clusters(self, finished_cluster):
        self.finished_clusters = finished_cluster
    def set_ptime_TDS(self, ptime_TDS):
        self.ptime_TDS = ptime_TDS
    def set_convey_entering_time(self, time):
        self.convey_entering_time = time
    def set_branching_path(self, branching_path):
        self.branching_path = branching_path
    def set_part_queue(self, queue):
        self.part_queue = queue
    #------------------------------

class Machine():
    def __init__(self, env, id, process_time, capacity, terminator, database, worked_time= 0,
        last_part_id=None, queue_in= None, queue_out= None, conveyors_out = None, blocking_policy= "BBS", 
        freq= None, cluster= None, final_machine = False, loop = "closed", exit = None, simtype = None, 
        ptime_qTDS = None, maxparts= None, initial_part= None, targeted_part_id= None, until= None):
        
        #-- Helper
        self.helper = Helper()

        #-- Main Properties
        self.env = env
        self.id = id
        self.name = 'Machine '+str(id)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.process_time = process_time #("dist_name", param_A, param_B, param_C)
        self.terminator = terminator

        #-- Secundary Proporties
        self.capacity = capacity
        self.blocking_policy = blocking_policy     
        self.freq = freq
        self.loop = loop
        
        #-- Flags and Counters Properties
        self.final_machine = final_machine
        self.allocated_part = False
        self.new_part = False
        self.flag_finished = False
        self.flag_stop_for_id = False
        self.current_state = "Idle"
        self.queue_to_get = None
        self.queue_to_put = None
        self.part_in_machine = None
        self.counter_queue_in = 0
        self.counter_queue_out = 0
        self.waiting = 1
        self.last_part_id = last_part_id # variable assigned with datab from part_vector
        self.exit = exit
        self.maxparts = maxparts
        self.working = False
        self.part_started_time = self.env.now
        self.targeted_part_id = targeted_part_id
        self.until = until # just for timeout

        #--- Allocation
        self.allocation_counter = 0
        #self.allocation_policy= "first"
        self.allocation_policy= "alternated"
        #-- Parts Selected Branch Queues
        self.parts_branch_queue= None

        #--- Save the old policy before becoming a branching
        self.old_policy = self.allocation_policy
        self.conveyors_out = conveyors_out
        self.conveyors_in = None

        #-- Database Properties
        self.database = database

        #--- (quasi) Trace Drive Simulation (TDS or qTDS)
        self.simtype = simtype
        self.ptime_qTDS = ptime_qTDS
        self.finished_parts = 0
        self.validator = None

        #--- Initial part already being processed
        self.worked_time = worked_time
        self.initial_part = initial_part
        self.cluster = cluster
        if self.worked_time != 0:
            #-- Part ready to be processed
            self.current_state = "Processing"
        self.branch = None

    def run(self):
    
        while True:
            if self.env.now == 267:
                pass
            ##### ============== State Machine  ==============

            # =================== Idle State ===================
            if self.current_state == "Idle":

                # ============ Start Action ============
                #--- Rise the Flag that the machine doesn't have any part
                flag_new_part = False

                #--- Check Initial Ghost Machine
                # Given that every queue need to connect with predecessor machine and sucessor machine, it's
                # not possible to create an initial queue without previous machine, that's why is important
                # to create a Ghost Machine that has no previous queue but connect with the first queue.
                # Issue #95 (add open loop) 

                if self.queue_in != None:
                    #--- Loop to look to all the queue in availables
                    for queue in self.queue_in:
                        
                        #-- Verify if the queue is empty
                        queue_empty = queue.get_len() == 0
                        if queue_empty:
                            flag_new_part = False
                        
                        #-- If the queue is not empty, we change the status of the flag
                        else:
                            flag_new_part = True
                            self.queue_to_get = queue
                            break # Using break, because I want to stop for the first queue available
                        


                        #--- Increment Counter IN
                        self.counter_queue_in +=1    

                #--- Ghost machine keeps stuck in the IDLE state
                elif self.queue_in == None:
                    pass


                # ============ Finished Action ============



                # ============ State Transition ============

                if flag_new_part == True:
                    self.current_state = "Processing" #return "Processing"

                
                else:
                    """
                    self.queue_to_get = self.queue_in[0]
                    self.part_in_machine = yield self.queue_to_get.get()
                    self.current_state = "Processing"   
                    """
                    yield self.env.timeout(1)   
                    self.current_state = "Idle"          
            # ============================================================================

            # =================== Processing State ===================
            if self.current_state == "Processing":
                # ============ Start Action ============
                #--- First thing before processing is to get the part:
                
                #-- There is no initial part
                if self.worked_time == 0:
                    #-- Get the part
                    if self.queue_to_get.get_len() != 0:
                        #- Just get a new part if the machine doesn't have a initial part to be processed
                        try_to_get = self.queue_to_get.get() 
                        self.part_in_machine = try_to_get.value

                #-- There is an initial part being processed, I don't need to take from the queue
                if self.worked_time != 0:
                    #-- machine has an initial part to be processed
                    self.part_in_machine = self.initial_part


                #-- Lower the flag that we finish the process
                flag_process_finished = False
                self.working = True
                self.part_started_time = self.env.now

                #---- Trace Driven Simulation (TDS) ----
                # Check if the comming part have trace
                if self.validator != None:
                    print(f"Part in machine being analysed in validation: {self.part_in_machine.get_name()}")
                    print(f"Part total TDS traces: {self.part_in_machine.get_all_ptime_TDS()}")
                    #--- If the current part is not within the TDS range (normal simulation)
                    if self.part_in_machine.get_id() > self.validator.get_len_TDS() and self.simtype != "qTDS":
                        self.simtype = None
                    #--- If the current part is within the TDS range (TDS simulation)
                    if self.part_in_machine.get_id() <= self.validator.get_len_TDS() and self.simtype != "qTDS":
                        self.simtype = "TDS"
                    #--- If the current part finish all the cluster that it has
                    if self.part_in_machine.get_all_ptime_TDS() != None:
                        if self.get_cluster() > len(self.part_in_machine.get_all_ptime_TDS()) and self.simtype != "qTDS":
                            self.simtype = None
                    #--- If the current part has TDS traces (process times) uses TDS simulation, if not use normal simulation
                    if self.part_in_machine.get_ptime_TDS(self.get_cluster() - 1) == False and self.simtype != "qTDS":
                        self.helper.printer(f"[WARNING][components.py/run()/'Processing'] The {self.part_in_machine.get_name()} in {self.name} didn't have a TDS trace, assigning a normal simulation...")
                        self.simtype = None
                    if self.part_in_machine.get_ptime_TDS(self.get_cluster() - 1) != False and self.simtype != "qTDS":
                        self.simtype = "TDS"

                    if self.worked_time != 0 and self.part_in_machine.get_ptime_TDS(self.get_cluster() - 1) == False:
                        pass

                    """ [OLD: before sync]
                    if self.part_in_machine.get_all_ptime_TDS() != None:
                        if self.part_in_machine.get_finished_clusters() + 1 > len(self.part_in_machine.get_all_ptime_TDS()) and self.simtype != "qTDS":
                            self.simtype = None
                    """

                # ====== Processing Time ======
                # processing of the part depending on part type
                if self.worked_time == 0:
                    #-- User interface
                    print(f'Time: {self.env.now} - [{self.name}] got {self.part_in_machine.get_name()} from {self.queue_to_get.get_name()} (capacity= {self.queue_to_get.get_len()})')

                    #--- Process Started (Update digital_log)
                    self.database.write_event(self.database.get_event_table(),
                    timestamp= self.env.now,
                    machine_id= self.name,
                    activity_type= "Started",
                    part_id= self.part_in_machine.get_name(),
                    queue= self.queue_to_get.get_name())

                #--------------- Type of Simulation ---------------
                #--- Normal Simulation
                if self.simtype == None:
                    #-- Get the name of the distribution
                    if type(self.process_time) == list:

                        distribution_name = self.process_time[0]

                        #-- generate the process time following the given distribution
                        if distribution_name == 'norm':
                            #current_process_time = norm.rvs(self.process_time[1], self.process_time[2], size= 1) - self.worked_time
                            current_process_time_gen = norm.rvs(self.process_time[1], self.process_time[2], size= 1)

                        elif distribution_name == 'expon':
                            #current_process_time_gen = norm.rvs(self.process_time[1], self.process_time[2], size= 1) - self.worked_time
                            current_process_time_gen = norm.rvs(self.process_time[1], self.process_time[2], size= 1) 

                    else:
                        #current_process_time_gen = self.process_time - self.worked_time
                        current_process_time_gen = self.process_time

                    # --- Check if the already worked time is higher than the current process time ---
                            
                    # Case 01: Part still being process by the machine
                    if self.worked_time < current_process_time_gen:
                        current_process_time = current_process_time_gen - self.worked_time
                    
                    # Case 02: Part already processed by the machine, but stuck inside of the machine because of BLOCKING CONDITIONS
                    if self.worked_time > current_process_time_gen:
                        # Since it was already process, I take just the time waited by the blocking condition
                        current_process_time = self.worked_time - current_process_time_gen

                    # Case 03: Part JUST FINISHED the process time of the machine (very rare case, but can happen)
                    if self.worked_time == current_process_time_gen:
                        # Sinse it just finished, assign the lowest process time possible
                        current_process_time= 1

                    #=========================================================
                    yield self.env.timeout(int(current_process_time))  # processing time
                    #=========================================================
                    

                #--- Trace Driven Simulation (TDS)
                elif self.simtype == "TDS":
                    #-- Quicky fix for TDS of parts in the middle of the simulation
                    
                    #-- If our first part still from the initial working
                    if self.worked_time != 0:
                        #-- Updated the processed time list of part considering the "supposed" finished cluster
                        if self.part_in_machine.get_ptime_TDS(self.get_cluster() - 1) == False:
                            pass
                        self.part_in_machine.quick_TDS_fix(self.get_cluster())

                    #-- Get the current cluster of that part
                    
                    ##### Old approach before Sync ####
                    #part_current_cluster = self.part_in_machine.get_finished_clusters()
                    #current_process_time = self.part_in_machine.get_ptime_TDS(part_current_cluster)

                    #--- Get machine cluster
                    machine_cluster = self.get_cluster()

                    #-- Get the current process time
                    # minus 1 because the machine cluster starts with 1 and the position of process time with 0

                    current_process_time = self.part_in_machine.get_ptime_TDS(machine_cluster - 1)

                    # get the related process time for that part and for this cluster of machine
                    #=========================================================
                    yield self.env.timeout(current_process_time)  # processing time
                    #=========================================================

                    #-- (old before sync) Update the next cluster for that part
                    #part_next_cluster = part_current_cluster + 1
                    #self.part_in_machine.set_finished_clusters(part_next_cluster)
                
                #--- quasi Trace Driven Simulation (qTDS)
                elif self.simtype == "qTDS":
                    #-- Get the current process time
                    current_process_time = self.ptime_qTDS[self.finished_parts]

                    #=========================================================
                    yield self.env.timeout(current_process_time)  # processing time
                    #=========================================================

                    #-- Updated the number of finished parts
                    self.finished_parts += 1

                    #--- Finishing Up
                    # case when the supposed number of finished parts are done,
                    # but the simulation still running. (almost finished)

                    if self.finished_parts > (len(self.ptime_qTDS) - 1):
                        # Use > because if it's equall it still have 1 less part to simulate
                        # -1 because finished parts range from 0 to len(L) -1 (L= [0,1] ,len(L) = 2)

                        #-- Go back to the normal process time procedure
                        self.simtype = None
                #------------------------------------------------------
                

                # --- Rise the flag of processing
                flag_process_finished = True
                self.working = False
                # --- All the work done, initial part done
                self.worked_time = 0

                # ============ Finished Action ============

                #------------------------------------------------------

                # ============ State Transition ============

                if flag_process_finished == True:
                    self.current_state = "Allocating" #return "Allocating"
                    
                else:
                    self.current_state = "Processing" #return "Processing"                
            # ============================================================================

            # =================== Allocating State ===================
            if self.current_state == "Allocating":

                #--- First we look for an available queue out
                flag_allocated_part = False

                # ============ Start Action ============

                # --------------------- OPEN LOOP ---------------------
                #--- Open Loops requires different allocation for final machines
                if self.loop == "open" and self.final_machine == True:

                    #--- Change Flag
                    flag_allocated_part = True

                    #--- Terminate
                    self.terminator.terminate_part(self.part_in_machine)
                    print(f'Time: {self.env.now} - [Terminator] xxx {self.part_in_machine.name} terminated xxx')

                    #--- Queue Allocated (Update digital_log)
                    self.database.write_event(self.database.get_event_table(),
                    timestamp= self.env.now,
                    machine_id= self.name,
                    activity_type= "Finished",
                    part_id= self.part_in_machine.get_name(),
                    queue= "---") #There is no queue to put

                    #--- Check to finish the simulation according to desired amount of parts
                    if self.terminator.get_len_terminated() == self.last_part_id:
                        # we can do this because all the machines were assigned for the same terminator
                        # (the same terminator that we're using for running analysis in the end)

                        #--- Terminates the simulations
                        self.exit.succeed()
                    
                    #--- Check to finish the simulation according to a specific part id
                    if self.part_in_machine.get_id() == self.targeted_part_id:
                        #-- The targeted part was just finished, the simulation can stop now
                        #-- This method is useful for RCT calculations for a specific part

                        #--- Terminates the simulation
                        self.exit.succeed()

                # ------------------- CLOSED LOOP -------------------
                else:
                    #--- Included cases
                    # All closed loop cases
                    # Open Loop cases that are not final machines

                    # ------------------ RCT Policy Check ------------------
                    # (only for branching machines)
                    if self.branch != None:

                        #--- Just do the process if the machine was set with the vector (from RCT server)
                        if self.parts_branch_queue != None:
                            # --- Take the correponding Branch Queue selection for the current part in machine
                            for part_tuple in self.parts_branch_queue:
                                # -- Get part name
                                part_name = part_tuple[0]
                                if self.part_in_machine.get_name() == 'Part 6':
                                    pass
                                # --- Find the part that I have inside
                                if self.part_in_machine.get_name() == part_name:
                                    # -- Get the selected queue for this part (that is the one that we have)
                                    branch_queue_selected = part_tuple[1]

                                    # -- Check if the part has any queue assigned
                                    if branch_queue_selected != None:
                                        # Store the name of the queue to put
                                        queue_name_to_put = branch_queue_selected

                                        # Change the Policy of the Machine
                                        self.allocation_policy = "rct"

                                    # -- If the part that was processed don't have a branch queue, than go back to normal
                                    else:
                                        self.allocation_policy = self.old_policy
                        # #--- If the machine was not set with the vector, keep the old policy
                        # if self.parts_branch_queue == None:
                        #     self.allocation_policy = self.old_policy

                    if self.part_in_machine.get_name() == 'Part 6':
                        pass
                    # ------------------ Branching Policy Check ------------------

                    #--- Take the list of paths (conveyors) 
                    part_paths = self.part_in_machine.get_branching_path() #list of conveyors selected

                    #--- Check if it's a branching manchine and if the part is with paths assigned
                    if self.branch != None and part_paths != None:
                        #--- change policy
                        self.allocation_policy = "branching"
                        
                    elif self.allocation_policy != 'rct':
                        #--- Go back to the default policy
                        self.allocation_policy = self.old_policy


                    # ------------------ Choosing the Next Queue ------------------

                    # ===================================================================================

                    # ---------------- First Queue Free Policy ----------------
                    if self.part_in_machine.get_id() == 6:
                        pass
                    if self.allocation_policy == "first":
                        for queue in self.queue_out:
                            if queue.get_len() >= queue.capacity: #queue  full
                                flag_allocated_part = False
                                

                            #--- If the current Queue is not full:
                            else:
                                #--- Mark the Queue Out Available
                                self.queue_to_put = queue
                                #-- Increment counter out
                                self.counter_queue_out += 1
                                break # I take the first free
                    # --------------------------------------------------------

                    # ---------------- Alternating Policy ----------------
                    if self.allocation_policy == "alternated":
                        
                        if self.name== 'Machine 2':
                            pass
                       
                        #--- Select the Queue based on the counter
                        queue_selected = self.queue_out[self.allocation_counter]

                        #--- Define the last Allocation counter as empty
                        last_allocation_counter = None
                        flag_allocated_queue = False

                        # Loop through next queue in the perspective of the counter
                        for i in range(self.allocation_counter, len(self.queue_out)):                                

                            #--- Select the current Queue to check
                            queue_selected = self.queue_out[i]

                            #---------------------- SELECT AVAIALABLE QUEUE ----------------------
                            if queue_selected.get_len() < queue_selected.get_capacity():
                                flag_allocated_queue = True
                                last_allocation_counter = i
                                self.queue_to_put = queue_selected
                                print(f"! Using 'alternated' policy to allocate {self.part_in_machine.get_name()} to {self.queue_to_put.get_name()}")
                                break
                            #----------------------------------------------------------------------
                            
                            #--- No queue chosen and already look to all the queues (all full)
                            if flag_allocated_queue == False and i+1 >= len(self.queue_out):
                                if self.env.now % 5 == 0:
                                    print(f'Time: {self.env.now} - [ALL QUEUES FULL] {self.name} is trying to allocate {self.part_in_machine.get_name()}, but all the output queues are full for this machine!')
                                
                                # -------------- WAITING --------------
                                yield self.env.timeout(self.waiting)
                                # -------------------------------------

                                # ---------------------- TIMEOUT ----------------------
                                if self.env.now >= 1000:
                                    self.helper.printer("[ERROR][components.py/alternating policy] TIMEOUT", 'red')
                                    self.exit.succeed()
                                    sys.exit()
                                # ------------------------------------------------------

                                # ------------------------ RESET VARIABLES -----------------
                                #-- Reset the i and also the allocation to check the queues again from the begining
                                self.allocation_counter = 0
                                i = 0
                                # -----------------------------------------------------------

                        #---------------------- In Case of None ------------------------
                        if last_allocation_counter == None: last_allocation_counter= 0
                        #---------------------------------------------------------------

                        #---------- Increase the counter for the next allocation ---------
                        self.allocation_counter = last_allocation_counter + 1
                        #-----------------------------------------------------------------

                        #---------------- Reset the counter if it's at maximum ----------------
                        if self.allocation_counter >= (len(self.queue_out)):
                            self.allocation_counter = 0 # minus 1 because we're going to increase 1 anyways
                        #-----------------------------------------------------------------------

                        
                        #--- Find the right conveyor (just check the conveyor if the machine found a queue free)
                        if flag_allocated_queue== True:
                            for conveyor in self.conveyors_out:
                                if conveyor.id == self.queue_to_put.get_id():
                                    #--- Conveyor of the same selected queue
                                    conveyor_to_put = conveyor
                                    break

                    # ---------------- Branching Policy ----------------
                    if self.allocation_policy == "branching":
                        #--- Between the existing out conveyors of the machine, search for
                        # one present also in the path of the part and selected it.
                        conveyor_to_put = self.branch.branch_decision(self.part_in_machine)

                        #--- Find the rigth queue to put
                        for queue in self.queue_out:
                            if conveyor_to_put.id == queue.get_id():
                                #-- Found the queue that the part is going
                                self.queue_to_put = queue
                    #-------------------------------------------------------------

                    # ----------------  RCT Policy ----------------
                    if self.allocation_policy == "rct":
                        #--- Find the rigth queue object based on the queue name
                        for queue in self.queue_out:
                            if queue.get_name() == queue_name_to_put:
                                self.queue_to_put = queue
                        
                        print(f"! Using 'rct' policy to allocate {self.part_in_machine.get_name()} to {self.queue_to_put.get_name()}")

                        #--- Find the right conveyor
                        for conveyor in self.conveyors_out:
                            if conveyor.id == self.queue_to_put.get_id():
                                #--- Conveyor of the same selected queue
                                conveyor_to_put = conveyor
                                break

                    # ============= Check if the Queue is not full =============
                    # --------------- Alternating Policy ---------------
                    if self.allocation_policy == "alternated":
                        # If it's alternated, it just choose the queue when it's free
                        # so we can use the same flag as before
                        if flag_allocated_queue == True:
                            flag_allocated_part = True
                    
                    # --------------- First, Branching and RCT Policy ---------------
                    if self.allocation_policy== "first" or self.allocation_policy=="branching" or self.allocation_policy=="rct":
                        # This policies receives the queue without knowing if it's
                        # full or not, so we need to check here:
                        if self.queue_to_put.get_len() < self.queue_to_put.get_capacity():
                            flag_allocated_part = True
                        
                    # ============= ALLOCATION (queue not full) =============
                    if self.part_in_machine.get_name()== 'Part 10' and self.name== 'Machine 2':
                        self 
                    if flag_allocated_part == True:
                        #--- Queue Allocated (Update digital_log)
                        # obs: makes senses to take the time just after the allocation, because in the model becuase the model generation works like that
                        self.database.write_event(self.database.get_event_table(),
                        timestamp= self.env.now,
                        machine_id= self.name,
                        activity_type= "Finished",
                        part_id= self.part_in_machine.get_name(),
                        queue= self.queue_to_put.get_name()) 

                        #--- Evaluate if the machine is the last machine in the process or not
                        if self.final_machine == False:
                            # Open and Closed loop included (that are not final machines)
                            
                            ###### (Old) Before Conveyors ######
                            """
                            #--- Put the part in the next queue as usual
                            self.queue_to_put.put(self.part_in_machine)
                            print(f'Time: {self.env.now} - [{self.name}] put {self.part_in_machine.get_name()} in {self.queue_to_put.name} (capacity = {self.queue_to_put.get_len()})')
                            flag_allocated_part = True
                            """

                            #--- Put the part in the rigth conveyor
                            conveyor_to_put.start_transp(self.part_in_machine)
                            flag_allocated_part = True
                            
                            
                            # ------- STOP Machine condition -------
                            # --- If the machine was set to stop the simulation when finish up this part:
                            if self.flag_stop_for_id == self.part_in_machine.get_id():
                                #--- Terminates the simulation
                                self.exit.succeed()

                        if self.final_machine == True and self.loop == "closed":
                            #--- Terminate
                            self.terminator.terminate_part(self.part_in_machine)
                            print(f'Time: {self.env.now} - [Terminator] xxx {self.part_in_machine.name} terminated xxx')
                            
                            
                            #--- Replace part
                            self.last_part_id += 1   
                            new_part_produced = Part(id= self.last_part_id, type= self.part_in_machine.get_type(), location= 0, creation_time= self.env.now)
                            print(f'Time: {self.env.now} - [Terminator] {new_part_produced.name} replaced')
                            
                            #---- Trace Driven Simulation (TDS) ----
                            # Assign the related Trace for the new part
                            # Here I don't change the type of simulation, just assign a trace for a part
                            # if that part exists in the given traces, changing the status I alsways do in
                            # in the begining.
                            if self.validator != None:
                                #--- More parts being created than the existing parts in the TDS
                                if new_part_produced.get_id() <= self.validator.get_len_TDS():
                                    # if the new part belongs to the given traced parts
                                    current_TDS = self.validator.get_part_TDS(new_part_produced)
                                    new_part_produced.set_ptime_TDS(current_TDS)
                                    
                            #------------------------------------

                            #--- Put the part to the next Queue
                            #self.queue_to_put.put(new_part_produced) #before conveyors
                            
                            #--- Put the part in the rigth conveyor
                            conveyor_to_put.start_transp(new_part_produced)
                            flag_allocated_part = True


                            #--- Check to finish the simulation according to a specific part id
                            if self.part_in_machine.get_id() == self.targeted_part_id:
                                #-- The targeted part was just finished, the simulation can stop now
                                #-- This method is useful for RCT calculations for a specific part

                                #--- Terminates the simulation
                                self.exit.succeed()

                        #--- Check max number of parts to be produced in the simulation
                        if self.maxparts != None and self.terminator.get_len_terminated() == self.maxparts:
                            #--- Terminates the simulations
                            self.exit.succeed()
                        
                        #--- Timeout in the simulation (number of parts produced higher than maximum allowed)
                        if self.terminator.get_len_terminated() >= 100:
                            #--- Why you produced so many parts? Maybe the system is stuck in some kind of infinity loop!
                            self.helper.printer("[ERROR][components.py/Machine()/run()] TIMEOUT in the simulation! More than 100 parts produced, the system might be stuck in an infinity loop, please check the stop conditions. Printing stop conditions...")
                            print("--------- Stop Conditions ---------")
                            print(f"|-- maxparts: {self.maxparts}")
                            print(f"|-- until: {self.until}")
                            print(f"|-- targeted part id: {self.targeted_part_id}")

                            self.helper.printer(f"---- Simulation was killed ----", 'red')
                            sys.exit()
                # ============ Finished Action ============

                #------------------------------------------------------

                # ============ State Transition ============

                if flag_allocated_part == True:
                    self.current_state = "Idle" #return "Idle"
                    
                else:
                    """
                    self.queue_to_put = self.queue_out[0]
                    yield self.queue_to_put.put(self.part_in_machine)

                    #--- Queue Allocated (Update digital_log)
                    # obs: makes senses to take the time just after the allocation, because in the model becuase the model generation works like that
                    self.database.write_event(self.database.get_event_table(),
                    timestamp= self.env.now,
                    machine_id= self.name,
                    activity_type= "Finished",
                    part_id= self.part_in_machine.get_name(),
                    queue= self.queue_to_put.get_name()) 
                    self.current_state = "Idle"
                    """
                    
                    yield self.env.timeout(1)
                    self.current_state = "Allocating"      
            # ==========================================================



    #--------- Defining GETs ---------
    def get_working(self):
        return self.working
    def get_queue_in(self):
        return self.queue_in  
    def get_queue_out(self):
        return self.queue_out
    def get_process_time(self):
        return self.process_time
    def get_name(self):
        return self.name
    def get_capacity(self):
        return self.capacity
    def get_blocking_policy(self):
        return self.blocking_policy
    def get_final_machine(self):
        return self.final_machine
    def get_ptime_qTDS(self):
        return self.ptime_qTDS
    def get_id(self):
        return self.id
    def get_part_started_time(self):
        return self.part_started_time
    def get_cluster(self):
        return self.cluster
    def get_initial_part(self):
        return self.initial_part
    def get_convey_ins(self):
        return self.conveyors_in
    def get_conveyors_out(self):
        return self.conveyors_out
    def get_branch(self):
        return self.branch
    def get_last_part_id(self):
        return self.last_part_id
    def get_worked_time(self):
        return self.worked_time
    def get_allocation_counter(self):
        return self.allocation_counter
    #--------- Defining SETs ---------
    def set_queue_in(self, value):
        self.queue_in = value
    def set_queue_out(self, value):
        self.queue_out = value
    def set_process_time(self, value):
        self.process_time = value
    def set_final_machine(self, value):
        self.final_machine = value
    def set_simtype(self, simtype):
        self.simtype = simtype
    def set_ptime_qTDS(self, ptime_qTDS):
        self.ptime_qTDS = ptime_qTDS
    def set_validator(self, validator):
        self.validator = validator
    def set_cluster(self, cluster):
        self.cluster = cluster
    def set_conveyors_out(self, conveyors_out):
        self.conveyors_out = conveyors_out
    def set_conveyors_in(self, convey):
        self.conveyors_in = convey
    def set_branch(self, branch):
        self.branch = branch
    def set_targeted_part_id(self, target_id):
        self.targeted_part_id = target_id
    def set_last_part_id(self, id):
        self.last_part_id = id
    def set_initial_part(self, part):
        self.initial_part = part
    def set_worked_time(self, value):
        self.worked_time = value
        
        if self.worked_time != 0:
            #-- Part ready to be processed
            self.current_state = "Processing"
    def set_stop_for_id(self, part_id):
        self.flag_stop_for_id = part_id
    def set_allocation_counter(self, counter):
        self.allocation_counter = counter
    def set_parts_branch_queue(self, tuple_vector):
        self.parts_branch_queue= tuple_vector
    #--- Special set for queue
    def add_queue_in(self, value):
        if self.queue_in is None:
            self.queue_in = []
        self.queue_in.append(value)
    def add_queue_out(self, value):
        if self.queue_out is None:
            self.queue_out = []
        self.queue_out.append(value)


    #--- Define verbose
    def verbose(self):
        print("----------------")
        #--- Machine Name
        print(f"> {self.get_name()}")

        #--- Queue In
        print(f"--Queue In:--")
        if self.get_queue_in() is None:
            print("None")
        else:
            for queue in self.get_queue_in():
                print(queue.get_name())
        
        #--- Queue Out        
        print(f"--Queue Out:--")
        if self.get_queue_out() is None:
            print("None")
        else:
            for queue in self.get_queue_out():
                print(queue.get_name())
        
        #--- Machine Cluster
        print(f"Machine Cluster: {self.get_cluster()}")

        #--- Machine Branching?
        if self.branch != None:
            print(f"Branching Machine: {self.branch.get_name()}")
            for conveyor in self.branch.get_conveyors():
                print(f"|-- {conveyor.get_name()}")

        #--- Quasi Trace Driven Simulation
        if self.get_ptime_qTDS() is not None:
            print("---Process Time for quasi Trace Driven Simulation---")
            print(self.get_ptime_qTDS())

        #--- Initial Working Parts
        if self.initial_part != None:
            print(f"--- Part already being processed: {self.initial_part.get_name()} ---")
        """
        print(f"Capacity: {self.get_capacity()}")
        print(f"Blocking Policy: {self.get_blocking_policy()}")
        print(f"Final Machine? {self.get_final_machine()}")
        print("----------------")
        """
        
class Queue():
    def __init__(self, env, id, capacity, arc_links= None, transp_time= None, freq= None):
        self.env = env
        self.id = id
        self.name = "Queue " + str(self.id)
        self.store = simpy.Store(env, capacity=capacity)
        self.capacity = capacity
        self.queue_strength = None   # add initial condition
        self.transp_time = transp_time
        self.freq = freq
        self.cluster = None
        self.arc_links = arc_links

    #======= Main Functions =======
    def put(self, resource):
        return self.store.put(resource)

    def get(self):
        return self.store.get()
    #==============================

    #--- Define Gets
    def get_all_items(self):
        return self.store.items
    def get_len(self):
        self.queue_strength = len(self.store.items)
        return self.queue_strength
    def get_arc_links(self):
        return self.arc_links
    def get_name(self):
        return self.name
    def get_capacity(self):
        return self.capacity
    def get_id(self):
        return self.id
    def get_cluster(self):
        return self.cluster
    def get_transp_time(self):
        return self.transp_time
    
    #--- Define Sets
    def set_id(self, id):
        self.id = id
        self.name = "Queue " + str(self.id)
    def set_cluster(self, cluster):
        self.cluster = cluster


    #--- Define verbose
    def verbose(self):
        print("----------------")
        print(f"{self.get_name()}")
        print(f"Arc links: {self.get_arc_links()}")
        print(f"Capacity: {self.get_capacity()}")
        for part in self.get_all_items():
            print(f"|-- Parts stored: {part.get_name()}")
            if part.get_all_ptime_TDS() != None:
                print(f"Part Processes for Trace Driven Simulation: {part.get_all_ptime_TDS()}")
        print(f"Queue Lenght: {self.get_len()}")

class Generator():
    def __init__(self, env = None,  loop_type = None, part_vector = None, queue_vector = None,):
        self.loop_type = loop_type
        self.part_vector = part_vector
        self.queue_vector = queue_vector
        self.env = env
    
    def allocate_part(self):
        for part in (self.part_vector):
            self.queue_vector[part.get_location()].put(part)
        
        return self.queue_vector

    def create_part(self, part_id = None, part_type= None, part_location= None):
        return Part(id= part_id, type= part_type, location= part_location, creation_time= self.env.now)

class Terminator():
    def __init__(self, env=None, loop_type=None):
        self.loop_type = loop_type
        self.env = env
        self.store = simpy.Store(env) #Terminator with infinity capacity
    
    def terminate_part(self, part):
        part.set_termination(self.env.now) #set the termination time
        self.store.put(part)
        
    
    def get_all_items(self):
        return self.store.items
    def get_len_terminated(self):
        return len(self.store.items)


# ========================= Conveyor Class =========================
class Conveyor():
    def __init__(self, env, transp_time, queue_out):
        self.name = "Conveyor towards " + queue_out.get_name()
        self.id = queue_out.get_id()
        self.transp_time = transp_time
        self.queue_out = queue_out
        self.env = env
        self.convey_store = simpy.Store(env= self.env)
        self.wait = 1
        self.flag_part_transported = False
    
    def start_transp(self, part):
        #--- Add a part in the conveyor
        print(f"Time: {self.env.now} - [{self.name}] GOT {part.get_name()}")
        part.set_convey_entering_time(self.env.now) 
        self.convey_store.put(part)
    
    def finish_transp(self):
        #--- Remove a part from the conveyor

        return self.convey_store.get()
    
    def get_all_items(self):
        return self.convey_store.items
    
    def run(self):
        """
        Note: It's better to not use the yield because during the transportation of one
        part, another part can already start the process. The yield would make the transportation
        unique for that specific part. That's why is better to track tha entry and exit time
        of each part individually.
        
        The loop of the conveyor get a part in the transportation and check if the first part
        already spend time enough. If yes it puts the part in the queue, if not it yield for while
        to check again later. If there is no parts in the conveyor, it also yields for a bit 
        before checking again.

        1) Just get a part from the queue in if the part arrived in the queue
        2) Create a new process that is able to receive different parts and have a run functions that
        take the first part and yields it and after drop it in the corresponded queue
        """

        while True:
            #--- Take all the parts in the conveyor
            parts_in_conveyor = self.get_all_items()

            #--- If there is any part in the conveyor
            if len(parts_in_conveyor) > 0:
                #--- Select the first part that arrived
                first_part = parts_in_conveyor[0]

                #--- Calculate the amount of time that the part spend in the conveyor
                started_time = first_part.get_convey_entering_time()
                current_time = self.env.now
                transported_time = current_time - started_time

                #--- Check if the part already spend enough time in transportation
                if transported_time >= self.transp_time:
                    #--- Transportation finished, PUT part to the Queue
                    print(f"Time: {self.env.now} - [{self.name}] PUT {first_part.get_name()} in the {self.queue_out.get_name()}") 
                    self.finish_transp()
                    self.queue_out.put(first_part)
                
            
            # --- Anyways, wait a bit before checking again
            yield self.env.timeout(self.wait)

    def get_id(self):
        return self.id()
    def get_convey_queue(self):
        return self.queue_out
    def get_name(self):
        return self.name
# =============================================================================

class Branch():
    def __init__(self, id, branch_conveyors, branch_machine, branch_queue_in):
        self.id= id
        self.name = f"Branch {self.id} | {branch_machine.get_name()}"
        self.branch_conveyors = branch_conveyors
        self.branch_machine = branch_machine
        self.branch_queue_in = branch_queue_in

    def branch_decision(self, part_to_put):
        #--- Between the machine option of conveyors to put, is there one 
        # that matches with one of options assigned for the part path?
        
        #--- Look through the conveyors of the machine
        for machine_conveyor in self.branch_machine.get_conveyors_out():
            #--- Look through the conveyor available for the part
            for part_conveyors in part_to_put.get_branching_path():
                if machine_conveyor.id == part_conveyors.id:
                    #--- Found a conveyor within of the parts paths available in the conveyors of the machine
                    conveyor_to_put = machine_conveyor
                    break
        
        #--- Branch PUT part in the conveyor
        return conveyor_to_put
        
    # ======= GETs =======
    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_conveyors(self):
        return self.branch_conveyors
    def get_branch_queue_in(self):
        return self.branch_queue_in
    def get_branch_machine(self):
        return self.branch_machine

