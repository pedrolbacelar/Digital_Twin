# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 15:15:18 2021

@author: franc
"""
import pandas as pd

def final_position(source_type,n_pallet,data):
    data=data
    if source_type=='sensors':
    
        
       
        
        number_activity = len(data['activity'].unique()) #number of stations identification
        number_id=[] 
        for actx in range(1,number_activity+1):
            number_id.append((len(data[data['activity']==actx].id.unique())))   # number of pallets(parts) acquired
      
        end_pos = pd.DataFrame(index = range(1,n_pallet+1), columns=['location','part_id'])
        
        #test=min(data.loc[(data['type']=="s")]['id'])+(self.n_pallet-1)
        test=max(data['id'])-(n_pallet)+1

        loc_id = data[data['id']>=test].drop_duplicates(subset=['id'],keep='last') #only the first Scan are kept, this to be correlated to the extraction of processing times
       
        for actx in range(1,number_activity+1):
           for i in range(0,n_pallet): #for all IDs
               if actx!=number_activity: #not in the last station
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 'f'):
                       end_pos.iloc[i,0]= actx+1
                       end_pos.iloc[i,1]=loc_id.iloc[i,2]
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 's'):
                       end_pos.iloc[i,0]=actx  
                       end_pos.iloc[i,1]=loc_id.iloc[i,2]
               else:
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 'f'):
                       end_pos.iloc[i,0]= 1
                       end_pos.iloc[i,1]=loc_id.iloc[i,2]
                   if(loc_id.iloc[i,1] ==actx and loc_id.iloc[i,3] == 's'):
                       end_pos.iloc[i,0]=actx 
                       end_pos.iloc[i,1]=loc_id.iloc[i,2]
        
        return end_pos
        

   
    if source_type== 'camera':
        return end_pos