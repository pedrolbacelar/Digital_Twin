import sqlite3


database_path = "databases/5s_determ/real_database.db"

with sqlite3.connect(database_path) as db:
    table = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='time_pointers';")
    print(table.fetchone())
    if table.fetchone() != None:
        print("time_pointers table exists")
    else:
        print("table 'time_pointers' does not exist")