#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 13:54:29 2020

@author: mickberkhout
"""
import random
from numpy import zeros

def simMMcQL (lam , mu , c, T):
    maxQL = 100 # keep track of at most 100 queue - length probabilities
    qlProbs = zeros(maxQL + 1) # empty vector to store these probabilities
    t = 0 # current time
    n = 0 # current state
    while t < T:
        lambdai = (lam + min(n, c) * mu) # lambda_i
        print(lambdai)
        dt = random.expovariate(lambdai ) # time till next event
        t += dt
        if n <= maxQL :
            qlProbs [n] += dt
        u = random.uniform(0, lambdai ) # alternative way to sample
        if u < lam : # arrival
            n += 1
        else : # departure
            n -= 1
    qlProbs = qlProbs / t
    return qlProbs

lam = 0.5
mu = 0.6
c = 1
QLprobs = simMMcQL(lam , mu , c, 100)
print( QLprobs [0:21])