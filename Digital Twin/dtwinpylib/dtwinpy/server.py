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
    
    def get_branch_choices(self):
        #--- Get the Branches objects
        branches = self.digital_model.get_branches()

        #--- branches_choices
        branches_choices = []

        #--- For each branch, get the choices (conveyors)
        for branch in branches:
            #-- Get Conveyors of the branch
            current_branch_choices = branch.get_conveyors()

            #-- Add conveyors choice of the branch to the global choice
            branches_choices.append(current_branch_choices)

        return branches_choices


    def generate_path_scenarios(self):
        #--- Get all the branches choices in the digital model
        
