# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:55:04 2020

@author: giova
"""

import xlsxwriter 

def mat2excel(sheet = 'Sheet1', size = [1,1]):
    '''
    function that given a sheet name and a list of 2 elements [nrows, ncolumns]
    returns the range of an excel sheet 
    
    Example: mat2excel(sheet = 'Sheet1', size = [2,2]) --> 'Sheet1!A1:B2'
    
    NOTE: currently up to 26 columns!!!
    '''
#    if size[1] >26:
#    
#        raise Exception('The required matrix is too big for this function (too many columns') 
#    
#    return sheet+ '!A1:' + chr(ord('@') + size[1])  + str(size[0]) 
    return sheet+ '!A1:' + xlsxwriter.utility.xl_col_to_name(size[1]-1)  + str(size[0]) 
############################################################################################################
# CPLEX
############################################################################################################    

#
#import xlwt 
#from xlwt import Workbook 
## Workbook is created 
#wb = Workbook() 
#
#
#cplex_path = r"C:\Users\giova\opl\MSM-1-V1"
#filename = cplex_path +r'\input2.xls'
#run_config = r' Configuration1'
#cplex_cmd = r'oplrun -p ' +cplex_path + run_config
#
##% preparo matrici
#sheet = 'init' # init: dimensioni del problema
#sheet1 = wb.add_sheet(sheet, cell_overwrite_ok=True) 
#
##xlRange = r'A1'  #[num2let(max(size(NumeroEventi))),num2str(max(size(NumeroEventi)))];
#sheet1.write(0, 0, max_events)      #xlswrite(filename,  NumeroEventi  ,sheet,xlRange)
#
#
#
#sheet = 'input'; # input: dimensioni standard % ="m!A1:A"&init!A1
#sheet2 = wb.add_sheet(sheet, cell_overwrite_ok=True) 
#
##%pesi m:
##s = '="m!A1:A' + str(n_activity_u) + '"'
#s = 'm!A1:A' + str(n_activity_u)
#sheet2.write(0, 0, s)   #xlswrite(filename,  s ,sheet,'A1')
#
#s = 'a!A1:' + chr(ord('@') + np.shape(ARCS)[1])  + str(np.shape(ARCS)[1])  
#sheet2.write(1, 0, s)     #xlswrite(filename,  s ,sheet,'A2')
#
#s = 'c!A1:' + chr(ord('@') + np.shape(ARCS)[1])  + str(np.shape(ARCS)[1])  
#sheet2.write(2, 0, s)     #xlswrite(filename,  s ,sheet,'A3')
#
#s = 'E!A1'
#sheet2.write(3, 0, s)  #xlswrite(filename,  s ,sheet,'A4')
#
#s = 'beta!A1:A' + str(n_activity_u)
#sheet2.write(4, 0, s)  #xlswrite(filename, s ,sheet,'A5')
#
#
#s = 'gamma!A1:'+ chr(ord('@') + np.shape(ARCS)[1])  + str(np.shape(ARCS)[1])
#sheet2.write(5, 0, s)  #xlswrite(filename,  s ,sheet,'A6')     
#
#
#sheet = 'm'
#sheet3 = wb.add_sheet(sheet, cell_overwrite_ok=True) 
#
#
#for x, value in np.ndenumerate(NODES):    #sheetrange =  ['A1:',num2let(size(NODES,2)),  num2str(size(NODES,1)) ]    ;
#    sheet3.write(x[0], 0, value)  #xlswrite(filename,  NODES ,sheet,sheetrange)     
#
#
#sheet = 'a'
#sheet4 = wb.add_sheet(sheet, cell_overwrite_ok=True) 
#
#for (x,y), value in np.ndenumerate(ARCS): #sheetrange =  ['A1:',num2let(size(ARC,2)),  num2str(size(ARC,1)) ]    ;
#    sheet4.write(x,y,value) #xlswrite(filename,  ARC ,sheet,sheetrange)     
#
#sheet = 'c';
#sheet5 = wb.add_sheet(sheet, cell_overwrite_ok=True)
# 
#for (x,y), value in np.ndenumerate(ARCS): #sheetrange =  ['A1:',num2let(size(ARC,2)),  num2str(size(ARC,1)) ]    ;
#    if value > 0:
#        sheet5.write(x,y,1) #xlswrite(filename,  double(ARC>0),sheet,sheetrange)       
#        
#sheet = 'E'
#sheet6 = wb.add_sheet(sheet, cell_overwrite_ok=True)
#sheet6.write(0,0,max_events) #xlswrite(filename,  MaxEventi ,sheet,sheetrange)   
#
#
#sheet = 'beta'
#sheet7 = wb.add_sheet(sheet, cell_overwrite_ok=True)
#
#sheet = 'gamma'
#sheet8 = wb.add_sheet(sheet, cell_overwrite_ok=True)
#
#wb.save(filename) 
#
#
#os.system(cplex_cmd)    #% run cplex model

############################################################################################################
#% gather results
#import xlrd
#
##beta = xlsread(filename, 'beta');
##gamma = xlsread(filename, 'gamma');
#
#wb = xlrd.open_workbook(filename) 
#sheet = wb.sheet_by_index(0) 
#sheet.cell_value(0, 0) 
#  
#for i in range(sheet.nrows): 
#    print(sheet.cell_value(i, 0)) 
    

# recupero nuovo activity_corr_data
    
# nuovo capacity_data (tra gli eventi che sono rimasti)

# nuovo grafo