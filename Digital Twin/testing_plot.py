from dtwinpylib.dtwinpy.tester import Plotter
from dtwinpylib.dtwinpy.tester import Tester
from dtwinpylib.dtwinpy.Digital_Twin import Digital_Twin
from dtwinpylib.dtwinpy.helper import Helper
import sqlite3
import json
import numpy as np
helper= Helper()


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
exp_database_path= 'data_generation/3.30.16.41/databases/exp_database.db'
fig_path = 'data_generation/3.30.16.41/figures'



with sqlite3.connect("allexp_database.db") as db:
    all_exp_ids = db.execute(
        """
        SELECT exp_id FROM experiment_setup
        """
    ).fetchall()

    #--- Adjust tuple
    for i in range(len(all_exp_ids)): all_exp_ids[i] = all_exp_ids[i][0]


for exp_id in all_exp_ids:
    #tester = Tester(exp_id=exp_id, from_data_generation= True)
    #tester.plot(show_plot= False)

    exp_database_path= f'data_generation/{exp_id}/databases/exp_database.db'
    fig_path = f'data_generation/{exp_id}/figures'


    mydt = Digital_Twin(name= 'None', keepModels= True)
    plotter = Plotter(
    exp_database_path= exp_database_path,
    plotterDT= mydt,
    figures_path= fig_path,
    show= False
    )

    try:
        plotter.plot_comparative_RCT()
    except:
        helper.printer(f"It was not possible to plot for {exp_id}")


#exp_db_path = 'databases/CT/exp_database.db'
#real_db_path = 'databases/CT/real_database.db'
#fig_path = 'figures/CT'




#tester = Tester(name= "CT")
#tester.run_analysis(real_db_path)








