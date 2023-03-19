# Assumptions

### info
Assumptions considered for the Digital twin components developed & integrated and its use cases.
Created on: 01/02/2023
Updated on: 19/03/2023

## Model generator

- the output file obtained from the model generator is a json dictionary.
- stations are mentioned as nodes and queues are mentioned as arcs.
- the maximum queue capacities available in the json file is accurate.
- the current number of parts in each queue is not available from model generation.
- the staion without a preedecessor is first staion and the station without a successor in the last station.
- processing time is mentioned as contemp in the json file.
- routing/transporting times are not available.

### Example for format of json dictionary file of 2s Model
```Python
{
    "nodes": [
        {
            "activity": 1,
            "predecessors": [
                5
            ],
            "successors": [
                2
            ],
            "frequency": 999,
            "capacity": 1,
            "contemp": 5,
            "cluster": 1
        },
        {
            "activity": 2,
            "predecessors": [
                1
            ],
            "successors": [
                3,
                4
            ],
            "frequency": 999,
            "capacity": 1,
            "contemp": 5,
            "cluster": 2
        }
    ],
    "arcs": [
        {
            "arc": [
                1,
                2
            ],
            "capacity": 10,
            "frequency": 1000,
            "contemp": 1
        },
        {
            "arc": [
                2,
                1
            ],
            "capacity": 10,
            "frequency": 1000,
            "contemp": 1
        }
    ],
    "initial":[
        1,
        0
    ]
}
```


## Model translator
  
- Model translator uses the json file from model generator as an input.
- All the arcs are considered as individual queues. This includes multiple arcs connecting to the same station.
- Following data has to be manually added:
  + Current number of parts in the queue during initiation
  + Routing/transportation time between stations
  + Number of parts in the system
  + Time length of simulation


## Use case

- It is a closed loop system with fixed number of pallets.
- The pallets are created by adding them directly to the first queue instantaneously (without interarrival time).
- Single part type
- Blocking conditions: Blocking After Service (BAS) based on the queue capacity of downstream buffer.
- Loading/Unloading times are already included in the processing time.
- The time delay between the communications of internal compenets of the digital twin are negligible.
- Throughput and system time are primary performance indicators.
- Failures are not considered for the simulation. It could be considered for synchronisation of Machine states.
  
  
## Branching and Path Simulation
  
- Branching machines don't have common output queues, each branching machines has a different output queue.
  So there is no case where branch 1 has as output conveyors [convey1, convey2] and other conveyor [convey1, convey3]












