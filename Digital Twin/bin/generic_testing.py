from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

mydt= Digital_Twin(name="5s_determ", maxparts=10)
mydt.run_digital_model()

#-----

mydt= Digital_Twin(name='5s_determ', copied_realDB= True, Freq_Sync= 20, Freq_Valid= 40, Freq_Service= 10000)
mydt.run()
