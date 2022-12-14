# Class that gets as input the filename and creates an object which is a list (self.ProcList) and an index (self.index)
# We must define a function that returns the processing time from the list in the correct index, and then increases the
# index by 1, in order to get the following processing time
from .Globals import G

class ProcessingTimeList(object):

    def __init__(self, fileName, procList):
        self.index = 0          # The index for choosing the correct processing time

        if fileName != None and procList == None:       # if the processing times come from a txt file
            fileName = fileName + ".txt"       # getting the correct filename
            my_file = open(fileName, "r")     # open the file
            content = my_file.read()          # read the file
            my_file.close()
            self.ProcList = content.split("\n")    # convert the data into a list of strings
            # self.tempNaN = int((''.join(self.ProcList).rindex(' NaN'))/4 + 1)       # eliminate all the NaN values
            # self.ProcList = self.ProcList[self.tempNaN:]
            for i in range(len(self.ProcList)):
                self.ProcList[i] = float(self.ProcList[i])        # converting the list of strings into a list of int
        else:                           # if the processing times come from a list variable
            self.ProcList = procList
        self.ProcList[-1] -= 3.2        # ONLY FOR LEGO MODEL TO CALCULATE THE FINAL POSITION
        self.ProcList.append(G.traceStop)  # append a value to the end of the list for finishing the simulation

        self.listLen = len(self.ProcList)                   # length of the list of the processing time

    def obtainNumber(self):                         # method to return the correct processing time
        self.index += 1                             # first we increase the index
        number = self.ProcList[self.index-1]
        return number                               # we return the correct processing time
