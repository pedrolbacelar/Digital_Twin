#--- Import Library
print("Importing the libraries.....")
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
factory_ip = "192.168.0.50"
my_ip = "127.0.0.1"

#--- Create a Digital Twin object with the require inputs
"""
mydt = Digital_Twin(
    name= "5s_determ",
    template= True, 
    Freq_Sync= 10, 
    Freq_Valid= 30, 
    Freq_Service= 10000, 
    delta_t_treshold=5,
    ip_address=my_ip,
    flag_API= True,
    rct_threshold= 0,
    rct_queue= 2,
    flag_external_service= False,
    logic_threshold= 0.0001,
    input_threshold=0.0001)

#--- Run the real time Digital Twin
mydt.run()
"""

mydt = Digital_Twin(name="5s_determ", maxparts= 5)
mydt.run_digital_model()