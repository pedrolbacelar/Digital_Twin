#--- Import Library
print("Importing the libraries.....")
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.tester import Tester


factory_ip = "192.168.0.50"
home_ip = "127.0.0.1"

my_ip = home_ip

#--- Create a Digital Twin object with the require inputs
mydt = Digital_Twin(
    name= 'debug_tracking',
    template= True, 
    Freq_Sync= 2, 
    Freq_Valid= 90, 
    Freq_Service= 2, 
    delta_t_treshold= 25,
    ip_address=my_ip,
    flag_API= False,
    rct_threshold= -1,
    rct_queue= 1,
    flag_external_service= True,
    flag_publish = False,
    logic_threshold= 0.7,
    input_threshold= 0.7,
    flag_validation= True,
    keepDB= True)

mydt.run()
