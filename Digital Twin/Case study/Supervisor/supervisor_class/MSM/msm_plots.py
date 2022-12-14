# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 15:17:12 2020

@author: giova
"""

# 
############################################################################################################
# PROVA DISEGNO GRAFO
############################################################################################################

import networkx as nx
import matplotlib.pyplot as plt # For drawing
import os
#from networkx.drawing.nx_agraph import graphviz_layout
os.environ["PATH"] += os.pathsep + 'C:\\Program Files (x86)\\graphviz-2.50.0\\Graphviz\\bin\\'
from graphviz import Digraph

def plot_model_old(model, fig_obj = False):

    list_of_arcs = [m['arc'] for m in model['arcs']]
    a = print_graph(list_of_arcs)
    if fig_obj:
        return a
    else:
        return None
    
    
def plot_model(model, filename, show = True):
    
    #plot_model(model, show = True)

    
    
    edges = []
    for arc in [a['arc'] for a in model['arcs']]:
        try:
            edges.append(  str(int(arc[0]))+str(int(arc[1])) ) 
        except:
            edges.append(  str(arc[0])+str(arc[1])) 
            
#    create graphviz digraph
    dot = Digraph()
    #dot.node('A', 'A')
    dot.edges(edges)
    
    print(dot.source)
    
    dot.render(filename, view=show)
    
    




# todo return the figure object
def print_graph(list_of_arcs):

    print('Graph Printing')
    
    options = {
        'node_color': 'orange',
        'node_size': 400,
        'width': 2,
        'arrowstyle': '-|>',
        'arrowsize': 5,
    }
    
    
    # create a graph
    #G = nx.Graph()
    G = nx.DiGraph(directed=True)
    #G.add_edges_from(
    #    [('A', 'B'), ('A', 'C'), ('D', 'B'), ('E', 'C'), ('E', 'F'),
    #     ('B', 'H'), ('B', 'G'), ('B', 'F'), ('C', 'G')])
    
    #G.add_edges_from(    [d['arc'] for d in capacity_data])
    G.add_edges_from(    list_of_arcs)
    
    # per assegnare dei pesi bisogna fare cosi
    #G.add_weighted_edges_from([(1, 2, 0.5), (3, 1, 0.75)])
    
    #[d['frequency'] for d in activity_corr_data]
#    val_map = {}
    
    #for d in activity_corr_data:
    #    val_map[d['activity']] = d['frequency']
    
#    A = to_agraph(G)
#    G.update(rankdir='LR')  # change direction of the layout
#    for rank_of_nodes in ranked_node_names:
#        A.add_subgraph(rank_of_nodes, rank='same')
#    # draw
#    A.draw('example.png', prog='dot')
    
#    val_map = {'A': 1.0,
#               'B': 2.0,}
#    
#    values = [val_map.get(node, 0.25) for node in G.nodes()]
    
#    a = nx.draw(G, pos = graphviz_layout(G), cmap = plt.get_cmap('jet'), node_color = values)
    a = nx.draw_networkx(G, arrows=True, **options)

    
    
    plt.show(a)
    plt.savefig('graph.png')
    
    return a

