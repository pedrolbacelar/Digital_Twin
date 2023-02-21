class Zone():
    def __init__(self, machine, queue_list):
        self.name = "Zone of " + machine.get_name()
        self.machine = machine
        self.queue_list = queue_list
        #--- Counters for in and out number of parts
        self.inZone = 0
        self.outZone = 0
        self.Zone_initial = 0
        self.NumParts = 0

        #--- Initial Conditions
        # Multiple Queues
        if len(self.queue_list) > 1:
            ini_count = 0
            for queue in self.queue_list:
                ini_count += queue.get_len()
            self.Zone_initial = ini_count
        
        # Single Queue
        if len(self.queue_list) == 1:
            queue = self.queue_list[0]
            self.Zone_initial = queue.get_len()
    
    #--- A part entered the Zone
    def addIn(self):
        self.inZone += 1
    #--- A part leaves the Zone
    def addOut(self):
        self.outZone += 1
    def calculate_parts(self):
        #--- Calculate the number of parts in the machine considering the initial conditions and the delta changes
        self.NumParts = (self.Zone_initial + self.inZone - self.outZone) 
        return  self.NumParts
    
    def self_validation(self):
        self_counter = 0
        #--- Check the number of parts in the queues ins
        for queue in self.queue_list:
            self_counter += queue.get_len()

        #--- Check if the machine is working (zone is parts in the queues ins and + machine)
        if self.machine.get_working() == True:
            self_counter += 1
        
        print(f"[{self.name}] NumParts = {self_counter}")
    

    #--- Basic Sets and Gets
    def get_name(self):
        return self.name
    def get_queue_list(self):
        return self.queue_list
    def get_machine_is_final(self):
        return self.machine.get_final_machine()


class Synchronizer():
    def __init__(self, digital_model, real_database):
        #--- Basic Information
        self.digital_model = digital_model
        self.real_database = real_database
        self.full_trace = self.real_database.read_store_data_all("real_log")
        self.zones_dict = {}

        #--- Digital Model
        (self.machines_vector, self.queues_vector) = self.digital_model.get_model_components()
        
    def create_zones(self):
        for machine in self.machines_vector:
            #--- Basic information from the machine
            machine_name = machine.get_name()
            machine_queues_in_list = machine.get_queue_in()

            #--- create a temp Zone object
            new_zone = Zone(machine= machine, queue_list= machine_queues_in_list)

            #--- add the Zone object in the dictionary of zones
            self.zones_dict[machine_name] = new_zone
                
    def positioning_discovery(self):
        #--- Find the Positioning
        for event in self.full_database:
            #--- Extract the important informations
            (machine_name, status, queue_name) = (event[1], event[2], event[4]) 
            
            # We just care about the events with status "Finished",
            # because this in the only moment when we subtract some part from the current
            # zone and add it to the next zone

            if status == "Finished":
                # For the current zone a part was finished, so we increment the Out
                current_zone = self.zones_dict[machine_name]
                current_zone.addOut()

                #--- Discovery in which zone the part was putted based on the queues and machines
                for key in self.zones_dict:
                    #--- For every zone in the zone dictionary
                    zone = self.zones_dict[key]

                    #--- For every queue of a Zone
                    for queue in zone.get_queue_list():

                        #--- Found a zone if the selected next queue
                        if queue.get_name() == queue_name:
                            next_zone = zone
                        
                #--- For the next zone, increment the In since we're adding a part to that zone
                next_zone.addIn()

    def show(self):
        """
        #--- Running Self Validation
        print("=========== Self Validation ===========")
        for key in self.zones_dict:
            current_zone = self.zones_dict[key]
            zone_NumParts = current_zone.self_validation()
        print("=========================================")
        """

        #--- Print the Zones Occupation
        print("=========== Zones Occupations ===========")
        for key in self.zones_dict:
            current_zone = self.zones_dict[key]
            zone_NumParts = current_zone.calculate_parts()
            print(f"[{current_zone.get_name()}] NumParts = {zone_NumParts}")
        print("=========================================")
    
    def run(self):
        #--- Create the Zones for the Initial Conditions
        self.create_zones()

        #--- Find the Positioning for the parts
        self.positioning_discovery()

        #--- Show the results
        self.show()