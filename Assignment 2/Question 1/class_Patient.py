# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:15:25 2020

@author: s159774
"""

class Patient:
    
    def __init__(self,xid, xtype, location):
        self.xid = xid # used to identify patients during debugging
        self.xtype = xtype # immobile or mobile
        self.location = location # current location of patient
       
    def __str__(self):
        return (str(self.xid) +
        '\n type: ' + str(self.xtype) +
        '\n location: ' + str(self.location ))