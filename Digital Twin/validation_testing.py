from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class

digital_twin = Digital_Twin(name= "model_5s_closed_no_shadow_real", initial=True, maxparts=20)
digital_twin.run_digital_model()
digital_twin.run_validation()