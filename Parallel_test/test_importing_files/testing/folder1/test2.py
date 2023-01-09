import manpy
# Create the simulation
sim = manpy.Simulation()

# Set the simulation parameters
sim.max_time = 1000
sim.seed = 123

# Create the machines
machine1 = manpy.Machine("Machine 1")
machine2 = manpy.Machine("Machine 2")

# Create the buffers
buffer1 = manpy.Buffer("Buffer 1", capacity=10)
buffer2 = manpy.Buffer("Buffer 2", capacity=10)

# Create the sources and sinks
source = manpy.Source("Source", output_flow=buffer1)
sink = manpy.Sink("Sink", input_flow=buffer2)

# Connect the elements of the model
machine1.input_flow = buffer1
machine1.output_flow = buffer2
machine2.input_flow = buffer2
machine2.output_flow = sink

# Run the simulation
sim.start_all()

# Analyze the results
print(f"Total number of entities: {sink.number_of_entities}")
print(f"Utilization of Machine 1: {machine1.utilization:.2f}")
print(f"Utilization of Machine 2: {machine2.utilization:.2f}")
