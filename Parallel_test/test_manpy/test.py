import manpy

# Create a simulation object
sim = manpy.Simulation()

# Create a queue object
queue = manpy.Queue("Queue", sim)

# Create a server object
server = manpy.Server("Server", sim)

# Create a generator object to generate customers
generator = manpy.Generator("Generator", sim)

# Connect the generator to the queue
manpy.Source(generator, queue)

# Connect the queue to the server
manpy.Sink(queue, server)

# Set the arrival rate of the generator
generator.interarrival_time = manpy.TimeDist("Exp", 1.0)

# Set the service time of the server
server.service_time = manpy.TimeDist("Exp", 2.0)

# Run the simulation for 1000 time units
sim.simulate(until=1000)

# Print the results
print("Number of customers served:", server.number_of_completions)