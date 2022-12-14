# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 13:52:20 2021

@author: franc
"""


import pandas as pd


def read_txt_digital_final_position(n_pallet,directory=None,file_name=None):
    
    if directory==None:
        print('directory not declared for digital_final_position')
    
    if file_name==None:
        print('file_name not declared for digital_final_position')
    
    data= pd.read_csv(str(directory) + str(file_name), header = None,sep=",",index_col=False)  #la cella 0:1 mi da i
    
    end_pos=pd.DataFrame( index = range(1,n_pallet+1),columns=['location'])
    
    
    for idx in range(0,data.iloc[0][1]+1):

        end_pos.iloc[idx][0]=1

    end_pos=end_pos.fillna(value=2)
    
    
    return end_pos
            
            
        
    
 