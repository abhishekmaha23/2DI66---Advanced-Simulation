# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:13:14 2020

@author: s159774
"""

class Event:
    
    def __init__(self, time, obj, eventtype):
        self.time = time # Time that event happens
        self.obj = obj # Object of event
        self.eventtype = eventtype # Name of event
        
    def __str__(self):
        return 'Person: ' + str(self.person) + 'undergoes event "' + str(self.eventtype) + '" at time:' + str(self.time)
        # person???
    def __lt__(self, other):
        return self.time < other.time