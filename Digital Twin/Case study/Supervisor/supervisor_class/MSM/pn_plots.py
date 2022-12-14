# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:20:59 2020

@author: giova
"""

###########################################################################
# PETRI NET VISUALIZER (+ EXTRA FUNCTION FROM PM4py)
#http://pm4py.pads.rwth-aachen.de/documentation/petri-net-management/
###########################################################################

from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri import utils


import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/graphviz-2.38/release/bin'

# create a PN
net = PetriNet("new_petri_net")



# DEFINE PLACES
# creating source, p_1 and sink place
source = PetriNet.Place("source")
sink = PetriNet.Place("sink")
p_1 = PetriNet.Place("p_1")


# ADD PLACES
net.places.add(source)
net.places.add(sink)
net.places.add(p_1)

# DEFINE TRANSITIONS
t_1 = PetriNet.Transition("name_1", "label_1")
t_2 = PetriNet.Transition("name_2", "label_2")


# ADD TRANSITIONS
net.transitions.add(t_1)
net.transitions.add(t_2)

# ADD ARCS
# devo definire archi su matrice poi pesco gli oggetti dalla matrice

utils.add_arc_from_to(source, t_1, net)
utils.add_arc_from_to(t_1, p_1, net)
utils.add_arc_from_to(p_1, t_2, net)
utils.add_arc_from_to(t_2, sink, net)


# DEFINE INITIAL MARKING
initial_marking = Marking()
initial_marking[source] = 1
final_marking = Marking()
final_marking[sink] = 1




from pm4py.objects.petri.exporter import pnml as pnml_exporter

pnml_exporter.export_net(net, initial_marking, "createdPetriNet1.pnml", final_marking=final_marking)



from pm4py.visualization.petrinet import factory as pn_vis_factory

gviz = pn_vis_factory.apply(net, initial_marking, final_marking)
pn_vis_factory.view(gviz)

# TODO SAVING PNG OF THE NET

###########################################################################
# TRIAL CODE from: http://pm4py.pads.rwth-aachen.de/documentation/petri-net-management/
###########################################################################
#
#
## create a PN
#net = PetriNet("new_petri_net")
#
#
#
## DEFINE PLACES
## creating source, p_1 and sink place
#source = PetriNet.Place("source")
#sink = PetriNet.Place("sink")
#p_1 = PetriNet.Place("p_1")
#
#
## ADD PLACES
#net.places.add(source)
#net.places.add(sink)
#net.places.add(p_1)
#
## DEFINE TRANSITIONS
#t_1 = PetriNet.Transition("name_1", "label_1")
#t_2 = PetriNet.Transition("name_2", "label_2")
#
#
## ADD TRANSITIONS
#net.transitions.add(t_1)
#net.transitions.add(t_2)
#
## ADD ARCS
#utils.add_arc_from_to(source, t_1, net)
#utils.add_arc_from_to(t_1, p_1, net)
#utils.add_arc_from_to(p_1, t_2, net)
#utils.add_arc_from_to(t_2, sink, net)
#
#
## DEFINE INITIAL MARKING
#initial_marking = Marking()
#initial_marking[source] = 1
#final_marking = Marking()
#final_marking[sink] = 1
#
#
#
#
#from pm4py.objects.petri.exporter import pnml as pnml_exporter
#
#pnml_exporter.export_net(net, initial_marking, "createdPetriNet1.pnml", final_marking=final_marking)
#
#
#
#from pm4py.visualization.petrinet import factory as pn_vis_factory
#
#gviz = pn_vis_factory.apply(net, initial_marking, final_marking)
#pn_vis_factory.view(gviz)
    
