from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.helper import Helper

helper = Helper()
helper.delete_databases('5s_stho')

home_ip = "127.0.0.1"

my_ip = home_ip

#--- Create a Digital Twin object with the require inputs
mydt = Digital_Twin(
    name= '5s_stho',
    ip_address=my_ip,

    Freq_Sync= 2, 
    Freq_Valid= 180, 
    Freq_Service= 2,

    delta_t_treshold= 20,
    rct_threshold= -1,
    rct_queue= 2,
    logic_threshold= 0.8,
    input_threshold= 0.8,

    flag_external_service= True,
    flag_publish = False,
    flag_API= False,
    flag_validation= True)

mydt.run()