# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 16:23:38 2020

@author: giova
"""

import scipy
import scipy.stats
#import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import operator
#import os
import sys
#import json
from warnings import warn
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from tqdm import tqdm


sys.path.append(r'C:\Users\giova\OneDrive - Politecnico di Milano\WIP')
sys.path.append('../')

#from MSM.msmlib import x_in_y
from MSM.other import getmenodesdata, find_first_node
#from MSM.msmlib import gen_model_init
#from MSM.modelred import givemethenodes


#######################################################################
# KPI ESTIMATION (TH)
#######################################################################

# ******************* THROUGHPUT *******************


# WARM UP IDENTIFICATION:


def warmup_mser(th, m = 5):
    """
    default value is 5 as in:
        https://warwick.ac.uk/fac/soc/wbs/projects/autosimoa/warmup/
    
    """
    
    if m != 1 and len(th)> m*3:
        listofmeans = [np.mean(i) for i in np.array_split(th, int(np.floor(len(th)/m))) ]
    else: 
        listofmeans = th
        m = 1
    
    n = len(listofmeans)
    dseq = []
    
    for d in range(1,n):
        
        dseq.append( np.std(listofmeans[d:]) /  np.sqrt(n-d) )
        
    wup = m * dseq.index(np.min(dseq[:int(np.floor(len(dseq)/2))]))  
    
    if dseq.index(np.min(dseq)) > len(dseq)/2:
        warn("MSER FAILED TO IDENTIFY WARMUP, RETURNING MINIMUM OF FIRST HALF: "+str(wup)+"/"+str(len(th)), stacklevel=2)
    
    return wup



def calc_th_seq_fromdata(data):
    
    
    """
    returns estimated througput data points sequence from data
    
    """
    
    ts_list = []
    
    for i in data.id.unique().tolist():
        #trovo time stamp a cui è uscita questa parte
        tsu = max(data[data.id == i].ts)    
       
#        cerco quante parti sono già uscite
#        data[data.ts <= tsu].id.unique()
        ts_list.append(tsu)
       
    
    ts_list_new = np.sort(np.array(ts_list))
    
#CONSISTENCY CHECK
    if len(data.id.unique().tolist()) != len(ts_list_new):
        raise ConsistencyError("throughput calculation is biased")
    
    return np.linspace(1, len(ts_list_new), len(ts_list_new))/ts_list_new


def calc_th_fromdata(data, wup = True, m = 5):
    

    if wup:
        
           th = calc_th_seq_fromdata(data)
           return mean_and_confidence_interval(th[warmup_mser(th, m):])
       
    else:
    
        # Throughput
        # 1st estimate: from data: pieces / time
        th = calc_th_seq_fromdata(data)
            
        return mean_and_confidence_interval(th)

    
def calc_th_fromtraces(id_trace_record):
#    TODO deprecate this
    st = []  
    for idd in id_trace_record:    
        st.append ( idd['ts'][-1] -   idd['ts'][0])
        
    # 2nd estimate: last activity of all pieces --> inter service time  
    interser = np.diff(np.sort( [idd['ts'][-1] for idd in id_trace_record ]))
    TH2 = 1/ np.mean(interser) # 2nd estimate [pieces / udt]
    
    # Single operations
    # suppose i have merged 2 operations 
    #ops = [1,4]
    #set(ops).issubset(   id_trace_record[2]['trace']   )
    #result = [id_trace_record[2]['trace']  .index(i) for i in ops]
    #imin =result.index(   min(result) )
    #imax = result.index(   max(result))
    #result[imin] # indice del primo el nella traccia
    #result[imax] # indice del ultimo el nella traccia
    #id_trace_record[2]['ts'][     result[imin]       ]
    #id_trace_record[2]['ts'][     result[imax]      ]
    
    return TH2



# ******************* INTER-LEAVING TIME *******************

def calc_interleaving_seq(data, s = 1.0):
    
    
    """
    returns estimated interleaving time vector from a station
    
    """
    
    ts_list = []
       
    ts_list = np.sort(data[(data['activity'] == s) & (data['tag'] == 'f')]['ts'].values)
    
    return ts_list[1:] - ts_list[:-1]

def calc_interleavingtimes(data, s = 1, wup = True, m = 5):
    

    if wup:
        
           ilt = calc_interleaving_seq(data, s)
           return mean_and_confidence_interval(ilt[warmup_mser(ilt, m):])
       
    else:
    
        ilt = calc_interleaving_seq(data, s)
            
        return mean_and_confidence_interval(ilt)


# ******************* SYSTEM TIME *******************

def calc_st_fromdata(data):
    
    stlist = []
    idlist = data.id.unique()
    
    for id in idlist:
        
        tsvect = data[data.id == id].ts
        stlist.append( max(tsvect) - min(tsvect) )
        
    return mean_and_confidence_interval(stlist)




############################################################################################################
# STATISTICAL ANALISIS
############################################################################################################    


################################
## LOAD TRIAL MODEL
#with open(r'C:\Users\giova\OneDrive - Politecnico di Milano\WIP\MSM_experiments\config.json', encoding='utf-8') as f:
#    config = json.load(f)
#    
#data = pd.read_csv( config["datapath"] , sep=" ", header='infer')
#model, unique_list, tracetoremove, mappings = gen_model_init(data, config)
################################

def mean_and_confidence_interval(data, confidence=0.95):
    """
    function that returns the mean and the conficence interval of a data sample
    
    outuput = mean, (CI_l, CI_u)
    """
    
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, (m-h, m+h)


def find_flowtimes(final_model, data, tag = False, aggregate = True):
    
    try:
    #    TODO mettere controllo tag qui
        print("FINDING FLOWTIMES OF NEW MODEL")
        #  1.  interarrivals
        fn = find_first_node(final_model)
        
        c = next(n for n in final_model['nodes'] if n['cluster'] == fn)
        
        # check if this node is a cluster or not
        if isinstance(c['activity'], list): 
            # se vero è un cluster, devo trovare il primo nodo nel cluster   
            primatt = find_first_in_cluster(data, c['activity'])
        
        else:   # se falso, la prima attivita va bene
            primatt = c['activity']
    
        c['interarrivals'] = find_interarrivals(data, primatt, tag)
    except:
        print("Could not estimate interarrivals")
    
    # 2. processing times
    for c in tqdm( final_model['nodes'] , position=0, leave=True):
        
        if isinstance(c['activity'],list) and aggregate:
    #        TODO ATTENTION! modified with division /nr. of stations. OK FOR FLOWLINE, NOT FOR PARALLEL!!!!!
#            c['flowtimes'] = flowtimes_among_cluster(data, c['activity'], tag) / len(c['activity'])
#            take interexittimes
            c['flowtimes'] = exittimes_from_cluster(data, c['activity'], tag)
        else:
            c['flowtimes'] = flowtimes_among_cluster(data, c['activity'], tag) 
            
    return final_model  
  

#assumo ok senza cluster
# funzione per interarrivals sull'1
    
def find_interarrivals(data, activity = 1, tag = False):

    """
    function that given the event log returns the interarrivals over a certain activity
    
    ATTENTION: depends on tag
    if start/finish tag is present, will take the interarrivals as flow times between start activities
    if not, will take interarrivals as flow times between the only time stamp of the activity
    """
        
    if tag:
        ts = np.array(data[(data['activity'] == activity) & (data['tag'] == 's')].sort_values(by=['ts']).ts)
        intarrivals = ts[1:] - ts[:-1]
    else:
        ts = np.array(data[data['activity'] == activity].sort_values(by=['ts']).ts)
        intarrivals = ts[1:] - ts[:-1]
    
    return intarrivals.tolist()


def find_first_in_cluster(data, cluster):
    
    """
    given eventlog and cluster in list format (example: [1,2,3])
    returns the name of the first activity as in the log
    """
    
    # prendo lista degli id
    id_u = data.id.unique().tolist()
    
    # inizializzo dizionario con scores
    scores = {}
    for element in cluster:
        scores[str(element)] = 0
    
    # non bellissimo perche non tutti gli id potrebbero fare le attività
    for element in id_u:
    
        a = data[(data.id == element)].sort_values(by=['ts']).activity.values[0]
        
#        if len(a) == 0:
#            continue
        
        scores[str(a)] += 1


    return max(scores.items(), key=operator.itemgetter(1))[0]





def flowtimes_between_clusters(data, c1, c2):
    
    """
    Function that given an event log and two clusters of events (list format like c1 = [1], c2 = [2,3])
    returns the inter flow times between those two clusters
    
    the function does not include negative values, hence a null array suggests an inverse relationship such as c2 --> c1
    """

    id_u = data.id.unique().tolist()
    
    it = []
    
    for element in id_u:
        
    #check if both activities are in log of that ID
        set( c1 + c2   ).issubset(   set( data[(data.id == element)].activity.values.tolist()   )  )
        
    # smallest ts in c1
        sc1 = data[(data.id == element) & (data.activity.isin(c1) )].sort_values(by=['ts']).ts.values[0]
    
    # largest ts in c2
        lc2 = data[(data.id == element) & (data.activity.isin(c2) )].sort_values(by=['ts']).ts.values[-1]
    
        it.append(lc2 - sc1)
        
    it = np.array(it)
    
    return it[it>0]





def flowtimes_among_cluster(data, cluster, tag = False):
    
    """
    Function that given an event log and ONE cluster of events (list format like c = [2,3])
    returns the inter flow times between activities in the cluster
    
    ATTENTION! IF CLUSTER IS SINGLE EVENT IT TAKES MIN-MAX TIMESTAMPS!
    

    """

    # TODO WHAT IF SINGLE CLUSTER WITH tag = FALSE?
    if tag == True:
            
        #correct the format of c1 cluster (if it's not a list, make it so)
        if not(isinstance(cluster, list)):
            cl = []
            cl.append(cluster)
        else:
            cl = cluster
        
    #    if len(cluster) <2:
    #        raise Exception("Size of cluster is "+str(len(cluster)) +", insufficient for calculation")
    
        id_u = data.id.unique().tolist()
        
        it = []
        
        for element in id_u:
            
        #check if both activities are in log of that ID
            
            if set( cl  ).issubset(   set( data[(data.id == element)].activity.values.tolist()   )  ):
            
            # timestamps:
            # non serve modificare con start/finish tag se prendo max - min???
                ts = data[(data.id == element) & (data.activity.isin(cl) )].ts.values
            
                if len(ts)>0:
                    # largest ts in c2
                    it.append(max(ts) - min(ts))
                    
            else:
                continue
                
        it = np.array(it)
        
        return it[it>0]
    
    elif tag == False:
        
        #correct the format of c1 cluster (if it's not a list, make it so)
        if not(isinstance(cluster, list)):
            cl = []
            cl.append(cluster)
        else:
            cl = cluster
        
    #    if len(cluster) <2:
    #        raise Exception("Size of cluster is "+str(len(cluster)) +", insufficient for calculation")
    
        id_u = data.id.unique().tolist()
        
        it = []
        
        for element in id_u:
            
        #check if both activities are in log of that ID
            
            if set( cl  ).issubset(   set( data[(data.id == element)].activity.values.tolist()   )  ):
            
            # timestamps:
            # non serve modificare con start/finish tag se prendo max - min???
                ts = data[(data.id == element) & (data.activity.isin(cl) )].ts.values
            
                it.append(ts)
                    
                
        it = np.array(it)
        
        it_new = it[1:] - it[:-1]
        
        return it_new[it_new>0]


def exittimes_from_cluster(data, cluster, tag = False):
    
    """
    Function that given an event log and ONE cluster of events (list format like c = [2,3])
    returns the inter EXIT times between activities in the cluster
        
    """
    
    if not(isinstance(cluster, list)):
        cl = []
        cl.append(cluster)
    else:
        cl = cluster
    
#    if len(cluster) <2:
#        raise Exception("Size of cluster is "+str(len(cluster)) +", insufficient for calculation")

    id_u = data.id.unique().tolist()
    
    ie = []
    
    for element in id_u:
        
    #check if both activities are in log of that ID
        
        if set( cl  ).issubset(   set( data[(data.id == element)].activity.values.tolist()   )  ):
        
        # timestamps:
        # non serve modificare con start/finish tag se prendo max - min???
            
            ts = max(data[(data.id == element) & (data.activity.isin(cl) ) & (data.tag == 'f' )].ts.values)
        
#            if len(ts)>0:
#                # largest ts in c2
#                it.append(max(ts) - min(ts))
            ie.append(ts)
                
        else:
            continue
            
    iexittimes = np.diff(np.sort(np.array(ie)))
    
    return iexittimes[iexittimes>0]




def calc_nodes_dist(model_w_flowtimes, data):

    for node in model_w_flowtimes['nodes']:
    
        # statistiche descrittive
        node['stats'] = {}
        
        node['stats']['mean'] = np.mean(np.array(node['flowtimes']))
        node['stats']['std'] = np.std(np.array(node['flowtimes']))
        
        # fit distribution
        dst = Distribution()
        #dst.dist_results
        node['stats']['dist'] = dst.Fit(node['flowtimes'])[0]
        node['stats']['params'] = dst.params[ node['stats']['dist'] ]
        
    return model_w_flowtimes

# def calc_nodes_dist(activity_corr_data, data):

#     for ad in activity_corr_data:
    
#         #ad['activity']  anzichè  activity_corr_data[0]
        
#         # estraggo log con questa attivita
#         temp = list(data[data['activity'] == ad['activity']].sort_values(by=['ts'])['ts'])   # do not use loc here, otherwise i get warnings later
        
        
#         # creo vettore intertempi
#         iproc = []    
#         for i in range(len(temp)-1):
#             iproc.append(temp[i+1] - temp[i])
    
#         # statistiche descrittive
#         ad['mean'] = np.mean(np.array(iproc))
#         ad['std'] = np.std(np.array(iproc))
        
#         # fit distribution
#         dst = Distribution()
#         #dst.dist_results
#         ad['dist'] = dst.Fit(iproc)[0]
#         ad['params'] = dst.params[ad['dist']]
    
#         # opzionale creo grafico (hist)
#         #plt.hist(iproc)
#         #dst.Plot(iproc)
        
#     return activity_corr_data


    
def calc_arcs_dist(capacity_data, data):

    
#ATTENZIONE FLOW TIMES NON SONO PIU IN CAPACITY DATA
    
    #stessa cosa fatta su archi! (prendo intertempi tra una parte e la successiva)
    for cd in capacity_data:
        
        # statistiche descrittive
        cd['mean'] = np.mean(np.array(cd['flowtimes']))
        cd['std'] = np.std(np.array(cd['flowtimes']))
    
        # fit distribution
        dst = Distribution()
        #dst.dist_results
        cd['dist'] = dst.Fit(cd['flowtimes'])[0]
        cd['params'] = dst.params[cd['dist']]
        
    return capacity_data



###############################################################################
# AUTO-CORRELATION CHECK
###############################################################################



def autocorr(x, t=1):
    
    return np.corrcoef(np.array([x[:-t], x[t:]]))


def check_autocorr(x):
    
    w = 0
    
    for t in range( int(len(x)/2) - 1):
#        print(t)
        y = autocorr(x, t+1)
        
        if y[0,1] == 1 or y[0,1] == -1:
            continue
        
        if (y[0,1]< -0.6) or (y[0,1]> 0.6):
            w = w + 1
            
        if (y[0,1]< -0.8) or (y[0,1]> 0.8):
            
            return 1,t
            
    return w/t
        

###############################################################################
# FIT EMPIRICAL DISTRIBUTION 
###############################################################################


def ecdf(data):
    
    """ Compute ECDF """
    
    x = np.sort(data)
    n = x.size
    y = np.arange(1, n+1) / n
    
    return (x,y)


def gen_from_ecdf(x, parts):
    
    """ Generate data from ECDF """
    sample = []
    sort = sorted(x)
    
    for i in range(parts):
        sample.append( sort[int(len(x) * np.random.random())] )
        
    return sample


#def gen_from_ecdf2(x, parts):
#    
#    """ Generate data from ECDF """
#    sample = []
#    
#    for i in range(parts):
#        sample.append( np.quantile(x, q=np.random.random() )   )
#        
#    return sample
    
###############################################################################
# FIT KERNEL DISTRIBUTION 
###############################################################################


def make_data(N, mean = 1.0, rseed=1234567):
    np.seed = rseed 
#    rand = np.random.RandomState(rseed)
    x = np.random.exponential(1/mean,N)
#    x[int(f * N):] += 5
    return x



def fit_kernel(x, Kernel = 'gaussian', rot = False):
    
    """
    Function that determines the  kernel density estimator of an array of data x!
    
    DEFAULT KERNEL IS GAUSSIAN!
    
    DEPENDS ON FUNCTIONS: decide_bandwith

    INPUT: np array of data
    OUTPUT: KDE OBJECT!

    example     decide_bandwith(  np.array([1,2,3,4,5,])  ) --> 1.2
    
    NOTES ON: https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html
    
    REFERENCE: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KernelDensity.html
    
    """

    if isinstance(x,(list,pd.core.series.Series,np.ndarray)):
        
        x = np.array(x)
        
        # instantiate and fit the KDE model
        kde = KernelDensity(bandwidth = decide_bandwith(x, Kernel, rot), kernel=Kernel)
        kde.fit(x[:, None])
        
        return kde
        
    else:
        raise Exception('wrong type')


def decide_bandwith(x, Kernel = 'gaussian', rot = False, default_bw = 0.1):
    """
    Function that determines the optimal bandwith of a kernel density estimator.
    
    DEFAULT KERNEL IS GAUSSIAN!

    INPUT: np array of data
    OUTPUT: OPTIMAL BANDWITH VALUE

    example     decide_bandwith(  np.array([1,2,3,4,5,])  ) --> 1.2
    
    NOTES ON: https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html
    """
    
    
    if isinstance(x,(list,pd.core.series.Series,np.ndarray)):
        
        x = np.array(x)
        
        
        if rot:
#             use rule of thumb to decide (Silvaeman, da tesi cornaggia)
        
            sd = np.std(x)
            iqr = np.subtract(*np.percentile(x, [75, 25]))
            bw = np.min([sd, iqr/1.349]) * np.size(x)**(-1/5)
            
            if bw <= 0:
                warn("KDE BANDWIDTH WAS "+str(bw)+"; USING DEFAULT VALUE:"+str(default_bw), stacklevel=2)
                return default_bw
            else:
                return  bw
                
        else:
            # CV to decide bandwidth
            bandwidths = 10 ** np.linspace(-1, 1, 100)
            grid = GridSearchCV(KernelDensity(kernel=Kernel),
                            {'bandwidth': bandwidths},
                            cv=5)
            grid.fit(x[:, None]);
            
            return grid.best_params_['bandwidth']
        
    else:
        raise Exception('wrong type')
        

def gen_pos_kernel_samples(kd, parts, seed):
    
    """
    kd : kernel density estimator object
    parts: number of parts I want to simulate
    seed: seed used for RNG
    
    """
    
    i = 1
    y = np.array([])
    
    while np.size(y) < parts:
    
        N = i * 100
    
        x = kd.sample(N*parts,seed)
        
        y = x [x > 0]
        
        y = y[0:parts]
        
        i = i + 1
        
    return y

    
def gen_samples(kde, parts, max_iters = 1000):
    
    """
    function that given a kernel density estimation object as inpyt (scikit), the number of parts 
    
    returns a vector of positive samples of length equal to the number of parts (parts)
    
    max - iters imposes an upper limit to the iterations
    
    raises MaxIterationsReached exeptio if max nr. of iter. is reached
    """
    seeds = []
    seed = np.random.randint(1,10000)
    seeds.append(seed)
    x_new = gen_pos_kernel_samples(kde, parts, seed)
    
#    i = 0
#    while check_autocorr(x_new.tolist()) > 0:
#    
#        
#        if seed in seeds:
#            seed = np.random.randint(1,10000)
#        
#        seeds.append(seed)
#        
#        x_new = gen_pos_kernel_samples(kde, parts, seed)
#        
#        i = i + 1
#        if i > max_iters:
#            
#            raise MaxIterationsReached("Reached Max Iters in Autocorr Checking")
#            break
        
    return x_new

###############################################################################

class Distribution(object):
    
    def __init__(self,dist_names_list = []):
        self.dist_names = ['norm','lognorm','expon']
        self.dist_results = []
        self.params = {}
        
        self.DistributionName = ""
        self.PValue = 0
        self.Param = None
        
        self.isFitted = False
        
        
    def Fit(self, y):
        self.dist_results = []
        self.params = {}
        for dist_name in self.dist_names:
            dist = getattr(scipy.stats, dist_name)
            param = dist.fit(y)
            
            self.params[dist_name] = param
            #Applying the Kolmogorov-Smirnov test
            D, p = scipy.stats.kstest(y, dist_name, args=param);
            self.dist_results.append((dist_name,p))
        #select the best fitted distribution
        sel_dist,p = (max(self.dist_results,key=lambda item:item[1]))
        #store the name of the best fit and its p value
        self.DistributionName = sel_dist
        self.PValue = p
        self.isFitted = True
        return self.DistributionName,self.PValue
    
    def Random(self, n = 1):
        if self.isFitted:
            dist_name = self.DistributionName
            param = self.params[dist_name]
            #initiate the scipy distribution
            dist = getattr(scipy.stats, dist_name)
            return dist.rvs(*param[:-2], loc=param[-2], scale=param[-1], size=n)
        else:
            raise ValueError('Must first run the Fit method.')
            
    def Plot(self,y):
        x = self.Random(n=len(y))
        plt.hist(x, alpha=0.5, label='Fitted')
        plt.hist(y, alpha=0.5, label='Actual')
        plt.legend(loc='upper right')