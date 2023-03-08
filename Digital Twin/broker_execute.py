#--- Import Broker Manager class
from dtwinpylib.dtwinpy.broker_manager import Broker_Manager

#--- Setting of the broker
factory_ip_address = "192.168.0.50"
polimi_ip_address = "10.169.114.208"
home_ip_address = "192.168.1.223"
alex_phone = "192.168.2.70"
ip = "10.169.119.37"

database_path = "databases/RFID_test.db"

#--- Create the Broker Manager
broker_manager = Broker_Manager(ip_address= alex_phone, real_database_path= database_path)

#--- Run Communication
broker_manager.run()

