import simpy

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
    def __init__(self, env, name, queue_in, queue_out, final_machine = False):
        self.env = env
        self.name = name
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.final_machine = final_machine

    def run(self):
        while True:
            if self.final_machine == False:
                resource = yield self.queue_in.get()
                print(f'{self.name} got resource at {env.now}')
                yield env.timeout(5)  # processing time
                self.queue_out.put(resource)
                print(f'{self.name} put resource in {self.queue_out.name} at {env.now}')

            if self.final_machine == True:
                resource = yield self.queue_in.get()
                print(f'{self.name} got resource at {env.now}')
                yield env.timeout(5)  # processing time

                terminator = Terminator(env= env, loop_type= "closed", resource = resource)
                terminator.terminate_part()
                
               
                new_part = Part(id= resource.get_id() + 1, type= resource.get_type(), location= 0, creation_time= env.now)
                print(f'{new_part.name} replaced at {env.now}')
                self.queue_out.put(new_part)



class Queue():
    def __init__(self, env, id, capacity):
        self.env = env
        self.id = id
        self.name = "Queue " + str(self.id)
        self.store = simpy.Store(env, capacity=capacity)

    def put(self, resource):
        return self.store.put(resource)

    def get(self):
        return self.store.get()

    def get_all_items(self):
        return self.store.items


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
    def __init__(self, env=None, loop_type=None, resource=None):
        self.loop_type = loop_type
        self.resource = resource
        self.env = env
        self.store = simpy.Store(env) #Terminator with infinity capacity
    
    def terminate_part(self):
        self.resource.set_termination(self.env.now) #set the termination time
        self.store.put(self.resource)
        print(f'{self.resource.name} terminated at {self.env.now}')


#========================================================================    

#--- Initial Part Generation (Maybe automated in the future)
part_vector = [Part(id= 0,type= "A", location= 0, creation_time= 0),
            Part(id= 1,type= "A", location= 0, creation_time= 0),
            Part(id= 2,type= "A", location= 2, creation_time= 0),
            Part(id= 3,type= "A", location= 3, creation_time= 0),
            Part(id= 4,type= "A", location= 3, creation_time= 0),
            Part(id= 5,type= "A", location= 3, creation_time= 0)]

#--- Queue Creation (should come from the Translator)
env = simpy.Environment()


queue_vector = [Queue(env = env, id= 0, capacity= 5),
            Queue(env = env, id= 1, capacity= 5),
            Queue(env = env, id= 2, capacity= 5),
            Queue(env = env, id= 3, capacity= 5),
            Queue(env = env, id= 4, capacity= 5)]

#--- Initialize Generator
generator_initial = Generator(env= env, loop_type="closed", part_vector= part_vector, queue_vector= queue_vector)
queue_vector = generator_initial.allocate_part()

#-- Show the parts allocated for each queue
for queue in queue_vector:
    print(queue.name + ": ", queue.get_all_items())

#================== Simple Model ==================
machine1 = Machine(env=env, name= "Machine 1", queue_in= queue_vector[0], queue_out= queue_vector[1])      
machine2 = Machine(env=env, name= "Machine 2", queue_in= queue_vector[1], queue_out= queue_vector[0], final_machine= True)      

env.process(machine1.run())
env.process(machine2.run())


env.run(until=20)
