#--- Import Library
print("Importing the libraries.....")
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

#--- Create a Digital Twin object with the require inputs
mydt = Digital_Twin(
    name= "5s_determ",
    template= True, 
    Freq_Sync= 30, 
    Freq_Valid= 60, 
    Freq_Service= 10000, 
    delta_t_treshold=21,
    ip_address="192.168.0.50")

#--- Run the real time Digital Twin
mydt.run()