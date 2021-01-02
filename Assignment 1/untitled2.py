#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 20:06:23 2020

@author: mickberkhout
"""

params = dict()
params['p'] = 2 / 3
params['beta1'] = 2
params['beta2'] = 4
params['delta1'] = 2
params['delta2'] = 4
params['tau'] = 1
params['mu'] = 1 / 2
    
# Helper function to keep code cleaner
def is_busy(nurse):
    if(nurse == 'B'):
        return True
    else:
        return False

def is_idle(nurse):
    if(nurse == 'I'):
        return True
    else:
        return False

# -- GENERATION OF possible STATES --
np2 = 4
possible_values = [i for i in range(0, np2 + 1)]
iterations = list(itertools.product(possible_values, repeat=4))
filtered = [i for i in iterations if sum(i) >= 2 and sum(i) <= 4]

all_states = []
# Add all nurse combinations to states
nurse_states = ['I','B','R']
for i in filtered:
    for nurse_1 in nurse_states:
        for nurse_2 in nurse_states:
            new_i = list(i)
            new_i.insert(2, nurse_1)
            new_i.insert(5, nurse_2)
            all_states.append(new_i)


# state[0] = Number in Private Room
# state[1] = Number in Queue for Nurse 1
# state[2] = Status of Nurse 1 (either I (idle) or B (busy) or R (returning))
# state[3] = Number in common Room
# state[4] = Number in Queue for Nurse 2
# state[5] = Status of Nurse 2 (either I (idle) or B (busy) or R (returning))

# Remove all states that are not possible
final_states = []
for state in all_states:
    state_sum = state[0] + state[1] + state[3] + state[4]
    
    # If one of the nurses is busy, there must be np-1 patients tracked
    if((not is_busy(state[2]) and is_busy(state[5])) or (is_busy(state[2]) and not is_busy(state[5]))):
        if(state_sum != np2-1):
            continue
    
    # If both nurses are busy, there must be np-2 patients tracked
    if(is_busy(state[2]) and is_busy(state[5])):
        if(state_sum != np2-2):
            continue
    
    # if both nurses are not busy, all 4 patients must be tracked
    if(not is_busy(state[2]) and not is_busy(state[5])):
        if(state_sum != np2):
            continue
    
    # If nurse 1 is idle, there cannot be a queue in front of the nurse 1
    if(state[1] >= 1 and state[2] == 'I'):
        continue
    
    # If nurse 2 is idle, there cannot be a queue in front of the nurse 2
    if(state[4] >= 1 and state[5] == 'I'):
        continue
    
    final_states.append(tuple(state)) # Transform back to tuple

# -- GENERATION of Matrix -- 
numberOfStates = len(final_states)
q_matrix = zeros((numberOfStates, numberOfStates))

for index, state in enumerate(final_states):
    state = list(state)
    x = index
    
    # -- Part 1: From private room -- #
    
    # Patients enters the Queue of the Private Rooms
    if(state[0] >= 1 and not is_idle(state[2])):
        #print('1')
        look_for = state.copy()
        look_for[0] = state[0] - 1
        look_for[1] = state[1] + 1
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['beta2'] * state[0] # b2 * people in common
        
    # Patient wants to enter Queue of Private Rooms, but Queue is empty (serve directly)
    if(state[0] >= 1 and is_idle(state[2])):
       # print('2')
        look_for = state.copy()
        look_for[0] = state[0] - 1
        look_for[2] = 'B'
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['beta2'] * state[0] # b2 * people in common
        
    # Nurse 1 returns and there is still a queue to serve
    if(state[1] >= 1 and state[2] == 'R'):
       # print('3')
        look_for = state.copy()
        look_for[1] = state[1] - 1
        look_for[2] = 'B'
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['mu'] # mu
    
    # Nurse 1 returns and there is no queue to serve
    if(state[1] == 0 and state[2] == 'R'):
        #print('4')
        look_for = state.copy()
        look_for[2] = 'I'
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['mu'] # mu
        
    # Nurse 1 brings patient to common room 
    if(state[2] == 'B'):
        #print('5')
        look_for = state.copy()
        look_for[2] = 'R'
        look_for[3] = state[3] + 1
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['mu'] # mu
    
    # -- Part 2: From common room -- #
    
    # Patients enters the Queue of the Common Rooms
    if(state[3] >= 1 and not is_idle(state[5])):
        #print('6')
        look_for = state.copy()
        look_for[3] = state[3] - 1
        look_for[4] = state[4] + 1
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['delta2'] * state[3] # b2 * people in common
        
    # Patient wants to enter Queue of Common Rooms, but Queue is empty (serve directly)
    if(state[3] >= 1 and is_idle(state[5])):
        #print('7')
        look_for = state.copy()
        look_for[3] = state[3] - 1
        look_for[5] = 'B'
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['delta2'] * state[3] # b2 * people in common
        
    # Nurse 2 returns and there is still a queue to serve
    if(state[4] >= 1 and state[5] == 'R'):
       # print('8')
        look_for = state.copy()
        look_for[4] = state[4] - 1
        look_for[5] = 'B'
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['mu'] # mu
    
    # Nurse 2 returns and there is no queue to serve
    if(state[4] == 0 and state[5] == 'R'):
        #print('9')
        look_for = state.copy()
        look_for[5] = 'I'
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['mu'] # mu
        
    # Nurse 2 brings patient to private room 
    if(state[5] == 'B'):
        #print('10')
        look_for = state.copy()
        look_for[5] = 'R'
        look_for[0] = state[0] + 1
        y = final_states.index(tuple(look_for))
        q_matrix[x, y] = params['mu'] # mu

for i, row in enumerate(q_matrix):
    # print(i, row)
    q_matrix[i, i] = -sum(row)