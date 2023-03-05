from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class

#mydt = Digital_Twin(name= "5s_dist", maxparts= 10)
mydt = Digital_Twin(name= "5s_determ", maxparts= 30)

mydt.run_digital_model(verbose=False)
mydt.run_validation()