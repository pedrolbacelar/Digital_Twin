from dtwinpylib.dtwinpy.digital_model import Model

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.digital_model) #reload this specifc module to upadte the class

model_path = "models/models_simple/models_one_multiple/model_case1.json"
database_path = "databases/database_simple/database_one_multiple/database_case1.db"
model = Model(name= "model_case3",model_path= model_path, database_path=database_path, initial=True, loop_type= "open")
model.model_translator()
model.verbose()
model.run()
#model.analyze_results()