# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:16:03 2020

@author: s159774
"""

class Nurse:
    
    def __init__(self,xtype , occupied, base):
        self.xtype = xtype # always for immobile patients
        self.occupied = occupied # boolean, True when nurse busy
        self.base = base # private room/common room
        
    def __str__(self):
        return 'occupied: ' + self.occupied + '\n base: ' + self.base


    