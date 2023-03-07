#--- Import DT Features
from .broker_manager import Broker_Manager

#--- Common Libraries
from matplotlib import pyplot as plt
import re


class Service_Handler():
    """
    ## Description
    The server is responsible for executing the external services of
    the Digital Twin, such as Remaining Cycle Time prediction and Decision
    Making based on RCT for branch points.

    ## RCT-based decision making
    The RCT is used as criteria for deicision making in branch points. When
    a part in the real world arrives in a Branch Point this services is reqquested.
    - Measure how many brench points exists in the simulation
    >Scenario Creation<
    - For a given part id, creates the total amount of combination possible
    of paths using the existing branch points 
    - Each combination creates a part with the right branch parameters for decision
    making
    >Measurement<
    - Each part is a simulation that will generate an RCT
    - The Server measures as well the RCT indicator that is basically comparing the
    current RCT with the highes (1 - RCTi / max(RCT) )
    - If the lowest RCT path is lower thant a certaing threshold,
    the Server will choose the combination with lowest RCT to be implemented
    - In the end, is also possible to calculate (using the real log) what would be
    the RCT of the part with and without the RCT optimization

    **Branch Point:** Is defined as point in the model where a machine can create
    different branchs, i.e, a machine with multiple output queues. In this type of point
    a machine in the physical world needs take a decision about where to put the part in 
    the most optimized path.

    """
    def __init__(self, name, generate_digital_model, broker_manager):
        self.name = name
        self.generate_digital_model = generate_digital_model
        self.digital_model = generate_digital_model(verbose= False)
        self.broker_manager = broker_manager

        #--- Get the components from the digital model
        self.branches = self.digital_model.get_branches()
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()
        self.part_vector = self.digital_model.get_all_parts()
    
    def get_branch_choices(self):
        """
        Function to return a vector with all the branches choices. 
        Choices are considered as the possible conveyors that a branch can choose.
        This vector is used to generate the path scenarios and is the based for
        the combinatory process.
        """

        #--- branches_choices
        branches_choices = []

        #--- For each branch, get the choices (conveyors)
        for branch in self.branches:
            #-- Get Conveyors of the branch
            current_branch_choices = branch.get_conveyors()

            #-- Add conveyors choice of the branch to the global choice
            branches_choices.append(current_branch_choices)

        return branches_choices

    def get_parts_making_decisions(self, queue_position = 2):
        """
        This functions look through digital model and search for parts within
        queues input of branching machines and see if there is any part in the
        right position for calculations (queue_position). This Queue Position is a
        position within a queue that is required to the Digital Twin have enough
        time to the calculation, that's why it's an input. As default, the
        queue_position is 2 (the second position of the queue, not the 3° position)
        """
        parts_making_decisions = []

        #--- For each existing branching point
        for branch in self.branches:
            #--- Get Queues In of the branching point
            branch_queues_in = branch.get_branch_queue_in()
            #--- For each queue in of the branches queues (ideally there is just one queue in)
            for queue in branch_queues_in:
                #-- Check if there is a part in the queue_position
                parts_in_queue = queue.get_all_items()

                #-- Check if the queue has a part in the right position
                if len(parts_in_queue) >= queue_position - 1:
                    parts_making_decisions.append(parts_in_queue[queue_position - 1])

        return parts_making_decisions

    def generate_path_scenarios(self, verbose = False):
        """
        ## Description
        This function generate the path scenarios based on combinations of 
        each branch choice. 

        ## TO-DO:
        1) Get the branches choices vector
        2) Based on this create a matrix of combinations (each line in the matrix is
        a different path that will need to be evaluated)
        """
        #--- Function to generate combinations recusively
        def generate_combinations(matrix):
            def generate_combinations_helper(matrix, current_index, current_combination, combinations):
                if current_index == len(matrix):
                    combinations.append(current_combination)
                    return
                for element in matrix[current_index]:
                    if element not in current_combination:
                        generate_combinations_helper(matrix, current_index + 1, current_combination + [element], combinations)

            combinations = []
            generate_combinations_helper(matrix, 0, [], combinations)
            return combinations
        
        #--- Get all the branches choices in the digital model
        branches_choices = self.get_branch_choices()

        #--- Generate the path scenarios based on the combination of branch choices
        path_scenarios = generate_combinations(branches_choices)

        #--- Show the paths generated
        if verbose == True:
            print("====== Paths Created ======")
            i = 1
            for path in path_scenarios:
                print(f"---- Path {i} ----")
                for convey in path:
                    print(convey.get_name())
                
                i += 1
            print("========================")
        return path_scenarios
    
    def assign_parts(self, SelecPath, path_scenarios, SelecPart = None):
        """
        ## Description
        This function is able to look into the existing parts in the simulation 
        and assign to each of them the paths to execute the simulation. The function
        select the parts waiting in the queue before branching points. For each branch point
        a set of copy of the same part is created for each possible path. The output of 
        this is a dictionary that give the copy parts for each branch point. This dictionary will
        be used for run the simulations. The function receives also for each scenario position it's 
        running. The trick part here is when we have more complex system where it's possible
        to have multiple parts in the decision making point.

        #### TO-DO:
        1) get the path scenarios
        2) Loop through each branch point
            3) Look the branch queue in if there is any part in first queue position take it
            4) Save all of this parts in a vector of parts that are waiting for take a decision
            5) For each part component assign the selected path according to the input in this fucntion 
        """
        #--- Extract the selected path
        selected_path = path_scenarios[SelecPath]

        #--- For each existing branching point
        for branch in self.branches:
            #--- Get Queues In of the branching point
            branch_queues_in = branch.get_branch_queue_in()
            parts_in_branching_dm = []

            #--- Check for each queue if there is a part in position for decision making
            for queue in branch_queues_in:

                ### ============== APPROACH 1 ============== ###
                # In this approach, the same path is allocated for all
                # the parts in a branching point of the simulation. The
                # good of this approach it needs to run less simulation,
                # because the number of simulation here is limited by the
                # number of scenarios (that is the combination of brench points
                # and their possibilities) and the number of brench points. 
                # Total Simulations = N. Brenches x N. Scenarios. The bad 
                # of this approach is that in the end on path of one part
                # is influencing the other.

                if SelecPart == None:
                    #--- There is at least a part in position 1 (0,1,2)
                    if queue.get_len() > 1:
                        #-- Take the part and assign the path selected
                        queue_parts = queue.get_all_items()
                        dm_part = queue_parts[1] # decision making part

                        #-- Assign for the part the selected path
                        dm_part.set_branching_path(selected_path)

                        #-- Save the parts in DM
                        parts_in_branching_dm.append(dm_part)

                ### ============== APPROACH 2 ============== ###
                # In this approach, only the Selected Part receives
                # the path, which means that for the simulation of this
                # part, the rest of the parts (including different parts in brench
                # points) will run as default. The good of this approach is that
                # we're testing the perfomance of this part for different scenarios
                # as it was in isolated scenario. Thus, this simulation doesn't 
                # has influence of other decision making.

                if SelecPart != None:
                    #--- Search in the queue brench for the selected part
                    parts_in_queue = queue.get_all_items()
                    #-- For each part in the queue 
                    for part in parts_in_queue:
                        #-- Found the selected part
                        if part.get_id() == SelecPart.get_id():
                            #-- Assign for the part the selected path
                            part.set_branching_path(selected_path)
        #--- Return the parts that were in branching decision to be possible to calculate their RCT
        return parts_in_branching_dm
    
    def simulate_paths(self,possible_pathes, parts_making_decisions, verbose= False):
        #--- Dictionary to store parts and its cycle time
        rct_dict = {}

        #--- For each part, let's simulate all the scenarios
        for part_id in range(len(parts_making_decisions)):
            part = parts_making_decisions[part_id]

            #--- For each existing path scenario
            path_counter = 1

            #--- Vector with RCT of each simulation
            rct_vector = []

            #--- Simulaion AS IS
            print(f"====================================== Simulation AS IS for {part.get_name()} ======================================")
            self.digital_model = self.generate_digital_model(targeted_part_id= part.id, verbose= False)
            self.digital_model.run()
            #- Get the RCT for the Simulation AS IS
            part_rct = self.digital_model.calculate_RCT(part_id_selected= part.id)
            rct_vector.append(part_rct)

            for path_scenario in possible_pathes:
                #--- Before assigning a new path and run a simulation, it's necessary to recreate the model (this generate new components / objects)
                self.digital_model = self.generate_digital_model(targeted_part_id= part.id, verbose= False)

                #--- Get Parts from the Digital Model
                current_parts_vector = self.digital_model.get_all_parts()

                #--- Assign to that part the current path scenario being analysed 
                for current_part in current_parts_vector:
                    if current_part.get_id() == part_id + 1:
                        current_part.set_branching_path(path_scenario)
                        part_being_simulated = current_part

                #--- Show the paths
                if verbose == True:
                    print(f"====================================== Running Scenario for {part.get_name()} | Path {path_counter} ======================================")
                    print(f"--- Showing Path for {part_being_simulated.get_name()} ---")
                    for convey in part_being_simulated.get_branching_path():
                        print(f"|-- {convey.get_name()}")
                    print("---")

                #--- Run the simulation
                self.digital_model.run()

                #--- Get the RCT for that path simulated
                part_rct = self.digital_model.calculate_RCT(part_id_selected= part_being_simulated.get_id())

                #--- Store the RCT of that simulation
                rct_vector.append(part_rct)

                #-- Increment the counter
                path_counter += 1
            
            #--- After finishing all the scenarios for that part, store RCT of each path
            rct_dict[part_being_simulated.get_name()] = rct_vector

        if verbose==True:
            print("____________________________________________")
            print("------ RCT Services Results: ------")
            for key in rct_dict:
                print(f"{key}: {rct_dict[key]}")

            print("------ Plot Results ------")
            #-- Count the number of scenarios
            x_scenarios = [0]
            for i in range(len(possible_pathes)):
                x_scenarios.append(i + 1)

            plt.title("Remaining Cycle Time for each path")
            plt.xlabel("Path Scenarios and Parts")
            plt.ylabel("Remaing Cycle Time")

            width = 0.4
            delta_x = width + 0.01
            for key in rct_dict:
                plt.bar(x_scenarios, rct_dict[key], width= width, label= key)

                for i in range(len(x_scenarios)):
                    x_scenarios[i] += delta_x 
            plt.legend()
            plt.show()

            plt.title("Max and Min RCT for each part")
            plt.xlabel("Parts")
            plt.ylabel("Remaing Cycle Time")
            vectors = []
            labels = []
            for key in rct_dict:
                vectors.append(rct_dict[key])
                labels.append(key)
            plt.boxplot(vectors, labels=labels)
            plt.legend()
            plt.show()

            print("____________________________________________")
        
        #--- Give back the dict with the RCTs for each part
        return rct_dict

    def RCT_check(self, rct_dict, rct_threshold, possible_pathes, verbose= False):
        """
        This function calculates the efficiency of each path comparing the path
        with the worst path. It can be seen as the gain of choosing that path.
        Thus, the worst path has 0% of gain, and the other path has something bigger.
        If the gain of the best path is not higher than the rct_threshold, than doesn't
        make sense to change the policy of the system (because both path are quite the same).

        feedback format:
        {
            'Part 1': (feedback_flag, [conveyor 1, conveyor 3, ...], gain)
            'Part 2': (feedback_flag, [conveyor 2, conveyor 4, ...], gain)
        }

        TO-DO:
        1) Do the following calculation for each Part making a decision
            2) find the max RCT and store it
            3) Loop through all the RCT
                4) Calculate RCT indicator (RCTi / RCTmax)
                5) Calculate the gain 1 - RCTindicator
                6) Store this in a new dict (gain_dict)
            7) Look to the higher gain and compare with the threshold
        """
        #--- Create the gain dictionary
        gain_dict = {}

        #--- Create the feedback dictionary
        feeback_dict = {}

        #--- For each part making a decision
        for key in rct_dict:
            #--- Create the feedback flag
            flag_feedback = False
            path_to_implement = 0

            #--- RCT of this part for each path
            rcts_paths = rct_dict[key]

            #--- Find the highest RCT for that part
            ASIS_RCT = rcts_paths[0]

            #--- Create the gain vector
            gain_vect = []

            #--- For each RCT of that part
            for rct in rcts_paths:
                #--- Calculate the RCT Indicator (how close it's from the worst scenario)
                rct_indicator = rct / ASIS_RCT

                #--- Calculate the RCT Gain (how far it's from the worst scenario)
                rct_gain = 1 - rct_indicator

                #--- Store this gain into the gain vector
                gain_vect.append(rct_gain)

            #--- Compare the higher gain with the threshold
            highets_gain = max(gain_vect)
            
            if highets_gain >= rct_threshold:
                #-- Rise the feedback flag
                flag_feedback = True
                #-- Take note of the optimized path
                path_to_implement = gain_vect.index(highets_gain) 

            #--- Update Dictionaries
            gain_dict[key] = gain_vect
            feeback_dict[key] = (flag_feedback, path_to_implement, highets_gain)

        #--- Plotting
        if verbose == True:
            plt.title("Gain of each path compared to the normal (AS-IS) path")
            plt.xlabel("Paths")
            plt.ylabel("Gain")

            # Create a list of markers
            markers = ['o', 's', '^', 'd', 'v', 'p', '*', 'x', '+']

            # Create a vector of datas to be plotted (y)
            datasets = []
            labels = []
            for key in gain_dict:
                datasets.append(gain_dict[key])
                labels.append(key)
            # Count Paths (x)
            x_data = []
            for i in range(len(datasets[0])):
                x_data.append(f"Path {i}")
            # Plot the data using different markers for each dataset

            for i, y in enumerate(datasets):
                marker = markers[i % len(markers)]
                plt.plot(x_data, y, marker=marker, label= labels[i], linestyle= '')
            
            plt.axhline(rct_threshold, color='red', linestyle='--', label='RCT Threshold')

            plt.legend()
            plt.show()

            #--- Printing the findings
            for key in feeback_dict:
                flag = feeback_dict[key][0]
                path_index = feeback_dict[key][1]
                highets_gain = feeback_dict[key][2]

                if flag == True:
                    print()
                    print(f"!!!!!!!!! Optimized Path Found for {key} !!!!!!!!!")
                    print(f"> Best Path: Path {path_index}")
                    print(f"> Gain: {format(highets_gain * 100, '.3f')} %") 
                    print("> Path:")
                    for convey in possible_pathes[path_index - 1]:
                        print(f"|- {convey.get_name()}")
                
                else:
                    print(f"----- No Path found with gain higher than {rct_threshold * 100}% -----")
            
        #--- Return the feedback flag and the chosen path index (dictionary)
        return feeback_dict[key]

    def publish_feedback(self, feedback_dict):
        """
        This function is able to take the feedback dictionary with the instructions of the most optimized
        path for the parts taking decision and send it to the right machine in the physical system.

        feedback format:
        {
            'Part 1': (feedback_flag, [conveyor 1, conveyor 3, ...], gain)
            'Part 2': (feedback_flag, [conveyor 2, conveyor 4, ...], gain)
        }

        TO-DO:
        1) Change the feedback format. For each part:
            1.0) Check if the flag to implement is True
            1.1) For each conveyor
                1.1.1) Find the unique branch machine correlated to it and take not of the id
                1.1.2) Now the format should be like:
                {'Part 1': [(convey 2, machine 1), (convey 5, machine 3), ...]}
        2) For each part, use the publishing function to pass the machine_id, part_id, and queue_id (convey id)
        """
        #---- Changing the feedback format
        #--- Loop through each part in the feedback dictionary
        for part_name in feedback_dict:
            #--- Get the part id from the string
            part_id = re.findall(r'\d+', part_name)[0]

            #--- Extract information from the dictionary
            feedback_flag = feedback_dict[part_name][0]
            path_to_implement = feedback_dict[part_name][1]
            gain = feedback_dict[part_name][2]

            #--- Check if the flag says to change the path or keep as usual
            if feedback_flag == True:

                #--- Find the location of the current part
                for part in self.part_vector:
                    #-- Found the part
                    if part.get_id() == part_id:
                        #-- Get location
                        part_location = part.get_location()
                
                #--- Find the branch based on the Queue ID
                for branch in self.branches:
                    branch_queue_ins = branch.get_branch_queue_in()
                    branch_machine = branch.get_branch_machine()

                    for branch_queue_in in branch_queue_ins:
                        #--- Found a branch that has our part
                        if branch_queue_in.get_id() - 1 ==  part_location:
                            #--- Found a branch with the unique convey, so take the machine id of that branch
                            machine_selected = branch_machine

                #---- Prepare the payload
                #--- Since the feedback is only for the rigth next branching machine,
                # we just care about the  conveyor in which the path selected
                machine_id = machine_selected.get_id()
                queue_id = path_to_implement[part_location].id
                # part_id already there

                #--- Send the MQTT publish payload
                self.broker_manager.publishing(
                    machine_id= machine_id, 
                    part_id= part_id, 
                    queue_id= queue_id, 
                    topic= "RCT_server"
                )

            else:
                pass

            
    def run_RCT_service(self, queue_position= 1, verbose= False):
        """
        ## Description
        This run method is one of the service related to the decision making based on the 
        prediction of the path with less RCT. 

        #### TO-DO
        - Indentify the approach selected
        ##### Approach 1
        1) Get the all the path
        2) Create a dict for each path to store the RCT for each part after the simulation is done
        3) Loop through the number os paths created
            - take the current path being analysed
            - use that path as input for the function of assigning paths to the parts
            - run the simulation
            - for each part that were in branchin DM, store the RCT for each path 
                - Maybe a matrix, each line for a part and each collunm for a simulation
                - Or in dicitonary...

        ##### Approach 2
        1) Get all the possible paths
        2) Get all the parts in Branching Points
        3) For each part in Branching Point ...
            4) For each possible path ...
                5) Assign to that part the current path
                6) Simulated
                7) Get the RCT 
                8) Stored it in a dict, where the key is the part name and the data is
                a vector where each element of the vector is the RCT for a path.
                Thus, following the same order as simulate ( ordered of path)
        9) Call a function to analyse the RCTs from the dict (RCT check)
            9.1) The function should compare the RCTs value and see if it's higher than
            a threshold
            9.2) If higher, return the choosen path
        10) Future: Send the choosen path to the machines of the parts
        """
        #--- Get all possible combination of path based on branching
        possible_pathes = self.generate_path_scenarios(verbose= verbose)

        #--- Get parts in positions of making decisions
        parts_making_decisions = self.get_parts_making_decisions(queue_position= queue_position)

        #--- Simulate for each path
        rct_dict = self.simulate_paths(possible_pathes= possible_pathes, parts_making_decisions= parts_making_decisions, verbose= verbose)

        #--- Check if there are a big difference between choices
        feedback_dict = self.RCT_check(rct_dict= rct_dict, rct_threshold= 0.1,possible_pathes = possible_pathes, verbose=verbose)

        #--- Send the chosen path to the rigth machine
        self.publish_feedback(feedback_dict= feedback_dict)