#--- Import DT Features
from .digital_model import Model
from .validator import Validator
from .interfaceDB import Database
from .synchronizer import Synchronizer
from .services import Service_Handler

import shutil

#--- Reload Package
import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.digital_model)
importlib.reload(dtwinpylib.dtwinpy.validator)
importlib.reload(dtwinpylib.dtwinpy.synchronizer)
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)


class Digital_Twin():
    def __init__(self, name, initial= True, targeted_part_id= None, until= None, part_type= "A", loop_type= "closed", maxparts = None):
        #--- Model Parameters
        self.name = name
        self.model_path = "models/" + self.name + ".json"
        self.initial = initial
        self.until = until
        self.part_type = "A"
        self.loop_type = "closed"
        self.digital_model = None
        self.maxparts = maxparts
        self.targeted_part_id = targeted_part_id

        #--- Database
        self.database_path = "databases/digital_" + self.name + "_db.db"
        self.real_database_path = "databases/real_" + self.name + "_db.db"
        #self.real_database = Database(self.real_database_path, "real_log")        
        

    #--- Create the Digital Model
    def generate_digital_model(self, maxparts= None, verbose= True, targeted_part_id = None):
        #--- if the functions don't receive nothing, use the default of the Digital Twin
        if maxparts == None:
            maxparts = self.maxparts

        #--- If the target conditions doesn't exist, assign it
        if targeted_part_id == None:
            targeted_part_id = self.targeted_part_id

        #--- Update the global maxparts and target part
        self.maxparts = maxparts
        self.targeted_part_id = targeted_part_id
        
        #--- Create the digital model with all the properties
        self.digital_model = Model(name= self.name,model_path= self.model_path, 
            database_path= self.database_path, until= self.until, initial= self.initial, 
            loop_type= self.loop_type, maxparts= maxparts,targeted_part_id=targeted_part_id)
        
        #--- Translate the digital model
        self.digital_model.model_translator()
        #--- Verbose if necessary
        if verbose == True:
            self.digital_model.verbose()

        return self.digital_model
    
    #--- Run normally the Digital Model and analyze the results
    def run_digital_model(self, plot= True, maxparts = None, targeted_part_id = None, verbose= True, generate_model = True):
        if generate_model == True:
            #--- Always before running re-generate the model, just in case it has some changes
            self.digital_model = self.generate_digital_model(maxparts= maxparts, targeted_part_id= targeted_part_id, verbose= verbose)
        
        #--- Run the simulation
        self.digital_model.run()
        
        #--- Plot Results
        if plot == True:
            self.digital_model.analyze_results()

    
    #--- Run the Validation
    def run_validation(self, copied_realDB= False):
        
        # ================== Trace Driven Simulation (TDS) ==================
        #--- (re)generate the Digital Model (reset)
        self.digital_model = self.generate_digital_model()

        #--- Copied the Digital into the Real Databse
        if copied_realDB == True:
            shutil.copy2(self.database_path, self.real_database_path)

        #--- Create the Logic Validator 
        validator_logic = Validator(digital_model= self.digital_model, simtype="TDS", real_database_path= self.real_database_path)
        
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
        self.digital_model = self.generate_digital_model()

        #--- Create the Input Validator
        validator_input = Validator(digital_model=self.digital_model, simtype="qTDS", real_database_path= self.real_database_path)

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
    def run_sync(self, repositioning = True, copied_realDB= False):
        #--- Make sure the model is updated
        self.generate_digital_model()

        #--- Copied the Digital into the Real Databse
        if copied_realDB == True:
            shutil.copy2(self.database_path, self.real_database_path)

        #--- Create the synchronizer
        synchronizer = Synchronizer(digital_model= self.digital_model, real_database_path= self.real_database_path)

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
        RCT_Service = Service_Handler(name= "RCT", generate_digital_model= self.generate_digital_model)
        RCT_Service.run_RCT_service(verbose=verbose)

        
