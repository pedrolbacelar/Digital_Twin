from dtwinpylib.dtwinpy.tester import Plotter

#exp_database_path = 'data_generation/3.27.19.50/databases/exp_database.db'
#exp_database_path = 'data_generation/3.27.19.22/databases/exp_database.db'
exp_database_path= 'data_generation/3.27.18.30/databases/exp_database.db'
figures_path = 'figures/test'

plotter = Plotter(
    exp_database_path= exp_database_path,
    show= True,
    figures_path= figures_path
)

plotter.plot_valid_indicators(threshold= 0.69)

plotter.plot_RCT_paths()