# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 10:42:32 2021

@author: user
"""
import numpy as np

def ecdf(data):
    """ Compute ECDF """
    dati=np.unique(data)
    x = np.sort(dati)
    n = x.size
    y = np.arange(1, n+1) / n
    return(x,y)

