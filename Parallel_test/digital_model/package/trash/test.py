import simpy
import json

class Part():
    def __init__(self, id, type, location, creation_time, termination_time = None):
        self.id = id
        self.name = "Part " + str(self.id)
        self.type = type
        self.location = location
        self.creation_time = creation_time
        self.termination_time = termination_time
    
    #--- Get methods
    def get_id(self):
        return self.id
    def get_type(self):
        return self.type
    def get_location(self):
        return self.location
    def get_creation(self):
        return self.creation_time
    def get_termination(self):
        return self.termination_time
    
    #--- Set Methdos
    def set_id(self, id):
        self.id = id
    def set_type(self, type):
        self.type = type
    def set_location(self, location):
        self.location = location
    def set_termination(self, termination_time):
        self.termination_time = termination_time

class Machine():
    def __init__(self, env, id, process_time, capacity, queue_in= [], queue_out= [], blocking_policy= "BBS", freq= None, cluster= None, final_machine = False):
        self.env = env
        self.name = 'Machine '+str(id)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.process_time = process_time
        self.capacity = capacity
        self.blocking_policy = blocking_policy
        self.final_machine = final_machine
        self.freq = freq
        self.cluster = cluster

    def run(self):
        while True:
            part = yield self.queue_in.get()
            print(f'{self.name} got part at {self.env.now}')

            #--- blocking policy for Blocking Before Service (BBS)
            if self.blocking_policy == 'BBS':
                while self.queue_out.get_len()>=self.queue_out.capacity:
                    yield

            #--- processing of the part depending on part type                    
            yield self.env.timeout(self.process_time[part.get_type()])  # processing time stored in a dictionary
            
            #--- blocking policy for Blocking After Service (BAS)
            if self.blocking_policy == 'BAS':
                while self.queue_out.get_len()>=self.queue_out.capacity:
                    yield


            #------ Add the part in the next Queue ------

            if self.final_machine == False:
                #--- Put the part in the next queue as usual
                self.queue_out.put(part)
                print(f'{self.name} put part in {self.queue_out.name} at {self.env.now}')

            if self.final_machine == True:
                #--- Terminate
                terminator = Terminator(env= self.env, loop_type= "closed", part = part)
                terminator.terminate_part()
                
               #--- Replace part
                global last_part_id # variable assigned with datab from part_vector
                last_part_id += 1   
                new_part = Part(id= last_part_id, type= part.get_type(), location= 0, creation_time= self.env.now)
                print(f'{new_part.name} replaced at {self.env.now}')
                self.queue_out.put(new_part)

    #--- Defining Gets and Sets
    def get_queue_in(self):
        return self.queue_in
    def add_queue_in(self, value):
        self.queue_in.append(value)
    def set_queue_in(self, value):
        self.queue_in = value

    def get_queue_out(self):
        return self.queue_out
    def add_queue_out(self, value):
        self.queue_out.append(value)
    def set_queue_out(self, value):
        self.queue_out = value

    def get_process_time(self):
        return self.process_time
    def set_process_time(self, value):
        self.process_time = value

    def get_final_machine(self):
        return self.final_machine
    def set_final_machine(self, value):
        self.final_machine = value

    def get_name(self):
        return self.name
    def get_capacity(self):
        return self.capacity
    def get_blocking_policy(self):
        return self.blocking_policy


    #--- Define verbose
    def verbose(self):
        print("----------------")
        print(self.get_name())
        print()
        print(f"--Queue In:--")
        for queue in self.get_queue_in():
            print(queue.get_name())
        print(f"--Queue Out:--")
        for queue in self.get_queue_out():
            print(queue.get_name())
        print()
        print(f"Capacity: {self.get_capacity()}")
        print(f"Blocking Policy: {self.get_blocking_policy()}")
        print(f"Final Machine? {self.get_final_machine()}")
        print("----------------")


class Queue():
    def __init__(self, env, id, capacity, arc_links, transportation_time= None, freq= None):
        self.env = env
        self.id = id
        self.name = "Queue " + str(self.id)
        self.store = simpy.Store(env, capacity=capacity)
        self.capacity = capacity
        self.queue_strength = None   # add initial condition
        self.transportation_time = transportation_time
        self.freq = freq
        self.arc_links = arc_links


    def put(self, resource):
        return self.store.put(resource)

    def get(self):
        return self.store.get()

    #--- Define Gets
    def get_all_items(self):
        return self.store.items
    def get_len(self):
        self.queue_strength = len(self.store.items)
        return self.queue_strength
    def get_arc_links(self):
        return self.arc_links

    def get_name(self):
        return self.name
    def get_capacity(self):
        return self.capacity
    
    #--- Define verbose
    def verbose(self):
        print("----------------")
        print(f"{self.get_name()}")
        print()
        print("--Intrinsic Properties--")
        print(f"Arc links: {self.get_arc_links()}")
        print(f"Capacity: {self.get_capacity()}")
        print()
        print("--Current Status--")
        print(f"Parts stored: {self.get_all_items()}")
        print(f"Queue Lenght: {self.get_len()}")
        print("----------------")

class Generator():
    def __init__(self, env = None,  loop_type = None, part_vector = None, queue_vector = None,):
        self.loop_type = loop_type
        self.part_vector = part_vector
        self.queue_vector = queue_vector
        self.env = env
    
    def allocate_part(self):
        for part in (self.part_vector):
            self.queue_vector[part.get_location()].put(part)
        
        return self.queue_vector

    def create_part(self, part_id = None, part_type= None, part_location= None):
        return Part(id= part_id, type= part_type, location= part_location, creation_time= self.env.now)

class Terminator():
    def __init__(self, env=None, loop_type=None, part=None):
        self.loop_type = loop_type
        self.part = part
        self.env = env
        self.store = simpy.Store(env) #Terminator with infinity capacity
    
    def terminate_part(self):
        self.part.set_termination(self.env.now) #set the termination time
        self.store.put(self.part)
        print(f'xxx {self.part.name} terminated at {self.env.now} xxx')




#--- Class Model
class Model():
    def __init__(self, name, env, model_path, part_type= "A", loop_type= "closed"):
        self.name = name
        self.model_path = model_path
        self.loop_type = loop_type
        self.env = env
        self.part_type = part_type

        #--- Vectors to store main components
        # Create an empty list to store Machine objects
        self.machines_vector = []
        # Create an empty list to store Queue objects
        self.queues_vector = []


    def queue_allocation(self):
        #Loop through each queue
        for queue in self.queues_vector:
            current_links = queue.get_arc_links()

            #Indentify the starting and ending point of the arc (minos 1 to match with python notation)
            arc_start = current_links[0] - 1
            arc_end = current_links[1] -1 

            #Arc start point (going out of the previous machine) -> Queue Out
            self.machines_vector[arc_start].add_queue_out(queue) #add current queue

            #Arc endind point (going in of the next machine) -> Queue In
            self.machines_vector[arc_end].add_queue_in(queue) #add current queue
        
   
    def model_translator(self):
        # Open the json file
        with open(self.model_path) as json_file:

            machines_vector = []
            # Create an empty list to store Queue objects
            queues_vector = []

            # Load the json data
            data = json.load(json_file)

            #--- Allocate the Queues for each machine
            #self.queue_allocation()
            queue_set = []
            for i in range(len(data['nodes'])):
                queue_set.append([[],[]])
            print("queue_set = ", queue_set)


            # Loop through the arcs in the json data
            queue_id = 0
            for arc in data['arcs']:
                # Create a new Queue object for each arc and add it to the list
                queues_vector.append(Queue(env= self.env, id= queue_id, arc_links= arc['arc'],
                capacity= arc['capacity'],freq= arc['frequency'],transportation_time= arc['contemp']))
                queue_id += 1

            for queue in queues_vector:
                current_links = queue.get_arc_links()

                #Indentify the starting and ending point of the arc (minos 1 to match with python notation)
                arc_start = current_links[0] - 1
                arc_end = current_links[1] -1 

                #Arc start point (going out of the previous machine) -> Queue Out
                queue_set[arc_start][1].append(queue) #add current queue

                #Arc endind point (going in of the next machine) -> Queue In
                queue_set[arc_end][0].append(queue) #add current queue
            
            
            #--- Read Basic informationf from the model
            # Loop through the nodes in the json data
            for node in data['nodes']:
                # Create a new Machine object for each node and add it to the list

                machines_vector.append(Machine(env= self.env, id= node['activity'] - 1,freq= node['frequency'],capacity= node['capacity'], 
                process_time= {self.part_type: node['contemp']},cluster= node['cluster'], queue_in= queue_set[node['activity'] - 1][0], queue_out=queue_set[node['activity'] - 1][1]))
            
            #--- Set final machine
            machines_vector[-1].set_final_machine(True)
            for queue in queues_vector:
                current_links = queue.get_arc_links()

                #Indentify the starting and ending point of the arc (minos 1 to match with python notation)
                arc_start = current_links[0] - 1
                arc_end = current_links[1] -1 

                machines_vector[arc_start].add_queue_out(queue)
                machines_vector[arc_end].add_queue_in(queue)

        return (machines_vector, queues_vector, queue_set)
     

    def get_model_components(self):
        return (self.machines_vector, self.queues_vector)

    def verbose(self):
        print(f"==========  Reading the Model: {self.name}  ==========")

        print()
        print(f"===> Big Picture")
        print(f"Total number of Machines: {len(self.machines_vector)}")
        print(f"Total number of Queues: {len(self.queues_vector)}")
        print()

        print()
        print("===>Detailed view of Queues:")
        for queue in self.queues_vector:
            queue.verbose()
        print()
        print("===>Detailed view of Machines:")
        for machine in self.machines_vector:
            machine.verbose()

environment = simpy.Environment()
model_3stations_open_path = "models\model_3stations_open.json"
model_3stations_open = Model(name= "model_3stations_open", env= environment, model_path= model_3stations_open_path)
(machines, queues, queue_set) = model_3stations_open.model_translator()

for machine in machines:
    machine.verbose()



