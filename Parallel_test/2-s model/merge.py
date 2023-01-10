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
    def __init__(self, env, id, queue_in, queue_out, process_time, capacity, blocking_policy, final_machine = False):
        self.env = env
        self.name = 'machine_'+str(id)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.process_time = process_time
        self.capacity = capacity
        self.blocking_policy = blocking_policy
        self.final_machine = final_machine

    def run(self):
        while True:
            part = yield self.queue_in.get()
            print(f'{self.name} got part at {env.now}')

            #--- blocking policy for Blocking Before Service (BBS)
            if self.blocking_policy == 'BBS':
                while self.queue_out.get_len()>=self.queue_out.capacity:
                    yield

            #--- processing of the part depending on part type                    
            yield env.timeout(self.process_time[part.get_type()])  # processing time stored in a dictionary
            
            #--- blocking policy for Blocking After Service (BAS)
            if self.blocking_policy == 'BAS':
                while self.queue_out.get_len()>=self.queue_out.capacity:
                    yield


            #------ Add the part in the next Queue ------

            if self.final_machine == False:
                #--- Put the part in the next queue as usual
                self.queue_out.put(part)
                print(f'{self.name} put part in {self.queue_out.name} at {env.now}')

            if self.final_machine == True:
                #--- Terminate
                terminator = Terminator(env= env, loop_type= "closed", part = part)
                terminator.terminate_part()
                
               #--- Replace part
                new_part = Part(id= part.get_id() + 100, type= part.get_type(), location= 0, creation_time= env.now)
                print(f'{new_part.name} replaced at {env.now}')
                self.queue_out.put(new_part)



class Queue():
    def __init__(self, env, id, capacity):
        self.env = env
        self.id = id
        self.name = "Queue " + str(self.id)
        self.store = simpy.Store(env, capacity=capacity)
        self.capacity = capacity
        self.queue_strength = None   # add initial condition


    def put(self, resource):
        return self.store.put(resource)

    def get(self):
        return self.store.get()

    def get_all_items(self):
        return self.store.items

    def get_len(self):
        self.queue_strength = len(self.store.items)
        return self.queue_strength


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
        self.part.set_termination(env.now) #set the termination time
        self.store.put(self.part)
        print(f'xxx {self.part.name} terminated at {self.env.now} xxx')


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
process_time_1 = {'A':5, 'B':15}
process_time_2 = {'A':5, 'B':17}


machine1 = Machine(env=env, id=0, process_time=process_time_1, queue_in= queue_vector[0],blocking_policy="BAS", capacity= 1, queue_out= queue_vector[1])      
machine2 = Machine(env=env, id=1, process_time=process_time_2,  queue_in= queue_vector[1], blocking_policy= "BAS",  capacity= 1, queue_out= queue_vector[0], final_machine= True)      

env.process(machine1.run())
env.process(machine2.run())


env.run(until=20)
