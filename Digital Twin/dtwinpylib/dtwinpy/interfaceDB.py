from .helper import Helper

import sqlite3
import shutil
import sys
from time import sleep
import keyboard

class Database():
    def __init__(self, database_path, event_table, feature_usingDB= None,start_time = None, end_time= None, copied_realDB= False):
        self.helper = Helper()
        #--- Common attributes
        self.database_path = database_path
        self.event_table = event_table
        self.feature_usingDB = feature_usingDB

        #--- This both parameters are used to constrain the traces from the real log
        self.start_time = start_time
        self.end_time = end_time

        self.start_time_id = None
        self.end_time_id = None

        self.start_time_status = None
        self.end_time_status = None

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

                print("---------- Pointer Status Initial ----------")
                print(f"Start Time: {self.start_time}")
                print(f"Start Time ID: {self.start_time_id}")
                
                print()
                print(f"End Time: {self.end_time}")
                print(f"End Time ID: {self.end_time_id}")
                
                print("-------------------------------------")

                
                
                #--- Adjust the start time to always starts with a event 'start'
                #self.update_start_time()
                self.update_end_time()

                #--- Calculate the relative time and update timestamp
                self.updated_relative_timestamp()

                #--- Update table of time pointers
                self.write_updated_start_end()

                print("---------- Pointer Status Updated ----------")
                print(f"Start Time: {self.start_time}")
                print(f"Start Time ID: {self.start_time_id}")
                if self.start_time_status == "Finished":
                    self.helper.printer("[ERROR][interfaceDB.py/__init__()] Pointer Start Time is 'Finished'. Not Allowed! Check logic or external interference.", 'red')
                    sys.exit()

                print()
                print(f"End Time: {self.end_time}")
                print(f"End Time ID: {self.end_time_id}")
            
                print("-------------------------------------")
                
                #--- Check for parts without the correct id within the traces
                self.check_parts_zero()

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
                    current_time_str TEXT,
                    palletID TEXT
                )
                """)

                db.commit()

        if event_table == "time_pointers":
            """
            This object just read the most recent end time. Nothing to do when initiating.
            """
            pass
    
        if event_table == "replicated_log":
            #--- Create the path of the new replicated database
            old_database_path= self.database_path.replace(".db","")
            self.replicated_database_path= f"{old_database_path}_replicated.db"
            

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
                SELECT event_id, activity_type
                FROM real_log
                WHERE timestamp_real >= ?
                ORDER BY timestamp_real ASC
                LIMIT 1
                """, (self.start_time,)).fetchone()
            
            if self.start_time_id == None:
                #--- Printer Error Message
                self.helper.printer(f"[ERROR][interfaceDB.py/find_line_ID_start_end()] It was not possible to find any event after the start time: {self.start_time}", 'red')
                (tstr, t) = self.helper.get_time_now()
                
                #--- Killing the program
                self.helper.printer(f"---- Digital Twin killed at {tstr} ----", 'red')
                sys.exit()

            # --- Update Start Pointers
            self.start_time_status = self.start_time_id[1]
            self.start_time_id = self.start_time_id[0]

            # --- Update Start Time in case of 'Finished'
            if self.start_time_status == "Finished":
                #--- Take by force the line id rigth before the last end time
                next_start_time_id = self.forced_update_start_time()
                self.helper.printer(f"[WARNING][interfaceDB.py/find_line_ID_start_end()] Changed Start Time by force because a initial trace was 'Finished'. Jumping start time id from {self.start_time_id} to {next_start_time_id}.")
                
                #--- update the start time id
                self.start_time_id = next_start_time_id

                #--- update the start time
                with sqlite3.connect(self.database_path) as db:
                    row= db.execute("""SELECT timestamp_real, activity_type FROM real_log WHERE event_id= ? """, (self.start_time_id,)).fetchone()
                    self.start_time= row[0]
                    self.start_time_status= row[1]

            self.end_time_id = db.execute(f"""
                SELECT event_id, activity_type
                FROM real_log
                WHERE timestamp_real <= ?
                ORDER BY timestamp_real DESC
                LIMIT 1
                """, (self.end_time,)).fetchone()
            
            if self.end_time_id == None:
                #--- Printer Error Message
                self.helper.printer(f"[ERROR][interfaceDB.py/find_line_ID_start_end()] It was not possible to find any event before the end time: {self.end_time}", 'red')
                (tstr, t) = self.helper.get_time_now()
                
                #--- Killing the program
                self.helper.printer(f"---- Digital Twin killed at {tstr} ----", 'red')
                sys.exit()
    
            # --- Update End Pointers
            self.end_time_status = self.end_time_id[1]
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

        looping = True
        try_counter = 1
        max_counter = 5
        #--- Timeout Loop
        while looping == True and try_counter <= max_counter:
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
            
            #--- Stop Conditions
            if row != None:
                # Found a started
                looping = False

            else:
                (time_str, time) = self.helper.get_time_now()
                self.helper.printer(f"[interfaceDB.py/update_end_time] Not found 'Started' after the end_time: {self.end_time}. Sleeping for 10 seconds and trying again", 'brown')
                #--- Sleep for the next try
                sleep(10)

                #--- Updated the trying counter
                try_counter += 1
        
        if try_counter > max_counter:
            #--- Printer Error Message
            (tstr, t) = self.helper.get_time_now()

            self.helper.printer(f"[ERROR][interfaceDB.py/update_end_time()] After trying {max_counter} times, it was not possible to find a 'Started' event after the end time: {self.end_time}", 'red')
            
            
            #--- Killing the program
            self.helper.printer(f"---- Digital Twin killed at {tstr} ----", 'red')
            sys.exit()
        

        #--- Take the rigth position before that event
        started_position = row[0] # line id
        selected_line_id = started_position - 1
        
        #--- Changed the pointer?
        if selected_line_id != self.end_time_id:
            (time_str, time) = self.helper.get_time_now()
            self.helper.printer(f"[interfaceDB.py/update_end_time] Pointer End Time updated from {self.end_time_id} to {selected_line_id}", 'brown')

        #--- Update the end_time
        self.end_time_id = selected_line_id

        #--- Take the updated end_time
        self.end_time = cursor.execute("""SELECT timestamp_real FROM real_log WHERE event_id= ? """, (selected_line_id,)).fetchone()[0]


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

    def check_parts_zero(self):
        with sqlite3.connect(self.database_path) as db:
            flag_not_missing_part_id = True
            sleep_time = 5
            timeout_max = 3
            timeout_counter = 1

            while flag_not_missing_part_id== True and timeout_counter <= timeout_max:
                (time_str, time) = self.helper.get_time_now()
                
                parts_zero = db.execute("SELECT * FROM real_log WHERE part_id= ? AND event_id >= ? AND event_id <= ?", ('Part 0', self.start_time_id, self.end_time_id)).fetchall()
                print(f"parts_zero: {parts_zero}")
                if len(parts_zero) == 0:
                    flag_not_missing_part_id = False
                else:
                    self.helper.printer(f"[WARNING][interfaceDB.py/check_parts_zero()] A Part 0 (without correct ID) was detected within the traces... Sleeping for {sleep_time} seconds")
                    sleep(sleep_time)
                    timeout_counter += 1
            
            if timeout_counter > timeout_max:
                self.helper.printer(f"[ERROR][interfaceDB.py/check_parts_zero()] After trying {timeout_max} ({timeout_max * sleep_time} seconds), there are still Part 0 within the selected trace. Most probably the some ESP32 is not detecting correctly the RFID Sticker", 'red')
                
                #--- Killing the program
                (tstr, t) = self.helper.get_time_now()
                self.helper.printer(f"---- Digital Twin killed at {tstr} ----", 'red')
                sys.exit()

    def get_current_durantion(self):
        current_durantion = self.end_time - self.start_time
        return current_durantion

    def write_updated_start_end(self):
        with sqlite3.connect(self.database_path) as db:
            #--- Create table for pointer
            db.execute(f"""
            CREATE TABLE IF NOT EXISTS time_pointers (
                line_id INTEGER PRIMARY KEY,
                current_time_str TEXT,
                start_time INTEGER,
                end_time INTEGER,
                start_time_id INTEGER,
                end_time_id INTEGER,
                feature_usingDB TEXT
            )
            """)
            db.commit()

            #--- Get current time
            (time_str, time) = self.helper.get_time_now()

            #--- Write the new pointers
            db.execute("""
            INSERT INTO time_pointers (current_time_str, start_time, end_time, start_time_id, end_time_id, feature_usingDB)
            VALUES (?, ?, ?, ?, ?, ?)""", (time_str, self.start_time, self.end_time, self.start_time_id, self.end_time_id, self.feature_usingDB)
            )

            db.commit()
    
    def read_last_end_time(self):
        with sqlite3.connect(self.database_path) as db:
            end_times = db.execute("""
            SELECT end_time FROM time_pointers
            """).fetchall()
            
            last_end_time = end_times[-1][0]

            return last_end_time
            
    def forced_update_start_time(self):
        with sqlite3.connect(self.database_path) as db:
            last_sync_endID = db.execute("""
                SELECT end_time_id from time_pointers WHERE feature_usingDB= ?
            """, (self.feature_usingDB,)).fetchall()
            
            last_sync_endID = last_sync_endID[-1][0]
            next_sync_startID = last_sync_endID + 1
        
        return next_sync_startID

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


    def update_column(self, table, column, line_id, new_value, current_time_str_):
        with sqlite3.connect(self.database_path) as DB:
            DB.execute(f"UPDATE {table} SET {column} = ?, current_time_str= ? WHERE event_id = ?", (new_value, current_time_str_, line_id))
            DB.commit()

    # --------- Function to add a UID and partid to the table ---------
    def add_UID_partid(self, table_name, uid, partid, current_time_str, palletID):
        with sqlite3.connect(self.database_path) as DB:
            # Check if UID already exists in table
            result = DB.execute(f"SELECT UID FROM {table_name} WHERE UID = ?", (uid,)).fetchone()
            if result is None:
                # UID does not exist in table, so insert new row
                DB.execute(f"INSERT INTO {table_name} (UID, PID, current_time_str, palletID) VALUES (?, ?, ?, ?)", (uid, partid, current_time_str, palletID))
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
            
    # --------- Database Replicator Function ---------
    def replicate_database(self):
        
        # --- Copy targeted database
        #shutil.copy2(self.database_path, self.replicated_database_path)

        # --- clear the table of the old database
        with sqlite3.connect(self.database_path) as db:
            db.execute(f"DROP TABLE IF EXISTS real_log")
            db.execute(f"DROP TABLE IF EXISTS time_pointers")
            db.commit()

        with sqlite3.connect(self.database_path) as db:
            #--- Create the table if not exist:
            db.execute(f"""
                CREATE TABLE IF NOT EXISTS real_log (
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

        with sqlite3.connect(self.replicated_database_path) as old_db:
            last_event_id = old_db.execute(f"""SELECT MAX(event_id) FROM real_log""").fetchone()[0]
            print(f"total number of traces = {last_event_id}")

            print("====== Starting database replicator ======")

            try:
                for ii in range(last_event_id):
                    event_id = ii + 1
                    current_event = old_db.execute(f"""SELECT * FROM real_log WHERE event_id = ?""",(event_id,)).fetchone()
                    if event_id == last_event_id:
                        break
                    else:
                        next_event_time = old_db.execute(f"""SELECT * FROM real_log WHERE event_id = ?""",(event_id+1,)).fetchone()[7]
                        wait = next_event_time - current_event[7]

                    print(f"current event_id : {current_event[0]}, machine_id : {current_event[2]}, status : {current_event[3]}, part_id : {current_event[4]}, queue_id : {current_event[5]}")
                    
                    #--- Assign properties
                    machine_id= current_event[2]
                    activity_type = current_event[3]
                    part_id= current_event[4]
                    queue= current_event[5]


                    #--- Insert data from the replicated DB into the real database
                    with sqlite3.connect(self.database_path) as db:
                        
                        #--- Take current time
                        (timestamp_str, timestamp) = self.helper.get_time_now()
                        timestamp = round(timestamp)

                        #--- Insert 
                        db.execute("""
                            INSERT INTO real_log (machine_id, activity_type, part_id, queue, current_time_str, timestamp_real)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (machine_id, activity_type, part_id, queue, timestamp_str, timestamp))

                        db.commit()

                    #--- we sleep between the traces
                    print(f"Next trace in {wait} seconds")
                    sleep(wait)

                self.helper.printer("---- Replication Done Successfully ----", 'green')

            except KeyboardInterrupt:
                self.helper.printer("---- Replication Killed ----", 'red')
            
            