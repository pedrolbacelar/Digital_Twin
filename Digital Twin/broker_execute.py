# -------------------- NAME OF THE FOLDER --------------------
name= "5s_stho"
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

# ------------ DEFINE WORK IN PROGRESS ------------
WIP = 12
# -------------------------------------------------

# ------------ DEFINE DICTIONARY OF UID AND PALLET ID ------------
UID_to_PalletID= {
    "236439249": "Pallet 1",
    "2041719249": "Pallet 2",
    "2049810149": "Pallet 3",
    "236629349": "Pallet 4",
    "1721739249": "Pallet 5",
    "28159349": "Pallet 6",
    "44139349": "Pallet 7",
    "601269249": "Pallet 8",
    "20419710149": "Pallet 9",
    "1889810149": "Pallet 10",
    "441289249": "Pallet 11",
    "28429249": "Pallet 12"
}

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
    broker_manager = Broker_Manager(name= name, ip_address= myIP, real_database_path= real_database_path, ID_database_path= ID_database_path, WIP= WIP, UID_to_PalletID= UID_to_PalletID)

    #--- Run Broker
    broker_manager.run()

except TimeoutError:
    helper.printer(f"[ERROR][broke_execute.py] Most probably the IP address {ip} is not correct!", 'red')


