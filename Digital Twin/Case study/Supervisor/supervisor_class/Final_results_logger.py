# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 17:26:02 2021

@author: franc
"""

from influxdb import InfluxDBClient
from synchroniser_class.broker_c import broker
from synchroniser_class.synchroniser_c import synchroniser
from database_class.interface_DB import interface_DB
from synchroniser_class.synchroniser_c import synchroniser
from controller_class.controller import controller
import pickle
import pandas as pd

initial_time="1654093329000000000"
              
description=[str("----------- Experiment 5---------------\n"),
             str("----------- RTSimulator  ---------------\n"),
             str("Scenario 4 \n"),
             str("sync with t_horizon=20m\n"),
             str("Forecast sleep:5m\n"),
             str("Time demostration 40m\n"),
             str("analyser sleep(2s)\n"),
             str("Validation: T_query:10min  frequency: 1min Simulator type: Manpy   Information type: KPI   KPI: System time  MEthod: DTW  Threshold: logic 0.95 input: 0.92"),
             ]

db=interface_DB("192.168.0.50","RTSimulatorDB",8086)#Create object database
#("192.168.0.50","RTSimulatorDB",8086)
#("localhost","legoDT",8086)
#n_pallet=12
#sync=synchroniser(db,n_pallet=n_pallet,source_type="sensors",simulator_type="Manpy",t_horizon="25h")



eventlog=db.queryData("eventlog","back_up",initial_time)

history_sync=db.queryData("history_synchronisation","back_up",initial_time)
history_validation_input=db.queryData("history_validation_input","back_up",initial_time)
history_validation_logic=db.queryData("history_validation_logic","back_up",initial_time)

digital_perf=db.queryData("digital_perf","back_up",initial_time)
real_perf=db.queryData("real_perf","back_up",initial_time)
distributions=db.queryData("distributions","back_up",initial_time)
digital_perf_mean=db.queryData("digital_perf_mean","back_up",initial_time)

feedback_info=db.queryData("feedback_info","back_up",initial_time)

# digital_perf_forecast=db.queryData("digital_perf_forecast","back_up",initial_time)
# digital_perf_forecast_system_time=db.queryData("digital_perf_system_time_forecast","back_up",initial_time)
# parts_produced_real=db.queryData("real_parts_produced","back_up",initial_time)
initialization=db.queryData("initialization","back_up",initial_time)
   
with pd.ExcelWriter("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/output.xlsx")as writer:
    
    (initialization).to_excel(writer,
                 sheet_name='initialization',index=False)

    
    # (parts_produced_real).to_excel(writer,
    #              sheet_name='parts_produced_real',index=False)
    
    
    (eventlog).to_excel(writer,
                 sheet_name='eventlog',index=False)
    
    (history_sync).to_excel(writer,
                  sheet_name='history_sync',index=False)
    
    (history_validation_logic).to_excel(writer,
                  sheet_name='history_Validation_LOGIC',index=False)
    
    (history_validation_input).to_excel(writer,
                 sheet_name='history_Validation_INPUT',index=False)

    (digital_perf.loc[(digital_perf['measures']=='System_Time_Digital')]).to_excel(writer,
                  sheet_name='System_Time_Digital',index=False)
    
    (digital_perf.loc[(digital_perf['measures']=='Interdeparture_Time_Digital')]).to_excel(writer,
                  sheet_name='Interdeparture_Time_Digital',index=False)
    
    (real_perf.loc[(real_perf['measures']=='processing_time_real')]).to_excel(writer,
                  sheet_name='processing_time_real',index=False)
    
    (real_perf.loc[(real_perf['measures']=='inter_dep_time_real')]).to_excel(writer,
                  sheet_name='inter_dep_time_real',index=False)
     
    (real_perf.loc[(real_perf['measures']=='system_time_real')]).to_excel(writer,
                  sheet_name='system_time_real',index=False)
    
    (distributions).to_excel(writer,
                  sheet_name='distributions',index=False)
    
    (digital_perf_mean).to_excel(writer,
                    sheet_name='digital_perf_mean',index=False)
    
    (feedback_info).to_excel(writer,
                    sheet_name='feedback_info',index=False)
   
    #(digital_perf_forecast).to_excel(writer,
                #   sheet_name='digital_perf_forecast',index=False)
    
    # (digital_perf_forecast_system_time).to_excel(writer,
    #               sheet_name='forecast_system_time',index=False)
    
    

with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/description_of_test.txt",mode="w") as Routing:
    Routing.write(str(description))       
    Routing.close()
    

with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/description_of_test",mode= "wb") as Processing_time:
    pickle.dump(description,Processing_time)
    Processing_time.close()
    
with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/eventlog.txt",mode="w") as Routing:
    Routing.write(eventlog.to_string(header=True, index=False))       
    Routing.close()
with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/eventlog",mode= "wb") as Processing_time:
    pickle.dump(eventlog,Processing_time)
    Processing_time.close()
        
# with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/history_sync.txt",mode="w") as Routing:
#     Routing.write(history_sync.to_string(header=True, index=False))       
    # Routing.close()
# with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/history_sync",mode= "wb") as Processing_time:
#     pickle.dump(history_sync,Processing_time)
#     Processing_time.close()
      
# with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/System_Time_Digital.txt",mode="w") as Routing:
#     Routing.write(digital_perf.loc[(digital_perf['measures']=='System_Time_Digital')].to_string(header=True, index=False))       
#     Routing.close()
# with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/System_Time_Digital",mode= "wb") as Processing_time:
#     pickle.dump(digital_perf.loc[(digital_perf['measures']=='System_Time_Digital')],Processing_time)
#     Processing_time.close()
 
# with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/Interdeparture_Time_Digital.txt",mode="w") as Routing:
#     Routing.write(digital_perf.loc[(digital_perf['measures']=='Interdeparture_Time_Digital')].to_string(header=True, index=False))       
#     Routing.close()
# with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/Interdeparture_Time_Digital",mode= "wb") as Processing_time:
#     pickle.dump(digital_perf.loc[(digital_perf['measures']=='Interdeparture_Time_Digital')],Processing_time)
#     Processing_time.close()
 
# with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/processing_time_real.txt",mode="w") as Routing:
#     Routing.write((real_perf.loc[(real_perf['measures']=='processing_time_real')]).to_string(header=True, index=False))       
#     Routing.close()
# with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/processing_time_real",mode= "wb") as Processing_time:
#     pickle.dump(real_perf.loc[(real_perf['measures']=='processing_time_real')],Processing_time)
#     Processing_time.close()
 
# with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/inter_dep_time_real.txt",mode="w") as Routing:
#     Routing.write((real_perf.loc[(real_perf['measures']=='inter_dep_time_real')]).to_string(header=True, index=False))       
#     Routing.close()
# with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/inter_dep_time_real",mode= "wb") as Processing_time:
#     pickle.dump(real_perf.loc[(real_perf['measures']=='inter_dep_time_real')],Processing_time)
#     Processing_time.close()
    
# with open("C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/system_time_real.txt",mode="w") as Routing:
#     Routing.write((real_perf.loc[(real_perf['measures']=='system_time_real')]).to_string(header=True, index=False))       
#     Routing.close()
# with open(r"C:/Users/franc\OneDrive - Politecnico di Milano/EDO&FRA_tesi/Case study/Supervisor/supervisor_class/Results/system_time_real",mode= "wb") as Processing_time:
#     pickle.dump(real_perf.loc[(real_perf['measures']=='system_time_real')],Processing_time)
#     Processing_time.close()
     
    
# with open("C:/Users/franc/Desktop/Tesi_magistrale/Lego/Scripts/supervisor_class/Results/distributions.txt",mode="w") as Routing:
#     Routing.write(distributions.to_string(header=True, index=False))       
#     Routing.close()
# with open(r"C:/Users/franc/Desktop/Tesi_magistrale/Lego/Scripts/supervisor_class/Results/distributions",mode= "wb") as Processing_time:
#     pickle.dump(distributions,Processing_time)
#     Processing_time.close()