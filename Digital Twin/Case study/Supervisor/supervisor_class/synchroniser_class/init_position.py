# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 15:55:55 2021

@author: franc
"""
import pandas as pd

def init_position(source_type,n_pallet,data):
    data=data
    if source_type=='sensors':
    
        number_activity = len(data['activity'].unique()) #number of stations identification
        # number_id=[] 
        # for actx in range(1,number_activity+1):
        #     number_id.append((len(data[data['activity']==actx].id.unique())))   # number of pallets(parts) acquired
      
        init_pos = pd.DataFrame(index = range(1,n_pallet+1), columns=['location','part_id'])
        
        #test=min(data.loc[(data['type']=="s")]['id'])+(self.n_pallet-1)
        test=min(data['id'])+(n_pallet-1)

        loc_id = data[data['id']<=test].drop_duplicates(subset=['id'],keep='first') #only the first Scan are kept, this to be correlated to the extraction of processing times
       
        for actx in range(1,number_activity+1):
           for i in range(0,n_pallet): #for all IDs
               if actx!=number_activity: #not in the last station
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 'f'):
                       init_pos.iloc[i,0]= actx+1
                       init_pos.iloc[i,1]=loc_id.iloc[i,2]
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 's'):
                       init_pos.iloc[i,0]=actx  
                       init_pos.iloc[i,1]=loc_id.iloc[i,2]
               else:
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 'f'):
                       init_pos.iloc[i,0]= 1
                       init_pos.iloc[i,1]=loc_id.iloc[i,2]
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 's'):
                       init_pos.iloc[i,0]=actx 
                       init_pos.iloc[i,1]=loc_id.iloc[i,2]
        
        return init_pos
        

        
    if source_type== 'camera':
        return init_pos
    