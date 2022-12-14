# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 21:20:49 2021

@author: franc
"""
import paho.mqtt.client as mqtt
import json
import pandas as pd
import pickle

#import datetime
import time
import datetime
from time import sleep
import numpy as np

# ADDED to query
from influx import InfluxDB
from influxdb import InfluxDBClient

# def processing_time(data):
#     number_activity = len(data['activity'].unique()) #number of stations identification
#     number_id=[] 
#     for actx in range(1,number_activity+1):
#         number_id.append((len(data[data['activity']==actx].id.unique())))   # number of pallets(parts) acquired
  
#     processing_time = pd.DataFrame(index = range(1,min(number_id)), columns= range(1,number_activity + 1)) #creation of DF for allocating processing times stamp
    
#     for idx in range(1,number_activity+1):  
#         n=int(max(data[data['activity']==idx].id.unique()) )
       
#         for i in range(1,n+1):
                        
#             id_s= data.loc[(data['type']=="s") & (data['activity']==idx) & (data['id']==i)]
#             time_id_s = id_s['time']
            
#             id_f = data.loc[(data['type']=="f") & (data['activity']==idx) & (data['id']==i)]
#             time_id_f = id_f['time']
            
            
#             if(len(time_id_s)==0 or len(time_id_f)==0):
#                 print("processing time calculation missing for id:", i)
#             else:
#                  processing_time[idx][i]= int(time_id_f) - int(time_id_s) #idx: number of stations i: number of pallets
                 
     
#     #  #Saving
     
#     # for actx in range(1,number_activity+1):
#     #     with open("C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/Processing_time_S"+str(actx)+".txt",mode="w") as Processing_time_Sactx:
#     #         Processing_time_Sactx.write( processing_time[actx].dropna().to_string(header=False, index=False))       
#     #         Processing_time_Sactx.close()    
#     #     with open(r"C:\Users\franc\Desktop\Tesi_magistrale\Model\Data extraction\Processing_time",mode= "wb") as Processing_time:
#     #         pickle.dump(processing_time,Processing_time)
#     #         Processing_time.close()

    
#     return processing_time


def processing_time(data):
    df_c=data
    number_activity = len(df_c['activity'].unique()) #number of stations identification
    number_id=[] 
    for actx in range(1,number_activity+1):
         number_id.append((len(df_c[df_c['activity']==actx].id.unique())))   # number of pallets(parts) acquired
    
    processing_time_test = pd.DataFrame(index = range(1,2*max(number_id)), columns=['activity','part_id','value']) #creation of DF for allocating processing times stamp
    
    idy=1
    for idx in range(1,number_activity+1):  
        n_min=int(min(df_c[df_c['activity']==idx].id.unique()))
        n_max=int(max(df_c[df_c['activity']==idx].id.unique()))
        
                   
        for i in range(n_min,n_max+1):
            
            
            id_s= df_c.loc[(df_c['type']=="s") & (df_c['activity']==idx) & (df_c['id']==i)]
            time_id_s = id_s['time']
            
            
            id_f = df_c.loc[(df_c['type']=="f") & (df_c['activity']==idx) & (df_c['id']==i)]
            time_id_f = id_f['time']
            
            
            if(len(time_id_s)==0 or len(time_id_f)==0):
                print("processing time calculation missing for id:", i)
            else:
                 
                 processing_time_test['activity'][idy]=idx
                 processing_time_test['value'][idy]=int(time_id_f) - int(time_id_s)
                 processing_time_test['part_id'][idy] =i
              
                 idy=idy+1

    processing_time_test=processing_time_test.dropna()
    
    return processing_time_test


def processing_time_Arena(data):
    
    df_c=data
    number_activity = len(df_c['activity'].unique()) #number of stations identification
    number_id=[] 
    for actx in range(1,number_activity+1):
         number_id.append((len(df_c[df_c['activity']==actx].id.unique())))   # number of pallets(parts) acquired
    
    processing_time_test = pd.DataFrame(index = range(1,2*max(number_id)), columns=['activity','part_id','value']) #creation of DF for allocating processing times stamp
    
    idy=1
    for idx in range(1,number_activity+1):  
        n_min=int(min(df_c[df_c['activity']==idx].id.unique()))
        n_max=int(max(df_c[df_c['activity']==idx].id.unique()))
        
                   
        for i in range(n_min,n_max+1):
            
            
            id_s= df_c.loc[(df_c['type']=="s") & (df_c['activity']==idx) & (df_c['id']==i)]
            time_id_s = id_s['time']
            
            
            id_f = df_c.loc[(df_c['type']=="f") & (df_c['activity']==idx) & (df_c['id']==i)]
            time_id_f = id_f['time']
            
            
            if(len(time_id_s)!=0 and len(time_id_f)!=0):
             
                 
                processing_time_test['activity'][idy]=idx
                processing_time_test['value'][idy]=int(time_id_f) - int(time_id_s)
                processing_time_test['part_id'][idy] =i
             
                idy=idy+1

    processing_time_test=processing_time_test.dropna()
    
    
    
    
    p_timesimul_input= pd.DataFrame(index = range(0,len(processing_time_test)),
                                    columns=[i for i in range(1,max(processing_time_test['activity'])+1)]+['part_id'])
    
    for actx in range(1,int(max(processing_time_test['activity']))+1):
        
        p_timesimul_column_candidate=processing_time_test.loc[(processing_time_test['activity']==actx)]
        p_timesimul_column_candidate.reset_index(drop=True)
        
        for i in range(0,len(p_timesimul_column_candidate)):
                                    
            p_timesimul_input[actx][i]=p_timesimul_column_candidate.iloc[i]['value']
            p_timesimul_input['part_id'][i]=p_timesimul_column_candidate.iloc[i]['part_id']
    
    
    p_timesimul_input=p_timesimul_input.dropna(how="all")
    
    p_timereal_Nan_count=[]
    
    for actx in range(1,p_timesimul_input.shape[1]):
        
        for i in range(0,p_timesimul_input.shape[0]):
            
            if pd.isna(p_timesimul_input[actx][i])==True:
                p_timereal_Nan_count.append([actx,p_timesimul_input['part_id'][i]])
    
    if len(p_timereal_Nan_count)!=0:
                       
        print('Processing Times Incomplete ATM:[Activity, Part_id] :')
        print(p_timereal_Nan_count)
        
    
    p_timesimul_input = p_timesimul_input.drop('part_id', axis='columns')
    
    
    return p_timesimul_input

def processing_time_Manpy(data):
    
    df_c=data
    number_activity = len(df_c['activity'].unique()) #number of stations identification
    number_id=[] 
    for actx in range(1,number_activity+1):
         number_id.append((len(df_c[df_c['activity']==actx].id.unique())))   # number of pallets(parts) acquired
    
    processing_time_test = pd.DataFrame(index = range(1,2*max(number_id)), columns=['activity','part_id','value']) #creation of DF for allocating processing times stamp
    
    idy=1
    for idx in range(1,number_activity+1):  
        n_min=int(min(df_c[df_c['activity']==idx].id.unique()))
        n_max=int(max(df_c[df_c['activity']==idx].id.unique()))
        
                   
        for i in range(n_min,n_max+1):
            
            
            id_s= df_c.loc[(df_c['type']=="s") & (df_c['activity']==idx) & (df_c['id']==i)]
            time_id_s = id_s['time']
            
            
            id_f = df_c.loc[(df_c['type']=="f") & (df_c['activity']==idx) & (df_c['id']==i)]
            time_id_f = id_f['time']
            
            
            if(len(time_id_s)!=0 and len(time_id_f)!=0):
                
                processing_time_test['activity'][idy]=idx
                processing_time_test['value'][idy]=int(time_id_f) - int(time_id_s)
                processing_time_test['part_id'][idy] =i
             
                idy=idy+1

    processing_time_test=processing_time_test.dropna()
    
    
    
    
    p_timesimul_input= pd.DataFrame(index = range(0,len(processing_time_test)),
                                    columns=[i for i in range(1,max(processing_time_test['activity'])+1)]+['part_id'])
    
    for actx in range(1,int(max(processing_time_test['activity']))+1):
        
        p_timesimul_column_candidate=processing_time_test.loc[(processing_time_test['activity']==actx)]
        p_timesimul_column_candidate.reset_index(drop=True)
        
        for i in range(0,len(p_timesimul_column_candidate)):
                                    
            p_timesimul_input[actx][i]=p_timesimul_column_candidate.iloc[i]['value']
            p_timesimul_input['part_id'][i]=p_timesimul_column_candidate.iloc[i]['part_id']
    
    
    p_timesimul_input=p_timesimul_input.dropna(how="all")
    
    p_timereal_Nan_count=[]
    
    for actx in range(1,p_timesimul_input.shape[1]):
        
        for i in range(0,p_timesimul_input.shape[0]):
            
            if pd.isna(p_timesimul_input[actx][i])==True:
                p_timereal_Nan_count.append([actx,p_timesimul_input['part_id'][i]])
    
    if len(p_timereal_Nan_count)!=0:
                       
        print('Processing Times Incomplete ATM:[Activity, Part_id] :')
        print(p_timereal_Nan_count)
        
    
    p_timesimul_input = p_timesimul_input.drop('part_id', axis='columns')
    
    for actx in range(1,p_timesimul_input.shape[1]+1):
        p_timesimul_input[actx]=p_timesimul_input[actx].dropna()
        p_timesimul_input =  p_timesimul_input.rename(columns={actx: 'M'+str(actx)})
    
    return p_timesimul_input



    
