import json
from DigitalModel_temp import DigitalModel_forecast
import pandas as pd
import statistics

with open('exec_model_validation.json') as f:
    model_temp = json.load(f)

model = DigitalModel_forecast(model_temp)

# I added the load time to the two machines, this way we can use the same distributions as the real model
model.ObjectList[0].unloadRng.mean += 4.4
model.ObjectList[1].unloadRng.mean += 4.4
model.nodes['M1']['unloadTime']['Fixed']['mean'] += 4.4
model.nodes['M2']['unloadTime']['Fixed']['mean'] += 4.4

actual_produced = 88

n_parts_real = [3, 16, 24, 35, 47, 61, 77]

init_list = [
    [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
    [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]
]

forecast_minute = [35, 30, 25, 20, 15, 10, 5]

# =============================================================
# DISTRIBUTIONS PARAMETERS
# =============================================================

distrM1 = "exp"
distrM2 = "exp"
paramM1 = [16]
paramM2 = [16]

distr_dict = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table = pd.DataFrame(distr_dict)

# Prediction
prediction_temp = []
error_temp = []
error_temp_abs = []
stdev_production = []
stdev_error = []
for time_id in range(7):  # cycle all the forecast
    results = model.runStochSimulation(
        distr_table, forecast_minute[time_id] * 60, 20, init_list[time_id], time_id*6)
    systime_list = results['elementList'][0]['results']['system_time_trace']
    list_produced = []
    list_error = []
    list_error_abs = []
    for rep in systime_list:
        list_produced.append(len(rep))
        list_error_abs.append(abs(len(rep) + n_parts_real[time_id] - actual_produced))
        list_error.append(len(rep) + n_parts_real[time_id] - actual_produced)
    # print(list_produced)
    # print(statistics.stdev(list_produced))
    stdev_production.append(statistics.stdev(list_produced))
    stdev_error.append(statistics.stdev(list_error))
    avg_produced_sim = statistics.mean(list_produced)
    avg_error_sim = statistics.mean(list_error)
    avg_error_sim_abs = statistics.mean(list_error_abs)
    avg_produced = avg_produced_sim + n_parts_real[time_id]
    prediction_temp.append(avg_produced)
    error_temp.append(avg_error_sim)
    error_temp_abs.append(avg_error_sim_abs)

column_names = ['Forecast at 5', 'Forecast at 10', 'Forecast at 15', 'Forecast at 20', 'Forecast at 25',
                'Forecast at 30', 'Forecast at 35']
index_names = ['Prediction', 'Error', 'Absolute Error', 'St.Dev. Production', 'St.Dev. Error']
result_list = [prediction_temp, error_temp, error_temp_abs, stdev_production, stdev_error]
result_df = pd.DataFrame(result_list, columns=column_names, index=index_names)

save_bool = input('\n+++ SAVE THE FILE INTO EXCEL?: ')
with pd.ExcelWriter('Output_scenario_5.xlsx') as writer:
    result_df.to_excel(writer)
