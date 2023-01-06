
<details>
  <summary>06/01/2023</summary>
  ManPy package installed using the following command does not have any simulation related files inside the library.
  
  ```python
  python3 -m pipenv install manpy
  ```
  
  It was first noticed while trying to run the following code:
  

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
  
    ```
  
  It was then confirmed by checking the library contents directly at the site of library installation.
  
  
  Hence, retired to install ManPy available from ManPy's github repository: https://github.com/nexedi/dream. The docuementation for ManPy which had the installation guidelines are available at https://github.com/Nexedi/dream/raw/master/ManPy_documentation.pdf.
  As per the guidelines in the abaove documentation, running setup.py file inside the package should have installed ManPy and related packages. The installation was tried with different perspectives including trying to install outside the virtual environment. But it gave out following error:
  
  ```
  ERROR: Could not find a version that satisfies the requirement setup.py (from versions: none)
  ERROR: No matching distribution found for setup.py
  ```
  
  One of the probable solution was to install the required dependencies manually before executing the setup.py file. The requirements were obtained from the list of requirements inside the setup.py script. Still the above mentioned error was repeated. Following were the requiremnts mentioned:
  - flask
  - SimPy>=3
  - xlrd
  - xlwt
  - pyparsing
  - pydot
  - numpy
  - zope.dottedname
  - rpy2
  - pulp
  - tablib
  - mysqlclient
  
  It has to be noted that, ManPy documentation has described the fact that, ManPy is a project under the name DREAM.
  
</details>

<details>
  <summary>05/01/2023</summary>
  
  - Tried to install the library ManPy from the github, but for that they recommend to use `python setup.py install`. But this approach was not working. I also tried to create the library using `python setup.py sdist`, but it was also not working. It was showing the following error:
  
  ```python
  py -> dream-0.0.1\.\dream\KnowledgeExtraction\KEtoolSimul8_examples\ParallelStationsFailures
  error: could not create 'dream-0.0.1\.\dream\KnowledgeExtraction\KEtoolSimul8_examples\ParallelStationsFailu
  res\ParallelStationsFailures.py': No such file or directory
  ```
  
  We tried several ways to fix that and to avoid the error, but nothing worked.
  
  - After that we took the the folder ```ManPy``` from the Digitial Twin folder and placed in an different folder. We tried to import some function from ManPy, some errors appeared because we were missing some libraries as follow
    - SimPy3
    - xlrd
    - xlwt
  - With this new folder ManPy and with the libraries it was possible to import function inside of that. But when trying to replicate the first example from the documentations it didn`t work, showing the following error
  ```python
    File "C:\Users\pedro\.virtualenvs\dtenv-wkibMAem\lib\site-packages\zope\dottedname\resolve.py", line 44, in resolve
    found = getattr(found, n)
    AttributeError: module 'dream' has no attribute 'Part'
    ModuleNotFoundError: No module named 'dream.Part'
  ```
  The testing code was
  ```python
  import numpy
  from manpy.simulation.imports import Source, Queue, Machine, Exit 

  numpy.seterr(all="raise")
  import simpy
  from manpy.simulation.Globals import G
  from manpy.simulation.Order import Order
  import manpy.simulation.PrintRoute as PrintRoute
  import manpy.simulation.ExcelHandler as ExcelHandler
  from manpy.simulation.ProcessingTimeList import ProcessingTimeList
  from manpy.simulation.RandomNumberGenerator import RandomNumberGenerator
  import time
  from random import Random
  import manpy.simulation.Globals as Globals



  S= Source('S1','Source',interArrivalTime={'Fixed':{'mean':0.5}}, entity='Dream.Part')
  Q=Queue('Q1','Queue', capacity=1)
  M=Machine('M1','Machine', processingTime={'Fixed':{'mean':0.25}})
  E=Exit('E1','Exit') 
  #define predecessors and successors for the objects 
  S.defineRouting(successorList=[Q])
  Q.defineRouting(predecessorList=[S],successorList=[M])
  M.defineRouting(predecessorList=[Q],successorList=[E])
  E.defineRouting(predecessorList=[M])
```
  we can see the error because here we use the name Dream ```S= Source('S1','Source',interArrivalTime={'Fixed':{'mean':0.5}}, entity='Dream.Part')```.
  Changing the name to "manpy" it worked.
  
  ### Next Steps
  - Try to follow the documentation to understand better how ManPy works and see until when it's possible to replicate the examples even without using the right version of the ManPy (because we're using one from the Digital Twin and not the "Dream" one)
  - Try to run the examples and replicate differents 
  - Start testing the functions of the Digital Twin in case isoleted
  - Test the SED with Simpy, maybe we can use directly this library instead of ManPy
 
  
</details>

