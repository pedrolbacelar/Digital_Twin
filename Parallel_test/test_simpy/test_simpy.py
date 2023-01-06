import simpy

def machine(env, name, queue, terminator):
    while True:
        # Get the next item from the queue
        item = yield queue.get()

        # Process the item
        print(f'{name} processing item {item} at time {env.now}')
        yield env.timeout(2)
        print(f'{name} finished processing item {item} at time {env.now}')

        # Add the item to the terminator
        terminator.items.append(item)

def generate_items(env, queue):
    for i in range(5):
        # Add an item to the queue
        yield queue.put(i)
        print(f'Added item {i} to the queue at time {env.now}')
        print(queue.items)

        # Wait for a random amount of time before adding the next item
        yield env.timeout(1)

class Terminator(object):
    def __init__(self):
        self.items = []

env = simpy.Environment()
queue = simpy.Store(env, capacity=2)  # Create a queue with a capacity of 2 using the simpy.Store class
terminator = Terminator()

# Start the machine, item generator, and terminator processes
env.process(machine(env, 'Machine', queue, terminator))
env.process(generate_items(env, queue))

# Run the simulation
env.run()
