import simpy

def machine(env, process_time, parts, done):
    while True:
        part = yield parts.get()
        if done.triggered():
            break
        yield env.timeout(process_time)
        parts.put(part)

def main(env, num_machines, process_time, num_parts):
    parts = simpy.Store(env, capacity=num_parts)
    done = env.event()
    for i in range(num_machines):
        env.process(machine(env, process_time, parts, done))
        
    for i in range(num_parts):
        parts.put(i)
        
    while len(parts.items) < num_parts:
        yield env.timeout(1)
    done.succeed()

env = simpy.Environment()
env.process(main(env, 2, 10, 8))
env.run()
