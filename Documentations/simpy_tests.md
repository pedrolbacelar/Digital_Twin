# Simpy Tests

## Description
SimPy is a Python library for performing discrete event simulations. It allows you to model real-world systems using Python objects and simulate their behavior over time.

SimPy is designed to be easy to use and flexible, making it a good choice for a wide range of simulation scenarios. It is particularly well-suited for simulations that involve processes, resources, and queues, such as those found in manufacturing, logistics, and computer systems.

Using SimPy, you can define and create objects that represent things like machines, devices, and people in your system, and then use these objects to model the interactions and behaviors of the system over time. You can then run your simulation and observe the results, which can help you understand the behavior of the system and make decisions about how to optimize it.

Some key features of SimPy include:

- Support for process-based simulations, where objects represent processes that execute over time and interact with other objects in the simulation
- Support for resource-based simulations, where objects represent resources that can be shared or used by processes in the simulation
- Support for queue-based simulations, where objects represent queues that hold or process items as they move through the system
- Support for generating random variables and statistical analysis of simulation results
- SimPy is a popular choice for discrete event simulation in Python and is widely used in academia and industry. It is open source and released under the MIT license.

The official documentation for SimPy is available online at:

https://simpy.readthedocs.io/

This documentation includes a user's guide, API reference, and a number of examples and tutorials that can help you get started with using SimPy for discrete event simulation.

In addition to the official documentation, there are also many other resources available online that can help you learn about and use SimPy, including blog posts, tutorials, and examples. Some good places to start include:

The SimPy website: https://simpy.readthedocs.io/
The SimPy GitHub page: https://github.com/simpy/simpy
The SimPy Google Group: https://groups.google.com/g/simpy-users

## Important topics

#### Timeout() and Yield
In the example you provided, the line yield env.timeout(2) causes the process to pause for 2 time units, which represents the processing time of the machine.

In SimPy, the env.timeout() method is used to pause the execution of a process for a specific amount of time. When a process calls env.timeout(), it yields a Simpy.Timeout object and waits until the specified time has elapsed.

Here is a more detailed explanation of how this works:

The process calls the env.timeout() method and passes in the number of time units to wait.
The env.timeout() method returns a Simpy.Timeout object.
The process yields the Simpy.Timeout object and waits until the specified time has elapsed.
When the specified time has elapsed, the generator yields a value and the process resumes execution.
In the example you provided, the yield env.timeout(2) line causes the process to pause for 2 time units, which represents the processing time of the machine.
In SimPy, the yield keyword is used to pause the execution of a process and return a value.

#### `simpy.Environment`
In SimPy, the simpy.Environment class represents the simulation environment. It is responsible for maintaining the current simulation time and scheduling events and processes.

The simpy.Environment class has several important methods and attributes that you can use to control and monitor the simulation:

- env.now: This attribute returns the current simulation time.
- env.run(until=None): This method runs the simulation until the specified time or until all scheduled events and processes have completed.
- env.process(process): This method schedules a process to run in the simulation.
- env.timeout(delay): This method returns a Simpy.Timeout object that can be used to pause a process for a specific amount of time.
- env.event(): This method creates a new Simpy.Event object that can be used to synchronize processes and schedule events.
To create a new simulation environment, you can call the simpy.Environment() constructor. For example:

```python
import simpy

env = simpy.Environment()
```

#### Schedule process in the simulation

When you schedule a process to run in a SimPy simulation, you are telling the simulation to execute the process at some point in the future. The simulation will then track the process and execute it when the time comes.

To schedule a process in a SimPy simulation, you can call the env.process() method and pass in the process as an argument. For example:
```python
import simpy

def process(env):
    print(f'Process starting at time {env.now}')
    yield env.timeout(1)
    print(f'Process ending at time {env.now}')

env = simpy.Environment()
env.process(process(env))
env.run()
```
In this example, the process() function is a SimPy process that prints a message and waits for 1 time unit. When you call env.process(process(env)), you are scheduling the process() function to run in the simulation. The simulation will then execute the process at the appropriate time.

When you call env.run(), the simulation will start running and execute the scheduled processes. In this example, the process() function will be executed and the messages will be printed to the console.

#### `simpy.resources`

In SimPy, the simpy.resources module provides classes for modeling resources and resource constraints in a simulation. These classes allow you to model resources that have a limited capacity and can be used by multiple processes or events at the same time.

Here is a list of the classes provided by the simpy.resources module:

- `simpy.resources.base.BaseResource`: This is the base class for all resource classes in SimPy. It provides the basic functionality for managing requests and releases of a resource.

- `simpy.resources.resource.Resource`: This class represents a resource with a fixed capacity. Processes or events can request and release the resource, and the resource will block requests when its capacity is reached.

- `simpy.resources.container.Container`: This class represents a resource that has a limited capacity and can store a certain amount of units. Processes or events can request and release units from the container, and the container will block requests when its capacity is reached.

- `simpy.resources.store.Store`: This class represents a resource that can store an unlimited number of items. Processes or events can put and get items from the store, and the store will block requests when it is empty or full, depending on the mode it is used in.

- `simpy.resources.store.FilterStore`: This class is similar to the simpy.resources.store.Store class, but it provides additional functionality for filtering items based on user-defined criteria.

You can use these classes to model resources and resource constraints in your SimPy simulation. For example, you could use the simpy.resources.Resource class to model a machine

In a SimPy simulation, a resource may not be available if it has reached its capacity or if it is being used by another process or event.

For example, consider a resource with a capacity of 1. If a process acquires the resource and then does not release it, the resource will not be available to other processes until it is released. Similarly, if multiple processes try to acquire the resource at the same time, only one of them will be able to acquire the resource, and the others will have to wait until the resource is released.

Here is an example of how a resource with a limited capacity can become unavailable in a SimPy simulation:

```python
import simpy

def process_a(env, resource):
    # Wait for the resource to be available
    with resource.request() as req:
        yield req
        print(f'Process A acquired the resource at time {env.now}')

        # Use the resource for a while
        yield env.timeout(5)
        print(f'Process A released the resource at time {env.now}')

def process_b(env, resource):
    # Wait for the resource to be available
    with resource.request() as req:
        yield req
        print(f'Process B acquired the resource at time {env.now}')

        # Use the resource for a while
        yield env.timeout(1)
        print(f'Process B released the resource at time {env.now}')

env = simpy.Environment()
resource = simpy.Resource(env, capacity=1)

# Start the process A and B
env.process(process_a(env, resource))
env.process(process_b(env, resource))

# Run the simulation
env.run()
```
In this example, the resource resource has a capacity of 1, which means that only one process can acquire it at a time. When you call env.run(), the simulation will start running and the processes will be executed in the order they were scheduled. Process A will acquire the resource first, and then Process B will have to wait until the resource is released by Process A.


#### `request()`
In SimPy, the request() method of a resource allows a process to request access to the resource. When a process calls queue.request(), it waits until the resource is available and then acquires the resource. The resource remains acquired until the process releases it or the process is interrupted.

The request() method returns a request object, which you can use with the yield keyword in a with statement to wait for the resource to become available. When the with block is entered, the process will wait until the resource is available, and then it will acquire the resource. When the with block is exited, the resource is automatically released.

Here is an example of how you can use the request() method to acquire and release a resource in a SimPy process:

```python
import simpy

def process(env, resource):
    # Wait for the resource to be available
    with resource.request() as req:
        yield req
        print(f'Process acquired the resource at time {env.now}')

        # Use the resource
        yield env.timeout(1)
        print(f'Process released the resource at time {env.now}')

env = simpy.Environment()
resource = simpy.Resource(env, capacity=1)

# Start the process
env.process(process(env, resource))

# Run the simulation
env.run()
```
In this example, the process() function is a SimPy process that acquires the resource resource, uses it for 1 time unit, and then releases it. The with statement and the request() method are used to acquire and release the resource as needed.
The yield keyword is used in a SimPy process to pause the process and allow other processes to run. When a process calls yield, it will pause until the next event in the simulation occurs, and then it will resume execution.

In the code you provided, the yield req statement is used to pause the process and wait for the resource to become available. When the process calls yield req, it will pause until the resource is available, and then it will acquire the resource and continue execution.

#### `simpy.Store`

The simpy.Store class provides the following methods:

- `simpy.Store.put(value)`: Adds a value to the store. This method returns a generator that can be used to pause the process until the value has been added to the store.
- `simpy.Store.get()`: Retrieves a value from the store. This method returns a generator that can be used to pause the process until a value is available in the store.
- `simpy.Store.items`: A list of the values currently in the store.
- `simpy.Store.capacity`: The maximum number of values that can be stored in the store.
 you can pass the capacity of the queue as an argument to the simpy.Store constructor to set the maximum number of items that can be stored in the queue.

For example, you can create a queue with a capacity of 2 items like this:
```python
queue = simpy.Store(env, capacity=2)
```
By default, the simpy.Store class has an infinite capacity, so you can store as many items as you like in the queue.
To access the list of items in a simpy.Store object, you can use the simpy.Store.items attribute.

For example, you can access the list of items in the queue object like this:

```python
items = queue.items
```
The simpy.Store.items attribute is a list that contains all of the items currently stored in the simpy.Store object. You can use the usual list operations to manipulate the items in the list, such as appending items, removing items, or iterating over the items.
Keep in mind that the simpy.Store.items attribute is a list, so any changes you make to the list will be reflected in the simpy.Store object. For example, if you remove an item from the list, it will also be removed from the simpy.Store object.

## Simulation Example

```python
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
```

**Output**
```
Added item 0 to the queue at time 0
[]
Machine processing item 0 at time 0
Added item 1 to the queue at time 1
[1]
Machine finished processing item 0 at time 2
Machine processing item 1 at time 2
Added item 2 to the queue at time 2
[2]
Added item 3 to the queue at time 3
[2, 3]
Machine finished processing item 1 at time 4
Machine processing item 2 at time 4
Added item 4 to the queue at time 4
[3, 4]
Machine finished processing item 2 at time 6
Machine processing item 3 at time 6
Machine finished processing item 3 at time 8
Machine processing item 4 at time 8
Machine finished processing item 4 at time 10
```

### Code explanaition

#### `machine()`
The machine() function is a SimPy process that represents a machine that processes items. The function takes four arguments:

- env: The SimPy environment in which the simulation is running.
- name: A string that specifies the name of the machine.
- queue: A simpy.Store object that represents the queue of items to be processed by the machine.
- terminator: An object that represents a terminator that stores the items that have been processed by the machine.

The machine() function has an infinite loop that retrieves the next item from the queue using the yield queue.get() statement, processes the item, and then adds the item to the terminator using the terminator.items.append(item) statement.

```python
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
```

#### `generate_items()`
The generate_items() function is a SimPy process that generates items and adds them to the queue. The function takes two arguments:

- env: The SimPy environment in which the simulation is running.
- queue: A simpy.Store object that represents the queue of items to be processed by the machine.

The generate_items() function has a loop that iterates 5 times and adds an item to the queue using the yield queue.put(i) statement. The function also waits for a random amount of time before adding the next item using the yield env.timeout(1) statement.

```python
def generate_items(env, queue):
    for i in range(5):
        # Add an item to the queue
        yield queue.put(i)
        print(f'Added item {i} to the queue at time {env.now}')
        print(queue.items)

        # Wait for a random amount of time before adding the next item
        yield env.timeout(1)
```
#### `Terminator`
The Terminator class is a simple class that has a single attribute, items, which is a list that stores the items that have been processed by the machine.
```python
class Terminator(object):
    def __init__(self):
        self.items = []
```

#### Running the simulation
To run the simulation, you need to do the following steps:

Create a SimPy environment using the simpy.Environment() function.
Create a simpy.Store object to represent the queue of items using the simpy.Store(env) constructor.
Create an instance of the Terminator class to represent the terminator.
Start the machine, item generator, and terminator processes using the env.process() function.
Run the simulation using the env.run() function.
Here is an example of how you can run the simulation with these steps:

```python
env = simpy.Environment()  # Create a SimPy environment
queue = simpy.Store(env)  # Create a queue using the simpy.Store class
terminator = Terminator()  # Create an instance of the Terminator class

# Start the machine, item generator, and terminator processes
env.process(machine(env, 'Machine', queue, terminator))
env.process(generate_items(env, queue))

env.run()  # Run the simulation
```






