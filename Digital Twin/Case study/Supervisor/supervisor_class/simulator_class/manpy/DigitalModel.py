# ===========================================================================
#                                    IMPORTS
# ===========================================================================
import logging

logger = logging.getLogger("manpy.platform")

# By default numpy just prints on stderr when there's an error. We do not want
# to hide errors.
import numpy

numpy.seterr(all="raise")
import simpy


from manpy.simulation.Globals import G
from manpy.simulation.Order import Order
import manpy.simulation.PrintRoute as PrintRoute
import manpy.simulation.ExcelHandler as ExcelHandler
from manpy.simulation.ProcessingTimeList import ProcessingTimeList
from manpy.simulation.RandomNumberGenerator import RandomNumberGenerator
import manpy.simulation.Globals as Globals


"""
from simulation.Globals import G
from simulation.Order import Order
import simulation.PrintRoute as PrintRoute
import simulation.ExcelHandler as ExcelHandler
from simulation.ProcessingTimeList import ProcessingTimeList
from simulation.RandomNumberGenerator import RandomNumberGenerator
import simulation.Globals as Globals
"""


import time
from random import Random


class DigitalModel:
    def __init__(self, execModel, ID=None):
        # The graphModel must be given as a dict
        if not isinstance(execModel, dict):
            raise ValueError("The executable model must be given as a dict")

        # Save the dict with key 'general'
        self.general = execModel["general"]

        # Save the dict of the nodes and edges
        self.nodes = execModel["graph"]["node"]
        self.edges = execModel["graph"]["edge"]
        self.inputWIP = execModel.get("input", {})
        self.bom = self.inputWIP.get("BOM", None)

        # Save the ID of the current executable model
        self.ID = ID

        # Initialize the attribute that saves the number of WIP in a closed system
        self.numOfWIP = 0

        # Initialize the lists with all the elements of the model
        self.ObjectList = []
        self.RouterListC = []
        self.EntityListC = []

        # Initialize the model
        G.ObjList = []          # first we initialize the global lists as empty
        G.RouterList = []
        # We initialize the lists and assign them as attributes of the object
        self.createObjectResourcesAndCoreObjects()
        self.createObjectInterruptions()
        self.setTopology()
        # self.ObjectList = G.ObjList
        # self.RouterListC = G.RouterList
        # We empty the global lists
        G.ObjList = []
        G.RouterList = []
        self.Thisenv = simpy.Environment()

# ===========================================================================
#                       reads general simulation inputs
# ===========================================================================
    def __repr__(self):
        sentence = f"Model composed of those {len(self.ObjectList)} objects \n"
        for i, a in enumerate(self.ObjectList):
            sentence += f'{a.id!r}: predecessorList = {a.previousIds}, successorList = {a.nextIds}\n'
        return sentence

# ===========================================================================
#                       reads general simulation inputs
# ===========================================================================
    def readGeneralInput(self):
        G.numberOfReplications = int(
            self.general.get("numberOfReplications", "1")
        )  # read the number of replications / default 1
        G.maxSimTime = float(
            self.general.get("maxSimTime", "100")
        )  # get the maxSimTime / default 100
        G.trace = self.general.get(
            "trace", "No"
        )  # get trace in order to check if trace is requested
        G.console = self.general.get(
            "console", "No"
        )  # get console flag in order to check if console print is requested
        G.confidenceLevel = float(
            self.general.get("confidenceLevel", "0.95")
        )  # get the confidence level
        G.seed = self.general.get("seed")  # the seed for random number generation
        G.extraPropertyDict = self.general.get(
            "extraPropertyDict", {}
        )  # a dict to put extra properties that are
        # generic for the model
        G.initializingFlag = self.general.get(
            "initializingFlag", False
        )
        G.initializingFilename = self.general.get(
            "initializingFilename", ""
        )

# ===========================================================================
    # Finds the list of successors for each object
# ===========================================================================
    def getSuccessorList(
        self, node_id, predicate=lambda source, destination, edge_class, edge_data: True
    ):
        successor_list = []  # dummy variable that holds the list to be returned

        for edge in list(self.edges.values()):
            source = edge["source"]
            destination = edge["destination"]
            edge_class = edge["_class"]
            edge_data = edge.get("data", {})
            if source == node_id:  # for the node_id argument
                if predicate(
                    source, destination, edge_class, edge_data
                ):  # find its 'destinations' and
                    successor_list.append(
                        destination
                    )  # append it to the successor list

        # XXX We should probably not need to sort, but there is a bug that
        # prevents Topology10 to work if this sort is not used.
        successor_list.sort()
        return successor_list

# ===========================================================================
#                       creates first the object interruptions
#                            and then the core objects
# ===========================================================================
    def createObjectResourcesAndCoreObjects(self):
        """
        define the lists of each object type
        """
        G.SourceList = []
        G.MachineList = []
        G.ExitList = []
        G.QueueList = []
        G.RepairmanList = []
        G.AssemblyList = []
        G.DismantleList = []
        G.ConveyorList = []
        G.MachineJobShopList = []
        G.QueueJobShopList = []
        G.ExitJobShopList = []
        G.BatchDecompositionList = []
        G.BatchSourceList = []
        G.BatchReassemblyList = []
        G.RoutingQueueList = []
        G.LineClearanceList = []
        G.EventGeneratorList = []
        G.OperatorsList = []
        G.OperatorManagedJobsList = []
        G.OperatorPoolsList = []
        G.BrokersList = []
        G.OperatedMachineList = []
        G.BatchScrapMachineList = []
        G.OrderDecompositionList = []
        G.ConditionalBufferList = []
        G.MouldAssemblyBufferList = []
        G.MouldAssemblyList = []
        G.MachineManagedJobList = []
        G.QueueManagedJobList = []
        G.ObjectResourceList = []
        G.CapacityStationBufferList = []
        G.AllocationManagementList = []
        G.CapacityStationList = []
        G.CapacityStationExitList = []
        G.CapacityStationControllerList = []

        """
        loop through all the model resources
        search for repairmen and operators in order to create them
        read the data and create them
        """

        for (element_id, element) in list(
            self.nodes.items()
        ):  # use an iterator to go through all the nodes
            element["id"] = element_id  # create a new entry for the element (dictionary)
            element = element.copy()
            for k in ("element_id", "top", "left"):
                element.pop(k, None)
                # with key 'id' and value the the element_id
            # resourceClass = element.pop("_class")  # get the class type of the element
            resourceClass = element["_class"]

            objectType = Globals.getClassFromName(resourceClass)
            from manpy.simulation.ObjectResource import (
                ObjectResource,
            )  # operator pools to be created later since they use operators

            # ToDo maybe it is semantically different object
            if (
                issubclass(objectType, ObjectResource)
                and not resourceClass == "manpy.OperatorPool"
            ):
                inputDict = dict(element)
                # create the CoreObject
                objectResource = objectType(**inputDict)
                # if there already coreObjectsIds defined then append the successors to them
                if objectResource.coreObjectIds:
                    for element in self.getSuccessorList(element["id"]):
                        if not element in objectResource.coreObjectIds:
                            objectResource.coreObjectIds.append(element)
                else:
                    objectResource.coreObjectIds = self.getSuccessorList(element["id"])

        """
        loop through all the model resources
        search for operatorPools in order to create them
        read the data and create them
        """
        from manpy.simulation.OperatorPool import OperatorPool

        for (element_id, element) in list(
            self.nodes.items()
        ):  # use an iterator to go through all the nodes
            # the key is the element_id and the second is the
            # element itself
            element = element.copy()
            element["id"] = element_id  # create a new entry for the element (dictionary)
            for k in ("element_id", "top", "left"):
                element.pop(k, None)
                # with key 'id' and value the the element_id
            # resourceClass = element.pop("_class")  # get the class type of the element
            resourceClass = element["_class"]
            if resourceClass == "manpy.OperatorPool":
                id = element.get(
                    "id", "not found"
                )  # get the id of the element   / default 'not_found'
                name = element.get(
                    "name", "not found"
                )  # get the name of the element / default 'not_found'
                capacity = int(element.get("capacity") or 1)
                operatorsList = []
                for (
                    operator
                ) in G.OperatorsList:  # find the operators assigned to the operatorPool
                    if id in operator.coreObjectIds:
                        operatorsList.append(operator)
                #             operatorsList = element.get('operatorsList', 'not found')
                if (
                    len(operatorsList) == 0
                ):  # if the operatorsList is empty then assign no operators
                    OP = OperatorPool(
                        element_id, name, capacity
                    )  # create a operatorPool object
                else:
                    OP = OperatorPool(
                        element_id, name, capacity, operatorsList
                    )  # create a operatorPool object
                OP.coreObjectIds = self.getSuccessorList(
                    id
                )  # update the list of objects that the operators of the operatorPool operate
                for operator in operatorsList:
                    operator.coreObjectIds = (
                        OP.coreObjectIds
                    )  # update the list of objects that the operators operate
                G.OperatorPoolsList.append(OP)  # add the operatorPool to the RepairmanList
        """
        loop through all the elements
        read the data and create them
        """
        for (element_id, element) in list(self.nodes.items()):
            element = element.copy()
            element["id"] = element_id
            element.setdefault("name", element_id)

            # XXX not sure about top & left.
            for k in ("element_id", "top", "left"):
                element.pop(k, None)
            # objClass = element.pop("_class")
            objClass = element["_class"]
            objectType = Globals.getClassFromName(objClass)

            from manpy.simulation.CoreObject import CoreObject

            if issubclass(objectType, CoreObject):
                # remove data that has to do with wip or object interruption. CoreObjects do not need it
                inputDict = dict(element)
                # create the CoreObject
                coreObject = objectType(**inputDict)
                self.ObjectList.append(coreObject)
                # update the nextIDs list of the object
                coreObject.nextIds = self.getSuccessorList(element["id"])
                # (Below is only for Dismantle for now)
                # get the successorList for the 'Parts'
                coreObject.nextPartIds = self.getSuccessorList(
                    element["id"],
                    lambda source, destination, edge_class, edge_data: edge_data.get(
                        "entity", {}
                    )
                    == "Part",
                )
                # get the successorList for the 'Frames'
                coreObject.nextFrameIds = self.getSuccessorList(
                    element["id"],
                    lambda source, destination, edge_class, edge_data: edge_data.get(
                        "entity", {}
                    )
                    == "Frame",
                )

        #                    loop through all the core objects
        #                         to read predecessors
        for element in self.ObjectList:
            # loop through all the nextIds of the object
            for nextId in element.nextIds:
                # loop through all the core objects to find the on that has the id that was read in the successorList
                for possible_successor in self.ObjectList:
                    if possible_successor.id == nextId:
                        possible_successor.previousIds.append(element.id)

# ===========================================================================
#                creates the object interruptions
# ===========================================================================
    def createObjectInterruptions(self):
        G.ObjectInterruptionList = []
        G.ScheduledMaintenanceList = []
        G.FailureList = []
        G.BreakList = []
        G.ShiftSchedulerList = []
        G.ScheduledBreakList = []
        G.EventGeneratorList = []
        G.CapacityStationControllerList = []
        G.PeriodicMaintenanceList = []

        #                loop through all the nodes to
        #            search for Event Generator and create them
        #                   this is put last, since the EventGenerator
        #                may take other objects as argument
        for (element_id, element) in list(
            self.nodes.items()
        ):  # use an iterator to go through all the nodes
            # the key is the element_id and the second is the
            # element itself
            element["id"] = element_id  # create a new entry for the element (dictionary)
            # with key 'id' and value the the element_id
            objClass = element.get(
                "_class", "not found"
            )  # get the class type of the element
            from manpy.simulation.ObjectInterruption import ObjectInterruption

            # objClass = element.pop("_class")
            objClass = element["_class"]
            objectType = Globals.getClassFromName(objClass)
            # from CoreObject import CoreObject
            # if issubclass(objectType, CoreObject):

            if issubclass(objectType, ObjectInterruption):  # check the object type
                inputDict = dict(element)
                # create the ObjectInterruption
                objectInterruption = objectType(**inputDict)
                if not "OperatorRouter" in str(objectType):
                    G.ObjectInterruptionList.append(objectInterruption)

        # search inside the nodes for encapsulated ObjectInterruptions (failures etc)
        # ToDo this will be cleaned a lot if we update the JSON notation:
        # define ObjectInterruption echelon inside node
        # define interruptions' distribution better
        from manpy.simulation.ScheduledMaintenance import ScheduledMaintenance
        from manpy.simulation.Failure import Failure
        from manpy.simulation.PeriodicMaintenance import PeriodicMaintenance
        from manpy.simulation.ShiftScheduler import ShiftScheduler
        from manpy.simulation.ScheduledBreak import ScheduledBreak
        from manpy.simulation.Break import Break

        for (element_id, element) in list(self.nodes.items()):
            element["id"] = element_id
            scheduledMaintenance = element.get("interruptions", {}).get(
                "scheduledMaintenance", {}
            )
            # if there is a scheduled maintenance initiate it and append it
            # to the interruptions- and scheduled maintenances- list
            if len(scheduledMaintenance):
                start = float(scheduledMaintenance.get("start", 0))
                duration = float(scheduledMaintenance.get("duration", 1))
                victim = self.ObjectById(element["id"])
                SM = ScheduledMaintenance(victim=victim, start=start, duration=duration)
                G.ObjectInterruptionList.append(SM)
                G.ScheduledMaintenanceList.append(SM)
            failure = element.get("interruptions", {}).get("failure", None)
            # if there are failures assigned
            # initiate them
            if failure:
                victim = self.ObjectById(element["id"])
                deteriorationType = failure.get("deteriorationType", "constant")
                waitOnTie = failure.get("waitOnTie", False)
                F = Failure(
                    victim=victim,
                    distribution=failure,
                    repairman=victim.repairman,
                    deteriorationType=deteriorationType,
                    waitOnTie=waitOnTie,
                )
                G.ObjectInterruptionList.append(F)
                G.FailureList.append(F)
            # if there are periodic maintenances assigned
            # initiate them
            periodicMaintenance = element.get("interruptions", {}).get(
                "periodicMaintenance", None
            )
            if periodicMaintenance:
                distributionType = periodicMaintenance.get("distributionType", "No")
                victim = self.ObjectById(element["id"])
                PM = PeriodicMaintenance(
                    victim=victim,
                    distribution=periodicMaintenance,
                    repairman=victim.repairman,
                )
                G.ObjectInterruptionList.append(PM)
                G.PeriodicMaintenanceList.append(PM)
            # if there is a shift pattern defined
            # initiate them
            shift = element.get("interruptions", {}).get("shift", {})
            if len(shift):
                victim = self.ObjectById(element["id"])
                shiftPattern = list(shift.get("shiftPattern", []))
                # patch to correct if input has end of shift at the same time of start of next shift
                # TODO check if the backend should be able to handle this
                for index, record in enumerate(shiftPattern):
                    if record is shiftPattern[-1]:
                        break
                    next = shiftPattern[index + 1]
                    if record[1] == next[0]:
                        record[1] = next[1]
                        shiftPattern.remove(next)
                endUnfinished = bool(int(shift.get("endUnfinished", 0)))
                receiveBeforeEndThreshold = float(shift.get("receiveBeforeEndThreshold", 0))
                thresholdTimeIsOnShift = bool(int(shift.get("thresholdTimeIsOnShift", 1)))
                rolling = bool(int(shift.get("rolling", 0)))
                lastOffShiftDuration = float(shift.get("lastOffShiftDuration", 10))
                SS = ShiftScheduler(
                    victim=victim,
                    shiftPattern=shiftPattern,
                    endUnfinished=endUnfinished,
                    receiveBeforeEndThreshold=receiveBeforeEndThreshold,
                    thresholdTimeIsOnShift=thresholdTimeIsOnShift,
                    rolling=rolling,
                    lastOffShiftDuration=lastOffShiftDuration,
                )
                G.ObjectInterruptionList.append(SS)
                G.ShiftSchedulerList.append(SS)
            scheduledBreak = element.get("interruptions", {}).get("scheduledBreak", None)
            # if there are scheduled breaks assigned initiate them
            if scheduledBreak:
                victim = self.ObjectById(element["id"])
                breakPattern = list(scheduledBreak.get("breakPattern", []))
                for index, record in enumerate(breakPattern):
                    if record is breakPattern[-1]:
                        break
                    next = breakPattern[index + 1]
                    if record[1] == next[0]:
                        record[1] = next[1]
                        shiftPattern.remove(next)
                endUnfinished = bool(int(scheduledBreak.get("endUnfinished", 0)))
                receiveBeforeEndThreshold = float(
                    scheduledBreak.get("receiveBeforeEndThreshold", 0)
                )
                rolling = bool(int(scheduledBreak.get("rolling", 0)))
                lastNoBreakDuration = float(scheduledBreak.get("lastOffShiftDuration", 10))
                SB = ScheduledBreak(
                    victim=victim,
                    breakPattern=breakPattern,
                    endUnfinished=endUnfinished,
                    receiveBeforeEndThreshold=receiveBeforeEndThreshold,
                    rolling=rolling,
                    lastNoBreakDuration=lastNoBreakDuration,
                )
                G.ObjectInterruptionList.append(SB)
                G.ShiftSchedulerList.append(SB)
            br = element.get("interruptions", {}).get("break", None)
            # if there are random breaks assigned initiate them
            if br:
                victim = self.ObjectById(element["id"])
                endUnfinished = bool(int(br.get("endUnfinished", 1)))
                offShiftAnticipation = br.get("offShiftAnticipation", 0)
                BR = Break(
                    victim=victim,
                    distribution=br,
                    endUnfinished=endUnfinished,
                    offShiftAnticipation=offShiftAnticipation,
                )
                G.ObjectInterruptionList.append(BR)
                G.BreakList.append(BR)

# ===========================================================================
#                       creates the entities that are wip
# ===========================================================================
    def createWIP(self):
        G.JobList = []
        G.WipList = []
        G.EntityList = []
        G.PartList = []
        G.OrderComponentList = []
        G.DesignList = []  # list of the OrderDesigns in the system
        G.OrderList = []
        G.MouldList = []
        G.BatchList = []
        G.SubBatchList = []
        G.CapacityEntityList = []
        G.CapacityProjectList = []
        # entities that just finished processing in a station
        # and have to enter the next machine
        G.pendingEntities = []

        # Initialize the entity list
        self.EntityListC = []
        # Initialize the number of WIP in a closed loop system
        self.numOfWIP = 0

        if self.bom:
            orders = self.bom.get("productionOrders", [])
            # for every order in the productionOrders list
            for prodOrder in orders:
                orderClass = prodOrder.get("_class", None)
                orderType = Globals.getClassFromName(orderClass)
                # make sure that their type is manpy.Order
                if orderClass == "manpy.Order":
                    id = prodOrder.get("id", "not found")
                    name = prodOrder.get("name", "not found")
                    priority = int(prodOrder.get("priority", "0"))
                    dueDate = float(prodOrder.get("dueDate", "0"))
                    orderDate = float(prodOrder.get("orderDate", "0"))
                    isCritical = bool(int(prodOrder.get("isCritical", "0")))
                    componentsReadyForAssembly = bool(
                        (prodOrder.get("componentsReadyForAssembly", False))
                    )
                    componentsList = prodOrder.get("componentsList", {})
                    # keep a reference of all extra properties passed to the job
                    extraPropertyDict = {}
                    for key, value in list(prodOrder.items()):
                        if key not in ("_class", "id"):
                            extraPropertyDict[key] = value
                    # initiate the Order
                    O = Order(
                        "G" + id,
                        "general " + name,
                        route=[],
                        priority=priority,
                        dueDate=dueDate,
                        orderDate=orderDate,
                        isCritical=isCritical,
                        componentsList=componentsList,
                        componentsReadyForAssembly=componentsReadyForAssembly,
                        extraPropertyDict=extraPropertyDict,
                    )
                    G.OrderList.append(O)
                else:
                    productionOrderClass = prodOrder.get("_class", None)
                    productionOrderType = Globals.getClassFromName(productionOrderClass)
                    inputDict = dict(prodOrder)
                    inputDict.pop("_class")
                    from manpy.simulation.Entity import Entity

                    if issubclass(productionOrderType, Entity):
                        entity = productionOrderType(**inputDict)
                        self.EntityListC.append(entity)

        for (element_id, element) in list(self.nodes.items()):
            element["id"] = element_id
            wip = element.get("wip", [])
            self.numOfWIP += len(wip)       # add the number of WIP to the variable
            from manpy.simulation.OrderDesign import OrderDesign

            for entity in wip:
                # if there is BOM defined
                if self.bom:
                    # and production orders in it
                    if self.bom.get("productionOrders", []):
                        # find which order has the entity in its componentsList
                        for order in G.OrderList:
                            if order.componentsList:
                                for componentDict in order.componentsList:
                                    # if the entity has no parent order the following control will not be performed
                                    if entity["id"] == componentDict["id"]:
                                        entityCurrentSeq = int(
                                            entity["sequence"]
                                        )  # the current seq number of the entity's  route
                                        entityRemainingProcessingTime = entity.get(
                                            "remainingProcessingTime", {}
                                        )
                                        entityRemainingSetupTime = entity.get(
                                            "remainingSetupTime", {}
                                        )
                                        ind = 0  # holder of the route index corresponding to the entityCurrentSeq
                                        solution = False  # flag to signal that the route step is found
                                        # find the step that corresponds to the entityCurrentSeq
                                        for i, step in enumerate(
                                            componentDict.get("route", [])
                                        ):
                                            stepSeq = step[
                                                "sequence"
                                            ]  # the sequence of step i
                                            if stepSeq == "":
                                                stepSeq = 0  # if the seq is ''>OrderDecomposition then 0
                                            # if the entityCurrentSeq is found and the id of the holding Station is in the steps stationIdsList
                                            if (
                                                int(stepSeq) == entityCurrentSeq
                                                and element["id"] in step["stationIdsList"]
                                            ):
                                                ind = i  # hold the index
                                                solution = True  # the solution isfound
                                                break
                                        # assert that there is solution
                                        assert solution, (
                                            "something is wrong with the initial step of "
                                            + entity["id"]
                                        )
                                        # the remaining route of the entity assuming that the given route doesn't start from the entityCurrentSeq
                                        entityRoute = componentDict.get("route", [])[ind:]
                                        entity = dict(componentDict)  # copy the entity dict
                                        entity.pop("route")  # remove the old route
                                        entity[
                                            "route"
                                        ] = entityRoute  # and hold the new one without the previous steps
                                        entity["order"] = order.id
                                        entity[
                                            "remainingProcessingTime"
                                        ] = entityRemainingProcessingTime
                                        entity[
                                            "remainingSetupTime"
                                        ] = entityRemainingSetupTime
                                        break

                entityClass = entity.get("_class", None)
                entityType = Globals.getClassFromName(entityClass)
                inputDict = dict(entity)
                inputDict.pop("_class")
                from manpy.simulation.Entity import Entity

                if issubclass(entityType, Entity) and (not entityClass == "manpy.Order"):
                    # if orders are provided separately (BOM) provide the parent order as argument
                    if entity.get("order", None):
                        entityOrder = self.ObjectById(entity["order"])
                        inputDict.pop("order")
                        entity = entityType(order=entityOrder, **inputDict)
                        entity.routeInBOM = True
                    else:
                        entity = entityType(**inputDict)
                    self.EntityListC.append(entity)
                    object = self.ObjectById(element["id"])
                    entity.currentStation = object

                # ToDo order is to defined in a new way
                if entityClass == "manpy.Order":
                    id = entity.get("id", "not found")
                    name = entity.get("name", "not found")
                    priority = int(entity.get("priority", "0"))
                    dueDate = float(entity.get("dueDate", "0"))
                    orderDate = float(entity.get("orderDate", "0"))
                    isCritical = bool(int(entity.get("isCritical", "0")))
                    basicsEnded = bool(int(entity.get("basicsEnded", "0")))
                    componentsReadyForAssembly = bool(
                        (entity.get("componentsReadyForAssembly", False))
                    )
                    # read the manager ID
                    manager = entity.get("manager", None)
                    # if a manager ID is assigned then search for the operator with the corresponding ID
                    # and assign it as the manager of the order
                    if manager:
                        for operator in G.OperatorsList:
                            if manager == operator.id:
                                manager = operator
                                break
                    componentsList = entity.get("componentsList", {})
                    JSONRoute = entity.get(
                        "route", []
                    )  # dummy variable that holds the routes of the jobs
                    #    the route from the JSON file
                    #    is a sequence of dictionaries
                    route = [x for x in JSONRoute]  #    copy JSONRoute

                    # keep a reference of all extra properties passed to the job
                    extraPropertyDict = {}
                    for key, value in list(entity.items()):
                        if key not in ("_class", "id"):
                            extraPropertyDict[key] = value

                    # Below it is to assign an order decomposition if it was not assigned in JSON
                    # have to talk about it with NEX
                    odAssigned = False
                    for element in route:
                        elementIds = element.get("stationIdsList", [])
                        for obj in self.ObjectList:
                            for elementId in elementIds:
                                if obj.id == elementId and obj.type == "OrderDecomposition":
                                    odAssigned = True
                    if not odAssigned:
                        odId = None
                        for obj in self.ObjectList:
                            if obj.type == "OrderDecomposition":
                                odId = obj.id
                                break
                        if odId:
                            #                         route.append([odId, 0])
                            route.append(
                                {
                                    "stationIdsList": [odId],
                                    "processingTime": {
                                        "distributionType": "Fixed",
                                        "mean": "0",
                                    },
                                }
                            )
                    # XXX dirty way to implement new approach were the order is abstract and does not run through the system
                    # but the OrderDesign does
                    # XXX initiate the Order and the OrderDesign
                    O = Order(
                        "G" + id,
                        "general " + name,
                        route=[],
                        priority=priority,
                        dueDate=dueDate,
                        orderDate=orderDate,
                        isCritical=isCritical,
                        basicsEnded=basicsEnded,
                        manager=manager,
                        componentsList=componentsList,
                        componentsReadyForAssembly=componentsReadyForAssembly,
                        extraPropertyDict=extraPropertyDict,
                    )
                    # create the OrderDesign
                    OD = OrderDesign(
                        id,
                        name,
                        route,
                        priority=priority,
                        dueDate=dueDate,
                        orderDate=orderDate,
                        isCritical=isCritical,
                        order=O,
                        extraPropertyDict=extraPropertyDict,
                    )
                    # add the order to the OrderList
                    G.OrderList.append(O)
                    # add the OrderDesign to the DesignList and the OrderComponentList
                    G.OrderComponentList.append(OD)
                    G.DesignList.append(OD)
                    G.WipList.append(OD)
                    self.EntityListC.append(OD)
                    G.JobList.append(OD)

        # if in the input json file there is the flag to include routing call the function routeWIP
        if G.initializingFlag and G.initializingFilename != "":
            self.initializeWIP_fromFile()

# ===========================================================================
#    function to introduce WIP through a initializing input file
# ===========================================================================
    def initializeWIP_fromFile(self):
        # open the initialize file
        initializingFileName = G.initializingFilename     # get the file name from the input json file
        initializingFile = open(initializingFileName, "r")            # open the file
        initializingContent = initializingFile.read()                 # read the content of the file
        initializingFile.close()                                 # close the file
        initializingList = initializingContent.split("\n")            # split the file into a list of strings
        entityClass = "manpy.Part"
        entityType = Globals.getClassFromName(entityClass)
        self.numOfWIP += len(initializingList)              # add the number of WIP to the variable
        for i in range(len(initializingList)):                   # for every element in the initializing file
            PartID = "P" + str(int(i) + 1)                  # ID of the part
            PartName = "Part" + str(int(i) + 1)             # name of the part
            PartDict = {
                "id": PartID,
                "name": PartName
            }
            entityR = entityType(**PartDict)
            initializingQueueName = self.ObjectById("Q" + str(int(initializingList[i])))     # object in which the part is placed
            self.EntityListC.append(entityR)                         # add the entity to the entity list
            entityR.currentStation = initializingQueueName            # place the entity in the correct queue

# ===========================================================================
#                       function to introduce WIP
# ===========================================================================
    def initializeWIP(self, init_list):
        initializingList = init_list    # init_list needs to be a list of integers
        entityClass = "manpy.Part"
        entityType = Globals.getClassFromName(entityClass)
        self.numOfWIP += len(initializingList)  # add the number of WIP to the variable
        for i in range(len(initializingList)):  # for every element in the initializing file
            PartID = "P" + str(int(i) + 1)  # ID of the part
            PartName = "Part" + str(int(i) + 1)  # name of the part
            PartDict = {
                "id": PartID,
                "name": PartName
            }
            entityR = entityType(**PartDict)
            initializingQueueName = self.ObjectById(
                "Q" + str(int(initializingList[i])))  # object in which the part is placed
            # initializingQueueName = self.ObjectById(
            #     "Q" + str(int(initializingList[i])) + '_P')  # object in which the part is placed
            self.EntityListC.append(entityR)  # add the entity to the entity list
            entityR.currentStation = initializingQueueName  # place the entity in the correct queue

# ===========================================================================
#    function to find the object by its id
# ===========================================================================

    def ObjectById(self, object_id):
        for obj in (
            self.ObjectList
            + G.ObjectResourceList
            + self.EntityListC
            + G.ObjectInterruptionList
            + G.OrderList
        ):
            if obj.id == object_id:
                return obj
        return None

# =======================================================================
# method to set-up the entities in the current stations
# =======================================================================

    def setupWIP(self, entityList):
        # for all the entities in the entityList
        for entity in entityList:
            # if the entity is of type Part
            if entity.type in ["Part", "Batch", "SubBatch", "CapacityEntity", "Vehicle"]:
                # these entities have to have a currentStation.
                # TODO apply a more generic approach so that all need to have
                if entity.currentStation:
                    obj = entity.currentStation  # identify the object
                    obj.getActiveObjectQueue().append(
                        entity
                    )  # append the entity to its Queue
                    entity.schedule.append(
                        {"station": obj, "entranceTime": self.Thisenv.now}
                    )  # append the time to schedule so that it can be read in the result

            # if the entity is of type Job/OrderComponent/Order/Mould
            # XXX Orders do no more run in the system, instead we have OrderDesigns
            elif entity.type in ["Job", "OrderComponent", "Order", "OrderDesign", "Mould"]:

                # find the list of starting station of the entity
                # XXX if the entity is in wip then the current station is already defined and the remainingRoute has to be redefined
                currentObjectIds = entity.remainingRoute[0].get("stationIdsList", [])

                # get the starting station of the entity and load it with it
                objectId = currentObjectIds[0]
                obj = self.ObjectById(objectId)
                obj.getActiveObjectQueue().append(
                    entity
                )  # append the entity to its Queue
                # if the entity is to be appended to a mouldAssemblyBuffer then it is readyForAssembly
                if obj.__class__.__name__ == "MouldAssemblyBuffer":
                    entity.readyForAssembly = 1

                # read the IDs of the possible successors of the object
                nextObjectIds = entity.remainingRoute[1].get("stationIdsList", [])
                # for each objectId in the nextObjects find the corresponding object and populate the object's next list
                nextObjects = []
                for nextObjectId in nextObjectIds:
                    nextObject = self.ObjectById(nextObjectId)
                    nextObjects.append(nextObject)
                # update the next list of the object
                for nextObject in nextObjects:
                    # append only if not already in the list
                    if nextObject not in obj.next:
                        obj.next.append(nextObject)
                entity.currentStep = entity.remainingRoute.pop(
                    0
                )  # remove data from the remaining route.
                entity.schedule.append(
                    {"station": obj, "entranceTime": self.Thisenv.now}
                )  # append the time to schedule so that it can be read in the result
                # if there is currentStep task_id  then append it to the schedule
                if entity.currentStep:
                    if entity.currentStep.get("task_id", None):
                        entity.schedule[-1]["task_id"] = entity.currentStep["task_id"]
            # if the currentStation of the entity is of type Machine then the entity
            #     must be processed first and then added to the pendingEntities list
            #     Its hot flag is not raised
            # the following to be performed only if there is a current station. Orders, Projects e.t.c do not have
            # TODO, maybe we should loop in wiplist here
            if (not (entity.currentStation in G.MachineList)) and entity.currentStation:
                # add the entity to the pendingEntities list
                G.pendingEntities.append(entity)

            # if the station is buffer then sent the canDispose signal
            from manpy.simulation.Queue import Queue

            if entity.currentStation:
                if issubclass(entity.currentStation.__class__, Queue):
                    # send the signal only if it is not already triggered
                    if not entity.currentStation.canDispose.triggered:
                        if entity.currentStation.expectedSignals["canDispose"]:
                            succeedTuple = (self.Thisenv, self.Thisenv.now)
                            entity.currentStation.canDispose.succeed(succeedTuple)
                            entity.currentStation.expectedSignals["canDispose"] = 0
            # if we are in the start of the simulation the object is of server type then we should send initialWIP signal
            # TODO, maybe use 'class_family attribute here'
            if self.Thisenv.now == 0 and entity.currentStation:
                if entity.currentStation.class_name:
                    stationClass = entity.currentStation.__class__.__name__
                    if stationClass in [
                        "ProductionPoint",
                        "ConveyorMachine",
                        "ConveyorPoint",
                        "ConditionalPoint",
                        "Machine",
                        "BatchScrapMachine",
                        "MachineJobShop",
                        "BatchDecomposition",
                        "BatchReassembly",
                        "M3",
                        "MouldAssembly",
                        "BatchReassemblyBlocking",
                        "BatchDecompositionBlocking",
                        "BatchScrapMachineAfterDecompose",
                        "BatchDecompositionStartTime",
                    ]:
                        entity.currentStation.currentEntity = entity
                        # trigger initialWIP event only if it has not been triggered. Otherwise
                        # if we set more than one entities (e.g. in reassembly) it will crash
                        if not (entity.currentStation.initialWIP.triggered):
                            if entity.currentStation.expectedSignals["initialWIP"]:
                                succeedTuple = (self.Thisenv, self.Thisenv.now)
                                entity.currentStation.initialWIP.succeed(succeedTuple)
                                entity.currentStation.expectedSignals["initialWIP"] = 0

# ===========================================================================
#    function to get the machines to obtain processing time from a list
# ===========================================================================
    def initializeFromList(self, processingTable):
        # processingTable should be a pandas dataframe with column names equal to the ID of the machines
        MachList = processingTable.columns.tolist()     # a list with the IDs of the machines whose PT we have
        for mach in MachList:       # loop through the machines in the table
            procTimes = (processingTable[mach].dropna()).tolist()      # extract the processing times connected to the machine
            condition = False
            for obj in self.ObjectList:       # loop through all the object in the model
                if mach == obj.id:      # if we find the machine in the model with the same ID
                    condition = True
                    obj.procTimeVal = ProcessingTimeList(None, procTimes)   # assign the list to the machine
                    obj.fromListFlag = True
            if not condition:
                print(f'ERROR: it exist no object named {mach!r}, the columns headers should be named like the object'
                      f' they refer to!!!')

# ===========================================================================
#    function to initialize the distributions in the machine
# ===========================================================================
    def initializeDistributions(self, distributionTable):
        # distribution table should be a pandas dataframe with column names equal to the ID of the machines
        # the first row is the distribution name while the second row is a list of the parameters of the distributions
        MachList = distributionTable.columns.tolist()   # a list with the IDs of the machines
        for mach in MachList:  # loop through the machines in the table
            distr_name = distributionTable[mach][0]     # extract the name of the distribution, it's a string
            distr_param = distributionTable[mach][1]    # extract the parameters of the distribution, it's a list
            condition = False
            for obj in self.ObjectList:       # loop through all the object in the model
                if mach == obj.id:      # if we find the machine in the model with the same ID
                    condition = True
                    processingTime_temp = Globals.convertDistribution(distr_name, distr_param)
                    processingTime = obj.getOperationTime(time=processingTime_temp)
                    obj.rng = RandomNumberGenerator(obj, processingTime)    # assign to the object the distribution
            if not condition:
                print(f'ERROR: it exist no object named {mach!r}, the columns headers should be named like the object'
                      f' they refer to!!!')

# ===========================================================================
#    defines the topology (predecessors and successors for all the objects)
# ===========================================================================
    def setTopology(self):
        # loop through all the objects
        for element in self.ObjectList:
            next = []
            previous = []
            for j in range(len(element.previousIds)):
                for q in range(len(self.ObjectList)):
                    if self.ObjectList[q].id == element.previousIds[j]:
                        previous.append(self.ObjectList[q])

            for j in range(len(element.nextIds)):
                for q in range(len(self.ObjectList)):
                    if self.ObjectList[q].id == element.nextIds[j]:
                        next.append(self.ObjectList[q])

            if element.type == "Source":
                element.defineRouting(next)
            elif element.type == "Exit":
                element.defineRouting(previous)
            # Dismantle should be changed to identify what the the successor is.
            # nextPart and nextFrame will become problematic
            elif element.type == "Dismantle":
                nextPart = []
                nextFrame = []
                for j in range(len(element.nextPartIds)):
                    for q in range(len(self.ObjectList)):
                        if self.ObjectList[q].id == element.nextPartIds[j]:
                            nextPart.append(self.ObjectList[q])
                for j in range(len(element.nextFrameIds)):
                    for q in range(len(self.ObjectList)):
                        if self.ObjectList[q].id == element.nextFrameIds[j]:
                            nextFrame.append(self.ObjectList[q])
                element.defineRouting(previous, next)
                element.definePartFrameRouting(nextPart, nextFrame)
            else:
                element.defineRouting(previous, next)

# ===========================================================================
#            initializes all the objects that are in the topology
# ===========================================================================
    def initializeObjects(self):
        for element in (
            self.ObjectList
            + G.ObjectResourceList
            + self.EntityListC
            + G.ObjectInterruptionList
            + G.RouterList
        ):
            if element.name in [
                "Machine",
                "Transport",
                "Queue",
                "Source",
                "Exit",
            ]:
                element.initialize(self.Thisenv)
            else:
                element.initialize()

# ===========================================================================
#                        activates all the objects
# ===========================================================================
    def activateObjects(self):
        for element in G.ObjectInterruptionList:
            self.Thisenv.process(element.run())
        for element in self.ObjectList:
            self.Thisenv.process(element.run())

# ===========================================================================
#             method that performs
# ===========================================================================
    def runTraceSimulation(self, proc_time, init_list=None):

        # create an empty list to store all the objects in
        self.ObjectList = []
        self.RouterListC = []
        self.EntityListC = []

        # Initialize the model
        G.ObjList = []  # first we initialize the global lists as empty
        G.RouterList = []
        # We initialize the lists and assign them as attributes of the object
        self.createObjectResourcesAndCoreObjects()
        self.createObjectInterruptions()
        self.setTopology()

        # G.ObjList = self.ObjectList
        G.RouterList = self.RouterListC
        G.calculateEventList = True
        G.MachineEventList = [[], [], [], []]
        G.calculateFinalPosition = True
        G.FinalPositionList = []

        start = time.time()  # start counting execution time

        # initialize the parameters of the simulation
        maxSimTime = 100000             # we use a very high number in order to be sure we use all processing times
        G.trace = "No"                  # no trace, it doesn't function at the moment
        G.console = "No"                # no console, don't know how it works and what it does
        G.confidenceLevel = "0.95"      # it doesn't work at the moment, there is no need for it in this function
        G.seed = 1                      # doesn't matter since we don't use stochastic data
        G.extraPropertyDict = {}        # no extra functions
        G.initializingFlag = False      # we don't use an initializing flag
        G.initializingFilename = ""

        self.initializeFromList(proc_time)      # Set the processing times as from list in the specified machines

        self.Thisenv = simpy.Environment()  # initialize the environment
        # since it may be changed for infinite ones
        if G.RouterList:
            G.RouterList[0].isActivated = False
            G.RouterList[0].isInitialized = False

        # if G.seed:
        #     G.Rnd = Random("%s%s" % (G.seed, i))
        #     G.numpyRnd.random.seed(G.seed + i)
        G.Rnd = Random()
        G.numpyRnd.random.seed()

        self.createWIP()
        if init_list:
            self.initializeWIP(init_list)
        self.initializeObjects()
        self.setupWIP(self.EntityListC)
        self.activateObjects()

        # # if the simulation is ran until no more events are scheduled,
        # # then we have to find the end time as the time the last entity ended.
        # if G.maxSimTime == -1:
        #     # If someone does it for a model that has always events, then it will run forever!
        #     G.env.run(until=float("inf"))
        #
        #     # identify from the exits what is the time that the last entity has ended.
        #     endList = []
        #     for exit in G.ExitList:
        #         endList.append(exit.timeLastEntityLeft)
        #
        #     # identify the time of the last event
        #     if float(max(endList)) != 0 and (
        #         G.env.now == float("inf") or G.env.now == max(endList)
        #     ):  # do not let G.maxSimTime=0 so that there will be no crash
        #         G.maxSimTime = float(max(endList))
        #     else:
        #         print("simulation ran for 0 time, something may have gone wrong")
        #         logger.info("simulation ran for 0 time, something may have gone wrong")
        # # else we simulate until the given maxSimTime
        # else:
        #     G.env.run(until=G.maxSimTime)

        # Start the simulation
        self.Thisenv.run(until=maxSimTime)

        # We need to know the time of the last event in order to do the post processing
        maxSimTime_temp = G.MachineEventList[0][-1]
        # maxSimTime_temp = maxSimTime
        postProcCorr = True

        # carry on the post processing operations for every object in the topology
        for element in self.ObjectList + G.ObjectResourceList + G.RouterList:
            element.postProcessing(MaxSimtime=maxSimTime_temp, correction=postProcCorr)

        # added for debugging, print the Route of the Jobs on the same G.traceFile
        PrintRoute.outputRoute()

        # output trace to excel
        if G.trace == "Yes":
            ExcelHandler.outputTrace("trace")
            import io

            traceStringIO = io.StringIO()
            G.traceFile.save(traceStringIO)
            encodedTrace = traceStringIO.getvalue().encode("base64")
            ExcelHandler.resetTrace()

        outputDict = {}
        outputDict["_class"] = "manpy.Simulation"
        outputDict["general"] = {}
        outputDict["general"]["_class"] = "manpy.Configuration"
        outputDict["general"]["totalExecutionTime"] = time.time() - start
        outputDict["elementList"] = []

        # output data to JSON for every object in the topology
        for obj in self.ObjectList + G.RouterList:
            outputDict["elementList"].append(obj.outputResultsDict())

        # output the trace as encoded if it is set on
        if G.trace == "Yes":
            # XXX discuss names on this
            jsonTRACE = {
                "_class": "manpy.Simulation",
                "id": "TraceFile",
                "results": {"trace": encodedTrace},
            }
            G.outputJSON["elementList"].append(jsonTRACE)

        # add to the output dict the eventlog
        outputDict.update({'eventlog': G.MachineEventList})
        G.FinalPositionList.sort()
        outputDict.update({'final_position': G.FinalPositionList})
        del outputDict['elementList'][0]['results']['system_time_trace'][0][0:self.numOfWIP]
        del outputDict['elementList'][0]['results']['interarrival_trace'][0][0:self.numOfWIP]

        return outputDict

# ===========================================================================
#                        the main script that is ran
# ===========================================================================
    def runStochSimulation(self, distrib_table=None, sim_time=10, n_replications=1, init_list=None, seed=1):

        # create an empty list to store all the objects in
        self.ObjectList = []
        self.RouterListC = []
        self.EntityListC = []

        # Initialize the model
        G.ObjList = []  # first we initialize the global lists as empty
        G.RouterList = []
        # We initialize the lists and assign them as attributes of the object
        self.createObjectResourcesAndCoreObjects()
        self.createObjectInterruptions()
        self.setTopology()

        # G.ObjList = self.ObjectList
        G.RouterList = self.RouterListC
        G.calculateEventList = True
        G.MachineEventList = [[], [], [], []]
        G.calculateFinalPosition = False

        start = time.time()  # start counting execution time

        # initialize the parameters of the simulation
        G.trace = "No"  # no trace, it doesn't function at the moment
        G.console = "No"  # no console, don't know how it works and what it does
        G.confidenceLevel = "0.95"  # it doesn't work at the moment
        G.seed = seed
        G.extraPropertyDict = {}  # no extra functions
        G.initializingFlag = False  # we don't use an initializing flag
        G.initializingFilename = ""

        if distrib_table is not None:
            self.initializeDistributions(distrib_table)

        # run the experiment (replications)
        for i in range(n_replications):
            self.Thisenv = simpy.Environment()  # initialize the environment
            sim_time_fin = sim_time     # read maxSimTime in each replication since it may be changed for infinite ones

            if G.RouterList:
                G.RouterList[0].isActivated = False
                G.RouterList[0].isInitialized = False

            if G.seed:
                G.Rnd = Random("%s%s" % (G.seed, i))
                G.numpyRnd.random.seed(G.seed + i)
            else:
                G.Rnd = Random()
                G.numpyRnd.random.seed()
            self.createWIP()
            if init_list:
                self.initializeWIP(init_list)
            self.initializeObjects()
            self.setupWIP(self.EntityListC)
            self.activateObjects()

            # if the simulation is ran until no more events are scheduled,
            # then we have to find the end time as the time the last entity ended.
            if G.maxSimTime == -1:
                # If someone does it for a model that has always events, then it will run forever!
                self.Thisenv.run(until=float("inf"))

                # identify from the exits what is the time that the last entity has ended.
                endList = []
                for exit in G.ExitList:
                    endList.append(exit.timeLastEntityLeft)

                # identify the time of the last event
                if float(max(endList)) != 0 and (
                    self.Thisenv.now == float("inf") or self.Thisenv.now == max(endList)
                ):  # do not let G.maxSimTime=0 so that there will be no crash
                    sim_time_fin = float(max(endList))
                else:
                    print("simulation ran for 0 time, something may have gone wrong")
                    logger.info("simulation ran for 0 time, something may have gone wrong")
            # else we simulate until the given maxSimTime
            else:
                self.Thisenv.run(until=sim_time_fin)

            # carry on the post processing operations for every object in the topology
            for element in self.ObjectList + G.ObjectResourceList + G.RouterList:
                element.postProcessing(MaxSimtime=sim_time_fin)

            # added for debugging, print the Route of the Jobs on the same G.traceFile
            PrintRoute.outputRoute()

            # output trace to excel
            if G.trace == "Yes":
                ExcelHandler.outputTrace("trace" + str(i))
                import io

                traceStringIO = io.StringIO()
                G.traceFile.save(traceStringIO)
                encodedTrace = traceStringIO.getvalue().encode("base64")
                ExcelHandler.resetTrace()

        # outputDict = {}
        # outputDict["_class"] = "manpy.Simulation"
        outputDict = {'_class': "manpy.Simulation"}
        outputDict["general"] = {}
        outputDict["general"]["_class"] = "manpy.Configuration"
        outputDict["general"]["totalExecutionTime"] = time.time() - start
        outputDict["elementList"] = []

        # output data to JSON for every object in the topology
        for obj in self.ObjectList + G.RouterList:
            outputDict["elementList"].append(obj.outputResultsDict())

        # remove the first values of the system_time and inter_arrivals equal to the number of wip
        # for i in range(n_replications):
        #     # Remove the first inter-arrival
        #     outputDict['elementList'][0]['results']['interarrival_trace'][i] = \
        #         outputDict['elementList'][0]['results']['interarrival_trace'][i][self.numOfWIP:]
        #     # Remove the first system_time
        #     outputDict['elementList'][0]['results']['system_time_trace'][i] = \
        #         outputDict['elementList'][0]['results']['system_time_trace'][i][self.numOfWIP:]


        # output the trace as encoded if it is set on
        if G.trace == "Yes":
            # XXX discuss names on this
            jsonTRACE = {
                "_class": "manpy.Simulation",
                "id": "TraceFile",
                "results": {"trace": encodedTrace},
            }
            G.outputJSON["elementList"].append(jsonTRACE)

        # Create the list of the eventlog
        outputDict.update({'eventlog': G.MachineEventList})

        return outputDict
