from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin as dt

mydt = dt(
    name= 'queue_full',
    targeted_part_id= 5
)

mydt.run_digital_model()