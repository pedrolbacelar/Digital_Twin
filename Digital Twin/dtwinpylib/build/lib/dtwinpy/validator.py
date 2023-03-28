#--- Importing Database components
from .interfaceDB import Database
from .helper import Helper

#--- Common Libraries
import numpy as np
import matplotlib.pyplot as plt
import sqlite3


#--- Reload Package

"""import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)"""


class Validator():
    def __init__(self, digital_model, simtype, real_database_path, start_time, end_time, generate_digital_model, id_database_path= False,copied_realDB= False, delta_t_treshold= 100):
        self.helper = Helper()
        self.digital_model = digital_model
        self.generate_digital_model= generate_digital_model
        self.simtype = simtype
        self.delta_t_treshold = delta_t_treshold
        # qTDS: each row is the list of process time for each part
        self.matrix_ptime_qTDS = None 
        # TDS: each row is the list of process time for each machine
        self.matrix_ptime_TDS = None
        self.copied_realDB = copied_realDB

        #--- Database
        # The real database is going to be create by the broker,
        # here we're just getting the object that point to that
        # database. That's why we don't initialize it.
        self.start_time = start_time
        self.end_time = end_time

        if simtype == "TDS":
            feature_usingDB= "valid_logic"
        if simtype == "qTDS":
            feature_usingDB= "valid_input"

        #--- Databases
        self.real_database = Database(database_path=real_database_path, event_table= "real_log", feature_usingDB= feature_usingDB, start_time=start_time, end_time=end_time, copied_realDB= copied_realDB)
        self.digital_database = self.digital_model.get_model_database()
        self.real_database_path = self.real_database.get_database_path()
        self.id_database = Database(database_path=id_database_path, event_table= "ID")

        #--- Change the name of the table in database if it's digital to real
        with sqlite3.connect(self.real_database_path) as db:
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            if len(tables) == 1 and tables[0][0] == "digital_log":
                self.real_database.rename_table("digital_log", "real_log")

        #--- Get the components of the simulation
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()


    # ======================= TRACE DRIVEN SIMULATION ======================= 
    #--- For a specific part ID return the related vector of ptime_TDS
    def get_part_TDS(self, part):
        """
        This function receives a part object and look into the dictionary of parts traces
        in order to get the correct trace of that part.
        """
        try:
            return self.matrix_ptime_TDS[part.get_name()]
        except KeyError:
            self.helper.printer(f"[WARNING][validator.py/get_part_TDS()] Trying to get the trace of {part.get_name()}, but no traces was created for that part", "yellow")
            print("If you're running a short simulation, it's possible that the part was in the simulation, but didn't had time to appear in the trace, otherwise CHECK IT OUT")

    #--- Get the number of parts given in the TDS
    def get_len_TDS(self):
        return len(self.matrix_ptime_TDS)
    
    #--- Initial Setup of TDS
    def set_TDS(self):
        """
        This function is responsible to take the traces of each part extracted from the real log and
        add it for the respective part. 
        """
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
        
        #--- Get the existing parts within operating machines
        for machine in self.machines_vector:
            if machine.get_initial_part() != None:
                part = machine.get_initial_part()
                part_list.append(part)
                # Note 1: I can do this because the Validator is being called after the simulation,
                # after assigned, we don't change the initial part of a machine
                
        
        #--- give for each part the ptime_TDS list 
        for part in part_list:
            current_ptime_TDS = self.get_part_TDS(part)
            part.set_ptime_TDS(current_ptime_TDS)

        #--- Set the simulation type for all the machines
        for machine in self.machines_vector:
            #--- Set the type of Simulation
            machine.set_simtype("TDS")

        #--- Extra adjust for initial parts (parts in WIP) already in middle of the simulation
        # Since this parts are already in the simulation, the TDS generated
        # is not aligned with the number of cluster. So let's say I started in 
        # cluster 2 and the system has 4 cluster. My TDS will have only 3 elements
        # (c2,c3,c4). But in cluster 2 i will take in element in position 2, so c3. 
        # To fix that we put some extra 0 in the beginning equivalent to the number
        # of cluster that I already been through.
        #
        # This fix is only for parts that are positionated in Queues, because the parts
        # that are inside of machine are already going to have their own quick fix. We do
        # all of this just to get the rigth queue, and based on the queue figure out the 
        # the cluster of machine. Here I don't need to have the dictionary, because I'm
        # changing each part at time.
        
        #--- Get all initial parts in queues from the simulation
        initial_parts = self.digital_model.get_all_parts()

        #--- Get the parts names that appears in traces
        #parts_in_trace = self.real_database.get_distinct_values(column= "part_id", table="real_log")
        parts_in_trace = self.real_database.get_parts_with_completed_traces()
        parts_in_trace_names = []
        # Take only the string from the database
        for part in parts_in_trace:
            parts_in_trace_names.append(part[0])

        #--- Try to match parts in simulation with parts in trace
        parts_to_remove = []
        for part in initial_parts:
            
            # Try to see if the part from the model is within the parts of trace
            try:
                parts_in_trace_names.index(part.get_name())

            except ValueError:
                print(f"{part.get_name()} was not found in the parts of trace... Removing part from the list")
                parts_to_remove.append(part)

        #--- Remove parts
        for part in parts_to_remove:
            initial_parts.remove(part)
        
        if len(parts_to_remove) > 0:
            print("----------------  Cleaning Parts for TDS  ----------------")
            print("Not all the parts in the system appeared in the traces. Printing parts that didn't appeared:")
            for part in parts_to_remove:
                print(f"|-- {part.get_name()}")
            print("Printing parts that appeared and are being considered for TDS:")
            for part in initial_parts:
                print(f"|-- {part.get_name()}")
            print("------------------------------------------------------------")

            

        """
        initial_copy = initial_parts
        for i in range(len(initial_copy)):
            pos = 
            part = initial_parts[i]
            # Loop for each simulation part
            flag_in_trace = False
            for part_in_trace_name in parts_in_trace:
                # Loop for each trace part name
                if part.get_name() == part_in_trace_name[0]:
                    # Found a the simulation part in the trace, don't need to keep chasing
                    flag_in_trace = True
                    break
            
            #--- Check if the part was found in some of the traces
            if flag_in_trace == False:
                # The part was in the simulation and did't appeared in the trace, removing...
                initial_parts.remove(part)
                pass
        """

        #--- Assign the queue object to the part
        for part in initial_parts:
            for queue in self.queues_vector:
                # If the numerical location of the part if the same as the id of the queue
                if part.get_location() == queue.get_id() - 1:
                    part.set_part_queue(queue)
                    break

        for part in initial_parts:
            #--- For parts in queues we know the cluster, for parts within machines it's solved internally
            part_queue = part.get_part_queue()
            # If the part is within a Queue and is not in the first queue
            if part_queue != None and part_queue.get_id() != 1:
                part_cluster = part_queue.get_cluster()
                part.quick_TDS_fix(part_cluster)
                print(f"--- Part name {part.get_name()} quick done. Part Cluster: {part_cluster}")
                print(f"All process time for each cluster:{part.get_all_ptime_TDS()}")
                print(f"Process time of the first cluster: {part.get_ptime_TDS(part_cluster - 1)}")
        

    #--- Generate the traces of TDS based on the real Event Log
    def generate_TDS_traces(self):
        """
        This function is used to create the traces of each part. By 'traces' we mean the process
        time that each part takes for each cluster of machine in the simulation. For that the function
        read the selected session of the database and look for the specific path that a part took. Finally
        the function adds this path in a dictionary that has as key the part name and as value the vector
        with the path.
        """

        #--- Extract the unique parts IDs from the real log
        part_ids = self.real_database.get_distinct_values(column= "part_id", table="real_log")
        
        #--- If the simulation is not started from the begining the part_ids is not ordered
        def sort_key(t):
            return int(t[0].split(' ')[-1])

        part_ids = sorted(part_ids, key=sort_key)
        
        #--- Create matrix to store trace of process time for each part
        #[OLD] matrix_ptime_TDS = [] 
        matrix_ptime_TDS = {}
        part_matrix_full_trace = []

        #--- Loop for each part of the simulation
        for part_id in part_ids:
            #--- Get the full trace for each part
            part_full_trace = self.real_database.get_time_activity_of_column(column= "part_id", table="real_log", column_id= part_id[0])
            part_matrix_full_trace.append(part_full_trace)

            #--- Initiate as blank values
            started_time = None
            finished_time = None
            processed_time = None
            part_trace = []

            #--- For each event in the path of each part
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
                
                #--- AVOID: In the case of part that already was in the machine (worked_time)
                if finished_time != None and started_time == None:
                    processed_time = finished_time

                    #--- Add event process time to the part trace
                    part_trace.append(processed_time)

                    #--- reset local started and finished time for the next cycle
                    started_time = None
                    finished_time = None
                    processed_time = None

            
            #--- Add part trace to the matrix of all parts traces
            #[OLD] matrix_ptime_TDS.append(part_trace)
            matrix_ptime_TDS[part_id[0]] = part_trace
            
        #--- Return the matrix of traces
        return matrix_ptime_TDS
    
    # =======================================================================

    

    # ==================== QUASI TRACE DRIVEN SIMULATION ====================

    #--- Initial Setup of qTDS
    def set_qTDS(self):
        #--- Update each existing machine in the model

        #--- Extract the unique parts IDs from the real log
        machines_ids = self.real_database.get_distinct_values(column= "machine_id", table="real_log")
        
        # For every machine that was USED in the real world
        # We iterate the within the machines id because it's possible that
        # the simulation has more machines rather than the real log, because
        # one of the machines in the real world was not chosen.
        for machine_id in machines_ids:
            
            # For this machine_id, find the machine object with the same id
            for i in range(len(self.machines_vector)):
                if machine_id[0] == self.machines_vector[i].get_name():
                    machine = self.machines_vector[i]

                    machine_process_time = machine.get_process_time()
                    #--- Dealing with Distribution Machines
                    if type(machine_process_time) == list:
                        #--- Set the type of Simulation
                        machine.set_simtype("qTDS")

                        #--- Get the related list of process time for that machine
                        current_ptime_qTDS = self.matrix_ptime_qTDS[machine.get_name()]

                        #--- Assign the list of processes time
                        machine.set_ptime_qTDS(current_ptime_qTDS)

                    #--- Dealing with Deterministic Machines
                    else:
                        #--- Don't assign nothing, because the comparasion will directly
                        pass

                    break

    #--- Generate the traces of qTDS based on the real Event Log (Xr)
    def generate_qTDS_traces(self):

        #--- Extract the unique parts IDs from the real log
        machines_ids = self.real_database.get_distinct_values(column= "machine_id", table="real_log")
        #--- Create matrix to store trace of process time for each part
        matrix_ptime_qTDS = {}
        machine_matrix_full_trace = []

        #--- Loop for each part of the simulation
        for machine_id in machines_ids:
            #--- Get the full trace for each machine
            machine_full_trace = self.real_database.get_time_activity_of_column(column= "machine_id", table="real_log", column_id=machine_id[0])
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

                #--- In the case of part that already was in the machine (worked_time)
                if finished_time != None and started_time == None:
                    processed_time = finished_time

                    #--- Add event process time to the part trace
                    machine_trace.append(processed_time)

                    #--- reset local started and finished time for the next cycle
                    started_time = None
                    finished_time = None
                    processed_time = None
            
            #--- Add machine trace to the matrix of all machines traces
            matrix_ptime_qTDS[machine_id[0]] = (machine_trace)
            
        #--- Return the matrix of traces
        return matrix_ptime_qTDS

    #--- Generate the Xs (traces) from Xr
    def generate_Xs_machine(self, loc, scale, distribution, Xr, a= None, b= None):
        # -----------------------------------------------------
        # Functions for eCDF and randomness
        # -----------------------------------------------------
        # Calculate the ECDF
        def ECDF(Xr):
            if len(Xr) == 25:
                pass
            Xr_sorted = np.sort(Xr)
            ecdf = np.arange(1, (len(Xr_sorted)+1)) / len(Xr_sorted) # calculate ecdf
            return(ecdf)
        # Calculate randomness u
        def randomness(ecdf,umax,Xr):
            Xr_sorted = np.sort(Xr)
            
            """
            u=np.array([])
            for ii in range(len(ecdf)):
                # BUG: ADDING 2 MORE THAN LEN(ECDF)
                u=np.append(u,ecdf[np.asarray(np.where(Xr_sorted==Xr[ii]))])
            """

            u = []
            for ii in range(len(ecdf)):
                ecdf_value = None
                for jj in range(len(Xr_sorted)):
                    if Xr_sorted[jj] == Xr[ii]:
                        ecdf_value = ecdf[jj]
                        break
                if ecdf_value is not None:
                    u.append(ecdf_value)


            # print(len(ecdf))
            for i in range(len(u)):
                if u[i] == 1.0:
                    pos_one = i
            #pos_one = np.where(u == 1.0)
            u[pos_one]=umax # change 1 to 0.99 to avoid infinity in dist.ppf function
            return(u,pos_one)

        # -----------------------------------------------------
        # Function for Generating dedicated disrtibutions
        # -----------------------------------------------------
        # we mention the number of parameters used to define the distribution as N_Parameter

        # Importing required library from SciPy
        if distribution == 'norm':
            from scipy.stats import norm as dist
            N_Parameter=2   # loc = mu, scale = sigma
        elif distribution == 'expon':
            from scipy.stats import expon as dist
            N_Parameter=2   # loc = threshold or inital value, scale = scale/slope of exponential curve
        elif distribution == 'gamma':
            from scipy.stats import gamma as dist
            N_Parameter=3   # a = shape parameter, loc, scale
        elif distribution == 'erlang':
            from scipy.stats import erlang as dist
            N_Parameter=3   # a = shape parameter, loc, scale
        elif distribution == 'weibull_min':
            from scipy.stats import weibull_min as dist
            N_Parameter=3   # a = shape parameter beta or k, loc = gamma, scale = eta(n) or lambda
        elif distribution == 'weibull_max':
            from scipy.stats import weibull_max as dist
            N_Parameter=3   # a = shape parameter beta or k, loc = gamma, scale = eta(n) or lambda
        elif distribution == 'triang':
            from scipy.stats import triang as dist
            N_Parameter=3   # a = shape or mode parameter, loc = minimum or start, scale = maximum or end
        elif distribution == 'lognorm':
            from scipy.stats import lognorm as dist
            N_Parameter=3   # a threshold, scale = sigma
        elif distribution == 'beta':
            from scipy.stats import beta as dist
            N_Parameter=4   # a,b = shape parameters, loc, scale
        else:
            print("Warning: Specified distribution type not found. Executing validation assuming an exponential distribution")
            from scipy.stats import expon as dist
            N_Parameter=2   # loc = threshold or inital value, scale = scale/slope of exponential curve

        # defining required arrays
        Xsf=np.array([])
        Xs=np.array([])
        diff=np.zeros(901)
        diff[900]=np.inf
        umax=np.zeros(900)
        sse=np.zeros(900)

        # Deriving randomness from Xr and generating Xs
        for ii in range(899,498,-1):
            umax[ii]=0.91+(ii*0.0001)
            Xsf=Xs

            if N_Parameter==2:  # for distributions with 2 parameters
                u,pos_one = randomness(ECDF(Xr),umax[ii],Xr) # calculate inverse transform of ecdf.
                Xs = (dist.ppf(u, loc, scale))    # generate distribution Xs.

            if N_Parameter==3:  # for distributions with 3 parameters
                u,pos_one = randomness(ECDF(Xr),umax[ii],Xr) # calculate inverse transform of ecdf.
                Xs = (dist.ppf(u, a, loc, scale))    # generate distribution Xs.

            if N_Parameter==4:  # for distributions with 4 parameters
                u,pos_one = randomness(ECDF(Xr),umax[ii],Xr) # calculate inverse transform of ecdf.
                Xs = (dist.ppf(u, a, b, loc, scale))    # generate distribution Xs.

            diff[ii]=abs(Xs[pos_one]-Xr[pos_one])   # Calculate error in the highest value due to impact of umax
            #sse[ii]=np.sum(np.square(Xr-Xs))
            
            if diff[ii]>diff[ii+1]:
                Xs=Xsf
                break

        i=range(1,len(Xr)+1)
        plt.plot(i,Xr,color='blue')
        plt.plot(i,Xs,color='red')
        plt.show()
        
        return(Xs)
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
        
        # we take the smallest sequence as first sequence to get the indicator value not greater than 1.0
        if len(Sequence1) > len(Sequence2):
            alt = Sequence1
            alt_time = Sequence1_time
            Sequence1 = Sequence2
            Sequence1_time = Sequence2_time
            Sequence2 = alt
            Sequence2_time = alt_time
        else:
            pass
        
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
        indicator = len(lcss) / max(m,n)
        print("-------------------------------------")
        print("Printing LCSS Event sequence...")
        for i in range(len(lcss)):
            print(f"[{i}] {lcss_time[i]} - {lcss[i]}")
        print("-------------------------------------")

        # return the longest common sub-sequence
        return (lcss, lcss_time, indicator)

    def dDTW(s1,s2):
        m = len(s1)                 # sequence 1 of size m
        n = len(s2)                 # sequence 2 of size n
        s1_bar = np.divide(s1,max(max(s1),max(s2)))
        s2_bar = np.divide(s2,max(max(s1),max(s2)))

        d = np.zeros((n+1,m+1))     # Distance matrix d. It has a size of (n+1)x(m+1).
        d[1:n+1:1,0] = np.inf
        d[0,1:m+1:1] = np.inf
        for i in range(1,n+1):
            for j in range(1,m+1):
                # we take the absolute distance between two points plus the minimum of the three values surronding it.
                d[i,j] = abs(s2_bar[i-1]-s1_bar[j-1])+min(d[i-1,j-1],d[i-1,j],d[i,j-1])
        # we divide the value of last cell with the max(n,m)
        dDTW_bar = d[n,m]/max(n,m)
        # validity index. Closer to 1 means less difference/distance between two sequences. Hence 1 means, the sequence is valid.
        dDTW = 1 - dDTW_bar         

        # print("cumulative distance = ", d[n,m])
        # print("distance matrix =\n",d)
        # print("validity index = ",dDTW)
        return(dDTW)


    # ========================= Overlaping Functions =========================
    def allocate(self):
        #--- Generate the traces

        # ---------------- qTDS ----------------
        #--generate Xr of real log for all the machines (matrix)
        Xr_matrix = self.generate_qTDS_traces()
        self.matrix_ptime_qTDS = {}
        
        #--- Loop to correlated each Xs with Xr
        # The loop can also be seem as loop through the machines
        machines_ids = self.real_database.get_distinct_values(column= "machine_id", table="real_log")
        for machine_id in machines_ids:
            
            # For this machine_id, find the machine object with the same id
            for i in range(len(self.machines_vector)):
                if machine_id[0] == self.machines_vector[i].get_name():
                    machine = self.machines_vector[i]
                    
                    #--- Take the distribution parameters of each machine
                    machine_process_time = machine.get_process_time()
                    if type(machine_process_time) == list:
                        dist = machine_process_time[0]
                        loc = machine_process_time[1]
                        scale = machine_process_time[2]

                        Xr_vector = Xr_matrix[machine.get_name()]
                        print(Xr_vector)

                        Xs_vector = self.generate_Xs_machine(loc= loc, scale= scale, distribution= dist, Xr= Xr_vector)
                        self.matrix_ptime_qTDS[machine.get_name()] = (Xs_vector)
                    
                    else:
                        #--- WRONG!!! This bellow implementation is wrong. The goal here is not to copy and paste
                        # the process time from the real into the digital machines. We're using it just to get the
                        # the randmness to generate new data using the current distribution parameters of the digital
                        # machines... But in the case that it's deterministic (not a list) we can't just copy from the real!
                        # we need just to run the simulation and compare the final sequences....
                        
                        #Xs_vector = Xr_matrix[machine.get_name()]
                        #self.matrix_ptime_qTDS[machine.get_name()] = (Xs_vector)
                        pass

                    break

        """
        # ---- Plotting to see correlation ----
        machine = 2
        counter = range(len(Xr_matrix[machine]))
        plt.plot(counter,Xr_matrix[machine],color='blue')
        plt.plot(counter,self.matrix_ptime_qTDS[machine],color='red')
        plt.show()
        """

        # ---------------- TDS ----------------
        #-- generate Xr = Xs
        self.matrix_ptime_TDS= self.generate_TDS_traces()

        #--- Setup initial Traces
        if self.simtype == "TDS":
            #--- Set the TDS for each part
            self.set_TDS()

        if self.simtype == "qTDS":
            #--- Set the qTDS for each machine and also the simtype
            self.set_qTDS()

        # --------- Interface ----------
        print("-----------------------------------------------------------------------------------------")
        print("=== matrix_ptime_qTDS ===")
        if len(self.matrix_ptime_qTDS) == 0:
            print("[VALIDATOR] Simulation Deterministic - No correlation of randoness needed")
        else:
            for key in self.matrix_ptime_qTDS:
                print(f"{key}: {self.matrix_ptime_qTDS[key]}")
        
        print()

        print("=== matrix_ptime_TDS ===")
        for key in self.matrix_ptime_TDS:
            print(f"{key}: {self.matrix_ptime_TDS[key]}")
            # [OLD] print(f"Part {j+1}: {self.matrix_ptime_TDS[j]}")
        print("-----------------------------------------------------------------------------------------")

    def run(self):

        # --- Update the Digital Model before running anything ---
        # --- Get model constrains
        (until, maxparts, targeted_part_id, targeted_cluster) = self.digital_model.get_model_constrains()

        # --- Update the duration of the simulation in case that none of other parameters was give
        # (also for that you need to have start and end time)
        if (until, maxparts, targeted_part_id, targeted_cluster) == (None, None, None, None) and (self.start_time != None and self.end_time != None):
            #--- Get the current duration between start and finish trace
            until = self.real_database.get_current_durantion()
            #-- adjust to run until the end
            until += 1

            #--- Set this new stop condition in the model
            self.digital_model.set_until(until)
            self.helper.printer(f"[Validator] Duration of the TDS and qTDS being used: {until}", 'brown')

        
        # ------- Assign Parts Queue Branches selected -------
        parts_branch_queue = self.id_database.read_parts_branch_queue()
        for machine in self.machines_vector:
            machine.set_parts_branch_queue(parts_branch_queue)
    

        # [OLD] self.digital_model = self.generate_digital_model(until= until)
        # Maybe this is a very wrong approach, because you're generating new components after
        # already made changes in the property of them before. Inside of the Features (validator,
        # synchronizer, etc we shouldn't create new modules, just update them!)

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
            (lcss, lcss_time, lcss_indicator) = self.LCSS(Sequence1= Ys_event, Sequence1_time= Ys_time, Sequence2= Yr_event, Sequence2_time= Yr_time, delta_t= self.delta_t_treshold)
            
            #--- User Interface
            print("==================== LOGIC VALIDATION ====================")
            print("---- Real Sequence:")
            for i in range(len(Yr_event)):
                print(f"{Yr_time[i]} | {Yr_event[i]}")
            print("---- Digital Sequence:")
            for i in range(len(Ys_time)):
                print(f"{Ys_time[i]} | {Ys_event[i]}")
            print(f">>> LCSS Indicator Logic: {lcss_indicator}")
            print("=========================================================")

            return((lcss, lcss_time, lcss_indicator))

        if self.simtype == "qTDS":
            #--- Run Quasi Trace Driven Simulation
            print("============ Running quasi Trace Driven Simulation ============")
            self.digital_model.run()

            #--- Generate output event sequence from the digital database
            (Ys_time, Ys_event) = self.generate_event_sequence(database= self.digital_database, table= "digital_log")
            
            #--- Generate output event sequence from the real database
            (Yr_time, Yr_event) = self.generate_event_sequence(database= self.real_database, table= "real_log")

            #--- Compare Event Sequence
            (lcss, lcss_time, lcss_indicator) = self.LCSS(Sequence1= Ys_event, Sequence1_time= Ys_time, Sequence2= Yr_event, Sequence2_time= Yr_time, delta_t= self.delta_t_treshold)
            
            #--- User Interface
            print("==================== INPUT VALIDATION ====================")
            print("---- Real Sequence:")
            for i in range(len(Yr_time)):
                print(f"{Yr_time[i]} | {Yr_event[i]}")
            print("---- Digital Sequence:")
            for i in range(len(Ys_time)):
                print(f"{Ys_time[i]} | {Ys_event[i]}")
            print(f">>> LCSS Indicator Input: {lcss_indicator}")
            print("=========================================================")

            return((lcss, lcss_time, lcss_indicator))
    # =======================================================================



        
