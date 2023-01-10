import simpy

class Machine:
    def __init__(self, env, name, queue_in, queue_out):
        self.env = env
        self.name = name
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.action = env.process(self.run())

    def run(self):
        while True:
            resource = yield self.queue_in.get()
            print(f'{self.name} got resource at {env.now}')
            yield env.timeout(5)  # processing time
            self.queue_out.put(resource)
            print(f'{self.name} put resource in {self.queue_out.name} at {env.now}')

class Queue:
    def __init__(self, env, name, capacity):
        self.env = env
        self.name = name
        self.store = simpy.Store(env, capacity=capacity)

    def put(self, resource):
        return self.store.put(resource)

    def get(self):
        return self.store.get()

        

env = simpy.Environment()

queue1 = Queue(env, 'Queue 1', capacity=float('inf'))
queue2 = Queue(env, 'Queue 2', capacity=float('inf'))

machine1 = Machine(env, 'Machine 1', queue1, queue2)
machine2 = Machine(env, 'Machine 2', queue2, queue1)

env.run(until=20)
