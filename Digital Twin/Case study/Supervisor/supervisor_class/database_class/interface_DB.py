# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:14:15 2021

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
# from influx import InfluxDB
from influxdb import InfluxDBClient
from influxdb import DataFrameClient


class interface_DB():
    
    def __init__(self,ip,DB_name,port):
        self.ip=ip
        self.DB_name=DB_name
        self.port=port
        self.client = InfluxDBClient(host=self.ip, port=self.port)
        self.client_df=DataFrameClient(host=self.ip, port=self.port)
        
        self.insert_time_digital=0
        
        
    # def writeData(self,measurement_name,measures_name,data):
        
    #     if measurement_name=='real_perf':
            
        
    #         if measures_name=='processing_times_real':
                         
                
                
    def queryData(self,measures_name,measurement_name,t_query=None,activity=None):
              
        
        self.client.switch_database(self.DB_name)
        
        if measurement_name=='eventlog_Arena':
           
                eventlog= self.client.query('SELECT * FROM eventlog WHERE time >now()-'+t_query,epoch='s')    ##      
                data=eventlog.raw
               
                try:       
                    df=pd.DataFrame(data['series'][0]['values'],columns=['time','activity','id','type']) #Dataframe
                    
                    #Filtering
                    df['activity'] = df['activity'].astype(int)  #conversion of activity column from string to integer
                    df['id'] = df['id'].astype(int)               #conversion of id column from string to integer
                    df_c=df.drop_duplicates(subset=['activity','id','type'],keep='first')   #elimination of duplicates for column 'type' ovvero le letture doppie di start e finish, OCCHIO CHE é UNA COSA MOLTO GREZZA
               
                except IndexError:
                    df_c=pd.DataFrame(columns=['activity','id','type'])
                    
                    print("eventlog is empty")
                    
                return df_c
          
            
          
        if measurement_name == 'eventlog_validator':
            eventlog = self.client.query('SELECT * FROM eventlog WHERE time >now()-'+t_query  , epoch='s')
            data = eventlog.raw
            df = pd.DataFrame(data['series'][0]['values'], columns=['time', 'activity', 'id', 'type'])  # Dataframe
            # Filtering
            df['activity'] = df['activity'].astype(int)  # conversion of activity column from string to integer
            df['id'] = df['id'].astype(int)  # conversion of id column from string to integer
            df_c = df.drop_duplicates(subset=['activity', 'id', 'type'],   keep='first')  # elimination of duplicates for column 'type' ovvero le letture doppie di start e finish, OCCHIO CHE é UNA COSA MOLTO GREZZA
            eventlog_NP=df_c.to_numpy()
            s=eventlog_NP[:,3]+eventlog_NP[:,1].astype(str)
            string_events_real=s.astype(str)
            time_events_real_=eventlog_NP[:,0]
            time_events_real=time_events_real_.astype(float)
            data_events_real=np.stack((string_events_real,time_events_real),axis=1)
            return data_events_real,df_c
            
        
    
        if measurement_name =='real_perf':
            if measures_name=='processing_time_real_Arena':
             
                p_timereal=self.client.query('SELECT * FROM real_perf WHERE time >now()-'+str(t_query),epoch='s')
                
                try:
                    p_timereal=pd.DataFrame(p_timereal.raw['series'][0]['values'],columns=['time','activity','measures','part_id','value'])
                
                    p_timereal=p_timereal.loc[(p_timereal['measures']=="processing_time_real")]
                    p_timereal=p_timereal.drop('time', axis='columns')
                    p_timereal=p_timereal.drop('measures', axis='columns')
                    p_timereal['activity']=pd.to_numeric(p_timereal['activity']).astype(int)
                    p_timereal['part_id']=pd.to_numeric(p_timereal['part_id']).astype(int)
                    p_timereal['value']=pd.to_numeric(p_timereal['value']).astype(int)
                
                except IndexError:
                    p_timereal=pd.DataFrame(columns=['activity','part_id','value'])
                    
                return p_timereal
            
            if measures_name=='system_time_real_Arena':
                
                S_timereal=self.client.query('SELECT * FROM real_perf WHERE time >now()-'+str(t_query),epoch='s')
                
                try:
                    S_timereal=pd.DataFrame(S_timereal.raw['series'][0]['values'],columns=['time','activity','measures','part_id','value'])
                
                    S_timereal=S_timereal.loc[(S_timereal['measures']=="system_time_real")]
                    S_timereal=S_timereal.drop('time', axis='columns')
                    S_timereal=S_timereal.drop('measures', axis='columns')
                    S_timereal['activity']=pd.to_numeric(S_timereal['activity']).astype(int)
                    S_timereal['part_id']=pd.to_numeric(S_timereal['part_id']).astype(int)
                    S_timereal['value']=pd.to_numeric(S_timereal['value']).astype(int)
                
                except IndexError:
                    S_timereal=pd.DataFrame(columns=['activity','part_id','value'])
                    
                return S_timereal
            
            if measures_name=='inter_dep_time_real_Arena':
                
                inter_dep_timereal=self.client.query('SELECT * FROM real_perf WHERE time >now()-'+str(t_query),epoch='s')
                
                try:
                    inter_dep_timereal=pd.DataFrame(inter_dep_timereal.raw['series'][0]['values'],columns=['time','activity','measures','part_id','value'])
                
                    inter_dep_timereal=inter_dep_timereal.loc[(inter_dep_timereal['measures']=="inter_dep_time_real")]
                    inter_dep_timereal=inter_dep_timereal.drop('time', axis='columns')
                    inter_dep_timereal=inter_dep_timereal.drop('measures', axis='columns')
                    inter_dep_timereal=inter_dep_timereal.drop('activity', axis='columns')
                    
                    inter_dep_timereal['part_id']=pd.to_numeric(inter_dep_timereal['part_id']).astype(int)
                    inter_dep_timereal['value']=pd.to_numeric(inter_dep_timereal['value']).astype(int)
                
                except IndexError:
                    inter_dep_timereal=pd.DataFrame(columns=['part_id','value'])
                    
                return inter_dep_timereal
            
                
        
            
 ##quey processing times per input validation
        if measurement_name == 'real_perf_validator':
            if measures_name == 'processing_time_real':
            # WHERE time >now()-' + str(t_query),
                p_timereal = self.client.query('SELECT * FROM real_perf WHERE time >now()-'+t_query ,
                                               epoch='s')

                p_timereal = pd.DataFrame(p_timereal.raw['series'][0]['values'],
                                          columns=['time', 'activity', 'measures', 'part_id', 'value'])
                p_timereal=p_timereal.loc[(p_timereal['measures'] == "processing_time_real")]
                p_timereal=p_timereal.loc[(p_timereal['activity'] == str(activity))]
                p_timereal = p_timereal.drop('time', axis='columns')
                p_timereal = p_timereal.drop('measures', axis='columns')
                p_timereal['activity'] = pd.to_numeric(p_timereal['activity']).astype(int)
                p_timereal['part_id'] = pd.to_numeric(p_timereal['part_id']).astype(int)
                p_timereal['value'] = pd.to_numeric(p_timereal['value']).astype(int)
                proc_timereal_=p_timereal.to_numpy()
                proc_timereal=proc_timereal_[:,2]
                return proc_timereal
             
        
        
        
        if measurement_name =='digital_perf':
            if measures_name=='System_time_Digital':
             
                S_time_digital=self.client.query("SELECT * FROM digital_perf where measures='System_Time_Digital' ",epoch='s')
                
                try:
                    S_time_digital=pd.DataFrame(S_time_digital.raw['series'][0]['values'],columns=['time','measures','part_id','replication','simulator_id','timelog','value'])
                    
                    S_time_digital=S_time_digital.loc[S_time_digital['time']==max(S_time_digital['time'])]
                    S_time_digital=S_time_digital.sort_values(by=['timelog'])
                    S_time_digital.reset_index(drop=True, inplace=True)
                    S_time_digital.loc[(S_time_digital['measures']=="System_Time_Digital")]
                    
                    S_time_digital=S_time_digital.drop('time', axis='columns')
                    S_time_digital=S_time_digital.drop('measures', axis='columns')
                    
                    S_time_digital['timelog']=pd.to_numeric(S_time_digital['timelog']).astype(int)
                    S_time_digital['part_id']=pd.to_numeric(S_time_digital['part_id']).astype(int)
                    S_time_digital['value']=pd.to_numeric(S_time_digital['value']).astype(int)
                
                except IndexError:
                    S_time_digital=pd.DataFrame(columns=['activity','part_id','value'])
                    
                return S_time_digital    
        
            
         # Read Graph model from the database (ModelConverter)
        if measurement_name == 'model':
            if measures_name == 'graph_model':
                 # query the last graph model
                 graph_model = self.client.query("SELECT * FROM model WHERE type = '"
                                                 + measures_name + "' GROUP BY * ORDER BY DESC LIMIT 1")
                 # extract the string with the last graph model
                 graph_model = graph_model.raw['series'][0]['values'][0][1]
                 # transform the string into a dict
                 graph_model = json.loads(graph_model.replace("\'", "\""))

                 return graph_model
             
        
                # Read Executable model from the database (DigitalModel)
        
            if measures_name == 'executable_model':
                # query the last executable model
                exec_model = self.client.query("SELECT * FROM model WHERE type = '"
                                               + measures_name + "' GROUP BY * ORDER BY DESC LIMIT 1")
                # extract the string with the last executable model
                exec_model = exec_model.raw['series'][0]['values'][0][1]
                # transform the string into a dict
                exec_model = json.loads(exec_model.replace("\'", "\""))

                return exec_model

                # Read Processing Times from the database (DigitalModel)

                # Read WIP position list from database (DigitalModel)

                # Read Correlated Processing Times from the database (DigitalModel)

        if measurement_name == 'distributions':
            if measures_name == 'processing_time_1':
            # WHERE type = ' "+ measures_name +" '
            #controllare le virgolette
                distribution = self.client.query('SELECT * FROM distributions ORDER by time DESC LIMIT 1',
                                                epoch='s')
        
                distribution = pd.DataFrame(distribution.raw['series'][0]['values'],columns=['time', 'measures','type','value'])
                distribution.loc[(distribution['measures'] == measures_name)]
                distribution = distribution.drop('time', axis='columns')
                distribution = distribution.drop('measures', axis='columns')
                #distribution['type'] = pd.to_string(distribution['type'])
                # distribution['type'] = pd.to_numeric(distribution['type']).astype(float)
                #distribution['value'] =pd.to_array(distribution['value']).astype(float)
                dist=str(distribution['type'].to_numpy())
                parameters=str(distribution['value'].to_numpy())
                
                return dist, parameters
            
            
            if measures_name == 'processing_time_1_dist_fitter':
            
                distribution = self.client.query("SELECT * FROM distributions where measures='processing_time_1' ORDER by time DESC LIMIT 1",
                                                epoch='s')
        
                distribution = pd.DataFrame(distribution.raw['series'][0]['values'],columns=['time', 'measures','type','value'])
                
                distribution = distribution.drop('time', axis='columns')
                distribution = distribution.drop('measures', axis='columns')
                distribution['type'] = pd.to_string(distribution['type'])
                
                distribution['value'] =pd.to_array(distribution['value']).astype(float)
               
                return distribution
            
            if measures_name == 'processing_time_2_dist_fitter':
            
                distribution = self.client.query("SELECT * FROM distributions where measures='processing_time_2' ORDER by time DESC LIMIT 1",
                                                epoch='s')
        
                distribution = pd.DataFrame(distribution.raw['series'][0]['values'],columns=['time', 'measures','type','value'])
                
                distribution = distribution.drop('time', axis='columns')
                distribution = distribution.drop('measures', axis='columns')
                distribution['type'] = pd.to_string(distribution['type'])
                
                distribution['value'] =pd.to_array(distribution['value']).astype(float)
               
                return distribution
            
            # AGGIUNTO DA EDO 16/12
            if measures_name == "proc_time":
                # query the last distribution
                distribution_1 = self.client.query(
                    "SELECT * FROM distributions where measures='processing_time_1' ORDER by time DESC LIMIT 1",
                    epoch='s')
                distribution_2 = self.client.query(
                    "SELECT * FROM distributions where measures='processing_time_2' ORDER by time DESC LIMIT 1",
                    epoch='s')

                dist_temp = distribution_1.raw['series']
                dist_temp.append(distribution_2.raw['series'][0])

                # dist_temp = dist_temp.raw['series']
                distr_dict = {}
                for dist_in in dist_temp:
                    mach = "M" + dist_in['values'][0][1][-1]
                    dist_name = dist_in['values'][0][2] + "SP"
                    param = json.loads(dist_in['values'][0][3])
                    distr_dict.update({mach: [dist_name, param]})

                distribution = pd.DataFrame(distr_dict)

                # return dist_temp[0]
                return distribution

            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        ##aggiunto il 14-12-2021
        
        if measurement_name=="initialization":
            
            if measures_name=="final_position":
                end_pos=self.client.query("SELECT * FROM initialization WHERE measures = '"
                                               + measures_name + "' GROUP BY * ORDER BY DESC LIMIT 1")
                
                end_pos=json.loads(end_pos.raw['series'][0]['values'][0][1])
                
                end_pos_pd=pd.DataFrame(columns=[i for i in range(min(end_pos),max(end_pos)+1)])
                for actx in range(min(end_pos),max(end_pos)+1):
                    
                    end_pos_pd.loc[1,actx]=end_pos.count(actx)
                    
        
                
                
                
                # end_pos = end_pos.drop('timestamp', axis='columns')
                
                return end_pos_pd
            
            # AGGIUNTO DA EDO 16/12
            if measures_name == "final_position_eval":
                final_pos = self.client.query(
                    "SELECT * FROM initialization WHERE measures = 'final_position' GROUP BY * ORDER BY DESC LIMIT 1")
                final_pos = final_pos.raw['series'][0]['values'][0][1]
                return json.loads(final_pos)
                # return final_pos.raw['series'][0]['values'][0][1]

            
            
            
            
            
            
            
            
            
        ##aggiunto il 14-12-2021    
        if measurement_name=="history_validation_controller":
            
            if measures_name=="input":   
                input_validation_pd=self.client.query("SELECT * FROM history_validation WHERE type = '"
                                               + measures_name + "' GROUP BY * ORDER BY DESC LIMIT 1")
                try:
                    input_validation_pd = pd.DataFrame(input_validation_pd.raw['series'][0]['values'],columns=['time', 'information_type','method','result','value'])
                    input_validation_pd = input_validation_pd.drop('time', axis='columns')
                    
                    input_validation_pd['information_type'] = (input_validation_pd['information_type']).astype(str)
                    input_validation_pd['method'] = (input_validation_pd['method']).astype(str)
                    
                    input_validation_pd['result'] = (input_validation_pd['result']).astype(int)
                    input_validation_pd['value'] = (input_validation_pd['value'])
                except IndexError:
                    input_validation_pd = pd.DataFrame(columns=['time', 'information_type','method','result','value'])
                    
                      
                return input_validation_pd
            
            if measures_name=="logic":   
                logic_validation_pd=self.client.query("SELECT * FROM history_validation WHERE type = '"
                                               + measures_name + "' GROUP BY * ORDER BY DESC LIMIT 1")
                try:
                    logic_validation_pd = pd.DataFrame(logic_validation_pd.raw['series'][0]['values'],columns=['time', 'information_type','method','result','value'])
                    logic_validation_pd = logic_validation_pd.drop('time', axis='columns')
                   
                    logic_validation_pd['information_type'] = (logic_validation_pd['information_type']).astype(str)
                    logic_validation_pd['method'] = (logic_validation_pd['method']).astype(str)
                    
                    logic_validation_pd['result'] = (logic_validation_pd['result']).astype(int)
                    logic_validation_pd['value'] = (logic_validation_pd['value'])
                except IndexError:
                    logic_validation_pd = pd.DataFrame(columns=['time', 'information_type','method','result','value'])
                    
                      
            return logic_validation_pd
       
        # AGGIUNTO DA EDO 16/12
        if measurement_name == "history_validation_Eval":
            if measures_name == "input":
                validation_hist = self.client.query("SELECT * FROM history_validation WHERE type = 'input' GROUP BY * ORDER BY DESC LIMIT 1")
                validation_val = int(validation_hist.raw['series'][0]['values'][0][3])
                validation_bool = not validation_val == 2
                return validation_bool
    
        # AGGIUNTO DA EDO 16/12
        if measurement_name == "digital_perf_mean":
            if measures_name == "th_eval":
                th_val = self.client.query("SELECT * FROM digital_perf_mean WHERE measures = 'th_eval' GROUP BY * ORDER BY DESC LIMIT 1")
                th_val = th_val.raw['series'][0]['values'][0][2]
                return json.loads(th_val)
           
        #aggiunto il 18-12
        if measurement_name=="parameters":
            if measures_name=="number_of_pallets":
                n_pallet = self.client.query("SELECT * FROM parameters WHERE measures = 'number_of_pallets' GROUP BY * ORDER BY DESC LIMIT 1")
                n_pallet = n_pallet.raw['series'][0]['values'][0][1]
                n_pallet=int(n_pallet)
                return n_pallet
                
               
       #aggiunto il 18-12
        if measurement_name =="back_up":
            if measures_name == "eventlog":
                eventlog= self.client.query('SELECT * FROM eventlog WHERE time >'+t_query,epoch='ns')    ##      
                data=eventlog.raw
               
                try:       
                    df=pd.DataFrame(data['series'][0]['values'],columns=['time','activity','id','type']) #Dataframe
                    
                    #Filtering
                    df['activity'] = df['activity'] #conversion of activity column from string to integer
                    df['id'] = df['id'].astype(int)               #conversion of id column from string to integer
                    df_c=df.drop_duplicates(subset=['activity','id','type'],keep='first')   #elimination of duplicates for column 'type' ovvero le letture doppie di start e finish, OCCHIO CHE é UNA COSA MOLTO GREZZA
               
                except IndexError:
                    df_c=pd.DataFrame(columns=['activity','id','type'])
                    
                    print("eventlog is empty")
                    
                return df_c
            
            if measures_name=="history_synchronisation":
                his_sync= self.client.query('SELECT * FROM history_synchronisation WHERE time >'+t_query,epoch='ns')    ## 
                df=pd.DataFrame(his_sync.raw['series'][0]['values'],columns=['time','measures','sync_id','value1','value2']) #Dataframe
                return df
            
            if measures_name=="history_validation_input":
                his_sync= self.client.query("SELECT * FROM history_validation WHERE type ='input' and time >"+t_query,epoch='ns')    ## 
                
                df=pd.DataFrame(his_sync.raw['series'][0]['values'],columns=['time','information_type','method','result','type','value']) #Dataframe
                return df
      
            
            if measures_name=="history_validation_logic":
                his_sync= self.client.query("SELECT * FROM history_validation WHERE type ='logic' and time >"+t_query,epoch='ns')    ## 
                
                df=pd.DataFrame(his_sync.raw['series'][0]['values'],columns=['time','information_type','method','result','type','value']) #Dataframe
                return df
            
            
            
            if measures_name=="digital_perf":
                digital_perf= self.client.query('SELECT * FROM digital_perf  WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(digital_perf.raw['series'][0]['values'],columns=['time','activity','measures','part_id','replication','simulator_id','timelog','value']) #Dataframe
                return df
            if measures_name=="real_perf":
                real_perf= self.client.query('SELECT * FROM real_perf ',epoch='ns')    ##
                df=pd.DataFrame(real_perf.raw['series'][0]['values'],columns=['time','activity','measures','part_id','value']) #Dataframe
                return df
            if measures_name=="distributions":
                real_perf= self.client.query('SELECT * FROM distributions WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(real_perf.raw['series'][0]['values'],columns=['time','measures','type','value']) #Dataframe
                return df
            if measures_name=="digital_perf_mean":
                real_perf= self.client.query('SELECT * FROM digital_perf_mean WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(real_perf.raw['series'][0]['values'],columns=['time','activity','measures','replication','value']) #Dataframe
                return df
            if measures_name=="feedback_info":
                fb_info= self.client.query('SELECT * FROM feedback_info WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(fb_info.raw['series'][0]['values'],columns=['time','detail','measures','value']) #Dataframe
                return df
            #
            if measures_name=="digital_perf_forecast":
                forecast_perf= self.client.query('SELECT * FROM digital_perf_forecast WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(forecast_perf.raw['series'][0]['values'],columns=['time','activity','measures','p_count_forecast','time demostration']) #Dataframe
                return df
            if measures_name=="digital_perf_system_time_forecast":
                digital_perf= self.client.query('SELECT * FROM digital_perf_system_time_forecast  WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(digital_perf.raw['series'][0]['values'],columns=['time','measures','part_id','replication','simulator_id','timelog','value']) #Dataframe
                return df
               
            if measures_name=="real_parts_produced":
                digital_perf= self.client.query('SELECT * FROM real_parts_produced  WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(digital_perf.raw['series'][0]['values'],columns=['time','measures','value']) #Dataframe
                return df
            
            if measures_name=="initialization":
                digital_perf= self.client.query('SELECT * FROM initialization  WHERE time >'+t_query,epoch='ns')    ##
                df=pd.DataFrame(digital_perf.raw['series'][0]['values'],columns=['time','measures','list']) #Dataframe
                return df
               
                    
                
            
            
        
            
       #aggiunto 14-02-2022
        if measurement_name =="eventlog":
            if measures_name == "produced_parts":
                df=self.client.query("SELECT * FROM eventlog WHERE activity='1' GROUP BY * ORDER BY desc limit 2",epoch='s')
                data=df.raw
               
            
                data=pd.DataFrame(data['series'][0]['values'],columns=['time','id','type']) #Dataframe
                
                p_count=int(data.loc[(data['type']=="s") & (data['id']==max(data['id']))]['id'])
                
                return p_count
         
        
       
       
            
            
   
   
   
    
               
       
        
        
    def writeData(self,measures_name,measurement_name,data,synchroniser_id=None):
        self.client.switch_database(self.DB_name)
        data=data
        
        if measurement_name =='initialization':
            if measures_name=="initial_position_Arena":
            
                init_pos=data
                json_init_pos=[{"measurement":"initialization","tags":{"measures":"initial_position"},"fields":{"list":str(init_pos['location'].tolist())}}]
                self.client.write_points(json_init_pos)
                
            if measures_name=="final_position_Arena":
            
                init_pos=data
                json_init_pos=[{"measurement":"initialization","tags":{"measures":"final_position"},"fields":{"list":str(init_pos['location'].tolist())}}]
                self.client.write_points(json_init_pos)
                
            if measures_name == "final_position_manpy":
                results = data
                final_list = results["final_position"]
                json_final_pos = [{"measurement": "initialization", 'tags': {'measures': "final_position"}, "fields": {"list": str(final_list)}}]
                self.client.write_points(json_final_pos)
              
            
        if measurement_name == "real_perf":
            if measures_name=="processing_time_real":
                
                for i in range(0,len(data)): 
                   
                    json_p_timereal=[{"measurement":"real_perf",
                                      "tags":{"measures":"processing_time_real",
                                              "activity":str(data.iloc[i]['activity']),
                                              "part_id":str(data.iloc[i]['part_id'])
                                              },
                                      "fields":{"value":float(data.iloc[i]['value'])
                                                }
                                      }]
                    
                    self.client.write_points(json_p_timereal)
                    
            if measures_name=="system_time_real":
                
                for i in range(0,len(data)): 
                   
                    json_s_timereal=[{"measurement":"real_perf",
                                      "tags":{"measures":"system_time_real",
                                              "activity":str(data.iloc[i]['activity']),
                                              "part_id":str(data.iloc[i]['part_id'])
                                              },
                                      
                                      "fields":{"value":float(data.iloc[i]['value'])
                                                }
                                      }]
                    
                    self.client.write_points(json_s_timereal)
                    
                    
                    
            if measures_name=="inter_dep_time_real":
                
                for i in range(0,len(data)): 
                   
                    json_inter_dep_timereal=[{"measurement":"real_perf",
                                      "tags":{"measures":"inter_dep_time_real",
                                              "activity":str(data.iloc[i]['activity']),
                                              "part_id":str(data.iloc[i]['part_id'])
                                              },
                                      
                                      "fields":{"value":float(data.iloc[i]['value'])
                                                }
                                      }]
                    
                    self.client.write_points(json_inter_dep_timereal)
                    
        # AGGIUNTO DA EDO 16/12
        if measurement_name == "digital_perf_mean":
            if measures_name == "th_eval":
                
                json_th = [{
                    "measurement": "digital_perf_mean",
                    "tags": {"measures": measures_name},
                    "fields": {
                        "activity": 1.0,
                        "interval": str(data)
                    }
                }]
                self.client.write_points(json_th)

            # AGGIUNTO DA EDO 16/12
            if measures_name == "util_sync":
                for i in range(2):
                    util_value = data['elementList'][i]['results']['working_ratio'][0]
                    
                    json_th = [{
                        "measurement": "digital_perf_mean",
                        "tags": {"measures": measures_name},
                        "fields": {
                            "activity": float(i+1),
                            "value": util_value
                        }
                    }]
                    self.client.write_points(json_th)      
                    
        if measurement_name == "digital_perf_forecast":
               
            if measures_name=="produced_parts_forecast":
                
                json_th = [{
                    "measurement": "digital_perf_forecast",
                    "tags": {"measures": measures_name},
                    "fields": {
                        "activity": 1.0,
                        "p_count_forecast": float(data[0]),
                        "time demostration": data[1]
                    }
                }]
                self.client.write_points(json_th)

                
        
        if measurement_name=="digital_perf":
            
            if measures_name=="system_time_digital_Arena":
                
                    
               
                insert_time=datetime.datetime.utcnow()
                
                 
                for i in range(0,data.shape[0]): 
                    
                    json_p_timereal=[{"measurement":"digital_perf",
                                      "tags":{"measures":"System_Time_Digital",
                                              "part_id":float(i),
                                              
                                              "simulator_id":"Arena",
                                              },
                                      "time": str(insert_time),
                                      "fields":{"replication":float(synchroniser_id),
                                                  "value":float(data.iloc[i]['System Time Digital']),
                                                 "timelog":float(data.iloc[i]['timelog'])
                                                
                                                }
                                      }]
                    
                    #self.client_df.write_points(data[i], "digital_perf", tags={"measures": "system_time_digital"},field_columns={'value'})
                    self.client.write_points(json_p_timereal)
                    
            
            
            
            
            
            
        
            
            if measures_name=="system_time_digital_Manpy":
                
                
                results = data
                datalist = results['elementList'][0]['results']['system_time_trace'][0]
                # initialize the lists for the columns in the dataframe
                timelog_list = []
                ID_list = []
                systime_list = []

                # populate the lists
                for i in range(len(datalist)):
                    timelog_list.append(datalist[i][0])
                    ID_list.append(datalist[i][1])
                    systime_list.append(datalist[i][2])

                # create the dict to transform into a DataFrame
                systime_dict = {
                    "activity": 1,  # TO FIX, INSERT THE ACTIVITY IN THE INPUT DICT result
                    "part_id": pd.Series(ID_list),
                    "replication": 1,  # TO FIX, INSERT THE REPLICATION IN THE INPUT DICT result
                    "simulator_id": 1,  # TO FIX, INSERT THE SIMULATOR ID IN THE INPUT DICT result
                    "timelog": pd.Series(timelog_list),
                    "value": pd.Series(systime_list),
                }

                # create the Dataframe
                systime_DF = pd.DataFrame(systime_dict)
                # systime_DF.set_index('part_id', inplace=True)

                self.insert_time_digital = datetime.datetime.utcnow()

                for i in range(0, systime_DF.shape[0]):
                    json_p_timereal = [{"measurement": "digital_perf",
                                        "tags": {"measures": "System_Time_Digital",
                                                 "part_id": float(systime_DF.iloc[i]['part_id']),
                                                  "simulator_id": "Manpy"+str(systime_DF.iloc[i]['simulator_id']),
                                                 },
                                        "time": str(self.insert_time_digital),
                                        #"fields": {"replication": float(systime_DF.iloc[i]['replication']),
                                        "fields": {"replication": float(synchroniser_id),
                                         
                                                    "value": float(systime_DF.iloc[i]['value']),
                                                   "timelog": float(systime_DF.iloc[i]['timelog'])

                                                   }
                                        }]

                    # self.client_df.write_points(data[i], "digital_perf", tags={"measures": "system_time_digital"},field_columns={'value'})
                    self.client.write_points(json_p_timereal)
            
            if measures_name == "interdeparture_time_digital_Manpy":
                results = data
                datalist = results['elementList'][0]['results']['interarrival_trace'][0]
                # initialize the lists for the columns in the dataframe
                timelog_list = []
                ID_list = []
                intarr_list = []

                # populate the lists
                for i in range(len(datalist)):
                    timelog_list.append(datalist[i][0])
                    ID_list.append(datalist[i][1])
                    intarr_list.append(datalist[i][2])

                # create the dict to transform into a DataFrame
                intarr_dict = {
                    "activity": 1,  # TO FIX, INSERT THE ACTIVITY IN THE INPUT DICT result
                    "part_id": pd.Series(ID_list),
                    "replication": 1,  # TO FIX, INSERT THE REPLICATION IN THE INPUT DICT result
                    "simulator_id": 1,  # TO FIX, INSERT THE SIMULATOR ID IN THE INPUT DICT result
                    "timelog": pd.Series(timelog_list),
                    "value": pd.Series(intarr_list),
                }

                # create the Dataframe
                intarr_DF = pd.DataFrame(intarr_dict)
                
                
                

                for i in range(0, intarr_DF.shape[0]):
                    json_p_timereal = [{"measurement": "digital_perf",
                                        "tags": {"measures": "Interdeparture_Time_Digital",
                                                 "part_id": float(intarr_DF.iloc[i]['part_id']),
                                                  "simulator_id": "Manpy"+str(intarr_DF.iloc[i]['simulator_id']),
                                                  "activity":1,
                                                 },
                                        "time": str(self.insert_time_digital),
                                        #"fields": {"replication": float(intarr_DF.iloc[i]['replication']),
                                        "fields": {"replication": float(synchroniser_id),
                                                    "value": float(intarr_DF.iloc[i]['value']),
                                                   "timelog": float(intarr_DF.iloc[i]['timelog'])
                                                   }
                                        }]

                    # self.client_df.write_points(data[i], "digital_perf", tags={"measures": "system_time_digital"},field_columns={'value'})
                    self.client.write_points(json_p_timereal)

                
                
                
            
        if measurement_name=="digital_perf_system_time_forecast":
            
            if measures_name=="system_time_digital_Manpy_forecast":
                
                
                results = data
                
                datalist = results['elementList'][0]['results']['system_time_trace'][0]
                # initialize the lists for the columns in the dataframe
                timelog_list = []
                ID_list = []
                systime_list = []

                # populate the lists
                for i in range(len(datalist)):
                    timelog_list.append(datalist[i][0])
                    ID_list.append(datalist[i][1])
                    systime_list.append(datalist[i][2])

                # create the dict to transform into a DataFrame
                systime_dict = {
                    "activity": 1,  # TO FIX, INSERT THE ACTIVITY IN THE INPUT DICT result
                    "part_id": pd.Series(ID_list),
                    "replication": 1,  # TO FIX, INSERT THE REPLICATION IN THE INPUT DICT result
                    "simulator_id": 1,  # TO FIX, INSERT THE SIMULATOR ID IN THE INPUT DICT result
                    "timelog": pd.Series(timelog_list),
                    "value": pd.Series(systime_list),
                }

                # create the Dataframe
                systime_DF = pd.DataFrame(systime_dict)
                # systime_DF.set_index('part_id', inplace=True)
                print(systime_DF)

                self.insert_time_digital = datetime.datetime.utcnow()

                
                for i in range(0, systime_DF.shape[0]):
                    
                    json_p_timereal = [{"measurement": "digital_perf_system_time_forecast",
                                        "tags": {"measures": "system_time_digital_Manpy_forecast",
                                                 "part_id": float(systime_DF.iloc[i]['part_id']),
                                                  "simulator_id": "Manpy"+str(systime_DF.iloc[i]['simulator_id']),
                                                 },
                                        "time": str(self.insert_time_digital),
                                        #"fields": {"replication": float(systime_DF.iloc[i]['replication']),
                                        "fields": {"replication": float(synchroniser_id),
                                         
                                                    "value": float(systime_DF.iloc[i]['value']),
                                                   "timelog": float(systime_DF.iloc[i]['timelog'])

                                                   }
                                        }]
                    
                   # self.client_df.write_points(data[i], "digital_perf", tags={"measures": "system_time_digital"},field_columns={'value'})
                    self.client.write_points(json_p_timereal)

            if measures_name == "system_time_digital_Manpy_forecast_rep":

                results = data

                datalist = results['elementList'][0]['results']['system_time_trace']
                # initialize the lists for the columns in the dataframe
                timelog_list = []
                ID_list = []
                systime_list = []
                rep_list = []
                realtime_list = []

                # populate the lists
                for i, rep in enumerate(datalist):
                    sleep(0.01)
                    time_temp = datetime.datetime.utcnow()
                    for datum in rep:
                        timelog_list.append(datum[0])
                        ID_list.append(datum[1])
                        systime_list.append(datum[2])
                        rep_list.append(i + 1)
                        realtime_list.append(time_temp)

                # self.insert_time_digital = datetime.datetime.utcnow()

                for i, a in enumerate(timelog_list):
                    json_p_timereal = [{"measurement": "digital_perf_system_time_forecast",
                                        "tags": {"measures": "system_time_digital_Manpy_forecast_rep",
                                                 "part_id": float(ID_list[i]),
                                                 "simulator_id": "Manpy",
                                                 },
                                        "time": str(realtime_list[i]),
                                        # "fields": {"replication": float(systime_DF.iloc[i]['replication']),
                                        "fields": {"replication": float(rep_list[i]),

                                                   "value": float(systime_list[i]),
                                                   "timelog": float(timelog_list[i])

                                                   }
                                        }]

                    # self.client_df.write_points(data[i], "digital_perf", tags={"measures": "system_time_digital"},field_columns={'value'})
                    self.client.write_points(json_p_timereal)


        if measurement_name=="eventlog":
            
            for i in range(0,data.shape[0]): 
                
                json_p_timereal=[{"measurement":"eventlog",
                                  "tags":{"activity":data.iloc[i]['activity'],
                                          },
                                  "time": data.iloc[i]['time'],
                                  "fields":{"id":float(data.iloc[i]['id']),
                                             "type":str(data.iloc[i]['type'])
                                            
                                            }
                                  }]
                
                #self.client_df.write_points(data[i], "digital_perf", tags={"measures": "system_time_digital"},field_columns={'value'})
                self.client.write_points(json_p_timereal,time_precision="s")
        
        if measurement_name == "digital_eventlog_Manpy":
            data=data["eventlog"]
            insert_time = datetime.datetime.utcnow()
        
            for i in range(len(data[0])):
                
                json_dig_eventlog = [{"measurement": "digital_eventlog",
                                      "tags": {"activity": data[1][i],
                                              "id": data[2][i],
                                               "type": data[3][i]
                                              },
                                      "time": insert_time,
                                      "fields": {"timelog": float(data[0][i])
                                               }
                                    }]
                self.client.write_points(json_dig_eventlog)
                
                
        if measurement_name == "digital_eventlog_Arena":
            data=data
            insert_time = datetime.datetime.utcnow()
        
            for i in range(0,data.shape[0]):
                
                json_dig_eventlog = [{"measurement": "digital_eventlog",
                                      "tags": {"activity": data.iloc[i]['activity'],
                                               "type": data.iloc[i]['type'],
                                               "id" : i   #Only for indexing, not consistent
                                              },
                                      "time": insert_time,
                                      "fields": {"timelog": float(data.iloc[i]['timelog'])
                                               }
                                    }]
                self.client.write_points(json_dig_eventlog)
                
        # Upload executable model to the database (ModelConverter)
        if measurement_name == "model":
            if measures_name == "executable_model":
                exec_model = data
                json_exec_model = [{"measurement": "model", "tags": {"type": "executable_model"},
                                    "fields": {"file": str(exec_model)}}]
                self.client.write_points(json_exec_model)
                
            if measures_name == "graph_model":
                graph_model = data
                json_graph_model = [{"measurement": "model", "tags": {"type": "graph_model"},
                                    "fields": {"file": str(graph_model)}}]
                self.client.write_points(json_graph_model)
            
        
        if measurement_name == "history":
            if measures_name == "logic":
                value=data[0]
                ind = data[1]
                json_res=[{"measurement":"history","tags":{"type":"logic"},"fields":{"result":value,"detail":ind}}]
                self.client.write_points(json_res)
            if measures_name == "input":
                value=data[0]
                ind = data[1]
                json_res=[{"measurement":"history","tags":{"type":"input"},"fields":{"result":value,"detail":ind}}]
                self.client.write_points(json_res)
        if measurement_name == "corr_input":
            if measures_name == "correlated_processing_times":
                activity=data[0]
                value = str(data[1:])
                json_res=[{"measurement":"corr_input","tags":{"measures":"correlated_processing_times"},"fields":{"activity":activity,"value":value}}]
                self.client.write_points(json_res)
        
        
        ###aggiunto il 14-12-2021       
        if measurement_name == "distributions":
            if measures_name == "processing_times_dist_fitter":
                insert_time = datetime.datetime.now()
                for i in range(1,data.shape[1]+1):
                    
                    json_dig_eventlog = [{"measurement": "distributions",
                                          "tags": {"measures": "processing_time_"+str(i)
                                                   },
                                          "time": insert_time,
                                          "fields": {"type": str(data.loc[1,i]),
                                                     "value": str(data.loc[2,i])
                                                   }
                                        }]
                    self.client.write_points(json_dig_eventlog)
                  
                 
        #aggiunto il 18-12
                 
        if measurement_name=="history_synchronisation":
            if measures_name=="synchronisation_index":
                for i in range(1,data.shape[1]):
                    
                    json_dig_eventlog = [{"measurement": "history_synchronisation",
                                          "tags": {"measures":"synchronisation_index"
                                                   },
                                          
                                          "fields": {"synchronisation_id": float(synchroniser_id),
                                                     "value1": float(data.loc[1,i]),
                                                     "value2": float(data.loc[1,i+1])
                                                   }
                                        }]
                    self.client.write_points(json_dig_eventlog)
                    
            if measures_name=="synchronisation_index_final":
                for i in range(1,data.shape[1]):
                    
                    json_dig_eventlog = [{"measurement": "history_synchronisation",
                                          "tags": {"measures":"synchronisation_index_final"
                                                   },
                                          
                                          "fields": {"synchronisation_id": float(synchroniser_id),
                                                     "value1": float(data.loc[1,i]),
                                                     "value2": float(data.loc[1,i+1])
                                                   }
                                        }]
                    self.client.write_points(json_dig_eventlog)
            
                  
        if measurement_name == "feedback_info":
            # tag: "measures" [str] ("case" quando ho il cambiamento scrivo 1, se no "scenario 1" e "scenario 2"
            #       "detail" [str]  (1 se applico scenario)
            # field: "value" [int]  (numero di parti)
            if measures_name == "case":
                json_fb = [{
                        "measurement": "feedback_info",
                        "tags": {"measures": "case"
                                 },
                        "fields": {"value": int(data)
                                   }
                            }]
                self.client.write_points(json_fb)
            if measures_name == "scenario":
                json_fb = [{
                    "measurement": "feedback_info",
                    "tags": {"measures": "scenario" + str(data[0]),
                        "detail": data[2]
                        },
                    "fields": { "value": data[1]
                            }
                        }]
                self.client.write_points(json_fb)
        
                        
        if measurement_name == "real_parts_produced":
            # tag: "measures" [str] ("case" quando ho il cambiamento scrivo 1, se no "scenario 1" e "scenario 2"
            #       "detail" [str]  (1 se applico scenario)
            # field: "value" [int]  (numero di parti)
            
            json_fb = [{
                    "measurement": "real_parts_produced",
                    "tags": {"measures": "parts"
                             },
                    "fields": {"value": int(data)
                               }
                        }]
            self.client.write_points(json_fb) 
             
    def queryDataSpecial(self,measures_name,measurement_name,t_query):
        
        if measurement_name =='real_perf':
            if measures_name=='processing_time_real_Arena':
            
                
            
                
                p_timereal=self.queryData(measures_name, measurement_name, t_query)
             
                p_timesimul_input= pd.DataFrame(index = range(0,len(p_timereal)),
                                                columns=[i for i in range(1,max(p_timereal['activity'])+1)]+['part_id'])
                
                for actx in range(1,int(max(p_timereal['activity']))+1):
                    
                    p_timesimul_column_candidate=p_timereal.loc[(p_timereal['activity']==actx)]
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
                    print('-----------------------------------')        
                
                return  p_timesimul_input
            
            if measures_name=='processing_time_real_Manpy':
                
                p_timereal=self.queryData('processing_time_real_Arena', measurement_name, t_query)
             
                p_timesimul_input= pd.DataFrame(index = range(0,len(p_timereal)),
                                                columns=[i for i in range(1,max(p_timereal['activity'])+1)]+['part_id'])
                
                for actx in range(1,int(max(p_timereal['activity']))+1):
                    
                    p_timesimul_column_candidate=p_timereal.loc[(p_timereal['activity']==actx)]
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
                    print('-----------------------------------')        
                
                p_timesimul_input=p_timesimul_input.drop('part_id', axis='columns')
                
                
                for actx in range(1,p_timesimul_input.shape[1]+1):
                    p_timesimul_input[actx]=p_timesimul_input[actx].dropna()
                    p_timesimul_input =  p_timesimul_input.rename(columns={actx: 'M'+str(actx)})
                    

                
                
                
                
                return  p_timesimul_input
            
                
    
        
     
     
            
        
            
    