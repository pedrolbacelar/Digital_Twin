# -------------------- NAME OF THE FOLDER --------------------
name= "5s_determ"
# ------------------------------------------------------------

# -------------------- SELECT THE IP ADDRESS --------------------
polimi_ip_address = "10.169.114.208"
home_ip_address = "192.168.1.223"
alex_phone = "192.168.15.41"
ip = "10.169.81.165"
factory_ip_address = "192.168.0.50"

# =========================
myIP = factory_ip_address
# ========================

# ---------------------------------------------------------------


#--- Import Broker Manager class
from dtwinpylib.dtwinpy.broker_manager import Broker_Manager
from dtwinpylib.dtwinpy.helper import Helper
helper = Helper()

#--- Real Database path
real_database_path = f"databases/{name}/real_database.db"

#--- ID Database path
ID_database_path = f"databases/{name}/ID_database.db"

#--- Digital Database path
digital_database_path = f"databases/{name}/digital_database.db"

#--- Delete Existing Databases
def delete_databases(database_path, real_database_path, ID_database_path):
    print("|- Deleting existing databases...")
    #- Delete Digital Database
    import os
    
    try:
        os.remove(database_path)
        print(f"|-- Digital Database deleted successfuly from {database_path}")

    except FileNotFoundError:
        helper.printer(f"[WARNING] The Digital Database doesn't exist yet in the path '{database_path}', proceding without deleting...")

    #- Delete Real Database
    try:
        os.remove(real_database_path)
        print(f"|-- Real Database deleted successfuly from {real_database_path}")
    except FileNotFoundError:
        helper.printer(f"[WARNING] The Real Database doesn't exist yet in the path '{real_database_path}', proceding without deleting...")

    #- Delete ID database
    try:
        os.remove(ID_database_path)
        print(f"|-- ID Database deleted successfuly from {ID_database_path}")
    except FileNotFoundError:
        helper.printer(f"[WARNING] The ID Database doesn't exist yet in the path '{ID_database_path}', proceding without deleting...")

# -------------------- DELETE EXISTING DATABASES -----------------------------
delete_databases(digital_database_path, real_database_path, ID_database_path)
# ----------------------------------------------------------------------------

try:
    #--- Create the Broker Manager
    broker_manager = Broker_Manager(ip_address= myIP, real_database_path= real_database_path, ID_database_path= ID_database_path)
    #--- Run Broker
    broker_manager.run()

except TimeoutError:
    helper.printer(f"[ERROR][broke_execute.py] Most probably the IP address {ip} is not correct!", 'red')


