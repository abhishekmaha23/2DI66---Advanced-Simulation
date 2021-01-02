#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 21:58:46 2020

@author: mickberkhout
"""
from scipy import stats
from class_TrafficJam import TrafficJam
import random

class Edge:
    def __init__(self, source_id, target_id, travel_time_distribution):
        self.source_id = source_id
        self.target_id = target_id
        self.travel_time_distribution = travel_time_distribution
        self.jam = '' # Set current travel jam to non-existant

    def __str__(self):
        stri = str(self.source_id) + '-> ' + str(self.target_id) + ' = ' + str(self.travel_time_distribution.rvs())
        return stri

    def __eq__(self, other):
        return self.source_id == other.source_id and self.target_id == other.target_id

    def __hash__(self):
        return hash((self.source_id, self.target_id))
    
    def hasJam(self):
        return (type(self.jam) != str)
    
    def startJam(self, jam):
        self.jam = jam
    
    def endJam(self):
        self.jam = ''
        
    def getJamInterarrival(self):
        alpha = 0.7949678079328055 # interarrival based on monday - friday gamma dist
        loc = 0
        scale = 294.3450468550495
        interarrival_dist = stats.gamma(alpha, loc, scale)
        return interarrival_dist.rvs()
        # Return Jam interarival -- CHECK
        
    def getJamDuration(self):
        shape = 0.9689235428381716
        loc =-2.005873343967834
        scale = 30.310979782335075
        duration_dist = stats.lognorm(shape, loc, scale)
        return duration_dist.rvs()
        # Return Jam Duration -- CHECK
    
    def getNextJam(self, time):
        startTime = time + self.getJamInterarrival()
        endTime = startTime + self.getJamDuration()
        newJam = TrafficJam(startTime, endTime, self)
        return newJam
    
    def getTravelTime(self):
        return self.travel_time_distribution.rvs()