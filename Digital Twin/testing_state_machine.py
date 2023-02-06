from dtwinpylib.dtwinpy.digital_model import Model

model_2stations_closed_path = "models/model_2stations_closed.json"
database_2stations_closed_path = "databases/2stations_closed_db.db"
model_2stations_closed = Model(name= "model_2stations_closed",model_path= model_2stations_closed_path, database_path=database_2stations_closed_path, until= 201, initial=True)
model_2stations_closed.model_translator()
model_2stations_closed.verbose()
model_2stations_closed.run()