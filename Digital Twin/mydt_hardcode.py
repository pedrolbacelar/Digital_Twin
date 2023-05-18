#--- Import Library
print("Importing the libraries.....")
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.tester import Tester


factory_ip = "192.168.0.50"
home_ip = "127.0.0.1"

my_ip = factory_ip
name = "5s_stho"

Freq_Sync= 2
Freq_Valid= 90
Freq_Service= 2

delta_t_treshold= 20
rct_threshold= -1
rct_queue= 1
logic_threshold= 0.7
input_threshold= 0.7

flag_API= "False"
flag_publish= "False"
flag_validation= "False"  
flag_external_service= "True"


#--- Create a Digital Twin object with the require inputs
mydt = Digital_Twin(
    name= name,
    template= True, 
    Freq_Sync= Freq_Sync, 
    Freq_Valid= Freq_Valid, 
    Freq_Service= Freq_Service, 
    delta_t_treshold= delta_t_treshold,
    ip_address=my_ip,
    flag_API= flag_API,
    rct_threshold= rct_threshold,
    rct_queue= rct_queue,
    flag_external_service= flag_external_service,
    flag_publish = flag_publish,
    logic_threshold= logic_threshold,
    input_threshold= input_threshold,
    flag_validation=flag_validation)

mydt.run()
