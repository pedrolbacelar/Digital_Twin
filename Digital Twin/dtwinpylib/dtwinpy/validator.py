#--- Importing Database components
from .interfaceDB import Database

#--- Reload Package

import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)


class Validator():
    def __init__(self, digital_model, simtype, real_database):
        self.digital_model = digital_model
        self.simtype = simtype
        # qTDS: each row is the list of process time for each part
        self.matrix_ptime_qTDS = None 
        # TDS: each row is the list of process time for each machine
        self.matrix_ptime_TDS = None

        #--- Database
        # The real database is going to be create by the broker,
        # here we're just getting the object that point to that
        # database. That's why we don't initialize it.
        self.real_database = real_database
        self.digital_database = self.digital_model.get_model_database()

        #--- Get the components of the simulation
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()


    # ======================= TRACE DRIVEN SIMULATION ======================= 
    #--- For a specific part ID return the related vector of ptime_TDS
    def get_part_TDS(self, part):
        return self.matrix_ptime_TDS[part.get_id() - 1]
    
    #--- Get the number of parts given in the TDS
    def get_len_TDS(self):
        return len(self.matrix_ptime_TDS)
    
    #--- Initial Setup of TDS
    def set_TDS(self):
        #--- List for all parts in the simulation
        part_list = []
        #--- Get the existing parts already allocated in the Queues
        for queue in self.queues_vector:
            #-- get the parts from the current queue
            current_parts = queue.get_all_items()
            if current_parts != None:
                #-- add each part to main list
                for part in current_parts:
                    part_list.append(part)
        
        #--- give for each part the ptime_TDS list 
        for part in part_list:
            current_ptime_TDS = self.get_part_TDS(part)
            part.set_ptime_TDS(current_ptime_TDS)
        
        #--- Set the simulation type for all the machines
        for machine in self.machines_vector:
            #--- Set the type of Simulation
            machine.set_simtype("TDS")

    #--- Generate the traces of TDS based on the real Event Log
    def generate_TDS_traces(self):

        #--- Extract the unique parts IDs from the real log
        part_ids = self.real_database.get_distinct_values(column= "part_id", table="real_log")
        #--- Create matrix to store trace of process time for each part
        matrix_ptime_TDS = []
        part_matrix_full_trace = []

        #--- Loop for each part of the simulation
        for part_id in part_ids:
            #--- Get the full trace for each part
            part_full_trace = self.real_database.get_time_activity_of_column(column= "part_id", table="real_log", column_id= part_id)
            part_matrix_full_trace.append(part_full_trace)

            #--- Initiate as blank values
            started_time = None
            finished_time = None
            processed_time = None
            part_trace = []

            for event in part_full_trace:
                #--- Extract the Started and Finished time
                if event[1] == 'Started':
                    started_time = event[0]
                elif event[1] == 'Finished':
                    finished_time = event[0]
                
                #--- Calculate the process time
                if started_time != None and finished_time != None:
                    processed_time = finished_time - started_time

                    #--- Add event process time to the part trace
                    part_trace.append(processed_time)

                    #--- reset local started and finished time for the next cycle
                    started_time = None
                    finished_time = None
                    processed_time = None
            
            #--- Add part trace to the matrix of all parts traces
            matrix_ptime_TDS.append(part_trace)
            
        #--- Return the matrix of traces
        return matrix_ptime_TDS
    
    # =======================================================================

    

    # ==================== QUASI TRACE DRIVEN SIMULATION ====================

    #--- Initial Setup of qTDS
    def set_qTDS(self):
        #--- Update each existing machine in the model
        for machine in self.machines_vector:
            #--- Set the type of Simulation
            machine.set_simtype("qTDS")

            #--- Get the related list of process time for that machine
            current_ptime_TDS = self.matrix_ptime_qTDS[machine.get_id() - 1]

            #--- Assign the list of processes time
            machine.set_ptime_qTDS(current_ptime_TDS)

    #--- Generate the traces of qTDS based on the real Event Log
    def generate_qTDS_traces(self):

        #--- Extract the unique parts IDs from the real log
        machines_ids = self.real_database.get_distinct_values(column= "machine_id", table="real_log")
        #--- Create matrix to store trace of process time for each part
        matrix_ptime_qTDS = []
        machine_matrix_full_trace = []

        #--- Loop for each part of the simulation
        for machine_id in machines_ids:
            #--- Get the full trace for each machine
            machine_full_trace = self.real_database.get_time_activity_of_column(column= "machine_id", table="real_log", column_id=machine_id)
            machine_matrix_full_trace.append(machine_full_trace)

            #--- Initiate as blank values
            started_time = None
            finished_time = None
            processed_time = None
            machine_trace = []

            for event in machine_full_trace:
                #--- Extract the Started and Finished time
                if event[1] == 'Started':
                    started_time = event[0]
                elif event[1] == 'Finished':
                    finished_time = event[0]
                
                #--- Calculate the process time
                if started_time != None and finished_time != None:
                    processed_time = finished_time - started_time

                    #--- Add event process time to the machine trace
                    machine_trace.append(processed_time)

                    #--- reset local started and finished time for the next cycle
                    started_time = None
                    finished_time = None
                    processed_time = None
            
            #--- Add machine trace to the matrix of all machines traces
            matrix_ptime_qTDS.append(machine_trace)
            
        #--- Return the matrix of traces
        return matrix_ptime_qTDS

    # =======================================================================

    # ======================== Sequence Generator ========================
    def generate_event_sequence(self, database, table):
        #--- Extract all the events from the table and store each in tuple
        events_full_trace = database.read_store_data(table)

        #--- Extract the time and store in a specific vector
        time_sequence = []
        for event in events_full_trace:
            time_sequence.append(event[0])
        
        #--- Create the string event and store in the vector of events
        events_sequence = []
        for event in events_full_trace:
            event_string = event[1] + " - " + event[2]
            events_sequence.append(event_string)

        return (time_sequence, events_sequence)

    # =======================================================================

    # ======================== Sequence Comparing Methods ========================

    def LCSS(self, Sequence1, Sequence1_time, Sequence2, Sequence2_time, delta_t, order = False):
        # initialize the lengths of the two input vectors
        m, n = len(Sequence1), len(Sequence2)
        
        # initialize an empty list to store the events that belong to the longest common sub-sequence
        lcss = []
        lcss_time = []
        jstart = 1
        # loop through each event in Sequence1
        for i in range(1, m + 1):
            # loop through each event in Sequence2
            for j in range(jstart, n + 1):
                # check if the current events in Sequence1 and Sequence2 are within the eps and delta_t threshold,
                # and if the time difference between them is less than or equal to delta_t
                if (Sequence1[i-1] == Sequence2[j-1]) and (abs(Sequence1_time[i-1] - Sequence2_time[j-1]) <= delta_t):
                    # add the current event from Sequence1 to the lcss list
                    lcss.append(Sequence1[i-1])
                    lcss_time.append(Sequence1_time[i-1])

                    #--- Mark the j used, the next iteration will look from this j to forward
                    if order == True:
                        jstart = j

                    # break from the inner loop
                    break

        
        #--- Similarity Indicator
        indicator = len(lcss) / min(m,n)

        # return the longest common sub-sequence
        return (lcss, lcss_time, indicator)




    # ========================= Overlaping Functions =========================
    def allocate(self):
        #--- Generate the tarces
        self.matrix_ptime_qTDS = self.generate_qTDS_traces()
        self.matrix_ptime_TDS= self.generate_TDS_traces()

        print("=== matrix_ptime_qTDS ===")
        for i in range(len(self.matrix_ptime_qTDS)):
            print(f"Machine {i+1}: {self.matrix_ptime_qTDS[i]}")

        print("=== matrix_ptime_TDS ===")
        for j in range(len(self.matrix_ptime_TDS)):
            print(f"Part {j+1}: {self.matrix_ptime_TDS[j]}")

        #--- Setup initial Traces
        if self.simtype == "TDS":
            #--- Set the TDS for each part
            self.set_TDS()

        if self.simtype == "qTDS":
            #--- Set the qTDS for each machine and also the simtype
            self.set_qTDS()

    def run(self):

        # obs: I can run the simulation direct because the machines already have the type of simulation
        if self.simtype == "TDS":
            #--- Run Trace Driven Simulation
            print("============ Running Trace Driven Simulation ============")
            self.digital_model.run()

            #--- Generate output event sequence from the digital database
            (Ys_time, Ys_event) = self.generate_event_sequence(database= self.digital_database, table= "digital_log")
            
            #--- Generate output event sequence from the digital database
            (Yr_time, Yr_event) = self.generate_event_sequence(database= self.real_database, table= "real_log")
            
            #--- Compare Event Sequence
            (lcss, lcss_time, lcss_indicator) = self.LCSS(Sequence1= Ys_event, Sequence1_time= Ys_time, Sequence2= Yr_event, Sequence2_time= Yr_time, delta_t=100)
            print("--- LCSS Sequence ---")
            print(lcss)

            print("--- LCSS Time ---")
            print(lcss_time)

            print(f">>> LCSS Indicator: {lcss_indicator}")
            
            print("=========================================================")

        if self.simtype == "qTDS":
            #--- Run Quasi Trace Driven Simulation
            print("============ Running quasi Trace Driven Simulation ============")
            self.digital_model.run()
            print("===============================================================")
    # =======================================================================



        
