# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 17:07:15 2021

@author: giuli
"""
#ultimaversione
import time
from supervisor_class.validator_class.class_validation import validator
#from db_GG import interface_DB
from supervisor_class.database_class.interface_DB import interface_DB
import pandas as pd

#Edo's libraries
#from supervisor_class.simulator_class.manpy.DigitalModel import DigitalModel

#fra's libraries
from supervisor_class.synchroniser_class.init_position import init_position
#from supervisor_class.simulator_class.simulator import simulator
from supervisor_class.simulator_class.simulator import simulator
from supervisor_class.analytics.processing_time import processing_time

frequency="20m"
threshold_logic=0.75
threshold_input=0.75
n_pallet=12
source_type="sensors"
l=validator('logic',threshold_logic)
i=validator('input',threshold_input)
simulator_type="Arena"

db= interface_DB('192.168.0.50', "RTSimulatorDB", port=8086)

#('192.168.0.50', "RTSimulatorDB", port=8086)
#("localhost","legoDT",8086)

global condition_validation 
condition_validation = True
while condition_validation == True:
   
    #t=time.time()
    t_query=frequency
    # query eventlog reale
    er,eventlog_real=interface_DB.queryData(db,None,'eventlog_validator',t_query,None)
    #print(er)
    #eventlog_real=interface_DB.queryData(db,None,'eventlog_Arena',str(frequency)+"h",None) ## CAMBIATO frequency 350h
    #query processing times real
    # P1=interface_DB.queryData(db,'processing_time_real','real_perf_validator',t_query,1)
    # P2=interface_DB.queryData(db,'processing_time_real','real_perf_validator',t_query,2)
    
    # dict_DF = {
    #     "1": pd.Series(P1.tolist()),
    #     "2": pd.Series(P2.tolist())
    #     }
    # processing = pd.DataFrame(dict_DF)
    #AGGIUNTO
    p_timereal=processing_time(eventlog_real)
    
    p_timesimul_input= pd.DataFrame(index = range(0,len(p_timereal)),
                                    columns=[i for i in range(1,max(p_timereal['activity'])+1)]+['part_id'])
    
    for actx in range(1,int(max(p_timereal['activity']))+1):
        
        p_timesimul_column_candidate=p_timereal.loc[(p_timereal['activity']==actx)]
        p_timesimul_column_candidate.reset_index(drop=True)
        
        for i in range(0,len(p_timesimul_column_candidate)):
                                    
            p_timesimul_input[actx][i]=p_timesimul_column_candidate.iloc[i]['value']
            p_timesimul_input['part_id'][i]=p_timesimul_column_candidate.iloc[i]['part_id']
    
    
    p_timesimul_input=p_timesimul_input.dropna(how="all")
    
    #FINO A QUI
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    init_pos= init_position(source_type,n_pallet,eventlog_real) #compute initial position of the pallet in for sample eventlog
    
    #chiamare simulazione 
    _,_,_,es=simulator(
                    db=db,
                    simulator_type =simulator_type,
                    t_horizon=None,
                    p_timesimul_input = p_timesimul_input,
                    init_pos = init_pos,
                    use_type = "logic_validation", 
                    n_pallet=n_pallet,
                    source_type=source_type,
                    )
    #print(es)
    # check logic
    data_l=validator.event_v(l,er[:,0],es[:,0])
    print(data_l)
    # write on DB
    interface_DB.writeData(db,'logic','history',data_l)
    if data_l[0]==1:
        print('model logic is valid')
    else:
        print('model logic is not valid-->model has to be generated again')
        #break
    
    

    #dist1, parameters1=interface_DB.queryData(db,'processing_time_1','distributions',t_query,None)
    #dist2, parameters2=interface_DB.queryData(db,'processing_time_2','distributions',t_query,None)
    # dist1=2
    # parameters1=[3,8,5]
    # dist2=2
    # parameters2=[3,8,5]
    
    # # inputs correlation
    # corr_P1=i.input_trace(P1,dist1,parameters1)
    # corr_P2=i.input_trace(P2,dist2,parameters2)
    
    # dict_DF_corr = {
    #     "M1": pd.Series(corr_P1.tolist()),
    #     "M2": pd.Series(corr_P2.tolist())
    #     }
    # processing_corr = pd.DataFrame(dict_DF_corr)
    
    # _,_,_,es_corr=simulator(
    #                 db=db,
    #                 simulator_type =simulator_type,
    #                 t_horizon=None,
    #                 p_timesimul_input = processing_corr,
    #                 init_pos = init_pos,
    #                 use_type = "input_validation", 
    #                 n_pallet=n_pallet,#aggiunto
    #                 source_type=source_type,#aggiunto
    #                 )
    
    # # check input
    # data_i=validator.event_v(i,er[:,0],es_corr[:,0])
    
    # # write on DB
    # interface_DB.writeData(db,'input','history',data_i)
    # if data_i[0]==1:
    #     print('model inputs are valid')
    # else:
    #     print('model inputs are not valid-->distributions have to be generated again')
        
    
    #condition_validation=False
    time.sleep(10)
    
    
    