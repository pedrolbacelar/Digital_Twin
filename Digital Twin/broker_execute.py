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

# ----------------------------------------------------------------------------

try:
    #--- Create the Broker Manager
    broker_manager = Broker_Manager(name= name, ip_address= myIP, real_database_path= real_database_path, ID_database_path= ID_database_path)

    #--- Run Broker
    broker_manager.run()

except TimeoutError:
    helper.printer(f"[ERROR][broke_execute.py] Most probably the IP address {ip} is not correct!", 'red')


