from .helper import Helper

import sqlite3
import shutil
import sys
from time import sleep

class Database():
    def __init__(self, database_path, event_table= None, feature_usingDB= None,start_time = None, end_time= None, copied_realDB= False, model_update= False, experimental_mode= False):
        self.helper = Helper()
        #--- Common attributes
        self.database_path = database_path
        self.event_table = event_table
        self.feature_usingDB = feature_usingDB
        self.model_update = model_update
        self.experimental_mode = experimental_mode
        self.copied_realDB = copied_realDB

        #--- This both parameters are used to constrain the traces from the real log
        self.start_time = start_time
        self.end_time = end_time

        self.start_time_id = None
        self.end_time_id = None

        self.start_time_status = None
        self.end_time_status = None

        # --- Threshold for trials
        self.looping = True
        self.try_counter = 1
        self.sleep_time = 1
        self.timeout = 30 # TODO: input variable for DT
        self.max_counter= round(self.timeout/self.sleep_time)

        #--- When create the object, already create the database and table if doesn't exist
        if event_table == "real_log" and self.model_update == False and self.experimental_mode== False:
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

        #--- Database for Model Update ---
        if self.model_update == True:
            """ 
            In this case, you just need to take the lines ID of the start and finish
            of the previous validation, don't need to update it. 
            """
            with sqlite3.connect(self.database_path) as db:
                valid_pointers = db.execute("""SELECT start_time_id, end_time_id FROM time_pointers WHERE feature_usingDB= ?""", ('valid_logic',)).fetchall()

                #--- Take the most recent id of start and end time (last validation - that needs to be updated)
                self.start_time_id = valid_pointers[-1][0]
                self.end_time_id = valid_pointers[-1][1]

                print("-- Time Pointers Conisdered for Model Update: --")
                print(f"|-- Start Time ID: {self.start_time_id}")
                print(f"|-- End Time ID: {self.start_time_id}")
        
        # --- Database for Experimental Mode ---
        if self.experimental_mode == True:
            """
            When creating the experimental database (in the __init__ of the Digital Twin), the object
            already create all the necessary tables with all the columns needed
            """
            # --- Create table for validation indicators
            self.create_valid_indicator_table()

            # --- Create table for RCT path
            self.create_RCTpaths_table()

            

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
                    palletID TEXT,
                    branch_queue TEXT
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
            
    # -------- Creation of Tables --------
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
    
    def create_valid_indicator_table(self):
        # TODO: Finish up
        with sqlite3.connect(self.database_path) as db:
                # --- Create table of validator indicators
                db.execute("""
                CREATE TABLE IF NOT EXISTS valid_indicators(
                    line_id INTEGER PRIMARY KEY,
                    current_time_str TEXT,
                    timestamp_real INTEGER,
                    logic_indicator FLOAT,
                    input_indicator FLOAT,
                    model_in TEXT,
                    model_out TEXT
                )
                """)

                db.commit()

    def create_RCTpaths_table(self):
        with sqlite3.connect(self.database_path) as db:
            #--- Create a table with the RCT of each path
            db.execute("""
            CREATE TABLE IF NOT EXISTs RCTpaths (
                line_id INTEGER PRIMARY KEY,
                current_time_str TEXT,
                timestamp_real INTEGER,
                RCT_path1 INTEGER,
                RCT_path2 INTEGER,
                queue_selected TEXT,
                gain INTEGER,
                partid TEXT
            )
            
            """)



    # -------- Setting Functions --------
    def rename_digital_to_real(self):
        with sqlite3.connect(self.database_path) as db:
                tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
                if len(tables) == 1 and tables[0][0] == "digital_log":
                    self.rename_table("digital_log", "real_log")
    
    def find_line_ID_start_end(self):
        with sqlite3.connect(self.database_path) as db:
            
            # ------------------------------------------ START TIME -------------------------------------------
            self.start_time_row = db.execute(f"""
                SELECT event_id, activity_type
                FROM real_log
                WHERE timestamp_real >= ?
                ORDER BY timestamp_real ASC
                LIMIT 1
                """, (self.start_time,)).fetchone()
            
            if self.start_time_row == None:
                #--- Printer Error Message
                self.helper.printer(f"[WARNING][interfaceDB.py/find_line_ID_start_end()] It was not possible to find any event after the start time: {self.start_time}")
                
                self.start_time_id = None
                self.start_time_status = None
                
            else:
                # --- Update Start Pointers (Natural Approach)
                self.start_time_id = self.start_time_row[0]
                self.start_time_status = self.start_time_row[1]
            
            with sqlite3.connect(self.database_path) as db:
                # --------------------------- FOR SYNC ---------------------------
                # (in case where a start time can occur twice in the same place, we check if the table exists)
                table = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='time_pointers';")
                if table.fetchone() != None and self.feature_usingDB != 'valid_logic' and self.feature_usingDB != 'valid_input':
                    print("time_pointers table exists")
                    # --- Update Start Pointers (Forced Approach)
                    if self.start_time_status == "Finished":
                            self.helper.printer(f"[WARNING][interfaceDB.py/find_line_ID_start_end()] Changed Start Time by force because a initial trace was 'Finished'.")

                    next_start_time_id = self.forced_update_start_time()
                    self.start_time_id = next_start_time_id
                    print("Start Time ID assigned by force using the previous End Time ID as reference")

                    #--- update the start time
                    with sqlite3.connect(self.database_path) as db:
                        row= db.execute("""SELECT timestamp_real, activity_type FROM real_log WHERE event_id= ? """, (self.start_time_id,)).fetchone()
                        self.start_time= row[0]
                        self.start_time_status= row[1]
                else:
                    print("table 'time_pointers' does not exist")

                # --------------------------- FOR VALID ---------------------------
                if (self.feature_usingDB == 'valid_logic' or self.feature_usingDB == 'valid_input') and self.start_time_id != 1:
                    print("selecting pointer by force for validation")
                    # --- Update Start Pointers (Forced Approach)
                    if self.start_time_status == "Finished":
                        self.helper.printer(f"[WARNING][interfaceDB.py/find_line_ID_start_end()] Changed Start Time by force because a initial trace was 'Finished'.")

                    next_start_time_id = self.forced_update_start_time()
                    self.start_time_id = next_start_time_id
                    print("Start Time ID assigned by force using the previous End Time ID as reference")

                    #--- update the start time
                    with sqlite3.connect(self.database_path) as db:
                        row= db.execute("""SELECT timestamp_real, activity_type FROM real_log WHERE event_id= ? """, (self.start_time_id,)).fetchone()
                        self.start_time= row[0]
                        self.start_time_status= row[1]

            """
            if self.start_time_id != 1:
                if self.start_time_status == "Finished":
                    self.helper.printer(f"[WARNING][interfaceDB.py/find_line_ID_start_end()] Changed Start Time by force because a initial trace was 'Finished'.")

                next_start_time_id = self.forced_update_start_time()
                self.start_time_id = next_start_time_id
                print("Start Time ID assigned by force using the previous End Time ID as reference")

                #--- update the start time
                
            """


            # ------------------------------------------ END TIME -------------------------------------------
                       
            #--- Timeout Loop
            self.looping = True
            self.try_counter = 0

            while self.looping == True and self.try_counter <= self.max_counter:
                # Take the line id most close to the end time but higher than the start time
                self.end_time_id = db.execute(f"""
                    SELECT event_id, activity_type
                    FROM real_log
                    WHERE timestamp_real <= ? AND timestamp_real >= ?
                    ORDER BY timestamp_real DESC
                    LIMIT 1
                    """, (self.end_time,self.start_time,)).fetchone()
                
                #--- Stop Conditions
                if self.end_time_id != None:
                    # Found a started
                    self.looping = False

                else:
                    self.helper.printer(f"[interfaceDB.py/find_line_ID_start_end()] (Waiting {self.try_counter* self.sleep_time} sec) Not found any event before the end_time: {self.end_time} and after the start_time: {self.start_time}. Sleeping for {self.sleep_time} seconds and trying again", 'brown')
                    #--- Sleep for the next try
                    sleep(self.sleep_time)

                    #--- Updated the trying counter
                    self.try_counter += 1

   
            if self.try_counter > self.max_counter:
                #--- Printer Error Message
                self.helper.printer(f"[ERROR][interfaceDB.py/find_line_ID_start_end()] It was not possible to find any event before the end time: {self.end_time} and after the start time: {self.start_time}", 'red')
                
                #--- Killing the program
                self.helper.printer(f"---- Digital Twin killed ----", 'red')
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


            #--- Timeout Loop
            self.looping = True
            self.try_counter = 0

            while self.looping == True and self.try_counter <= self.max_counter:
                #--- Check if both start and end reference to the same line (rows == Traces)
                if  self.start_time_id == self.end_time_id:
                    rows = db.execute("SELECT * FROM real_log WHERE event_id = ?", (self.start_time_id,)).fetchall()
                else:
                    rows = db.execute("SELECT * FROM real_log WHERE event_id >= ? AND event_id <= ?", (self.start_time_id, self.end_time_id)).fetchall()
                    
                #--- Stop Conditions
                if rows != None:
                    # Found a started
                    self.looping = False

                else:
                    self.helper.printer(f"[interfaceDB.py/updated_relative_timestamp()] (Waiting {self.try_counter* self.sleep_time} sec) Not found any event between [{self.start_time_id}, {self.end_time_id}]. Sleeping for {self.sleep_time} seconds and trying again", 'brown')
                    #--- Sleep for the next try
                    sleep(self.sleep_time)

                    #--- Updated the trying counter
                    self.try_counter += 1

   
            if self.try_counter > self.max_counter:
                #--- Printer Error Message
                self.helper.printer(f"[ERROR][interfaceDB.py/updated_relative_timestamp()] It was not possible to find any event between [{self.start_time_id}, {self.end_time_id}]", 'red')
                
                #--- Killing the program
                self.helper.printer(f"---- Digital Twin killed ----", 'red')
                sys.exit()

            print(f"-------- Printing the traces: --------")
            for row in rows:
                print(f"{row}")

            # Loop through the selected rows and update the timestamp column with relative values 
            try:
                start_timestamp = rows[0][-1]
            except IndexError:
                self.helper.printer("[ERROR][interfaceDB.py/updated_relative_timestamp()] No traces found to start. Check if the real system is working or if you initiate the replicator correctly.", 'red')
                self.helper.kill()

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

        #--- Timeout Loop
        self.looping = True
        self.try_counter = 0
        while self.looping == True and self.try_counter <= self.max_counter:
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
                self.looping = False

            else:
                self.helper.printer(f"[interfaceDB.py/update_end_time] (Waiting {self.try_counter* self.sleep_time} sec) Not found 'Started' after the end_time: {self.end_time}. Sleeping for {self.sleep_time} seconds and trying again", 'brown')
                #--- Sleep for the next try
                sleep(self.sleep_time)

                #--- Updated the trying counter
                self.try_counter += 1
        
        if self.try_counter > self.max_counter:
            #--- Printer Error Message
            self.helper.printer(f"[ERROR][interfaceDB.py/update_end_time()][TIMEOUT] After trying {self.max_counter} times, it was not possible to find a 'Started' event after the end time: {self.end_time}", 'red')
            
            #--- Killing the program
            self.helper.printer(f"---- Digital Twin killed ----", 'red')
            sys.exit()
        

        #--- Take the rigth position before that event
        started_position = row[0] # line id
        # To not go to zero, don't subtract with it's one
        if started_position != 1:
            selected_line_id = started_position - 1
        else:
            selected_line_id = started_position
        
        #--- Changed the pointer?
        if selected_line_id != self.end_time_id:
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
            timeout_counter = 1

            while flag_not_missing_part_id== True and timeout_counter <= self.max_counter:

                parts_zero = db.execute("SELECT * FROM real_log WHERE part_id= ? AND event_id >= ? AND event_id <= ?", ('Part 0', self.start_time_id, self.end_time_id)).fetchall()
                print(f"parts_zero: {parts_zero}")
                if len(parts_zero) == 0:
                    flag_not_missing_part_id = False
                else:
                    self.helper.printer(f"[WARNING][interfaceDB.py/check_parts_zero()] (Waiting {timeout_counter* self.sleep_time} sec) A Part 0 (without correct ID) was detected within the traces... Sleeping for {self.sleep_time} seconds")
                    sleep(self.sleep_time)
                    timeout_counter += 1
            
            if timeout_counter > self.max_counter:
                self.helper.printer(f"[ERROR][interfaceDB.py/check_parts_zero()] After trying {self.max_counter} ({self.max_counter * self.sleep_time} seconds), there are still Part 0 within the selected trace. Most probably the some ESP32 is not detecting correctly the RFID Sticker", 'red')
                
                #--- Killing the program
                self.helper.printer(f"---- Digital Twin killed ----", 'red')
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
        
    def read_last_end_time_valid(self):
        with sqlite3.connect(self.database_path) as db:
            end_times = db.execute("""
            SELECT end_time FROM time_pointers WHERE feature_usingDB= 'valid_input'
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

# ===================== DIGITAL LOG FUNCTION =====================
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

    # ============================ ID DATABASE ============================
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
                self.helper.printer(f"[ERROR][interfaceDB.py/get_PID()] The part id '{partid}' was not found in the database: '{self.database_path}'", 'red')
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
            try:
                last_event_id = old_db.execute(f"""SELECT MAX(event_id) FROM real_log""").fetchone()[0]
                print(f"total number of traces = {last_event_id}")

                print("====== Starting database replicator ======")
            except sqlite3.OperationalError:
                self.helper.printer(f"[ERROR][interfaceDB.py/replicate_database()] Replicated database is empty (path: {self.replicated_database_path}). Try to copy a real database and rename it to 'replicated_database.db'. (Original error:sqlite3.OperationalError: no such table: real_log )", 'red')
                self.helper.kill()

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
    
    # --------- Write the Selected Queue from RCT ---------
    def write_selected_branch_queue(self, UID, selected_queue):
        with sqlite3.connect(self.database_path) as db:
            #--- Find the line ID for the given UID
            line_id= db.execute("""
            SELECT line_id FROM ID WHERE UID= ?
            """, (UID,)).fetchone()
            
            db.execute("""
            UPDATE ID SET branch_queue= ? WHERE line_id= ?
            """, (selected_queue, line_id[0]))

            db.commit()

            print(f"Branch Queue of '{UID}' (line id: '{line_id}') updated to '{selected_queue}'")

    # --------- Read Branch Queues for each Part ----------
    def read_parts_branch_queue(self):
        """
        This functions read the ID database and returns the part name (PID) with 
        their respective branch_queue.
        """
        with sqlite3.connect(self.database_path) as db:
            parts_branch_queue_vect = db.execute("""
            SELECT PID, branch_queue FROM ID
            """).fetchall()

        print(f"parts_branch_queue_vect = {parts_branch_queue_vect}")
        return parts_branch_queue_vect
    
    # ========================== FOR TDS ==========================
    def get_parts_with_completed_traces(self):
        with sqlite3.connect(self.database_path) as db:
            if self.start_time != None and self.end_time != None:
                return db.execute("""
                        SELECT DISTINCT t1.part_id
                        FROM real_log t1
                        INNER JOIN (
                        SELECT part_id, activity_type, MIN(timestamp_real) AS min_time
                        FROM real_log
                        WHERE event_id >= ? AND event_id <= ?
                        GROUP BY part_id, activity_type
                        ) t2
                        ON t1.part_id = t2.part_id AND t1.activity_type = t2.activity_type AND t1.timestamp_real = t2.min_time
                        WHERE t1.activity_type = 'Finished' AND t1.event_id  >= ? AND t1.event_id <= ?
                    """, (self.start_time_id, self.end_time_id, self.start_time_id, self.end_time_id)).fetchall()

            else:
                print("Didn't test properly")
                return db.execute("""
                        SELECT DISTINCT t1.part_id
                        FROM real_log t1
                        INNER JOIN (
                        SELECT part_id, activity_type, MIN(timestamp_real) AS min_time
                        FROM real_log
                        GROUP BY part_id, activity_type
                        ) t2
                        ON t1.part_id = t2.part_id AND t1.activity_type = t2.activity_type AND t1.timestamp_real = t2.min_time
                        WHERE t1.activity_type = 'Finished'
                    """).fetchall()

    def get_machines_with_completed_traces(self):
        with sqlite3.connect(self.database_path) as db:
            traces = db.execute(
                """
                SELECT DISTINCT t1.machine_id
                FROM (
                    SELECT machine_id, activity_type, MIN(event_id) AS min_event_id
                    FROM real_log
                    WHERE activity_type IN ('Started', 'Finished') AND event_id >= ? AND event_id <= ?
                    GROUP BY machine_id, activity_type
                ) AS t1
                INNER JOIN (
                    SELECT machine_id, MIN(event_id) AS min_started_event_id, MAX(event_id) AS max_finished_event_id
                    FROM real_log
                    WHERE activity_type = 'Started' AND event_id >= ? AND event_id <= ?
                    GROUP BY machine_id
                ) AS t2 ON t1.machine_id = t2.machine_id
                WHERE t1.activity_type = 'Started' AND t1.min_event_id = t2.min_started_event_id
                AND EXISTS (
                    SELECT 1
                    FROM real_log
                    WHERE real_log.machine_id = t1.machine_id AND activity_type = 'Finished' AND event_id >= t1.min_event_id AND event_id <= t2.max_finished_event_id
                )
                """, (self.start_time_id, self.end_time_id, self.start_time_id, self.end_time_id)
            ).fetchall()


            print("Printing unique machines ids with completed traces")
            for element in traces:
                print(element)

            return traces
        

    # ========================== EXPERIMENTAL DATABASE ==========================
    # --------- Write the RCT prediction into exp_database ---------
    def write_RCTpaths(self, RCT_path1, RCT_path2, queue_selected, gain, partid):
        """ This function writes in the experimental database the rct calculate for each path"""
        (tstr, t) = self.helper.get_time_now()
        
        with sqlite3.connect(self.database_path) as db:
            db.execute("""
            INSERT INTO RCTpaths (current_time_str, timestamp_real, RCT_path1, RCT_path2, queue_selected, gain, partid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tstr, t, RCT_path1, RCT_path2, queue_selected, gain, partid))

            db.commit()

    # --------- Write the Validation Indicators into the exp_database ---------
    def write_ValidIndicators(self, logic_indicator, input_indicator, model_in, model_out):
        #-- Get time
        (tstr, t)= self.helper.get_time_now()

        #-- Write into the database
        with sqlite3.connect(self.database_path) as db:
            db.execute("""
                INSERT INTO valid_indicators (current_time_str, timestamp_real, logic_indicator, input_indicator, model_in, model_out)
                VALUES (?,?,?,?,?,?)
            """, (tstr, t, logic_indicator, input_indicator, model_in, model_out))

            db.commit()

    # --------- Read valid indicators ---------
    def read_ValidIndicator(self, indicator_name):
        with sqlite3.connect(self.database_path) as db:
            indicator = db.execute(
                f"""
                SELECT {indicator_name} FROM valid_indicators
                """
            ).fetchall()

            # --- Fix tuple
            for i in range(len(indicator)): indicator[i] = indicator[i][0] 

            timestamp = db.execute(
                """
                SELECT timestamp_real FROM valid_indicators
                """
            ).fetchall()

            # --- Fix tuple
            for i in range(len(timestamp)): timestamp[i] = timestamp[i][0] 

            return (indicator, timestamp)
    
    def read_RCT_path(self):
        with sqlite3.connect(self.database_path) as db:
            # --- Get timestamp
            timestamp = db.execute("""SELECT timestamp_real FROM RCTpaths""").fetchall()
            # --- Fix tuple
            for i in range(len(timestamp)): timestamp[i] = timestamp[i][0] 

            # --- Get rct from path 1
            rct_path1 = db.execute("""SELECT RCT_path1 FROM RCTpaths""").fetchall()
            # --- Fix tuple
            for i in range(len(rct_path1)): rct_path1[i] = rct_path1[i][0] 

            # --- Get rct from path 2
            rct_path2 = db.execute("""SELECT RCT_path2 FROM RCTpaths""").fetchall()
            # --- Fix tuple
            for i in range(len(rct_path2)): rct_path2[i] = rct_path2[i][0] 

            return (rct_path1, rct_path2, timestamp)



