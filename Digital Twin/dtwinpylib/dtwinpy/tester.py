from dtwinpylib.dtwinpy.helper import Helper
from dtwinpylib.dtwinpy.interfaceDB import Database

#--- Commom Libraries
import sqlite3
import json
import os
from dtwinpylib.dtwinpy.helper import Helper
import numpy as np
import shutil
import sys
from matplotlib import pyplot as plt


class Tester():
    def __init__(self, exp_id = 'recent', name= None, exp_db_path = None):
        
        #--- attributes from allexp_database
        self.allexp_path = 'allexp_database.db'
        self.allexp_table = 'experiment_setup'
        self.exp_id = exp_id
        self.exp_db_path = exp_db_path
        self.helper = Helper()

        #--- Create the experimental database (if name)
        if name != None:
            self.name = name
            #-- exp path
            self.exp_db_path = f"databases/{self.name}/exp_database.db"
            #-- create a Database object
            self.exp_db = Database(
                exp_database_path= self.exp_db_path,
                experimental_mode= True
            )
        
        
    def initiate(self):
        #--- loading the experiment setup from allexp
        self.load_exp_setup()
        self.replace_initial_json()


        self.exp_db_path = f"databases/{self.name}/exp_database.db"
        self.exp_setup_table = "setup_data"

        
        self.delete_exp_database()  #--- delete existing exp_database to create new
        self.create_exp_database()  #--- create new exp_db and create setup_data table
        self.write_setup()          #--- write setup data from allexp_db to exp_db setup_data table
        
        
        


#-------------------------------------------------------------------------------------------------
#---------------------------------------- MAIN FUNCTIONS -----------------------------------------
#-------------------------------------------------------------------------------------------------

    #--- to create experimental_data table
    def create_allexp_database(self):
        with sqlite3.connect(self.allexp_path) as allexp:
            allexp.execute(f"""CREATE TABLE IF NOT EXISTS {self.allexp_table} (
                exp_id TEXT PRIMARY KEY DEFAULT 'recent',
                timestamp TEXT,
                objective TEXT,
                dt_name TEXT DEFAULT '5s_determ',
                Freq_Sync INTEGER DEFAULT 2,
                Freq_Valid INTEGER DEFAULT 30,
                Freq_Service INTEGER DEFAULT 2,
                delta_t_treshold INTEGER DEFAULT 20,
                flag_API TEXT DEFAULT 'True',
                rct_threshold FLOAT DEFAULT 0,
                rct_queue INTEGER DEFAULT 2,
                flag_external_service INTEGER DEFAULT 'True',
                logic_threshold FLOAT DEFAULT 0.8,
                input_threshold FLOAT DEFAULT 0.8,

                predecessors_M1 TEXT DEFAULT '[5]',
                successors_M1 TEXT DEFAULT '[2]',
                frequency_M1 INTEGER DEFAULT 999,
                capacity_M1 INTEGER DEFAULT 1,
                contemp_M1 INTEGER DEFAULT 11,
                cluster_M1 INTEGER DEFAULT 1,
                worked_time_M1 INTEGER DEFAULT 0,

                predecessors_M2 TEXT DEFAULT '[1]',
                successors_M2 TEXT DEFAULT '[3,4]',
                frequency_M2 INTEGER DEFAULT 999,
                capacity_M2 INTEGER DEFAULT 1,
                contemp_M2 INTEGER DEFAULT 17,
                cluster_M2 INTEGER DEFAULT 2,
                worked_time_M2 INTEGER DEFAULT 0,
                allocation_counter INTEGER DEFAULT 0,

                predecessors_M3 TEXT DEFAULT '[2]',
                successors_M3 TEXT DEFAULT '[5]',
                frequency_M3 INTEGER DEFAULT 999,
                capacity_M3 INTEGER DEFAULT 1,
                contemp_M3 INTEGER DEFAULT 60,
                cluster_M3 INTEGER DEFAULT 3,
                worked_time_M3 INTEGER DEFAULT 0,

                predecessors_M4 TEXT DEFAULT '[2]',
                successors_M4 TEXT DEFAULT '[5]',
                frequency_M4 INTEGER DEFAULT 999,
                capacity_M4 INTEGER DEFAULT 1,
                contemp_M4 INTEGER DEFAULT 38,
                cluster_M4 INTEGER DEFAULT 3,
                worked_time_M4 INTEGER DEFAULT 0,

                predecessors_M5 TEXT DEFAULT '[3,4]',
                successors_M5 TEXT DEFAULT '[1]',
                frequency_M5 INTEGER DEFAULT 999,
                capacity_M5 INTEGER DEFAULT 1,
                contemp_M5 INTEGER DEFAULT 10,
                cluster_M5 INTEGER DEFAULT 4,
                worked_time_M5 INTEGER DEFAULT 0,

                arc_Q1 TEXT DEFAULT '[5,1]',
                capacity_Q1 INTEGER DEFAULT 12,
                frequency_Q1 INTEGER DEFAULT 1000,
                contemp_Q1 INTEGER DEFAULT 9,

                arc_Q2 TEXT DEFAULT '[1,2]',
                capacity_Q2 INTEGER DEFAULT 10,
                frequency_Q2 INTEGER DEFAULT 1000,
                contemp_Q2 INTEGER DEFAULT 11,

                arc_Q3 TEXT DEFAULT '[2,3]',
                capacity_Q3 INTEGER DEFAULT 10,
                frequency_Q3 INTEGER DEFAULT 1000,
                contemp_Q3 INTEGER DEFAULT 23,

                arc_Q4 TEXT DEFAULT '[2,4]',
                capacity_Q4 INTEGER DEFAULT 10,
                frequency_Q4 INTEGER DEFAULT 1000,
                contemp_Q4 INTEGER DEFAULT 20,

                arc_Q5_1 TEXT DEFAULT '[3,5]',
                capacity_Q5_1 INTEGER DEFAULT 10,
                frequency_Q5_1 INTEGER DEFAULT 1000,
                contemp_Q5_1 INTEGER DEFAULT 11,

                arc_Q5_2 TEXT DEFAULT '[4,5]',
                capacity_Q5_2 INTEGER DEFAULT 10,
                frequency_Q5_2 INTEGER DEFAULT 1000,
                contemp_Q5_2 INTEGER DEFAULT 6,

                n_parts_Q1 INTEGER DEFAULT '["Part 1","Part 2","Part 3","Part 4","Part 5","Part 6","Part 7","Part 8","Part 9","Part 10","Part 11","Part 12"]',
                n_parts_Q2 INTEGER DEFAULT '[]',
                n_parts_Q3 INTEGER DEFAULT '[]',
                n_parts_Q4 INTEGER DEFAULT '[]',
                n_parts_Q5 INTEGER DEFAULT '[]',
                flag_publish TEXT DEFAULT True
            )
            """)
            allexp.commit()

    #--- load all the setup variables from allexp_database
    def load_exp_setup(self):
        with sqlite3.connect(self.allexp_path) as allexp:
            cursor = allexp.cursor()
            exp_setup = cursor.execute(f"""SELECT * FROM {self.allexp_table} WHERE exp_id = '{self.exp_id}'""").fetchall()
            
            #-- setup variables read from the database
            self.exp_id = exp_setup[0][0]
            self.objective = exp_setup[0][1]
            self.name= exp_setup[0][2]
            self.Freq_Sync= exp_setup[0][3] 
            self.Freq_Valid= exp_setup[0][4] 
            self.Freq_Service= exp_setup[0][5]
            self.delta_t_treshold=exp_setup[0][6]
            self.flag_API= True if exp_setup[0][7] == 'True' else False
            self.rct_threshold= exp_setup[0][8]
            self.rct_queue= exp_setup[0][9]
            self.flag_external_service= True if exp_setup[0][10] == 'True' else False
            self.logic_threshold= exp_setup[0][11]
            self.input_threshold= exp_setup[0][12]
            self.flag_publish= True if exp_setup[0][78] == 'True' else False

            self.initial_json = {
                "nodes": [
                    {
                    "activity": 1,
                    "predecessors": json.loads(exp_setup[0][13]),
                    "successors": json.loads(exp_setup[0][14]),
                    "frequency": exp_setup[0][15],
                    "capacity": exp_setup[0][16],
                    "contemp": exp_setup[0][17],
                    "cluster": exp_setup[0][18],
                    "worked_time": exp_setup[0][19]
                    },
                    {
                    "activity": 2,
                    "predecessors": json.loads(exp_setup[0][20]),
                    "successors": json.loads(exp_setup[0][21]),
                    "frequency": exp_setup[0][22],
                    "capacity": exp_setup[0][23],
                    "contemp": exp_setup[0][24],
                    "cluster": exp_setup[0][25],
                    "worked_time": exp_setup[0][26],
                    "allocation_counter": exp_setup[0][27]
                    },
                    {
                    "activity": 3,
                    "predecessors": json.loads(exp_setup[0][28]),
                    "successors": json.loads(exp_setup[0][29]),
                    "frequency": exp_setup[0][30],
                    "capacity": exp_setup[0][31],
                    "contemp": exp_setup[0][32],
                    "cluster": exp_setup[0][33],
                    "worked_time": exp_setup[0][34]
                    },
                    {
                    "activity": 4,
                    "predecessors": json.loads(exp_setup[0][35]),
                    "successors": json.loads(exp_setup[0][36]),
                    "frequency": exp_setup[0][37],
                    "capacity": exp_setup[0][38],
                    "contemp": exp_setup[0][39],
                    "cluster": exp_setup[0][40],
                    "worked_time": exp_setup[0][41]
                    },
                    {
                    "activity": 5,
                    "predecessors": json.loads(exp_setup[0][42]),
                    "successors": json.loads(exp_setup[0][43]),
                    "frequency": exp_setup[0][44],
                    "capacity": exp_setup[0][45],
                    "contemp": exp_setup[0][46],
                    "cluster": exp_setup[0][47],
                    "worked_time": exp_setup[0][48]
                    }
                ],
                "arcs": [
                    {
                    "arc": json.loads(exp_setup[0][53]),
                    "capacity": exp_setup[0][54],
                    "frequency": exp_setup[0][55],
                    "contemp": exp_setup[0][56]
                    },
                    {
                    "arc": json.loads(exp_setup[0][57]),
                    "capacity": exp_setup[0][58],
                    "frequency": exp_setup[0][59],
                    "contemp": exp_setup[0][60]
                    },
                    {
                    "arc": json.loads(exp_setup[0][61]),
                    "capacity":exp_setup[0][62],
                    "frequency": exp_setup[0][63],
                    "contemp": exp_setup[0][64]
                    },
                    {
                    "arc": json.loads(exp_setup[0][65]),
                    "capacity": exp_setup[0][66],
                    "frequency": exp_setup[0][67],
                    "contemp": exp_setup[0][68]
                    },
                    {
                    "arc": json.loads(exp_setup[0][69]),
                    "capacity": exp_setup[0][70],
                    "frequency": exp_setup[0][71],
                    "contemp": exp_setup[0][72]
                    },
                    {
                    "arc": json.loads(exp_setup[0][49]),
                    "capacity":exp_setup[0][50],
                    "frequency": exp_setup[0][51],
                    "contemp": exp_setup[0][52]
                    }
                ],
                "initial": [
                    json.loads(exp_setup[0][73]),
                    json.loads(exp_setup[0][74]),
                    json.loads(exp_setup[0][75]),
                    json.loads(exp_setup[0][76]),
                    json.loads(exp_setup[0][77])
                ]
                }
            
    #--- replace the existing initial json file in models folder with the data from allexp_database
    def replace_initial_json(self):
        json_path = f"models/{self.name}/initial.json"
        with open(json_path, 'w') as file:
            json.dump(self.initial_json, file)

    #--- delete existing exp_database
    def delete_exp_database(self):
        if os.path.exists(self.exp_db_path):
            os.remove(self.exp_db_path)
            print(f"Existing exp_database deleted")
        else:
            print(f"No exp_database was found. New one will be created.")

    #--- to create exp_database and experimental_data table
    def create_exp_database(self):
        with sqlite3.connect(self.exp_db_path) as exp_db:
                exp_db.execute(f"""CREATE TABLE IF NOT EXISTS {self.exp_setup_table} (
                    exp_id TEXT PRIMARY KEY DEFAULT 'recent',
                    timestamp TEXT,
                    objective TEXT,
                    dt_name TEXT DEFAULT '5s_determ',
                    Freq_Sync INTEGER DEFAULT 2,
                    Freq_Valid INTEGER DEFAULT 30,
                    Freq_Service INTEGER DEFAULT 2,
                    delta_t_treshold INTEGER DEFAULT 20,
                    flag_API TEXT DEFAULT 'True',
                    rct_threshold FLOAT DEFAULT 0,
                    rct_queue INTEGER DEFAULT 2,
                    flag_external_service INTEGER DEFAULT 'True',
                    logic_threshold FLOAT DEFAULT 0.8,
                    input_threshold FLOAT DEFAULT 0.8
                    )
                    """)
                exp_db.commit()

    #--- write mydt definitions
    def write_setup(self):
        with sqlite3.connect(self.exp_db_path) as exp_db:
                cursor = exp_db.cursor()
                cursor.execute(f"""INSERT INTO {self.exp_setup_table} (
                    exp_id,
                    timestamp,
                    objective,
                    dt_name,
                    Freq_Sync,
                    Freq_Valid,
                    Freq_Service,
                    delta_t_treshold,
                    flag_API,
                    rct_threshold,
                    rct_queue,
                    flag_external_service,
                    logic_threshold,
                    input_threshold) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,(self.exp_id, self.helper.get_time_now()[0], self.objective, self.name, self.Freq_Sync, 
                        self.Freq_Valid, self.Freq_Service, self.delta_t_treshold, str(self.flag_API), 
                        self.rct_threshold, self.rct_queue, str(self.flag_external_service), self.logic_threshold, 
                        self.input_threshold))
                exp_db.commit()

    #--- create exp_models_tables for all machines
    def create_exp_machines_table(self, machine_id, branching = False):
        if branching == False:        
            with sqlite3.connect(self.exp_db_path) as exp_db:
                exp_db.execute(f"""CREATE TABLE IF NOT EXISTS machine_{machine_id} (
                    model_id INTEGER PRIMARY KEY,
                    model_name TEXT,
                    predecessors TEXT,
                    successors TEXT,
                    frequency INTEGER,
                    capacity INTEGER,
                    contemp INTEGER,
                    cluster INTEGER,
                    worked_time TEXT
                )
                """)
                exp_db.commit()
        elif branching == True:
            with sqlite3.connect(self.exp_db_path) as exp_db:
                exp_db.execute(f"""CREATE TABLE IF NOT EXISTS machine_{machine_id} (
                    model_id INTEGER PRIMARY KEY,
                    model_name TEXT,
                    predecessors TEXT,
                    successors TEXT,
                    frequency INTEGER,
                    capacity INTEGER,
                    contemp INTEGER,
                    cluster INTEGER,
                    worked_time TEXT,
                    allocation_counter INTEGER DEFAULT 0
                )
                """)
                exp_db.commit()

    #--- create exp_models_tables for all queues
    def create_exp_queues_table(self, queue_id, converging = False):
        if converging == False:        
            with sqlite3.connect(self.exp_db_path) as exp_db:
                exp_db.execute(f"""CREATE TABLE IF NOT EXISTS queue_{queue_id} (
                    model_id INTEGER PRIMARY KEY,
                    model_name TEXT,
                    arc TEXT,
                    capacity INTEGER,
                    frequency INTEGER,
                    contemp INTEGER,

                    n_parts INTEGER
                    )
                    """)
                exp_db.commit()
        elif converging == True:
            with sqlite3.connect(self.exp_db_path) as exp_db:
                exp_db.execute(f"""CREATE TABLE IF NOT EXISTS queue_{queue_id} (
                    model_id INTEGER PRIMARY KEY,
                    model_name TEXT,
                    arc_1 TEXT,
                    capacity_1 INTEGER,
                    frequency_1 INTEGER,
                    contemp_1 INTEGER,

                    arc_2 TEXT,
                    capacity_2 INTEGER,
                    frequency_2 INTEGER,
                    contemp_2 INTEGER,

                    n_parts INTEGER
                    )
                """)
                exp_db.commit()

    def write_queue_table(self,queue_id, arc_id, model_dict, model_name, arc_id_secondary = None):
        with sqlite3.connect(self.exp_db_path) as exp_db:
            cursor = exp_db.cursor()
            if arc_id_secondary == None:
                cursor.execute(f"""INSERT INTO queue_{queue_id} (
                model_name,
                arc,
                capacity,
                frequency,
                contemp,
                n_parts) VALUES (?,?,?,?,?,?)
                """,(str(model_name), 
                    json.dumps(model_dict['arcs'][arc_id]['arc']),
                    model_dict['arcs'][arc_id]['capacity'],
                    model_dict['arcs'][arc_id]['frequency'],
                    model_dict['arcs'][arc_id]['contemp'],
                    json.dumps(model_dict['initial'][queue_id-1])))
            
            else:
                cursor.execute(f"""INSERT INTO queue_{queue_id} (
                model_name,
                arc_1,
                capacity_1,
                frequency_1,
                contemp_1,

                arc_2,
                capacity_2,
                frequency_2,
                contemp_2,

                n_parts) VALUES (?,?,?,?,?,?,?,?,?,?)
                """,(str(model_name), 
                    json.dumps(model_dict['arcs'][arc_id]['arc']),
                    model_dict['arcs'][arc_id]['capacity'],
                    model_dict['arcs'][arc_id]['frequency'],
                    model_dict['arcs'][arc_id]['contemp'],
                    json.dumps(model_dict['arcs'][arc_id_secondary]['arc']),
                    model_dict['arcs'][arc_id_secondary]['capacity'],
                    model_dict['arcs'][arc_id_secondary]['frequency'],
                    model_dict['arcs'][arc_id_secondary]['contemp'],
                    json.dumps(model_dict['initial'][queue_id-1])))
            
            exp_db.commit()
    
    #--- write json models into the models_table in exp_database
    def write_json_model(self, model_dict, model_name):
        with sqlite3.connect(self.exp_db_path) as exp_db:
            cursor = exp_db.cursor()
            #--- write machine tables
            for machine_id in range(1,6):
                cursor.execute(f"""INSERT INTO machine_{machine_id} (
                model_name,
                predecessors,
                successors,
                frequency,
                capacity,
                contemp,
                cluster,
                worked_time) VALUES (?,?,?,?,?,?,?,?)
                """,(str(model_name), 
                    json.dumps(model_dict['nodes'][machine_id-1]['predecessors']),
                    json.dumps(model_dict['nodes'][machine_id-1]['successors']),
                    model_dict['nodes'][machine_id-1]['frequency'],
                    model_dict['nodes'][machine_id-1]['capacity'],
                    model_dict['nodes'][machine_id-1]['contemp'],
                    model_dict['nodes'][machine_id-1]['cluster'],
                    json.dumps(model_dict['nodes'][machine_id-1]['worked_time'])))

            #--- write allocation counter for machine 2    
            cursor.execute(f"""UPDATE machine_2 SET allocation_counter = {model_dict['nodes'][1]['allocation_counter']} WHERE model_name = '{model_name}'""")
            
            #--- save changes
            exp_db.commit()
            
            #--- write queue tables for non converging queues
            self.write_queue_table(queue_id = 1, arc_id=5,model_dict = model_dict, model_name = model_name, arc_id_secondary=None)   
            self.write_queue_table(queue_id = 2, arc_id=0,model_dict = model_dict, model_name = model_name, arc_id_secondary=None)   
            self.write_queue_table(queue_id = 3, arc_id=1,model_dict = model_dict, model_name = model_name, arc_id_secondary=None)   
            self.write_queue_table(queue_id = 4, arc_id=2,model_dict = model_dict, model_name = model_name, arc_id_secondary=None)   
            self.write_queue_table(queue_id = 5, arc_id=3,model_dict = model_dict, model_name = model_name, arc_id_secondary=4)   

    #--- main function to call and create all the required machine and queue tables in exp_database
    def create_json_model_table(self):
        #--- create tables for machines and queues
        self.create_exp_machines_table(machine_id = 1, branching = False)
        self.create_exp_machines_table(machine_id = 2, branching = True)
        self.create_exp_machines_table(machine_id = 3, branching = False)
        self.create_exp_machines_table(machine_id = 4, branching = False)
        self.create_exp_machines_table(machine_id = 5, branching = False)
        
        self.create_exp_queues_table(queue_id = 1, converging = False)
        self.create_exp_queues_table(queue_id = 2, converging = False)
        self.create_exp_queues_table(queue_id = 3, converging = False)
        self.create_exp_queues_table(queue_id = 4, converging = False)
        self.create_exp_queues_table(queue_id = 5, converging = True)

    #--- assign exp_id to the 'recent' experiment in the allexp_database and exp_database
    def assign_exp_id(self,exp_id):
        #--- updating in allexp
        with sqlite3.connect(self.allexp_path) as allexp:
            cursor = allexp.cursor()
            cursor.execute(f"""UPDATE {self.allexp_table} SET exp_id = '{exp_id}' WHERE exp_id = 'recent'""")
            allexp.commit()
        #--- updating in exp_db
        with sqlite3.connect(self.exp_db_path) as exp_db:
            cursor = exp_db.cursor()
            cursor.execute(f"""UPDATE setup_data SET exp_id = '{exp_id}' WHERE exp_id = 'recent'""")
            exp_db.commit()
        self.exp_id = exp_id

    #--- create results table
    def create_results_table(self):
        with sqlite3.connect(self.exp_db_path) as exp_db:
            exp_db.execute(f"""CREATE TABLE IF NOT EXISTS global_results (
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


    def calculate_CT(self, real_db_path):
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

        with sqlite3.connect(self.exp_db_path) as exp_db:
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
            average_CT FLOAT) VALUES (?,?,?,?,?,?,?,?,?,?,?)
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




class Plotter():
    def __init__(self, exp_database_path, figures_path= None,  show= False, save= True):
        #--- Experimental Database
        self.exp_database_path = exp_database_path
        self.exp_database = Database(
            database_path= self.exp_database_path
        )

        #--- Figures Folder
        self.figures_path = figures_path

        #--- Common flags
        self.show = show
        self.save = save

        #--- vector of markers and colors
        self.markers = ['o', '*', '^', 's', 'd', 'v', 'p', 'x', '+']
        self.colors = ['blue', 'orange', 'green', 'red' , 'purple']

    #--- Basic Functions ---
    def ADD_complemts(self, title, xlable, ylable):
        """ Adds title, x lable and y lable"""

        plt.title(title)
        plt.xlabel(xlable)
        plt.ylabel(ylable)
        plt.legend()
    
    def set_max_min(self, xlim= None, ylim= None):
        """ Set max and min for x and y. Receive vectors"""
        if xlim:
            plt.xlim(xlim)
        if ylim:
            plt.ylim(ylim)

    def save_fig(self, name):
        """Function takes the figure path and save the given figure using the given name"""
        path_to_save = f"{self.figures_path}/{name}.png"
        
        print(f"path to save fig: {path_to_save}")

        plt.savefig(path_to_save)


    def plot_valid_indicators(self, threshold= None, adjust = True):
        """
        This functions plots the validation indicators (logic and input) from
        the experimental database. If threshold is given, the function also
        trace the line of the threshold in the plot.
        """

        #--- Read logic indicators
        (logic_indicators, timestamp) = self.exp_database.read_ValidIndicator('logic_indicator')
        print(f"logic_indicators: {logic_indicators}")

        #--- read input indicators
        (input_indicators, timestamp) = self.exp_database.read_ValidIndicator('input_indicator')
        print(f"input_indicators: {input_indicators}")

        print(f"timestamp: {timestamp}")

        #--- Add complements
        self.ADD_complemts(
            title= "Validation Indicators",
            xlable= "Timestamp (secs)",
            ylable= "Indicator (%)"
        )

        #--- Plot logic indicator
        plt.plot(timestamp, logic_indicators, marker='o', label= 'logic_indicator')

        #--- Plot input indicator
        plt.plot(timestamp, input_indicators, marker= 'x', label= 'input_indicator')

        #--- Add threshold line
        if threshold:   plt.axhline(threshold, color='red', linestyle='--', label='Indicator Threshold')
        
        #--- Adjust the scale of the graph
        if adjust: self.set_max_min(ylim=[0, 1.05])
        
        #--- Save
        if self.save:
            self.save_fig("Validation_Indicators")

        #--- Show
        if self.show:
            plt.show()

    def plot_RCT_paths(self):
        """
        This functions plots the validation indicators (logic and input) from
        the experimental database. If threshold is given, the function also
        trace the line of the threshold in the plot.
        """

        #--- Read RCT paths
        (rct_path1, rct_path2, timestamp) = self.exp_database.read_RCT_path()

        #--- Add complements
        self.ADD_complemts(
            title= "RCT Paths 1 and 2",
            xlable= "Timestamp (secs)",
            ylable= "RCT"
        )

        #--- Plot logic indicator
        plt.plot(timestamp, rct_path1, marker='o', label= 'Path 1 (Queue 3)')

        #--- Plot input indicator
        plt.plot(timestamp, rct_path2, marker= 'o', label= 'Path 2 (Queue 4)')

        
        #--- Save
        if self.save:
            self.save_fig("RCT_Path")

        #--- Show
        if self.show:
            plt.show()

    def plot_queues_occupation(self, number_queues = 5, stacked= False):
        """
        Loop through the queues table to get the amount of parts in the queue
        after each synchronization. Plot this amount over time.
        """
        #--- Create a dictionary to store the occupation of each queue
        queue_occupation = {}

        #--- Loop through all the queues id 
        for i in range(0, number_queues):
            #-- Create Queue ID
            queue_id= i + 1

            #-- Extract occupation vector
            occupation_vector = self.exp_database.read_queue_occupation(queue_id)

            #-- Add the occupation of this queue in the global dictionary
            queue_occupation[f'Queue {queue_id}'] = occupation_vector
        
        #--- Create the x_vector (syncs) with the same length as the queue_occupation
        x_vector = []
        for i in range(len(occupation_vector)):x_vector.append(i)

        # ------ Plot for each queue ------
        if stacked == False:
            marker = 0
            for i in range(0, number_queues): 
                #-- Create Queue ID
                queue_id= i + 1

                #--- reset markers
                if marker > len(self.markers): marker = 0

                # ------------------ PLOT ----------------------
                plt.plot(
                    x_vector, 
                    queue_occupation[f'Queue {queue_id}'],
                    label= f'Queue {queue_id}',
                    color= self.colors[marker]
                
                )
                # -------------------------------------------------

                #--- Increase marker for the next
                marker += 1
        if stacked == True:
            #--- creator matrix with queue occupation
            stacked_vector = []
            labels = []
            for key in queue_occupation:
                stacked_vector.append(queue_occupation[key])
                labels.append(key)

            plt.stackplot(
                x_vector,
                stacked_vector,
                labels= labels
            )

        #--- Add complements
        self.ADD_complemts(
            title= "Queues Occupation",
            xlable= "Number of Sync",
            ylable= "Parts in Queue"
        )

        #--- Save
        if self.save:
            self.save_fig("Queues_Occupation")

        #--- Show
        if self.show:
            plt.show()

        # --------------------- COMPARE QUEUE 3 AND QUEUE 4 ---------------------
        marker = 2
        if stacked == False:
            for i in range(2, 4): 
                #-- Create Queue ID
                queue_id= i + 1

                #--- reset markers
                if marker > len(self.markers): marker = 0

                # ------------------ PLOT ----------------------
                plt.plot(
                    x_vector, 
                    queue_occupation[f'Queue {queue_id}'],
                    label= f'Queue {queue_id}',
                    color= self.colors[marker]
                )
                # -------------------------------------------------

                #--- Increase marker for the next
                marker += 1
        if stacked == True:
            #--- creator matrix with queue occupation
            stacked_vector = [queue_occupation['Queue 3'], queue_occupation['Queue 4']]
            labels = ['Queue 3', 'Queue 4']

            plt.stackplot(
                x_vector,
                queue_occupation['Queue 3'],
                queue_occupation['Queue 4'],
                labels= labels
            )


        #--- Add complements
        self.ADD_complemts(
            title= "Queue 3 x Queue 4",
            xlable= "Number of Sync",
            ylable= "Parts in Queue"
        )

        #--- Save
        if self.save:
            self.save_fig("Queues_Occupation_3_4")

        #--- Show
        if self.show:
            plt.show()