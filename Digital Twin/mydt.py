#--- Import Library
print("Importing the libraries.....")
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

#--- Create a Digital Twin object with the require inputs
mydt = Digital_Twin(name= "2s_determ", template= True, Freq_Sync= 10, Freq_Valid= 120, Freq_Service= 10000, delta_t_treshold=30)

#--- Run the real time Digital Twin
mydt.run()