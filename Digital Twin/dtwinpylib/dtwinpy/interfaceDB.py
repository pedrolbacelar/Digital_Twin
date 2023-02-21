import sqlite3

class Database():
    def __init__(self, database_path, event_table):
        self.database_path = database_path
        self.event_table = event_table

    
    def initialize(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB:

            digital_model_DB.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                event_id INTEGER PRIMARY KEY,
                timestamp INTEGER,
                machine_id TEXT,
                activity_type TEXT,
                part_id TEXT,
                queue TEXT
            )
            """)

            digital_model_DB.commit()
    
    def clear(self, table):
        #--- clear all the data written in {table}

        with sqlite3.connect(self.database_path) as digital_model_DB:
            digital_model_DB.execute(f"DROP TABLE IF EXISTS {table}")
            digital_model_DB.commit()


    def write_event(self, table, timestamp, machine_id, activity_type, part_id, queue):
        #--- Write the given evento into the the database
        
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            digital_model_DB.execute(f"""
            INSERT INTO {table} (timestamp, machine_id, activity_type, part_id, queue)
            VALUES (?, ?, ?, ?, ?)""", (timestamp, machine_id, activity_type, part_id, queue))

            digital_model_DB.commit()

    def read_all_events(self, table):
        #--- Read all the events from the given table
        
        print(f"=== Reading all the events from table: {table} ===")
        with sqlite3.connect(self.database_path) as digital_model_DB:
            event_points = digital_model_DB.execute(f"SELECT * FROM {table}")
            for event_point in event_points:
                print(event_point)

    def get_event_table(self):
        return self.event_table

    def get_distinct_values(self, column, table):
        with sqlite3.connect(self.database_path) as DB:
            return DB.execute(f"SELECT DISTINCT {column} FROM {table}").fetchall()

    def get_time_activity_of_column(self, column, column_id, table):
        with sqlite3.connect(self.database_path) as DB:
            return DB.execute(f"SELECT timestamp, activity_type FROM {table} WHERE {column}=?", column_id).fetchall()

    def read_store_data(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id FROM {table}").fetchall()
        return data_full_trace
    
    def read_store_data_all(self, table):
        with sqlite3.connect(self.database_path) as digital_model_DB: 
            data_full_trace = digital_model_DB.execute(f"SELECT timestamp, machine_id, activity_type, part_id, queue FROM {table}").fetchall()
        return data_full_trace