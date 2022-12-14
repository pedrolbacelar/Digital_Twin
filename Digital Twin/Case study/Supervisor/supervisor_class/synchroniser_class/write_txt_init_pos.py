# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 15:59:26 2021

@author: franc
"""

def write_txt_init_pos(data,directory=None,file_name=None):
    
    data =data
    
    # if directory==None:
    #     print('Routing.txt has not a directory')
    
    if file_name==None:
        print('Routing.txt is not directed to a file_name')
    
    with open(str(directory)+str(file_name),mode="w") as Routing:
         Routing.write(data['location'].to_string(header=False, index=False))       
         Routing.close()   
    