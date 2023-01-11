# Digital Model Documentation (0.0.1)

In this documment, a detailed description about the first documentation of the first developed Digital Model is created. This documentation discuss about which Class object in the model and also the tests cases created.
This documentation initally refers to this [commit](https://github.com/pedrolbacelar/Digital_Twin/commit/a56c648efb597f65fd4132dfa6b138c49ea77001). Besideds that, [here](https://github.com/pedrolbacelar/Digital_Twin/blob/main/Documentations/logbook/10-01-2023.md) you can find the notes from the logbook about the day that this version was created. 

## Objects Definition

The Class objects are defined in the following code:

```python
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



```
