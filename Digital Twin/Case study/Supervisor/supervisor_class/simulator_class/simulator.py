# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 16:57:29 2021

@author: franc

"""

import sys

sys.path.append(r'C:\Users\THE FACTORY PC 2\Politecnico di Milano\Francesco Verucchi - EDO&FRA_tesi\Case study\Supervisor')
sys.path.append('../')
import pandas as pd
import os
import numpy as np
from supervisor_class.synchroniser_class.write_txt_init_pos import write_txt_init_pos
from supervisor_class.synchroniser_class.init_position import init_position
from supervisor_class.synchroniser_class.write_txt_processing_time import write_txt_processing_time,write_txt_processing_time_validator
from supervisor_class.analytics.processing_time import processing_time_Arena 
from supervisor_class.analytics.processing_time import processing_time_Manpy
from supervisor_class.synchroniser_class.read_txt_system_time_digital import read_txt_system_time_digital
from supervisor_class.synchroniser_class.read_txt_digital_eventlog import read_txt_digital_eventlog
from supervisor_class.synchroniser_class.write_txt_init_pos import write_txt_init_pos
from supervisor_class.synchroniser_class.read_txt_digital_final_position import read_txt_digital_final_position

#Edo's libraries
from supervisor_class.simulator_class.manpy.DigitalModel import DigitalModel
from DigitalModel_temp import DigitalModel_forecast


def simulator(
        db=None,
        simulator_type = None,
        t_horizon = None,
        p_timesimul_input = None,
        init_pos = None,
        use_type = None, 
        n_pallet=None,#aggiunto
        source_type=None,#aggiunto
        synchroniser_id=None #aggiunto
        ):
    
    
    if not(db):
        print("ERROR: interface_database not declared")
    
   
    
   
    if use_type=="logic_validation":
       if simulator_type == "Manpy":
           
           exec_model_temp = db.queryData("executable_model","model")
           exec_model = DigitalModel(exec_model_temp,1)
           results = exec_model.runTraceSimulation(p_timesimul_input, init_pos['location'].tolist())
           
           # Write on database all digital KPIs specifying that they come from logic validation
           digital_eventlog = results['eventlog']
           #print(digital_eventlog)
           digital_events=[]
           digital_timelog=digital_eventlog[0] #
           for i in range(len(digital_timelog)): #
             digital_events.append(digital_eventlog[3][i]+digital_eventlog[1][i]) #
            
        
           digital_data=np.column_stack((digital_events,digital_timelog)) #
           
           
           
           system_time_digital = results['elementList'][0]['results']['system_time_trace'][0] #
           final_position = results['final_position']
       
           return system_time_digital,digital_eventlog,  final_position,digital_data
           print('simulation type Manpy Run for logic_validation')
       
       if simulator_type == "Arena":
           
           write_txt_init_pos(init_pos,"C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/","Routing.txt") #write initial position on txt file available fro arena to be read
           write_txt_processing_time(p_timesimul_input,"C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/","Processing_time_S")  #write on txt. file to be then read by arena
           
           os.system(r'siman -p C:\Users\franc\Desktop\Tesi_magistrale\Model\Arena\Using\Shadow\Arena_model_legofactory.p')
          
           
          
           # Acquire Output Data from Run            
           system_time_digital = read_txt_system_time_digital(n_pallet,'C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_System_Time.txt')
           digital_eventlog = read_txt_digital_eventlog('C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_digital_eventlog.txt')
           end_pos=read_txt_digital_final_position(n_pallet,'C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_final_position.txt')
           
           final_position=end_pos
           
             
           eventlog_NP=digital_eventlog.to_numpy()
           s=eventlog_NP[:,2]+eventlog_NP[:,1].astype(str)
           string_events=s.astype(str)
           time_events_=eventlog_NP[:,0]
           time_events=time_events_.astype(float)
           digital_data=np.stack((string_events,time_events),axis=1)
           
           return system_time_digital,digital_eventlog,final_position,digital_data
           print('simulation type Arena Run for logic_validation')
       
        
       
    if use_type=="input_validation":
        
       if simulator_type == "Manpy":
            
            exec_model_temp = db.queryData("executable_model","model")
            exec_model = DigitalModel(exec_model_temp,1)
            results = exec_model.runTraceSimulation(p_timesimul_input, init_pos['location'].tolist())
            # Write on database all digital KPIs specifying that they come from input validation
            digital_eventlog = results['eventlog']
           #print(digital_eventlog)
            digital_events=[]
            digital_timelog=digital_eventlog[0] #
            for i in range(len(digital_timelog)): #
             digital_events.append(digital_eventlog[3][i]+digital_eventlog[1][i]) #
            
        
            digital_data=np.column_stack((digital_events,digital_timelog)) #
           
           
           
            system_time_digital = results['elementList'][0]['results']['system_time_trace'][0] #
            final_position = results['final_position']
            
            return system_time_digital,  digital_eventlog, final_position,digital_data
            print('simulation type Manpy Run for Input_validation')
        
       if simulator_type == "Arena":
            
            write_txt_init_pos(init_pos,"C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/","Routing.txt") #write initial position on txt file available fro arena to be read
            write_txt_processing_time(p_timesimul_input,"C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/","Processing_time_S")  #write on txt. file to be then read by arena
            
            os.system(r'siman -p C:\Users\franc\Desktop\Tesi_magistrale\Model\Arena\Using\Shadow\Arena_model_legofactory.p')
           
            
           
            # Acquire  Output Data from Run            
            
            #system_time_digital = read_txt_system_time_digital(n_pallet,'C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_System_Time.txt')
            system_time_digital=[]
            digital_eventlog = read_txt_digital_eventlog('C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_digital_eventlog.txt')
            end_pos=read_txt_digital_final_position(n_pallet,'C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_final_position.txt')
            
            final_position=end_pos
            
            eventlog_NP=digital_eventlog.to_numpy()
            s=eventlog_NP[:,2]+str(eventlog_NP[:,1])
            string_events=s.astype(str)
            time_events_=eventlog_NP[:,0]
            time_events=time_events_.astype(float)
            digital_data=np.stack((string_events,time_events),axis=1)
            
            return system_time_digital,digital_eventlog,final_position,digital_data
            print('simulation type Arena Run for Input_validation')
        
        
    if use_type == "shadow":
         
        if simulator_type== "Arena":
            #Query data and compute for Run
            eventlog_sample=db.queryData(None,'eventlog_Arena',t_horizon) #sample of eventlog within t_horizon acquisition
            #p_timesimul_input=db.queryDataSpecial('processing_time_real_Arena','real_perf',t_horizon) #acquire  acquisition for t_horizon of processing time
            
            p_timesimul_input=processing_time_Arena(eventlog_sample)
            
            init_pos= init_position(source_type,n_pallet,eventlog_sample) #compute initial position of the pallet in for sample eventlog
            write_txt_init_pos(init_pos,"C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/","Routing.txt") #write initial position on txt file available fro arena to be read
            write_txt_processing_time(p_timesimul_input,"C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/","Processing_time_S")  #write on txt. file to be then read by arena
            
            os.system(r'siman -p C:\Users\franc\Desktop\Tesi_magistrale\Model\Arena\Using\Shadow\Arena_model_legofactory.p')
           
            
           
            # Acquire and Save Output Data from Run            
            system_time_digital = read_txt_system_time_digital(n_pallet,'C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_System_Time.txt')
            digital_eventlog = read_txt_digital_eventlog('C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_digital_eventlog.txt')
            end_pos=read_txt_digital_final_position(n_pallet,'C:/Users/franc/Desktop/Tesi_magistrale/Model/Data extraction/','Validation_final_position.txt')
            
            db.writeData("initial_position_Arena","initialization",init_pos)
            db.writeData("final_position_Arena","initialization",end_pos)
            db.writeData(None,"digital_eventlog_Arena",digital_eventlog)
            db.writeData("system_time_digital_Arena","digital_perf",system_time_digital)
            
            print('simulation type Arena Run & KPIs updated')

        if simulator_type== "Manpy":
            
            #Query data and compute for Run
            eventlog_sample=db.queryData(None,'eventlog_Arena',t_horizon) #sample of eventlog within t_horizon acquisition
            #p_timesimul_input=db.queryDataSpecial('processing_time_real_Manpy','real_perf',t_horizon) #acquire  acquisition for t_horizon of processing time
            p_timesimul_input=processing_time_Manpy(eventlog_sample)
            exec_model_temp=db.queryData("executable_model","model")
            
            exec_model=DigitalModel(exec_model_temp,1)
            init_pos= init_position(source_type,n_pallet,eventlog_sample) #compute initial position of the pallet in for sample eventlog
            
            
            results=exec_model.runTraceSimulation(p_timesimul_input,init_pos['location'].tolist())
            
            # Write Data from Run
            db.writeData("initial_position_Arena","initialization",init_pos)
            db.writeData("util_sync","digital_perf_mean",results)
            db.writeData("system_time_digital_Manpy","digital_perf",results,synchroniser_id)
            db.writeData("interdeparture_time_digital_Manpy","digital_perf",results,synchroniser_id)
            db.writeData("final_position_manpy",'initialization',results)
            db.writeData(None,"digital_eventlog_Manpy",results)
            
            print('simulation type Manpy Run & KPIs updated')
            
    
    if use_type == "forecast":
        if simulator_type== "Manpy":
            
            exec_model_temp = db.queryData("executable_model", "model")

            # distrM1 = "fixed"
            # distrM2 = "fixed"
            # paramM1 = [14.4]
            # paramM2 = [16.4]
            distrM1 = "weibull"
            distrM2 = "triangular"
            paramM1 = [18,3] #[shape,scale]
            paramM2 = [14.4,25.4,24.4]
            
            # distrM1 = "triangular"
            # distrM2 = "triangular"
            # paramM1 = [14.4,22.4,18.4] #[shape,scale]
            # paramM2 = [15.4,23.4,19.4]




            distr_dict = {
                "M1": [distrM1, paramM1],
                "M2": [distrM2, paramM2]
            }
            distr_new = pd.DataFrame(distr_dict)
            
            # distr_new = db.queryData("proc_time", "distributions", t_query=2)   # 2 is the number of machine
            
            model = DigitalModel_forecast(exec_model_temp, 1)
            
            # % Da commentare
            model.ObjectList[0].unloadRng.mean += 4.4
            
            init_pos = db.queryData("final_position_eval", "initialization")
            
            print('test')
                
            results = model.runStochSimulation(distr_new, t_horizon, p_timesimul_input, init_pos, seed=synchroniser_id)

            # For a single replication
            # db.writeData("system_time_digital_Manpy_forecast","digital_perf_system_time_forecast",results,synchroniser_id)

            # For multiple replications
            db.writeData("system_time_digital_Manpy_forecast_rep", "digital_perf_system_time_forecast", results, synchroniser_id)
            return results
            
            
   
        
        
