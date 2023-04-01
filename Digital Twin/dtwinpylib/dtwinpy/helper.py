from IPython.display import Markdown, display
from playsound import playsound
import os

#--- Common Libraries
import datetime
from time import sleep
import shutil
import os
import re
import sys
import json




class Helper():
    def __init__(self, type= "py"):
        self.type = type

        #--- Get global path of the library
        # Get the directory of the code.py file
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        #--- To print on the normal terminal
        if self.type == "py":
            self.Red= "\033[31m"
            self.Green= "\033[32m"
            self.Yellow= "\033[33m"
            self.Blue= "\033[34m"
            self.Purple= "\033[35m "
            self.Brown= "\033[38;5;94m "
            self.Reset = '\033[0m'

        #--- To print on the Jupyter Notebook
        else:
            self.Red = "<span style='color:red'>"
            #self.Green = "<span style='color:green'>"
            self.Green = "<span style='color:#7DCEA0'>"
            self.Yellow = "<span style='color:yellow'>"
            self.Blue = "<span style='color:#3498DB'>"
            self.Purple = "<span style='color:#A569BD'>"
            self.Brown = "<span style='color:#DC7633'>"
            self.Reset = "</span>"

        self.colors = {
            'red': self.Red,
            'green': self.Green,
            'yellow': self.Yellow,
            'blue': self.Blue,    
            'purple': self.Purple,
            'brown': self.Brown,
            'reset': self.Reset                 
            }

        #--- Construct the sounds paths
        """self.sounds = {
            'red': os.path.join(self.dir_path, 'sound', 'error.mp3'),
            'green': os.path.join(self.dir_path, 'sound', 'success.mp3'),
            'yellow': os.path.join(self.dir_path, 'sound', 'warning.mp3') 
        }"""
    
    #--- Printing with colors
    def printer(self, text, color= 'yellow', time= True, play= True):
        (tstr, t) = self.get_time_now()
        if time == True:
            if self.type == "py":
                print(f"{self.colors[color]}{tstr} |{text}{self.Reset}")
            
            else:
                display(Markdown(f"{self.colors[color]}{tstr} |{text}{self.Reset}"))
        else:
            if self.type == "py":
                print(f"{self.colors[color]}{text}{self.Reset}")
            
            else:
                display(Markdown(f"{self.colors[color]}{text}{self.Reset}"))

        
        # Play the Sound related to the color (always for errors)
        if play or color== 'red':
            pass
            # Take the respective sound object
            #sound_path = self.sounds[color]

            # Play the sound
            #print(f"Sound Path: {sound_path}")
            #playsound(r"C:/Users/pedro/Github_repos/Digital_Twin/Digital Twin/dtwinpylib/dtwinpy/sound/success.mp3")

    #--- Print with Markdown language
    def markdown(self, mark):
        if self.type == "py":
            print(f"[ERROR][helper.py/markdown()] Trying to use markdown with the wrong helper type: {self.type}")
        else:
            display(Markdown(f"{mark}{self.Reset}"))

    #--- Get all the internal colors
    def get_colors(self):
        return self.colors
    
    #--- Get the timestemp and translate it
    def get_time_now(self, verbose= False):
        current_timestamp = datetime.datetime.now().timestamp()
        current_timestamp = round(current_timestamp)
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%d %B %H:%M:%S")

        if verbose == True:
            print(f"Current Time: {current_time_str}")
            print(f"Current Timestamp: {current_timestamp}")

        return (current_time_str, current_timestamp)
    
    #--- Copy one file into a new path
    def duplicate_file(self, reference_file, copied_file):
        shutil.copy2(reference_file, copied_file)

    #--- Extract the first number in a string
    def extract_int(self, string):
        integer = int(re.findall('\d+', string)[0])
        return integer
    
    def kill(self):
        #--- Killing the program
        self.printer(f"---- Digital Twin killed ----", 'red')
        sys.exit()

    def delete_databases(self, name):
        print("|- Deleting existing databases...")
        #--- Get current time
        (tstr, t) = self.get_time_now()

        #--- Digital Database path
        digital_database_path = f"databases/{name}/digital_database.db"
        real_database_path = digital_database_path.replace("digital", "real")
        ID_database_path = digital_database_path.replace("digital", "ID")
        exp_database_path = digital_database_path.replace("digital", "exp")


        try:
            os.remove(digital_database_path)
            print(f"|-- Digital Database deleted successfuly from {digital_database_path}")

        except FileNotFoundError:
            self.printer(f"[WARNING][helper.py/delete_databases()] The Digital Database doesn't exist yet in the path '{digital_database_path}', proceding without deleting...")
        except PermissionError:
            self.printer(f"[ERROR][helper.py/delete_databases()] The Digital Database is busy somewhere, please close and try again.", 'red')
            self.printer(f"---- Digital Twin was killed ----", 'red')
            sys.exit()


        #- Delete Real Database
        try:
            os.remove(real_database_path)
            print(f"|-- Real Database deleted successfuly from {real_database_path}")
        except FileNotFoundError:
            self.printer(f"[WARNING][helper.py/delete_databases()] The Real Database doesn't exist yet in the path '{real_database_path}', proceding without deleting...")
        except PermissionError:
            self.printer(f"[ERROR][helper.py/delete_databases()] The Real Database is busy somewhere, please close and try again.", 'red')
            self.printer(f"---- Digital Twin was killed ----", 'red')
            sys.exit()

        #- Delete ID database
        try:
            os.remove(ID_database_path)
            print(f"|-- ID Database deleted successfuly from {ID_database_path}")
        except FileNotFoundError:
            self.printer(f"[WARNING][helper.py/delete_databases()] The ID Database doesn't exist yet in the path '{ID_database_path}', proceding without deleting...")
        except PermissionError:
            self.printer(f"[ERROR][helper.py/delete_databases()] The ID Database is busy somewhere, please close and try again.", 'red')
            self.printer(f"---- Digital Twin was killed at {tstr} ----", 'red')
            sys.exit()

        #- Delete Experimental database
        """
        try:
            os.remove(exp_database_path)
            print(f"|-- Experimental Database deleted successfuly from {exp_database_path}")
        except FileNotFoundError:
            self.printer(f"[WARNING][helper.py/delete_databases()] The Experimental Database doesn't exist yet in the path '{exp_database_path}', proceding without deleting...")
        except PermissionError:
            self.printer(f"[ERROR][helper.py/delete_databases()] The Experimental Database is busy somewhere, please close and try again.", 'red')
            self.printer(f"---- Digital Twin was killed at {tstr} ----", 'red')
            sys.exit()
        """


    #--- Delete models (except by one specific file)
    def delete_old_model(self, folder_path, file_to_save):
        print(f"Deleting existing model (excepted by '{file_to_save}') from the relative folder path:'{folder_path}'")
        model_counter = 0
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name != file_to_save:
                os.remove(file_path)
                print(f"File '{file_name}' deleted...")
                model_counter += 1
        print(f"Done! Deleted {model_counter} successfuly")

    def convert_stringVect_to_listVect(self, stringVect):
        return json.loads(stringVect)
    
    def convert_tuple_vector_to_list(self, tuple_vector):
        for i in range(len(tuple_vector)):
            tuple_vector[i] = tuple_vector[i][0]
        return tuple_vector
    
    def adjust_relative_vector(self, vector):
        first_value = vector[0]
        for i in range(len(vector)):
            relative_value = vector[i] - first_value
            vector[i] = relative_value
        
        return vector