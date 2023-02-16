#--- Import DT Features
from .digital_model import Model
from .validator import Validator

#--- Reload Package

import importlib
import dtwinpylib
#reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.digital_model)
importlib.reload(dtwinpylib.dtwinpy.validator)

class Digital_Twin():
    def __init__(self, name, model_path, database_path, initial= False, until= None, part_type= "A", loop_type= "closed", maxparts = None):
        #--- Model Parameters
        self.name = name
        self.model_path = model_path
        self.database_path = database_path
        self.initial = initial
        self.until = until
        self.part_type = "A"
        self.loop_type = "closed"
        self.digital_model = None
        self.maxparts = maxparts

    #--- Create the Digital Model
    def generate_digital_model(self):
        self.digital_model = Model(name= self.name,model_path= self.model_path, database_path= self.database_path, until= self.until, initial= self.initial, loop_type= self.loop_type, maxparts= self.maxparts)
        self.digital_model.model_translator()
        self.digital_model.verbose()

        return self.digital_model
    
    #--- Run normally the Digital Model and analyze the results
    def run_digital_model(self):
        if self.digital_model == None:
            self.digital_model = self.generate_digital_model()

        self.digital_model.run()
        self.digital_model.analyze_results()
        self.digital_model.analyze_results(options=["avg_cycle_time"])
    
    #--- Run the Validation
    def run_validation(self, matrix_ptime_qTDS = None, matrix_ptime_TDS = None):
        
        # ================== Trace Driven Simulation (TDS) ==================
        #--- (re)generate the Digital Model (reset)
        self.digital_model = self.generate_digital_model()

        #--- Create the Logic Validator 
        validator_logic = Validator(digital_model= self.digital_model, simtype="TDS", matrix_ptime_TDS=matrix_ptime_TDS)

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
        validator_input = Validator(digital_model=self.digital_model, simtype="qTDS", matrix_ptime_qTDS=matrix_ptime_qTDS)

        #--- Allocate the traces
        validator_input.allocate()

        #--- Run the qTDS
        validator_input.run()

        # ========================================================================