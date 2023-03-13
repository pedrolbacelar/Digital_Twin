import sqlite3
import shutil

class Database():
    def __init__(self, database_path, event_table, start_time = None, end_time= None, copied_realDB= False):
        self.database_path = database_path
        self.event_table = event_table

        #--- This both parameters are used to constrain the traces from the real log
        self.start_time = start_time
        self.end_time = end_time

        #--- When create the object, already create the database and table if doesn't exist
        if event_table == "real_log":
            #--- Check if exist a 'digital_log' (in case of copied databases)
            with sqlite3.connect(self.database_path) as db:
                tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
                if len(tables) == 1 and tables[0][0] == "digital_log":
                    self.rename_table("digital_log", "real_log")
                    
            #--- Check to create the table
            with sqlite3.connect(self.database_path) as db:
                db.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.event_table} (
                    event_id INTEGER PRIMARY KEY,
                    timestamp INTEGER,
                    machine_id TEXT,
                    activity_type TEXT,
                    part_id TEXT,
                    queue TEXT,
                    current_time_str TEXT,
                    timestamp_real INTEGER
                )
                """)

                db.commit()

            #--- Copy the timestamp to timestamp_real
            if copied_realDB == True:
                with sqlite3.connect(self.database_path) as db:
                    first_time = db.execute("SELECT * FROM real_log").fetchall()
                    #--- The timestamp need to have something to you to copy it
                    if first_time[0][-1] == None:
                        db.execute("UPDATE real_log SET timestamp_real = timestamp")
                        db.execute("UPDATE real_log SET timestamp = ?", (None,))
                        db.commit

            #--- Update timestamp according to the relative time
            if start_time != None and end_time != None:
                with sqlite3.connect(self.database_path) as db:
                    first_time = db.execute("SELECT * FROM real_log").fetchall()
                    #--- The timestamp need to have something to you to copy it (only for virtual tests)
                    if first_time[0][-1] == None:
                        db.execute("UPDATE real_log SET timestamp_real = timestamp")

                    rows = db.execute("SELECT * FROM real_log WHERE timestamp_real >= ? AND timestamp_real <= ?", (start_time, end_time)).fetchall()
                    # Loop through the selected rows and update the timestamp column with relative values
                    start_timestamp = rows[0][-1]
                    for row in rows:
                        timestamp_real = row[-1]  
                        relative_timestamp = timestamp_real - start_timestamp
                        db.execute("UPDATE real_log SET timestamp = ? WHERE timestamp_real = ?", (relative_timestamp, timestamp_real))

                    # Commit the changes and close the database connection
                    db.commit()

            

        if event_table == "digital_log":
            with sqlite3.connect(self.database_path) as digital_model_DB:
                digital_model_DB.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.event_table} (
                    event_id INTEGER PRIMARY KEY,
                    timestamp INTEGER,
                    machine_id TEXT,
                    activity_type TEXT,
                    part_id TEXT,
                    queue TEXT
                )
                """)

                digital_model_DB.commit()


        if event_table == "ID":
            with sqlite3.connect(self.database_path) as db:
                db.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.event_table} (
                    line_id INTEGER PRIMARY KEY,
                    UID TEXT,
                    PID TEXT,
                    current_time_str TEXT
                )
                """)

                db.commit()

    
    def initialize(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB:

            digital_model_DB.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                event_id INTEGER PRIMARY KEY,
                timestamp INTEGER,
                machine_id TEXT,
                activity_type TEXT,
                part_id TEXT,
                queue TEXT,
                current_time_str TEXT,
                timestamp_real INTEGER
            )
            """)

            digital_model_DB.commit()
    
    def clear(self, table):
        #--- clear all the data written in {table}

        with sqlite3.connect(self.database_path) as digital_model_DB:
            digital_model_DB.execute(f"DROP TABLE IF EXISTS {table}")
            digital_model_DB.commit()


    def write_event(self, table, timestamp, machine_id, activity_type, part_id, queue, current_time_str= None, timestamp_real= None):
        #--- Write the given evento into the the database
        
        with sqlite3.connect(self.database_path) as DB: 
            if table == "real_log":
                DB.execute(f"""
                INSERT INTO {table} (timestamp, machine_id, activity_type, part_id, queue, current_time_str, timestamp_real)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (0, machine_id, activity_type, part_id, queue, current_time_str, timestamp_real))

            if table == "digital_log":
                DB.execute(f"""
                INSERT INTO {table} (timestamp, machine_id, activity_type, part_id, queue)
                VALUES (?, ?, ?, ?, ?)""", (timestamp, machine_id, activity_type, part_id, queue))

            DB.commit()
    
    

    def read_all_events(self, table):
        #--- Read all the events from the given table
        
        print(f"=== Reading all the events from table: {table} ===")
        with sqlite3.connect(self.database_path) as digital_model_DB:
            if self.start_time != None and self.end_time != None:
                event_points = digital_model_DB.execute(f"SELECT * FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time))
            else:
                event_points = digital_model_DB.execute(f"SELECT * FROM {table}")
            for event_point in event_points:
                print(event_point)
            digital_model_DB.commit()

    def get_event_table(self):
        return self.event_table

    def get_distinct_values(self, column, table):
        with sqlite3.connect(self.database_path) as DB:
            if self.start_time != None and self.end_time != None:
                return DB.execute(f"SELECT DISTINCT {column} FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time)).fetchall()

            else:
                return DB.execute(f"SELECT DISTINCT {column} FROM {table}").fetchall()

    def get_time_activity_of_column(self, column, column_id, table):
        with sqlite3.connect(self.database_path) as DB:
            if self.start_time != None and self.end_time != None:
                return DB.execute(f"SELECT timestamp, activity_type FROM {table} WHERE {column}=? AND timestamp_real >= ? AND timestamp_real <= ?", (column_id, self.start_time, self.end_time)).fetchall()
            else:
                return DB.execute(f"SELECT timestamp, activity_type FROM {table} WHERE {column}=?", (column_id,)).fetchall()

    def get_database_path(self):
        return self.database_path
    
    def read_store_data(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            if self.start_time != None and self.end_time != None:
                data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time)).fetchall()
            else:
                data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id FROM {table}").fetchall()
 
            digital_model_DB.commit()
        return data_full_trace
    
    def read_store_data_all(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            if self.start_time != None and self.end_time != None:
                data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id, queue FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time)).fetchall()
            else:
                data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id, queue FROM {table}").fetchall()
        
            digital_model_DB.commit()
        return data_full_trace

    def rename_table(self, table_old, table_new):
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            digital_model_DB.execute(f"ALTER TABLE {table_old} RENAME TO {table_new};")
            digital_model_DB.commit()

    def read_part_path(self, partid, table):
        with sqlite3.connect(self.database_path) as DB:
            if self.start_time != None and self.end_time != None:
                return DB.execute(f"SELECT * FROM {table} WHERE part_id=? AND timestamp_real >= ? AND timestamp_real <= ?", (partid, self.start_time, self.end_time)).fetchall()

            else:
                return DB.execute(f"SELECT * FROM {table} WHERE part_id=?", (partid,)).fetchall()


    def findLine_2conditions(self, table, column1, column2, condition1, condition2):
        with sqlite3.connect(self.database_path) as DB:
            if self.start_time != None and self.end_time != None:
                return DB.execute(f"SELECT event_id FROM {table} WHERE {column1}=? AND {column2}= ? AND timestamp_real >= ? AND timestamp_real <= ?", (condition1, condition2, self.start_time, self.end_time)).fetchall()
            else:
                return DB.execute(f"SELECT event_id FROM {table} WHERE {column1}=? AND {column2}= ? ", (condition1, condition2)).fetchall()


    def update_column(self, table, column, line_id, new_value):
        with sqlite3.connect(self.database_path) as DB:
            DB.execute(f"UPDATE {table} SET {column} = ? WHERE event_id = ?", (new_value, line_id))
            DB.commit()

    # --------- Function to add a UID and partid to the table ---------
    def add_UID_partid(self, table_name, uid, partid, current_time_str):
        with sqlite3.connect(self.database_path) as DB:
            # Check if UID already exists in table
            result = DB.execute(f"SELECT UID FROM {table_name} WHERE UID = ?", (uid,)).fetchone()
            if result is None:
                # UID does not exist in table, so insert new row
                DB.execute(f"INSERT INTO {table_name} (UID, PID, current_time_str) VALUES (?, ?, ?)", (uid, partid, current_time_str))
            else:
                # UID already exists in table, so update existing row
                DB.execute(f"UPDATE {table_name} SET PID = ? WHERE UID = ?", (partid, uid))
            DB.commit()
    
    # --------- Function to retrieve PID for a given partid ---------
    def get_PID(self, table_name, partid):
        with sqlite3.connect(self.database_path) as DB:
            result = DB.execute(f"SELECT UID FROM {table_name} WHERE PID = ?", (partid,)).fetchone()
            if result is None:
                #--- [ERROR] Part ID not stored in dictionary
                print(f"[ERROR][interfaceDB.py/get_PID()] The part id '{partid}' was not found in the database: '{self.database_path}'")
                print("Sending a generic UID: {x}")
                return "x"
            else:
                return result[0]