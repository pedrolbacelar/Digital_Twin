from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class


digital_twin = Digital_Twin(
    name= "5s_merging",
    maxparts= 100
)
digital_model = digital_twin.generate_digital_model()
digital_twin.run_digital_model()