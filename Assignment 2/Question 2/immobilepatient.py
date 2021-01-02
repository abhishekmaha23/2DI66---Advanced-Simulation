from numpy import zeros
from util import simulation,get_params


def immobile_patient_simulation(params, initial_state):
    '''
    Gateway to initialize entire simulation. Actual simulation logic is in the util file. This file
    contains generator matrix creation as well as aggregated statistics calculation.
    It receives the parameters for the simulation as well as the initial state.
    :param params:
    :param initial_state:
    :return:
    '''
    q_matrix, filtered_states = immobile_q_matrix_generation(params)
    initial_state_index = filtered_states.index(initial_state)
    state_probabilities = simulation(q_matrix, initial_state_index, params['T'])
    average_per_room = immobile_patient_stats(state_probabilities, filtered_states, params['np2'])
    return average_per_room


# Generation of the Q Matrix
def immobile_q_matrix_generation(params):
    '''
    Receives parameters, identifies all possible n states in the system, then creates an n*n generator matrix containing
    the transition rates. These rates are described in the report.
    :param params:
    :return:
    '''
    # Two simple help functions to make code more readable
    def is_busy(nurse):
        if nurse == 'B':
            return True
        else:
            return False

    def is_idle(nurse):
        if nurse == 'I':
            return True
        else:
            return False

    # -- GENERATION OF possible STATES --
    number_of_immobile_patients = params['np2']
    possible_values = [i for i in range(0, number_of_immobile_patients + 1)] # Generate all values
    # iterations = list(itertools.product(possible_values, repeat=4))
    iterations = [(a, b, c, d) for a in possible_values for b in possible_values
                  for c in possible_values for d in possible_values]
    # Remove all values that are already not possible
    filtered = [i for i in iterations if sum(i) >= (number_of_immobile_patients-2) and sum(i) <= number_of_immobile_patients] 

    all_states = []
    # Add all nurse combinations to states
    nurse_states = ['I', 'B', 'R']
    for i in filtered: 
        for nurse_1 in nurse_states:
            for nurse_2 in nurse_states:
                new_i = list(i)
                new_i.insert(2, nurse_1) # Add to 2nd positon
                new_i.insert(5, nurse_2) # Add to 5th position
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
        if (not is_busy(state[2]) and is_busy(state[5])) or (is_busy(state[2]) and not is_busy(state[5])):
            if state_sum != number_of_immobile_patients - 1:
                continue

        # If both nurses are busy, there must be np-2 patients tracked
        if is_busy(state[2]) and is_busy(state[5]):
            if state_sum != number_of_immobile_patients - 2:
                continue

        # if both nurses are not busy, all 4 patients must be tracked
        if not is_busy(state[2]) and not is_busy(state[5]):
            if state_sum != number_of_immobile_patients:
                continue

        # If nurse 1 is idle, there cannot be a queue in front of the nurse 1
        if state[1] >= 1 and state[2] == 'I':
            continue

        # If nurse 2 is idle, there cannot be a queue in front of the nurse 2
        if state[4] >= 1 and state[5] == 'I':
            continue

        final_states.append(tuple(state))  # Transform back to tuple

    # print(final_states)
    # -- GENERATION of Matrix --
    numberOfStates = len(final_states) # Total number of states
    q_matrix = zeros((numberOfStates, numberOfStates))

    # We loop over the x-axis and find y-values for all x.
    for index, state in enumerate(final_states):
        state = list(state)
        x = index

        # -- Part 1: From private room -- #

        #  1. Patients enters the Queue of the Private Rooms
        if state[0] >= 1 and not is_idle(state[2]):
            # print('1')
            look_for = state.copy()
            look_for[0] = state[0] - 1
            look_for[1] = state[1] + 1
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['beta2'] * state[0]  # b2 * people in common

        # 2. Patient wants to enter Queue of Private Rooms, but Queue is empty (serve directly)
        if state[0] >= 1 and is_idle(state[2]):
            # print('2')
            look_for = state.copy()
            look_for[0] = state[0] - 1
            look_for[2] = 'B'
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['beta2'] * state[0]  # b2 * people in common

        # 3. Nurse 1 returns and there is still a queue to serve
        if state[1] >= 1 and state[2] == 'R':
            # print('3')
            look_for = state.copy()
            look_for[1] = state[1] - 1
            look_for[2] = 'B'
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['mu']  # mu

        # 4. Nurse 1 returns and there is no queue to serve
        if state[1] == 0 and state[2] == 'R':
            # print('4')
            look_for = state.copy()
            look_for[2] = 'I'
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['mu']  # mu

        # 5. Nurse 1 brings patient to common room
        if state[2] == 'B':
            # print('5')
            look_for = state.copy()
            look_for[2] = 'R'
            look_for[3] = state[3] + 1
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['mu']  # mu

        # -- Part 2: From common room -- #

        # 6. Patients enters the Queue of the Common Rooms
        if state[3] >= 1 and not is_idle(state[5]):
            # print('6')
            look_for = state.copy()
            look_for[3] = state[3] - 1
            look_for[4] = state[4] + 1
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['delta2'] * state[3]  # b2 * people in common

        # 7. Patient wants to enter Queue of Common Rooms, but Queue is empty (serve directly)
        if state[3] >= 1 and is_idle(state[5]):
            # print('7')
            look_for = state.copy()
            look_for[3] = state[3] - 1
            look_for[5] = 'B'
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['delta2'] * state[3]  # b2 * people in common

        # 8. Nurse 2 returns and there is still a queue to serve
        if state[4] >= 1 and state[5] == 'R':
            # print('8')
            look_for = state.copy()
            look_for[4] = state[4] - 1
            look_for[5] = 'B'
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['mu']  # mu

        # 9. Nurse 2 returns and there is no queue to serve
        if state[4] == 0 and state[5] == 'R':
            # print('9')
            look_for = state.copy()
            look_for[5] = 'I'
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['mu']  # mu

        # 10. Nurse 2 brings patient to private room
        if state[5] == 'B':
            # print('10')
            look_for = state.copy()
            look_for[5] = 'R'
            look_for[0] = state[0] + 1
            y = final_states.index(tuple(look_for))
            q_matrix[x, y] = params['mu']  # mu

    # Now set the diagonal axis of the matrix
    for i, row in enumerate(q_matrix):
        # print(i, row)
        q_matrix[i, i] = -sum(row)

    # print(final_states)
    # print(sorted(final_states, reverse=True))
    # for index, state in enumerate(final_states):
    #     print(index, state)
    # print(q_matrix.shape)
    # print(q_matrix)

    return q_matrix, final_states

# Calculation of all immobile patient stats
def immobile_patient_stats(stateProbs, final_states, number_of_patients):
    '''
    The simulation logic return state probabilities, with a normalized weight for each state. These are aggregated here
    with logic to calculate the standard deviation and average. The general base truth is that the queue1 is
    equivalent to the patient waiting in the private room, and queue2 is equivalent to the patients waiting in
    the common room. Calculation is quite similar to that of the mobile simulation. More information is present in
    the report.
    :param stateProbs:
    :param final_states:
    :param number_of_patients:
    :return:
    '''
    # Creating a dict that contains the probability for possible numbers of patients in each room.
    probabilities = dict()
    probabilities['common'] = [0] * (number_of_patients + 1)
    probabilities['private'] = [0] * (number_of_patients + 1)
    probabilities['queue1'] = [0] * (number_of_patients + 1)
    probabilities['queue2'] = [0] * (number_of_patients + 1)

    # Get all the possible probabilities
    for index, probability in enumerate(stateProbs):
        state = list(final_states[index])
        if state[2] == 'B':
            probabilities['private'][state[0] + 1] += probability
        else:
            probabilities['private'][state[0]] += probability
        probabilities['queue1'][state[1]] += probability
        if state[5] == 'B':
            probabilities['common'][state[3] + 1] += probability
        else:
            probabilities['common'][state[3]] += probability
        probabilities['queue2'][state[4]] += probability

    averages = dict()
    averages['common'] = 0
    averages['private'] = 0
    averages['queue1'] = 0
    averages['queue2'] = 0

    for index in range(number_of_patients + 1):
        averages['private'] += index * probabilities['private'][index]
        averages['common'] += index * probabilities['common'][index]
        averages['queue1'] += index * probabilities['queue1'][index]
        averages['queue2'] += index * probabilities['queue2'][index]

    # Creating a dict for the variances per room
    variances = dict()
    variances['common'] = 0
    variances['private'] = 0
    variances['queue1'] = 0
    variances['queue2'] = 0
    # We use here the weighted formula for variance. The weights are normalized, and hence the denominator is 1.
    # Thus, we only need a summation of (weight)*((value - expected_value(value))^2)
    for index in range(number_of_patients + 1):
        variances['private'] += probabilities['private'][index] * ((index - averages['private']) ** 2)
        variances['common'] += probabilities['common'][index] * ((index - averages['common']) ** 2)
        variances['queue1'] += probabilities['queue1'][index] * ((index - averages['queue1']) ** 2)
        variances['queue2'] += probabilities['queue2'][index] * ((index - averages['queue2']) ** 2)

    return averages, variances


# Testing function for individual trials

# if __name__ == '__main__':
#     params = get_params(1)
#     immobile_initial_state = (params['np2'], 0, 'I', 0, 0, 'I')
#     temp, temp2 = immobile_patient_simulation(params, immobile_initial_state)
#     print(temp)
#     print(temp2)