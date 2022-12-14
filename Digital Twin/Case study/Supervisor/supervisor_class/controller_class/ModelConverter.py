# This class converts the graph model obtained through the process mining method into a model executable by the
# simulator
import manpy.simulation.Globals as Globals


class ModelConverter:

    def __init__(self, graph_model, timed_config=None):
        # The graphModel must be given as a dict
        if not isinstance(graph_model, dict):
            raise ValueError("The graph model must be given as a dict")

        # Save the nodes and arcs as lists of dicts
        self.nodes = graph_model["nodes"]
        self.arcs = graph_model["arcs"]

        self.timed_config = timed_config

        self.unloadTime = None
        self.transportationTime = None
        self.transportationCap = 0
        self.loop_start = None
        self.queue_cap_config = None

        if self.timed_config:
            # self.loop_start = self.timed_config['start']
            # self.unloadTime = self.timed_config['unloadTime']
            # self.transportationTime = self.timed_config['transportationTime']
            # self.transportationCap = self.timed_config['transportationCap']
            self.loop_start = self.timed_config.get('start', None)
            self.unloadTime = self.timed_config.get('unloadTime', None)
            self.transportationTime = self.timed_config.get('transportationTime', None)
            self.transportationCap = self.timed_config.get('transportationCap', 0)
            self.queue_cap_config = self.timed_config.get('queueCap', None)

        # Calculate the number of machines
        self.numOfMachines = len(self.nodes)
        # Calculate the number of queues
        self.numOfQueues = len(self.arcs)
        # Calculate the number of connections, which is also two times the number of queues
        self.numOfConnections = self.numOfQueues * 2

        self.outModel = {}

    def convertModel(self):
        # This method is used to convert the graph model into a model containing Machines and Queues which is
        # executable by the simulator class

        # Initialization of the output dict which contains the model containing Machines and Queues
        self.outModel = {                # output dict variable, that will be transformed into a JSON file
            "general": {            # key "general", containing the simulation parameters
                "maxSimTime": 1,
                "numberOfReplications": 1,
                "Trace": "No",
                "seed": 1
            },
            "graph": {              # key "graph", containing "edge" and "node"
                "edge": {},         # key "edge", containing all the connections between objects
                "node": {}          # key "node", containing all the objects of the system
            }
        }

        # We create as many Machines as there are nodes
        for m in range(self.numOfMachines):     # loop through all the nodes
            machine_capacity = self.nodes[m]['capacity']
            if self.nodes[m]['stats'] == 'temp':
                # self.nodes[m]['stats']['dist'] = 'norm'
                # self.nodes[m]['stats']['params'] = [10, 20]
                self.nodes[m]['stats'] = {'dist': 'norm'}
                self.nodes[m]['stats'].update({'params': [10, 20]})
            machine_distr = self.nodes[m]['stats']['dist'] + 'SP'
            machine_distr_param = self.nodes[m]['stats']['params']
            if machine_capacity == 1:  # if the capacity of the machine is 1, we create only 1 machine
                self.outModel["graph"]["node"].update({
                    "M" + str(m + 1): {  # ID of the single machine
                        "_class": "manpy.Machine",  # specify that the object is a machine
                        "name": "Machine",
                        "processingTime": Globals.convertDistribution(machine_distr, machine_distr_param)
                    }
                })
                if self.unloadTime:
                    self.outModel["graph"]["node"]["M" + str(m + 1)].update({
                        "unloadTime": {
                            "Fixed": {
                                "mean": self.unloadTime
                            }
                        }
                    })
            else:  # if the capacity of the machine is greater than one, create parallel machines equal to capacity
                for c in range(machine_capacity):  # for cycle for machines with capacity greater than one
                    self.outModel["graph"]["node"].update({
                        "M" + str(m + 1) + "_" + str(c + 1): {  # if M1 has capacity 3, we create M1_1, M1_2, M1_3
                            "_class": "manpy.Machine",
                            "name": "Machine",
                            "processingTime": Globals.convertDistribution(machine_distr, machine_distr_param)
                        }
                    })
        # If we are using timed queues, we must create the transport machines
        if self.transportationCap:
            for q in range(self.numOfQueues):
                for c in range(self.transportationCap):
                    self.outModel["graph"]["node"].update({
                        "QM" + str(q + 1) + "_" + str(c + 1): {
                            "_class": "manpy.Machine",
                            "name": "Transport",
                            "capacity": 1,
                            "processingTime": {
                                "Fixed": {
                                    "mean": self.transportationTime
                                }
                            }
                        }
                    })

        # We create as many Queues as there are arcs
        for q in range(self.numOfQueues):  # cycle for writing the queues with all their parameters
            self.outModel["graph"]["node"].update({
                "Q" + str(q + 1): {  # ID of the single queue
                    "_class": "manpy.Queue",  # specify that the object is a queue
                    "capacity": self.arcs[q]['capacity'] - self.transportationCap,  # obtain the capacity of the queue from the input file
                    "name": "Queue",
                    "wip": []
                }
            })

        if self.timed_config:
            for m in range(self.numOfMachines):
                precMachID = self.arcs[m]['arc'][0]
                succMachID = self.arcs[m]['arc'][1]
                for c in range(self.transportationCap):
                    self.outModel["graph"]["edge"].update({
                        str(self.transportationCap*m + c + 1): {
                            "_class": "manpy.Edge",
                            "destination": "QM" + str(succMachID) + "_" + str(c+1),  # picks the current queue
                            "source": "M" + str(precMachID)  # picks the incoming machine
                        }
                    })
            for m in range(self.numOfMachines):
                succMachID = self.arcs[m]['arc'][1]
                for c in range(self.transportationCap):
                    self.outModel["graph"]["edge"].update({
                        str(self.transportationCap*self.numOfMachines + self.transportationCap*m + c + 1): {
                            "_class": "manpy.Edge",
                            "destination": "Q" + str(succMachID),  # picks the current queue
                            "source": "QM" + str(succMachID) + "_" + str(c+1)  # picks the incoming machine
                        }
                    })
            for m in range(self.numOfMachines):
                precMachID = self.arcs[m]['arc'][0]
                self.outModel["graph"]["edge"].update({
                    str(self.transportationCap * self.numOfMachines * 2 + 1 + m): {
                        "_class": "manpy.Edge",
                        "destination": "M" + str(precMachID),  # picks the current queue
                        "source": "Q" + str(precMachID) # picks the incoming machine
                    }
                })

        else:
            # We create the connections between the objects
            for e in range(0, self.numOfConnections, 2):  # cycle for writing all the edges
                precMachID = self.arcs[int(e / 2)]['arc'][0]  # id of the predecessor machine
                succMachID = self.arcs[int(e / 2)]['arc'][1]  # id of the successor machine
                precMachCap = self.nodes[precMachID - 1]["capacity"]  # capacity of the predecessor machine
                succMachCap = self.nodes[succMachID - 1]["capacity"]  # capacity of the successor machine
                if precMachCap == 1:  # if the predecessor machine has capacity equal to 1, we create only one arc
                    self.outModel["graph"]["edge"].update({  # for every queue we have an incoming edge
                        str(e + 1): {
                            "_class": "manpy.Edge",
                            "destination": "Q" + str(int(e / 2) + 1),  # picks the current queue
                            "source": "M" + str(precMachID)  # picks the incoming machine
                        }
                    })
                else:  # if the predecessor machine has capacity greater than 1, we create as many edges as capacity
                    for c in range(precMachCap):
                        self.outModel["graph"]["edge"].update({
                            str(e + 1) + "_" + str(c + 1): {
                                "_class": "manpy.Edge",
                                "destination": "Q" + str(int(e / 2) + 1),
                                "source": "M" + str(precMachID) + "_" + str(c + 1)
                            }
                        })

                if succMachCap == 1:
                    self.outModel["graph"]["edge"].update({  # for every queue we have an outgoing edge
                        str(e + 2): {
                            "_class": "manpy.Edge",
                            "destination": "M" + str(succMachID),  # picks the outgoing machine
                            "source": "Q" + str(int(e / 2) + 1)  # picks the current queue
                        }
                    })
                else:
                    for c in range(succMachCap):
                        self.outModel["graph"]["edge"].update({
                            str(e + 2) + "_" + str(c + 1): {
                                "_class": "manpy.Edge",
                                "destination": "M" + str(succMachID) + "_" + str(c + 1),
                                "source": "Q" + str(int(e / 2) + 1)
                            }
                        })
                        
        # Create the Source and Exit objects
        source_idx = 1
        exit_idx = 1
        for node in self.nodes:
            # check if the node has no predecessor
            if not node['predecessors']:
                self.outModel["graph"]["node"].update({
                    "S" + str(source_idx): {
                        "_class": "manpy.Source",
                        "entity": "manpy.Part",
                        "id": "S1",
                        "interArrivalTime": {
                            "Fixed": {          # TODO temp value
                                "mean": 3.55
                            }
                        },
                        "name": "Source"
                    }
                })
                self.outModel["graph"]["edge"].update({
                    "S_" + str(source_idx): {
                        "_class": "manpy.Edge",
                        "destination": "M" + str(node['activity']),
                        "source": "S" + str(source_idx)
                    }
                })
                source_idx += 1

            # check if the node has no successor
            if not node['successors']:
                self.outModel["graph"]["node"].update({
                    "E" + str(exit_idx): {
                        "_class": "manpy.Exit",
                        "name": "Exit"
                    }
                })
                self.outModel["graph"]["edge"].update({
                    "E_" + str(exit_idx): {
                        "_class": "manpy.Edge",
                        "destination": "E" + str(exit_idx),
                        "source": "M" + str(node['activity'])
                    }
                })
                exit_idx += 1

        # If closed loop, select the starting machine, which is given in the configuration input
        if self.loop_start:
            self.outModel['graph']['node'][self.loop_start].update({"gatherSysTime": 1, "gatherIntArr": 1})

        # If we want we can select the capacity of the queue manually from the configuration input
        if self.queue_cap_config:
            for q, c in self.queue_cap_config.items():
                self.outModel['graph']['node'][q]['capacity'] = c - self.transportationCap
        return self.outModel

