


polimi_ip_address = "10.169.114.208"
home_ip_address = "192.168.1.223"
alex_phone = "192.168.15.41"
ip = "10.169.81.165"



#--- Import Broker Manager class
from dtwinpylib.dtwinpy.broker_manager import Broker_Manager
name= "5s_deterministic_complex"

#--- Setting of the broker
factory_ip_address = "192.168.0.50"

#--- Real Database path
real_database_path = f"databases/{name}/real_database.db"

#--- ID Database path
ID_database_path = f"databases/{name}/ID_database.db"

#--- Create the Broker Manager
ip = alex_phone

try:
    broker_manager = Broker_Manager(ip_address= factory_ip_address, real_database_path= real_database_path, ID_database_path= ID_database_path)
    #--- Run Broker
    broker_manager.run()

except TimeoutError:
    print(f"[ERROR][broke_execute.py] Most probably the IP address {ip} is not correct!")


