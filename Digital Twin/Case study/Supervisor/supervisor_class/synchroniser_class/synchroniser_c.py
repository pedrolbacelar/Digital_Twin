# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:12:23 2021

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
from influxdb import DataFrameClient

import threading

#simulator: Arena
import os

#personal libraries
from database_class.interface_DB import interface_DB
from analytics.processing_time import processing_time
from analytics.system_time_real import system_time_real
from analytics.interdeparture_time_real import interdeparture_time_real 

from synchroniser_class.write_txt_processing_time import write_txt_processing_time
from synchroniser_class.init_position import init_position


from synchroniser_class.read_txt_system_time_digital import read_txt_system_time_digital
from synchroniser_class.read_txt_digital_eventlog import read_txt_digital_eventlog
from synchroniser_class.write_txt_init_pos import write_txt_init_pos
from synchroniser_class.read_txt_digital_final_position import read_txt_digital_final_position

#Edo's libraries
from simulator_class.manpy.DigitalModel import DigitalModel

from simulator_class.simulator import simulator




condition=True

#class synchroniser(threading.Thread):
class synchroniser():
    def __init__(self,interface_DB=None,n_pallet=None,source_type=None,simulator_type=None,t_horizon=None):
        threading.Thread.__init__(self)
        self.n_pallet=n_pallet
        self.source_type=source_type
        self.simulator_type=simulator_type
        self.t_horizon=t_horizon
        self.db=interface_DB
        
       
        
        
        
        # global init_pos
        # global number_activity
         
    def run_simulator(self,synchroniser_id):
        self.n_pallet=self.db.queryData("number_of_pallets","parameters")
        print("number of pallets = "+str(self.n_pallet))
        simulator(self.db,self.simulator_type,self.t_horizon,None,None,"shadow",self.n_pallet,self.source_type,synchroniser_id)
      
    def run(self,synchroniser_id):   #Trace Driven simulation
        
        
        
        #while condition==True:
            
            
        
    #update derivatived data
       #  print('---------------------------------------')
       #  print('Derivatived data alignment: ')
       #  #query measurement: eventlog
       #  data=self.db.queryData(None,'eventlog_Arena',self.t_horizon)
        
       #  #query old measurement: real_perf ---> processing_time
        
       #  p_timereal_old=self.db.queryData('processing_time_real_Arena','real_perf',self.t_horizon) #acquire last acquisition t_query of processing time
       # #compute processing_time 
       #  p_timereal=processing_time(data) ###calculate processing time back again 
       #  #generate processing_time new
       #  id_count=p_timereal['part_id'].astype(int)
       #  number_activity = len(data['activity'].unique()) #number of stations identification
        
       #  p_timereal_new=pd.DataFrame( columns=['activity','part_id','value'])
        
       #  idy=1
       #  for actx in range(1,number_activity +1):
            
       #      for i in range (min(id_count),max(id_count)+1):
                
       #          p_timereal_new_candidate= p_timereal.loc[(p_timereal['activity']==actx) & (p_timereal['part_id']==i)]
                
       #          if p_timereal_old.loc[(p_timereal_old['activity']==actx) & (p_timereal_old['part_id']==i)].empty ==True :
                    
       #              if p_timereal_new_candidate.empty == False:
                                                 
       #                  p_timereal_new.loc[idy,'activity']=actx
       #                  p_timereal_new.loc[idy,'part_id']=i
       #                  p_timereal_new.loc[idy,'value']=int(p_timereal_new_candidate['value'])
                        
       #                  idy=idy+1
       
         
       #  #write Processing_time_New generated
       #  if p_timereal_new.empty == False:
       #      self.db.writeData("processing_time_real","real_perf",p_timereal_new)
            
                        
        
       #  #query old measurement: real_perf ---> system_time
       #  s_timereal_old=self.db.queryData('system_time_real_Arena','real_perf',self.t_horizon) #acquire last acquisition t_query of system_time
       #  #compute System_time_real
       #  s_timereal=system_time_real(self.n_pallet,data) 
       #  #generate system_time new
       #  id_count=s_timereal['part_id'].astype(int)
       #  s_timereal_new=pd.DataFrame( columns=['activity','part_id','value','timelog'])
       #  idy=1
       #  for i in range (min(id_count),max(id_count)+1):
            
       #      s_timereal_new_candidate= s_timereal.loc[(s_timereal['part_id']==i)]
            
       #      if s_timereal_old.loc[(s_timereal_old['part_id']==i)].empty ==True :
                
       #          if s_timereal_new_candidate.empty == False:
                                             
       #              s_timereal_new.loc[idy,'activity']=1
       #              s_timereal_new.loc[idy,'part_id']=i
       #              s_timereal_new.loc[idy,'value']=int(s_timereal_new_candidate['value'])
       #              s_timereal_new.loc[idy,'timelog']=int(s_timereal_new_candidate['timelog'])
                    
                    
       #              idy=idy+1
                    
       #    #write Processing_time_New generated
       #  if s_timereal_new.empty == False:
       #      self.db.writeData("system_time_real","real_perf",s_timereal_new)
        
        
        
        
        
       #  #query old measurement: real_perf ---> inter_dep_timereal
       #  inter_dep_timereal_old=self.db.queryData('inter_dep_time_real_Arena','real_perf',self.t_horizon) #acquire last acquisition t_query of system_time
       #  #compute System_time_real
       #  inter_dep_timereal=interdeparture_time_real(data) 
       #  #generate system_time new
       #  id_count=inter_dep_timereal['part_id'].astype(int)
        
       #  inter_dep_timereal_new=pd.DataFrame( columns=['activity','part_id','value'])
       #  idy=1
       #  for i in range (min(id_count),max(id_count)+1):
            
       #      inter_dep_timereal_new_candidate= inter_dep_timereal.loc[(inter_dep_timereal['part_id']==i)]
            
       #      if inter_dep_timereal_old.loc[(inter_dep_timereal_old['part_id']==i)].empty ==True :
                
       #          if inter_dep_timereal_new_candidate.empty == False:
                                             
       #              inter_dep_timereal_new.loc[idy,'activity']=1
       #              inter_dep_timereal_new.loc[idy,'part_id']=i
       #              inter_dep_timereal_new.loc[idy,'value']=int(inter_dep_timereal_new_candidate['value'])
       #              #inter_dep_timereal_new.loc[idy,'timelog']=int(s_timereal_new_candidate['timelog'])
                    
                    
       #              idy=idy+1
                    
         
       #    #write Processing_time_New generated
       #  if inter_dep_timereal_new.empty == False:
       #      self.db.writeData("inter_dep_time_real","real_perf",inter_dep_timereal_new)
        
        
        print('------------------------------------')
        print('Synchronisation Digital Object')
        self.run_simulator(synchroniser_id)
        
        print(synchroniser_id)
        print('-------------------------')
         
        
        
        # condition=False
         #sleep(2)
         
            
            
            
    
    