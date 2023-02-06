from dtwinpylib.dtwinpy.digital_model import Model

"""
model_2stations_closed_path = "models/model_2stations_closed.json"
database_2stations_closed_path = "databases/2stations_closed_db.db"
model_2stations_closed = Model(name= "model_2stations_closed",model_path= model_2stations_closed_path, database_path=database_2stations_closed_path, until= 201, initial=True)
model_2stations_closed.model_translator()
model_2stations_closed.verbose()
model_2stations_closed.run()
"""

model_5s_closed_no_shadow_path = "models/model_5s_closed_no_shadow.json"
database_5s_closed_no_shadow_path = "databases/5s_closed_no_shadow_db.db"
model_5s_closed_no_shadow = Model(name= "model_5s_closed_no_shadow",model_path= model_5s_closed_no_shadow_path, database_path=database_5s_closed_no_shadow_path, until= 2000100, initial=True)
model_5s_closed_no_shadow.model_translator()
model_5s_closed_no_shadow.verbose()
model_5s_closed_no_shadow.run()