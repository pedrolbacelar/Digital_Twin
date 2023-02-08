from dtwinpylib.dtwinpy.digital_model import Model

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.digital_model) #reload this specifc module to upadte the class

model_multiple2one_case1_path = "models/models_simple/models_multiple_one/model_case1.json"
database_multiple2one_case1_path = "databases/database_simple/database_multiple_one/database_case1.db"
model_multiple2one_case1 = Model(name= "model_case1",model_path= model_multiple2one_case1_path, database_path=database_multiple2one_case1_path, until= 201, initial=True, loop_type= "open")
model_multiple2one_case1.model_translator()
model_multiple2one_case1.verbose()
model_multiple2one_case1.run()