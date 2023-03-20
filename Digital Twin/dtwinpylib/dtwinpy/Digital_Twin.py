#--- Import DT Features
from .digital_model import Model
from .validator import Validator
from .interfaceDB import Database
from .synchronizer import Synchronizer
from .services import Service_Handler
from .broker_manager import Broker_Manager
from .helper import Helper
from .interfaceAPI import interfaceAPI

#--- Common Libraries
import shutil
import os
import sys
import datetime
from time import sleep
import random

#--- Reload Package
import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.digital_model)
importlib.reload(dtwinpylib.dtwinpy.validator)
importlib.reload(dtwinpylib.dtwinpy.synchronizer)
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)
importlib.reload(dtwinpylib.dtwinpy.helper)



class Digital_Twin():
    def __init__(self, name, copied_realDB= False,model_path= None, ip_address= None, initial= True, targeted_part_id= None, targeted_cluster= None, until= None, digital_database_path= None, real_database_path= None, ID_database_path= None, Freq_Sync= 1000, Freq_Valid= 10000, delta_t_treshold= 100,Freq_Service = None, part_type= "A", loop_type= "closed", maxparts = None, template= False, keepDB= True, plot= False, verbose= True, rct_queue= 3):
        self.helper = Helper()
        #--- Model Parameters
        self.name = name
        self.part_type = "A"
        self.loop_type = "closed"
        self.digital_model = None
        self.initial = initial
        self.copied_realDB = copied_realDB
        self.delta_t_treshold = delta_t_treshold

        #--- User Interface options
        self.verbose= verbose
        self.plot= plot
        self.rct_queue= rct_queue
    
        #--- Simulation stop conditions
        self.until = until
        self.maxparts = maxparts
        self.targeted_part_id = targeted_part_id
        self.targeted_cluster = targeted_cluster

        #--- Frequencies
        self.Freq_Sync = Freq_Sync
        self.Freq_Valid = Freq_Valid
        self.Freq_Service = self.Freq_Sync
        #self.interfaceAPI = interfaceAPI()


        #--- Time intervals
        (initial_time_str, initial_timestamp) = self.helper.get_time_now()
        self.current_timestamp = initial_timestamp
        

        self.next_Tsync = initial_timestamp + self.Freq_Sync
        self.last_Tsync = initial_timestamp

        self.next_Tvalid = initial_timestamp + self.Freq_Valid
        self.last_Tvalid = initial_timestamp

        self.next_Tserv = initial_timestamp + self.Freq_Service
        self.last_Tserv = initial_timestamp

        #--- Flags the integration
        self.flag_time_to_synchronize = False
        self.flag_time_to_validate = False
        self.flag_time_to_rct_service = False

        self.flag_Validated = False
        self.flag_synchronized = False
        self.flag_rct_served = False

        #--- Features Counters
        self.counter_Sync = 1
        self.counter_Valid = 1
        self.counter_Serv = 1

        #--- Model Pointers
        self.model_pointer_Sync = 0
        self.model_pointer_Valid = 0
        self.model_pointer_Serv = 0
        self.model_subpath_dict = {0: "initial"}
        """ 
        model_subpath_dict = {
            pointer1: 'timestamp1_pointer1',
            pointer2: 'timestamp2_pointer2',
            pointer3: 'timestamp3_pointer3'.
        }
        """

    
        #--- Figure path
        if not os.path.exists(f"figures"):
            os.makedirs(f"figures/")

        #------ Model JSON ------

        #-- Models root
        self.model_root = f"models/{self.name}"

        if model_path == None:
            # If folder doesn't exist, creates folder
            if not os.path.exists(self.model_root):
                os.makedirs(self.model_root)
            
            #-- First model name
            first_model = "initial.json"

            #-- Model Path default
            self.model_path = f"{self.model_root}/{first_model}"

            #-- Clean existing model files
            self.helper.delete_old_model(self.model_root, first_model)
        else:
            self.model_path = model_path

        #-- delete the current model and copy the template
        """
        if template == True:
            #- Delete old model
            os.remove(self.model_path)

            #- Copy the template into the model json
            template_path = f"models/{self.name}/template.json"
            try:
                shutil.copy2(template_path, self.model_path)
                print(f"Model copied successfuly from {template_path}!")
            except FileNotFoundError:
                self.helper.printer(f"[ERROR][Digital_Twin.py/__init__()] The template file does not exist, please create one or remoe Template condition", 'red')
        """

        # --------------- Database ----------------
        # Digital Database path assign
        if digital_database_path == None:
            # If folder doesn't exist, creates folder
            if not os.path.exists(f"databases/{self.name}"):
                os.makedirs(f"databases/{self.name}")
            
            # Assign database path
            self.database_path = f"databases/{self.name}/digital_database.db"
        else:
            self.database_path = digital_database_path
        
        # Real Database path assign
        if real_database_path == None:
            # If folder doesn't exist, creates folder
            if not os.path.exists(f"databases/{self.name}"):
                os.makedirs(f"databases/{self.name}")
            
            # Assign database path
            self.real_database_path = f"databases/{self.name}/real_database.db"
        else:
            self.real_database_path = real_database_path
        
        # ID database path assign
        if ID_database_path == None:
            # If folder doesn't exist, creates folder
            if not os.path.exists(f"databases/{self.name}"):
                os.makedirs(f"databases/{self.name}")
            
            # Assign database path
            self.ID_database_path = f"databases/{self.name}/ID_database.db"
        else:
            self.ID_database_path = ID_database_path

        # Delete existing database before starting anything
        if keepDB == False:
            print("|- Deleting existing databases...")
            
            #- Delete Digital Database
            try:
                os.remove(self.database_path)
                print(f"|-- Digital Database deleted successfuly from {self.database_path}")

            except FileNotFoundError:
                self.helper.printer(f"[WARNING][Digital_Twin.py/__init()__] The Digital Database doesn't exist yet in the path '{self.database_path}', proceding without deleting...")

            #- Delete Real Database
            try:
                os.remove(self.real_database_path)
                print(f"|-- Real Database deleted successfuly from {self.real_database_path}")
            except FileNotFoundError:
                self.helper.printer(f"[WARNING][Digital_Twin.py/__init()__] The Real Database doesn't exist yet in the path '{self.real_database_path}', proceding without deleting...")

            #- Delete ID database
            try:
                os.remove(self.ID_database_path)
                print(f"|-- ID Database deleted successfuly from {self.ID_database_path}")
            except FileNotFoundError:
                self.helper.printer(f"[WARNING][Digital_Twin.py/__init()__] The ID Database doesn't exist yet in the path '{self.ID_database_path}', proceding without deleting...")

        # --- For Local Test
        if self.copied_realDB == True:
            #--- Update the timestamp ---
        
            #--- before copying, we delete the previous one
            try:
                os.remove(self.real_database_path)
            except FileNotFoundError:
                self.helper.printer(f"[WARNING][Digital_Twin.py/init()] The file '{self.real_database_path}' does not exist")
                print(f"copying file {self.database_path} in the path {self.real_database_path}")
            
            #--- Copy the whole database
            shutil.copy2(self.database_path, self.real_database_path)

            #--- Create a temporary real db object for initial fix
            self.temporary_real_database = Database(database_path= self.real_database_path, event_table= 'real_log', copied_realDB= self.copied_realDB)

            #--- Copy the column timestamp into timestamp_real and clean the previous one
            self.temporary_real_database.copy_timestamp_to_timestamp_real()

            #--- Update the timestamp according to the current real time
            self.temporary_real_database.update_real_time_now()
        
        # Time Pointers table (just after real database created)
        self.pointers_database = Database(database_path= self.real_database_path, event_table= "time_pointers")

        # ------------------------------------------
        print(f"--- printing databases paths ---")
        print(f"Digital Database: '{self.database_path}'")
        print(f"Real Database: '{self.real_database_path}'")
        print(f"ID Database: '{self.ID_database_path}'")

        #--- Initiate the Broker for Feedback (just if ip_address if given)
        self.ip_address = ip_address
        self.broker_manager = None
        if self.ip_address != None:
            #--- Create a Broker
            self.broker_manager = self.initiate_broker(self.ip_address)
            print("Broker Manager internally create for publishing feedback...")


        # ================================ SET UP FINISHED ================================
        self.helper.printer(f"---- Digital Twin '{self.name}' created sucessfully ----", 'green')       
        # ==================================================================================

    # -------------------------------------------------- INDIVIDUAL FUNCTIONS --------------------------------------------------
    #--- Initiate Broker 
    def initiate_broker(self, ip_address, ID_database_path= None, port= 1883, keepalive= 60, topics_sub = ['trace', 'part_id', 'RCT_server'], topic_pub= 'RCT_server', client = None):
        #--- Take the global features
        self.ip_address = ip_address
        self.topic_pub = topic_pub
        if ID_database_path == None:
            ID_database_path = self.ID_database_path
        
        #--- Create the Broker Manager
        self.broker_manager = Broker_Manager(
            name= self.name,
            ip_address= self.ip_address,
            real_database_path= self.real_database_path,
            ID_database_path= ID_database_path,
            port= port,
            keepalive= keepalive,
            topics= topics_sub
        )

        return self.broker_manager
        
    #--- Create the Digital Model
    def generate_digital_model(self, until= None, maxparts= None, verbose= False, targeted_part_id = None, targeted_cluster= None):
        #--- if the functions don't receive nothing, use the default of the Digital Twin
        if maxparts == None:
            maxparts = self.maxparts

        #--- If the target conditions doesn't exist, assign it
        if targeted_part_id == None:
            targeted_part_id = self.targeted_part_id

        if targeted_cluster == None:
            targeted_cluster = self.targeted_cluster

        if until == None:
            until= self.until

        #--- Update the global maxparts and target part
        self.maxparts = maxparts
        self.targeted_part_id = targeted_part_id
        self.targeted_cluster = targeted_cluster
        self.until = until
        
        #--- Create the digital model with all the properties
        self.digital_model = Model(name= self.name,model_path= self.model_path, 
            database_path= self.database_path, until= self.until, initial= self.initial, 
            loop_type= self.loop_type, maxparts= maxparts,targeted_part_id=targeted_part_id,
            targeted_cluster= self.targeted_cluster)
        
        #--- Translate the digital model
        self.digital_model.model_translator()
        #--- Verbose if necessary
        if verbose == True:
            self.digital_model.verbose()

        return self.digital_model
    
    #--- Run normally the Digital Model and analyze the results
    def run_digital_model(self, plot= True, maxparts = None, until = None, targeted_part_id = None, targeted_cluster= None, verbose= True, generate_model = True):
        if generate_model == True:
            if maxparts == None:
                maxparts = self.maxparts

            #--- If the target conditions doesn't exist, assign it
            if targeted_part_id == None:
                targeted_part_id = self.targeted_part_id

            if targeted_cluster == None:
                targeted_cluster = self.targeted_cluster

            if until == None:
                until = self.until
            #--- Update the global maxparts and target part
            self.maxparts = maxparts
            self.targeted_part_id = targeted_part_id
            self.targeted_cluster = targeted_cluster
            self.until = until

            #--- Always before running re-generate the model, just in case it has some changes
            self.digital_model = self.generate_digital_model(until= self.until, maxparts= self.maxparts, targeted_part_id= self.targeted_part_id, targeted_cluster= self.targeted_cluster, verbose= verbose)
        
        #--- Run the simulation
        self.digital_model.run()
        
        #--- Plot Results
        if plot == True:
            self.digital_model.analyze_results()
 
    #--- Run the Validation
    def run_validation(self, copied_realDB= False, verbose= False, start_time= None, end_time= None):
        
        # ================== Trace Driven Simulation (TDS) ==================
        #--- (re)generate the Digital Model (reset)
        self.digital_model = self.generate_digital_model(verbose= verbose)

        """[OLD] Now we do this when creating the digital twin
        #--- Copied the Digital into the Real Databse
        if copied_realDB == True:
            shutil.copy2(self.database_path, self.real_database_path)
        """
        
        #--- Create the Logic Validator 
        validator_logic = Validator(digital_model= self.digital_model, simtype="TDS", real_database_path= self.real_database_path, start_time= start_time, end_time= end_time, generate_digital_model= self.generate_digital_model, copied_realDB= self.copied_realDB, delta_t_treshold= self.delta_t_treshold)
        
        #--- IMPROVE: give the object validator for the machine to be able to update the ptime_TDS for new parts
        #--- Get the components of the simulation
        (machines_vector, queues_vector) = self.digital_model.get_model_components()
        for machine in machines_vector:
            machine.set_validator(validator_logic)
        
        #--- Allocate the traces
        validator_logic.allocate()

        #--- Run the TDS
        (lcss_logic, lcss_time_logic, lcss_indicator_logic) = validator_logic.run()

        # ========================================================================


        # ================== quasi Trace Driven Simulation (qTDS) ==================

        #--- (re)generate the Digital Model (reset)
        self.digital_model = self.generate_digital_model(verbose= verbose)

        #--- Create the Input Validator
        validator_input = Validator(digital_model=self.digital_model, simtype="qTDS", real_database_path= self.real_database_path, start_time= start_time, end_time= end_time, copied_realDB= self.copied_realDB, generate_digital_model= self.generate_digital_model, delta_t_treshold= self.delta_t_treshold)

        #--- Allocate the traces
        validator_input.allocate()

        #--- Run the qTDS
        (lcss_input, lcss_time_input, lcss_indicator_input) = validator_input.run()

        # ========================================================================

        print("_______________________ Validation Results _______________________")
        print(f"> LCSS indicator for LOGIC: {lcss_indicator_logic}")
        print(f"> LCSS indicator for INPUT: {lcss_indicator_input}")
        print("__________________________________________________________________")

    #--- Run Synchronization
    def run_sync(self, repositioning = True, start_time= None, end_time= None, copied_realDB= False):            
        
        #--- Make sure the model is updated
        self.generate_digital_model()

        #--- Copied the Digital into the Real Databse
        """[OLD] Now we do this when creating the digital twin
        if self.copied_realDB == True:
            
            #--- before copying, we delete the previous one
            try:
                os.remove(self.real_database_path)
            except FileNotFoundError:
                self.helper.printer(f"[WARNING][Digital_Twin.py/run_sync()] The file '{self.real_database_path}' does not exist")
                print(f"copying file {self.database_path} in the path {self.real_database_path}")

            #--- copy
            shutil.copy2(self.database_path, self.real_database_path)
        """

        #--- Create the synchronizer
        synchronizer = Synchronizer(digital_model= self.digital_model, real_database_path= self.real_database_path, start_time= start_time, end_time= end_time, copied_realDB= self.copied_realDB, generate_digital_model= self.generate_digital_model, delta_t_treshold= self.delta_t_treshold)

        #--- Run the synchronizer (positioning)
        synchronizer.run(repositioning= repositioning)

    #--- Run RCT Services
    def run_RCT_services(self, verbose= True, plot= False, queue_position= 3):
        """
        This functions creates Service object that is responsible for finding parts making decisions in the simulation,
        generate all possible paths, and calculate the most optimized path for those parts.
        """
        #--- Create a Service 
        RCT_Service = Service_Handler(name= "RCT", generate_digital_model= self.generate_digital_model, broker_manager= self.broker_manager)
        
        #--- Run the RCT Service
        RCT_Service.run_RCT_service(verbose=verbose, plot= plot, queue_position= queue_position)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------

    # -------------------------------------------------- INTERNAL & EXTERNAL SERVICES --------------------------------------------------

    #--- Internal Services (Synchronization and Validation)    
    def Internal_Services(self):
        
        # ====================== Running Synchronization ======================
        if self.flag_time_to_synchronize:

            # --------------------- BEFORE SERVICES SETTINGS ---------------------
            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            self.helper.printer(f"[Internal Service] Starting Synchronization n° {self.counter_Sync}", 'blue')

            # --- Update Start and End time
            start_time = round(self.last_Tsync)
            end_time = round(self.next_Tsync)

            # --- Update Model Sync Pointer
            self.model_pointer_Sync += 1

            # --- Duplicate current before syncing
            (tstr, t) = self.helper.get_time_now()
            subpath = f"{t}_{self.model_pointer_Sync}"
            new_model_path = f"{self.model_root}/{subpath}.json"
            self.helper.duplicate_file(self.model_path, new_model_path)

            # --- Update model time dict
            self.model_subpath_dict[self.model_pointer_Sync] = subpath

            # --- Update Model Path
            self.model_path = new_model_path
            print(f"--- Model Path being used: {self.model_path}")
            

            # -------------- Run Synchronization --------------
            self.run_sync(copied_realDB= self.copied_realDB, start_time= start_time, end_time= end_time)
            # -------------------------------------------------

            

            # --- Send data through API
            # API
            """
            sleep(2)
            random_machines = [random.randint(0, 1) for _ in range(5)]
            for machine in random_machines:
                if machine == 0: machine = False
                if machine == 1: machine = True

            self.interfaceAPI.station_status(
                station_1= random_machines[0],
                station_2= random_machines[1],
                station_3= random_machines[2],
                station_4= random_machines[3],
                station_5= random_machines[4])
            
            random_queues = [random.randint(1, 6) for _ in range(5)]

            self.interfaceAPI.queue_status(
                queue_1= random_queues[0],
                queue_2= random_queues[1],
                queue_3= random_queues[2],
                queue_4= random_queues[3],
                queue_5= random_queues[4],asset_id="7da127f5a566408db16e0aeace5181e9"
            )
            """
            


            # --------------------- AFTER SERVICES SETTINGS ---------------------
            # --- Increase Sync Counter
            self.counter_Sync += 1
            
            # --- Validation just finish, so not time to validate anymore
            self.flag_time_to_synchronize = False

            # --- Adjust WHEN WAS the last validation (just happened)
            #-- Take the last end time ("previous next_TSync but updated")
            last_end_time = self.pointers_database.read_last_end_time()
            self.last_Tsync = last_end_time + 1

            #self.last_Tsync = self.next_Tsync # TODO: Update this considering the updated end time!
            

            # --- Adjust WHEN WILL be the next validation
            self.next_Tsync = self.current_timestamp + self.Freq_Sync

            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            nexttime = datetime.datetime.fromtimestamp(self.next_Tsync).strftime("%d %B %H:%M:%S")
            self.helper.printer(f"[Internal Service] System Synchronized. Next Sync (n° {self.counter_Sync}): {nexttime}", 'blue')
        
        # ====================== Running Validation ======================
        if  self.flag_time_to_validate:
            # --------------------- BEFORE SERVICES SETTINGS ---------------------
            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            self.helper.printer(f"[Internal Service] Starting Validation (n° {self.counter_Valid})", 'green')

            # --- Update Start and End time
            start_time = round(self.last_Tvalid)
            end_time = round(self.next_Tvalid)

            # --- Take the subpath according to last validation pointer
            subpath = self.model_subpath_dict[self.model_pointer_Valid]

            # --- Update the model path for Validation
            self.model_path = f"{self.model_root}/{subpath}.json"
            print(f"--- Model Path being used: {self.model_path}")

            # --- Update validation pointer according to the current Sync Pointer
            self.model_pointer_Valid = self.model_pointer_Sync

            # -------------- Run Validation --------------
            self.run_validation(copied_realDB= self.copied_realDB, start_time= start_time, end_time= end_time)
            # -------------------------------------------------

            

            # --- Send data through API
            # API
            """
            sleep(2)
            random_logic_indicator = random.uniform(0.85, 0.95)
            random_input_indicator = random.uniform(0.75, 0.95)
            self.interfaceAPI.indicator(logic= random_logic_indicator, input= random_input_indicator)
            """

            # --------------------- AFTER SERVICES SETTINGS ---------------------
            # --- Give back the model pointer to the present
            subpath = self.model_subpath_dict[self.model_pointer_Valid]
            self.model_path = f"{self.model_root}/{subpath}.json"

            # --- Increase Valid Counter
            self.counter_Valid += 1

            # --- Validation just finish, so not time to validate anymore
            self.flag_time_to_validate = False

            # --- Adjust WHEN WAS the last validation (just happened)
            #-- Take the last end time ("previous next_TValid but updated")
            last_end_time = self.pointers_database.read_last_end_time()
            self.last_Tvalid = last_end_time

            #self.last_Tvalid = self.next_Tvalid

            # --- Adjust WHEN WILL be the next validation
            self.next_Tvalid = self.current_timestamp + self.Freq_Valid

            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            nexttime = datetime.datetime.fromtimestamp(self.next_Tvalid).strftime("%d %B %H:%M:%S")
            self.helper.printer(f"[Internal Service] System Validated. Next Validation (n° {self.counter_Valid}): {nexttime}", 'green')


    #--- External Services (RCT Services and Feedback)
    def External_Services(self):

        # ====================== Running Services ======================
        if self.flag_time_to_rct_service:
            # --------------------- BEFORE SERVICES SETTINGS ---------------------
            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            self.helper.printer(f"[External Service] Starting RCT Service (n° {self.counter_Serv})", 'purple')

            # --- Check if Broker exists and if ip_address was given
            if self.broker_manager == None:
                (tstr, t) = self.helper.get_time_now()
                if self.ip_address == None:
                    self.helper.printer(f"[ERROR][Digital_Twin.py/External_Services()] Trying to run RCT services without a Broker because none IP ADDRESS was given. Please, provide an IP address to run online (recommendation: 192.168.0.50). For now, running offiline...", 'red')
                    
                else:
                    self.helper.printer(f"[ERROR][Digital_Twin.py/External_Services()] Trying to run RCT services without a Broker because of unknown reason. Please, check it out...", 'red')
                    self.helper.printer(f"---- Digital Twin was killed ----", 'red')
                    sys.exit()

            # --- Take the subpath according to last Service pointer
            subpath = self.model_subpath_dict[self.model_pointer_Serv]

            # --- Update the model path for Service
            self.model_path = f"{self.model_root}/{subpath}.json"
            print(f"--- Model Path being used: {self.model_path}")

            # --- Update Service pointer according to the current Sync Pointer
            self.model_pointer_Serv = self.model_pointer_Sync

            # -------------------- Run Service ---------------------------------
            self.run_RCT_services(verbose= self.verbose, plot= self.plot, queue_position= self.rct_queue)
            # ------------------------------------------------------------------

            # Send API results
            """
            sleep(2)
            part_id =  random.randint(1, 10)
            quque_id = random.randint(2, 3)
            path_1 = random.uniform(10000, 15000)
            path_2 = random.uniform(12000, 19000)

            self.interfaceAPI.RCT_server(part_id= part_id, path_1= path_1, path_2= path_2, queue_id= quque_id)
            """

            # --------------------- AFTER SERVICES SETTINGS ---------------------
            # --- Give back the model pointer to the present
            subpath = self.model_subpath_dict[self.model_pointer_Serv]
            self.model_path = f"{self.model_root}/{subpath}.json"

            # --- Increase Serv Counter
            self.counter_Serv += 1

            # --- Service just finish, so not time to validate anymore
            self.flag_time_to_rct_service = False

            # --- Adjust WHEN WAS the last validation (just happened)
            #-- Take the last end time ("previous next_Tserv but updated")
            last_end_time = self.pointers_database.read_last_end_time()
            self.last_Tserv = last_end_time

            #self.last_Tserv = self.next_Tserv

            # --- Adjust WHEN WILL be the next validation
            self.next_Tserv = self.current_timestamp + self.Freq_Service

            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            nexttime = datetime.datetime.fromtimestamp(self.next_Tserv).strftime("%d %B %H:%M:%S")
            self.helper.printer(f"[External Service] System RCT completed. Next Service (n° {self.counter_Serv}): {nexttime}", 'purple')

            # --- Reset the targeted part id to not change the stop condition of Validation
            self.targeted_part_id = None
            self.targeted_cluster = None
            
    #--- Update Flags of time
    def Update_time_flags(self):
        #--- Take the current time
        (time_str, timestamp) = self.helper.get_time_now()
        self.current_timestamp = timestamp

        #--- Check if it's time to Sync
        if timestamp >= self.next_Tsync:
            #-- Rise Time to Sync
            self.flag_time_to_synchronize = True
            self.flag_time_to_rct_service = True

        #--- Check if it's time to Validate
        if timestamp >= self.next_Tvalid:
            #-- Rise Time to Validate
            self.flag_time_to_validate = True

        #--- Check if it's time to Serve
        if timestamp >= self.next_Tserv:
            #-- Rise Time to Serve
            self.flag_time_to_rct_service = True

    # ------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    def run(self):
        """
        ## Architecture
        ----- For more details, please check the paper: DOI 0.00.000.0 -----

        #### Sequence of Actions in Loop 

        -------------------- Internal Services --------------------
        1. Run Sync with a certain frequency (Freq_sync)
            1.1 Down Flag_Synchronized -> False | time_to_synchronize -> True
            1.2 Run Sync
                1.2.1 API: Send Occupation and Indicators
            1.3 Rise Flag_Synchronized -> True | time_to_synchronize -> False
        2. Run Validation with a frequency (Freq_valid) multiple of Freq_sync
            2.1 time_to_validate -> True
            2.2 Run Validation
                2.2.1 If valid: Flag_Validation -> True
                2.2.2 If not valid: Flag_Validation -> False
                2.2.3 API: Send Indicators
            2.3 time_to_validate -> False
        ------------------------------------------------------------

        -------------------- External Services --------------------
        3. Run RCT Service matching Freq_Sync
            3.1 If Flag_Synchronized == True and Flag_Validation == True:
                3.1.1 Run RCT Services
                3.1.2 Implement the Feedback
        ------------------------------------------------------------

        extra: Clean the memory!
        """

        try: 
            
            while True:
                
                #--- Update the flags of time to know when to Sync, Validate and Run Services
                self.Update_time_flags()

                #--- Run the Internal Services (Synchronization and Validation)
                self.Internal_Services()

                #--- Run the External Services (RCT path prediction)
                self.External_Services()

        except KeyboardInterrupt:
            self.helper.printer(f"---- Digital Twin '{self.name}' was killed manually ----", 'red')


        
