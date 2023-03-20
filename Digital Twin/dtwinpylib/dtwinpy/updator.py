#--- Import features
from dtwinpylib.dtwinpy.helper import Helper
from dtwinpylib.dtwinpy.interfaceDB import Database
import numpy as np
import scipy.stats
import warnings
import matplotlib.pyplot as plt

class Updator():
    """
    The class Updator is called when the validation is given a certain amount of indicators beyond
    the allowed threshold. 
    """
    def __init__(self, update_type, real_database_path, start_time, end_time):
        #--- Create helper
        self.helper = Helper()

        #--- Basic Stuff
        self.update_type = update_type
        self.real_database_path = real_database_path
        self.start_time = start_time
        self.end_time = end_time

        #--- Create database object
        self.real_database_updator = Database(
            database_path= self.real_database_path,
            event_table= 'real_log',
            start_time= self.start_time,
            end_time= self.end_time
        )

    
    # ------------------------------ Main Updating Functions ------------------------------
    def update_logic(self):
        ############# MODEL GENERATION (FUTURE ) #############
        pass

    def update_input(self, input_data, probable_distribution = None):
        #-- distributions list we are interested in.
        distribution_types_list = ['norm', 'expon']
        # distribution_types_list = ['norm', 'expon', 'gamma','erlang','weibull_min','weibull_max','triang','lognorm','beta']
        distribution_index = len(distribution_types_list)

        #-- initialte variables
        ks_result = np.zeros((distribution_index,2))
        parameters = [0 for _ in range(distribution_index)]

        #-- loop for fitting and testing all the distribution in the list
        for ii in range(distribution_index):
            #--- fit the distribution type to the data
            distribution = distribution_types_list[ii]
            
            warnings.filterwarnings("ignore", category=RuntimeWarning)  # we ignore RuntimeWarning

            parameters[ii] = list(getattr(scipy.stats, distribution).fit(input_data))
            
            #--- calculate the KS test statistic and p-value
            #-- Pick the distribution with the best p-value close to 1. p-value above 0.95 can be considered good.
            ks_result[ii,0], ks_result[ii,1] = scipy.stats.kstest(input_data, distribution, args=parameters[ii])  #-- output is D,p-value

            warnings.filterwarnings("default", category=RuntimeWarning) #-- we reset RuntimeWarning

        ks_best_id = np.argmax(ks_result,axis=0)[1]    #-- find index of best p-value (column index 1)
        ks = [distribution_types_list[ks_best_id], ks_result[ks_best_id,1]]
        
        #-- to print all the test results
        # print("result of ks_test = ",ks_result)
        # print("calculated parameters for each distribution = ", parameters)

        #-- QQ plot
        # plot with parameters of best distrribution
        plt.figure(figsize=(8, 6))
        res = scipy.stats.probplot(input_data, dist=ks[0], sparams=parameters[ks_best_id], plot=plt)
        plt.title(f"Normal Q-Q Plot with best fit distribution")
        plt.show()

        # plot with parameters of actual distrribution
        if probable_distribution != None:
            # plot with parameters of actual distrribution
            plt.figure(figsize=(8, 6))
            res = scipy.stats.probplot(input_data, dist=probable_distribution, sparams=parameters[distribution_types_list.index(probable_distribution)], plot=plt)
            plt.title(f"Normal Q-Q Plot with actual distribution")
            plt.show()
        
        # #-- to print selected distribution parameters
        # print(f"Best result is: {ks[0]} distribution with a p-value of {ks[1]:.6f}")
        # print(f"The calculated parameters are {parameters[ks_best_id]}")

        #--- calculating mean
        if ks[0] == "norm":
            mean = parameters[ks_best_id][0]
        elif ks[0] == "expon":
            mean = parameters[ks_best_id][0] + (1/parameters[ks_best_id][1])

        print(f"the identified parameter is '{ks[0]}' and its parameters are {parameters[ks_best_id][0]} and {parameters[ks_best_id][1]}.")
        print(f"The mean value calculated is {mean}.")

        return (ks[0],parameters[ks_best_id], mean)


        



    # ---------------------------------------------------------------------------------------

    def run(self):
        """
        Run the model update for logic (if requested) or for input (if requested)
        """

        # --------------- Logic Model Update ---------------
        if self.update_type == 'logic':
            pass

        # --------------- Input Model Update ---------------
        if self.update_type == 'input':
            self.update_input()