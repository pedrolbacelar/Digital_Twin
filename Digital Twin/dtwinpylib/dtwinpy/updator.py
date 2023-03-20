#--- Import features
from dtwinpylib.dtwinpy.helper import Helper
from dtwinpylib.dtwinpy.interfaceDB import Database

class Updator():
    """
    The class Updator is called when the validation is given a certain amount of indicators beyond
    the allowed threshold. 
    """
    def __init__(self, update_type, real_database_path, start_time, end_time):
        #--- Create helper
        self.helper = Helper()

        #--- Basic Stuff
        self.update_type = update_type
        self.real_database_path = real_database_path
        self.start_time = start_time
        self.end_time = end_time

        #--- Create database object
        self.real_database_updator = Database(
            database_path= self.real_database_path,
            event_table= 'real_log',
            start_time= self.start_time,
            end_time= self.end_time
        )

    
    # ------------------------------ Main Updating Functions ------------------------------
    def update_logic(self):
        ############# MODEL GENERATION (FUTURE ) #############
        pass

    def update_input(self):
        pass
    # ---------------------------------------------------------------------------------------

    def run(self):
        """
        Run the model update for logic (if requested) or for input (if requested)
        """

        # --------------- Logic Model Update ---------------
        if self.update_type == 'logic':
            pass

        # --------------- Input Model Update ---------------
        if self.update_type == 'input':
            pass