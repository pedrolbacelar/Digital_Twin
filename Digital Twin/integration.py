from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.interfaceDB import Database

import importlib
import shutil
import sqlite3
import os
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) 
importlib.reload(dtwinpylib.dtwinpy.interfaceDB) 

digital_path = "databases/5s_determ/digital_database.db"
real_path = "databases/5s_determ/real_database.db"

"""


mydt = Digital_Twin(name= "5s_determ", copied_realDB= True)
mydt.run_digital_model(plot= False, verbose= False, maxparts= 5)

shutil.copy2(digital_path, real_path)
os.remove(digital_path)

mydt = Digital_Twin(name= "5s_determ", until= 30000)
mydt.run_digital_model(plot= False, verbose= False)
mydt.run_validation(start_time=0, end_time= 30000)

mydt.run_digital_model(plot= False, verbose= False)

digital_path = mydt.database_path
real_path = "databases/5s_determ/real_database.db"
#shutil.copy2(digital_path, real_path)

database_path = mydt.database_path
mydb = Database(database_path= real_path, copied_realDB=True, event_table= 'real_log')
"""

mydt = Digital_Twin(name= "5s_determ_real", copied_realDB= True, Freq_Service=10, Freq_Sync= 10, Freq_Valid= 30)
mydt.run()