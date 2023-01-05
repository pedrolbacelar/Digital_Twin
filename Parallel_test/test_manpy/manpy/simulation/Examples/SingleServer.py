from manpy.simulation.imports import Source, Queue, Machine, Exit
from manpy.simulation.Globals import runSimulation

# define the objects of the model
S = Source(
    "S1", "Source", interArrivalTime={"Fixed": {"mean": 0.5}}, entity="manpy.Part"
)
Q = Queue("Q1", "Queue", capacity=1000)
M = Machine("M1", "Machine", capacity=1, processingTime={"Fixed": {"mean": 1}})
E = Exit("E1", "Exit", gatherSysTimeEx=True)

# define predecessors and successors for the objects
S.defineRouting(successorList=[Q])
Q.defineRouting(predecessorList=[S], successorList=[M])
M.defineRouting(predecessorList=[Q], successorList=[E])
E.defineRouting(predecessorList=[M])


def main(test=0):
    # add all the objects in a list
    objectList = [S, Q, M, E]
    # set the length of the experiment
    maxSimTime = 100
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)

    # calculate metrics
    working_ratio = (M.totalWorkingTime / maxSimTime) * 100

    # return results for the test
    if test:
        return {"parts": E.numOfExits, "working_ratio": working_ratio}

    # print the results
    print(("the system produced", E.numOfExits, "parts"))
    print(("the total working ratio of the Machine is", working_ratio, "%"))
    print(E.SysTime_E)


if __name__ == "__main__":
    main()
