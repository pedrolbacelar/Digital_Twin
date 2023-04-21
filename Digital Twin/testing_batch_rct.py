from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin as dt

batch = [
    "Part 13",
    "Part 14",
    "Part 15",
    "Part 16"
]

mydt = dt(
    name= 'batch_rct',
    maxparts= 20
)

mymodel = mydt.generate_digital_model()

mymodel.run()

batch_rct = mymodel.calculate_Batch_RCT(batch)

