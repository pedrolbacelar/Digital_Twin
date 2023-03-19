# Assumptions

### info
Assumptions considered for the Digital twin components developed & integrated and its use cases.
Created on: 01/02/2023
Updated on: 19/03/2023

## Physical twin
- The physical system is a closed loop system with multiple machines.
- The number of pallets in the system is fixed.
- When a part completes a cycle, the pallet enters the system with a new part.
- Each machine has a facility to recognize which pallet it is processing (such as a RFID reader).
- Processing capacity of all the machines are 1.
- Queue capacity is an integer value.
- The physical system is capable of sending the traces of key events to the 'real log' in real time.
- The physical system is capable of recieving feedback from the digital twin and implementing it in the system.
- The 'Started' trace is send when the pusher allows a part from the queue to the station.
- The 'Finished' trace is send after unloading the part in the station.


## Model generator

- the output file obtained from the model generator is a json dictionary.
- stations are mentioned as nodes and queues are mentioned as arcs.
- the maximum queue capacities available in the json file are accurate.
- the current number of parts in each queue is not available from model generation.
- processing time is mentioned as contemp in the json file.
- routing/transporting times are not obtained from the model generation.
- cluster number of each machine are available in the json dictionary
- initial part positions in each queue is known from json dictionary.

### Example: format of json dictionary file of 2s Model

```Python
{
    "nodes": [
      {
        "activity": 1,
        "predecessors": [
          2
        ],
        "successors": [
          2
        ],
        "frequency": 999,
        "capacity": 1,
        "contemp": 12,
        "cluster": 1,
        "worked_time": 0
      },
      {
        "activity": 2,
        "predecessors": [
          1
        ],
        "successors": [
          1
        ],
        "frequency": 999,
        "capacity": 1,
        "contemp": 12,
        "cluster": 2,
        "worked_time": 0
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
        "contemp": 14
      },
      {
        "arc": [
          2,
          1
        ],
        "capacity": 10,
        "frequency": 1000,
        "contemp": 14
      }
    ],
    "initial": [
      [
        "Part 1",
        "Part 2"
      ],
      [],
      [],
      [],
      []
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
- Remaining cycle time for individual part, Throughput and system time are primary performance indicators.
- Failures are not considered for the simulation.











