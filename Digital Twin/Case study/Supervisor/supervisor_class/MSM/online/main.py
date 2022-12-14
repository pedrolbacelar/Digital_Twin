# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 15:55:40 2020

@author: giova
"""

from logmanager import LogManager

lm = LogManager()

lm.run()
lm.stop()

 

############################################################################################################
# DEBUG / PRINTING
############################################################################################################
#import matplotlib.animation
## write log header
#with open('log_new.csv', 'w') as file:
#    file.write('activity,id,ts\n')
from logmanager import *
## start log manager thread
logmanager = LogManager()
logmanager.start()

#options = {
#    'node_color': 'gray',
#    'node_size': 100,
#    'width': 2,
#    'arrowstyle': '-|>',
#    'arrowsize': 5,
#}
#
#
#
#G = nx.DiGraph(directed=True)
#pos = nx.spring_layout(G)
#
#fig, ax = plt.subplots(figsize=(6,4))
#
#def update(num):
#    
#    capacity_data, activity_corr_data = main()
#    
#    G.add_edges_from(    [d['arc'] for d in capacity_data])
#    #pos = nx.spring_layout(G) #other layout commands are available.
#    #fig1 = nx.draw_networkx(G, pos = pos)
#    
#    val_map = {}
#    for d in activity_corr_data:
#        val_map[d['activity']] = d['frequency']
#    
##    values = [val_map.get(node, 0.25) for node in G.nodes()]
#    
#    nx.draw_networkx(G, ax = ax, arrows=True, **options)
#
#
#ani = matplotlib.animation.FuncAnimation(fig, update, frames=6, interval=2000, repeat=True)
#plt.show()
