import numpy
from manpy.simulation.imports import Source, Queue, Machine, Exit 

numpy.seterr(all="raise")
import simpy
from manpy.simulation.Globals import G
from manpy.simulation.Order import Order
import manpy.simulation.PrintRoute as PrintRoute
import manpy.simulation.ExcelHandler as ExcelHandler
from manpy.simulation.ProcessingTimeList import ProcessingTimeList
from manpy.simulation.RandomNumberGenerator import RandomNumberGenerator
import time
from random import Random
import manpy.simulation.Globals as Globals



S= Source('S1','Source',interArrivalTime={'Fixed':{'mean':0.5}}, entity='manpy.Part')
Q=Queue('Q1','Queue', capacity=1)
M=Machine('M1','Machine', processingTime={'Fixed':{'mean':0.25}})
E=Exit('E1','Exit') 
#define predecessors and successors for the objects 
S.defineRouting(successorList=[Q])
Q.defineRouting(predecessorList=[S],successorList=[M])
M.defineRouting(predecessorList=[Q],successorList=[E])
E.defineRouting(predecessorList=[M])





print("hello world")