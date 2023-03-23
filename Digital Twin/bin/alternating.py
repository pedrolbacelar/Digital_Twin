from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) 

mydt = Digital_Twin(
    name= "5s_alternating",
    maxparts= 5
)
mydt.run_digital_model()