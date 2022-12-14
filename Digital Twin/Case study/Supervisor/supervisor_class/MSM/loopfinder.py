# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 18:14:01 2020

@author: giova
"""


import networkx as nx



def firstloopfinder(model):
    
    """
    Function that takes as input the list of unique traces and returns the list of loops in the graph that gemerated those traces
    No statistical counters here
    PROBLEMS:
        - finds only one loop per trace!
        - based on only the first duplicate event found
        
    """
    
    
             
    arcs_list =  [ m['arc'] for m in model['arcs']  ]  
    G = nx.DiGraph(arcs_list)       
    
    try:
            cycle = nx.find_cycle(G)
            return cycle
    except: 
        return []
        

def loopsfinder(model):
    """
    FROM:
        https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.cycles.simple_cycles.html#networkx.algorithms.cycles.simple_cycles
    Find simple cycles (elementary circuits) of a directed graph.
    Returns a list of lists of nodes
    if no cycles are found returns empty list
    """
    
    arcs_list =  [ m['arc'] for m in model['arcs']  ]  
    G = nx.DiGraph(arcs_list)  
    return list(nx.simple_cycles(G))

    
#def loopsfinder(arcs_list):
#    """
#    FROM:
#        https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.cycles.simple_cycles.html#networkx.algorithms.cycles.simple_cycles
#    Find simple cycles (elementary circuits) of a directed graph.
#    Returns a list of lists of nodes
#    if no cycles are found returns empty list
#    """
#    
##    arcs_list =  [ m['arc'] for m in model['arcs']  ]  
#    G = nx.DiGraph(arcs_list)  
#    return list(nx.simple_cycles(G))


    
    
    
#    unique_list = [[1, 3, 5], [1, 4, 5], [1, 2, 5], [1,2,1,3,5]]
#    loops = []
#    
#    
#    for k in range(len(unique_list)):
#        
#        seen = {}
#        dupes = []
#    
#        for x in unique_list[k]:
#            if x not in seen:
#                seen[x] = 1
#            else:
#                if seen[x] == 1:
#                    dupes.append(x)
#                seen[x] += 1
#        
#        if len(dupes) == 0:
#            continue
#        
#        indexes = []
#        i = 0
#        
#    
#        for element in unique_list[k]:
#            if element == dupes[0]:
#                indexes.append(i)
#            i = i+1
#            
#        loops.append(unique_list[k][indexes[0]: indexes[1]])
#        
#        
#        return loops
    


    
        


