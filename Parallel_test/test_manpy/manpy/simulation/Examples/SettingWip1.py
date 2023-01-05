from manpy.simulation.imports import Machine, Queue, Exit, Part, ExcelHandler
from manpy.simulation.Globals import runSimulation, G

# define the objects of the model
Q = Queue("Q1", "Queue", capacity=1)
M = Machine("M1", "Machine", processingTime={"Fixed": {"mean": 0.25}})
E = Exit("E1", "Exit")
P1 = Part("P1", "Part1", currentStation=Q)      # We don't have a source, we simply have a part in the queue

# define predecessors and successors for the objects
Q.defineRouting(successorList=[M])
M.defineRouting(predecessorList=[Q], successorList=[E])
E.defineRouting(predecessorList=[M])


def main(test=0):
    # add all the objects in a list
    objectList = [Q, M, E, P1]
    # set the length of the experiment
    maxSimTime = float("inf")       # We run the simulation until the only part goes into the sink
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime, trace="Yes")

    # calculate metrics
    working_ratio = (M.totalWorkingTime / G.maxSimTime) * 100   # We can't use maxSimTime since it is inf, we use G.

    # return results for the test
    if test:
        return {
            "parts": E.numOfExits,
            "simulationTime": E.timeLastEntityLeft,     # Time at which the last entity was disposed in a sink
            "working_ratio": working_ratio,
        }

    # print the results
    print(
        (
            "the system produced",
            E.numOfExits,
            "parts in",
            E.timeLastEntityLeft,
            "minutes",
        )
    )
    print(("the total working ratio of the Machine is", working_ratio, "%"))
    ExcelHandler.outputTrace("Wip1")       # We save the trace into an excel file


if __name__ == "__main__":
    main()
