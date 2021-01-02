#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 19:59:39 2020

@author: mickberkhout
"""
from collections import deque
import random

class TrafficJam:
    
    def __init__(self, startTime, endTime, edge):
        self.startTime = startTime
        self.endTime = endTime
        self.edge = edge
        self.location_on_edge = random.random()
        self.queue = deque()
        self.processingTime = 2/60 # 2 seconds, depending on the time units that are used
        
    def addCar(self, car):
        self.queue.append(car)
    
    def removeCar(self, car):
        self.queue.remove(car)
    
    def getQueueLength(self):
        return len(self.queue)
    
    def getLeavingCar(self):
        car = self.queue[0]
        return car # REturn the car that leaves the queue next
    
    def getProcessingTime(self):
        return self.processingTime