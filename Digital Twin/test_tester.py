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
folder_name= '3.27.12.56'
path = f"{root_folder}/{folder_name}/databases/real_database.db"
with sqlite3.connect(path) as real_db:
    cursor = real_db.cursor()

    # first and last trace of started nd finished.
    cursor.execute("SELECT * FROM real_log LIMIT 1")
    first_start_event = cursor.fetchone()[-1]

    cursor.execute("SELECT * FROM real_log WHERE machine_id = ? AND activity_type = ? ORDER BY rowid DESC LIMIT 1", ('Machine 5','Finished'))
    event = cursor.fetchall()
    last_finish_event = event[0][-1]
    last_part = event[0][4]
    print(last_part)
    
    # count number of times machine 5 appears with activity as finished
    cursor.execute("SELECT COUNT(*) FROM real_log WHERE machine_id = ? AND activity_type = ?", ('Machine 5','Finished'))
    count = cursor.fetchone()[0]

#---throughput
run_time = last_finish_event - first_start_event
throughput = count/run_time #--- parts/second
ct_piece = run_time/count

print(f" start {first_start_event}, stop {last_finish_event}, number of parts {count}, duration {run_time}, throughput {throughput}, ct_piece {ct_piece}")
CT_part_time = []
CT_part_list = []
#--- cycle time of parts
with sqlite3.connect(path) as real_db:
    cursor = real_db.cursor()
    # get a list of the unique values in the column
    values = cursor.execute("SELECT DISTINCT part_id FROM real_log").fetchall()
    print(values)
    # iterate over the values in the column
    for value in values:
        if value[0] == last_part:
            break
        # execute the query with the current value
        start = cursor.execute(f"""SELECT timestamp_real FROM real_log WHERE part_id = '{value[0]}' AND machine_id = 'Machine 1' AND activity_type = 'Started'""").fetchall()

        finish = cursor.execute(f"""SELECT timestamp_real FROM real_log WHERE part_id = '{value[0]}' AND machine_id = 'Machine 5' AND activity_type = 'Finished'""").fetchall()
        print(start,finish,value[0])
        if finish != []:
            CT_part_time.append(finish[0][0] - start[0][0])
            CT_part_list.append(value[0])

print(CT_part_list)
print(CT_part_time)
print(np.mean(CT_part_time))
        




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