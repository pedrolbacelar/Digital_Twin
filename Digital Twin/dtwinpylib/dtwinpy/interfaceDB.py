from .helper import Helper

import sqlite3
import shutil

class Database():
    def __init__(self, database_path, event_table, start_time = None, end_time= None, copied_realDB= False):
        self.helper = Helper()
        self.database_path = database_path
        self.event_table = event_table

        #--- This both parameters are used to constrain the traces from the real log
        self.start_time = start_time
        self.end_time = end_time
        self.start_time_id = None
        self.end_time_id = None

        #--- When create the object, already create the database and table if doesn't exist
        if event_table == "real_log":
            #--- Check if exist a 'digital_log' (in case of copied databases)
            self.rename_digital_to_real()
                    
            #--- Check to create the table
            self.create_reallog_table()

            # ------- Update the relative time -------
            if start_time != None and end_time != None:
                #--- Take the ID of start and end time
                self.find_line_ID_start_end()
                
                #--- Adjust the start time to always starts with a event 'start'
                #self.update_start_time()
                self.update_end_time()

                #--- Calculate the relative time and update timestamp
                self.updated_relative_timestamp()

                print("---------- Pointer Status ----------")
                print(f"Start Time ID: {self.start_time_id}")
                print(f"End Time ID: {self.end_time_id}")
                print("-------------------------------------")
                    

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

    
    # -------- Setting Functions --------
    def rename_digital_to_real(self):
        with sqlite3.connect(self.database_path) as db:
                tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
                if len(tables) == 1 and tables[0][0] == "digital_log":
                    self.rename_table("digital_log", "real_log")
    
    def create_reallog_table(self):
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

    def find_line_ID_start_end(self):
        with sqlite3.connect(self.database_path) as db:

            self.start_time_id = db.execute(f"""
                SELECT event_id
                FROM real_log
                WHERE timestamp_real >= ?
                ORDER BY timestamp_real ASC
                LIMIT 1
                """, (self.start_time,)).fetchone()

            self.start_time_id = self.start_time_id[0]

            #--- If it's not the first event, always go to the next because
            # when start time is replaced it's replaced as the previous end time
            if self.start_time_id != 1:
                self.start_time_id += 1

            
            self.end_time_id = db.execute(f"""
                SELECT event_id
                FROM real_log
                WHERE timestamp_real <= ?
                ORDER BY timestamp_real DESC
                LIMIT 1
                """, (self.end_time,)).fetchone()
    
            self.end_time_id = self.end_time_id[0]

    def copy_timestamp_to_timestamp_real(self):
        with sqlite3.connect(self.database_path) as db:
            first_time = db.execute("SELECT * FROM real_log").fetchall()
            #--- The timestamp need to have something to you to copy it
            if first_time[0][-1] == None:
                db.execute("UPDATE real_log SET timestamp_real = timestamp")
                db.execute("UPDATE real_log SET timestamp = ?", (None,))
                db.commit

    def updated_relative_timestamp(self):
        with sqlite3.connect(self.database_path) as db:
            first_time = db.execute("SELECT * FROM real_log").fetchall()
            #--- The timestamp need to have something to you to copy it (only for virtual tests)
            if first_time[0][-1] == None:
                db.execute("UPDATE real_log SET timestamp_real = timestamp")

            #--- Clean the timestamp column before updating it again
            db.execute("UPDATE real_log SET timestamp = ?", (None,))

            #rows = db.execute("SELECT * FROM real_log WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time)).fetchall()
            rows = db.execute("SELECT * FROM real_log WHERE event_id >= ? AND event_id <= ?", (self.start_time_id, self.end_time_id)).fetchall()

            # Loop through the selected rows and update the timestamp column with relative values
            start_timestamp = rows[0][-1]
            for row in rows:
                row_event_id = row[0]
                timestamp_real = row[-1]  
                relative_timestamp = timestamp_real - start_timestamp
                db.execute("UPDATE real_log SET timestamp = ? WHERE event_id = ?", (relative_timestamp, row_event_id))

            # Commit the changes and close the database connection
            db.commit()

    def update_start_time(self):
        # we need to do this to be possible to use the relative timestamp
        # otherwise, in the relative we start always with 0 and in the simulation
        # we could start with different than 0. Having 'start' both start with 0

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Check for the most recent 'started' activity_type before the original start time
        cursor.execute(f"""
            SELECT event_id, timestamp_real
            FROM real_log
            WHERE timestamp_real < ?
            AND activity_type = 'Started'
            ORDER BY timestamp_real DESC
            LIMIT 1
        """, (self.start_time,))

        row = cursor.fetchone()

        if row is not None:
            # If there is, return the timestamp_real and line id of the 'started' activity_type as the new start time
            new_start_time = row[1]
            line_id = row[0]

            #---- Update start time
            self.start_time = new_start_time
        else:
            # If there is no 'started' activity_type before the original start time, use the original start time and set line id to None
            new_start_time = self.start_time
            line_id = None

        conn.close()

    def update_end_time(self):
        # we need to do this to be possible to use the relative timestamp
        # otherwise, in the relative we start always with 0 and in the simulation
        # we could start with different than 0. Having 'start' both start with 0

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # Check for the most recent 'started' activity_type before the original start time
        cursor.execute(f"""
            SELECT event_id, timestamp_real
            FROM real_log
            WHERE timestamp_real >= ?
            AND activity_type = 'Started'
            ORDER BY timestamp_real ASC
            LIMIT 1
        """, (self.end_time,))

        #--- Found the next event to be Started
        row = cursor.fetchone()

        #--- Take the rigth position before that event
        started_position = row[0] # line id
        selected_line_id = started_position - 1
        
        #--- Changed the pointer?
        if selected_line_id != self.end_time_id:
            self.helper.printer(f"[interfaceDB.py/update_end_time] Pointer End Time updated from {self.end_time_id} to {selected_line_id}", 'brown')

        #--- Update the end_time
        self.end_time_id = selected_line_id

        conn.close()

    def update_real_time_now(self):
        (time_str, timestamp_now) = self.helper.get_time_now()
        with sqlite3.connect(self.database_path) as db:
            timestamp_real = db.execute(f"""SELECT timestamp_real FROM real_log""").fetchall()
            for timestamp in timestamp_real:
                #--- add the current real timestamp to the virtual timestamp
                timestamp = timestamp[0]
                timestamp_updated = timestamp + timestamp_now
                timestamp_updated = round(timestamp_updated)

                #--- Update in the database
                db.execute("UPDATE real_log SET timestamp_real = ? WHERE timestamp_real = ?", (timestamp_updated, timestamp))

            #-- Commit all the changes
            db.commit()

    def get_current_durantion(self):
        current_durantion = self.end_time - self.start_time
        return current_durantion


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
                #event_points = digital_model_DB.execute(f"SELECT * FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time))
                event_points = digital_model_DB.execute(f"SELECT * FROM {table} WHERE event_id >= ? AND event_id <= ?", (self.start_time_id, self.end_time_id))

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
                #return DB.execute(f"SELECT DISTINCT {column} FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time)).fetchall()
                return DB.execute(f"SELECT DISTINCT {column} FROM {table} WHERE event_id >= ? AND event_id <= ?", (self.start_time_id, self.end_time_id)).fetchall()

            else:
                return DB.execute(f"SELECT DISTINCT {column} FROM {table}").fetchall()

    def get_time_activity_of_column(self, column, column_id, table):
        with sqlite3.connect(self.database_path) as DB:
            if self.start_time != None and self.end_time != None:
                #return DB.execute(f"SELECT timestamp, activity_type FROM {table} WHERE {column}=? AND timestamp_real >= ? AND timestamp_real <= ?", (column_id, self.start_time, self.end_time)).fetchall()
                return DB.execute(f"SELECT timestamp, activity_type FROM {table} WHERE {column}=? AND event_id >= ? AND event_id <= ?", (column_id, self.start_time_id, self.end_time_id)).fetchall()

            else:
                return DB.execute(f"SELECT timestamp, activity_type FROM {table} WHERE {column}=?", (column_id,)).fetchall()

    def get_database_path(self):
        return self.database_path
    
    def read_store_data(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            if self.start_time != None and self.end_time != None:
                #data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time)).fetchall()
                data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id FROM {table} WHERE event_id >= ? AND event_id <= ?", (self.start_time_id, self.end_time_id)).fetchall()

            else:
                data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id FROM {table}").fetchall()
 
            digital_model_DB.commit()
        return data_full_trace
    
    def read_store_data_all(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            if self.start_time != None and self.end_time != None:
                #data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id, queue FROM {table} WHERE timestamp_real >= ? AND timestamp_real <= ?", (self.start_time, self.end_time)).fetchall()
                data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id, queue FROM {table} WHERE event_id >= ? AND event_id <= ?", (self.start_time_id, self.end_time_id)).fetchall()

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
                #return DB.execute(f"SELECT * FROM {table} WHERE part_id=? AND timestamp_real >= ? AND timestamp_real <= ?", (partid, self.start_time, self.end_time)).fetchall()
                return DB.execute(f"SELECT * FROM {table} WHERE part_id=? AND event_id >= ? AND event_id <= ?", (partid, self.start_time_id, self.end_time_id)).fetchall()

            else:
                return DB.execute(f"SELECT * FROM {table} WHERE part_id=?", (partid,)).fetchall()


    def findLine_2conditions(self, table, column1, column2, condition1, condition2):
        with sqlite3.connect(self.database_path) as DB:
            if self.start_time != None and self.end_time != None:
                #return DB.execute(f"SELECT event_id FROM {table} WHERE {column1}=? AND {column2}= ? AND timestamp_real >= ? AND timestamp_real <= ?", (condition1, condition2, self.start_time, self.end_time)).fetchall()
                return DB.execute(f"SELECT event_id FROM {table} WHERE {column1}=? AND {column2}= ? AND event_id >= ? AND event_id <= ?", (condition1, condition2, self.start_time_id, self.end_time_id)).fetchall()

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