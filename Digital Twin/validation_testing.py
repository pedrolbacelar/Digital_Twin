from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin) #reload this specifc module to upadte the class

digital_twin = Digital_Twin(name= "model_2stations_closed",
    model_path= "models/model_2stations_closed.json",
    database_path="databases/2stations_closed_db.db",
    until= 4000, initial=True, maxparts=4)

digital_model = digital_twin.generate_digital_model()


matrix_ptime_TDS = [
    [10,10],
    [15,15],
    [20,20]
]

matrix_ptime_qTDS = [
    [1000,100,100,100],
    [2000,200,200,200],
]

digital_twin.run_validation(matrix_ptime_qTDS=matrix_ptime_qTDS, matrix_ptime_TDS=matrix_ptime_TDS)
