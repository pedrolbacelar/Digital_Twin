#--- Import
from dtwinpylib.dtwinpy.helper import Helper
helper = Helper()

#--- Name of the DT
name = '5s_determ'
name = 'testing_negPT'


#--- Delete Databases
helper.delete_databases(name)

#--- Delete models
helper.delete_old_model(f"models/{name}", "initial.json")