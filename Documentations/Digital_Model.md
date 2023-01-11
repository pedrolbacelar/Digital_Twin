# Digital Model Documentation (0.0.1)

In this documment, a detailed description about the first documentation of the first developed Digital Model is created. This documentation discuss about which Class object in the model and also the tests cases created.
This documentation initally refers to this [commit](https://github.com/pedrolbacelar/Digital_Twin/commit/a56c648efb597f65fd4132dfa6b138c49ea77001). Besideds that, [here](https://github.com/pedrolbacelar/Digital_Twin/blob/main/Documentations/logbook/10-01-2023.md) you can find the notes from the logbook about the day that this version was created. 

## Source Code

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

```

## Overall Idea

The above code defines a simulation of a production line consisting of a number of machines and queues. The simulation uses the simpy library, which is a discrete event simulation library in Python.

The `Part class` is defined with an `id, type, location, creation_time, and termination_time attribute`, as well as a set of "get" and "set" methods for each attribute.

The `Machine class` is defined with an `env, id, queue_in, queue_out, process_time, capacity, blocking_policy, and final_machine attribute`. The `run` method on the Machine class is where the core simulation logic resides. The machine continually gets parts from its input queue, processes them based on their type attribute, and then either puts the part into the next queue, or terminates the part if it's the final machine.

The `Queue class` represents a single queue in the simulation, with a `simpy.Store` object to store parts, a capacity attribute, and a queue_strength attribute. The class has methods for adding and removing parts from the queue, as well as methods for getting the current items in the queue and the current queue strength.

The `Generator class` creates new parts and places them in the specified initial queue. The `Terminator class` marks parts as terminated when they leave the final machine.

The code then creates the necessary objects and runs the simulation by calling the run method of the machines.


## Components (Classes)

### `Class Part()`

**The Part is the work-pieces of the system.**
The Part class represents a single part in the simulation. It is defined with the following attributes:

- id: a unique identifier for the part.
- name: the name of the part, which is "Part " followed by the id.
- type: the type of the part.
- location: the location of the part.
- creation_time: the time at which the part was created.
- termination_time: the time at which the part was terminated.

It has also five methods for each of the attributes to access their value:

- get_id(): returns the id of the part.
- get_type(): returns the type of the part.
- get_location(): returns the location of the part.
- get_creation(): returns the creation time of the part.
- get_termination(): returns the termination time of the part.

And also it has 4 methods to set the value of each attribute:

- set_id(): sets the id of the part.
- set_type(): sets the type of the part.
- set_location(): sets the location of the part.
- set_termination(): sets the termination time of the part.

This class is used to store information about the parts that move through the simulation and to provide an interface for other parts of the simulation to interact with them (i.e get or set attributes values)

### `Class Machine()`

The Machine class represents a single machine in the simulation. It is defined with the following attributes:

- env: the environment object provided by the simpy library, which controls the flow of time in the simulation.
- name: the name of the machine, which is "machine_" followed by the id.
- queue_in: the queue from which the machine gets parts to process.
- queue_out: the queue to which the machine puts parts after processing.
- process_time: the time it takes to process a part, stored as a dictionary with the keys as the part types, and values as the time it takes to process a part of that type.
- capacity: the maximum number of parts the machine can process at once.
- blocking_policy: a string indicating the machine's blocking policy, either "BBS" for blocking before service, or "BAS" for blocking after service.
- final_machine: a boolean indicating whether the machine is the final machine in the simulation.

It has a method run() which is where the core simulation logic resides. The machine continually gets parts from its input queue, processes them based on their type attribute and the process_time attribute, and then either puts the part into the next queue, or terminates the part if it's the final machine, depending on the final_machine attribute.

It also uses the blocking policy attribute. If the attribute is set to "BBS", the machine waits if the next queue is full before starting to process the part. If the attribute is set to "BAS", the machine waits after processing the part if the next queue is full before putting the processed part in the queue.

A final machine is the last machine in the production line, this condition is indicated by the final_machine attribute of the Machine class. If the final_machine attribute is set to True this indicates that the machine is the final machine in the simulation.

If the machine is a final machine, the run method of the Machine class has special behavior for when it finishes processing a part. Instead of putting the part in the next queue, the part is instead "terminated", which means that it is removed from the simulation and is no longer tracked. The `Terminator` class is used to mark parts as terminated when they leave the final machine. Additionally, a new part is created and placed in the final queue, this new part has an id 100 greater than the original part and is created at the current simulation time. This new part will be used in the next cycle of the simulation, this is done by calling the Part class constructor.

This class is used to simulate the behavior of a machine on the production line, and how it interacts with the parts and queues in the simulation.

### `Class Queeu()`

The Queue class represents a single queue in the simulation. It is defined with the following attributes:

- env: the environment object provided by the simpy library, which controls the flow of time in the simulation.
- id: a unique identifier for the queue.
- name: the name of the queue, which is "Queue " followed by the id.
- store: the simpy.Store object provided by the simpy library, which is used to store parts in the queue.
- capacity: the maximum number of parts that can be stored in the queue.
- queue_strength: the current number of parts in the queue.

It has methods for adding and removing parts from the queue. `put(resource)` which places a part in the queue. `get()` which retrieves a part from the queue. It also has methods for getting the current items in the queue `get_all_items()` and the current queue strength `get_len()`

This class is used to simulate a queue in the production line, and it keeps track of the parts that are waiting to be processed by a machine, as well as the number of parts currently in the queue.


### `Class Generator()`
The Generator class is responsible for creating new parts and placing them in the specified initial queues at the beginning of the simulation. It is defined with the following attributes:

- env: the environment object provided by the simpy library, which controls the flow of time in the simulation.
- loop_type: a string that indicates whether the generator runs indefinitely ("open" loop) or stops after a certain number of iterations ("closed" loop). - However, this version of the class does not use the loop_type attribute.
- part_vector: a list of tuples containing information about the different types of parts that the generator can create, including their id, type, and location.
- queue_vector: a list of queues to which the parts should be added.

It has two methods.

- `allocate_part():` that method places the parts specified in the part_vector attribute in the corresponding queue specified by the location attribute of each part in the queue_vector attribute.
- `create_part():` This method creates a new Part object using the Part class constructor and sets the attributes of the part using the arguments passed to the method part_id, part_type, and part_location. This method also sets the creation_time attribute of the part to the current time of the simulation.

This class is used to simulate the creation of new parts at the beginning of the simulation, set their initial properties and add them to the corresponding initial queue.


### `Class Terminator()`

The Terminator class is responsible for marking parts as "terminated" when they leave the final machine. A part is considered "terminated" when it is removed from the simulation and is no longer tracked.

It is defined with the following attributes:

- env: the environment object provided by the simpy library, which controls the flow of time in the simulation.
- loop_type: a string that indicates whether the generator runs indefinitely ("open" loop) or stops after a certain number of iterations ("closed" loop).
- part: the part that is being terminated.

It has a method `terminate_part()` which marks the part as terminated and logs it to the console with a message indicating that the part has been terminated at the current time of the simulation.

This class is used to simulate the termination of a part at the end of the production process, it is used in conjunction with the Machine class to stop tracking a part after it has completed the production process.

## Simulation Testing

First we start creating the Queues and the Parts:

```python
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
```

This is a section of code that initializes the parts and queues for the simulation.

The part_vector list is created with six elements, which are instances of the Part class. Each element has a unique id, the same type "A", different location attribute, and a creation time of 0, meaning all parts were created at the start of the simulation.

queue_vector list is created with five elements, which are instances of the Queue class. Each element has a unique id and capacity of 5, meaning each queue can hold a maximum of 5 parts.

generator_initial is an instance of the Generator class, it is passed the environment object env, the loop_type is set to "closed" but is not used in this version of the code, the part_vector and queue_vector are passed as arguments. The generator_initial.allocate_part() method is used to place the parts into the specified queues, it returns the queue_vector.

The for loop iterates through the queue_vector and prints the queue name and the parts that are currently in that queue. The queue.get_all_items() method is used to get the parts in the queue.

After this we start the setup of the simulation and run the simulation:

```python
#================== Simple Model ==================
process_time_1 = {'A':5, 'B':15}
process_time_2 = {'A':5, 'B':17}


machine1 = Machine(env=env, id=0, process_time=process_time_1, queue_in= queue_vector[0],blocking_policy="BAS", capacity= 1, queue_out= queue_vector[1])      
machine2 = Machine(env=env, id=1, process_time=process_time_2,  queue_in= queue_vector[1], blocking_policy= "BAS",  capacity= 1, queue_out= queue_vector[0], final_machine= True)      

env.process(machine1.run())
env.process(machine2.run())


env.run(until=20)
```


This is a section of code that defines the machines and sets up the production process.

process_time_1 and process_time_2 are dictionaries which contain the processing time for different types of parts. process_time_1 has a processing time of 5 for type A parts and 15 for type B parts. process_time_2 has a processing time of 5 for type A parts and 17 for type B parts.

machine1 and machine2 are instances of the Machine class.

machine1 is defined with env, id =0, process_time=process_time_1, queue_in= queue_vector[0], blocking_policy="BAS", capacity= 1, queue_out= queue_vector[1]
machine2 is defined with env, id =1, process_time=process_time_2, queue_in= queue_vector[1], blocking_policy="BAS", capacity= 1, queue_out= queue_vector[0], final_machine= True
The final_machine attribute on machine2 is set to True, which means that the part that will be processed by the machine2 will be considered to be terminated and removed from the simulation.

The `env.process()` function is used to schedule the execution of the run() method of the machine.


















