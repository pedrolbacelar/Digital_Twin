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

actual_produced = [93, 81, 220, 81, 412]

# =============================================================
# INITIAL PARAMETERS FOR EACH MOMENT
# =============================================================
n_parts_real = [
    [15, 26, 40, 48, 60, 71, 80],  # moment 1
    # [2, 15, 22, 35, 48, 61, 70],    # moment 2 REAL
    [2, 15, 22, 35, 48, 61, 69],  # moment 2
    [140, 153, 164, 173, 188, 202, 214],  # moment 3
    # [4, 17, 25, 37, 49, 56, 69],    # moment 4 REAL
    [4, 17, 25, 37, 49, 56, 68],  # moment 4
    [335, 348, 359, 372, 381, 392, 404]  # moment 5
]
init_list = [
    [
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],  # moment 1
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2]
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],  # moment 2
        [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
    ],
    [
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],  # moment 3
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],  # moment 4
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2]
    ],
    [
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],  # moment 5
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
    ]
]

forecast_minute = [35, 30, 25, 20, 15, 10, 5]

# =============================================================
# DISTRIBUTIONS PARAMETERS
# =============================================================

distrM1 = "weibull"
distrM2 = "triangular"
paramM1 = [18, 3]
paramM2 = [10, 21, 20]

distr_dict = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table = pd.DataFrame(distr_dict)

# =============================================================
# CYCLE ALL THE MOMENTS AND SIMULATE
# =============================================================

prediction_final = []
error_final = []
error_final_abs = []
for mom_id in range(5):  # cycle the moments
    prediction_temp = []
    error_temp = []
    error_temp_abs = []
    for time_id in range(7):  # cycle all the forecast
        results = model.runStochSimulation(
            distr_table, forecast_minute[time_id] * 60, 5, init_list[mom_id][time_id], (time_id + 137) * (mom_id + 43))
        systime_list = results['elementList'][0]['results']['system_time_trace']
        list_produced = []
        list_error = []
        list_error_abs = []
        for rep in systime_list:
            list_produced.append(len(rep))
            list_error_abs.append(abs(len(rep) + n_parts_real[mom_id][time_id] - actual_produced[mom_id]))
            list_error.append(len(rep) + n_parts_real[mom_id][time_id] - actual_produced[mom_id])
        avg_produced_sim = statistics.mean(list_produced)
        avg_error_sim = statistics.mean(list_error)
        avg_error_sim_abs = statistics.mean(list_error_abs)
        avg_produced = avg_produced_sim + n_parts_real[mom_id][time_id]
        prediction_temp.append(avg_produced)
        error_temp.append(avg_error_sim)
        error_temp_abs.append(avg_error_sim_abs)

    prediction_final.append(prediction_temp)
    error_final.append(error_temp)
    error_final_abs.append(error_temp_abs)

column_names_f = ['Forecast at 5', 'Forecast at 10', 'Forecast at 15', 'Forecast at 20', 'Forecast at 25',
                  'Forecast at 30', 'Forecast at 35']
column_names_e = ['Error at 5', 'Error at 10', 'Error at 15', 'Error at 20', 'Error at 25',
                  'Error at 30', 'Error at 35']
column_names_ea = ['Abs error at 5', 'Abs error at 10', 'Abs error at 15', 'Abs error at 20', 'Abs error at 25',
                   'Abs error at 30', 'Abs error at 35']
index_names = ['Moment 1', 'Moment 2', 'Moment 3', 'Moment 4', 'Moment 5']
list_df_temp = [
    pd.DataFrame(prediction_final, columns=column_names_f, index=index_names),
    pd.DataFrame(error_final, columns=column_names_e, index=index_names),
    pd.DataFrame(error_final_abs, columns=column_names_ea, index=index_names)
]
final_df = pd.concat(list_df_temp, axis=1)
print(final_df)

# Freq forecast
forecast_freq_list = []
forecast_5 = []
forecast_10 = []
forecast_15 = []
forecast_20 = []
forecast_40 = []
for err in error_final_abs:
    forecast_5.append((err[0] * 5 + err[1] * 5 + err[2] * 5 + err[3] * 5 + err[4] * 5 + err[5] * 5 + err[6] * 5)/35)
    forecast_10.append((err[0] * 10 + err[2] * 10 + err[4] * 10 + err[6] * 5)/35)
    forecast_15.append((err[0] * 15 + err[3] * 15 + err[6] * 5)/35)
    forecast_20.append((err[0] * 20 + err[4] * 15)/35)
    forecast_40.append(err[0])

forecast_freq_list = [forecast_5, forecast_10, forecast_15, forecast_20, forecast_40]

column_names_freq = ['Moment 1', 'Moment 2', 'Moment 3', 'Moment 4', 'Moment 5']
index_names_freq = ['TB_Forecast 5', 'TB_Forecast 10', 'TB_Forecast 15', 'TB_Forecast 20', 'TB_Forecast 40']
forecast_freq_df = pd.DataFrame(forecast_freq_list, columns=column_names_freq, index=index_names_freq)

mean_forecast_freq = [statistics.mean(forecast_5), statistics.mean(forecast_10),
                      statistics.mean(forecast_15),
                      statistics.mean(forecast_20), statistics.mean(forecast_40)]

stdev_forecast_freq = [statistics.stdev(forecast_5), statistics.stdev(forecast_10),
                       statistics.stdev(forecast_15),
                       statistics.stdev(forecast_20), statistics.stdev(forecast_40)]

forecast_freq_df['Mean'] = mean_forecast_freq
forecast_freq_df['St. Dev.'] = stdev_forecast_freq

print(forecast_freq_df)

save_bool = input('\n+++ SAVE THE FILE INTO EXCEL?: ')
if save_bool:
    with pd.ExcelWriter('Output_exp2.xlsx') as writer:
        final_df.to_excel(writer, sheet_name='Numerical results')
        forecast_freq_df.to_excel(writer, sheet_name='Forecast frequency')
