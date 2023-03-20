# Experimental setup

## Test 1

### Objective
- To test the functioning of RCT_server.
- To verify if the path selected by the RCT_server for a specifi part_id is optimal by comparing it with actual system.
- To verify capability of real system to change dispatch policy for a specific part.

### Experimental Setup
- Model: 5s model
- Number of pallets: 7
- Default policy of branch: alternating policy with station 2 as initial station.
- Digital twin definition:
  ```python
  mydt = Digital_Twin(name= "5s_determ", template= True, Freq_Sync= 30, Freq_Valid= 60, Freq_Service= 10000, delta_t_treshold=21)
  ```
- Initial condition:
  - 7 parts in Queue 1.
  - No parts in the rest of the queues.
  - No parts inside the machines.

### Results
- Did RCT_server provide the expected service (Y/N):
- Did physical system change the part policy for the partID accurately (Y/N):
- Part ID selected:
- RCT calculated by the digital twin for both paths:
- Selected path:
- Actual time took for the part to finish the cycle in physical system:

### Observation
- The test was run on 5s Model.


## Test 2
### Objective
- Run 5s model with minimal number of pallets and calculate the RCT for couple of parts in a specific station manually and compare with digital calculation

### Experimental Setup
- Model: 5s model
- Number of pallets: 4
- selected station for calculation: station 1
- Default policy of branch: alternating policy with station 2 as initial station.
- Digital twin definition:
  ```python
  mydt = Digital_Twin(name= "5s_determ", template= True, Freq_Sync= 30, Freq_Valid= 60, Freq_Service= 10000, delta_t_treshold=21)
  ```
- Initial condition:
  - 4 parts in Queue 1.
  - No parts in the rest of the queues.
  - No parts inside the machines.

### Results
- Did RCT_server apply its service for targeted parts (Y/N):
- number of targeted parts:
- RCT of each targeted part {part id, simulated RCT, manual RCT}:
    1. {part id : , simulated RCT : , manual RCT : }
    2. {part id : , simulated RCT : , manual RCT : }
    3. ...

### Observation
- The test was run on 5s Model.

## Test 3
### Objective
- Compare the evolution of the RCT of a specific part in the simulation (for cluster C1, C2, C3, C4, C5 for a specific part).

### Experimental Setup
- Model: 5s model
- Number of pallets: 7
- Default policy of branch: alternating policy with station 2 as initial station.
- Digital twin definition:
  ```python
  mydt = Digital_Twin(name= "5s_determ", template= True, Freq_Sync= 30, Freq_Valid= 60, Freq_Service= 10000, delta_t_treshold=21)
  ```
- Initial condition:
  - 7 parts in Queue 1.
  - No parts in the rest of the queues.
  - No parts inside the machines.

### Results
- Did RCT_server apply its service for targeted parts (Y/N):
- Targeted part ID:
- RCT of each cluster for the targeted part {part id, simulated RCT, manual RCT}:
    1. Cluster 1:
    2. Cluster 2:
    3. Cluster 3:
    4. Cluster 4:

### Observation
- The test was run on 5s Model.


## Test 4
### Objective
- Compare the performance of the system before and after adopting the automatically RCT service. (compare throughput of system with and without RCT).
- Repeat the test thrice to check if the reults are reliable.

### Experimental Setup 1
- Model: 5s model
- RCT service: On
- Test run time: 10 minutes
- Number of pallets: 9
- Default policy of branch: alternating policy with station 2 as initial station.
- Digital twin definition:
  ```python
  mydt = Digital_Twin(name= "5s_determ", template= True, Freq_Sync= 30, Freq_Valid= 60, Freq_Service= 10000, delta_t_treshold=21)
  ```
- Initial condition:
  - 9 parts in Queue 1.
  - No parts in the rest of the queues.
  - No parts inside the machines.

### Experimental Setup 2
- Model: 5s model
- RCT service: Off
- Test run time: 10 minutes
- Number of pallets: 9
- Default policy of branch: alternating policy with station 2 as initial station.
- Digital twin definition:
  ```python
  mydt = Digital_Twin(name= "5s_determ", template= True, Freq_Sync= 30, Freq_Valid= 60, Freq_Service= 10000, delta_t_treshold=21)
  ```
- Initial condition:
  - 9 parts in Queue 1.
  - No parts in the rest of the queues.
  - No parts inside the machines.

### Results
- Did RCT_server apply its service for targeted parts (Y/N):
- Throughput with RCT service On:
  - Trial 1:
  - Trial 2:
  - Trial 3:
- Throughput with RCT service Off:
  - Trial 1:
  - Trial 2:
  - Trial 3:


### Observation
- The test was run on 5s Model.

## Test 5
### Objective
- Add failures (changes in the process time) we analyze if the validation and model update is being able to correct those misalignments and give in the end a more precise RCT prediction

### Experimental Setup
- Model: 5s model
- RCT service: On
- Number of pallets: 7
- Default policy of branch: alternating policy with station 2 as initial station.
- Digital twin definition:
  ```python
  mydt = Digital_Twin(name= "5s_determ", template= True, Freq_Sync= 30, Freq_Valid= 60, Freq_Service= 10000, delta_t_treshold=21)
  ```
- Initial condition:
  - 7 parts in Queue 1.
  - No parts in the rest of the queues.
  - No parts inside the machines.
- Process time temporarily adjusted by manipulating the blocking sensor.
  
### Results
- Did RCT_server apply its service for targeted parts (Y/N):
- Validation indicator


### Observation
- The test was run on 5s Model.


