from .Machine import Machine
from .Globals import G

class ParallelMachine(Machine):
    def canAccept(self, callerObject=None):
        # do not start processing unless the sum of parts in the parallel and the parts in the following queue are
        # lower than the capacity required, which is equal to the number of machines in parallel
        if (self.countInternalParts() + len(self.next[0].getActiveObjectQueue())) >= len(G.InternalParallelList):
            return False
        return Machine.canAccept(self, callerObject)

    def canAcceptAndIsRequested(self, callerObject=None):
        if (self.countInternalParts() + len(self.next[0].getActiveObjectQueue())) >= len(G.InternalParallelList):
            return False
        return Machine.canAcceptAndIsRequested(self, callerObject)

    # returns the number of internal parts in the parallel
    def countInternalParts(self):
        totalParts = 0
        for object in G.InternalParallelList:
            totalParts += len(object.getActiveObjectQueue())
        return totalParts
