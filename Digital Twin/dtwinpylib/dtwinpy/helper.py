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

class Helper():
    def __init__(self, type= "ipynb"):
        self.type = type

        #--- To print on the normal terminal
        if self.type == "py":
            self.Red= "\033[31m"
            self.Green= "\033[32m"
            self.Yellow= "\033[33m"
            self.Blue= "\033[34m"
            self.RESET = '\033[0m'

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
    
    #--- Printing with colors
    def printer(self, text, color= 'yellow'):
        if self.type == "py":
            print(f"{self.colors[color]}{text}{self.Reset}")
        
        else:
            display(Markdown(f"{self.colors[color]}{text}{self.Reset}"))

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
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%d %B %H:%M:%S")

        if verbose == True:
            print(f"Current Time: {current_time_str}")
            print(f"Current Timestamp: {current_timestamp}")

        return (current_time_str, current_timestamp)