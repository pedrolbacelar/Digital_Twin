from dtwinpylib.dtwinpy.tester import Tester
import json
import os
import sqlite3
import numpy as np

#--- create allexp databse
# test.create_allexp_database()

# test = Tester(exp_id='3.27.12.56')
# test.load_exp_setup()
# print(test.initial_json)

#--- calculate CT and TH of system
root_folder = "data_generation"
folder_name= '3.28.10.26'
path = f"{root_folder}/{folder_name}/databases/real_database.db"
test = Tester()
test.calculate_CT(real_db_path=path)
        




"""
#--- write json model to database
root_folder = "data_generation"
folder_name= '3.27.19.50'
model_subfolder_path = f"{root_folder}/{folder_name}/models"
models_list = os.listdir(model_subfolder_path)
test.exp_db_path = f"{root_folder}/{folder_name}/databases/exp_database.db"

conn = sqlite3.connect(test.exp_db_path)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS machine_1")
cursor.execute("DROP TABLE IF EXISTS machine_2")
cursor.execute("DROP TABLE IF EXISTS machine_3")
cursor.execute("DROP TABLE IF EXISTS machine_4")
cursor.execute("DROP TABLE IF EXISTS machine_5")
cursor.execute("DROP TABLE IF EXISTS queue_1")
cursor.execute("DROP TABLE IF EXISTS queue_2")
cursor.execute("DROP TABLE IF EXISTS queue_3")
cursor.execute("DROP TABLE IF EXISTS queue_4")
cursor.execute("DROP TABLE IF EXISTS queue_5")
conn.commit()
conn.close()

test.create_json_model_table()
for model in models_list:
    with open(f"{model_subfolder_path}/{model}") as file:
        # Load the JSON data into a Python object
        print(f"writing {model} into exp_database")
        json_model = json.load(file)
        test.write_json_model(model_dict=json_model, model_name=model)

"""