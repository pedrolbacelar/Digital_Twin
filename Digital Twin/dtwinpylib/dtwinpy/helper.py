from IPython.display import Markdown, display
"""
Examples using the helper:

from dtwinpylib.dtwinpy.helper import Helper

helper = Helper()
helper.printer("warning", "yellow")
colors = helper.get_colors()
helper.markdown(f"## {colors['yellow']} warning")

"""

#--- Common Libraries
import datetime
from time import sleep
import shutil
import os
import re
import pygame


class Helper():
    def __init__(self, type= "py"):
        self.type = type

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
        
        # Initia the player
        pygame.mixer.init()

        """
        self.sounds = {
            'red': pygame.mixer.Sound("sound/error.mp3"),
            'green': pygame.mixer.Sound("sound/success.mp3"),
            'yellow': pygame.mixer.Sound("sound/warning.mp3") 
        }
        """

    
    #--- Printing with colors
    def printer(self, text, color= 'yellow', time= True, play= False):
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

        # Play the Sound related to the color 
        if play:
            # Take the respective sound object
            sound = self.sounds[color]

            # Play the sound
            sound.play()

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

    #--- Extract the first number in a string
    def extract_int(self, string):
        integer = int(re.findall('\d+', string)[0])
        return integer