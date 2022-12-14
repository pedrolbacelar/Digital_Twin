# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 16:28:30 2021

@author: franc
"""
import pandas as pd

"""
System Time determined when a pallet determined a start on station 2 
and the the same pallet with new part_id determined a start on station 2
"""

def system_time_real(n_pallet,data):
    data = data
    df_c = data
    
    
    number_activity = len(df_c['activity'].unique()) #number of stations identification
    #number_id=[]
    
    id_max_completed=max(df_c[df_c['activity']==2]['id'])
    id_min_completed=min(df_c[df_c['activity']==2]['id'])


    S_time=pd.DataFrame(index = range(1,id_max_completed+1), columns= ['part_id','value','timelog'])
    S_time_Nan_count=[]
    for i in range(id_min_completed,id_max_completed+1):
        try:
            time_id_initial=df_c.loc[(df_c['id']==i) & (df_c['activity']==1) & (df_c['type']=='s')].iloc[0][0]
            time_id_completed=df_c.loc[(df_c['id']==i+n_pallet) & (df_c['activity']==1) & (df_c['type']=='s')].iloc[0][0]
            #th[1][i]=min(df_c.loc[(df_c['id']==i+n_pallet)]['time']) - max(df_c.loc[(df_c['id']==i)]['time'])
            
              
        
            S_time.iloc[i-1,0]=min(df_c.loc[(df_c['id']==i)]['id'])
            S_time.iloc[i-1,1]=int(time_id_completed) - int(time_id_initial)
            S_time.iloc[i-1,2]=time_id_completed
     
        except IndexError:
            #time_id_completed.empty or time_id_initial.empty:
            print('id',i,' System time Real not acquired') 
            
    S_time= S_time.dropna()   
        
    return S_time
    
