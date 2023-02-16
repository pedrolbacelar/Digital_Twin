class Validator():
    def __init__(self, digital_model, simtype, real_event_log = None, matrix_ptime_qTDS = None, matrix_ptime_TDS = None):
        self.digital_model = digital_model
        self.simtype = simtype
        self.real_event_log = real_event_log
        # qTDS: each row is the list of process time for each part
        self.matrix_ptime_qTDS = matrix_ptime_qTDS 
        # TDS: each row is the list of process time for each machine
        self.matrix_ptime_TDS = matrix_ptime_TDS

        #--- Get the components of the simulation
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()

    # ======================= TRACE DRIVEN SIMULATION =======================
   
    #--- For a specific part ID return the related vector of ptime_TDS
    def get_part_TDS(self, part):
        return self.matrix_ptime_TDS[part.get_id() - 1]
    #--- Get the number of parts given in the TDS
    def get_len_TDS(self):
        return len(self.matrix_ptime_TDS)
    
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
        
        #--- give for each part the ptime_TDS list 
        for part in part_list:
            current_ptime_TDS = self.get_part_TDS(part)
            part.set_ptime_TDS(current_ptime_TDS)
        
        #--- Set the simulation type for all the machines
        for machine in self.machines_vector:
            #--- Set the type of Simulation
            machine.set_simtype("TDS")
 

    # =======================================================================




    # ==================== QUASI TRACE DRIVEN SIMULATION ====================

    def set_qTDS(self):
        #--- Update each existing machine in the model
        for machine in self.machines_vector:
            #--- Set the type of Simulation
            machine.set_simtype("qTDS")

            #--- Get the related list of process time for that machine
            current_ptime_TDS = self.matrix_ptime_qTDS[machine.get_id() - 1]

            #--- Assign the list of processes time
            machine.set_ptime_qTDS(current_ptime_TDS)

    
    # =======================================================================



    # ========================= Overlaping Functions =========================
    def allocate(self):
        if self.simtype == "TDS":
            #--- Set the TDS for each part
            self.set_TDS()

        if self.simtype == "qTDS":
            #--- Set the qTDS for each machine and also the simtype
            self.set_qTDS()

    def run(self):

        # obs: I can run the simulation direct because the machines already have the type of simulation
        if self.simtype == "TDS":
            #--- Run Trace Driven Simulation
            print("============ Running Trace Driven Simulation ============")
            self.digital_model.run()
            print("=========================================================")

        if self.simtype == "qTDS":
            #--- Run Quasi Trace Driven Simulation
            print("============ Running quasi Trace Driven Simulation ============")
            self.digital_model.run()
            print("===============================================================")
    # =======================================================================



        
