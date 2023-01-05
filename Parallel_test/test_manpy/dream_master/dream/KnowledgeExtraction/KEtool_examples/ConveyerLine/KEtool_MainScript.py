'''
Created on 4 Apr 2015

@author: Panos
'''
# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================

from dream.KnowledgeExtraction.ImportCSVdata import ImportCSVdata
from dream.KnowledgeExtraction.DistributionFitting import Distributions
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.JSONOutput import JSONOutput
from dream.KnowledgeExtraction.DetectOutliers import DetectOutliers
from dream.KnowledgeExtraction.ReplaceMissingValues import ReplaceMissingValues
import json
import os
################### Import data using the ImportCSVdataobject ###################################
def main(test=0, CSVFileName1='InterArrivalData.csv',
                CSVFileName2='DataSet.csv',
                JSONFileName='JSON_ConveyerLine.json',
                jsonFile=None, csvFile1=None, csvFile2=None):
    if csvFile2:
        CSVFileName2 = csvFile2.name
    if csvFile1:
        CSVFileName1 = csvFile1.name
    
    CSV=ImportCSVdata()   #call the Import_CSV module and using its method Input_data import the data set from the CSV file to the tool
    procData=CSV.Input_data(CSVFileName2)
    sourceData=CSV.Input_data(CSVFileName1)
    M1=procData.get('M1',[])       #get from the returned Python dictionary the data sets
    M2=procData.get('M2',[])
    S1=sourceData.get('S1',[])
    
    ################### Processing of the data sets calling the following objects ###################################
    #Replace missing values calling the corresponding object
    missingValues=ReplaceMissingValues()
    M1=missingValues.DeleteMissingValue(M1)
    M2=missingValues.DeleteMissingValue(M2)
    S1=missingValues.ReplaceWithMean(S1)
    
    #Detect outliers calling the DetectOutliers object
    outliers=DetectOutliers()
    M1=outliers.DeleteExtremeOutliers(M1)
    M2=outliers.DeleteExtremeOutliers(M2)
    S1=outliers.DeleteOutliers(S1)
    
    #Conduct distribution fitting calling the Distributions object and DistFittest object
    MLE=Distributions()
    KStest=DistFittest()
    M1=KStest.ks_test(M1)
    M2=KStest.ks_test(M2)
    S1=MLE.Exponential_distrfit(S1)
    #================================= Output preparation: output the updated values in the JSON file of this example =========================================================#
    if not jsonFile:
        jsonFile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), JSONFileName),'r')      #It opens the JSON file 
        data = json.load(jsonFile)             #It loads the file
        jsonFile.close()
    else:
        data = json.load(jsonFile) 
    
    exportJSON=JSONOutput()
    stationId1='M1'
    stationId2='M2'
    stationId3='S1'
    
    data=exportJSON.ProcessingTimes(data, stationId1, M1)                           
    data1=exportJSON.ProcessingTimes(data, stationId2, M2)
    data2=exportJSON.InterarrivalTime(data1, stationId3, S1)
    
    # if we run from test return the data2
    if test:
        return data2
    
    jsonFile = open('JSON_ConveyerLine_Output.json',"w")     #It opens the JSON file
    jsonFile.write(json.dumps(data2, indent=True))           #It writes the updated data to the JSON file 
    jsonFile.close()                                         #It closes the file
    
if __name__ == '__main__':
    main()