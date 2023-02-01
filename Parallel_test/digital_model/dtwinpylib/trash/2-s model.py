import simpy

class Machine:
    def __init__(self, env, id, queue_in, queue_out, process_time, capacity, blocking_policy):
        self.env = env
        self.id = id
        self.name = 'machine_'+str(id)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.process_time = process_time
        self.capacity = capacity
        self.blocking_policy = blocking_policy
        
        

    def run(self):
        while True:
            resource = yield self.queue_in.get()

            print(f'{self.name} got resource at {self.env.now}')

            

            # blocking policy for Blocking Before Service (BBS)
            if self.blocking_policy == 'BBS':
                while self.queue_out.get_len()>=self.queue_out.capacity:
                    yield


            # processinf of the part depending on part type
                        
            yield env.timeout(self.process_time[resource.get_type()])  # processing time stored in a dictionary


            # blocking policy for Blocking After Service (BAS)
            if self.blocking_policy == 'BAS':
                while self.queue_out.get_len()>=self.queue_out.capacity:
                    yield
            self.queue_out.put(resource)
            print(f'{self.name} put resource in {self.queue_out.name} at {env.now}')

class Queue:
    def __init__(self, env, id, capacity, machine_in, machine_out):  # machine_in/out might be contradictory.
        self.env = env
        self.id = id
        self.name = 'queue_'+str(id)
        self.store = simpy.Store(env, capacity=capacity)
        self.capacity = capacity
        self.machine_in = machine_in
        self.machine_out = machine_out
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


class Part:
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
    def get_type(self):
        return self.type
    

env = simpy.Environment()

process_time_1 = {'type_A':5, 'type_B':15}
process_time_2 = {'type_A':8, 'type_B':17}

part1 = Part("Part1", "type_A")

queue1 = Queue(env, 1, float('inf'), 'machine_1', 'machine_2')
queue2 = Queue(env, 2, float('inf'), 'machine_2', 'machine_1')

machine1 = Machine(env,1, queue1, queue2, process_time_1, 1, 'BAS')
machine2 = Machine(env,2, queue2, queue1, process_time_2, 1, 'BAS')
# machine2 = Machine(env, 'Machine 2', queue2, queue1) #old

env.process(machine1.run())
env.process(machine2.run())

def generator(env, queue):
    while True:
        yield env.timeout(3)
        part = Part("Part {}".format(env.now), type="type_A")
        queue1.put(part)


env.process(generator(env, Queue))

env.run(until=200)

