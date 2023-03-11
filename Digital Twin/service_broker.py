#--- Import modules from the library
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.broker_manager import Broker_Manager

#--- Reload modules
import importlib
import dtwinpylib
importlib.reload(dtwinpylib.dtwinpy.Digital_Twin)
importlib.reload(dtwinpylib.dtwinpy.broker_manager)

my_pc_ip_address = "192.168.1.223"

mydt = Digital_Twin(name= "5s_deterministic_complex", targeted_part_id= 1)
mydt.initiate_broker(ip_address= my_pc_ip_address)
mydt.run_RCT_services(verbose= True)