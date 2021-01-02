from numpy import zeros
import random


def get_params(set_number):
    '''
    Given a set number, we return the corresponding parameters in a dict from the question.
    np1 - Number of mobile patients
    np2 - Number of immobile patients
    p - Probability of mobile patient moving to common room
    beta1 - Average time spent by mobile patient in private room
    beta2- Average time spent by immobile patient in private room
    delta1 - Average time spent by mobile patient in common room
    delta2 - Average time spent by immobile patient in common room
    tau - Average time spent by mobile patient in gym
    mu - Average time taken by nurse to make a trip in one direction
    trials - Number of runs made to get a consistent value.
    T - Maximum time limit of events taking place signaling end of simulation.
    :param set_number:
    :return:
    '''
    params = dict()
    params['trials'] = 100
    params['T'] = 10000
    if set_number == 1:
        params['np1'] = 4
        params['np2'] = 2
        params['p'] = 2 / 3
        params['beta1'] = 1 / 2
        params['beta2'] = 1 / 4
        params['delta1'] = 1 / 2
        params['delta2'] = 1 / 4
        params['tau'] = 1 / 1
        params['mu'] = 2

        return params
    elif set_number == 2:
        params['np1'] = 6
        params['np2'] = 1
        params['p'] = 1 / 2
        params['beta1'] = 1 / 1
        params['beta2'] = 1 / 3
        params['delta1'] = 1 / 2
        params['delta2'] = 1 / 6
        params['tau'] = 1 / 1
        params['mu'] = 2

        return params
    elif set_number == 3:
        params['np1'] = 2
        params['np2'] = 4
        params['p'] = 1 / 3
        params['beta1'] = 1 / 1
        params['beta2'] = 1 / 3
        params['delta1'] = 1 / 2
        params['delta2'] = 1 / 4
        params['tau'] = 1 / 2
        params['mu'] = 3

        return params


def simulation(q_matrix, initial_state, T):
    '''
    A Markov chain simulation is done given a generator matrix, an initial state to begin with, and a time limit.
    The generator matrix (transition rate matrix contains every possible state transition in an n*n form.
    A random distribution is used to make choices based on probabilities of possible transitions, and
    the time taken for the chosen transition is calculated using the random.expovariate function.
    :param q_matrix:
    :param initial_state:
    :param T:
    :return:
    '''

    # The initial number of states in the generator matrix are identified, and a placeholder is generated to
    # store the probabilities of being in those states.
    numberOfStates = q_matrix.shape[0]
    stateProbs = zeros(numberOfStates)

    t = 0  # current time
    state = initial_state  # current state

    p_matrix = q_matrix.copy() # We create the transition probability matrix
    for i in range(numberOfStates): # by copying Q and setting diagonal
        p_matrix[i, :] = - p_matrix[i, :] / p_matrix[i, i] # elements to zero .
        p_matrix[i, i] = 0

    # start_time = time.process_time()
    number_of_events = 0
    # Until time taken does not exceed T
    while t < T:
        dt = random.expovariate(-q_matrix[state, state])  # time till next event
        t += dt
        # Appending time taken for the transition that has happened.
        stateProbs[state] += dt
        number_of_events += 1
        # Choosing the next state through a random choice in the transition probability matrix.
        state = random.choices(range(numberOfStates), weights=p_matrix[state], k=1)[0]
    # print('Number of events -', number_of_events)
    # print('Time taken -', time.process_time() - start_time)

    stateProbs = stateProbs / t
    # Dividing the total time taken by each of the states by the entire time gives us the probability of the state.

    return stateProbs