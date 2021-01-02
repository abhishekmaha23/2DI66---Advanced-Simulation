#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 11:13:21 2020

@author: mickberkhout

Results can be obtained by calling functions: Question1(n, amountOfRuns)
                                              Question2(n, amountOfRuns)
                                              Question3(n, amountOfRuns)
                                              Where n indicates the size of the board

Results of Question 4 are calculated on running the script, amount of runs for this
part need to be adjusted manually. Also, confidence intervals for Question 1 are 
calculated on running the script.

"""
import random

def generatePick(possible_options, delete = True):
    list_number = random.randint(0,len(possible_options)-1)
    pick = possible_options[list_number]
    if(delete):
        del possible_options[list_number]
    return pick

def generateWinOptions(n):
    possible_options = list(range(0,n**2))
    win_options = []
    diagonal_one = []
    diagonal_two = []
    for i in range(0,n):
        # Horizontal results
        win_options.append(possible_options[i*n:(i+1)*n])
        # Vertical results
        win_options.append(possible_options[i::n])
        #Diagonal results
        diagonal_one.append(i*n+i)
        diagonal_two.append((i+1)*n-(i+1))    
    win_options.append(diagonal_one)
    win_options.append(diagonal_two)
    return win_options
 
def playGameConditional(n, start = -1, p1_taken = [], p2_taken = [], turn = 'p1'):
    possible_options = list(range(0,n**2))
    win_options = generateWinOptions(n)
    
    if(start != -1): # Start can only be -1 if it is not set.
        if turn == 'p1':
            p1_taken.append(start)
            turn = 'p2'
            start = -1
            for option in win_options:
                if(set(option) <= set(p1_taken)):
                    return 'p1'
            
        elif turn == 'p2':
            p2_taken.append(start)
            turn = 'p1'
            start = -1
            for option in win_options:
                if(set(option) <= set(p2_taken)):
                    return 'p2'
    
    for move in p1_taken:
        possible_options.remove(move)

    for move in p2_taken:
        possible_options.remove(move)
    
    for i in range(0,len(possible_options)):      
        if(turn == 'p1'):
            p1_taken.append(generatePick(possible_options))
            turn = 'p2'
        else:
            p2_taken.append(generatePick(possible_options))
            turn = 'p1'
        for option in win_options:
            if(set(option) <= set(p1_taken)):
                return 'p1'
            if(set(option) <= set(p2_taken)):
                return 'p2'
    return 'draft'

# Question 1  
def Question1(n, amountOfRuns):
    p1_wins = 0
    p2_wins = 0
    drafts = 0
    for i in range(amountOfRuns):
        game = playGameConditional(n, -1, [], [])
        if(game == 'p1'):
            p1_wins += 1
        elif(game == 'p2'):
            p2_wins += 1
        else:
            drafts += 1
    p1_probability = p1_wins / amountOfRuns
    p2_probability = p2_wins / amountOfRuns
    draft_probability = drafts / amountOfRuns
    return (p1_probability, p2_probability, draft_probability)

# Question 2
def getSymmetry(n):
    if n == 3:
        symmetry = [0,1,4]
    elif n == 4:
        symmetry = [0,1,5]
    elif n == 5:
        symmetry = [0,5,6,10,11,12]
    return symmetry

def Question2(n, amountOfRuns):
    symmetries = getSymmetry(n)
    results = dict()  
    for symmetry in symmetries:
        p1_wins = 0
        p2_wins = 0
        drafts = 0
        for i in range(amountOfRuns):
            game = playGameConditional(n, symmetry, [],[])
            if(game == 'p1'):
                p1_wins += 1
            elif(game == 'p2'):
                p2_wins += 1
            else:
                drafts += 1
        results[(n,symmetry)] = {'Player1': p1_wins/amountOfRuns, 'Player2': p2_wins/amountOfRuns, 'Drafts': drafts/amountOfRuns}
        print('start from', symmetry, ':', results[n,symmetry])

# Question 3
def getGameTaken(n):
    three_game_p1 = [0,8] # cross
    three_game_p2 = [6,7] # circle

    four_game_p1 = [3,5,9,10,11,12] # cross
    four_game_p2 = [1,2,4,6,8,15] # circle
    
    five_game_p1 = [0,2,3,4,6,9,14,16,23] #cross
    five_game_p2 = [1,5,7,11,12,15,18,22,24] # circle

    if(n == 3):
        return (three_game_p1, three_game_p2)
    if(n == 4):
        return (four_game_p1, four_game_p2)
    if(n == 5):
        return (five_game_p1, five_game_p2)


def Question3(n, amountOfRuns): 
    possible_options = list(range(0,n**2))
    (game_p1, game_p2) = getGameTaken(n)
    for move in game_p1:
        possible_options.remove(move)
    for move in game_p2:
        possible_options.remove(move)
    results = dict()
    for move in possible_options:
        p1_wins = 0
        p2_wins = 0
        drafts = 0
        for i in range(amountOfRuns):
            game = playGameConditional(n, move, game_p1.copy(), game_p2.copy())
            if(game == 'p1'):
                p1_wins += 1
            elif(game == 'p2'):
                p2_wins += 1
            else:
                drafts += 1
        results[move] = {'Player1': p1_wins/amountOfRuns, 'Player2': p2_wins/amountOfRuns, 'Drafts': drafts/amountOfRuns}
        print('for move', move, ':', results[move])


#question 4
        
def Simwin(possible_options, turn, taken1, taken2, amountOfRuns): # returns the best move in order to win
    data = dict()
    for move in possible_options:
        p1_wins = 0
        p2_wins = 0
        drafts = 0
        for i in range(amountOfRuns):
            if playGameConditional(3, move, taken1.copy(), taken2.copy(), turn) == 'p1':
                p1_wins +=1
            elif playGameConditional(3, move, taken1.copy(), taken2.copy(), turn) == 'p2':
                p2_wins +=1
            elif playGameConditional(3, move, taken1.copy(), taken2.copy(), turn) == 'draft':
                drafts += 1
        if turn == 'p1':
            data[move] = p1_wins/amountOfRuns
        elif turn == 'p2':
            data[move] = p2_wins/amountOfRuns        
    bestmove = max(data, key=lambda k: data[k])
    return bestmove
        
        
def SimNotLose(possible_options, turn, taken1, taken2, amountOfRuns): # chooses the move with the highest probability of draft or win
    data = dict()
    for move in possible_options:
        p1_wins = 0
        p2_wins = 0
        drafts = 0
        for i in range(amountOfRuns):
            if playGameConditional(3, move, taken1.copy(), taken2.copy(), turn) == 'p1':
                p1_wins +=1
            elif playGameConditional(3, move, taken1.copy(), taken2.copy(), turn) == 'p2':
                p2_wins +=1
            elif playGameConditional(3, move, taken1.copy(), taken2.copy(), turn) == 'draft':
                drafts += 1
        if turn == 'p1':
            data[move] = p1_wins/amountOfRuns + drafts/amountOfRuns
        elif turn == 'p2':
            data[move] = p2_wins/amountOfRuns + drafts/amountOfRuns
    bestmove = max(data, key=lambda k: data[k])
    return bestmove

def Question4(amountOfRuns, strategy1, strategy2, turn ,taken1 = [], taken2 = []): # simulates 1 game with the given strategies
    n=3
    possible_options = list(range(0,n**2))
    win_options = generateWinOptions(n)
    for move in taken1:
        possible_options.remove(move)
    for move in taken2:
        possible_options.remove(move)
    NumberOfTurns = len(possible_options)
    for i in range(0,NumberOfTurns):
        if turn == 'p1':
            if strategy1 == 'Simwin':
                move = Simwin(possible_options,turn, taken1, taken2, amountOfRuns)
            elif strategy1 == 'SimNotLose':
                move = SimNotLose(possible_options, turn, taken1, taken2, amountOfRuns)
            elif strategy1 == 'Random':
                move = generatePick(possible_options, False)
            else:
                print('no valid strategy')
                return
            taken1.append(move)
            possible_options.remove(move)
            turn = 'p2'
        elif turn =='p2':
            if strategy2 == 'Simwin':
                move = Simwin(possible_options,turn, taken1, taken2, amountOfRuns)
            elif strategy2 == 'SimNotLose':
                move = SimNotLose(possible_options, turn, taken1, taken2, amountOfRuns)
            elif strategy2 == 'Random':
                move = generatePick(possible_options, False)
            else:
                print('no valid strategy')
                return
            taken2.append(move)
            possible_options.remove(move)
            turn = 'p1'
        for option in win_options:
            if(set(option) <= set(taken1)):
                print(i, taken1,taken2)
                return 'p1'
            if(set(option) <= set(taken2)):
                print(i, taken1,taken2)
                return 'p2'    
    print(i, taken1,taken2)        
    return 'draft'  

#--------------presenting results of Question4-----------------
import timeit

starttime = timeit.default_timer()

Q4 = dict()  #saves all the probabilities for each situation
for strategy1 in ['Simwin', 'SimNotLose', 'Random']:
    for strategy2 in ['Simwin', 'SimNotLose' , 'Random']:
        p1 = 0
        p2 = 0
        draft = 0
        for i in range(100):
            game = Question4(1000, strategy1, strategy2, 'p1', [], [])
            if game == 'p1': 
                p1 += 1
            elif game == 'p2':
                p2 += 1
            elif game == 'draft':
                draft +=1
        Q4[(strategy1,strategy2)] = {'p1' : p1/100, 'p2' : p2/100, 'draft' : draft/100}

print(Q4)

stop = timeit.default_timer()    
print('Time: ', stop - starttime) 

#---------------presenting confidence intervals--------------------------
from numpy import std, mean

def Q1CI(n): # calculates the confidence intervals for question 1
    p1_probs = list()
    p2_probs = list()
    draw_probs = list()
    for i in range(n):
        temp = Question1(3, 100000)
        p1_probs.append(temp[0])
        p2_probs.append(temp[1])
        draw_probs.append(temp[2])
        print(i)
    return (p1_probs, p2_probs, draw_probs)

list_probs = Q1CI(50)
#print(list_probs)
std_p1_prob = std(list_probs[0])
p1_halfwidth = 1.96 * ((std_p1_prob**2)/ 50)**0.5

p1_prob = mean(list_probs[0])
p1_ci = (p1_prob - p1_halfwidth, p1_prob + p1_halfwidth)

print(p1_prob)
print(p1_ci)

std_p2_prob = std(list_probs[1])
p2_halfwidth = 1.96 * ((std_p2_prob**2)/ 50)**0.5

p2_prob = mean(list_probs[1])
p2_ci = (p2_prob - p2_halfwidth, p2_prob + p2_halfwidth)

print(p2_prob)
print(p2_ci)

std_draw_prob = std(list_probs[2])
draw_halfwidth = 1.96 * ((std_draw_prob**2)/ 50)**0.5

draw_prob = mean(list_probs[2])
draw_ci = (draw_prob - draw_halfwidth, draw_prob + draw_halfwidth)

print(draw_prob)
print(draw_ci)