from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

mydt = Digital_Twin(name= "sync_copy", maxparts= 5)
mydt.run_digital_model(plot= False)
mydt.run_sync(copied_realDB= True)