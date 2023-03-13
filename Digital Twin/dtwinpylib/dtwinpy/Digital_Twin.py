#--- Import DT Features
from .digital_model import Model
from .validator import Validator
from .interfaceDB import Database
from .synchronizer import Synchronizer
from .services import Service_Handler
from .broker_manager import Broker_Manager
from .helper import Helper

#--- Common Libraries
import shutil
import os
import datetime
from time import sleep

#--- Reload Package
import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.digital_model)
importlib.reload(dtwinpylib.dtwinpy.validator)
importlib.reload(dtwinpylib.dtwinpy.synchronizer)
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)
importlib.reload(dtwinpylib.dtwinpy.helper)



class Digital_Twin():
    def __init__(self, name, copied_realDB= False,model_path= None, initial= True, targeted_part_id= None, targeted_cluster= None, until= None, digital_database_path= None, real_database_path= None, ID_database_path= None, Freq_Sync= 1000, Freq_Valid= 10000, Freq_Service = None, part_type= "A", loop_type= "closed", maxparts = None):
        self.helper = Helper()
        #--- Model Parameters
        self.name = name
        self.part_type = "A"
        self.loop_type = "closed"
        self.digital_model = None
        self.initial = initial
        self.copied_realDB = copied_realDB
    
        #--- Simulation stop conditions
        self.until = until
        self.maxparts = maxparts
        self.targeted_part_id = targeted_part_id
        self.targeted_cluster = targeted_cluster

        #--- Frequencies
        self.Freq_Sync = Freq_Sync
        self.Freq_Valid = Freq_Valid
        self.Freq_Service = self.Freq_Sync


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



        

        #--- Model and Figure path
        if not os.path.exists(f"figures"):
            os.makedirs(f"figures/")

        if model_path == None:
            # If folder doesn't exist, creates folder
            if not os.path.exists(f"models"):
                os.makedirs(f"models/")
                
            # Model Path default
            self.model_path = "models/" + self.name + ".json"
        else:
            self.model_path = model_path

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
        # ------------------------------------------

        self.helper.printer(f"Digital Twin '{self.name}' created sucessfully at {initial_time_str}", 'green')       
        print(f"--- printing databases paths ---")
        print(f"Digital Database: '{self.database_path}'")
        print(f"Real Database: '{self.real_database_path}'")
        print(f"ID Database: '{self.ID_database_path}'")

    #--- Initiate Broker 
    def initiate_broker(self, ip_address, ID_database_path= None, port= 1883, keepalive= 60, topics_sub = ['trace', 'part_id', 'RCT_server'], topic_pub= 'RCT_server', client = None):
        #--- Take the global features
        self.ip_address = ip_address
        self.topic_pub = topic_pub
        if ID_database_path == None:
            ID_database_path = self.ID_database_path
        
        #--- Create the Broker Manager
        self.broker_manager = Broker_Manager(
            ip_address= self.ip_address,
            real_database_path= self.real_database_path,
            ID_database_path= ID_database_path,
            port= port,
            keepalive= keepalive,
            topics= topics_sub
        )

        return self.broker_manager
        
    #--- Create the Digital Model
    def generate_digital_model(self, until= None, maxparts= None, verbose= True, targeted_part_id = None, targeted_cluster= None):
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

        #--- Copied the Digital into the Real Databse
        if copied_realDB == True:
            shutil.copy2(self.database_path, self.real_database_path)

        #--- Create the Logic Validator 
        validator_logic = Validator(digital_model= self.digital_model, simtype="TDS", real_database_path= self.real_database_path, start_time= start_time, end_time= end_time, copied_realDB= self.copied_realDB)
        
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
        validator_input = Validator(digital_model=self.digital_model, simtype="qTDS", real_database_path= self.real_database_path, start_time= start_time, end_time= end_time, copied_realDB= self.copied_realDB)

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
    def run_sync(self, repositioning = True, start_time= None, end_time= None):
        #--- Make sure the model is updated
        self.generate_digital_model()

        #--- Copied the Digital into the Real Databse
        if self.copied_realDB == True:
            
            #--- before copying, we delete the previous one
            try:
                os.remove(self.real_database_path)
            except FileNotFoundError:
                self.helper.printer(f"[WARNING][Digital_Twin.py/run_sync()] The file '{self.real_database_path}' does not exist")
                print(f"copying file {self.database_path} in the path {self.real_database_path}")

            #--- copy
            shutil.copy2(self.database_path, self.real_database_path)

        #--- Create the synchronizer
        synchronizer = Synchronizer(digital_model= self.digital_model, real_database_path= self.real_database_path, start_time= start_time, end_time= end_time, copied_realDB= self.copied_realDB)

        #--- Run the synchronizer (positioning)
        synchronizer.run(repositioning= repositioning)

    #--- Run RCT Services
    def run_RCT_services(self, verbose= False):
        """
        print("============ Running RCT Services ============")
        #--- Run the Digital Model for the current picture of the system
        if part_id != None and batch == None:
            self.run_digital_model(plot= False, verbose= False, targeted_part_id= part_id + 3)
        if part_id == None and batch != None:
            self.run_digital_model(plot= False, verbose= False, maxparts= batch + 3)

        #--- Calculate the RCT for the given request
        self.digital_model.calculate_RCT(part_id_selected= part_id, batch= batch)
        """
        #--- Create RCT Handler
        
        RCT_Service = Service_Handler(name= "RCT", generate_digital_model= self.generate_digital_model, broker_manager= self.broker_manager)
        RCT_Service.run_RCT_service(verbose=verbose)

    #--- Internal Services (Synchronization and Validation)    
    def Internal_Services(self):
        
        # ====================== Running Synchronization ======================
        if self.flag_time_to_synchronize:
            # --- User Interface
            (current_time_str, ) = self.helper.get_time_now()
            self.helper(f"{current_time_str} |[Internal Service] Starting Synchronization", 'blue')

            # --- Update Start and End time
            start_time = self.last_Tsync
            end_time = self.next_Tsync

            # -------------- Run Synchronization --------------
            #self.run_sync(copied_realDB= self.copied_realDB, start_time= start_time, end_time= end_time)
            # -------------------------------------------------

            sleep(2)

            # --- Send data through API
            # API


            # --------------------- AFTER SERVICES SETTINGS ---------------------
            # --- Validation just finish, so not time to validate anymore
            self.flag_time_to_synchronize = False

            # --- Adjust WHEN WAS the last validation (just happened)
            self.last_Tsync = self.next_Tsync

            # --- Adjust WHEN WILL be the next validation
            self.next_Tsync = self.current_timestamp + self.Freq_Sync

            # --- User Interface
            (current_time_str, ) = self.helper.get_time_now()
            nexttime = datetime.datetime.fromtimestamp(self.next_Tsync).strftime("%d %B %H:%M:%S")
            self.helper(f"{current_time_str} |[Internal Service] System Synchronized. Next Sync: {nexttime}", 'blue')
        
        # ====================== Running Validation ======================
        if  self.flag_time_to_validate:
            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            self.helper(f"{current_time_str} |[Internal Service] Starting Validation", 'blue')


            # --- Update Start and End time
            start_time = self.last_Tsync
            end_time = self.next_Tsync

            # -------------- Run Validation --------------
            #self.run_validation(copied_realDB= self.copied_realDB, start_time= start_time, end_time= end_time)
            # -------------------------------------------------

            sleep(2)

            # --- Send data through API
            # API

            # --------------------- AFTER SERVICES SETTINGS ---------------------
            # --- Validation just finish, so not time to validate anymore
            self.flag_time_to_validate = False

            # --- Adjust WHEN WAS the last validation (just happened)
            self.last_Tvalid = self.next_Tvalid

            # --- Adjust WHEN WILL be the next validation
            self.next_Tvalid = self.current_timestamp + self.Freq_Valid

            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            nexttime = datetime.datetime.fromtimestamp(self.next_Tvalid).strftime("%d %B %H:%M:%S")
            self.helper(f"{current_time_str} |[Internal Service] System Validated. Next Validation: {nexttime}", 'blue')


    #--- External Services (RCT Services and Feedback)
    def External_Services(self):

        # ====================== Running Synchronization ======================
        if self.flag_time_to_rct_service:
            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            self.helper(f"{current_time_str} |[External Service] Starting RCT Service", 'blue')


            # RUN Service
            sleep(2)

            # --------------------- AFTER SERVICES SETTINGS ---------------------
            # --- Validation just finish, so not time to validate anymore
            self.flag_time_to_rct_service = False

            # --- Adjust WHEN WAS the last validation (just happened)
            self.last_Tserv = self.next_Tserv

            # --- Adjust WHEN WILL be the next validation
            self.next_Tserv = self.current_timestamp + self.Freq_Service

            # --- User Interface
            (current_time_str, x) = self.helper.get_time_now()
            nexttime = datetime.datetime.fromtimestamp(self.next_Tserv).strftime("%d %B %H:%M:%S")
            self.helper(f"{current_time_str} |[External Service] System RCT completed. Next Service: {nexttime}", 'blue')



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
            self.helper(f"The Digital Twin named as {self.name} was killed manually", 'red')


        
