# Class evaluator
from supervisor_class.simulator_class.manpy.DigitalModel import DigitalModel
import supervisor_class.simulator_class.manpy.simulation.Globals as Globals
import scipy.stats
import math
import threading
from time import sleep
import datetime as dt
import json
from supervisor_class.synchroniser_class.broker_c_WI import broker


class Evaluator(threading.Thread):

    def __init__(self, db, time_interval):
        threading.Thread.__init__(self)
        self.time_interval = time_interval

        # There are three modes: "standby", "waiting" and "evaluate"
        # When status is:
        #   "standby": The last valid distribution is already evaluated, waiting for input not validated
        #   "waiting": The last distribution is not validated, waiting for a new one to be fitted and validated
        #   "evaluate": When a new distribution is validated, it starts being evaluated
        self.flag = "evaluate"
        self.db = db
        self.initialization = True     # Must be True
        self.sim_time = 3600
        self.num_replications = 20
        self.confidence = 0.95
        self.what_if = False             # Must be False
        self.model = None
        self.init_pos = []
        self.distr_new = None
        self.distr_old = None

        self.ttr = 100

        self.start_time = dt.datetime.now()
        self.time_change = 5 * 60      # time at witch we change the distribution
        self.time_demonstration = 60 * 60       # total time of the demonstration
        self.change_flag = True        # Must be True

        self.topic = "topic/config"

        self.brok = broker("192.168.0.50", 1883, 60, "RTSimulatorDB")

        print("\n=========================================================")
        print(f'THE EVALUATOR CLASS IS INITIALIZED AT TIME: {self.start_time}')
        print("=========================================================\n")

        # # PLACEHOLDER
        # path_IN_model = "C:/Users/edoar/repos/Model_Generator/AA_Trials/Test Files/Input Files/"
        # with open(path_IN_model + 'Static_model.json') as f:
        #     in_data = json.load(f)
        # self.model = DigitalModel(in_data, 1)

        # READ EXTERNAL JSON WITH CONFIG
        path_IN_config = "C:/Users/edoar/repos/Model_Generator/AA_Trials/Miscellaneous/WhatIf/"
        # with open(path_IN_config + 'ims_config.json', 'r') as f:
        with open('ims_config.json', 'r') as f:
            json_str = f.read()
            ims_config = json.loads(json_str)
        self.config = ims_config

        # Write on the database
        self.db.writeData("case", "feedback_info", 0)
        self.db.writeData("scenario", "feedback_info", [1, 0, 0])
        self.db.writeData("scenario", "feedback_info", [2, 0, 0])

    # Performance analysis method
    def run(self):
        global condition_evaluator
        condition_evaluator = True
        while condition_evaluator:
            print("\n=========================================================")
            print("=========================================================\n")

            print("\n=========================================================")
            print(f'The current status is {self.flag}')
            print("=========================================================\n")
            print("\n=========================================================")
            print('Check if there are new distributions to evaluate')
            print("=========================================================\n")

            self.new_distribution_check()
            if self.flag == "evaluate":

                print("\n=========================================================")
                print(f'The current status is {self.flag}')
                print('A new distribution is being evaluated')
                print("=========================================================\n")

                self.perf_simulation()

            if self.what_if:
                self.perform_wi_analysis()
            self.distr_old = self.distr_new

            if self.change_flag:
                time_diff = (dt.datetime.now() - self.start_time).total_seconds()
                time_left = self.time_demonstration - time_diff
                print("\n=========================================================")
                print(f'Time since start of the evaluation: {time_diff}')
                print(f'Time left to the end of the demonstration: {time_left}')
                print("=========================================================\n")
                if time_diff > self.time_change:
                    print("\n=========================================================")
                    print('Changing the distribution on machine 2')
                    print("=========================================================\n")
                    self.config['w_distribution_par'] = [9, 14, 11]
                    self.brok.feedback(self.config, self.topic)
                    self.change_flag = False
                    self.db.writeData("case", "feedback_info", 1.0)
            # condition_evaluator = False

            sleep(self.time_interval)

    def new_distribution_check(self):

        if self.flag != "evaluate":
            # Query the last input validation
            validation_bool = self.db.queryData("input", "history_validation_Eval")
            if not validation_bool:
                self.flag = "waiting"
                print("\n=========================================================")
                print(f'The last distributions are not validated, waiting for a new distribution to be fitted and'
                      f' validated')
                print("=========================================================\n")
            elif validation_bool and self.flag == "waiting":
                self.flag = "evaluate"
            else:
                print("\n=========================================================")
                print('The last distribution is validated and already analyzed')
                print("=========================================================\n")

    def perf_simulation(self):
        # Modify the flag to standby
        self.flag = "standby"

        # Query the last distributions UNDERSTAND IF USE THE DISTRIBUTION ID
        self.distr_new = self.db.queryData("proc_time", "distributions", t_query=2)   # 2 is the number of machine
        if self.initialization:
            self.distr_old = self.distr_new
        # Query the last average throughput
        last_th = 0
        if not self.initialization:
            last_th = self.db.queryData("th_eval", "digital_perf_mean")

        # Query the last available executable model
        exec_model_temp = self.db.queryData("executable_model", "model")

        # Initialize the model
        self.model = DigitalModel(exec_model_temp, 1)

        # Download the initial position
        self.init_pos = self.db.queryData("final_position_eval", "initialization")
        # self.init_pos = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]
        # Run the simulation
        results = self.model.runStochSimulation(self.distr_new, self.sim_time, self.num_replications, self.init_pos)

        # Extract the list with the average throughput for each replication
        intarr_list = results['elementList'][0]['results']['interarrival_trace']
        intarr_list_mean = Globals.extract_mean_val(intarr_list, 2)
        th_list = [1/x for x in intarr_list_mean]

        # Build the confidence interval
        conf_interval = Globals.confidence_interval(th_list, self.confidence)

        # Upload the new confidence interval of the throughput
        self.db.writeData("th_eval", "digital_perf_mean", conf_interval)
        print("\n=========================================================")
        print(f'The new performances have been calculated, the new throughput is equal to {conf_interval[0]}')
        print("=========================================================\n")
        # Comparing the new throughput with the last one
        if not self.initialization:

            print("\n=========================================================")
            print('Comparing the new performances with the last validated')
            print("=========================================================\n")

            self.compare_th(last_th, conf_interval)
        self.initialization = False

    def compare_th(self, old_value, new_value):
        mean_val = [old_value[0], new_value[0]]     # means of the two alternatives
        t_val = scipy.stats.t.ppf((1 + self.confidence) / 2., self.num_replications - 1)        # t-student
        interval = [old_value[2] - old_value[0], new_value[2] - new_value[0]]   # intervals of the two alternatives
        se = [x/t_val for x in interval]        # squared error of the two alternatives
        se_sq = [pow(x, 2) for x in se]         # error of the two alternatives
        diff_mean = mean_val[0] - mean_val[1]    # difference of the means
        diff_interval = math.sqrt(se_sq[0] + se_sq[1])
        diff_interval = t_val * diff_interval       # new interval
        diff_conf = [diff_mean - diff_interval, diff_mean + diff_interval]
        print("\n=========================================================")
        print(f'The confidence interval of the difference of the last condition with the new one is: {diff_conf}')
        print("=========================================================\n")
        threshold = diff_mean - diff_interval
        # check if the threshold is higher than zero, if so the new alternative is slower that the last
        if threshold > 0:
            self.what_if = True
            print("\n=========================================================")
            print('The new performance is worse than the old one, do What-if analysis')
            print("=========================================================\n")
            # we perform what-if simulations

    def perform_wi_analysis(self):
        import statistics

        print("\n=========================================================")
        print('Performing What-if analysis')
        print("=========================================================\n")

        n_produced = []
        # We calculate the time that is left in the demonstration
        sim_time_left = self.time_demonstration - (dt.datetime.now() - self.start_time).total_seconds()

        print("\n=========================================================")
        print(f'Time left in the demonstration: {sim_time_left}')
        print("=========================================================\n")

        # Download the initial position
        self.init_pos = self.db.queryData("final_position_eval", "initialization")

        # Scenario 1 - Do Nothing
        # We continue with this distribution
        results = self.model.runStochSimulation(self.distr_new, sim_time_left, self.num_replications, self.init_pos)
        # Extract the number of parts produced
        n_produced.append(statistics.mean(results['elementList'][0]['results']['completed_jobs']))

        # Scenario 2 - Restore
        # We stop the machine for time equal to ttr and then start again with the previous distribution
        results = self.model.runStochSimulation(self.distr_old, sim_time_left - self.ttr,
                                                self.num_replications, self.init_pos)
        # Extract the number of parts produced
        n_produced.append(statistics.mean(results['elementList'][0]['results']['completed_jobs']))

        # Find the best scenario
        best_scen = n_produced.index(max(n_produced))
        print("\n=========================================================")
        print(f'The better performing scenario is scenario {best_scen+1}')
        print(f'Scenario 1 produced {n_produced[0]} parts in the next {sim_time_left/60} minutes')
        print(f'Scenario 2 produced {n_produced[1]} parts in the next {sim_time_left/60} minutes')
        print("=========================================================\n")

        # Implement the best solution
        self.feedback_loop(best_scen)

        # Write on the database
        # [index of scenario, n_produced, bool if implemented]
        # Scenario 1
        self.db.writeData("scenario", "feedback_info", [1, int(n_produced[0]), int(best_scen == 0)])
        # Scenario 2
        self.db.writeData("scenario", "feedback_info", [2, int(n_produced[1]), int(best_scen == 1)])

    def feedback_loop(self, index):
        # Scenario 1 - NOTHING CHANGES
        if index == 0:
            pass

        # Scenario 2
        if index == 1:
            print("\n=========================================================")
            print('Implementing Scenario 2')
            print("=========================================================\n")
            # First we need to change the configuration to initiate the stoppage on the machine
            self.config['failure_prob'] = 1             # The next part will initiate a failure
            self.config['failure_time'] = self.ttr      # Time spent by the machine in failure state

            self.brok.feedback(self.config, self.topic)

            # Wait some time before uploading the new configuration
            sleep(15)

            # Change the configuration so that we go back to the previous distributions
            self.config['failure_prob'] = 0
            self.config['w_distribution_par'] = [3, 8, 5]

            self.brok.feedback(self.config, self.topic)

        self.what_if = False
