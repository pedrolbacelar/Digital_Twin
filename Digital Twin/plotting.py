#--- Libraries
from dtwinpylib.dtwinpy.helper import Helper
from dtwinpylib.dtwinpy.tester import Tester
from dtwinpylib.dtwinpy.tester import Plotter


def plotting(exp_ids, plots= ["plot_valid_indicators", "plot_RCT_paths", "plot_queues_occupation", "plot_comparative_RCT", "plot_utilization", "plot_RCTtracking"], show= False, save= True):
    """
    Plot for all experiments IDs from exp_ids the plots indicated in the vector plots. 
    All the requiered information is extracted from allexp database.
    The function create a tester to help with the plotting.
    """

    #--- Run for all the exp_ids given
    for exp_id in exp_ids:
        #--- Create a Tester object
        tester = Tester(exp_id=exp_id, from_data_generation= True)

        #--- Initiate it for analysis
        tester.initiate_for_analysis()

        #--- Get the basic informations
        (exp_db_path, figures_folder, mydt) = tester.get_setup()

        #--- Run each required plot
        for plot_type in plots:
            #--- For every new plot, create a new plotter object
            plotter = Plotter(
                        exp_database_path= exp_db_path,
                        plotterDT= mydt,
                        figures_path= figures_folder,
                        show= show,
                        save= save
                    )

            # ------------------ Plotting Requireds ------------------
            
            # -- Plot Validation Indicators --
            if plot_type == "plot_valid_indicators":
                plotter.plot_valid_indicators()

            # -- Plot RCT Paths --
            if plot_type == "plot_RCT_paths":
                plotter.plot_RCT_paths()

            # -- Plot Comparative RCT --
            if plot_type == "plot_comparative_RCT":
                plotter.plot_comparative_RCT()

            # -- Plot Queues Occupation --
            if plot_type == "plot_queues_occupation":
                plotter.plot_queues_occupation()

            # -- Plot Comparative parts CT --
            if plot_type == "plot_comparative_parts_CT":
                plotter.plot_comparative_parts_CT()

            # -- Plot plot utilization --
            if plot_type == "plot_utilization":
                tester.plot_utilization()

            # -- Plot RCT tracking --
            if plot_type == "plot_RCTtracking":
                plotter.plot_RCTtracking()

############# Running #############
exp_ids = ["4.11.15.46", "4.11.17.26"]
exp_ids = ["4.11.15.46"]

#plots= ["plot_comparative_RCT", "plot_utilization", "plot_RCTtracking"]
plots= ["plot_RCTtracking"]
plotting(
    exp_ids= exp_ids,
    plots= plots
)

