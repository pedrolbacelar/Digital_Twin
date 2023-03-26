from .interfaceDB import Database
from .helper import Helper

class Tester():
    def __init__(self, name, experimental_database_path= None, real_database_path= None):
        self.helper = Helper()
        #--- Database Path management
        self.real_database_path= real_database_path
        self.experimental_database_path= experimental_database_path

        #--- Database creation
        self.real_database = Database(
            database_path= self.real_database_path
            event_table= "real_log",
        )

        self.experimental_database = Database(
            database_path= self.experimental_database_path,
        )
    
    # --- Write Validator Indicators ---
    def 