from dtwinpylib.dtwinpy.helper import Helper
from dtwinpylib.dtwinpy.interfaceDB import Database
from matplotlib import pyplot as plt

helper = Helper()

#--- Cases databases paths
exp_database_path_case01= "data_generation/4.11.15.46/databases/exp_database.db"
real_database_path_case01 = exp_database_path_case01.replace('exp', 'real')

exp_database_path_case02 ="data_generation/4.11.17.26/databases/exp_database.db"
real_database_path_case02 = exp_database_path_case02.replace('exp', 'real')

#--- Creat exp db objects
exp_database_case01 = Database(database_path= exp_database_path_case01)
exp_database_case02 = Database(database_path= exp_database_path_case02)

#--- Parts to track
PID_case01 = 'Part 57'
PID_case02 = 'Part 36'

# ---------------------- Case 01 ----------------------
#--- Take the REAL RCT and timestamp for that PID
(rct_real, timestamp_real, flag_part_completed) = exp_database_case01.get_real_RCTtracking(real_database_path_case01, PID_case01)

if flag_part_completed == True:
    timestamp_real = helper.adjust_relative_vector(timestamp_real)

    #--- Take the DIGITAL RCT and timestamp for that PID
    (rct_digital, timestamp_digital_case01) = exp_database_case01.get_digital_RCTtracking(PID_case01)
    timestamp_digital_case01 = helper.adjust_relative_vector(timestamp_digital_case01)

    #--- Calculate the Error
    error_case01 = []
    for i in range(len(rct_digital)):
        fake_real_value = rct_real[0] - (1)*timestamp_digital_case01[i]
        digital_value = rct_digital[i]
        error = abs(digital_value - fake_real_value) / max(digital_value, fake_real_value)
        error_case01.append(error)

# ---------------------- Case 02 ----------------------
#--- Take the REAL RCT and timestamp for that PID
(rct_real, timestamp_real, flag_part_completed) = exp_database_case01.get_real_RCTtracking(real_database_path_case02, PID_case02)

if flag_part_completed == True:
    timestamp_real = helper.adjust_relative_vector(timestamp_real)

    #--- Take the DIGITAL RCT and timestamp for that PID
    (rct_digital, timestamp_digital_case02) = exp_database_case02.get_digital_RCTtracking(PID_case02)
    timestamp_digital_case02 = helper.adjust_relative_vector(timestamp_digital_case02)
    
    #-- outliers
    rct_digital.pop(5)
    timestamp_digital_case02.pop(5)
    rct_digital.pop(2)
    timestamp_digital_case02.pop(2)

    #--- clean the end
    rct_digital = rct_digital[:11]
    timestamp_digital_case02 = timestamp_digital_case02[:11]

    #--- Calculate the Error
    error_case02 = []
    real_value_case02 = []
    for i in range(len(rct_digital)):
        fake_real_value = rct_real[0] - (1)*timestamp_digital_case02[i]
        real_value_case02.append(fake_real_value)
        digital_value = rct_digital[i]
        error = abs(digital_value - fake_real_value) / max(digital_value, fake_real_value)
        error_case02.append(error)

print(f"rct_digital: {rct_digital}")
print(f"real_value_case02: {real_value_case02}")

# ------------------------ PLOT ----------------------

#--- Plot Case 01
plt.plot(
            timestamp_digital_case01,
            error_case01,
            marker='o',
            label= f'Error in Case 01'
        )

#--- Plot Case 02
plt.plot(
            timestamp_digital_case02,
            error_case02,
            marker='x',
            label= f'Error in Case 02'
        )

plt.title("Prediction Error Case 01 x Case 02")
plt.xlabel("Relative Timestamp (s)")
plt.ylabel("Error (%)")
plt.legend()
plt.savefig("Prediction_error.png")
plt.show()

# ------------------------ Comparative RCT ------------------------
#---------
plt.clf()
# -------------------- Case 01 --------------------
#--- Get the Real RCT and the predicted RCT (for both path) from the real log
(parts_name_finished_vec_case01, RCT_real_case01, RCT_path1_vec, RCT_path2_vec) = exp_database_case01.get_real_RCT(real_database_path_case01)
parts_finished_ids_vec_case01 = []
for part_name in parts_name_finished_vec_case01: parts_finished_ids_vec_case01.append(helper.extract_int(part_name))

linestyle= 'dashdot'
#--- Plot REAL RCT for each finished part
plt.plot(
    parts_finished_ids_vec_case01, 
    RCT_real_case01, 
    marker='o',
    linestyle= linestyle,
    label= 'Physical RCT [Case 01] (s)'
)
print(f"parts_finished_ids_vec_case01= {parts_finished_ids_vec_case01}")
# -------------------- Case 02 --------------------
#--- Get the Real RCT and the predicted RCT (for both path) from the real log
(parts_name_finished_vec_case02, RCT_real_case02, RCT_path1_vec, RCT_path2_vec) = exp_database_case02.get_real_RCT(real_database_path_case02)
parts_finished_ids_vec_case02 = []
for part_name in parts_name_finished_vec_case02: parts_finished_ids_vec_case02.append(helper.extract_int(part_name))

linestyle= 'dashdot'
#--- Plot REAL RCT for each finished part
max_PID = max(parts_finished_ids_vec_case01)
plt.plot(
    parts_finished_ids_vec_case02[:max_PID-1], 
    RCT_real_case02[:max_PID-1], 
    marker='o',
    linestyle= linestyle,
    label= 'Physical RCT [Case 02] (s)'
)

plt.title("Real RCT per Part ID (Case 01 x Case 02)")
plt.xlabel("Parts IDs")
plt.ylabel("RCT (s)")
plt.legend()
plt.savefig("Real RCT both cases.png")
plt.show()