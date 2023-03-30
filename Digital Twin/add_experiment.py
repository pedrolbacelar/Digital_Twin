"""
Script to INSERT a line in the All Experiments database that is used to give inputs for 
the Digital Twin to run.
"""
import sqlite3

#--- All Experiments Database path
allexp_database_path = 'allexp_database.db'

############## EXPERIMENT OBJECTIVE ##############
objective= "Without Publishing RCT and adding a change in the process time of machine 1 and 5 for a higher one. Delta t now is 20 (10 to 40 for both)"
##################################################

################################ INPUT PARAMETERS ################################
dt_name= "5s_stho"

Freq_Sync= 2
Freq_Valid= 90
Freq_Service= 2

delta_t_treshold= 20
rct_threshold= -1
rct_queue= 1
logic_threshold= 0.7
input_threshold= 0.7

flag_API= "False"
flag_publish= "False"
flag_validation= "True"  
flag_external_service= "True"

contemp_M1= '["norm", 11, 2]'
contemp_M2= '["norm", 17, 2]'
contemp_M3= '["norm", 60, 2]'
contemp_M4= '["norm", 38, 2]'
contemp_M5= '["norm", 10, 2]'
###################################################################################### 

def create_experiment():
    with sqlite3.connect(allexp_database_path) as allexp:
        allexp.execute(f"""INSERT INTO experiment_setup (
            objective,
            dt_name,

            Freq_Sync,
            Freq_Valid,
            Freq_Service,

            delta_t_treshold,
            rct_threshold,
            rct_queue,
            logic_threshold,
            input_threshold,

            flag_API,
            flag_publish,
            flag_validation,     
            flag_external_service,
            
            contemp_M1,
            contemp_M2,
            contemp_M3,
            contemp_M4,
            contemp_M5
        ) VALUES (
            ?,
            ?,

            ?,
            ?,
            ?,

            ?,
            ?,
            ?,
            ?,
            ?,

            ?,
            ?,
            ?,     
            ?,
            
            ?,
            ?,
            ?,
            ?,
            ?
        )

        """,
        (
            objective,
            dt_name,

            Freq_Sync,
            Freq_Valid,
            Freq_Service,

            delta_t_treshold,
            rct_threshold,
            rct_queue,
            logic_threshold,
            input_threshold,

            flag_API,
            flag_publish,
            flag_validation,     
            flag_external_service,
            
            contemp_M1,
            contemp_M2,
            contemp_M3,
            contemp_M4,
            contemp_M5
        ))

        allexp.commit()

create_experiment()