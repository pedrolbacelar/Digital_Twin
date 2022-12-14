# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 15:49:42 2020

@author: giova
"""
import numpy as np
     
############################################################################################################
# CALCOLO SCORE (R1,R2, R3..)
############################################################################################################

# R1 Capacity
#arcs
def r1arcs(model):
    
    if model is not None:
        somma = 0
        for arc in model['arcs']:
            somma += arc['capacity'] 
            
        return somma  
    
    else:
        return 0
#nodes
def r1nodes(model):
    
    if model is not None:
        somma = 0
        for node in model['nodes']:
            somma += node['capacity'] 
            
        return somma  
    
    else:
        return 0


def r1(model, captot_nodes = 1, captot_arcs = 1, w_n = 0.5, w_a = 0.5):
    
    """
    
    r1 is the function that evaluates the capacity score of the current model 
    
    NB model must be in the form 
        model = { 'nodes':  clusters_data, 'arcs' : capacity_data }

    the score is maximum 1 in any case (!!! even error scenario (sum > 1) will return 1 !!!)

    """
    
    
    if (w_n * r1nodes(model)/captot_nodes  + w_a * r1arcs(model)/ captot_arcs )> 1:
        return 1
    else:
        return w_n * r1nodes(model)/captot_nodes  + w_a * r1arcs(model)/ captot_arcs

    





# R2a  - on nodes     
def r2nodes(model):
    
#    sommatot= sum([acd['frequency'] for acd in model['nodes']])  
    ratio = 0
    for node in model['nodes']:
        ratio += node['contemp']/node['frequency']
                
    return (1 - ratio)

# R2a  - on nodes     
def r2arcs(model):
    
#    sommatot= sum([acd['frequency'] for acd in model['nodes']])  
    ratio = 0
    for arc in model['arcs']:
        ratio += arc['contemp']/arc['frequency']
                
    return (1 - ratio)


def r2(model):
#     todo finish r2 nodes and arcs --> need to solve case with aggregated clusters
    return 0.5 * r2nodes(model) + 0.5 * r2arcs(model)



# R3 LOOPS                  
from MSM.loopfinder import loopsfinder
# dipende se uso model come modello base allora devo mettere loops del modello "nuovo" (quindi calcolo a partire da lista nodi e archi)
def r3(model, unique_list):
#    if len(loopsfinder(model)) == 0:
#        return 0
#    else:
    if len(loopsfinder(model))/ len(unique_list) > 1 : # TODO cambiare dopo!!! deve diventare quella sul paper
           return 1
    else:
        return len(loopsfinder(model))/ len(unique_list)
    
    
    
    
# R4 BRANCHING 

def r4(model, incoming_init = 1, outgoing_init = 1, w_i = 0.5, w_o = 0.5):

    # SKIP ERRORS
    if incoming_init == 0:
        incoming_init = 1
        
    if outgoing_init == 0:
        outgoing_init = 1
    
    incoming = 0
    outgoing = 0 
    
    for node in model['nodes']: 
        incoming += len(node['predecessors'])
        outgoing += len(node['successors'])    

    
    return w_i * incoming/incoming_init + w_o * outgoing/outgoing_init
    

# R5 CORRELATION         
def r5():
#     TODO check codice di siamak
    return 0
    

def r6( model, ifreq_nodes = 1, ifreq_arcs = 1, y6n = 0.5, y6a = 0.5):
    
    freq_nodes = sum([n['frequency'] for n in model['nodes']])
    freq_arcs = sum([a['frequency'] for a in model['arcs']])
    
    return y6n * freq_nodes/ifreq_nodes + y6a * freq_arcs/ifreq_arcs
    


    
def score_calc(model, captot_nodes, captot_arcs, ifreq_nodes, ifreq_arcs, y6n, y6a , w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o, ws = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2]):

    s1 = r1(model, captot_nodes, captot_arcs, w_n, w_a)
    s2 = r2(model)
    s3 = r3(model, unique_list)
    s4 = r4(model, incoming_init, outgoing_init, w_i, w_o)
    s5 = r5()
    s6 = r6( model, ifreq_nodes, ifreq_arcs, y6n, y6a)

    return ws[0]*s1 + ws[1]*s2 + ws[2]*s3 + ws[3]*s4 + ws[4]*s5 + ws[5]*s6




