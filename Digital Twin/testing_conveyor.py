from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin


import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class


mydt = Digital_Twin(name="conveyors", maxparts= 20)
mydt.run_digital_model()