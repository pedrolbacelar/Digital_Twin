from IPython.display import Markdown, display
"""
Examples using the helper:

from dtwinpylib.dtwinpy.helper import Helper

helper = Helper()
helper.printer("warning", "yellow")
colors = helper.get_colors()
helper.markdown(f"## {colors['yellow']} warning")

"""
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
            self.Green = "<span style='color:green'>"
            self.Yellow = "<span style='color:yellow'>"
            self.Blue = "<span style='color:blue'>"
            self.Reset = "</span>"

        self.colors = {
            'red': self.Red,
            'green': self.Green,
            'yellow': self.Yellow,
            'blue': self.Blue,    
            'reset': self.Reset                 
            }
         
    def printer(self, text, color):
        if self.type == "py":
            print(f"{self.colors[color]}{text}{self.Reset}")
        
        else:
            display(Markdown(f"{self.colors[color]}{text}{self.Reset}"))

    def markdown(self, mark):
        if self.type == "py":
            print(f"[ERROR][helper.py/markdown()] Trying to use markdown with the wrong helper type: {self.type}")
    
        else:
            display(Markdown(f"{mark}{self.Reset}"))
    
    def get_colors(self):
        return self.colors