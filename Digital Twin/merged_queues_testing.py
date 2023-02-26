from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class


digital_twin = Digital_Twin(
    name= "merging_non_parallel"
)
digital_model = digital_twin.generate_digital_model()