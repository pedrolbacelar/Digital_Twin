class Sever():
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
    def __init__(self, name, digital_model):
        self.name = name
        self.digital_model = digital_model

        #--- Get the Branches objects
        self.branches = self.digital_model.get_branches()
    
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

        print(f"Branches Choices {branches_choices}")
        return branches_choices


    def generate_path_scenarios(self):
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
        return path_scenarios
    
    def assign_parts(self, SelecPath, path_scenarios, SelecPart = None):
        """
        ## Description
        This function is able to look into the existing parts in the simulation 
        and assign to it of them the paths to execute the simulation. The function
        select the parts waiting in the queue before branching points. For each branch point
        a set of copy of the same part is created for each possible path. The output of 
        this is a dictionary that give the copy parts for each branch point. This dictionary will
        be used for run the simulations. The function receives also for each scenario position it's 
        running. The trick part here is when we have more complex system where it's possible
        to have multiple parts in the decision making point.

        ## TO-DO:
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
    
    def run_RCT_service(self, approach):
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
        """


        