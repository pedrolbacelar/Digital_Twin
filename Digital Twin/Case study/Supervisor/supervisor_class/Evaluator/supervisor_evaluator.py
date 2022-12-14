from Evaluator import Evaluator
from supervisor_class.database_class.interface_DB import interface_DB
import supervisor_class.simulator_class.manpy.simulation.Globals as Globals
import numpy as np
import scipy.stats
import math
import json

# IP = "localhost"
# DB_name = "RTSimulatorDB"
# port = 8086
IP = "192.168.0.50"
DB_name = "RTSimulatorDB"
port = 8086
db = interface_DB(IP, DB_name, port)
time_interval = 20
# ciao = db.queryData("input", "history_validation_Eval")
# print(ciao)
# print(json.loads(ciao[1]['values'][0][2]))
# print(len(ciao))

evaluator = Evaluator(db, time_interval)
evaluator.start()


# =============================================================
# CHECK IF THE FUNCTION compare_th() WORKS -> IT DOES
# a = [15.5, 16.3, 17.8, 19.2, 15.9]
# b = [13.2, 12.9, 13.5, 14.8, 15.0]
#
# conf_a = Globals.confidence_interval(a, 0.95)
# conf_b = Globals.confidence_interval(b, 0.95)
#
# # print(conf_a)
# # print(conf_b)
#
# a_arr = 1.0 * np.array(a)
# n_a = len(a_arr)
# m_a, var_a = np.mean(a_arr), np.var(a_arr)
#
# b_arr = 1.0 * np.array(b)
# n_b = len(b_arr)
# m_b, var_b = np.mean(b_arr), np.var(b_arr)
#
# t_val = scipy.stats.t.ppf((1 + 0.95) / 2., n_a - 1)
#
# h_diff = math.sqrt(var_b/n_b + var_a/n_a)
# h_diff = t_val * h_diff
# m_diff = m_a - m_b
# conf_diff = [m_diff, m_diff - h_diff, m_diff + h_diff]
# print(conf_diff)
#
# mean_val = [conf_a[0], conf_b[0]]     # means of the two alternatives
# interval = [conf_a[2] - conf_a[0], conf_b[2] - conf_b[0]]   # intervals of the two alternatives
# se = [x/t_val for x in interval]        # squared error of the two alternatives
# se_sq = [pow(x, 2) for x in se]         # error of the two alternatives
# diff_mean = mean_val[0] - mean_val[1]    # difference of the means
# diff_interval = math.sqrt(se_sq[0] + se_sq[1])
# diff_interval = t_val * diff_interval       # new interval
# conf_diff_a = [diff_mean, diff_mean - diff_interval, diff_mean + diff_interval]
# print(conf_diff_a)







