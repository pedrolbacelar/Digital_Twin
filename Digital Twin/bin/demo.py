from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin


myDigitalTwin_dist = Digital_Twin(name="myDigitalTwin_dist", maxparts= 50)
myDigitalTwin_dist.run_digital_model()
myDigitalTwin_dist.run_validation()