class Validator():
    def __init__(self, digital_model, simtype, matrix_ptime_qTDS = None, matrix_ptime_TDS = None):
        self.digital_model = digital_model
        self.simtype = simtype
        # qTDS: each row is the list of process time for each part
        self.matrix_ptime_qTDS = matrix_ptime_qTDS 
        # TDS: each row is the list of process time for each machine
        self.matrix_ptime_TDS = matrix_ptime_TDS

        #--- Get the components of the simulation
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()

    def set_qTDS(self):
        #--- Update each existing machine in the model
        for machine in self.machines_vector:
            #--- Set the type of Simulation
            machine.set_simtype("qTDS")

            #--- Get the related list of process time for that machine
            current_ptime_TDS = self.matrix_ptime_qTDS[machine.get_id() - 1]

            #--- Assign the list of processes time
            machine.ptime_qTDS(current_ptime_TDS)
    
    def set_TDS(self):
        #--- List for all parts in the simulation
        part_list = []
        #--- Get the existing parts already allocated in the Queues
        for queue in self.queues_vector:
            #-- get the parts from the current queue
            current_parts = queue.get_all_items()
            if current_parts != None:
                #-- add each part to main list
                for part in current_parts:
                    part_list.append(part)
        
