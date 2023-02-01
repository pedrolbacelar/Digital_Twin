import mypythonlib
from mypythonlib import myfunctions

import dtpy
import simpy
from dtpy.digital_model import Model

environment = simpy.Environment()
model_5s_closed_no_shadow_path = "models\model_5s_closed_no_shadow.json"
model_5s_closed_no_shadow = Model(name= "model_5s_closed_no_shadow",model_path= model_5s_closed_no_shadow_path, until= 200100, initial=True, env= environment)
model_5s_closed_no_shadow.model_translator()
model_5s_closed_no_shadow.verbose()
model_5s_closed_no_shadow.run()
