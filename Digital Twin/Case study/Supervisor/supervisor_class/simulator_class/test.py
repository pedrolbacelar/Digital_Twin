import sys

sys.path.append(r'C:\Users\THE FACTORY PC 2\Politecnico di Milano\Francesco Verucchi - EDO&FRA_tesi\Case study\Supervisor\supervisor_class\simulator_class\manpy')
sys.path.append('../')

import json
from DigitalModel_temp import DigitalModel_forecast
import pandas as pd

# directory_in = "C:/Users/edoar/repos/Model_Generator/AA_Trials/Validation test/Arena/LEGO Model dist/Files/"
# directory_out = "C:/Users/edoar/repos/Model_Generator/AA_Trials/Validation test/Arena/LEGO Model dist/Output/"
# dir_model = "C:/Users/edoar/repos/Model_Generator/AA_Trials/Validation test/"

with open("exec_model_validation.json") as f:
    in_data = json.load(f)

# distrM1 = "fixed"
# distrM2 = "fixed"
# paramM1 = [14.4]
# paramM2 = [16.4]
distrM1 = "triangular"
distrM2 = "triangular"
paramM1 = [12, 30, 24]
paramM2 = [12, 35, 19]

distr_dict = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table = pd.DataFrame(distr_dict)

initWIP = []
init_1 = 12
init_2 = 0
for i in range(init_1):
    initWIP.append(1)
for i in range(init_2):
    initWIP.append(2)
n_pallet = len(initWIP)

model = DigitalModel_forecast(in_data)
sim_time = 60*60*0.5
n_replications = 5
confid_level = 0.95

results = model.runStochSimulation(distr_table, sim_time, n_replications, initWIP, 45)

systime = results['elementList'][0]['results']['system_time_trace']
print(len(systime[0]))

timelog_list = []
ID_list = []
systime_list = []
rep_list = []

for i, rep in enumerate(systime):
    for data in rep:
        timelog_list.append(data[0])
        ID_list.append(data[1])
        systime_list.append(data[2])
        rep_list.append(i+1)

# print(rep_list)

