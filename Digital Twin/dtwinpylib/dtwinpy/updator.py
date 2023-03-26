#--- Import features
from .helper import Helper
from .interfaceDB import Database

#--- Common Libraries
import numpy as np
import scipy.stats
import warnings
import matplotlib.pyplot as plt
import json

class Updator():
    """
    The class Updator is called when the validation is given a certain amount of indicators beyond
    the allowed threshold. 
    """
    def __init__(self, update_type, digital_model, real_database_path, start_time, end_time, model_last_sync, plot= False):
        #--- Create helper
        self.helper = Helper()

        #--- Basic Stuff
        self.update_type = update_type
        self.digital_model = digital_model
        self.model_last_sync = model_last_sync
        self.plot = plot

        #--- Setting Database
        self.real_database_path = real_database_path
        self.start_time = start_time
        self.end_time = end_time
        if self.update_type == 'logic': self.feature_usingDB= 'valid_logic'
        if self.update_type == 'input': self.feature_usingDB= 'valid_input'

        #--- Get the model components
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()

        #--- Create database object
        self.real_database = Database(
            database_path= self.real_database_path,
            event_table= 'real_log',
            start_time= self.start_time,
            end_time= self.end_time,
            feature_usingDB= self.feature_usingDB,
            model_update= True
        )

        #--- User Interface
        self.helper.printer(f"Updator for {self.update_type} created", 'brown')
        #print(f"Model path being updated: {self.digital_model.get_model_path()}...")
        print(f"Model path being updated: {self.model_last_sync}...")


    # ------------------------------ Main Updating Functions ------------------------------
    # ------ Update the the model logic using model generation ------
    def update_logic(self):
        ############# MODEL GENERATION (FUTURE ) #############
        self.helper.printer("[WARNING][updator.py/update_logic()] Trying to run Model Generation... This feature still in progress!")
        pass

    # ------ Update the model inputs using distribution fitting ------
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
        if self.plot == True:
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

    # ------ Generate traces of each machines ------
    def generate_qTDS_traces(self):
        """
        Same function used in Validator.
        """
        #--- Extract the unique parts IDs from the real log
        #machines_ids = self.real_database.get_distinct_values(column= "machine_id", table="real_log")
        machines_ids = self.real_database.get_machines_with_completed_traces()
        #--- Create matrix to store trace of process time for each part
        matrix_ptime_qTDS = {}
        machine_matrix_full_trace = []

        #--- Loop for each part of the simulation
        for machine_id in machines_ids:
            #--- Get the full trace for each machine
            machine_full_trace = self.real_database.get_time_activity_of_column(column= "machine_id", table="real_log", column_id=machine_id[0])
            
            
            machine_matrix_full_trace.append(machine_full_trace)

            #--- Initiate as blank values
            started_time = None
            finished_time = None
            processed_time = None
            machine_trace = []

            for event in machine_full_trace:
                #--- Extract the Started and Finished time
                if event[1] == 'Started':
                    started_time = event[0]
                elif event[1] == 'Finished':
                    finished_time = event[0]
                
                #--- Calculate the process time
                if started_time != None and finished_time != None:
                    processed_time = finished_time - started_time

                    #--- Add event process time to the machine trace
                    machine_trace.append(processed_time)

                    #--- reset local started and finished time for the next cycle
                    started_time = None
                    finished_time = None
                    processed_time = None

                #--- In the case of part that already was in the machine (worked_time)
                if finished_time != None and started_time == None:
                    processed_time = finished_time

                    #--- Add event process time to the part trace
                    machine_trace.append(processed_time)

                    #--- reset local started and finished time for the next cycle
                    started_time = None
                    finished_time = None
                    processed_time = None
            
            #--- Add machine trace to the matrix of all machines traces
            matrix_ptime_qTDS[machine_id[0]] = (machine_trace)

        print("--- Printing the sequence considered for update ---")
        for key in matrix_ptime_qTDS:
            print(f"{key}: {matrix_ptime_qTDS[key]}")
            
        #--- Return the matrix of traces
        return matrix_ptime_qTDS

    # ------ Check if it's a deterministic or distribution model ------
    def is_deterministic(self):
        #--- Initial flag as not deterministic
        flag_is_deterministic = False

        #--- Loop through all the machines to see if there is distribution machine
        for machine in self.machines_vector:
            if type(machine.get_process_time()) != list:
                #--- Got it, some of machines are not deterministic. Threating all as distribution
                flag_is_deterministic = True
        
        #--- Retunr the flag as a result
        return flag_is_deterministic

    def aligner(self, machine_id, new_process_time):
        """
        This function receive a INT machine id and a INT or LIST process time. Base on the 
        machine_id the function attribute to the write node in the model new process time.
        """
        #--- Get model path
        #model_path = self.digital_model.get_model_path()
        

        with open(self.model_last_sync, 'r+') as model_file:
            data = json.load(model_file)
            #--- For each machine (node)
            for node in data['nodes']:
                if node['activity'] == machine_id:
                    #--- Take the old process time:
                    old_process_time = node["contemp"]
                    machine_name = f'Machine {machine_id}'

                    #--- Update the process time
                    node["contemp"] = (new_process_time)

                    #--- User Interface
                    self.helper.printer(f"Process Time of {machine_name} updated from {old_process_time} to {new_process_time}.", 'brown')

            #---- Write Back the Changes
            # Move the file pointer to the beginning of the file
            model_file.seek(0)
            # Write the modified data back to the file
            json.dump(data, model_file)
            # Truncate any remaining data in the file
            model_file.truncate()



    # ---------------------------------------------------------------------------------------

    def run(self):
        """
        Run the model update for logic (if requested) or for input (if requested)
        """

        # --------------- Logic Model Update ---------------
        if self.update_type == 'logic':
            self.update_logic()

        # --------------- Input Model Update ---------------
        if self.update_type == 'input':
            #--- Generate the traces for all the machines
            matrix_ptime_qTDS = self.generate_qTDS_traces()

            #--- Check if the machine is deterministic or not
            flag_deterministic = self.is_deterministic()
            
            #--- Loop through all the machines to update all of them
            for key in matrix_ptime_qTDS:
                #--- Get the machine component
                machine = self.digital_model.get_selected_machine(machine_name= key)

                #--- Get the machine name and machine id
                machine_name = machine.get_name()
                machine_id = machine.get_id()

                #--- Get the machine trace
                machine_trace = matrix_ptime_qTDS[machine_name]

                #--- Generate the new process time
                update_result = self.update_input(machine_trace)

                #--- System Deterministic: Take just the mean value
                if flag_deterministic:
                    #--- Take the new process time (last position, mean)
                    new_process_time = update_result[-1]
                    new_process_time = round(new_process_time)

                #--- System not Deterministic: Take the distribution parameters
                if not flag_deterministic:
                    #--- Take the whole parameters
                    dist_name = update_result[0]
                    parameter_a = update_result[1]
                    parameter_b = update_result[2]

                    (new_process_time) = [dist_name, parameter_a, parameter_b]


                #--- Write the new process time in the json model
                self.aligner(machine_id, new_process_time)
            
        #--- Finished the Updated
        self.helper.printer("--- System Updated ---", 'green')