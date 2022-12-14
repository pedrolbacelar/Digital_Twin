import json
from DigitalModel_temp import DigitalModel_forecast
import pandas as pd
import statistics
import copy

with open('exec_model_validation.json') as f:
    model_temp = json.load(f)

model = DigitalModel_forecast(model_temp)

# I added the load time to the two machines, this way we can use the same distributions as the real model
model.ObjectList[0].unloadRng.mean += 4.4
model.ObjectList[1].unloadRng.mean += 4.4
model.nodes['M1']['unloadTime']['Fixed']['mean'] += 4.4
model.nodes['M2']['unloadTime']['Fixed']['mean'] += 4.4

actual_produced = [94, 90, 86, 92, 90]


# =============================================================
# INITIAL PARAMETERS FOR EACH MOMENT
# =============================================================
n_parts_real = [
    [4, 44, 82],    # moment 1
    [3, 41, 79],    # moment 2
    [0, 38, 75],    # moment 3
    [4, 42, 79],    # moment 4
    [2, 39, 77]     # moment 5
]

init_list = [
    [
        [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],       # moment 1
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ],
    [
        [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],       # moment 2
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2]
    ],
    [
        [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],       # moment 3
        [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ],
    [
        [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2],       # moment 4
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2]
    ],
    [
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],       # moment 5
        [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
        [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2]
    ]
]

forecast_minute = [35, 20, 5]

# =============================================================
# DISTRIBUTIONS
# =============================================================

# Config 1: mean=low variance=low dist=Weibull
# Config 2: mean=high variance=low dist=Weibull
# Config 3: mean=low variance=high dist=Weibull
# Config 4: mean=high variance=high dist=Weibull
# Config 5: mean=low variance=low dist=Uniform
# Config 6: mean=high variance=low dist=Uniform
# Config 7: mean=low variance=high dist=Uniform
# Config 8: mean=high variance=high dist=Uniform

model_list = []
distribution_list = []

# CONFIGURATION 1 mean=low variance=low dist=Weibull
distrM1 = "weibull"
distrM2 = "triangular"
paramM1 = [18, 3]
paramM2 = [10, 21, 20]

distr_dict_1 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_1 = pd.DataFrame(distr_dict_1)
distribution_list.append(distr_table_1)

model_1 = copy.deepcopy(model)
model_list.append(model_1)


# CONFIGURATION 2 mean=high variance=low dist=Weibull
distrM1 = "weibull"
distrM2 = "triangular"
paramM1 = [18, 3]      # [shape, scale]
paramM2 = [10, 21, 20]

distr_dict_2 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_2 = pd.DataFrame(distr_dict_2)
distribution_list.append(distr_table_2)

model_2 = copy.deepcopy(model)
model_2.ObjectList[0].unloadRng.mean += 4
model_2.nodes['M1']['unloadTime']['Fixed']['mean'] += 4
model_list.append(model_2)

# CONFIGURATION 3 mean=low variance=high dist=Weibull
distrM1 = "weibull"
distrM2 = "triangular"
paramM1 = [18.135, 2]  # [shape, scale]
paramM2 = [10, 21, 20]

distr_dict_3 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_3 = pd.DataFrame(distr_dict_3)
distribution_list.append(distr_table_3)

model_3 = copy.deepcopy(model)
model_list.append(model_3)

# CONFIGURATION 4 mean=high variance=high dist=Weibull
distrM1 = "weibull"
distrM2 = "triangular"
paramM1 = [18.135, 2]
paramM2 = [10, 21, 20]

distr_dict_4 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_4 = pd.DataFrame(distr_dict_4)
distribution_list.append(distr_table_4)

model_4 = copy.deepcopy(model)
model_4.ObjectList[0].unloadRng.mean += 4
model_4.nodes['M1']['unloadTime']['Fixed']['mean'] += 4
model_list.append(model_4)

# CONFIGURATION 5 mean=low variance=low dist=Uniform
distrM1 = "uniformSP"
distrM2 = "triangular"
paramM1 = [5.9515, 20.237]
paramM2 = [10, 21, 20]

distr_dict_5 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_5 = pd.DataFrame(distr_dict_5)
distribution_list.append(distr_table_5)

model_5 = copy.deepcopy(model)
model_list.append(model_5)

# CONFIGURATION 6 mean=high variance=low dist=Uniform
distrM1 = "uniformSP"
distrM2 = "triangular"
paramM1 = [5.9515, 20.237]
paramM2 = [10, 21, 20]

distr_dict_6 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_6 = pd.DataFrame(distr_dict_6)
distribution_list.append(distr_table_6)

model_6 = copy.deepcopy(model)
model_6.ObjectList[0].unloadRng.mean += 4
model_6.nodes['M1']['unloadTime']['Fixed']['mean'] += 4
model_list.append(model_6)

# CONFIGURATION 7 mean=low variance=high dist=Uniform
distrM1 = "uniformSP"
distrM2 = "triangular"
paramM1 = [1.5189, 29.1022]
paramM2 = [10, 21, 20]

distr_dict_7 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_7 = pd.DataFrame(distr_dict_7)
distribution_list.append(distr_table_7)

model_7 = copy.deepcopy(model)
model_list.append(model_7)

# CONFIGURATION 8 mean=high variance=high dist=Uniform
distrM1 = "uniformSP"
distrM2 = "triangular"
paramM1 = [1.5189, 29.1022]
paramM2 = [10, 21, 20]

distr_dict_8 = {
    "M1": [distrM1, paramM1],
    "M2": [distrM2, paramM2]
}
distr_table_8 = pd.DataFrame(distr_dict_8)
distribution_list.append(distr_table_8)

model_8 = copy.deepcopy(model)
model_8.ObjectList[0].unloadRng.mean += 4
model_8.nodes['M1']['unloadTime']['Fixed']['mean'] += 4
model_list.append(model_8)

# =============================================================
# CYCLE ALL THE MOMENTS AND SIMULATE
# =============================================================
results_final = []
column_names_f = ['Forecast at 5', 'Forecast at 20', 'Forecast at 35']
column_names_e = ['Error at 5', 'Error at 20', 'Error at 35']
index_names = ['Moment 1', 'Moment 2', 'Moment 3', 'Moment 4', 'Moment 5']
for conf_id in range(8):
    prediction_final = []
    error_final = []
    print(model_list[conf_id].ObjectList[0].unloadRng.mean)
    for mom_id in range(5):     # cycle the moments
        prediction_temp = []
        error_temp = []
        for time_id in range(3):    # cycle all the forecast
            results = model_list[conf_id].runStochSimulation(
                distribution_list[conf_id], forecast_minute[time_id]*60, 5, init_list[mom_id][time_id],
                (time_id+1)*(mom_id+1)*(conf_id+1))
            systime_list = results['elementList'][0]['results']['system_time_trace']
            list_produced = []
            list_error = []
            for rep in systime_list:
                list_produced.append(len(rep))
                list_error.append(abs(len(rep) + n_parts_real[mom_id][time_id] - actual_produced[mom_id]))
            avg_produced_sim = statistics.mean(list_produced)
            avg_error_sim = statistics.mean(list_error)
            avg_produced = avg_produced_sim + n_parts_real[mom_id][time_id]
            prediction_temp.append(avg_produced)
            error_temp.append(avg_error_sim)

        prediction_final.append(prediction_temp)
        error_final.append(error_temp)

    # prediction_df = pd.DataFrame(prediction_final, columns=column_names_f, index=index_names)
    # error_df = pd.DataFrame(error_final, columns=column_names_e, index=index_names)
    # prediction_df.join(error_df)
    print(model_list[conf_id].ObjectList[0])
    print(model_list[conf_id].ObjectList[0].unloadRng.mean)
    list_df_temp = [pd.DataFrame(prediction_final, columns=column_names_f, index=index_names),
                    pd.DataFrame(error_final, columns=column_names_e, index=index_names)]
    # results_final.append(pd.DataFrame(prediction_final, columns=column_names_f, index=index_names))
    # error_final.append(pd.DataFrame(error_final, columns=column_names_e, index=index_names))
    results_final.append(pd.concat(list_df_temp, axis=1))

    print(f'Calculated results for configuration {conf_id+1}')

save_bool = input('\n+++ SAVE THE FILE INTO EXCEL?: ')
if save_bool:
    with pd.ExcelWriter('Output.xlsx') as writer:
        for save_id in range(8):
            # results_final[save_id].join(error_final[save_id])
            results_final[save_id].to_excel(writer, sheet_name='Configuration_' + str(save_id+1))
