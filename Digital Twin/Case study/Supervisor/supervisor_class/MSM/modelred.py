# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 14:49:35 2020

@author: giova
"""

from operator import itemgetter
from copy import deepcopy
import time
import numpy as np
from warnings import warn


from MSM.other import getmenodesdata, findinvolvedarcs, findinandoutarcs, model_dim



############################################################################################################
# TABU SEARCH FOR MODEL REDUCTION
############################################################################################################    

# function call example
from MSM.modelscores import score_calc   
#score_calc(model, captot_nodes, captot_arcs, 0.5, 0.5,  unique_list, incoming_init, outgoing_init, 0.5, 0.5, ws = [0.2, 0.2, 0.2, 0.2, 0.2])


############################################################################################################
# LOCAL SEARCH (TO BE TRASFERED)
############################################################################################################    


#INITIAL PARAMETERS FOR MODEL SCORE CALCULATION
# calcolo capacita totale del sistema (mi serve per calc score R1)


#neighbours_prova = find_neighbours(arcs_list)

def local_search(model, unique_list, config, pen = 0):
    
#    unpacking weights from config
    w_n = config["modelred"]["weights"]["y1n"]
    w_a = config["modelred"]["weights"]["y1a"]
    w_i = config["modelred"]["weights"]["y4in"]
    w_o = config["modelred"]["weights"]["y4out"]
    ws = config["modelred"]["weights"]["ws"]
    y6n = config["modelred"]["weights"]["y6n"]
    y6a = config["modelred"]["weights"]["y6a"]

#    INITIAL VALUES (OMEGA_0)
    captot_nodes = 0
    for element in model['nodes']:
        captot_nodes += element['capacity']
    
    captot_arcs = 0
    for element in model['arcs']:
        captot_arcs += element['capacity']
        
    incoming_init = 0
    outgoing_init = 0 
    
    for node in model['nodes']: 
        incoming_init += len(node['predecessors'])
        outgoing_init += len(node['successors'])    
        
    ifreq_nodes = sum([n['frequency'] for n in model['nodes']])
    ifreq_arcs = sum([a['frequency'] for a in model['arcs']])

    
    # number of neighbours found by aggregating and reducing model, respectively
    n_aggregate = config['modelred']['n_aggregate']
    n_reducing = config['modelred']['n_reducing']
    
    neighbours_type = []  # lista con 'a' ed 'r' per tipo di neighbour
    for i in range(n_aggregate):
        neighbours_type.append('a')
    for i in range(n_reducing):
        neighbours_type.append('r')
        
    current_solution = deepcopy(model)
    score_of_current_solution = score_calc(model, captot_nodes, captot_arcs, ifreq_nodes, ifreq_arcs, y6n, y6a , w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o,ws)
#    score_calc(model, captot_nodes, captot_arcs, w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o, ws)    

    count = 1
    condition = True
    
    min_n_nodes = 2
    max_n_nodes = config['modelred']['desired_size']
#    MinReductionConditionAchieved = False  # True if at least one solution has been found with maximum nr of nodes (reduction constraint)
    max_iters = config['modelred']['max_iters']
    
    start = time.time()
    finish = time.time()
    
    iter_record = []
    iter_record.append( {'iter': 0, 'solution': current_solution , 'score': score_of_current_solution,  'type': 'init', 'time' : finish -start }  )

    if model_dim(model) == config['modelred']['desired_size']:
        return iter_record

    while condition:   
        
        neighbours = neighbours_aggregate(current_solution, config, n_aggregate) + neighbours_reducing(current_solution, config, n_reducing)
             
        if len(neighbours) == 0:
            warn("NO MORE NEIGHBOURS CAN BE GENERATED")
            finish = time.time()
            condition = False
            continue
        
        # ASSIGN PENALTY TO THE INDEXES OF SCORES FROM AGGREGATION MODELS
        pen_ind = [index for index, value in enumerate(neighbours_type) if value == 'a']

        scores = []
        # for each neighbour, calculate score
        for nb in neighbours:
            if neighbours.index(nb) in pen_ind:
                scores.append( score_calc(nb, captot_nodes, captot_arcs, ifreq_nodes, ifreq_arcs, y6n, y6a , w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o, ws)   )
            else:
                scores.append((1-pen)* score_calc(nb, captot_nodes, captot_arcs, ifreq_nodes, ifreq_arcs, y6n, y6a , w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o, ws))

        #vettore degli indici degli score
        scores_ordering = list(np.argsort(scores))
        scores_ordering.reverse() 
        
        scores.sort(reverse = True)
        
        j  = 0
#        index_of_best_neighbour_solution = scores_ordering[j]    #index of the local solution to be analysed 
        
#    #    candidate solution 
#    #    neighbours[scores_ordering[j] ]
#        FoundTabu = True
#        while FoundTabu:
#            if neighbours[scores_ordering[j] ] in tabu_list:
#                j = j + 1
#            else:
#                FoundTabu = False
#            if j == len(scores_ordering):
#                print('ALL NEIGHBORS IN TABU LIST: STOP')
#    #            save last perf and close
#                break
            
            
        #check if best score ever can be updated
#        if scores[j] > best_score_ever:
#            best_score_ever = scores[j]
##            best_solution_ever =   dict( neighbours[ scores_ordering[j] ] ) 
#    
#        #check if local score ever can be updated
#        if scores[j] > best_local_score:
#            best_local_score = scores[j]
#            best_local_solution =   dict( neighbours[ scores_ordering[j] ] ) 
#        
#    #   "put the selected solution in tabu list" (shall be the move?)
#        tabu_list.append(  neighbours[ scores_ordering[j] ]    )
#    #    check if needed to reduce tabu list (proxy TS)
#        if len(tabu_list) >= tabu_list_max_size:
#            tabu_list.pop(0)
        
        #    SAVE INFO ABOUT CURRENT BEST SOLUTION IN THIS ITERATION
        finish = time.time()
        current_solution = dict(neighbours[ scores_ordering[j] ])
#        iter_record.append( (count, neighbours[ scores_ordering[j] ] ,  scores[j],  neighbours_type[scores_ordering[j]]   )      )
        iter_record.append( {'iter': count, 'solution': current_solution , 'score': scores[j],  'type': neighbours_type[scores_ordering[j]], 'time' : finish -start }  )

        if count >= max_iters:
            condition = False
            finish = time.time()
            print('REACHED COMPUTATION LIMIT')
            
        elif len(current_solution['nodes']) <= min_n_nodes:
            condition = False
            finish = time.time()
            print('REACHED MINIMUM MODEL SIZE')
    
#    todo check
        elif len(current_solution['nodes']) <= max_n_nodes:
    #        NB <= e non = perche potrebbe togliere piu nodi per dipendenze implicite
#            MinReductionConditionAchieved = True
            condition = False
            finish = time.time()
            print('REACHED DESIRED MODEL SIZE')
    
    #   UPDATE ITERATIONS COUNTER
        count += 1
        
    #    SET CURRENT SOLUTION (NEIGHBOURS CALCULATED FROM HERE)
        
    
    
    # SAVE RESULTS OF TEST
#    test_results = {'initial_model': model, 'final_model':current_solution,   'iter_record' : iter_record, 'tabu_time' : finish - start }

    return iter_record







############################################################################################################
# FUNCTIONS FOR TABU
############################################################################################################    


def neighbours_aggregate(model, config, nn = 2): 
    
    if nn == 0:
        return []

    clusters_data = deepcopy(model['nodes'])
    capacity_data = deepcopy(model['arcs'])

    try:
        capacity_data.sort(key=itemgetter(config['modelred']['proxy']))
        if config['modelred']['proxy'] == 'contemp':
            capacity_data.reverse()
            
    except Exception as e: 
        print(e)
        warn("COULD NOT FOLLOW PROXY, AGGREGATING AS-IS!!!")
    
    # list of arcs to aggregate from
    arcs_list = [  cd['arc'] for cd in  capacity_data[:nn] ]
    
    # cluster merging
    neighbours_list = []
    
    if nn > len(arcs_list):
        warn('WARNING: NEIGHBOURS ASKED: '+ str(nn) + '> NUMBER OF ARCS: ' + str(len(clusters_data)) + ', USING MAXIMUM NUMBER OF NODES')
        nn = len(arcs_list)
        
    for arc in arcs_list:
    
        clusters_data_new, cluster_merged = aggregate_nodes(model, [arc[0],arc[1]])
        capacity_data_new =  aggregate_arcs(model, [arc[0],arc[1]], cluster_merged)
        
        #  TODO CHECK  update predecessors successors list: SU TUTTE LE ATTIVITA!
        clusters_data_fixed = fixpredsuccs(capacity_data_new, clusters_data_new)
        
        new_model = { 'nodes':   clusters_data_fixed  , 'arcs' : capacity_data_new}
        neighbours_list.append( new_model )
        
    return neighbours_list



# STEP 1 - MERGE NODES
def aggregate_nodes(model, list_of_nodes):

    
    clusters_data = deepcopy(model['nodes'])
    capacity_data = deepcopy(model['arcs'])
    
    c1 = list_of_nodes[0]
    c2 = list_of_nodes[1]
    
    print('AGGREGATING NODES: ' +str(c1) +', '+str(c2) )
    
    cluster_merged = dict()
    # add one cluster (numero univoco)
    cluster_merged['cluster'] =  max([cluster['cluster'] for cluster in clusters_data]) + 1
    
    # merge activities properties of 2 clusters (merging is between 2 clusters!)
    # esempio unisco clusters 1 e 2
    
    # prendo dati dei due cluster da unire
    cluster1 = next(cluster for cluster in clusters_data if cluster['cluster'] == c1)
    cluster2 = next(cluster for cluster in clusters_data if cluster['cluster'] == c2)
    
    # activities are merged in a list (if there is no activity list yet, it is created)
    if 'activity' not in cluster_merged.keys():
      cluster_merged['activity'] = []  
    
    if isinstance(cluster1['activity'], list):
        cluster_merged['activity'].extend(cluster1['activity'])
    else:
        cluster_merged['activity'].append(cluster1['activity'])
        
    if isinstance(cluster2['activity'], list):
        cluster_merged['activity'].extend(cluster2['activity'])
    else:
        cluster_merged['activity'].append(cluster2['activity'])
        
    cluster_merged['predecessors'] = list(set(cluster1['predecessors'] + cluster2['predecessors']))
    cluster_merged['successors'] = list(set(cluster1['successors'] + cluster2['successors']))
    
    # INHERITANCE: frequency
    cluster_merged['frequency'] = max([cluster1['frequency'], cluster2['frequency']])
    
    # capacity
    # find if there is an arc between the two activities merging ( can only be either A > B or B > A)
    involvedarcs = findinvolvedarcs(c1, c2, list(item['arc'] for item in capacity_data))
    
    capsum = 0
    conte = []
     
    # INHERITANCE: CAPACITY and CONTEMP
    # Calculate capacity of involved arcs:
    if len(involvedarcs) > 0:
#        capsum = 0
        for arc in involvedarcs:
#            arc = (c1,c2)
            capsum += next(cd['capacity'] for cd in capacity_data if cd['arc'] == arc)
            conte.append( next(cd['contemp'] for cd in capacity_data if cd['arc'] == arc))

            
    cluster_merged['capacity'] = cluster1['capacity'] + cluster2['capacity'] + capsum
    
#    !!! ATTENTION MODIFIED RECENTLY INHERITANCE OF CONTEMPS!
    cluster_merged['contemp'] = min( [cluster1['contemp'], cluster2['contemp']] + conte) 
    
    #check: in predecessor e successor non devono esserci ne una ne l'altra attivita che ho unito, se ci sono tolgo
    for act in cluster_merged['activity']:
        if act in cluster_merged['predecessors']:
            cluster_merged['predecessors'].remove(act)
        if act in cluster_merged['successors']:
            cluster_merged['successors'].remove(act)
    
    # new cluster list
    clusters_data_new = clusters_data.copy()
    clusters_data_new.remove(cluster1)
    clusters_data_new.remove(cluster2)
    clusters_data_new.append(cluster_merged)
    
    return clusters_data_new, cluster_merged



# STEP 2 - MERGE ARCS
def aggregate_arcs(model, list_of_nodes, cluster_merged):
# correct data about arcs
    
#    clusters_data = model['nodes'].copy()
#    clusters_data = deepcopy(model['nodes'])
    capacity_data = deepcopy(model['arcs'])
    
    c1 = list_of_nodes[0]
    c2 = list_of_nodes[1]
        
    print('AGGREGATING ARCS TO AND FROM: ' +str(c1) +', '+str(c2) )
    
    incoming, outgoing = findinandoutarcs(c1,c2, list(item['arc'] for item in capacity_data))
    
    capacity_data_new = deepcopy(capacity_data)
    # remove arc (c1, c2) or (c2, c1) if present
    if  ((c1, c2) in  list(item['arc'] for item in capacity_data_new)) |  ((c2, c1) in  list(item['arc'] for item in capacity_data_new)) :
        capacity_data_new.remove(next(cdn  for cdn in capacity_data_new if  ((cdn['arc'] == (c1,c2)) |  (cdn['arc'] == (c2,c1))  )   ) )
    
    
    # change name of modified arcs
    for arcin in incoming:
        next(cdn for cdn in capacity_data_new if  cdn['arc'] == arcin )['arc'] = (  arcin[0]  , cluster_merged['cluster'])
    
    for arcout in outgoing:
        next(cdn for cdn in capacity_data_new if  cdn['arc'] == arcout )['arc'] = (  cluster_merged['cluster'], arcout[1]  )
    
    return capacity_data_new


# STEP 3 - FIX PREDECESSORS AND SUCCESSORS
    
def fixpredsuccs(capacity_data_new, clusters_data_new):
    
    #capacity_data_new = na[0]['arcs']
    
    clusters_data_fixed =  deepcopy(clusters_data_new)
    
    nd = getmenodesdata([a['arc'] for a in capacity_data_new])
    
    for node in nd: # poi ciclo
        
        clustertofix = next(cluster for cluster in clusters_data_fixed if cluster['cluster'] == node['node'])
        clustertofix['predecessors'] = node['predecessors']
        clustertofix['successors'] = node['successors']
    
    return clusters_data_fixed


def neighbours_reducing(model, config, nn = 2):
    
    """
    Function that takes as input a model in the form: 
    model = { 'nodes':  clusters_data, 'arcs' : capacity_data }
    
    and returns a list of nn models obtained by removing 1 node at a time with the nodes_removal function 
    (WARNING: arcs and nodes might be implicictly removed!)
    
    nodes are removed starting from the node with the lowest frequency!
    
    
    Dependencies:
        - itemgetter  ( from operator import itemgetter)
        - nodes_removal
        - update_arcs_property
        - givemethenodes
    
    """
    
    if nn == 0:
        return []
    
    clusters_data = model['nodes'].copy()
    capacity_data = model['arcs'].copy()
    
    if nn > len(clusters_data):
        print('WARNING: NEIGHBOURS ASKED: '+ str(nn) + '> NUMBER OF NODES: ' + str(len(clusters_data)) + ', USING MAXIMUM NUMBER OF NODES')
        nn = len(clusters_data)
        
#    ORDER NODES BASED ON PROXY
    try:
        clusters_data.sort(key=itemgetter(config['modelred']['proxy']))
        if config['modelred']['proxy'] == 'contemp':
            capacity_data.reverse()
            
    except Exception as e: 
        print(e)
        warn("COULD NOT FOLLOW PROXY, AGGREGATING AS-IS!!!")     
    
    
    nodes_list_initial = [ c['cluster'] for c in  clusters_data[:nn] ] # list of nodes to try to remove
    arcs_list = [ cd['arc'] for cd in    capacity_data ]
    
    neighbours_list = []
    
    for node in nodes_list_initial:
        
        current_model, arcs_to_update = nodes_removal(node, arcs_list)
        capacity_data_new = update_arcs_property(arcs_to_update, capacity_data, clusters_data)
        
        # rebuild model: select from clusters_data and capacity data the ones coherent with result
        new_model = { 'nodes':  [c for c in clusters_data if c['cluster'] in givemethenodes(current_model)]      , 'arcs' : [cd for cd in capacity_data_new if  cd['arc'] in current_model  ] }
        neighbours_list.append( new_model )
        
    return neighbours_list

#
#def find_neighbours(arcs_list):
#
#    """
#    
#    !!!! ATTENTION !!!!!
#    
#    FUNCTION DEPRECATED: USE neighbours_reducing OR neighbours_aggregate INSTEAD
#    
#    !!!!!!!!!!!!!!!!!!!!
#    
#    Function that gives neighbours of current graph (defined by the list of its arcs)
#    The neighbour is defined by the graphs obtained by removing one node at the time
#    
#    Example:           
#              -->  2    --> 4
#            1
#              -->  3
#              
#              Model: arcs_list  = [(1,2), (2,4), (1,3) ]
#              
#              Neighbours: 
#                  - remove 1: [(2,4)]
#                  - remove 2: [(1,3)]
#                  - remove 3: [(1,2), (2,4)]
#                  - remove 4: [(1,2), (1,3)]
#    Returns the list of tuples of the kind: (model, score_of_model)     
#    The list is sorted: models with higher score are first in list       
#    
#    """
#
## TODO ADD PARAMETERS OF SCORE CALC AS USER INPUT
#
#    neighbours_list = []
#    nodes_list_initial = givemethenodes(arcs_list)
#    
#    for node in nodes_list_initial:
#        current_model = nodes_removal(node, arcs_list)[0]
#    #    calculate score of current model
#        cost_of_current_model = score_calc(givemethenodes(current_model), current_model, capacity_data, activity_corr_data, 0.5, 0.5, unique_list, model, 0.5, 0.5)     
#        neighbours_list.append( (current_model, cost_of_current_model) )
#        
#    #Sorts the neighbour lists by score, so that first element is with max score, ect.
#    neighbours_list_sorted = sorted(neighbours_list, key=lambda tup: tup[1])  
#    neighbours_list_sorted.reverse()
#    
#    return neighbours_list_sorted



############################################################################################################
# FUNCTIONS FOR MODEL REDUCTION 
############################################################################################################    


def arc_removal(arcs_remove_list, arcs_list):

    """
    Function that removes arcs from a list
    also removes arcs implicitly if they remain blind over the graph
    

    FUNCTION CALL EXAMPLE:   
    #arcs_list = list(item['arc'] for item in model['arcs'])
    #arcs_remove_list = [(1,3)]
    #arcs_list, arcs_implicit_remove = arc_removal(arcs_remove_list, arcs_list)

    
    """
    
# check if arc to remove is in list
    arcs_implicit_remove = []
    
    if len(arcs_remove_list) == 0:
        print('you have finished to remove arcs')
        return arcs_list, arcs_implicit_remove
    
    for ra in arcs_remove_list:
    
        if ra not in arcs_list:
            print('arc not in list, do something!!!')
            arcs_remove_list.remove(ra)
            return arc_removal(arcs_remove_list, arcs_list)
            
            
        arcs_list_new = arcs_list.copy()
        arcs_list_new.remove(ra)
            
        
        # check primo elemento ha altri incoming o outcoming
        ra[0]
        has_incoming = False
        has_outgoing = False
        for arc in arcs_list_new:
            if arc[0] == ra[0]:
                has_outgoing = True
            if arc[1] == ra[0]:
                has_incoming = True
            
        if has_outgoing or has_incoming:
            print('ok, DO NOT REMOVE 1st NODE')
            
        elif not(has_outgoing) and not(has_incoming):
        # se non ha incoming ne outgoing, e` rimasto un nodo isolato che va tolto
            print('1ST NODE IS ISOLATED! REMOVE IT')
            
        
        # check secondo elemento ha incoming (se ha solo outgoing raise warning )
        ra[1]
        has_incoming = False
        has_outgoing = False
        for arc in arcs_list_new:
            if arc[0] == ra[1]:
                has_outgoing = True
            if arc[1] == ra[1]:
                has_incoming = True
                
        if has_incoming:
            print('SECOND NODE HAS OTHER INCOMING ARCS, DO NOT REMOVE')
            
        elif has_outgoing and not(has_incoming):
            print('YOU HAVE TO IMPLICITLY REMOVE ARCS STARTING FROM SECOND NODE')
        #    find arcs starting from second node
    #        arcs_implicit_remove = []
            for arc in arcs_list_new:
                if arc[0] == ra[1]:
                    arcs_implicit_remove.append(arc)
        # remove 
            
        elif not(has_outgoing) and not(has_incoming):
        # se non ha incoming ne outgoing, e` rimasto un nodo isolato che va tolto
            print('2ND NODE IS ISOLATED! REMOVE IT')
#        non serve fare lista di nodi (la faccio alla fine)
    
        return arc_removal(arcs_implicit_remove, arcs_list_new)




def nodes_removal(node, arcs_list):
    """
    Function that removes node from model defined by arcs_list
    returns final list of arcs
    
    GEOMETRY-BASED ONLY: applies to any graph model
    
    """
    arcs_to_update = []
    previous = []
    successive = []
    p_arcs = []
    s_arcs = []
    added_arcs = []
    removed_arcs = []
    arcs_list_new = arcs_list.copy()
    # find arcs starting from this node
    for arc in arcs_list:
        if arc[0] == node:
            successive.append(arc[1])
            s_arcs.append(arc)
        if arc[1] == node:
            previous.append(arc[0])
            p_arcs.append(arc)
    
    
    # se previous e succesive sono vuote, il nodo e` isolato e lo posso togliere
    if (len(previous) == 0) and (len(successive) == 0):
        print('WARNING: NODE ' + str(node) +' NOT IN GRAPH: NO ACTION WAS TAKEN')
    
    
    if (len(previous) == 0) and (len(successive) > 0):
    #    remove all the arcs starting from it (NOT with ARCS REMOVAL to avoid implicit removal)
        for arc in s_arcs:
            arcs_list_new.remove(arc)
            removed_arcs.append(arc)
            print('REMOVED ' + str(arc))
            
    if (len(previous) > 0) and (len(successive) == 0):
    #    remove all the arcs arriving to this node (NOT with ARCS REMOVAL to avoid implicit removal)
        for arc in p_arcs:
            arcs_list_new.remove(arc)
            removed_arcs.append(arc)
            print('REMOVED ' + str(arc))
    
    if (len(previous) > 0) and (len(successive) > 0):
        
#        remove incoming arcs
        for arc in p_arcs:
            arcs_list_new.remove(arc)
            removed_arcs.append(arc)
            print('REMOVED ' + str(arc))
         #        remove outgoing arcs   
        for arc in s_arcs:
            arcs_list_new.remove(arc)
            removed_arcs.append(arc)
            print('REMOVED ' + str(arc))
        
        #        fix graph by adding missing connections  
        for start in  previous:
            for end in successive:
                added_arcs.append((start, end))
                #aggiungo alla lista di archi finale solo se non c'e` gia (NB: provare con set)
                if not((start, end) in arcs_list_new):
                    arcs_list_new.append((start, end))
                print('ADDED ' + str(  (start, end)  ))
                
                # has to become a list
                
                arcs_to_update.append({'arc': (start, end) , 'capacity' : {'nodes': node , 'arcs': [(start, node), (node, end)] }  }  )
    
    return arcs_list_new, arcs_to_update


    
    
def update_arcs_property(arcs_to_update, capacity_data, activity_corr_data):

    
    # UPDATE PROPERTIES OF ARCS (GENERATE NEW CAPACITY DATA DATABASE)
    
    # ! MEMO: STRUCTURE OF ARCS TO UPDATE
    # arcs_to_update 
    # [{'arc': (1.0, 3.0),
    #  'capacity': {'nodes': 2.0, 'arcs': [(1.0, 2.0), (2.0, 3.0)]}}]
    
    # check if capacity_to_update is not none
    if len(arcs_to_update) > 0:
        
        capacity_data_new = capacity_data.copy()
            
        for atu in arcs_to_update:
            
            #Se arco e` gia presente non aggiorno il database! (NB todo potrei fare altro come merge)
            if atu['arc'] in [cd['arc'] for cd in capacity_data]:  
                continue
            
#            INHERITANCE:
            cap = 0
            freq = []
            conte = []
            
            # remove arc that has been removed
            for arctoremove in atu['capacity']['arcs']:

# TODO  VA IN STOP ITERATION NEL CASO MARELLI SHORT!!!   CHECK!             
                temp =  next(cdn for cdn in capacity_data_new if cdn['arc'] == arctoremove )
            #    keep track of frequency and capacity (will be added later)
                cap += temp['capacity']
                freq.append(temp['frequency'])
                conte.append( temp['contemp'] )
                
                # remove the arc data 
                if temp in capacity_data_new:
                    capacity_data_new.remove( temp )
                    
                    
            # add data about the node
                    
            if (atu['capacity']['nodes'] in [acd['activity'] for acd in activity_corr_data] ):   
                temp = next(acd for acd in activity_corr_data if acd['cluster'] == atu['capacity']['nodes'])
                cap += temp['capacity']
                freq.append(   temp['frequency'])
                conte.append( temp['contemp'] )
            
            #add data about the added arc to the new arcs database
            capacity_data_new.append( {'arc' : atu['arc'], 'capacity' : cap , 'frequency' : max(freq), 'contemp' : min(conte) } )
    
        return capacity_data_new
    
    else:
        return capacity_data
    


    
    
def givemethenodes(arcs_list):
    """ 
    function that given a list of arcs returns list of nodes
    example: lista = [(1,2), (2,3)]
    givemethenodes(lista) --> [1,2,3]

    """
    nodes_list = set()
    for arc in arcs_list:
        nodes_list.add(arc[0])
        nodes_list.add(arc[1])
    return list(nodes_list)




############################################################################################################
# TABU MODEL REDUCTION (DEPRECATED 26/5/2020)
############################################################################################################    


#neighbours_prova = find_neighbours(arcs_list)
#
#def tabureduction(model, unique_list, config, pen = 0):
#    
#    #INITIAL PARAMETERS FOR MODEL SCORE CALCULATION
#    # calcolo capacita totale del sistema (mi serve per calc score R1)
#    captot_nodes = 0
#    for element in model['nodes']:
#        captot_nodes += element['capacity']
#    
#    captot_arcs = 0
#    for element in model['arcs']:
#        captot_arcs += element['capacity']
#        
#    incoming_init = 0
#    outgoing_init = 0 
#    
#    for node in model['nodes']: 
#        incoming_init += len(node['predecessors'])
#        outgoing_init += len(node['successors'])    
#    
##    unpacking weights from config
#    w_n = config["modelred"]["weights"]["r1_w_n"]
#    w_a = config["modelred"]["weights"]["r1_w_a"]
#    w_i = config["modelred"]["weights"]["r4_w_i"]
#    w_o = config["modelred"]["weights"]["r4_w_o"]
#    ws = config["modelred"]["weights"]["ws"]
#
#    current_solution = model
#    score_of_current_solution = score_calc(model, captot_nodes, captot_arcs, w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o, ws)    
#    best_solution_ever = current_solution
#    best_score_ever = score_of_current_solution
#    best_local_score = 0
#    
#    # number of neighbours found by aggregating and reducing model, respectively
#    n_aggregate = config['modelred']['n_aggregate']
#    n_reducing = config['modelred']['n_reducing']
#    
#    neighbours_type = []  # lista con 'a' ed 'r' per tipo di neighbour
#    for i in range(n_aggregate):
#        neighbours_type.append('a')
#    for i in range(n_reducing):
#        neighbours_type.append('r')
#    
#    
#    # INIT TABU SEARCH PARAMETERS AND VARIABLES
#    tabu_list = list()
#    tabu_list_max_size = 100000
#    count = 1
#    condition = True
#    min_n_nodes = 2
#    max_n_nodes = config['modelred']['desired_size']
#    MinReductionConditionAchieved = False  # True if at least one solution has been found with maximum nr of nodes (reduction constraint)
#    max_iters = config['modelred']['max_iters']
#    iter_record = []
#    iter_record.append( (0, current_solution , score_of_current_solution,  'init'   )      )
#    
#    
#    start = time.time()
#    while condition:   
#        
#        neighbours = neighbours_aggregate(current_solution, n_aggregate) + neighbours_reducing(current_solution, n_reducing)
#             
#        # ASSIGN PENALTY TO THE INDEXES OF SCORES FROM AGGREGATION MODELS
#        pen_ind = [index for index, value in enumerate(neighbours_type) if value == 'a']
#
#        scores = []
#        # for each neighbour, calculate score
#        for nb in neighbours:
#            if neighbours.index(nb) in pen_ind:
#                scores.append(score_calc(nb, captot_nodes, captot_arcs, w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o, ws)   )
#            else:
#                scores.append((1-pen)*score_calc(nb, captot_nodes, captot_arcs, w_n, w_a,  unique_list, incoming_init, outgoing_init, w_i, w_o, ws)   )
#
#    
#
#        #vettore degli indici degli score
#        scores_ordering = list(np.argsort(scores))
#        scores_ordering.reverse() 
#        
#        scores.sort(reverse = True)
#        
#        j  = 0
#        index_of_best_neighbour_solution = scores_ordering[j]    #index of the local solution to be analysed 
#        
#    #    candidate solution 
#    #    neighbours[scores_ordering[j] ]
#        FoundTabu = True
#        while FoundTabu:
#            if neighbours[scores_ordering[j] ] in tabu_list:
#                j = j + 1
#            else:
#                FoundTabu = False
#            if j == len(scores_ordering):
#                print('ALL NEIGHBORS IN TABU LIST: STOP')
#    #            save last perf and close
#                break
#            
#            
#        #check if best score ever can be updated
#        if scores[j] > best_score_ever:
#            best_score_ever = scores[j]
#            best_solution_ever =   dict( neighbours[ scores_ordering[j] ] ) 
#    
#        #check if local score ever can be updated
#        if scores[j] > best_local_score:
#            best_local_score = scores[j]
#            best_local_solution =   dict( neighbours[ scores_ordering[j] ] ) 
#        
#    #   "put the selected solution in tabu list" (shall be the move?)
#        tabu_list.append(  neighbours[ scores_ordering[j] ]    )
#    #    check if needed to reduce tabu list (proxy TS)
#        if len(tabu_list) >= tabu_list_max_size:
#            tabu_list.pop(0)
#        
#    #    SAVE INFO ABOUT CURRENT BEST SOLUTION IN THIS ITERATION
#        iter_record.append( (count, neighbours[ scores_ordering[j] ] ,  scores[j],  neighbours_type[scores_ordering[j]]   )      )
#    
#        
#        if count >= max_iters:
#            condition = False
#            finish = time.time()
#            print('REACHED COMPUTATION LIMIT')
#            
#        elif len(best_local_solution['nodes']) <= min_n_nodes:
#            final_model = best_local_solution
#            condition = False
#            finish = time.time()
#            print('REACHED MINIMUM MODEL SIZE')
#    
##    todo check
#        elif len(best_local_solution['nodes']) <= max_n_nodes:
#    #        NB <= e non = perche potrebbe togliere piu nodi per dipendenze implicite
#            final_model = best_local_solution
#            MinReductionConditionAchieved = True
#            condition = False
#            finish = time.time()
#            print('REACHED DESIRED MODEL SIZE')
#    
#    #   UPDATE ITERATIONS COUNTER
#        count += 1
#        
#    #    SET CURRENT SOLUTION (NEIGHBOURS CALCULATED FROM HERE)
#        current_solution = dict(neighbours[ scores_ordering[j] ])
#        
#    
#    
#    # SAVE RESULTS OF TEST
#    test_results = {'initial_model': model, 'final_model':final_model,   'iter_record' : iter_record, 'tabu_time' : finish - start }
#
#    return test_results
#

############################################################################################################
# TABU SEARCH ALGO
############################################################################################################    




# OLD ONE
    
#
#start = time.time()
#while condition:   
#    
#    neighbours = neighbours_aggregate(current_solution, n_aggregate) + neighbours_reducing(current_solution, n_reducing)
#    
#    scores = []
##for each neighbour, calculate score
#    for nb in neighbours:
#        scores.append(score_calc(nb, captot_nodes, captot_arcs, 0.5, 0.5,  unique_list, incoming_init, outgoing_init, 0.5, 0.5, ws = [0.2, 0.2, 0.2, 0.2, 0.2])   )
#
#    scores_ordering = list(np.argsort(scores))
#    scores_ordering.reverse()
#
#
#    index_of_index_of_best_solution  = 0
#    index_of_best_solution = scores_ordering[index_of_index_of_best_solution]    #index of the local solution to be analysed 
#    
#    
#    best_solution = neighbours[index_of_best_solution]
#    best_score = scores[index_of_best_solution]
##   neighbours_type[index_of_best_solution]
#    
#    
#    found = False
#    i = 0
#    while found is False:
##        
##        while i < len(best_solution):
##            if best_solution[i] != current_solution[i]:
##                first_exchange_node = best_solution[i]
##                second_exchange_node = current_solution[i]
##                break
#        
#        #JUST DEBUG
#        i = i + 1
#        if i > count*1000:
#            print('BEWARE: ERROR IN CYCLE')
#            break
#        
#        if best_solution not in tabu_list:
#            
##            check if its "global" optimum
#            if score_of_current_solution > best_score:
#                
#                best_score_ever = score_of_current_solution
#                best_solution_ever = current_solution
##           update tabu list so i will not come back here again
#            tabu_list.append(best_solution)
##            set as current solution
#            current_solution = best_solution
#            score_of_current_solution = best_score
#            print(score_of_current_solution)
#            
#            found = True
#            
#            iter_record.append( (count, current_solution,score_of_current_solution,  neighbours_type[index_of_best_solution]  )  )
#                
#        else:
#            
##            move to second best solution
#            index_of_index_of_best_solution = index_of_index_of_best_solution + 1
#            
#            if index_of_index_of_best_solution >= len(neighbours):
#                print('NEIGHBORS FINISHED')
#                break
#            
#            best_solution = neighbours[scores_ordering[index_of_index_of_best_solution]]
#            best_score = scores[scores_ordering[index_of_index_of_best_solution]]
#            print(best_score)
#
##        current_solution = neighbours[index_of_best_solution][0]
##        score_of_current_solution = neighbours[index_of_best_solution][1]
#    
#    if len(tabu_list) >= tabu_list_max_size:
#        tabu_list.pop(0)
#    
#    if count >= iters:
#        condition = False
#        finish = time.time()
#        print('REACHED COMPUTATION LIMIT')
#        
#    elif len(best_solution_ever['nodes']) <= min_n_nodes:
#        condition = False
#        finish = time.time()
#        print('REACHED MINIMUM MODEL SIZE')
#
#    elif len(best_solution_ever['nodes']) <= max_n_nodes:
##        NB <= e non = perche potrebbe togliere piu nodi per dipendenze implicite
#        MinReductionConditionAchieved = True
#        condition = False
#        finish = time.time()
#        print('REACHED DESIRED MODEL SIZE')
#
#    count += 1