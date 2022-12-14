# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 15:14:35 2021

@author: franc
"""


#Function to write on file txt to then be used by arena.
#directory is wehre the file is placed
#file_name: is the file name !!!! pay attention it has to be the same on Arena


def write_txt_processing_time(data,directory=None,file_name=None):
    
    if directory==None:
        print('Processing_time.txt has not a directory')
    
    if file_name==None:
        print('Processing_time.txt is not directed to a file_name')
    
    
    for actx in range(1,data.shape[1]):
        with open(str(directory)+str(file_name)+str(actx)+".txt",mode="w") as Processing_time_Sactx:
            Processing_time_Sactx.write( (data[actx].dropna()).to_string(header=False, index=False))       
            Processing_time_Sactx.close()

def write_txt_processing_time_validator(data,directory=None,file_name=None):
    
    if directory==None:
        print('Processing_time.txt has not a directory')
    
    if file_name==None:
        print('Processing_time.txt is not directed to a file_name')
    
    
    for actx in range(0,data.shape[1]):
        with open(str(directory)+str(file_name)+str(actx+1)+".txt",mode="w") as Processing_time_Sactx:
            Processing_time_Sactx.write( ((data.iloc[:,actx].dropna()).astype(int)).to_string(header=False, index=False))       
            Processing_time_Sactx.close()
    