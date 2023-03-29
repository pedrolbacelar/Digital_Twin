from dtwinpylib.dtwinpy.tester import Plotter
from dtwinpylib.dtwinpy.tester import Tester
import sqlite3

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
exp_ids = ['3.28.16.31', '3.28.16.43', '3.28.16.54', '3.28.17.05', '3.28.17.18', '3.28.17.37']

with sqlite3.connect("allexp_database.db") as db:
    all_exp_ids = db.execute(
        """
        SELECT exp_id FROM experiment_setup
        """
    ).fetchall()

    #--- Adjust tuple
    for i in range(len(all_exp_ids)): all_exp_ids[i] = all_exp_ids[i][0]


for exp_id in all_exp_ids:
    tester = Tester(exp_id=exp_id, from_data_generation= True)
    tester.plot(show_plot= False)
