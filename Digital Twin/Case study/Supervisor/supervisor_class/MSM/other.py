# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 15:14:47 2020

@author: giova
"""

# recognizing parallel graph parts 

# lets create a graph (list of arcs) with 2 parallel parts




#arcs = [(1,2), (1,3), (3,4), (2,4), (4, 5), (4, 6), (5, 7), (6, 7), (4, 8), (8,7)]


#######################################################################################

def find_parallel(arcs_list):
    
    """
    Function that givan an arc's list, it returns the list of sections between which there are activities in parallel
    
    example:
        
        arcs = [(1,2), (1,3), (3,4), (2,4), (4, 5), (4, 6), (5, 7), (6, 7), (4, 8), (8,7)]
    
    
        [
         {'section': (4, 7), 'activities_involved': {5, 6, 8} },
         {'section': (1, 4), 'activities_involved': {2, 3} }       
        ]
    
    """

    nodes_data =  getmenodesdata(arcs_list)
    
    return find_par_clusters(nodes_data)


#######################################################################################
# DEPENDENT FUNCTIONS

def common(a,b): 
    c = [value for value in a if value in b] 
    return c


def getmenodesdata(arcs_list):
    
    # first structure
    nodes = set()
    for arc in arcs_list:
        for node in arc:
            nodes.add(node)
      
    nodes_data = []      
    for node in nodes:
        nodes_data.append({'node': node, 'predecessors': [], 'successors': []  })
    
    
    # STEP 1: reconstruct predecessors and successors for each node
    for node in nodes:
        for arc in arcs_list:
            if node == arc[0]:
                next(n for n in nodes_data if n['node'] == node)['successors'].append(arc[1])
            if node == arc[1]:
                next(n for n in nodes_data if n['node'] == node)['predecessors'].append(arc[0])
     
    return nodes_data




def find_par_clusters(nodes_data):
    
    # STEP 2: for each node check if it has same predecessor as another node/ nodes
    clusters_data = []
    nodes = set ( [n ['node'] for n in nodes_data   ]   )

    
    for node in nodes:
            
        succs = next(n for n in nodes_data if n['node'] == node  )['successors']
        
        # non serve continuare se non ho almeno 2 nodi (altrimenti non avrei nessun parallelo)
        # if len(sucs) < 2 continue 
        # non serve !  prendo un nodo i suoi successors, vedo se loro hanno successors in comune
        # unica eccezione e` se modello iniziasse con 2 nodi in parallelo:
        # ipotesi! ho gia inserito il nodo "start"
        
        for node_i in succs:
            
            succs_of_first_node = next(n for n in nodes_data if n['node'] == node_i  )['successors']
            other_nodes = list(set(succs) - set([node_i]))
            
            for node_j in other_nodes:
                
                succs_of_other_node = next(n for n in nodes_data if n['node'] == node_j  )['successors']
                
                if len(common ( succs_of_first_node , succs_of_other_node   ) ) > 0:
                    
        #             creo cluster
                    cluster = {  'section': (node,  common ( succs_of_first_node , succs_of_other_node   )[0]  ) , 'activities_involved': [node_i, node_j] }
                    clusters_data.append(cluster)
    
    clusters_data_final = []
    
    for sec in set ( [s['section'] for s in clusters_data ]   ):
    
        activities = set()
        
        for c in clusters_data:
            if c['section'] == sec:
                activities = activities | set(c['activities_involved']) 
        
        clusters_data_final.append ({'section' : sec , 'activities_involved' : activities  })
        
    return clusters_data_final




#################################################################################
# ARCS/NODES RELATIONS
#################################################################################

def findinvolvedarcs(c1, c2, listofarcs):
    
    """
    Function that takes as input 2 nodes and a list of arcs, returns the arcs in which both nodes are involved
    example findinvolvedarcs(1, 2, [(1,2), (2,3), (3,4)]) --> [(1,2)]
    """

    temp = []
    
    if ((c1,c2) in listofarcs):
        temp.append( (c1,c2) )
    if ((c2,c1) in listofarcs):
        temp.append( (c2,c1) )
        
    return temp


def findinandoutarcs(c1, c2, listofarcs):
    
    """
    Function that takes as input 2 nodes and a list of arcs, returns the arcs in which nodes are involved
    as 2 lists: (1) incoming and (2) outgoing 
    example findinandoutarcs(1, 2, [(1,2), (2,3), (3,4)]) --> incoming = [] ; outgoing = [2,3]
    """

    incoming = []
    outgoing = []
    
    for arc in listofarcs:
        # attenzione se arco include entrambi i nodi va tolto per questo " and not ..."
        if ((arc[1] == c1) | (arc[1] == c2)) and not(  (arc == (c1,c2)) | (arc == (c2,c1))   ) :
           incoming.append(arc) 
        if ((arc[0] == c1) | (arc[0] == c2)) and not(  (arc == (c1,c2)) | (arc == (c2,c1))   ):
           outgoing.append(arc) 
         
    return incoming, outgoing


def find_ordered_arcs(final_model):
    
    
        #  1.  interarrivals
    fn = find_first_node(final_model)
    
    c = next(n for n in final_model['nodes'] if n['cluster'] == fn)
    
    # check if this node is a cluster or not
    if isinstance(c['activity'], list): 
        # se vero è un cluster, devo trovare il primo nodo nel cluster   
        primatt = find_first_in_cluster(data, c['activity'])
    
    else:   # se falso, la prima attivita va bene
        primatt = c['activity']
        
    listofarcs = [a['arc'] for a in final_model['arcs']]
    
    listofarcs_ordered = []
    listofnodes_ordered = []
    first_node = primatt
    while 1:
        try:
            arc = next(a for a in listofarcs if a[0] == first_node)
            listofarcs_ordered.append(arc)
            listofnodes_ordered.append(arc[0])
            first_node = arc[1]
        except StopIteration:
            listofnodes_ordered.append(arc[1])
            break
    
    return listofarcs_ordered, listofnodes_ordered




def find_first_node(model):
    
    a =  [a['arc'] for a in model['arcs']]
    
    pn = [n for n in getmenodesdata(a) if n['predecessors'] == []]
    
    if len(pn) == 0:
        pn = 1
        
    else:
        primonodo = pn[0]['node']
    
    return primonodo



#################################################################################
# MODEL DIMENTION
#################################################################################




def model_dim(model):
   
    return len( [n for n in model['nodes']] )



