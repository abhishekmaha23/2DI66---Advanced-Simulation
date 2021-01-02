# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:13:40 2020

@author: s159774

This class is inspired by the example from the Lecture Notes, Listing 8.4
"""

import heapq

class FES:
    
    def __init__(self):
        self.events = []
        
    def __str__(self): # gives all events when print(FES) is called
        sortedList = sorted(self.events)
        s = ''
        for event in sortedList:
            s += str(event) + '\n'
        return s 
        
    def add(self, event): # adds a new event to the list
        heapq.heappush(self.events, event)
        
    def next(self): # returns next event and deletes it from the list
        return heapq.heappop(self.events)
    
    
    
    
        