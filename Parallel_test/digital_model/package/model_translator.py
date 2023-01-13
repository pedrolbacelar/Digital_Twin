import simpy
import json
import matplotlib.pyplot as plt

#--- Import simulation components
from .components import Part
from .components import Machine
from .components import Queue
from .components import Generator
from .components import Terminator

#--- Reload Package

import importlib
import package
importlib.reload(package.components) #reload this specifc module to upadte the class






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
            if self.initial == True:
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

        for machine in self.machines_vector:
            self.env.process(machine.run())
            
        self.env.run(until= self.until)
        print("### Simulation Done ###")

    def analyze_results(self):
        parts_finished = self.terminator.get_all_items()
        parts_finished_time = []
        parts_finished_id = []
        for part in parts_finished:
            parts_finished_time.append(part.get_termination())
            parts_finished_id.append(part.get_id())
        
        plt.plot(parts_finished_id, parts_finished_time, '-o')
        plt.show()
        plt.savefig(f"figures/{self.name}.png")




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




