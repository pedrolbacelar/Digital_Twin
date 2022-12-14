# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 15:47:10 2021

@author: giuli
"""




from supervisor_class.validator_class.levenshteinDistance import levenshteinDistance
import numpy as np

class validator():

   # def __init__(self,type_validation,data_real,data_sim,threshold_logic,threshold_input): #potremmo anche mettere solo threshold generale e non entrambi, tanto è legato al type_validation iniziale
   def __init__(self,type_validation,threshold):
       self.type_validation=type_validation
       # self.data_real=data_real
       # self.data_sim=data_sim
       self.threshold=threshold
       # self.threshold_input=threshold_input
        
          
   def event_v(self,data_real,data_sim):
       
       #if self.type_validation=='logic':
                
                ind= 1-levenshteinDistance(data_real[:],data_sim[:])/max(len(data_real[:]),len(data_sim[:]))
                if ind>= self.threshold:
                    value=1
                else:
                    value=0
                
                data=[value,ind]
               
                return data
            
   def input_trace(self,processing_times_real,dist,param):
        #processing_times matrice di processing times
        #distribution matrice per ogni processing time ho tipo e parametri
        from ecdf import ecdf
        import scipy.stats
        from scipy.stats import norm
        from scipy.stats import beta
        from scipy.stats import gamma
        from scipy.stats import lognorm
        from scipy.stats import pareto
        from scipy.stats import logistic
        from scipy.stats import rayleigh
        from scipy.stats import uniform
        from scipy.stats import triang
     
         
        n_parts=np.size(processing_times_real)
        u_p=np.array([])
        X_p,F_p = ecdf(processing_times_real)
        for ii in range(n_parts):
          u_p = np.append(u_p,F_p[np.asarray(np.where(X_p == processing_times_real[ii]))])

        """Experimental Settings"""

        
          #1. uniform Distribution
        if dist == 1:
            distribution='uniform'
            y_p = uniform.ppf(u_p,param[0],param[1]) 
            
              #2. triang Distribution
        if dist  == 2:
            distribution='triang'
            #y_p = triang.ppf(u_p,param[0],param[1],param[2]) 
            y_p =triang.ppf(u_p,(param[2]-param[0])/param[1]-param[0],param[0],param[1]-param[0]) ######
        
        #  3. Normal
        if dist == 3:
            distribution='tnormal'
            y_p = norm.ppf(u_p,param[0],param[1]) 
        
        #  4. Beta Distribution
        if dist == 4:
            distribution='Beta'
            y_p =beta.ppf(u_p,param[0],param[1])*(max(processing_times_real)-min(processing_times_real))
        
        #  5. Gamma Distribution
        if dist == 5:
            distribution='Gamma'
            y_p = gamma.ppf(u_p,param[0],param[1],param[2]) 
            
        #  6. Lognormal Distribution
        if dist == 6:
            distribution='Lognormal'
            y_p = lognorm.ppf(u_p,param[0],param[1],param[2]) 
                 
        #  7. Pareto Distribution
        if dist == 7:
            distribution='pareto'
            y_p = pareto.ppf(u_p,param[0],param[1],param[2]) 
            
        #  8. Logistic Distribution
        if dist == 8:
            distribution='logistic'
            y_p = logistic.ppf(u_p,param[0],param[1]) 
            
              #9. rayleigh Distribution
        if dist == 9:
            distribution='rayleigh'
            y_p = rayleigh.ppf(u_p,param[0],param[1]) 
       



        if max(y_p) == np.inf:
            pos = np.where(y_p==np.inf)
            pos=np.asarray(pos)
            y_p[pos] = processing_times_real[pos]

        correlated_processing_time=y_p

         
        return correlated_processing_time
       
            
   # def input_v(self,data_real,data_sim): #magari possiamo mettere tutto dentro la stessa funzione sia input che logic e poi sara if che fa la differenza 
       
   #     if self.type_validation=='input':
           
   #          ind= 1-levenshteinDistance(data_real[:],data_sim[:])/max(len(data_real[:]),len(data_sim[:]))
   #          if ind>= self.threshold:
   #              value=1
   #          else:
   #                  value=0
   #          data=[value,ind]
            
   #          return data