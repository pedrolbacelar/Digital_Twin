from dtwinpylib.dtwinpy.interfaceDB import Database

#--- Database to replicated path
database_path = "databases/5s_determ/real_database.db"
#database_path = "databases/debug_valid/real_database.db"
#database_path = "databases/debug_update/real_database.db"
name = "5s_stho"
name = "debug_tracking"

change_name = input(f"The dafault Digital Twin's name is {name}. Would like to change? [y/n]")
if change_name == 'y':
    name = input(f"Type the new Digital Twin's name: ")


print(f"Using Digital Twin's name: {name}")
database_path = f"databases/{name}/real_database.db"


print(f"REPLICATOR WRITING HERE: {database_path}")
#--- Create DB object
mydb = Database(database_path= database_path, event_table= "replicated_log")

#--- Run replication
mydb.replicate_database()