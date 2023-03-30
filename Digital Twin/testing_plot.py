from dtwinpylib.dtwinpy.tester import Plotter
from dtwinpylib.dtwinpy.tester import Tester
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
import sqlite3
import json
import numpy as np


"""
#exp_database_path = 'data_generation/3.27.19.50/databases/exp_database.db'
#exp_database_path = 'data_generation/3.27.19.22/databases/exp_database.db'
exp_database_path= 'data_generation/3.27.18.30/databases/exp_database.db'
exp_database_path= 'databases/5s_stho/exp_database.db'

figures_path = 'figures/test'

plotter = Plotter(
    exp_database_path= exp_database_path,
    show= True,
    figures_path= figures_path
)

plotter.plot_valid_indicators(threshold= 0.69)

#plotter.plot_RCT_paths()

#plotter.plot_queues_occupation(stacked= True)
"""

"""
exp_ids = ['3.28.16.31', '3.28.16.43', '3.28.16.54', '3.28.17.05', '3.28.17.18', '3.28.17.37']

with sqlite3.connect("allexp_database.db") as db:
    all_exp_ids = db.execute(
        "
        #SELECT exp_id FROM experiment_setup
        "
    ).fetchall()

    #--- Adjust tuple
    for i in range(len(all_exp_ids)): all_exp_ids[i] = all_exp_ids[i][0]


for exp_id in all_exp_ids:
    tester = Tester(exp_id=exp_id, from_data_generation= True)
    tester.plot(show_plot= False)
"""
exp_db_path = 'databases/CT/exp_database.db'
real_db_path = 'databases/CT/real_database.db'
fig_path = 'figures/CT'


tester = Tester(name= "CT")
tester.run_analysis(real_db_path)


mydt = Digital_Twin(name= "CT")
plotter = Plotter(
    exp_database_path= exp_db_path,
    plotterDT= mydt,
    figures_path= fig_path,
    show= True
)

plotter.plot_comparative_parts_CT()


"""
import matplotlib.pyplot as plt
import numpy as np

# Generate some sample data
x = np.linspace(0, 10, 20)
y1 = np.sin(x)
y2 = np.sin(x) + np.random.normal(0, 0.1, 20)

# Compute the error bars for each data point
err1 = 0.1 * np.ones_like(x)
err2 = 0.2 * np.ones_like(x)

# Create a line plot of the data
#plt.plot(x, y1, label='Ideal', marker= 'o')
plt.plot(x, y2, label='Digital', marker= 'o')

# Add error bars to show the range of the data points
plt.errorbar(x, y2, yerr=err2, linestyle='None', capsize=3, color='orange')

# Add labels and title
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Comparison of Digital and Physical Simulations with Ideal')

# Add a legend
plt.legend()

# Show the plot
plt.show()
"""

"""
import matplotlib.pyplot as plt

# generate some data
x = [1, 2, 3, 4, 5]
y1 = [10, 20, 30, 40, 50]
y2 = [2, 1, 3, 7, 2]

# create the figure and the first axis
fig, ax1 = plt.subplots()

# plot the first data set
ax1.plot(x, y1, color='blue')
ax1.set_xlabel('X-axis')
ax1.set_ylabel('Raw error', color='blue')

# create the second axis
ax2 = ax1.twinx()

# plot the second data set
ax2.plot(x, y2, color='red')
ax2.set_ylabel('Percentage of error', color='red')

# add a legend
ax1.legend(['Raw error'], loc='upper left')
ax2.legend(['Percentage of error'], loc='upper right')

plt.show()
"""

