# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 16:09:29 2021

@author: franc
"""
import pandas as pd


def read_txt_system_time_digital(n_pallet,directory=None,file_name=None):
    
    if directory==None:
        print('directory not declared for system time digital')
    
    if file_name==None:
        print('file_name not declared for system time digital')
    
    
    data= pd.read_csv(str(directory) + str(file_name),names=['System Time Digital','timelog'], header = None,sep=" ",index_col=False)
    
    data=data[n_pallet+1:]
    data['timelog']=data['timelog']- min(data['timelog'])
    data['timelog']=data['timelog']+ data.iloc[0][0]
 
    
    
    
    return data.dropna()
    
