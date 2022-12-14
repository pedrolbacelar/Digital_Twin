# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 10:35:23 2021

@author: franc
"""
import warnings
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm
from scipy.stats._continuous_distns import _distn_names
import matplotlib
import matplotlib.pyplot as plt
import pickle
from supervisor_class.database_class.interface_DB import interface_DB
import pandas as pd



matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
matplotlib.style.use('ggplot')
dists_avlb =['norm','beta','gamma','triang','uniform','pareto','lognorm','logistic','rayleigh']

def best_fit_distribution(data, bins=80, ax=None):
    """Model data by finding best fit distribution to data"""
    # Get histogram of original data
    y, x = np.histogram(data, bins=bins, density=True)
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Best holders
    best_distributions = []

    # Estimate distribution parameters from data
    #for ii, distribution in enumerate([d for d in _distn_names if not d in ['levy_stable', 'studentized_range']]):
    for ii, distribution in enumerate([d for d in dists_avlb if not d in ['levy_stable', 'studentized_range']]):

        #print("{:>3} / {:<3}: {}".format( ii+1, len(_distn_names), distribution ))
        print("{:>3} / {:<3}: {}".format( ii+1, len(dists_avlb), distribution ))
        
        distribution_name =distribution

        distribution = getattr(st, distribution)

        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                
                # fit dist to data
                params = distribution.fit(data)

                # Separate parts of parameters
                arg = params[:-2]
                loc = params[-2]
                scale = params[-1]
                
                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse = np.sum(np.power(y - pdf, 2.0))
                
                # if axis pass in add to plot
                try:
                    if ax:
                        pd.Series(pdf, x).plot(ax=ax)
                    end
                except Exception:
                    pass

                # identify if this distribution is better
                
                
                
                
                best_distributions.append((distribution_name, params, sse))
        
        except Exception:
            pass

    
    return sorted(best_distributions, key=lambda x:x[2])

def dist_fit(db,t_horizon):
    #query processing_times
    p_time=db.queryData("processing_time_real_Arena","real_perf",t_horizon)
    
    best_dist_pd=pd.DataFrame(columns=[i for i in range(min(p_time['activity']),max(p_time['activity'])+1)])
    
    for actx in range(min(p_time['activity']),max(p_time['activity'])+1):
        data=p_time.loc[(p_time['activity']==actx)]['value']
        best_distributions = best_fit_distribution(data, 20)
        best_dist = best_distributions[0]
        best_dist_pd.loc[1,actx]=str(best_dist[0])
        best_dist_pd.loc[2,actx]=str(list(best_dist[1]))
        best_dist_pd.loc[3,actx]=str((best_dist[2]))
    
    db.writeData("processing_times_dist_fitter","distributions",best_dist_pd)
    
    
    return best_dist_pd
    #write best_dist per procesing_1 and 2
    