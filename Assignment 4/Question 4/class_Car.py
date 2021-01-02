#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 19:59:39 2020

@author: mickberkhout
"""

class Car:
    
    def __init__(self, isGhost = True, route = [], current_edge = ''):
        self.isGhost = isGhost
        self.route = route
        self.current_edge = ''
        self.edge_traveled = []
        self.traffic_jams = []
        self.edge_depature_time = ''
        self.newInstance = True
        self.departureTime = 0
        self.arrivalTime = 0
        
    def __str__(self):
        return (str(self.isGhost) + str(self.route) + str(self.current_edge))
        
    def nextTravel(self, time):
        if(self.newInstance):
            self.departureTime = time
        else: # If car departs, then set time as depature
            self.edge_traveled.append(self.current_edge)
        self.edge_depature_time = time
        edge = self.route.pop()
        self.current_edge = edge
        
        self.edge_travel_time = edge.getTravelTime()
        self.newInstance = False
        return edge
    
    def isAtDestination(self):
        return (len(self.route) == 0)
    
    def destinationArrival(self, time):
        self.arrivalTime = time
    
    def addTrafficJam(self, time):
        self.traffic_jams.append({'start': time, 'end': 0})
    
    def endTrafficJam(self, time):
        self.traffic_jams[-1]['end'] = time
        return time - self.traffic_jams[-1]['start']