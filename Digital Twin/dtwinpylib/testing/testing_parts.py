import simpy
import json 
import matplotlib.pyplot as plt

class Part():
    def __init__(self, id, type, location, creation_time, termination_time = None):
        self.id = id
        self.name = "Part " + str(self.id)
        self.type = type
        self.location = location
        self.creation_time = creation_time
        self.termination_time = termination_time
    
    #--- Get methods
    def get_name(self):
        return self.name
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
    def __init__(self, env, id, process_time, capacity, terminator, last_part_id=None, queue_in= None, queue_out= None, blocking_policy= "BBS", freq= None, cluster= None, final_machine = False):
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
        self.allocated_part = False
        self.new_part = False
        self.terminator = terminator

        self.counter_queue_in = 0
        self.counter_queue_out = 0
        self.waiting = 1
        self.last_part_id = last_part_id # variable assigned with datab from part_vector



    def run(self):
        

        while True:
            #xxx From Which Queue should I take a part? (plural) xxx
            

            if (self.allocated_part == True) or (self.allocated_part==False and self.new_part==False):
                
                for queue in self.queue_in: #MDSSSSSSSSS se nao tiver um yiel ele nao sai do processo!!!!
                    queue_empty = queue.get_len() == 0

                    if queue_empty:
                        self.new_part = False
                    
                    else:
                        try_to_get = queue.get() #Not necessary the yield
                        part = try_to_get.value
                        print(f'Time: {self.env.now} - {self.name} got {part.get_name()}')
                        self.new_part = True
                        break

                    
                    if self.counter_queue_in >= len(self.queue_in):
                        yield self.env.timeout(self.waiting)

                        self.counter_queue_in = 0
                        break

                    self.counter_queue_in +=1
            
            if self.new_part == True:

                #xxx For What Queue should I put this part? xxx
                for queue in self.queue_out:
                    self.allocated_part = False
                    if queue.get_len() >= queue.capacity: #queue  full
                        pass

                    else:
                        #--- blocking policy for Blocking Before Service (BBS)
                        if self.blocking_policy == 'BBS':
                            while queue.get_len()>=queue.capacity:
                                yield self.env.timeout(self.waiting)

                        #--- processing of the part depending on part type                    
                        yield self.env.timeout(self.process_time[part.get_type()])  # processing time stored in a dictionary
                        #yield self.env.timeout(5)

                        #--- blocking policy for Blocking After Service (BAS)
                        if self.blocking_policy == 'BAS':
                            while queue.get_len()>=queue.capacity:
                                yield self.env.timeout(self.waiting)


                        #------ Add the part in the next Queue ------
                        if self.final_machine == False:
                            #--- Put the part in the next queue as usual
                            queue.put(part)
                            self.allocated_part = True
                            print(f'Time: {self.env.now} - {self.name} put {part.get_name()} in {queue.name}')
                            break

                        if self.final_machine == True:
                            #--- Terminate
                            self.terminator.terminate_part(part)
                            
                            #--- Replace part
                            self.last_part_id += 1   
                            new_part_produced = Part(id= self.last_part_id, type= part.get_type(), location= 0, creation_time= self.env.now)
                            print(f'Time: {self.env.now} - {new_part_produced.name} replaced')
                            queue.put(new_part_produced)
                            self.allocated_part = True
                            break
                    
                    if self.counter_queue_out >= len(self.queue_out):
                        yield self.env.timeout(self.waiting)

                        self.counter_queue_out = 0
                        break
                    self.counter_queue_out += 1


    #--- Defining Gets and Setsv.t
    def get_queue_in(self):
        return self.queue_in
    def set_queue_in(self, value):
        self.queue_in = value

    def add_queue_in(self, value):
        if self.queue_in is None:
            self.queue_in = []
        self.queue_in.append(value)

    def add_queue_out(self, value):
        if self.queue_out is None:
            self.queue_out = []
        self.queue_out.append(value)

    def get_queue_out(self):
        return self.queue_out
    def set_queue_out(self, value):
        self.queue_out = value

    def get_process_time(self):
        return self.process_time
    def set_process_time(self, value):
        self.process_time = value

    def get_name(self):
        return self.name
    def get_capacity(self):
        return self.capacity
    def get_blocking_policy(self):
        return self.blocking_policy
    def get_final_machine(self):
        return self.final_machine
    def set_final_machine(self, value):
        self.final_machine = value

    #--- Define verbose
    def verbose(self):
        print("----------------")
        print(f"> {self.get_name()}")
        print(f"--Queue In:--")
        if self.get_queue_in() is None:
            print("None")
        else:
            for queue in self.get_queue_in():
                print(queue.get_name())
        print(f"--Queue Out:--")
        if self.get_queue_out() is None:
            print("None")
        else:
            for queue in self.get_queue_out():
                print(queue.get_name())
        """
        print(f"Capacity: {self.get_capacity()}")
        print(f"Blocking Policy: {self.get_blocking_policy()}")
        print(f"Final Machine? {self.get_final_machine()}")
        print("----------------")
        """
        


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
        for part in self.get_all_items():
            print(f"Parts stored: {part.get_name()}")
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
    def __init__(self, env=None, loop_type=None):
        self.loop_type = loop_type
        self.env = env
        self.store = simpy.Store(env) #Terminator with infinity capacity
    
    def terminate_part(self, part):
        part.set_termination(self.env.now) #set the termination time
        self.store.put(part)
        print(f'Time: {self.env.now} - xxx {part.name} terminated xxx')
    
    def get_all_items(self):
        return self.store.items

#--- Class Model
class Model():
    def __init__(self, name, env, model_path, initial= False, until= 20, part_type= "A", loop_type= "closed"):
        self.name = name
        self.model_path = model_path
        self.loop_type = loop_type
        self.env = env
        self.part_type = part_type
        self.until = until
        self.initial = initial
        self.last_part_id = 0

        #--- Vectors to store main components
        # Create an empty list to store Machine objects
        self.machines_vector = []
        # Create an empty list to store Queue objects
        self.queues_vector = []

        # Initial Part of the Model
        self.initial_parts = []

        self.terminator = Terminator(env= self.env, loop_type= "closed")


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
        
    def initial_allocation(self):
        with open(self.model_path) as json_file:
            # Load the json data
            data = json.load(json_file)

            #Create the initial parts
            part_id = 1
            for n_queues in range(len(data['initial'])):
                for n_parts in range(data['initial'][n_queues]):
                    self.initial_parts.append(Part(id= part_id, type= self.part_type, location=n_queues, creation_time=0))
                    part_id += 1

        generator_initial = Generator(env= self.env, loop_type="closed", part_vector= self.initial_parts, queue_vector= self.queues_vector)
        self.queues_vector = generator_initial.allocate_part()


    def model_translator(self):
        

        # Open the json file
        with open(self.model_path) as json_file:
            # Load the json data
            data = json.load(json_file)
            #--- Calculate the number of part initially in the model
            for i in range(len(data['initial'])):
                self.last_part_id += data['initial'][i]

            #--- Read Basic informationf from the model
            # Loop through the nodes in the json data
            for node in data['nodes']:
                # Create a new Machine object for each node and add it to the list
                self.machines_vector.append(Machine(env= self.env, id= node['activity'],freq= node['frequency'],capacity= node['capacity'], 
                process_time= {self.part_type: node['contemp']},cluster= node['cluster'], last_part_id = self.last_part_id, terminator= self.terminator))
            
            self.machines_vector[-1].set_final_machine(True)

            # Loop through the arcs in the json data
            queue_id = 0
            for arc in data['arcs']:
                queue_id += 1
                # Create a new Queue object for each arc and add it to the list
                self.queues_vector.append(Queue(env= self.env, id= queue_id, arc_links= arc['arc'],
                capacity= arc['capacity'],freq= arc['frequency'],transportation_time= arc['contemp']))


            #--- Allocate the Queues for each machine
            self.queue_allocation()

        if self.initial == True:
            #--- Allocate the initial Parts for each Queue
            self.initial_allocation()

    def run(self):
        #for machine in self.machines_vector:
        #   self.env.process(machine.run())
        
        self.env.process(self.machines_vector[0].run())
        self.env.process(self.machines_vector[1].run())
        self.env.run(until= self.until)
        print("Hello World")

    def analyze_results(self):
        parts_finished = self.terminator.get_all_items()
        parts_finished_time = []
        parts_finished_id = []
        for part in parts_finished:
            parts_finished_time.append(part.get_termination())
            parts_finished_id.append(part.get_id())
        
        plt.plot(parts_finished_id, parts_finished_time, '-o')
        plt.show()




    def get_model_components(self):
        return (self.machines_vector, self.queues_vector)

    def verbose(self):
        print(f"==========  Reading the Model: {self.name}  ==========")


        print(f"===> Big Picture")
        print(f"Total number of Machines: {len(self.machines_vector)}")
        print(f"Total number of Queues: {len(self.queues_vector)}")
        print()

        
        print("===>Detailed view of Queues:")
        for queue in self.queues_vector:
            queue.verbose()
        print()
        
        
        print("===>Detailed view of Machines:")
        for machine in self.machines_vector:
            machine.verbose()

environment = simpy.Environment()

model_2stations_closed_path = "models\model_2stations_closed.json"
model_2stations_closed = Model(name= "model_2stations_closed",model_path= model_2stations_closed_path, initial=True, env= environment, until= 200)
model_2stations_closed.model_translator()
#model_2stations_closed.verbose()
model_2stations_closed.run()
model_2stations_closed.analyze_results()