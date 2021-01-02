from numpy import zeros
from util import simulation, get_params


def mobile_patient_simulation(params, initial_state):
    '''
    Gateway to initialize entire simulation. Actual simulation logic is in the util file. This file
    contains generator matrix creation as well as aggregated statistics calculation.
    It receives the parameters for the simulation as well as the initial state.
    :param params:
    :param initial_state:
    :return:
    '''
    q_matrix, filtered_states = mobile_q_matrix_generation(params)
    initial_state_index = filtered_states.index(initial_state)
    state_probabilities = simulation(q_matrix, initial_state_index, params['T'])
    average_per_room = mobile_patient_stats(state_probabilities, filtered_states, params['np1'])
    return average_per_room


def mobile_q_matrix_generation(params):
    '''
    Receives parameters, identifies all possible n states in the system, then creates an n*n generator matrix containing
    the transition rates. These rates are described in the report.
    :param params:
    :return:
    '''
    number_of_mobile_patients = params['np1']

    # Generating all possible states, by filtering out all states that don't add up to the number of mobile patients.
    possible_values = [i for i in range(0, number_of_mobile_patients + 1)]
    iterations = [(a, b, c) for a in possible_values for b in possible_values for c in possible_values]
    filtered_states = [i for i in iterations if sum(i) == number_of_mobile_patients]
    filtered_states = sorted(filtered_states, reverse=True)

    # Generator matrix is created by setting values according to the types of transitions possible in the system.
    numberOfStates = len(filtered_states)
    q_matrix = zeros((numberOfStates, numberOfStates))
    for index, state in enumerate(filtered_states):
        i = index
        # 4 types of transitions are possible (described in the report), and they are as follows.
        possible_transitions = [(state[0] - 1, state[1] + 1, state[2]), # Type 0 - Person moving from Private room to Common room
                                (state[0] - 1, state[1], state[2] + 1), # Type 1 - Person moving from Private room to Gym
                                (state[0] + 1, state[1] - 1, state[2]), # Type 2 - Person moving from Common to Private room
                                (state[0] + 1, state[1], state[2] - 1)] # Type 3 - Person moving from Gym to Private room
        for type_trans, transition_candidate in enumerate(possible_transitions):
            try:
                j = filtered_states.index(transition_candidate)
                if type_trans == 0:
                    q_matrix[i, j] = state[0]*params['p']*params['beta1']
                elif type_trans == 1:
                    q_matrix[i, j] = state[0] * (1 - params['p']) * params['beta1']
                elif type_trans == 2:
                    q_matrix[i, j] = state[1] * params['delta1']
                elif type_trans == 3:
                    q_matrix[i, j] = state[2] * params['tau']
            except:
                # If a state is unreachable, then exceptions are filtered out (for example, negative number of patients)
                pass

    # Setting diagonal values according to Markov chain logic.
    for i, row in enumerate(q_matrix):
        q_matrix[i, i] = -sum(row)

    return q_matrix, filtered_states
    
    
def mobile_patient_stats(state_probabilities, filtered_states, number_of_patients):
    '''
    The simulation logic return state probabilities, with a normalized weight for each state. These are aggregated here
    with logic to calculate the standard deviation and average.
    :param state_probabilities:
    :param filtered_states:
    :param number_of_patients:
    :return:
    '''
    # Creating a dict that contains the probability for possible numbers of patients in each room.
    probabilities = dict()
    probabilities['common'] = [0] * (number_of_patients + 1)
    probabilities['gym'] = [0] * (number_of_patients + 1)
    probabilities['private'] = [0] * (number_of_patients + 1)
    # Indices represent numbers of patients, so the calculation is easy.
    for index, probability in enumerate(state_probabilities):
        state = list(filtered_states[index])
        probabilities['private'][state[0]] += probability
        probabilities['common'][state[1]] += probability
        probabilities['gym'][state[2]] += probability
    # Average calculation is then a simple process.
    averages = dict()
    averages['common'] = 0
    averages['gym'] = 0
    averages['private'] = 0

    for index in range(number_of_patients + 1):
        averages['private'] += index * probabilities['private'][index]
        averages['common'] += index * probabilities['common'][index]
        averages['gym'] += index * probabilities['gym'][index]

    # Creating a dict for the variances
    variances = dict()
    variances['common'] = 0
    variances['gym'] = 0
    variances['private'] = 0

    # We use here the weighted formula for variance. The weights are normalized, and hence the denominator is 1.
    # Thus, we only need a summation of (weight)*((value - expected_value(value))^2)
    for index in range(number_of_patients + 1):
        variances['private'] += probabilities['private'][index] * ((index - averages['private']) ** 2)
        variances['common'] += probabilities['common'][index] * ((index - averages['common']) ** 2)
        variances['gym'] += probabilities['gym'][index] * ((index - averages['gym']) ** 2)

    return averages, variances


# Testing function for individual trials

# if __name__ == '__main__':
#     params = get_params(1)
#     mobile_initial_state = (params['np1'], 0, 0)
#     temp, temp2 = mobile_patient_simulation(params, mobile_initial_state)
#     print(temp)
#     print(temp2)
