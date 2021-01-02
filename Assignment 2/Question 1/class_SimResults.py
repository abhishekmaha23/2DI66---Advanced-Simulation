# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:16:33 2020

@author: s159774
"""
from numpy.ma.core import zeros
import matplotlib.pyplot as plt

class SimResults:
    
    def __init__(self,P1,P2, timelim):
        self.P1 = P1 # needed to create zeros array for histogram
        self.P2 = P2 # needed to create zeros array for histogram
        self.timelim = timelim # the timelimit of the simulation
        self.M_common_room_Histogram = zeros(P1 + 1) # list that counts time that N mobile patients reside in common room during simulation
        self.M_private_room_Histogram = zeros(P1 + 1) # list that counts time that N mobile patients reside in private room during simulation
        self.M_gym_Histogram = zeros(P1 + 1) # list that counts time that N patients reside in the gym during simulation
        self.M_sum_in_common = 0 # used for calculating the mean number of mobile patients in the common room
        self.M_sum_in_common2 = 0 # used for calculating the variance of mobile patients in the common room
        self.M_sum_in_private = 0 # used for calculating the mean numberof mobile patients in the private room
        self.M_sum_in_private2 = 0 # used for calculating the variance of mobile patients in the private room
        self.M_sum_in_gym = 0 # used for calculating the mean number of mobile patients in the gym
        self.M_sum_in_gym2 = 0 # used for culculating the variance of the number of patients in the gym
        self.I_common_room_Histogram = zeros(P2 + 1) # list that count time that N immobile patients reside in the common room 
        self.I_private_room_Histogram = zeros(P2 + 1) # list that counts time that N immobile patient reside in the private room
        self.I_sum_in_common = 0 # used for calculating the mean number of immobile patients in the common room
        self.I_sum_in_common2 = 0 # used for calculating the variance of the number of immobile patients in the common room
        self.I_sum_in_private = 0 # used for calculating the mean number of immobile patients in the private room
        self.I_sum_in_private2 = 0
        self.I_sum_Qcommon = 0 # used for calculating the mean number of immobile patients in the queue at the common room
        self.I_sum_Qcommon2 = 0 # used for calculating the variance of the number of immobile patients in the queue at the common room
        self.I_sum_Qprivate = 0 # used for calculating the mean number of immobile patients in the queue at the private room
        self.I_sum_Qprivate2 = 0 # used for calculating the variance of the number of immobile patients in the queue at the private room
        self.I_Qcommon_Histogram = zeros(P2 +1)
        self.I_Qprivate_Histogram = zeros(P2 + 1)
        self.sum_in_common = 0
        self.sum_in_private = 0

    def __str__(self):
        return ('histogram mobile:\n' +
                str(self.M_common_room_Histogram) + '\n' +
                str(self.M_private_room_Histogram) + '\n' +
                str(self.M_gym_Histogram) + '\n' +
                'histogram immobile: \n' +
                str(self.I_common_room_Histogram) + '\n' +
                str(self.I_private_room_Histogram) + '\n' +
                'histogram queues: \n' +
                str(self.I_Qcommon_Histogram) + '\n' +
                str(self.I_Qprivate_Histogram))
        
    
    def registerRoomMobile(self, new_time, old_time, number_in_room, room):
        if room == 'private room':
            self.M_sum_in_private += number_in_room * ( new_time - old_time) 
            self.M_sum_in_private2 += number_in_room**2 * ( new_time - old_time )
            self.M_private_room_Histogram[number_in_room] += ( new_time - old_time )
        elif room == 'common room':
            self.M_sum_in_common += number_in_room * ( new_time - old_time )
            self.M_sum_in_common2 += number_in_room**2 * ( new_time - old_time )
            self.M_common_room_Histogram[number_in_room] += ( new_time - old_time )
        elif room == 'gym':
            self.M_sum_in_gym += number_in_room * ( new_time - old_time )
            self.M_sum_in_gym2 += number_in_room**2 * ( new_time - old_time )
            self.M_gym_Histogram[number_in_room] += ( new_time - old_time )
            
    def registerRoomImmobile(self, new_time, old_time, number_in_room, room):
        if room == 'private room':
            self.I_sum_in_private += number_in_room * ( new_time - old_time) 
            self.I_sum_in_private2 += number_in_room**2 * ( new_time - old_time )
            self.I_private_room_Histogram[number_in_room] += ( new_time - old_time )
        elif room == 'common room':
            self.I_sum_in_common += number_in_room * ( new_time - old_time )
            self.I_sum_in_common2 += number_in_room**2 * ( new_time - old_time )
            self.I_common_room_Histogram[number_in_room] += ( new_time - old_time )
            
    def registerTotal(self, new_time, old_time, number_in_rooms, room):
            if room ==  'private room':
                self.sum_in_private += (number_in_rooms * (new_time - old_time))
            elif room == 'common room':
                self.sum_in_common += (number_in_rooms * (new_time - old_time))
            
    def registerQueue(self,new_time, old_time, number_in_queue, queue):
        if queue == 'queue common':
            self.I_sum_Qcommon += number_in_queue * (new_time - old_time)
            self.I_sum_Qcommon2 += number_in_queue**2 * (new_time - old_time)
            self.I_Qcommon_Histogram[number_in_queue] += (new_time - old_time)
        elif queue == 'queue private':
            self.I_sum_Qprivate += number_in_queue * (new_time - old_time)
            self.I_sum_Qprivate2 += number_in_queue**2 * (new_time - old_time)
            self.I_Qprivate_Histogram[number_in_queue] += (new_time - old_time)
            
    def plotHist(self):
        fig_M_common_hist = plt.figure()
        plt.title('Time of mobile patients in common room')
        plt.xlabel('Number of mobile Patients')
        plt.ylabel('Time units')
        plt.bar(list(range(0,len(self.M_common_room_Histogram))), self.M_common_room_Histogram)
        plt.xticks(range(0,len(self.M_common_room_Histogram)))
        plt.savefig('fig_M_common_hist.png')
        
        fig_I_common_hist = plt.figure()
        plt.title('Time of immobile patients in common room')
        plt.xlabel('Number of immobile Patients')
        plt.ylabel('Time units')
        plt.xticks(range(0,len(self.I_common_room_Histogram)))
        plt.bar(list(range(0,len(self.I_common_room_Histogram))), self.I_common_room_Histogram)
        plt.savefig('fig_I_common_hist.png')
        
        fig_M_private_hist = plt.figure()
        plt.title('Time of mobile patients in private room')
        plt.xlabel('Number of mobile Patients')
        plt.ylabel('Time units')
        plt.xticks(range(0,len(self.M_private_room_Histogram)))
        plt.bar(list(range(0,len(self.M_private_room_Histogram))), self.M_private_room_Histogram)
        plt.savefig('fig_M_private_hist.png')
        
        fig_I_private_hist = plt.figure()
        plt.title('Time of immobile patients in private room')
        plt.xlabel('Number of immobile Patients')
        plt.ylabel('Time units')
        plt.xticks(range(0,len(self.I_private_room_Histogram)))
        plt.bar(list(range(0,len(self.I_private_room_Histogram))), self.I_private_room_Histogram)
        plt.savefig('fig_I_private_hist.png')
        
        fig_M_gym_hist = plt.figure()
        plt.title('Time of mobile patients in gym')
        plt.xlabel('Number of mobile Patients')
        plt.ylabel('Time units')
        plt.xticks(range(0,len(self.M_gym_Histogram)))
        plt.bar(list(range(0,len(self.M_gym_Histogram))), self.M_gym_Histogram)
        plt.savefig('fig_M_gym_hist.png')
        
        fig_Q_common_hist = plt.figure()
        plt.title('Number of immobile patients waiting in the queue of the common room')
        plt.xlabel('Number of immobile Patients')
        plt.ylabel('Time units')
        plt.xticks(range(0,len(self.I_Qcommon_Histogram)))
        plt.bar(list(range(0,len(self.I_Qcommon_Histogram))),self.I_Qcommon_Histogram)
        plt.savefig('fig_I_Qcommon_hist.png')
        
        fig_Q_private_hist = plt.figure()
        plt.title('Number of immobile patients waiting in the queue of the private room')
        plt.xlabel('Number of immobile Patients')
        plt.ylabel('Time units')
        plt.xticks(range(0,len(self.I_Qprivate_Histogram)))
        plt.bar(list(range(0,len(self.I_Qprivate_Histogram))),self.I_Qprivate_Histogram)
        plt.savefig('fig_I_Qprivate_hist.png')
        
        
        return plt.show()
            
            
        
    def getMeans(self):
        P1_mean_common = self.M_sum_in_common/self.timelim
        P1_var_common = (self.M_sum_in_common2/self.timelim) - P1_mean_common**2
        P1_mean_private = self.M_sum_in_private/self.timelim
        P1_var_private = (self.M_sum_in_private2/self.timelim) - P1_mean_private**2
        P1_mean_gym = self.M_sum_in_gym/self.timelim
        P1_var_gym = (self.M_sum_in_gym2/self.timelim) - P1_mean_gym**2
        P2_mean_common = self.I_sum_in_common/self.timelim
        P2_var_common = (self.I_sum_in_common2/self.timelim) - P2_mean_common**2
        P2_mean_private = self.I_sum_in_private/self.timelim
        P2_var_private = (self.I_sum_in_private2/self.timelim) - P2_mean_private**2
        mean_P1 = (P1_mean_private, P1_mean_common, P1_mean_gym)
        mean_P2 = (P2_mean_private, P2_mean_common)
        var_P1 = (P1_var_private, P1_var_common, P1_var_gym)
        var_P2 = (P2_var_private, P2_var_common)
        return (mean_P1, mean_P2, var_P1, var_P2)
    
    def getTotalMeans(self):
        mean_private = (self.sum_in_private/self.timelim)
        mean_common = (self.sum_in_common/self.timelim)
        mean_gym = self.M_sum_in_gym/self.timelim
        return (mean_private, mean_common, mean_gym)
        
    
  