import simpy

def check_queue_func(queue, check_queue):
    
    if len(queue) != 0: check_queue.succeed()

    return check_queue


def machine(env, queue_in, queue_out, process_time, ID):
    check_queue = env.event()
    while True:  
        if check_queue.triggered: check_queue = env.event()

        yield check_queue_func(queue_in, check_queue)

        print(f"[Machine {ID}]: There is something in my Queue_In")

        # some processing
        queue_in.pop()
        yield env.timeout(process_time)
        print(f"Time: {env.now} - [Machine {ID}] - Finished Process")
        queue_out.append(1)

        print(f"Queue In:  {queue_in}")
        print(f"Queue Out:  {queue_out}")
        print()


queue1 = []
queue2 = [1,1,1]

env = simpy.Environment()
env.process(machine(env, queue2, queue1, 5, 1))
env.process(machine(env, queue1, queue2, 1, 2))
env.run(until=40)