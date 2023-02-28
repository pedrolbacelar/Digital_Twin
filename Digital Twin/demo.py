from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin


myDigitalTwin_determ = Digital_Twin(name="myDigitalTwin_determ", maxparts=50)
myDigitalTwin_determ.run_digital_model()
myDigitalTwin_determ.run_validation()