# import simpy

# # Define a Process class for the machines
# class Machine(simpy.Process):
#     def __init__(self, env, name, processing_time):
#         super().__init__(env)
#         self.name = name
#         self.processing_time = processing_time
        
#     def run(self):
#         while True:
#             # Wait for a part to be available
#             part = yield env.process(input_buffer.get())
            
#             # Process the part
#             print(f"{self.name} is processing part {part}")
#             yield env.timeout(self.processing_time)
            
#             # Send the processed part to the output buffer
#             yield env.process(output_buffer.put(part))
            
# # Define a Process class for the buffers
# class Buffer(simpy.Process):
#     def __init__(self, env, capacity):
#         super().__init__(env, generator=self.run)  # Pass the run method as the generator argument
#         self.capacity = capacity
#         self.buffer = simpy.Store(env, capacity=capacity)
        
#     def run(self):
#         while True:
#             # Wait for a request to put or get a part from the buffer
#             request = yield self.buffer.get()
#             if request[0] == "put":
#                 # Put the part in the buffer
#                 yield self.buffer.put(request[1])
#             elif request[0] == "get":
#                 # Get a part from the buffer
#                 part = yield self.buffer.get()
#                 request[1].succeed(part)
        
#     def put(self, part):
#         # Send a request to put a part in the buffer
#         return self.buffer.put(("put", part))
        
#     def get(self):
#         # Send a request to get a part from the buffer
#         get_request = self.env.event()
#         self.buffer.put(("get", get_request))
#         return get_request

# # Create an environment and the input and output buffers
# env = simpy.Environment()
# input_buffer = Buffer(env, capacity=10)
# output_buffer = Buffer(env, capacity=10)

# # Create the machines
# machine1 = Machine(env, "Machine 1", processing_time=5)
# machine2 = Machine(env, "Machine 2", processing_time=10)

# # Start the processes
# env.process(input_buffer.put("Part 1"))
# env.process(machine1)
# env.process(machine2)

# # Run the simulation
# env.run()

###############################

import simpy

# Define a Process class for the machines
class Machine(simpy.Process):
    def __init__(self, env, name, processing_time):
        super().__init__(env)
        self.name = name
        self.processing_time = processing_time
        
    def run(self):
        while True:
            # Wait for a part to be available
            part = yield env.process(input_buffer.get())
            
            # Process the part
            print(f"{self.name} is processing part {part}")
            yield env.timeout(self.processing_time)
            
            # Send the processed part to the output buffer
            yield env.process(output_buffer.put(part))
            
# Define a Process class for the buffers
class Buffer(simpy.Process):
    def __init__(self, env, capacity):
        super().__init__(env, generator=self.run)  # Pass the run method as the generator argument
        self.capacity = capacity
        self.buffer = simpy.Store(env, capacity=capacity)
        
    def run(self):
        while True:
            # Wait for a request to put or get a part from the buffer
            request = yield self.buffer.get()
            if request[0] == "put":
                # Put the part in the buffer
                yield self.buffer.put(request[1])
            elif request[0] == "get":
                # Get a part from the buffer
                part = yield self.buffer.get()
                request[1].succeed(part)
        
    def put(self, part):
        # Send a request to put a part in the buffer
        return self.buffer.put(("put", part))
        
    def get(self):
        # Send a request to get a part from the buffer
        get_request = self.env.event()
        self.buffer.put(("get", get_request))
        return get_request

# Create an environment and the input and output buffers
env = simpy.Environment()
input_buffer = Buffer(env, capacity=10)
output_buffer = Buffer(env, capacity=10)

# Create the machines
machine1 = Machine(env, "Machine 1", processing_time=5)
machine2 = Machine(env, "Machine 2", processing_time=10)

# Start the processes
env.process(input_buffer.put("Part 1"))
env.process(machine1)
env.process(machine2)

# Define a Process class to represent the flow of parts between the machines, buffers, and other parts of the system
class Flow(simpy.Process):
    def __init__(self, env):
        super().__init__(env)
        
    def run(self):
        while True:
            # Wait for a processed part to be available
            part = yield env.process(output_buffer.get())
            
            # Process the part
            print(f"Flow is processing part {part}")
            yield env.timeout(1)
            
# Start the flow process
env.process(Flow(env))

# Run the simulation
env.run(until=20)
