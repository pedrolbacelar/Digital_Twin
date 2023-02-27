from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.interfaceDB import Database


import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class
importlib.reload(dtwinpylib.dtwinpy.interfaceDB) #reload this specifc module to upadte the class

"""
name = "5s_allocation"
digital_twin = Digital_Twin(name= name,maxparts=5, initial=True )
digital_twin.run_digital_model()
digital_twin.run_sync()
"""
name = "5s_merging_sync"
digital_twin = Digital_Twin(name= name,maxparts=10)
digital_twin.generate_digital_model()
digital_twin.run_digital_model()

