# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 17:15:18 2021

@author: franc
"""

import pandas as pd

def interdeparture_time_real(data):
   
    df_c=data
    
    id_max_completed=max(df_c[df_c['activity']==1]['id'])
    id_min_completed=min(df_c[df_c['activity']==1]['id'])
      
    Inter_dep=pd.DataFrame(index = range(1,id_max_completed+1), columns= ['part_id','value'])
   
    for i in range(id_min_completed,id_max_completed+1):
        
        time_id_departedA=df_c.loc[(df_c['id']==i) & (df_c['activity']==1) & (df_c['type']=='s')]['time']
        time_id_departedB=df_c.loc[(df_c['id']==i+1) & (df_c['activity']==1) & (df_c['type']=='s')]['time']
        
        if time_id_departedA.empty or time_id_departedB.empty:
            
            print(i,"'th interdeparture time not acquired")        
        else:
            Inter_dep.iloc[i-1,0]=min(df_c.loc[(df_c['id']==i)]['id'])
            
            Inter_dep.iloc[i-1,1]=float(time_id_departedB) - float(time_id_departedA)
            
            
    Inter_dep= Inter_dep.dropna()   
    
    return Inter_dep

