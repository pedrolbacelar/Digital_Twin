# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 18:27:23 2021

@author: franc
"""
from controller_class.final_position import final_position
from supervisor_class.analytics.dist_fit import dist_fit
from controller_class.ModelConverter import ModelConverter

import threading
import time
from time import sleep 

import pandas as pd 

# GIOVANNI x MODEL GEN
from MSM.msmlib import gen_model_init
# from MSM.msm_parameval import find_flowtimes

class controller(threading.Thread):
    def __init__(self,interface_DB=None,synchroniser=None,n_pallet=None,t_horizon=None):
        threading.Thread.__init__(self)
        self.n_pallet=n_pallet
        self.sync=synchroniser
        
        self.t_horizon=t_horizon
        self.t_horizon_dist="10m"
        self.db=interface_DB
        self.end_pos_digital=None
        self.end_pos_real=None
        self.threshold_sync_check=0.00
        self.threshold_init_check=0.09
        self.synchroniser_id=1
        
        
        global condition_controller
        condition_controller=True
        
        
        
        
    def controller_generation(self):
  
        # sum_r=self.end_pos_real.sum(axis=1).item()
        # sum_d=self.end_pos_digital.sum(axis=1).item()
        
        
        # if abs(sum_r-sum_d)/self.n_pallet > 0.09:
        #         print('Generation for n_pallet is INCORRECT')
        #         # generate model 
                
        idx_logic=self.db.queryData("logic","history_validation_controller")
        if int(idx_logic['result'])==2:
            #generate model Giovanni
            
            # TODO
            
            # query Eventlog
            ordata=self.db.queryData(None,"eventlog_Arena","10m")
            # ordata = TODO QUERY
            
            # Generate model return graph_dict
            config = {"batching": {"threshold_arcs": 1,"threshold_nodes" : 1}}
            
            ordata['ts'] = ordata['time'].apply(lambda x: x)
            ordata['tag'] = ordata['type'].apply(lambda x: x)
            ordata['id_new'] = ordata['id'].apply(lambda x: x%self.n_pallet)   # calculate id of the pallet
            ordata.loc[ ordata['id_new'] == 0 , 'id_new'] = self.n_pallet
            
            data = ordata
            data['id'] = ordata['id_new']
            
            graph_dict, unique_list, tracetoremove, id_trace_record = gen_model_init(data, config, tag = True)
            
            for node in graph_dict["nodes"]:
                node["stats"]='temp'

            
            # write Graph model
            
            self.db.writeData("graph_model","model",graph_dict)
            
            # convert Graph model into executable
            
            initial_config = {
                'start': 'M1',
                'unloadTime': 3.2,
                'transportationTime': 17.2,
                'transportationCap': 3,
                'queueCap': {
                            'Q1': 8,
                            'Q2': 8,
                            }
                }

            converter = ModelConverter(graph_dict, initial_config) 
            
            exec_model = converter.convertModel()
            
            self.db.writeData("executable_model","model",exec_model)
            
            
            
            #write Executable model
            
            
            
            
            
            
     
    def controller_initialization(self):   
        
        #query history input_validation to check threshold
        idx_input=self.db.queryData("input","history_validation_controller")
        
        
        if int(idx_input['result']) == 2:  #( not validated)
            print('-----------------------------------------')
            print('initialization with dist is INCORRECT')
       
            dist_fit(self.db,self.t_horizon_dist)
            print('new dist fitted & Saved with time horizon: '+str(self.t_horizon_dist))
            print('-----------------------------------------')
            #generate model
        else: 
            print('-----------------------------------------')
            print('initialization with dist is CORRECT')
            print('-----------------------------------------')
            
       
            
         
        
        
        
        
        
    def controller_synchronisation(self):
       
        
        data=self.db.queryData(None,"eventlog_Arena",self.t_horizon)
        
        #comparison end position for Real and Final
        end_pos=final_position("sensors",self.n_pallet,data)
        
        end_pos_real=pd.DataFrame(columns=[i for i in range(min(data['activity']),max(data['activity'])+1)])
        for i in range(min(data['activity']),max(data['activity'])+1):
            end_pos_real.loc[1,i]=len(end_pos.loc[(end_pos['location']==i)])
        
        end_pos_digital=self.db.queryData("final_position","initialization",None)
        
        end_pos_eval=pd.DataFrame(columns=[i for i in range(min(data['activity']),max(data['activity'])+1)])
        
        for actx in range(min(data['activity']),max(data['activity'])+1):
            
            end_pos_eval.loc[1,actx]=abs(end_pos_digital.loc[1,actx]-end_pos_real.loc[1,actx])/self.n_pallet
            
            if end_pos_eval.loc[1,actx]>self.threshold_sync_check:
               end_pos_eval.loc[2,actx]=False #synchronisation require to be aligned
               
            else:
                end_pos_eval.loc[2,actx]=True  #synchronisation is correct
        
         
        
        if end_pos_eval.loc[2,:].any()==False:
            print('Digital Model synchronisation is NOT Correct')
            self.synchroniser_id=self.synchroniser_id+1
            
            self.sync.run() #activate new synchronisation
            
            print('--------------------')
        
        else:
            print('Digital Model synchronisation is Correct')
            print(end_pos_eval)
        
            print('--------------------')
    
                
        
        self.db.writeData("synchronisation_index","history_synchronisation",end_pos_eval,synchroniser_id=self.synchroniser_id)        
    
    def kill_thread(self):
        
       return
        
        
             
        # condition_controller_test=input('condizione :')
            
        
        
        # condition_controller_test
        
        
       
        
    def run(self):
        global condition_controller
        
        # global condition_controller
        
        condition_controller=True
        
        #self.kill_thread()
        
        while condition_controller:
            
            self.controller_generation()
            
            self.controller_initialization()
            
            
            self.controller_synchronisation()
            
            print(condition_controller)
            
            
            #condition_controller=False
            sleep(5)
            
    
            
            
        
        
        
        