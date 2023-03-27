
import sqlite3
import json
import os
import shutil
import sys

class Tester():
    def __init__(self, exp_id = 'recent'):
        
        #--- attributes from allexp_database
        self.allexp_path = 'allexp_database.db'
        self.allexp_table = 'experiment_setup'
        self.exp_id = exp_id
        
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
                n_parts_Q5 INTEGER DEFAULT '[]'
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
            self.timestamp = exp_setup[0][1]
            self.objective = exp_setup[0][2]
            self.name= exp_setup[0][3]
            self.Freq_Sync= exp_setup[0][4] 
            self.Freq_Valid= exp_setup[0][5] 
            self.Freq_Service= exp_setup[0][6]
            self.delta_t_treshold=exp_setup[0][7]
            self.flag_API= True if exp_setup[0][8] == 'True' else False
            self.rct_threshold= exp_setup[0][9]
            self.rct_queue= exp_setup[0][10]
            self.flag_external_service= True if exp_setup[0][11] == 'True' else False
            self.logic_threshold= exp_setup[0][12]
            self.input_threshold= exp_setup[0][13]

            self.initial_json = {
                "nodes": [
                    {
                    "activity": 1,
                    "predecessors": json.loads(exp_setup[0][14]),
                    "successors": json.loads(exp_setup[0][15]),
                    "frequency": exp_setup[0][16],
                    "capacity": exp_setup[0][17],
                    "contemp": exp_setup[0][18],
                    "cluster": exp_setup[0][19],
                    "worked_time": exp_setup[0][20]
                    },
                    {
                    "activity": 2,
                    "predecessors": json.loads(exp_setup[0][21]),
                    "successors": json.loads(exp_setup[0][22]),
                    "frequency": exp_setup[0][23],
                    "capacity": exp_setup[0][24],
                    "contemp": exp_setup[0][25],
                    "cluster": exp_setup[0][26],
                    "worked_time": exp_setup[0][27],
                    "allocation_counter": exp_setup[0][28]
                    },
                    {
                    "activity": 3,
                    "predecessors": json.loads(exp_setup[0][29]),
                    "successors": json.loads(exp_setup[0][30]),
                    "frequency": exp_setup[0][31],
                    "capacity": exp_setup[0][32],
                    "contemp": exp_setup[0][33],
                    "cluster": exp_setup[0][34],
                    "worked_time": exp_setup[0][35]
                    },
                    {
                    "activity": 4,
                    "predecessors": json.loads(exp_setup[0][36]),
                    "successors": json.loads(exp_setup[0][37]),
                    "frequency": exp_setup[0][38],
                    "capacity": exp_setup[0][39],
                    "contemp": exp_setup[0][40],
                    "cluster": exp_setup[0][41],
                    "worked_time": exp_setup[0][42]
                    },
                    {
                    "activity": 5,
                    "predecessors": json.loads(exp_setup[0][43]),
                    "successors": json.loads(exp_setup[0][44]),
                    "frequency": exp_setup[0][45],
                    "capacity": exp_setup[0][46],
                    "contemp": exp_setup[0][47],
                    "cluster": exp_setup[0][48],
                    "worked_time": exp_setup[0][49]
                    }
                ],
                "arcs": [
                    {
                    "arc": json.loads(exp_setup[0][54]),
                    "capacity": exp_setup[0][55],
                    "frequency": exp_setup[0][56],
                    "contemp": exp_setup[0][57]
                    },
                    {
                    "arc": json.loads(exp_setup[0][58]),
                    "capacity": exp_setup[0][59],
                    "frequency": exp_setup[0][60],
                    "contemp": exp_setup[0][61]
                    },
                    {
                    "arc": json.loads(exp_setup[0][62]),
                    "capacity":exp_setup[0][63],
                    "frequency": exp_setup[0][64],
                    "contemp": exp_setup[0][65]
                    },
                    {
                    "arc": json.loads(exp_setup[0][66]),
                    "capacity": exp_setup[0][67],
                    "frequency": exp_setup[0][68],
                    "contemp": exp_setup[0][69]
                    },
                    {
                    "arc": json.loads(exp_setup[0][70]),
                    "capacity": exp_setup[0][71],
                    "frequency": exp_setup[0][72],
                    "contemp": exp_setup[0][73]
                    },
                    {
                    "arc": json.loads(exp_setup[0][50]),
                    "capacity":exp_setup[0][51],
                    "frequency": exp_setup[0][52],
                    "contemp": exp_setup[0][53]
                    }
                ],
                "initial": [
                    json.loads(exp_setup[0][74]),
                    json.loads(exp_setup[0][75]),
                    json.loads(exp_setup[0][76]),
                    json.loads(exp_setup[0][77]),
                    json.loads(exp_setup[0][78])
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
                """,(self.exp_id, self.timestamp, self.objective, self.name, self.Freq_Sync, 
                        self.Freq_Valid, self.Freq_Service, self.delta_t_treshold, self.flag_API, 
                        self.rct_threshold, self.rct_queue, self.flag_external_service, self.logic_threshold, 
                        self.input_threshold))
                exp_db.commit()

    #--- create exp_models_tables for all machines
    def create_exp_machines_table(self, machine_id, branching = False):
        if branching == False:        
            with sqlite3.connect(self.exp_db_path) as exp_db:
                exp_db.execute(f"""CREATE TABLE IF NOT EXISTS machine_{machine_id} (
                    model_name TEXT PRIMARY KEY,
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
                    model_name TEXT PRIMARY KEY,
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
                    model_name TEXT PRIMARY KEY,
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
                    model_name TEXT PRIMARY KEY,
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

