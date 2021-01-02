# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:17:00 2020

@author: s159774
"""
from Distribution import Distribution
from class_Event import Event
from class_Patient import Patient
from class_Nurse import Nurse
from class_SimResults import SimResults
from class_FES import FES
from Ass2 import getParams
from scipy import stats
from collections import deque
import random
from numpy import std

class Simulation:
    
    def __init__(self, P1, P2, p, beta1, beta2, delta1, delta2, tau, mu):
        self.P1 = P1
        self.P2 = P2
        self.p = p
        self.beta1 = beta1
        self.beta2 = beta2
        self.delta1 = delta1
        self.delta2 = delta2
        self.tau = tau
        self.mu = mu
        self.P1_private = P1
        self.P1_common = 0 # number of patients in room
        self.P1_gym = 0
        self.P2_private = P2
        self.P2_common = 0
        self.queue_private = deque()
        self.queue_common = deque()

    def __str__(self): # what to return when Simulation object is printed
        return (str(self.P1) + '\n' 
        + str(self.P2)+ '\n' 
        + str(self.p)+ '\n' 
        + str(self.beta1)+ '\n' 
        + str(self.beta2)+ '\n' 
        + str(self.delta1)+ '\n' 
        + str(self.delta2)+ '\n' 
        + str(self.tau)+ '\n' 
        + str(self.mu) + '\n'
        + str(self.test))
        
    def dist(self, distribution):   
        if distribution == 'expon':
            time_beta1 = Distribution(stats.expon(scale = (self.beta1))) #time in private room by mobile patients
            time_beta2 = Distribution(stats.expon(scale = (self.beta2))) # time in private room by immobile patients
            time_delta1 = Distribution(stats.expon(scale = (self.delta1))) # time in common room by mobile patients
            time_delta2 = Distribution(stats.expon(scale = (self.delta2))) # time in common room by immobile patients
            time_tau = Distribution(stats.expon(scale = (self.tau))) # time in gym
            time_mu = Distribution(stats.expon(scale = (self.mu))) # serving time
        elif distribution =='uniform':   
            time_beta1 = Distribution(stats.uniform((0.25*self.beta1), (1.75*self.beta1))) #time in private room by mobile patients
            time_beta2 = Distribution(stats.uniform((0.25*self.beta2), (1.75*self.beta2))) # time in private room by immobile patients
            time_delta1 = Distribution(stats.uniform((0.25*self.delta1), (1.75*self.delta1))) # time in common room by mobile patients
            time_delta2 = Distribution(stats.uniform((0.25*self.delta2), (1.75*self.delta2))) # time in common room by immobile patients
            time_tau = Distribution(stats.uniform((0.25*self.tau), (1.75*self.tau))) # time in gym
            time_mu = Distribution(stats.uniform((0.25*self.mu), (1.75*self.mu))) # serving time
        return (time_beta1, time_beta2, time_delta1, time_delta2, time_tau, time_mu)
        
    def simulate(self, timelim, distribution):
        (time_beta1, time_beta2, time_delta1, time_delta2, time_tau, time_mu) = self.dist(distribution)
        
        t = 0 # start time
        fes = FES() # future event set
        res = SimResults(self.P1,self.P2, timelim) # stores results
        
        #generate nurses
        nurses = list() # nurses[0] for private, nurses[1] for common
        nurses.append(Nurse('immobile', False, 'private room'))
        nurses.append(Nurse('immobile', False, 'common room'))
        
        # generate patients
        mobile_patients = list() 
        immobile_patients = list()
        for i in range(0,self.P1): # generates mobile patients starting in private room
            mobile_patients.append(Patient(str('m') + str(i), 'mobile', 'private room')) # privateroom
            pProb = random.uniform(0,1)
            if pProb < self.p:
                fes.add(Event((t + time_beta1.rvs()), mobile_patients[i], 2)) # goto common room
            elif pProb >= self.p:
                fes.add(Event((t + time_beta1.rvs()), mobile_patients[i], 1)) # goto gym        
        for j in range(0,self.P2): # generates immobile patients starting in private room
            immobile_patients.append(Patient(str('i') + str(i), 'immobile', 'private room' ))
            fes.add(Event(t+time_beta2.rvs(), immobile_patients[j], 5))
            # add event to enter que to go to common room
        
        while t < timelim:
            e = fes.next() # next event
            person = e.person
            new_time = e.time
            #count immobile patients in rooms
            res.registerRoomImmobile(new_time, t, self.P2_private, 'private room')
            res.registerRoomImmobile(new_time, t, self.P2_common, 'common room')          
            # count immobile patients in queue
            res.registerQueue(new_time, t, len(self.queue_private), 'queue private')
            res.registerQueue(new_time, t, len(self.queue_common), 'queue common')
            
            # count mobile patients in rooms
            res.registerRoomMobile(new_time, t, self.P1_private, 'private room')
            res.registerRoomMobile(new_time, t, self.P1_common, 'common room')
            res.registerRoomMobile(new_time, t,  self.P1_gym, 'gym')
            
            res.registerTotal(new_time, t, (self.P1_private + self.P2_private), 'private room')
            res.registerTotal(new_time, t, (self.P1_common + self.P2_common), 'common room')
            
            # simulation for mobile patients
            if person.xtype == 'mobile':
                
                if e.eventtype == 1: # gotogym
                    self.P1_private -= 1
                    person.location = 'gym'
                    self.P1_gym += 1
                    fes.add(Event(new_time+time_tau.rvs(), person, 3)) # goto private
                    
                elif e.eventtype == 2: #goto commonroom
                    self.P1_private -= 1
                    person.location = 'common room'
                    self.P1_common += 1
                    fes.add(Event(new_time+time_delta1.rvs(), person, 3)) # goto private
                    
                elif e.eventtype == 3: # goto private room
                    if person.location == 'gym':
                        self.P1_gym -= 1
                    else:
                        self.P1_common -=1
                    person.location = 'private room'
                    self.P1_private += 1
                    pProb = random.uniform(0,1)
                    if pProb < self.p:
                        fes.add(Event(new_time+time_beta1.rvs(), person, 2)) # goto common room
                    elif pProb >= self.p:
                        fes.add(Event(new_time+time_beta1.rvs(), person, 1)) # goto gym
                
            # simulation for immobile patients    
            elif person.xtype == 'immobile':
                
                if e.eventtype == 4: # join queue to leave common room 
                    if len(self.queue_common) > 0: # join queue
                        self.queue_common.append(person)
                        person.location = 'queue common'
                    elif nurses[1].occupied == True: # join queue
                        self.queue_common.append(person)
                        person.location = 'queue common'
                    else: #goto private room with nurse
                        fes.add(Event(new_time,person,7))
                
                elif e.eventtype == 5: # join queue to leave private room
                    if len(self.queue_private) > 0: # join queue
                        self.queue_private.append(person)
                        person.location = 'queue private'
                    elif nurses[0].occupied == True: # join queue
                        self.queue_private.append(person)
                        person.location = 'queue private'
                    else: #goto common room with nurse
                        fes.add(Event(new_time,person,6))
                        
                elif e.eventtype == 6: # goto common room with nurse
                    if len(self.queue_private) > 0: # if there is a queue the longest waiting patient will be removed
                        person = self.queue_private.pop() # patient travelling with nurse is first in line and removed from line
                    nurses[0].occupied = True # nurse starts serving patient
                    transport = time_mu.rvs()
                    fes.add(Event(new_time + transport, person, 10)) # add arriving event of patient
                    fes.add(Event((new_time + transport + time_mu.rvs()), nurses[0], 8)) # add return event of nurse  
                    
                elif e.eventtype == 7: # goto private room with nurse
                    if len(self.queue_common) > 0: # if there is a queue the longest waiting patient will be removed
                        person = self.queue_common.pop()
                    nurses[1].occupied = True # nurse starts serving patient
                    transport = time_mu.rvs()
                    fes.add(Event(new_time + transport, person, 11)) # add arriving event of patient
                    fes.add(Event((new_time + transport + time_mu.rvs()), nurses[1], 9)) # add return event of nurse  
                    
                elif e.eventtype == 8: # return of nurse to private room
                    nurses[0].occupied = False
                    if len(self.queue_private) > 0:
                        fes.add(Event(new_time, self.queue_private[-1] ,6))
                        
                elif e.eventtype == 9: # return of nurse to common room
                    nurses[1].occupied = False
                    if len(self.queue_common) > 0:
                        fes.add(Event(new_time, self.queue_common[-1] ,7))
                
                elif e.eventtype == 10: #arrival at common room
                    self.P2_private -=1
                    self.P2_common += 1
                    person.location = 'common room'
                    fes.add(Event(new_time + time_delta2.rvs(), person, 4))
     
                elif e.eventtype == 11: #arrival at private room
                    self.P2_common -= 1
                    self.P2_private += 1
                    person.location = 'private room'
                    fes.add(Event(new_time + time_beta2.rvs(), person, 5))        

            t = new_time
                 
        return res
        

# retrieving results for report
import timeit
start = timeit.default_timer()

runs = 100

results = dict()
results['E_Nc_1'] = list()
results['E_Np_1'] = list()
results['E_Nw_1'] = list()
results['E_Nc_2'] = list()
results['E_Np_2'] = list()
results['V_Nc_1'] = list()
results['V_Np_1'] = list()
results['V_Nw_1'] = list()
results['V_Nc_2'] = list()
results['V_Np_2'] = list()
means_common = list()
means_private = list()


for dist in ['expon', 'uniform']:
    for paramSet in ['Set1','Set2','Set3']:
        start = timeit.default_timer()
        print('Results for parameter ' + paramSet + '\nDistribution: ' + dist +'\n')
        results = dict()
        results['E_Nc_1'] = list()
        results['E_Np_1'] = list()
        results['E_Nw_1'] = list()
        results['E_Nc_2'] = list()
        results['E_Np_2'] = list()
        results['V_Nc_1'] = list()
        results['V_Np_1'] = list()
        results['V_Nw_1'] = list()
        results['V_Nc_2'] = list()
        results['V_Np_2'] = list()
        means_common = list()
        means_private = list()
        for i in range(runs):
            sim = Simulation(*getParams(paramSet))
            res = sim.simulate(10000, dist) #choose distribution uniform or expon
            (mean_P1, mean_P2, var_P1, var_P2) = res.getMeans()
            (mean_private, mean_common, mean_gym) = res.getTotalMeans()
            results['E_Nc_1'].append(mean_P1[1])
            results['E_Np_1'].append(mean_P1[0])
            results['E_Nw_1'].append(mean_P1[2])
            results['E_Nc_2'].append(mean_P2[1]) 
            results['E_Np_2'].append(mean_P2[0])
            results['V_Nc_1'].append(var_P1[1])
            results['V_Np_1'].append(var_P1[0])
            results['V_Nw_1'].append(var_P1[2])
            results['V_Nc_2'].append(var_P2[1])
            results['V_Np_2'].append(var_P2[0])
            means_common.append(mean_common)
            means_private.append(mean_private)
            
        # mean and standard deviation of mobile patients in the common room
        E_Nc_mobile = sum(results['E_Nc_1'])/runs
        std_Nc_mobile = (sum(results['V_Nc_1'])/runs)**0.5
        
        # mean and standard deviation of immobile patients in the common room
        E_Nc_immobile = sum(results['E_Nc_2'])/runs
        std_Nc_immobile = (sum(results['V_Nc_2'])/runs)**0.5
        
        # mean and standard deviation of total number of patients in the common room
        E_Nc = E_Nc_mobile + E_Nc_immobile
        std_Nc = ((sum(results['V_Nc_1']) + sum(results['V_Nc_2']))/runs)**0.5
        
        # mean and standard deviation of mobile patients in the private room
        E_Np_mobile = sum(results['E_Np_1'])/runs
        std_Np_mobile = (sum(results['V_Np_1'])/runs)**0.5
        
        # mean and standard deviation of immobile patients in the private room
        E_Np_immobile = sum(results['E_Np_2'])/runs
        std_Np_immobile = (sum(results['V_Np_2'])/runs)**0.5
        
        # mean and standard deviation of total number of patients in the private room
        E_Np = E_Np_mobile + E_Np_immobile
        std_Np = ((sum(results['V_Np_1']) + sum(results['V_Np_2']))/runs)**0.5
        
        # mean and standard deviation of total number of patients in the gym
        E_Nw = sum(results['E_Nw_1'])/runs
        std_Nw = (sum(results['V_Nw_1'])/runs)**0.5
        
        print('E[Nc]: \t ' +str(E_Nc) + '\n' +
              'Std[Nc]: '  +str(std_Nc)+ '\n'+
              'E[Np]: \t '  +str(E_Np) + '\n' +
              'Std[Np]: ' +str(std_Np)+ '\n'+
              'E[Nw]: \t '  +str(E_Nw) +  '\n'+
              'Std[Nw]: '+str(std_Nw)+ '\n')
        
        
        stop = timeit.default_timer()
        
        print('Time: ', stop - start)  
            
        
        # compute the 95%-confidence intervals of E[Nc], E[Np] and E[Nw]
        CI_std_Nc = std(means_common) #(var(results['E_Nc_1']) + var(results['E_Nc_2']))**0.5
        halfwidth_Nc = 1.96 * CI_std_Nc / (runs ** 0.5)
        CI_Nc = (E_Nc - halfwidth_Nc, E_Nc + halfwidth_Nc)
        
        CI_std_Np = std(means_common)#(var(results['E_Np_1']) + var(results['E_Np_2']))**0.5
        halfwidth_Np = 1.96 * CI_std_Np / (runs ** 0.5)
        CI_Np = (E_Np - halfwidth_Np, E_Np + halfwidth_Np)  
        
        CI_std_Nw = std(results['E_Nw_1'])
        halfwidth_Nw = 1.96 * CI_std_Nw / (runs ** 0.5)
        CI_Nw = (E_Nw - halfwidth_Nw, E_Nw + halfwidth_Nw)  
        
        print('CI E[Nc]: \t ' +str(CI_Nc) + '\n' +
              'CI E[Np]: \t ' +str(CI_Np) + '\n' +
              'CI E[Nw]: \t ' +str(CI_Nw) + '\n' + '------------------------------------------------------')

"""    
privates = open('privates.txt','w')
commons = open('commons.txt','w')
gyms = open('gyms.txt','w')
for timelim in [1,5,10,20,50,100,500,1000,2000,5000,10000,50000,100000,1000000] :
    sim = Simulation(*getParams('Set1'))
    res = sim.simulate(timelim, 'expon')   
    (mean_private, mean_common, mean_gym) = res.getTotalMeans()
    privates.write(str(mean_private) + '\n')
    commons.write(str(mean_common) + '\n')
    gyms.write(str(mean_gym) + '\n')
    
privates.close()
commons.close()
gyms.close()
"""  
    
        