# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 19:09:21 2021

@author: franc
"""

import pandas as pd


def read_txt_digital_eventlog(directory=None,file_name=None):
    
    if directory==None:
        print('directory not declared for digital_eventlog')
    
    if file_name==None:
        print('file_name not declared for digital_eventlog')
   
    
    data= pd.read_csv(str(directory) + str(file_name),names=['timelog','activity','type'], header = None,sep=" ",index_col=False)
    
    
 
    
    
    
    return data.dropna()
    
