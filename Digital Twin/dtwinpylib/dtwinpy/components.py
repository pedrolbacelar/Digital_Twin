import simpy


class Part():
    def __init__(self, id, type, location, creation_time, termination_time = None):
        self.id = id
        self.name = "Part " + str(self.id)
        self.type = type
        self.location = location
        self.creation_time = creation_time
        self.termination_time = termination_time
    
    #--- Get methods
    def get_name(self):
        return self.name
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
    def __init__(self, env, id, process_time, capacity, terminator, last_part_id=None, queue_in= None, queue_out= None, blocking_policy= "BBS", freq= None, cluster= None, final_machine = False):
        self.env = env
        self.name = 'Machine '+str(id)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.process_time = process_time
        self.capacity = capacity
        self.blocking_policy = blocking_policy
        self.final_machine = final_machine
        self.freq = freq
        self.cluster = cluster
        self.allocated_part = False
        self.new_part = False
        self.terminator = terminator

        self.counter_queue_in = 0
        self.counter_queue_out = 0
        self.waiting = 1
        self.last_part_id = last_part_id # variable assigned with datab from part_vector



    def run(self):
        while True:
            #xxx From Which Queue should I take a part? (plural) xxx
            

            if (self.allocated_part == True) or (self.allocated_part==False and self.new_part==False):
                
                for queue in self.queue_in: #MDSSSSSSSSS se nao tiver um yiel ele nao sai do processo!!!!
                    queue_empty = queue.get_len() == 0

                    if queue_empty:
                        self.new_part = False
                    
                    else:
                        try_to_get = queue.get() #Not necessary the yield
                        part = try_to_get.value
                        print(f'Time: {self.env.now} - [{self.name}] got {part.get_name()} from {queue.get_name()} (capacity= {queue.get_len()})')
                        
                        self.new_part = True
                        break

                    
                    if self.counter_queue_in >= len(self.queue_in):
                        yield self.env.timeout(self.waiting)
                        
                        #--- All the queues are empty (wait to get part from the next queue to have a part)
                        #part = yield self.queue_in[0].get()
                        #self.new_part = True

                        self.counter_queue_in = 0
                        break

                    self.counter_queue_in +=1
            
            if self.new_part == True:

                #xxx For What Queue should I put this part? xxx
                for queue in self.queue_out:
                    self.allocated_part = False
                    if queue.get_len() >= queue.capacity: #queue  full
                        pass

                    else:
                        #--- blocking policy for Blocking Before Service (BBS)
                        if self.blocking_policy == 'BBS':
                            while queue.get_len()>=queue.capacity:
                                print(f'Time: {self.env.now} - [{self.name}] Blocking... <===')
                                yield self.env.timeout(self.waiting)

                        #--- processing of the part depending on part type                    
                        yield self.env.timeout(self.process_time[part.get_type()])  # processing time stored in a dictionary
                        #yield self.env.timeout(5)

                        #--- blocking policy for Blocking After Service (BAS)
                        if self.blocking_policy == 'BAS':
                            while queue.get_len()>=queue.capacity:
                                print(f'Time: {self.env.now} - [{self.name}] Blocking... <===')
                                yield self.env.timeout(self.waiting)


                        #------ Add the part in the next Queue ------
                        if self.final_machine == False:
                            #--- Put the part in the next queue as usual
                            self.allocated_part = True
                            queue.put(part)
                            print(f'Time: {self.env.now} - [{self.name}] put {part.get_name()} in {queue.name} (capacity = {queue.get_len()})')
                            
                            break

                        if self.final_machine == True:
                            #--- Terminate
                            self.terminator.terminate_part(part)
                            print(f'Time: {self.env.now} - [Terminator] xxx {part.name} terminated xxx')
                            
                            
                            #--- Replace part
                            self.last_part_id += 1   
                            new_part_produced = Part(id= self.last_part_id, type= part.get_type(), location= 0, creation_time= self.env.now)
                            print(f'Time: {self.env.now} - [Terminator] {new_part_produced.name} replaced')
                            
                            queue.put(new_part_produced)
                            self.allocated_part = True
                            break
                    
                    if self.counter_queue_out >= len(self.queue_out):
                        yield self.env.timeout(self.waiting)

                        self.counter_queue_out = 0
                        break
                    self.counter_queue_out += 1


    #--- Defining Gets and Setsv.t
    def get_queue_in(self):
        return self.queue_in
    def set_queue_in(self, value):
        self.queue_in = value

    def add_queue_in(self, value):
        if self.queue_in is None:
            self.queue_in = []
        self.queue_in.append(value)

    def add_queue_out(self, value):
        if self.queue_out is None:
            self.queue_out = []
        self.queue_out.append(value)

    def get_queue_out(self):
        return self.queue_out
    def set_queue_out(self, value):
        self.queue_out = value

    def get_process_time(self):
        return self.process_time
    def set_process_time(self, value):
        self.process_time = value

    def get_name(self):
        return self.name
    def get_capacity(self):
        return self.capacity
    def get_blocking_policy(self):
        return self.blocking_policy
    def get_final_machine(self):
        return self.final_machine
    def set_final_machine(self, value):
        self.final_machine = value

    #--- Define verbose
    def verbose(self):
        print("----------------")
        print(f"> {self.get_name()}")
        print(f"--Queue In:--")
        if self.get_queue_in() is None:
            print("None")
        else:
            for queue in self.get_queue_in():
                print(queue.get_name())
        print(f"--Queue Out:--")
        if self.get_queue_out() is None:
            print("None")
        else:
            for queue in self.get_queue_out():
                print(queue.get_name())
        """
        print(f"Capacity: {self.get_capacity()}")
        print(f"Blocking Policy: {self.get_blocking_policy()}")
        print(f"Final Machine? {self.get_final_machine()}")
        print("----------------")
        """
        


class Queue():
    def __init__(self, env, id, capacity, arc_links, transportation_time= None, freq= None):
        self.env = env
        self.id = id
        self.name = "Queue " + str(self.id)
        self.store = simpy.Store(env, capacity=capacity)
        self.capacity = capacity
        self.queue_strength = None   # add initial condition
        self.transportation_time = transportation_time
        self.freq = freq
        self.arc_links = arc_links


    def put(self, resource):
        return self.store.put(resource)

    def get(self):
        return self.store.get()

    #--- Define Gets
    def get_all_items(self):
        return self.store.items
    def get_len(self):
        self.queue_strength = len(self.store.items)
        return self.queue_strength
    def get_arc_links(self):
        return self.arc_links

    def get_name(self):
        return self.name
    def get_capacity(self):
        return self.capacity
    
    #--- Define verbose
    def verbose(self):
        print("----------------")
        print(f"{self.get_name()}")
        print()
        print("--Intrinsic Properties--")
        print(f"Arc links: {self.get_arc_links()}")
        print(f"Capacity: {self.get_capacity()}")
        print()
        print("--Current Status--")
        for part in self.get_all_items():
            print(f"Parts stored: {part.get_name()}")
        print(f"Queue Lenght: {self.get_len()}")
        print("----------------")



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
    def __init__(self, env=None, loop_type=None):
        self.loop_type = loop_type
        self.env = env
        self.store = simpy.Store(env) #Terminator with infinity capacity
    
    def terminate_part(self, part):
        part.set_termination(self.env.now) #set the termination time
        self.store.put(part)
        
    
    def get_all_items(self):
        return self.store.items
