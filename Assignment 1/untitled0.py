from numpy import zeros
import itertools
import random

if __name__ == '__main__':

    params = dict()
    params['p'] = 2 / 3
    params['beta1'] = 2
    params['beta2'] = 4
    params['delta1'] = 2
    params['delta2'] = 4
    params['tau'] = 1
    params['mu'] = 1 / 2

    T = 10000

    roomProbs = zeros(3)
    t = 0

    np1 = 6
    np2 = 2
    nc1 = 0
    nc2 = 0
    ng = 0

    initial_state = (np1, 0, 0)
    # possible_states = []
    # possible_states.append(initial_state)
    possible_values = [i for i in range(0, np1 + 1)]
    iterations = list(itertools.product(possible_values, repeat=3))
    # print(list(sum(i) for i in iterations))
    filtered = [i for i in iterations if sum(i) == 4]
    # print(sorted(filtered, reverse=True))
    filtered = sorted(filtered, reverse=True)
    print(filtered)
    numberOfStates = len(filtered)
    print(numberOfStates)
    q_matrix = zeros((numberOfStates, numberOfStates))
    p_matrix = zeros((numberOfStates, numberOfStates))
    # print(q_matrix)
    for index, state in enumerate(filtered):
        # state = filtered[i]
        # print(state[0], state[1], state[2])
        # 4 cases possible
        # print(state)
        i = index
        possible_transitions = [(state[0] - 1, state[1] + 1, state[2]), # Type 0 - Person moving from Private room to Common room
                                (state[0] - 1, state[1], state[2] + 1), # Type 1 - Person moving from Private room to Gym
                                (state[0] + 1, state[1] - 1, state[2]), # Type 2 - Person moving from Common to Private room
                                (state[0] + 1, state[1], state[2] - 1)] # Type 3 - Person moving from Gym to Private room
        for type_trans, transition_candidate in enumerate(possible_transitions):
            # print(i)
            try:
                j = filtered.index(transition_candidate)
                # print(i, j, " of type ", type_trans)
                # Setting values of the matrices, because this is incredibly necessary in the simulation
                if type_trans == 0:
                    p_matrix[i, j] = params['p']
                    q_matrix[i, j] = state[0]*params['p']*params['beta1']
                    # pass
                elif type_trans == 1:
                    p_matrix[i, j] = 1 - params['p']
                    q_matrix[i, j] = state[0] * (1 - params['p']) * params['beta1']
                    # pass
                elif type_trans == 2:
                    p_matrix[i, j] = 1
                    q_matrix[i, j] = state[1] * params['delta1']
                    # pass
                elif type_trans == 3:
                    p_matrix[i, j] = 1
                    q_matrix[i, j] = state[2] * params['tau']
                    # pass
                # p_matrix[i, j] = 200
            except:
                # print('Not present so moving on')
                pass
    # print(p_matrix)
    # print(q_matrix)
    for i, row in enumerate(q_matrix):
        # print(i, row)
        q_matrix[i, i] = -sum(row)
    # print(q_matrix)

    print('Beginning simulation')
    # nrStates = len()
    stateProbs = zeros(numberOfStates)
    #
    t = 0  # current time
    state = 0  # current state
    # print(-q_matrix[state, state])
    while t < T:
        # print('Event at t', t)
        dt = random.expovariate(-q_matrix[state, state])  # time till next event
        # print(dt)
        t += dt
        stateProbs[state] += dt
        state = random.choices(range(numberOfStates), weights=p_matrix[state], k=1)[0]
    stateProbs = stateProbs / t
    # # return stateProbs

    print('Probabilities of corresponding states')
    print(stateProbs)