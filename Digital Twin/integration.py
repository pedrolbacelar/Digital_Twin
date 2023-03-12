from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.interfaceDB import Database

import importlib
import sqlite3
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) 
importlib.reload(dtwinpylib.dtwinpy.interfaceDB) 

mydt = Digital_Twin(name= "5s_determ")
mydt.run_digital_model(plot= True, verbose= False, targeted_part_id= 4, targeted_cluster= 1)
mydt.run_sync(copied_realDB= True)