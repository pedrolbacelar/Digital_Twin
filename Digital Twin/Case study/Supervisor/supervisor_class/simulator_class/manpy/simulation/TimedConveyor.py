from .Conveyor import Conveyor

class TimedConveyor(Conveyor):
    def canAccept(self, callerObject=None):
        # if the sum of parts on the conveyor and the following queue is higher than the capacity, don't accept
        if (len(self.next[0].getActiveObjectQueue()) + len(self.getActiveObjectQueue())) > self.capacity:
            return False
        # else use the normal conveyor logic
        # return Conveyor.canAccept(self, callerObject)
        else: return True

    def canAcceptAndIsRequested(self, callerObject=None):
        # if the sum of parts on the conveyor and the following queue is higher than the capacity, don't accept
        activeObjectQueue = self.Res.users
        giverObject = callerObject
        assert giverObject, "there must be a caller for canAcceptAndIsRequested"
        if (len(activeObjectQueue) + len(self.next[0].getActiveObjectQueue())) > self.capacity and giverObject.haveToDispose(
            self
        ):
            return False
        # return Conveyor.canAcceptAndIsRequested(self, callerObject)
        else: return True
