# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 11:39:04 2020

@author: giova
"""

import itertools


from MSM.other import getmenodesdata
from MSM.msmlib import unique
from MSM.msmlib import initialsandfinals
from MSM.modelred import givemethenodes




def topetri(model, unique_list):
        
    capacity_data = model['arcs']
    
    #arcs_list = [(1,2), (1,3), (1,4), (2,5), (3, 5), (4, 5)]
    arcs_list = [a['arc'] for a in capacity_data]
    transitions = givemethenodes(arcs_list)
    
    places_init = finddominantarcs(arcs_list)
    
    places = []
    new_arcs = []
    
    incoming_edges = []
    outgoing_edges = []
    
    for p in places_init:
        
        places.append(  'P'+str(  places_init.index(p) +1  )  )
        
        for element in p[0]:
            new_arcs.append( ( element, places[-1]  ) )
            outgoing_edges.append( ( element, places[-1]  )  )
            
        for element in p[1]:
            new_arcs.append( ( places[-1], element  ) )
            incoming_edges.append( ( places[-1], element  )   )
    
    # come aggiungere capacita tra due transizioni
    
    capacity_places = [] 
    capacity_places_cap = [] 
    capacity_arcs = []
    
    
    for arc in arcs_list:
        
        # aggiungo un capacity place in corrispondenza di ogni arco con capacita finita
        capacity_places.append('C'+str(len (capacity_places) + 1 ))
        
        capacity_arcs.append(  ( arc[1],   capacity_places[-1]   )    )
        outgoing_edges.append(  ( arc[1],   capacity_places[-1]   )   )
        
        capacity_arcs.append(  (  capacity_places[-1], arc[0]   )    )
        incoming_edges.append( (  capacity_places[-1], arc[0]   )    )
        
        capacity_places_cap.append(  {'place' : capacity_places[-1] , 'capacity': next(a['capacity'] for a in capacity_data if a['arc'] == arc)   }    )
    
    
    initials, finals = initialsandfinals(unique_list)
    
    places.append(  'S'  ) # add source place
    places.append(  'F'  ) # add sink place
    
    support_arcs = []
    support_arcs.append( ( 'S', initials[0]  ) ) # add arc from source to first activity
    incoming_edges.append(  ( 'S', initials[0]  )      )
    
    support_arcs.append( ( finals[0], 'F' ) )   # add arc from last activity to sink
    outgoing_edges.append( ( finals[0], 'F' ) )
    
    
    
    arcs_global = new_arcs + capacity_arcs + support_arcs
    places_global = places + capacity_places
    
    
    return places_global, transitions, arcs_global, incoming_edges, outgoing_edges

#
#from msm_plots import print_graph
#print_graph(arcs_global)




#######################################################################
# test petri net conversion to ERG
######################################################################

places = ['P1', 'P2', 'S', 'F']
transitions = ['2', '3', '1']
incoming_edges = [('P1', '3'), ('P2', '2'), ('S', '1')]
outgoing_edges =  [('2', 'P1'), ('1', 'P2'), ('3', 'F')]


def petri_to_erg(places, transitions, incoming_edges, outgoing_edges):
    
    verts= []
    edges = []
    
    for t in transitions:
        
        # all incoming edges to a PN transition become a single start transition vertex
    
        verts.append({'name': 'start-' + str(t) , 'PN_edges': [i for i in incoming_edges if i[1] == t] })   
    
    # all outgoing edges from a PN transition become a single end transition vertex
    
        verts.append({'name': 'end-' + str(t) , 'PN_edges': [i for i in outgoing_edges if i[0] == t] })   
    
    # a transition vertex will become an unconditional edge with an edge delay equal to the transition firing time
        edges.append( { 'arc': ( 'start-' + str(t) ,   'end-' + str(t) ) , 'cond': None, 'delay': None    })
    #todo complete with search of transition firing time
        
    
    places_new = places.copy()    
        
    # Remove S and F places for next mapping analysis    
    if set(['S', 'F']).issubset(set(places)):
        places_new.remove('S')
        places_new.remove('F')
        
    # a place vertex will become a zero delay edge conditioned by the token counts of all places preceding the next transition
    for p in places_new:
    
        after = [ie for ie in incoming_edges if ie[0] == p  ]  # find the transition after this place
        before = [oe for oe in outgoing_edges if oe[1] == p ]  # find the transition before this place
             
    #    transform to subset check
        start = [ v['name'] for v in verts if all(b in v['PN_edges'] for b in before  ) ]   # find the corresponding vertex name before this place
        end =  [  v['name'] for v in verts if all(a in  v['PN_edges'] for a in after ) ]    # find the corresponding vertex name after this place
        
        if len(start) == 1:
            start = start[0]
            
        if len(end) == 1:
            end = end[0]
        
        # find  all places preceding the next transition
        conditions = []
    #    find which PN edges are associated with the end transition
        pnelist =  next(v['PN_edges'] for v in verts if (end == v['name'] ))
    #   check if those edges are incoming
        for pne in pnelist:
            if pne in incoming_edges:
                conditions.append(pne[0])
        
        #todo add condition (token size of place)
        edges.append( { 'arc': ( start, end) , 'cond': conditions, 'delay': None    })
        
    return verts, edges
 


def finddominantarcs(arcs):
    
    """
    Function that takes as input a list of arcs of the type 
    
    (  start, end )
    
    returns the list of dominating arcs, defined as arcs for which no other arcs can contain them 
    
    example:
        
        #arcs = [(1,2), (1,3), (1,4), (2,5), (3, 5), (4, 5)]
    
        dominants_global =  [([1], [2, 3, 4]), ([2, 3, 4], [5])]
           
    """
    
    nodesdata = getmenodesdata(arcs)
    
    # forward search
    forward = []
    backward = [] 
    
    for node in nodesdata:
        if len( node['successors']) > 0:
            forward.append( (   [node['node']] ,   node['successors'] )  )
    
        if len( node['predecessors']) > 0:
            backward.append( (  node['predecessors']  ,  [ node['node'] ] )  )
    
    complete = forward + backward
    
    start = []
    finish = []
    
    for element in  complete:
        start.append(element[0])
        finish.append(element[1])
    
    start_u = unique(start)
    finish_u = unique(finish)
    
    
    dominants_temp = []
    
    # archi con stesso nodo iniziale
    for start in start_u:
    
        d_temp = dominiziale(     [ element for element in complete if element[0] == start ]        )
        dominants_temp = dominants_temp + d_temp
    
    
    dominants_global = []
    
    # archi con stesso nodo finale
    for finish in finish_u:
    
        d_temp = domfinale(     [ element for element in dominants_temp if element[1] == finish ]        )
        dominants_global = dominants_global + d_temp
    
    
    return dominants_global


    

def domfinale(check):
    
    """
    Function that takes as input a list of arcs of the type 
    
    (  [list of start nodes] , [list of end nodes]   )
    
    where [list of end nodes is the same for all the elements of the list
    
    returns the list of dominating arcs, defined as arcs for which no other arcs can contain them 
    
    example:
        
        arcs:   [1,2]  --> 3
                [2]  --> 3
                [1]  --> 3
    
        returns: [
                    ( [1,2], [3] )  
                  ]
        
           
    """
    
    dominants = []
    
    if len(check) == 1:
        dominants = dominants + check
        return unique(dominants)
    
    else:
    
        for a, b in itertools.combinations(check, 2):
            
    #        aoverb = False
    #        bovera = False
            
            if set(a[0]).issubset(set(b[0])):
                # dominand is b
                dominants.append(b)
    #            bovera = True
                
            if set(b[0]).issubset(set(a[0])):
                # dominand is a
                dominants.append(a)
    #            aoverb = True
    #            
    #        if aoverb == False and bovera == False:
    #            dominants.append(a)
    #            dominants.append(b)
        
        return unique(dominants)


def dominiziale(check):
    
    """
    Function that takes as input a list of arcs of the type 
    
    (  [list of start nodes] , [list of end nodes]   )
    
    where [list of start nodes] is the same for all the elements of the list
    
    returns the list of dominating arcs, defined as arcs for which no other arcs can contain them 
    
    example:
        
        arcs:   [1]  --> [2, 3]
                [1]  --> [3]
                [1]  --> [2]
    
        returns: [
                    ( [1], [2,3] )  
                 ]
           
    """
    
    
    dominants = []
    
    if len(check) == 1:
        dominants = dominants + check
        return unique(dominants)
    
    else:
    
        for a, b in itertools.combinations(check, 2):
            
    #        aoverb = False
    #        bovera = False
            
            if set(a[1]).issubset(set(b[1])):
                # dominand is b
                dominants.append(b)
    #             bovera = True
            if set(b[1]).issubset(set(a[1])):
                # dominand is a
                dominants.append(a)
    #            aoverb = True
                
    #        if aoverb == False and bovera == False:
    #            dominants.append(a)
    #            dominants.append(b)
    
        return unique(dominants)


