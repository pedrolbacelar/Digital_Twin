#--- Import DT Features
from .digital_model import Model
from .validator import Validator
from .interfaceDB import Database
from .synchronizer import Synchronizer

#--- Reload Package

import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.digital_model)
importlib.reload(dtwinpylib.dtwinpy.validator)
importlib.reload(dtwinpylib.dtwinpy.synchronizer)
importlib.reload(dtwinpylib.dtwinpy.interfaceDB)

class Digital_Twin():
    def __init__(self, name, initial= True, until= None, part_type= "A", loop_type= "closed", maxparts = None):
        #--- Model Parameters
        self.name = name
        self.model_path = "models/" + self.name + ".json"
        self.initial = initial
        self.until = until
        self.part_type = "A"
        self.loop_type = "closed"
        self.digital_model = None
        self.maxparts = maxparts

        #--- Database
        self.database_path = "databases/digital_" + self.name + "_db.db"
        self.real_database_path = "databases/real_" + self.name + "_db.db"
        self.real_database = Database(self.real_database_path, "real_log")
        

    #--- Create the Digital Model
    def generate_digital_model(self):
        self.digital_model = Model(name= self.name,model_path= self.model_path, database_path= self.database_path, until= self.until, initial= self.initial, loop_type= self.loop_type, maxparts= self.maxparts)
        self.digital_model.model_translator()
        self.digital_model.verbose()

        return self.digital_model
    
    #--- Run normally the Digital Model and analyze the results
    def run_digital_model(self):
        #--- Always before running re-generate the model, just in case it has some changes
        self.digital_model = self.generate_digital_model()
        
        #--- Run the simulation
        self.digital_model.run()
        self.digital_model.analyze_results()

    
    #--- Run the Validation
    def run_validation(self):
        
        # ================== Trace Driven Simulation (TDS) ==================
        #--- (re)generate the Digital Model (reset)
        self.digital_model = self.generate_digital_model()

        #--- Create the Logic Validator 
        validator_logic = Validator(digital_model= self.digital_model, simtype="TDS", real_database= self.real_database)
        
        #--- IMPROVE: give the object validator for the machine to be able to update the ptime_TDS for new parts
        #--- Get the components of the simulation
        (machines_vector, queues_vector) = self.digital_model.get_model_components()
        for machine in machines_vector:
            machine.set_validator(validator_logic)
        
        #--- Allocate the traces
        validator_logic.allocate()

        #--- Run the TDS
        validator_logic.run()

        # ========================================================================


        # ================== quasi Trace Driven Simulation (qTDS) ==================

        #--- (re)generate the Digital Model (reset)
        self.digital_model = self.generate_digital_model()

        #--- Create the Input Validator
        validator_input = Validator(digital_model=self.digital_model, simtype="qTDS", real_database= self.real_database)

        #--- Allocate the traces
        validator_input.allocate()

        #--- Run the qTDS
        validator_input.run()

        # ========================================================================

    #--- Run Synchronization
    def run_sync(self, repositioning = True):
        #--- Make sure the model is updated
        self.generate_digital_model()

        #--- Create the synchronizer
        synchronizer = Synchronizer(digital_model= self.digital_model, real_database= self.real_database)

        #--- Run the synchronizer (positioning)
        synchronizer.run(repositioning= repositioning)