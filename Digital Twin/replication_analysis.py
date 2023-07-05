from dtwinpylib.dtwinpy.helper import Helper
import sqlite3
from matplotlib import pyplot as plt
helper = Helper()

"""
TODO:
- read the database exp_database.db
- in the table RCTpaths, for each unique part id, do:
    - store how many times each part was tested
    - for each RCT path (colunms RCT_path1 and RCT_path2):
        - calculate the relative timestamp (current value minus the delta of time that is the final timestamp minus the current)
        - store the relative timestamp in a list
        - calculate the average of the relative timestamp
        - store the average in a list
    - compare the average timestamp between rct_path1 and rct_path2
    - chose the one with the lowest average timestamp
    - compare with the chosen one is equal to the column queue_selected of the last value of the part id
    - if it is equal, store 1 in a list, else store 0 in a list
- considering all the rct paths, plot the average of the relative timestamp
- calculate the percentage of results that are equal to 1
"""
#--- Database path
#database_path = "data_generation/5.18.19.32/databases/exp_database.db"
#database_path = "data_generation/4.11.19.12/databases/exp_database.db"

#-- Use Case 1: without Digital Twin
database_path = "data_generation/4.11.15.46/databases/exp_database.db"

#-- Use Case 2: with Digital Twin
#database_path = "data_generation/4.11.17.26/databases/exp_database.db"


#--- read the database exp_database.db and get important
with sqlite3.connect(database_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT RCT_path1, RCT_path2, queue_selected, partid FROM RCTpaths")
    data = cursor.fetchall()

#--- Get unique part ids
with sqlite3.connect(database_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT partid FROM RCTpaths")
    partids = cursor.fetchall()
    partids= helper.convert_tuple_vector_to_list(partids)

#--- Create vectors
# RCT averages
RCT1_avg = {}
RCT1_default = {}

RCT2_avg = {}
RCT2_default = {}

# RCT ranges
RCT1_range = {}
RCT2_range = {}

# Queues selecteds
Queues_selected = {}
Queues_avg_selected = {}



def relative_average_calculator(RCT, timestamp):
    #--- Calculate the relative timestamp
    relative_rct = []
    for i in range(len(RCT)):
        delta = abs(timestamp[-1] - timestamp[i])
        relative_rct.append(RCT[i] - delta)
    
    #--- Calculate the average
    average = sum(relative_rct)/len(relative_rct)

    #--- Range of RCT
    max_rct = abs(max(relative_rct) - RCT[-1])
    min_rct = abs(min(relative_rct) - RCT[-1])
    range_rct = [max_rct, min_rct]

    return average, range_rct


#---- For each Part ID
for partid in partids:
    #--- Get RCT1 and RCT2
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        #--- Queue Selected (get the last queue_selected of the partid)
        cursor.execute("SELECT queue_selected FROM RCTpaths WHERE partid = ?", (partid,))
        queue_selected = cursor.fetchall()
        queue_selected = queue_selected[-1][0]
        #--- Add into the dictionary
        Queues_selected[partid] = queue_selected

        #--- RCT1
        cursor.execute("SELECT RCT_path1 FROM RCTpaths WHERE partid = ?", (partid,))
        RCT_path1 = cursor.fetchall()
        RCT_path1 = helper.convert_tuple_vector_to_list(RCT_path1)
        RCT1_default[partid] = RCT_path1

        #--- RCT2
        cursor.execute("SELECT RCT_path2 FROM RCTpaths WHERE partid = ?", (partid,))
        RCT_path2 = cursor.fetchall()
        RCT_path2 = helper.convert_tuple_vector_to_list(RCT_path2)
        RCT2_default[partid] = RCT_path2

        #--- Take the timestamp
        cursor.execute("SELECT timestamp_real FROM RCTpaths WHERE partid = ?", (partid,))
        timestamp = cursor.fetchall()
        timestamp = helper.convert_tuple_vector_to_list(timestamp)

        
        if partid == "Part 10":
            pass
        #--- Calculate Relative Average for RCT1
        RCT1_avg[partid], RCT1_range[partid] = relative_average_calculator(RCT_path1, timestamp)
        #--- Calculate Relative Average for RCT2
        RCT2_avg[partid], RCT2_range[partid] = relative_average_calculator(RCT_path2, timestamp)

        #--- Decision Making based on the average
        if RCT1_avg[partid] <= RCT2_avg[partid]:
            Queues_avg_selected[partid] = "Queue 3"
        if RCT1_avg[partid] > RCT2_avg[partid]:
            Queues_avg_selected[partid] = "Queue 4"

        pass




#--- Plot the average of the relative RCT 1 versus the normal RCT 1
rct1_values = []
for rct_list in RCT1_default.values():
    for rct in rct_list:
        rct1_values.append(rct)
#--- Extract parts ids
partids = []
for partid in RCT1_avg.keys():
    partids.append(helper.extract_int(partid))


#--- RCT range (max and min) relatively to the chosen
range1_max = []
range1_min = []

for range_rct in RCT1_range.values():
    range1_min.append(range_rct[0])
    range1_max.append(range_rct[1])

range2_max = []
range2_min = []

for range_rct in RCT2_range.values():
    range2_min.append(range_rct[0])
    range2_max.append(range_rct[1])


#--- RCT Chosen (last simulation)
rct1_chosen = []
for rct in RCT1_default.values():
    rct1_chosen.append(rct[-1])

rct2_chosen = []
for rct in RCT2_default.values():
    rct2_chosen.append(rct[-1])

#--- Getting the Real RCT
from dtwinpylib.dtwinpy.interfaceDB import Database
exp_database = Database(
    database_path= database_path,
)
real_database_path = database_path.replace("exp_database", "real_database")
(parts_name_finished_vec, RCT_real, RCT_path1_vec, RCT_path2_vec) = exp_database.get_real_RCT(real_database_path)
#--- Convert the list of parts names in integers ids
parts_finished_ids_vec = []
for part_name in parts_name_finished_vec: parts_finished_ids_vec.append(helper.extract_int(part_name))


# ================================== Plotting RCT Range ==================================
#--- Plot real RCT
linestyle= ''
linestyle_rct1= ''
linestyle_rct2= ''
#--- Plot REAL RCT for each finished part
plt.plot(
    parts_finished_ids_vec, 
    RCT_real, 
    marker='^',
    linestyle= linestyle,
    label= 'Real RCT'
)

#--- Plot for RCT1
plt.errorbar(partids, 
            rct1_chosen,
            yerr= [range1_min, range1_max], 
            fmt='o', 
            capsize=3, 
            linestyle= linestyle_rct1,
            label= "Expected RCT Path 1")

#--- Plot for RCT2
plt.errorbar(partids, 
            rct2_chosen, 
            yerr= [range2_min, range2_max], 
            fmt='x', 
            capsize=3, 
            linestyle= linestyle_rct2,
            label= "Expected RCT Path 2")

#--- Settings
# Add labels and title
plt.xlabel('Part ID')
plt.ylabel('Estimated RCT [seconds]')
plt.title('Plot RCT with Error Range')
plt.legend()
# Display the plot
#plt.show()

# ================================== Plotting ZigZag ==================================
from dtwinpylib.dtwinpy.tester import Plotter
plotter = Plotter(
    exp_database_path= database_path
)

plotter.plot_zigzage()

"""

plt.figure(figsize=(10, 5))
plt.plot(partids, RCT1_avg.values(), label="RCT 1", marker= "o")
plt.plot(partids, RCT2_avg.values(), label="RCT 2", marker= "x")
plt.xlabel("Part ID")
plt.ylabel("RCT [seconds]")
plt.title("Average of the Relative RCT 1 versus the normal RCT 1")
plt.legend()
plt.show()

part_id_now = 11
plt.figure(figsize=(10, 5))
plt.plot(RCT1_avg[f"Part {part_id_now}"], label="RCT2_avg", marker= "o")
plt.plot(RCT1_default[f"Part {part_id_now}"], label="RCT2_default", marker= "x")
plt.xlabel("time")
plt.ylabel("RCT [seconds]")
plt.title(f"Part {part_id_now}")
plt.legend()
plt.show()


#--- Plot Decisions Making
# Convert Queue 3 to 1 and Queue 4 to 2
for partid in Queues_selected.keys():
    if Queues_selected[partid] == "Queue 3":
        Queues_selected[partid] = 1
    if Queues_selected[partid] == "Queue 4":
        Queues_selected[partid] = 2
for partid in Queues_avg_selected.keys():
    if Queues_avg_selected[partid] == "Queue 3":
        Queues_avg_selected[partid] = 1
    if Queues_avg_selected[partid] == "Queue 4":
        Queues_avg_selected[partid] = 2

plt.figure(figsize=(10, 5))
plt.plot(partids, Queues_selected.values(), label="Queue Selected", marker= "o")
plt.plot(partids, Queues_avg_selected.values(), label="Queue Selected based on the Average", marker= "x")
plt.xlabel("Part ID")
plt.ylabel("Queue Selected")
plt.title("Decision Making")
plt.legend()
plt.show()


#--- Compare the Queues selected with the Queues selected based on the average
correct_counter = 0
wrong_counter = 0

for partid in partids:
    if Queues_selected[f"Part {partid}"] == Queues_avg_selected[f"Part {partid}"]:
        correct_counter += 1
    else:
        wrong_counter += 1

#--- Calculate the percentage of correct and wrong
percentage_correct = (correct_counter/(correct_counter + wrong_counter))*100
percentage_wrong = (wrong_counter/(correct_counter + wrong_counter))*100

#--- Print Percentage Results
helper.printer(f"Percentage of correct: {percentage_correct} %", "green")
helper.printer(f"Percentage of wrong: {percentage_wrong} %", "red")
"""

        



