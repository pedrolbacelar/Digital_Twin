# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:00:09 2020

@author: giova
"""
import pandas as pd
import numpy as np
from tqdm import tqdm
from warnings import warn


#################################################################################
# SUPPORT
#################################################################################


def unique(list1): 
  
    # intilize a null list 
    unique_list = [] 
    
#    print("evaluating unique values... \n")
    
    # traverse for all elements 
    for x in list1: 
        # check if exists in unique_list or not 
        if x not in unique_list: 
            unique_list.append(x)
            
#    print("finished evaluating unique values.")
    
    return unique_list


def x_in_y(query, base):
    """
    >>> x_in_y([3,4,5], [1,2,3,4,5])
        True
        >>> x_in_y([3], [1,2,3,4,5])
        True
        >>> x_in_y(3, [1,2,3,4,5])
        True
        >>> x_in_y([2,3], [1,2,3,4,5])
        True
        >>> x_in_y([2,4], [1,2,3,4,5])
        False
        >>> x_in_y([1,5], [1,2,3,4,5])
        False
    """
    
    
    try:
        l = len(query)
    except TypeError:
        l = 1
        query = type(base)((query,))

    for i in range(len(base)):
        if base[i:i+l] == query:
            return True
    return False



#################################################################################
# GENERATE INITIAL MODEL
#################################################################################


def gen_model_init(data, config, tag = False):
    #check if mapping data is needed

    
    # TRACES
    id_trace_record, unique_list, trace_list, tracetoremove = traces(data, tag)
    
    # CORRELATIONS (PREDECESSORS AND SUCCESSORS)  
    activity_corr_data = activity_rel_data(unique_list, trace_list, data)
    
    # CAPACITY CALCULATION
    capacity_data = capacity_calc(activity_corr_data, id_trace_record, data, tag)
    
    # update activity_corr_data with branching probabilities (after capacity is done)
# TODO do this after clustering
#   activity_corr_data = branching_calc(activity_corr_data, capacity_data)
    
    
    # Contemporary Events (BATCHING)
    # on nodes
    print('Evaluating Batching on Nodes: \n')
    threshold_nodes = config["batching"]["threshold_nodes"]
    for ad in tqdm( activity_corr_data , position=0, leave=True):
        ad['contemp'] = batching_on_nodes(ad['activity'], data, threshold_nodes, tag)
    
        
    # on arcs (TEMPO COMPUTAZ ALTO!!)    
    print('Evaluating Batching on Arcs: \n')
    threshold_arcs = config["batching"]["threshold_arcs"]
    for cd in tqdm( capacity_data , position=0, leave=True):  
         cd['contemp'] = batching_on_arcs( cd['arc'], data, threshold_arcs, tag)
         
    # initial CLUSTERING 
    clusters_data = []
    # creo initial list of clusters (same as act corr data)
    print('Creating Initial Clustering... \n')
    for act in tqdm( activity_corr_data , position = 0, leave=True):
        clusters_data.append(act)
        clusters_data[-1]['cluster'] = act['activity']
         
        
    # SAVE MODEL
    model = { 'nodes':  clusters_data, 'arcs' : capacity_data }

    return model, unique_list, tracetoremove, id_trace_record






        
        
        

#################################################################################
# MINING
#################################################################################

def checktype(data):

    activity_mapping = {}
    id_mapping = {}
    ts_mapping = {}
    
    
    
    if isinstance(data.activity[0], str):
    
        for value in set(data.activity.values):
            activity_mapping[value] = list(set(data.activity.values)).index(value)
    
        print('Activities have been mapped')        
    
    if isinstance(data.id[0], str):
    
        for value in set(data.id.values):
            id_mapping[value] = list(set(data.id.values)).index(value)
            
        print('Part IDs have been mapped')     
    
    if isinstance(data.ts[0], str):
    
        for value in set(data.ts.values):
            ts_mapping[value] = list(set(data.ts.values)).index(value)
            
        print('Timestamps have been mapped')     
    
#    data.columns
    
    newdata = data.copy()
    
    if len(activity_mapping)>0:
        for i in range(len(data)):
            newdata.loc[i,'activity'] = activity_mapping[data.loc[i,'activity']]
    
    if len(id_mapping)>0:
        for i in range(len(data)):
            newdata.loc[i,'id'] = activity_mapping[data.loc[i,'id']]
    
    if len(ts_mapping)>0:
        for i in range(len(data)):
            newdata.loc[i,'ts'] = activity_mapping[data.loc[i,'ts']]
    
    mappings = {'activity': activity_mapping, 'id' : id_mapping, 'ts' : ts_mapping }
    
    return newdata, mappings


def model_after_mapping(model, mappings):
    
#    todo complete with id and ts
    for node in model['nodes']:
        node['name'] = list(mappings['activity'].keys())[list(mappings['activity'].values()).index(node['activity'])]
        
    for arcs in model['arcs']:
            el1 = list(mappings['activity'].keys())[list(mappings['activity'].values()).index(arcs['arc'][0])]
            el2 = list(mappings['activity'].keys())[list(mappings['activity'].values()).index(arcs['arc'][1])]
            arcs['name'] = (el1, el2)
            
    return model




def traces(data, tag = False):
    """
    Function that takes as input the log file as pandas dataframe and a list of unique ids,
    returns the list of id trace records  
    ( dictionary of the kind: 
      
      {'id': 3112,
      'trace': ['buffer_in', 'machine_in', 'machine_out'],
      'ts': [8, 8, 16]
      }
      
    )
    ... and the list of unique traces followed 
    
    
    ATTENTION: if event logs has start/finish tags, traces discards them and considers only start times! (only logical relationship is needed)
    
    """
    
#CHECK IF START/FINISH TAGS ARE PROVIDED
    if tag:
        
        if "tag" in data.columns:
            data = data[data["tag"] == "s"]
        else:
            warn("Asked to use tags but no tags in the event-log, continued without.")
    
    else:
        
        if "tag" in data.columns:
                data = data[data["tag"] == "s"]
                warn("Event log has start/finish tags, considering them now.")

    
    id_u = data.id.unique().tolist()
#    activity_u = data.activity.unique().tolist()
    
#    n_id_u = len(id_u)
#    n_activity_u = len(activity_u)
    
#    id_trace_list = []
#    id_contemp = []
    trace_list = []
    id_trace_record = []
#    id_contemp = []
    
    
    print('Traces Calculation \n')
    for i in tqdm( range( len(id_u) ) , position=0, leave=True):
#     id_trace_list.append(data.loc[data['id'] == id_u[i]].sort_values(by=['ts']))
        id_trace_record.append(  {'id': id_u[i] , 'trace': list(data.loc[data['id'] == id_u[i]].sort_values(by=['ts']).activity), 'ts': list(data.loc[data['id'] == id_u[i]].sort_values(by=['ts']).ts)}   )
        trace_list.append(list(data.loc[data['id'] == id_u[i]].sort_values(by=['ts']).activity))
#     identify ids with contemporary events
#        if len(list(data.loc[data['id'] == id_u[i]]['ts'])) != len(set(list(data.loc[data['id'] == id_u[i]]['ts']))):
#            id_contemp.append(id_u[i])
         
        
#         WARNING, DOES NOT WORK IF ACTIVITY IS A STRING!
    #calculate percentage of syncronous events ids
#    ids_with_sync_events =  len(id_contemp) / len(id_u) 
#    unique_list2, unique_list_frequency2 = np.unique(trace_list, return_counts = True)
#    unique_list = list (unique_list2)
#    unique_list_frequency= list (unique_list_frequency2)
#    #calculate frequency to identify outliers (example: data errors)
#    
    
    unique_list = unique(trace_list)
    
    unique_list_frequency = []
    for element in unique_list:
        counter = 0
        for i in range(len(trace_list)):
            if trace_list[i] == element:
                counter += 1
        unique_list_frequency.append(counter)    
        
    to_remove = []    
    
    if len(unique_list) <=1: 
        return id_trace_record, unique_list, trace_list, to_remove
        
    print('OUTLIERS CHECK: \n')
    
    anyoutlier = False
#    OUTLIERS CHECK
    for trace in unique_list:
        tmp_list = unique_list.copy()
        tmp_list.remove(trace)
        condition1 = False
        condition2 = False
#        condition3 = False
        lens = []
        
        for other_trace in tmp_list:
            # CONDIZIONE 1: LA LUNGHEZZA E` 5 VOLTE SUPERIORE DELLE ALTRE TRACCE
            lens.append(len(other_trace))
            
        if len(trace) > 5 * max(lens):
            condition1 = True
            
        # CONDIZIONE 2: FREQUENZA RELATIVA INFERIORE AL 5%
        if unique_list_frequency[unique_list.index(trace)] /sum(unique_list_frequency) < 0.05:
            condition2 = True
            
        if unique_list_frequency[unique_list.index(trace)] /sum(unique_list_frequency) < 0.01:
#            condition3 = True
            to_remove.append(trace)
            print('TRACE NR.' + str(unique_list.index(trace) ) + ' REMOVED. \n')
            anyoutlier = True
            
        if condition1 and condition2:
            to_remove.append(trace)
            print('TRACE NR.' + str(unique_list.index(trace) ) + ' REMOVED. \n')
            anyoutlier = True
            
    for tracetoremove in to_remove:
        if tracetoremove in unique_list:  
            unique_list.remove(tracetoremove)
        if tracetoremove in trace_list:  
            trace_list.remove(tracetoremove)
        
    if not anyoutlier:
        print('NO OUTLIERS FOUND. \n')
#                
#            
#    if len(unique_list_frequency) != len(unique_list):
#    #    raise TroubleWithDataError
#        print('ATTENTION!!! There is a problem with the list dimentions')
    
    return id_trace_record, unique_list, trace_list, to_remove


def initialsandfinals(unique_list):
    
    """
    Find first and last activities of the network
    Takes as input the list of unique traces
    Returns 2 lists: list of initial activities and list of final activities (in this order)
    """

    initials = set()
    finals = set()
    
    for trace in unique_list:
        
        initials.add( trace[0]  )
        finals.add( trace[-1]  )
        
    return list(initials), list(finals)




def activity_rel_data(unique_list, trace_list, data):
    
    """
    Function that takes as input the unique list of traces as list of lists (example: [['a','b'] , ['b', 'c']])
    ... and the list of unique activities of  interest (example: ['a', 'b', 'c'])
    
    returns the activity relationship data as list of dictionaries of the kind:
        
        {'activity': 'buffer_in',
         'predecessors': [],  # List of prececessors
#         'successors': ['machine_in'],  # List of successors
         'frequency': None,
         'capacity' : 1 } # DEFAULT VALUE = 1
        
    """
# TODO remove trace_list - i can calculate frequency from data
    
    activity_u = data.activity.unique().tolist() 

    activity_corr_data = []   # list of dictionaries with predecessors and successors of an activity
    print('Activities Relationships Mining')
    
    for i in range(len(activity_u)):
        activity_corr_data.append({  'activity': activity_u[i], 'predecessors': [] , 'successors': [], 'frequency': None, 'capacity' : 1  })   
        
    for e in tqdm( range(len(unique_list)) , position=0, leave=True):
        
        if len(unique_list[e]) == 1:
            continue
        
        for a in activity_u:
            
            if a in unique_list[e]:    # 1 has to become the index of footprint check
                
                i = unique_list[e].index(a) 
                
#                
                for i in [k for k in range(len(unique_list[e])) if unique_list[e][k] == a]:
#                
                    if i == 0:
                        if unique_list[e][i+1] not in next(item for item in activity_corr_data if item["activity"] == a)['successors']:   # TODO : check if better with set:    x = set([1,2,3]) >>> x.add(2)
        
                #            next(item for item in activity_corr_data if item["activity"] == 998)['predecessors'].append(unique_list[1][i-1])
                            next(item for item in activity_corr_data if item["activity"] == a)['successors'].append(unique_list[e][i+1])
                       
                    elif i == len( unique_list[e])-1:
                        
                        if unique_list[e][i-1] not in next(item for item in activity_corr_data if item["activity"] == a)['predecessors']:
                            next(item for item in activity_corr_data if item["activity"] == a)['predecessors'].append(unique_list[e][i-1])
            #            next(item for item in activity_corr_data if item["activity"] == 998)['successors'].append(unique_list[1][i+1])
                    
                    else:
                        
                        if unique_list[e][i+1] not in next(item for item in activity_corr_data if item["activity"] == a)['successors']:   # TODO : check if better with set:    x = set([1,2,3]) >>> x.add(2)
        
                            next(item for item in activity_corr_data if item["activity"] == a)['successors'].append(unique_list[e][i+1])
                        
                        if unique_list[e][i-1] not in next(item for item in activity_corr_data if item["activity"] == a)['predecessors']:
                            
                            next(item for item in activity_corr_data if item["activity"] == a)['predecessors'].append(unique_list[e][i-1])
                            



    return frequency_nodes(activity_corr_data, trace_list)


def frequency_nodes(activity_corr_data, trace_list):
                        
    for act in activity_corr_data:
        
        #Calculates NODES (frequenza dell'attivita nel log)
        frequency = 0
        for i in range(len(trace_list)):
            if act['activity'] in trace_list[i]:
                frequency += 1
        act['frequency'] = frequency
        
#    CHECK OUTLIERS
    freq_max = max([act['frequency'] for act in activity_corr_data])

    for act in activity_corr_data:
        
        if act['frequency'] < freq_max / 100 :
            
            warn('ACTIVITY ' + str(act['activity'] ) + ' REMOVED. \n')
            activity_corr_data.remove(act)
        
    return activity_corr_data


def branching_calc(activity_corr_data, capacity_data):
    
    print('Evaluating Branching on Nodes: \n')
    
    for ad in tqdm( activity_corr_data, position=0, leave=True):
    
        ad['branching'] = []
        
        freq = []
        dest = []
        for cd in capacity_data:
        #    tmp.append(cd['arc'][0] == a)
            if cd['arc'][0] == ad['activity']:
                freq.append(cd['frequency'])
                dest.append(cd['arc'][1])
                
        if len(freq) > 1:
             for element in dest:
                 ad['branching'].append({'dest': element,'prob': freq[dest.index(element)]/sum(freq)})
                 
    return activity_corr_data





def capacity_calc(activity_corr_data,id_trace_record, data, tag = False):

    """
    Function that determines how to calculate capacity. 
    If tags are in the log, use the f capacity_calc_withtags(...)
    If not, use capacity_calc_nottags(...)
    
    returns the same output as capacitycalc, so capacity_data...
    
    """
    
    if tag:
        return capacity_calc_withtags(activity_corr_data,id_trace_record, data)
    
    else:
        return  capacity_calc_notags(activity_corr_data,id_trace_record, data)
    
            

# CAPACITY CALCULATION
def capacity_calc_withtags(activity_corr_data,id_trace_record, data):
    
    """
    CAPACITY MINING
    
    HP self loops are not included in the analysis
    """    
    
    print('Capacity Mining')
    
#    get list of unique ids
    id_u = data.id.unique().tolist()
    
    capacity_data = []  # list of dictionaries of the type { 'arc' : (predecessor, successor), 'capacity' : capacity_value }
    
    # per ogni attivita
    for act in tqdm( range(len(activity_corr_data)), position=0, leave=True) :
        
    #    remove same activity (HP self loops are not included in the analysis)
        if activity_corr_data[act]['activity'] in activity_corr_data[act]['successors']:
            activity_corr_data[act]['successors'].remove(activity_corr_data[act]['activity'])
            
        if activity_corr_data[act]['activity'] in activity_corr_data[act]['predecessors']:
            activity_corr_data[act]['predecessors'].remove(activity_corr_data[act]['activity'])
    
    
        if len(activity_corr_data[act]['successors']) > 0: 
            
            
            for s in range(len(activity_corr_data[act]['successors'])):
                
                tupla = (activity_corr_data[act]['activity'],  activity_corr_data[act]['successors'][s] )
                
#                print (str(tupla))
#                TODO separate frequency and capacity
                frequency = 0
                id_ok = []
                # per ogni ID
                for part in range(len(id_u)):
                    
                    #verifico 3 condizioni: che sia predecessor che successor siano nel trace dell'ID, e che siano uno a seguito dell'altro (non è detto che quell'ID abbia seguito il trace che ho in mente)
                    if activity_corr_data[act]['activity'] in id_trace_record[part]['trace'] and activity_corr_data[act]['successors'][s] in id_trace_record[part]['trace']:
#                    OLD and id_trace_record[part]['trace'].index(activity_corr_data[act]['activity']) == id_trace_record[part]['trace'].index(activity_corr_data[act]['successors'][s]) - 1:
                        
                        indiciatt = [k for k in range(len(id_trace_record[part]['trace'])) if id_trace_record[part]['trace'][k] == activity_corr_data[act]['activity']]
                        indicisucc = [d-1 for d in range(len(id_trace_record[part]['trace'])) if id_trace_record[part]['trace'][d] == activity_corr_data[act]['successors'][s]]
                        
                        if any(x in indiciatt for x in indicisucc):
                            id_ok.append(id_trace_record[part]['id'])
                            frequency += 1
                        
                        
                if len(id_ok) > 0:
                    
#                    capacity mining
#                    TODO aggiungo condizione tag == s e tag == f
#                    TODO aggiungo condizione se i due ts sono uguali val = 0 (potrebbero invertirsi poi nel sort )
                    data.loc[ (data['id'].isin(id_ok)) & (data['activity'] == tupla[0]) & (data['tag'] == 'f'), 'val'    ] = 1
                    data.loc[ (data['id'].isin(id_ok)) & (data['activity'] == tupla[1]) & (data['tag'] == 's'), 'val'    ] = - 1

                    
                    cumsum = data.loc[ (data['id'].isin(id_ok)) & ( ((data['activity'] == tupla[0]) & (data['tag'] == 'f')) | ((data['activity'] == tupla[1]) & (data['tag'] == 's')) ), :].sort_values(by=['ts']).loc[:, 'val'].cumsum()
                    
            
                    # here frequency is ARCS value   PRIMA: capacity:  tempdf['cumsum'].max()
                    try:
                        capacity_data.append(   { 'arc' : tupla, 'capacity' : max(cumsum)-1 ,   'frequency' : frequency  })  # , 'flowtimes': iarc  }    )
                    except ValueError:
                        warn('ValueError when evaluating capacity on arc (' + str(tupla[0]) + ',' + str(tupla[1]) + ').')
                        capacity_data.append(   { 'arc' : tupla, 'capacity' : 0 ,   'frequency' : frequency  })  # , 'flowtimes': iarc  }    )

        else:
            continue
    
    return capacity_data


    

# CAPACITY CALCULATION
def capacity_calc_notags(activity_corr_data,id_trace_record, data):
    
    """
    CAPACITY MINING
    
    HP self loops are not included in the analysis
    """    
    
    print('Capacity Mining')
    
#    get list of unique ids
    id_u = data.id.unique().tolist()
    
    capacity_data = []  # list of dictionaries of the type { 'arc' : (predecessor, successor), 'capacity' : capacity_value }
    
    # per ogni attivita
    for act in tqdm( range(len(activity_corr_data)), position=0, leave=True) :
        
    #    remove same activity (HP self loops are not included in the analysis)
#     TODO this has to go to activity rel function!
        if activity_corr_data[act]['activity'] in activity_corr_data[act]['successors']:
            activity_corr_data[act]['successors'].remove(activity_corr_data[act]['activity'])
            
        if activity_corr_data[act]['activity'] in activity_corr_data[act]['predecessors']:
            activity_corr_data[act]['predecessors'].remove(activity_corr_data[act]['activity'])
    
    
        if len(activity_corr_data[act]['successors']) > 0: 
            
            
            for s in range(len(activity_corr_data[act]['successors'])):
                
                tupla = (activity_corr_data[act]['activity'],  activity_corr_data[act]['successors'][s] )
                
                frequency = 0
                id_ok = []
                # per ogni ID
                for part in range(len(id_u)):
                    
                    #verifico 3 condizioni: che sia predecessor che successor siano nel trace dell'ID, e che siano uno a seguito dell'altro (non è detto che quell'ID abbia seguito il trace che ho in mente)
                    if activity_corr_data[act]['activity'] in id_trace_record[part]['trace'] and activity_corr_data[act]['successors'][s] in id_trace_record[part]['trace']:
#                    OLD and id_trace_record[part]['trace'].index(activity_corr_data[act]['activity']) == id_trace_record[part]['trace'].index(activity_corr_data[act]['successors'][s]) - 1:
                        
                        indiciatt = [k for k in range(len(id_trace_record[part]['trace'])) if id_trace_record[part]['trace'][k] == activity_corr_data[act]['activity']]
                        indicisucc = [d-1 for d in range(len(id_trace_record[part]['trace'])) if id_trace_record[part]['trace'][d] == activity_corr_data[act]['successors'][s]]
                        
                        if any(x in indiciatt for x in indicisucc):
                            id_ok.append(id_trace_record[part]['id'])
                            frequency += 1
                        
                        
                if len(id_ok) > 0:
                    
#                    PRIMA
#                    tempdf = data[data['id'].isin(id_ok)]   # do not use loc here, otherwise i get warnings later
#                    tempdf.loc[  tempdf['activity'] == tupla[0], 'val'    ] = 1
#                    tempdf.loc[  tempdf['activity'] == tupla[1], 'val'    ] = - 1
#                    
#                    DOPO
                    data.loc[ (data['id'].isin(id_ok)) & (data['activity'] == tupla[0]), 'val'    ] = 1
                    data.loc[ (data['id'].isin(id_ok)) & (data['activity'] == tupla[1]), 'val'    ] = - 1
                    
                    
#                    iarc = []
#                    for element in id_ok:
#                        iarc.append(tempdf["ts"][(tempdf['activity'] == tupla[1]) & (tempdf['id'] == element  )].item()  - tempdf["ts"][(tempdf['activity'] == tupla[0]) & (tempdf['id'] == element  )].item() )
#                    
#                   PRIMA
                    # qui sort
#                    tempdf = tempdf.sort_values(by=['ts'])
#                    tempdf.loc[:, 'cumsum'] = tempdf['val'].cumsum()
                    
#                   DOPO
                    cumsum = data.loc[ (data['id'].isin(id_ok)) & ((data['activity'] == tupla[0]) | (data['activity'] == tupla[1])), :].sort_values(by=['ts']).loc[:, 'val'].cumsum()
#                    tempdf.loc[:, 'cumsum'] = tempdf['val'].cumsum()
                    
                    
                    
                    # here frequency is ARCS value   PRIMA: capacity:  tempdf['cumsum'].max()
                    capacity_data.append(   { 'arc' : tupla, 'capacity' : max(cumsum)-1 ,   'frequency' : frequency  })  # , 'flowtimes': iarc  }    )
            
        else:
            continue
    
    return capacity_data



############################################################################################################
# BATCHING
############################################################################################################


def batching_on_nodes(node, data, threshold_nodes = 1, tag = False):
    
    """
    Function that takes as input a node, a dataframe, and a threshold value (same unit of timestamp in database)
    
    The function looks up for the column 'ts' in the dataframe and returns the Q3 of the number of consecutive events on the node
    
    NOTE:
        
        consecutive is intended from the start times!!!
        
        consecutive is defined depending on the threshold value
        
        (i) and (i + 1)-th events on the node are consec if:
            t[i+1] - t[i] < threshold 
            
    default value is 1 time unit
    
    FUNCTION RETURNS 0 IF NO CONSEC EVENTS ARE FOUND
        
    """
    #np.diff ( x ) --> x = vettore timestamp ordinato della attivita 'a' nel database
    
    if tag:
#        OLD
#        proc_times = np.diff ( data[(data['activity'] == node) & (data['tag'] == 's')].sort_values(by=['ts'])['ts'].values  )
        intertempi = []
    
        id_u = data.id.unique().tolist()
        
        for i in id_u:
        
            tempi = data[(data['id'] == i) & (data['activity'] == node)  ].ts
            
            if len(tempi) > 1:
                
                intertempi.append(max(tempi) - min(tempi))
        
        proc_times = np.array(intertempi)
        
    else:
        
        if 'tag' in data.columns:
            proc_times = np.diff ( data[(data['activity'] == node) & (data['tag'] == 's')  ].dropna(how='all').sort_values(by=['ts'])['ts'].values  )
        else:
            proc_times = np.diff ( data[(data['activity'] == node)  ].dropna(how='all').sort_values(by=['ts'])['ts'].values  )

    return int(sum(proc_times < threshold_nodes))





def batching_on_arcs(arc, data, threshold_arcs = 1, tag = False):
    
    """
    Function that takes as input an arc, the id_trace_record, and a threshold value (same unit of timestamp in database)
    
    The function looks up for the 'ts' key in the id_trace_record database (list of dictionairies of the form
    {'id': 2, 'trace': [1, 3, 5], 'ts': [0.072359, 2.5525, 2.5859]}
    
    and returns the number of consecutive events on the arc
    
    NOTE:
        
        consecutive is defined depending on the threshold value
        
        (i) and (i + 1)-th events on the arc are consec if:
            t[i+1] - t[i] < threshold 
            
    default value is 1 second
    
    FUNCTION RETURNS 0 IF NO CONSEC EVENTS ARE FOUND

        
    """
    
    intertempi = []
    i = 0
    
    id_u = data.id.unique().tolist()
    for i in id_u:
    
        try:
            tempi = data[(data['id'] == i) & ( (data['activity'] == arc[0]) & (data['tag'] == 'f')  | (data['activity'] == arc[1]) & (data['tag']  == 's')  )  ].ts
            
            if len(tempi) > 1:
                intertempi.append(max(tempi) - min(tempi))
        except: continue
    
#   OLD:
#    for part in range(len(id_trace_record)):
#        # verifico che arco sia compatibile con la traccia 
#        #entrambe le attivita sono nella traccia
#        if (all(elem in id_trace_record[part]['trace']  for elem in   list(arc))) :
#            indice0 =  id_trace_record[part]['trace'].index(arc[0]) 
#            indice1 =  id_trace_record[part]['trace'].index(arc[1]) 
#            
#            # l'ordine dell'arco e` rispettato
#            if indice0 < indice1:
#                intertempi.append(id_trace_record[part]['ts'][  indice1  ] - id_trace_record[part]['ts'][  indice0 ])
#        
    it = np.array(intertempi)
    
    return int(sum(it < threshold_arcs))





    

############################################################################################################
# calculate arcs and nodes MATRIX FORM
############################################################################################################

def arcs_matrix(activity_u, capacity_data):

    eps = 10e-30
    ARCS = np.empty([len(activity_u), len(activity_u)])
    
    for i in range(len(capacity_data)):
        ARCS[activity_u.index(capacity_data[i]['arc'][0])][activity_u.index(capacity_data[i]['arc'][1])] = capacity_data[i]['frequency']
    
    for (x,y), value in np.ndenumerate(ARCS):
        if value < eps or np.isnan(value):
            ARCS[x,y] = 0
            
    return ARCS


def nodes_matrix(activity_u, activity_corr_data):

    eps = 10e-30
    NODES = np.empty([len(activity_u)])
    
    for i in range(len(activity_corr_data)):
        NODES[activity_u.index(activity_corr_data[i]['activity'])] = activity_corr_data[i]['frequency']
     
    for x, value in np.ndenumerate(NODES):
        if value < eps or np.isnan(value):
            NODES[x] = 0
        
    return NODES


