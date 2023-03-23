from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) 

mydt = Digital_Twin(
    name= "5s_determ",
    verbose= True
)
mydt.generate_digital_model(verbose= True)
mydt.run_RCT_services(queue_position= 4)
