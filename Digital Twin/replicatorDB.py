from dtwinpylib.dtwinpy.interfaceDB import Database

#--- Database to replicated path
database_path = "databases/5s_determ/real_database.db"

#--- Create DB object
mydb = Database(database_path= database_path, event_table= "replicated_log")

#--- Run replication
mydb.replicate_database()