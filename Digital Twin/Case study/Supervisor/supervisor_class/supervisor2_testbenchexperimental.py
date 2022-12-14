# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 23:05:27 2021

@author: franc
"""


import sys

sys.path.append(r'C:\Users\THE FACTORY PC 2\Politecnico di Milano\Francesco Verucchi - EDO&FRA_tesi\Case study\Supervisor\supervisor_class')
sys.path.append('../')

from influxdb import InfluxDBClient
from synchroniser_class.broker_c import broker
from synchroniser_class.synchroniser_c import synchroniser
from database_class.interface_DB import interface_DB
from synchroniser_class.synchroniser_c import synchroniser
from controller_class.controller2_testbenchexperimental import controller
from analytics.analyser_real_c import analyser_real


#broker=broker("192.168.0.50",1883,60,"RTSimulatorDB")
#broker.active()


db=interface_DB("192.168.0.50","RTSimulatorDB",8086)#Create object database
#("localhost","legoDT",8086)
#("192.168.0.50","RTSimuldataatorDB",8086)
#n_pallet=db.queryData("number_of_pallets","parameters")

n_pallet=12


sync=synchroniser(db,n_pallet=n_pallet,source_type="sensors",simulator_type="Manpy",t_horizon="10m")


controller=controller(db,synchroniser=sync,n_pallet=n_pallet ,t_horizon="10m")

controller.start()


# with open(r"eventlog_acquisition",mode= "rb") as Processing_time_file:
#     eventlog_sample = pickle.load(Processing_time_file)
#     Processing_time_file.close()



