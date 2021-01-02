# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:13:14 2020

@author: s159774
"""

class Event:
    
    #eventttypes
    goto_gym = 1 # mobile patient leaving private room to go to the gym
    goto_commonroom = 2 # mobile patient leaving private room to go to the common room
    goto_privateroom = 3 # mobile patient leaving gym or common room to go to private room
    join_queue_common_to_private = 4 # immobile patient stepping in line to leave the common room
    join_queue_private_to_common = 5 # immobile patient stepping in line to leave the private room
    serve_queue_private = 6 # nurse becomes unavailable
    serve_queue_common = 7 # nurse becomes unavailable
    nurse_return_private = 8 # nurse becomes available again at the private room
    nurse_return_common = 9 # nurse becomes available again at the common room
    arrive_at_common_room = 10 # patient arrives at the common room with nurse
    arrive_at_private_room = 11 # patient arrives at the private room with nurse
    
    def __init__(self,time, person, eventtype):
        self.time = time # time that the event takes place
        self.person = person # patient or nurse object
        self.eventtype = eventtype # number that corresponds to a certain event
        
    def __str__(self):
        return 'person:' + str(self.person) + '\n eventtype:' + str(self.eventtype) + '\n time:' + str(self.time)
        
    def __lt__(self, other):
        return self.time < other.time