#========================================================================    

#--- Initial Part Generation (Maybe automated in the future)
part_vector = [Part(id= 0,type= "A", location= 0, creation_time= 0),
            Part(id= 1,type= "A", location= 0, creation_time= 0),
]

last_part_id = 2 # id used by the last part created # initialised here based on data from part_vector
print("-------Simulation initiated with ", last_part_id, " parts in the queues-------")
#--- Queue Creation (should come from the Translator)
env = simpy.Environment()


queue_vector = [Queue(env = env, id= 0, capacity= 5),
            Queue(env = env, id= 1, capacity= 5),]

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
print("------- End of simulation -------")
print("The last part created is part id: ",last_part_id)