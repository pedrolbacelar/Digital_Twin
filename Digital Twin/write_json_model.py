from dtwinpylib.dtwinpy.tester import Tester
import json
import os
import sqlite3

test = Tester()

#--- write json model to database
test.exp_db_path = f"databases/exp_database.db" #--- use your database path
test.create_json_model_table()  #--- create database and required tables in the path

test.write_json_model(model_dict= myjson_model_variable, model_name= 'myjson_model_name') #--- pass the json dictionary and its name