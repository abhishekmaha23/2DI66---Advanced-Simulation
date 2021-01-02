# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:52:21 2020

@author: s159774
"""

def getParams(xset):
    Set = xset
#---------SET1---------------------------------

    if Set == 'Set1':
        P1 = 4
        P2 = 2
        p = 2/3
        beta1 = 2
        beta2 = 4
        delta1 = 2
        delta2 = 4
        tau = 1
        mu = 1/2
        return P1,P2,p,beta1,beta2,delta1,delta2,tau,mu
    #---------SET2---------
    elif Set == 'Set2':
        P1 = 6
        P2 = 1
        p = 1/2
        beta1 = 1
        beta2 = 3
        delta1 = 2
        delta2 = 6
        tau = 1
        mu = 1/2
        return P1,P2,p,beta1,beta2,delta1,delta2,tau,mu
    #---------Set3----------    
    elif Set == 'Set3':
        P1 = 2
        P2 = 4
        p = 1/3
        beta1 = 1
        beta2 = 3
        delta1 = 2
        delta2 = 4
        tau = 2
        mu = 1/3
        return P1,P2,p,beta1,beta2,delta1,delta2,tau,mu 
    else:
        print('no valid set')
 #-------------------------------------------  

        
        
    
        
        
    















 