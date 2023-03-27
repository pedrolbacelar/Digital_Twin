from dtwinpylib.dtwinpy.tester import Tester
import json
import os

#--- create allexp databse
# test.create_allexp_database()

test = Tester()
root_folder = "data_generation"
folder_name= '3.27.15.55'
model_subfolder_path = f"{root_folder}/{folder_name}/models"
models_list = os.listdir(model_subfolder_path)
test.exp_db_path = f"{root_folder}/{folder_name}/databases/exp_database.db"
test.create_json_model_table()
for model in models_list:
    with open(f"{model_subfolder_path}/{model}") as file:
        # Load the JSON data into a Python object
        json_model = json.load(file)
        test.write_json_model(model_dict=json_model, model_name=model)
