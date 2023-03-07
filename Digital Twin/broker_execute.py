#--- Import Broker Manager class
from dtwinpylib.dtwinpy.broker_manager import Broker_Manager

#--- Setting of the broker
ip_address = "192.168.0.50"
database_path = "databases/broker_tests.db"

#--- Create the Broker Manager
broker_manager = Broker_Manager(ip_address=ip_address, real_database_path= database_path)

#--- Run Communication
broker_manager.run()

