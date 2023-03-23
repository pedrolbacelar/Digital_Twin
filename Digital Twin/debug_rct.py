from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.interfaceDB import Database
import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class

mydt = Digital_Twin(name="debug_rct", ip_address= "127.0.0.1")

"""
#mydt.run_RCT_services(queue_position= 2)
#mydt.run_digital_model(maxparts=10)
#--- Create a Database object for ID database
ID_database_path= "databases/debug_rct/ID_database.db"
ID_database = Database(database_path= ID_database_path, event_table= "ID")

#--- Get model components
digital_model = mydt.generate_digital_model(maxparts=5)
(machines_vector, queues_vector) = digital_model.get_model_components()

# ------- Assign Parts Queue Branches selected -------
parts_branch_queue = ID_database.read_parts_branch_queue()
for machine in machines_vector:
    machine.set_parts_branch_queue(parts_branch_queue)

digital_model.run()

"""

mydt.run_RCT_services(queue_position=2, rct_threshold= 0)
