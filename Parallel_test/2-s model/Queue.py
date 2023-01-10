import simpy

class Queue():
    def __init__(self, env, name, capacity, ):
        self.env = env
        self.name = name
        self.store = simpy.Store(env, capacity=capacity)

    def put(self, resource):
        return self.store.put(resource)

    def get(self):
        return self.store.get()

    def show_items(self):
        return self.store.items

class Generator():
    def __init__(self, name, queue_id_vector, queue_item_vector):
        self.name = name
        self.queue_id_vector = queue_id_vector
        self.queue_item_vector = queue_item_vector

        print(f'{self.name} created at {env.now}')

    def generate(self):
        for queue_id in range(len(self.queue_id_vector)):
            self.queue_id_vector[queue_id].put(self.queue_item_vector[queue_id])

    def get_updated_queues(self):
        return self.queue_id_vector




#--- 
env = simpy.Environment()
queue1 = Queue(env, 'Queue 1', capacity=1)
queue2 = Queue(env, 'Queue 2', capacity=2)
queue3 = Queue(env, 'Queue 3', capacity=3)

queue_vector = [queue1, queue2, queue3]
queue_initial_conditions = [2,0,1]




print(queue1.show_items())
