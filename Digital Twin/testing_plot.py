from dtwinpylib.dtwinpy.tester import Plotter
from dtwinpylib.dtwinpy.tester import Tester
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
import sqlite3
import json
import numpy as np


"""
#exp_database_path = 'data_generation/3.27.19.50/databases/exp_database.db'
#exp_database_path = 'data_generation/3.27.19.22/databases/exp_database.db'
exp_database_path= 'data_generation/3.27.18.30/databases/exp_database.db'
exp_database_path= 'databases/5s_stho/exp_database.db'

figures_path = 'figures/test'

plotter = Plotter(
    exp_database_path= exp_database_path,
    show= True,
    figures_path= figures_path
)

plotter.plot_valid_indicators(threshold= 0.69)

#plotter.plot_RCT_paths()

#plotter.plot_queues_occupation(stacked= True)
"""

"""
exp_ids = ['3.28.16.31', '3.28.16.43', '3.28.16.54', '3.28.17.05', '3.28.17.18', '3.28.17.37']

with sqlite3.connect("allexp_database.db") as db:
    all_exp_ids = db.execute(
        "
        #SELECT exp_id FROM experiment_setup
        "
    ).fetchall()

    #--- Adjust tuple
    for i in range(len(all_exp_ids)): all_exp_ids[i] = all_exp_ids[i][0]


for exp_id in all_exp_ids:
    tester = Tester(exp_id=exp_id, from_data_generation= True)
    tester.plot(show_plot= False)
"""
exp_db_path = 'databases/CT/exp_database.db'
real_db_path = 'databases/CT/real_database.db'
fig_path = 'figures/CT'

with sqlite3.connect(exp_db_path) as exp_db:
    exp_db.execute(f"""CREATE TABLE IF NOT EXISTS results (
        result_id INTEGER PRIMARY KEY,
        run_time INTEGER,
        start_time INTEGER,
        finish_time INTEGER,
        last_part TEXT,
        number_of_parts_processed INTEGER,
        throughput_per_seconds FLOAT,
        thourhput_per_hour FLOAT,
        CT_system FLOAT,
        List_parts_finished  TEXT,
        CT_parts TEXT,
        average_CT FLOAT
        )
        """)
    exp_db.commit()

def calculate_CT(real_db_path, exp_db_path):
    with sqlite3.connect(real_db_path) as real_db:
        cursor = real_db.cursor()

        # first and last trace of started nd finished.
        cursor.execute("SELECT * FROM real_log LIMIT 1")
        first_start_time = cursor.fetchone()[-1]

        cursor.execute("SELECT * FROM real_log WHERE machine_id = ? AND activity_type = ? ORDER BY rowid DESC LIMIT 1", ('Machine 5','Finished'))
        event = cursor.fetchall()
        last_finish_time = event[0][-1]
        last_part = event[0][4]
        print(f"last_part to exit is: {last_part}")
        
        # count number of times machine 5 appears with activity as finished
        cursor.execute("SELECT COUNT(*) FROM real_log WHERE machine_id = ? AND activity_type = ?", ('Machine 5','Finished'))
        count = cursor.fetchone()[0]

    #---throughput
    run_time = last_finish_time - first_start_time
    throughput_second = count/run_time #--- parts/second
    throughput_hour = (count*3600)/run_time #--- parts/hour
    ct_system = run_time/count


    print(f"start: {first_start_time}\nstop: {last_finish_time}\nnumber of parts: {count}\nduration: {run_time}\nthroughput per seconds: {throughput_second}\nthourhput per hour: {throughput_hour}\nct_system: {ct_system}")
    
    #--- part level cycle time
    CT_part_time = []
    CT_part_list = []
    #--- cycle time of parts
    with sqlite3.connect(real_db_path) as real_db:
        cursor = real_db.cursor()
        # get a list of the unique values in the column
        values = cursor.execute("SELECT DISTINCT part_id FROM real_log").fetchall()
        # iterate over the values in the column
        for value in values:
            # execute the query with the current value
            start = cursor.execute(f"""SELECT timestamp_real FROM real_log WHERE part_id = '{value[0]}' AND machine_id = 'Machine 1' AND activity_type = 'Started'""").fetchall()

            finish = cursor.execute(f"""SELECT timestamp_real FROM real_log WHERE part_id = '{value[0]}' AND machine_id = 'Machine 5' AND activity_type = 'Finished'""").fetchall()
            # print(start,finish,value[0])
            if finish != []:
                CT_part_time.append(finish[0][0] - start[0][0])
                CT_part_list.append(value[0])
    average_CT = np.mean(CT_part_time)
    print(f"parts finished: {CT_part_list}")
    print(f"cycle time of individual parts: {CT_part_time}")
    print(f"average cycle time of parts: {average_CT}")

    #--- write to results table in exp_db
    with sqlite3.connect(exp_db_path) as exp_db:
        cursor = exp_db.cursor()
        cursor.execute(f"""INSERT INTO results (
        run_time,
        start_time,
        finish_time,
        last_part,
        number_of_parts_processed,
        throughput_per_seconds,
        thourhput_per_hour,
        CT_system,
        List_parts_finished ,
        CT_parts,
        average_CT) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,(run_time,
            first_start_time,
            last_finish_time,
            str(last_part),
            count,
            throughput_second,
            throughput_hour,
            ct_system,
            json.dumps(CT_part_list),
            json.dumps(CT_part_time),
            average_CT))
        
        exp_db.commit()

calculate_CT(real_db_path, exp_db_path)

mydt = Digital_Twin(name= "CT")
plotter = Plotter(
    exp_database_path= exp_db_path,
    plotterDT= mydt,
    figures_path= fig_path,
    show= True
)

plotter.plot_comparative_parts_CT()