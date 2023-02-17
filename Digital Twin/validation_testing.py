from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class

name = "5s_closed_distribution"
digital_twin = Digital_Twin(name = name, initial= True, maxparts=30)
digital_twin.run_digital_model()
digital_twin.run_validation()