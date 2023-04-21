from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin

mydt = Digital_Twin(
    name= 'debug_update',
    Freq_Service= 10000000,
    Freq_Sync= 2,
    Freq_Valid= 30,
    delta_t_treshold=20,
    input_threshold= 0.8,
    logic_threshold= 0.8,
    flag_external_service= False,
    ip_address= '127.0.0.1',
    flag_API= True
    )

mydt.run()