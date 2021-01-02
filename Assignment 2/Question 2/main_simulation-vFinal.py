from numpy import std, var
from mobilepatient import mobile_patient_simulation
from immobilepatient import immobile_patient_simulation
from util import get_params

if __name__ == '__main__':
    '''
    Starting point of the entire Markov Chain simulation for both mobile and immobile patients..
    '''
    # Obtain parameters from one of the sets from the assignment.
    # The complete set of parameters is described in the util file.
    params = get_params(3)

    # Initializing lists for storing values from the simulations.
    # Each simulation returns a mean value as well as a variance value for each room (and queue).
    mobile_values_common = []
    mobile_values_private = []
    mobile_values_gym = []
    immobile_values_private = []
    immobile_values_common = []
    immobile_values_queue1 = []
    immobile_values_queue2 = []

    mobile_var_values_common = []
    mobile_var_values_private = []
    mobile_var_values_gym = []
    immobile_var_values_private = []
    immobile_var_values_common = []
    immobile_var_values_queue1 = []
    immobile_var_values_queue2 = []


    # The initial values are set for each simulation.
    # State for the mobile simulation is a tuple in the form ('private', 'common', 'gym')
    # State for the immobile simulation is a tuple in the form ('private', 'queue1', 'nurse1 status',
    # 'common', 'queue2', 'nurse2 status')
    # Each of those labels represents the number of patients in the room, or queue. In the case of nurse status, it
    # can take one of 3 values - 'B' (Busy), 'I' (Idle), 'R' (Return)

    # -----------------
    # IMPORTANT
    # -----------------
    # Queue1 represents the queue from the Private to the Common room.
    # Nurse1 represents the nurse dedicated to serving this queue.
    # Similarly, Queue2 represents the queue in the opposite direction, and Nurse 2 is the nurse
    # dedicated towards clearing that line.

    # The initial state has all the patients in their private rooms, and both nurses being idle. This can be modified.

    mobile_initial_state = (params['np1'], 0, 0)
    immobile_initial_state = (params['np2'], 0, 'I', 0, 0, 'I')

    # The loop performs the same simulation for a certain number of runs determined by the params['trials'] value
    # defined in the parameters in the util file
    for trial in range(params['trials']):
        # Checkpointing every 5th trial in order to show progress.
        if trial % 5 == 0:
            print('At trial', trial)

        # Mobile patient simulation invokes the gateway method from the mobilepatient.py file.
        # Each time that it is called, it returns 2 dict objects, one containing the average values per room for
        # the trial, and the other one containing the variances. These are appended to the list objects defined above.
        trial_mobile_averages, trial_mobile_var_deviations = mobile_patient_simulation(params, mobile_initial_state)
        mobile_values_common.append(trial_mobile_averages['common'])
        mobile_values_private.append(trial_mobile_averages['private'])
        mobile_values_gym.append(trial_mobile_averages['gym'])

        mobile_var_values_common.append(trial_mobile_var_deviations['common'])
        mobile_var_values_private.append(trial_mobile_var_deviations['private'])
        mobile_var_values_gym.append(trial_mobile_var_deviations['gym'])


        # Similarly, the immobile patient simulation invokes the gateway method from the immobilepatient.py file.
        # Return values are identical, but they return the mean and average values for queue1 and queue2 instead
        # of the gym.
        trial_immobile_averages, trial_immobile_var_deviations = immobile_patient_simulation(params, immobile_initial_state)
        immobile_values_common.append(trial_immobile_averages['common'])
        immobile_values_private.append(trial_immobile_averages['private'])
        immobile_values_queue1.append(trial_immobile_averages['queue1'])
        immobile_values_queue2.append(trial_immobile_averages['queue2'])

        immobile_var_values_common.append(trial_immobile_var_deviations['common'])
        immobile_var_values_private.append(trial_immobile_var_deviations['private'])
        immobile_var_values_queue1.append(trial_immobile_var_deviations['queue1'])
        immobile_var_values_queue2.append(trial_immobile_var_deviations['queue2'])


    # Once the trials are over, we begin aggregating the statistics for the overall simulation process.
    # Mean calculation is done below.
    mobile_avg_common = sum(mobile_values_common) / len(mobile_values_common)
    mobile_avg_private = sum(mobile_values_private) / len(mobile_values_private)
    mobile_avg_gym = sum(mobile_values_gym) / len(mobile_values_gym)

    immobile_avg_private = sum(immobile_values_private) / len(immobile_values_private)
    immobile_avg_common = sum(immobile_values_common) / len(immobile_values_common)
    immobile_avg_queue1 = sum(immobile_values_queue1) / len(immobile_values_queue1)
    immobile_avg_queue2 = sum(immobile_values_queue2) / len(immobile_values_queue2)

    immobile_avg_private_combined = immobile_avg_private + immobile_avg_queue1
    immobile_avg_common_combined = immobile_avg_common + immobile_avg_queue2

    # We combine the statistics for all rooms for both patient types in the following way.
    # Patients who are in the queue are still technically in their rooms until they are served.
    total_avg_private = mobile_avg_private + immobile_avg_private + immobile_avg_queue1
    total_avg_common = mobile_avg_common + immobile_avg_common + immobile_avg_queue2

    # We take the average of the variances and take the square root to obtain the standard
    # deviations per room (or queue)
    mobile_std_common = (sum(mobile_var_values_common) / len(mobile_var_values_common)) ** 0.5
    mobile_std_private = (sum(mobile_var_values_private) / len(mobile_var_values_private)) ** 0.5
    mobile_std_gym = (sum(mobile_var_values_gym) / len(mobile_var_values_gym)) ** 0.5

    immobile_std_common = (sum(immobile_var_values_common) / len(immobile_var_values_common)) ** 0.5
    immobile_std_private = (sum(immobile_var_values_private) / len(immobile_var_values_private)) ** 0.5
    immobile_std_queue1 = (sum(immobile_var_values_queue1) / len(immobile_var_values_queue1)) ** 0.5
    immobile_std_queue2 = (sum(immobile_var_values_queue2) / len(immobile_var_values_queue2)) ** 0.5

    immobile_std_common_combined = ((immobile_std_common**2) + (immobile_std_queue2 **2)) ** 0.5
    immobile_std_private_combined = ((immobile_std_private ** 2) + (immobile_std_queue1 ** 2)) ** 0.5

    # The total standard deviation is similar. We sum variances, divide by the number of trials and take the root.
    total_std_common = ((sum(mobile_var_values_common) + sum(immobile_var_values_common) +
                         sum(immobile_var_values_queue2))/params['trials']) ** 0.5
    total_std_private = ((sum(mobile_var_values_private) + sum(immobile_var_values_private) +
                          sum(immobile_var_values_queue1)) / params['trials']) ** 0.5

    # The confidence intervals are for the mean values, and thus, we first find the standard deviations
    # of the mean values for all the rooms (and queues) for each patient type.
    ci_mobile_std_common = std(mobile_values_common)
    ci_mobile_std_private = std(mobile_values_private)
    ci_mobile_std_gym = std(mobile_values_gym)

    # ci_immobile_std_private = std(immobile_values_private)
    # ci_immobile_std_common = std(immobile_values_common)
    ci_immobile_std_private = (var(immobile_values_private) + var(immobile_values_queue1)) ** 0.5
    ci_immobile_std_common = (var(immobile_values_common) + var(immobile_values_queue2)) ** 0.5
    ci_immobile_std_queue1 = std(immobile_values_queue1)
    ci_immobile_std_queue2 = std(immobile_values_queue2)

    # The total variance is obtained by summing the variances, since the distributions are independent.
    ci_total_std_private = (var(mobile_values_private) + var(immobile_values_private) + var(immobile_values_queue2)) ** 0.5
    ci_total_std_common = (var(mobile_values_common) + var(immobile_values_common) + var(immobile_values_queue2)) ** 0.5
    ci_total_std_gym = ci_mobile_std_gym

    # A 96% confidence interval is obtained thus through the usual method by first finding half-widths.
    mobile_halfwidth_common = 1.96 * ci_mobile_std_common / (params['trials'] ** 0.5)
    mobile_halfwidth_private = 1.96 * ci_mobile_std_private / (params['trials'] ** 0.5)
    mobile_halfwidth_gym = 1.96 * ci_mobile_std_gym / (params['trials'] ** 0.5)

    immobile_halfwidth_common = 1.96 * ci_immobile_std_common / (params['trials'] ** 0.5)
    immobile_halfwidth_private = 1.96 * ci_immobile_std_private / (params['trials'] ** 0.5)
    immobile_halfwidth_queue1 = 1.96 * ci_immobile_std_queue1 / (params['trials'] ** 0.5)
    immobile_halfwidth_queue2 = 1.96 * ci_immobile_std_queue2 / (params['trials'] ** 0.5)

    total_halfwidth_common = 1.96 * ci_total_std_common / (params['trials'] ** 0.5)
    total_halfwidth_private = 1.96 * ci_total_std_private / (params['trials'] ** 0.5)

    # We then determine the ranges.
    mobile_ci_common = (mobile_avg_common - mobile_halfwidth_common, mobile_avg_common + mobile_halfwidth_common)
    mobile_ci_private = (mobile_avg_private - mobile_halfwidth_private, mobile_avg_private + mobile_halfwidth_private)
    mobile_ci_gym = (mobile_avg_gym - mobile_halfwidth_gym, mobile_avg_gym + mobile_halfwidth_gym)

    immobile_ci_common = (immobile_avg_common_combined - immobile_halfwidth_common, immobile_avg_common_combined + immobile_halfwidth_common)
    immobile_ci_private = (immobile_avg_private_combined - immobile_halfwidth_private, immobile_avg_private_combined + immobile_halfwidth_private)
    immobile_ci_queue1 = (immobile_avg_queue1 - immobile_halfwidth_queue1, immobile_avg_queue1 + immobile_halfwidth_queue1)
    immobile_ci_queue2 = (immobile_avg_queue2 - immobile_halfwidth_queue2, immobile_avg_queue2 + immobile_halfwidth_queue2)

    total_ci_common = (total_avg_common - total_halfwidth_common, total_avg_common + total_halfwidth_common)
    total_ci_private = (total_avg_private - total_halfwidth_private, total_avg_private + total_halfwidth_private)

    # Finally the results are printed.
    print('Average Statistics')
    print('=======')
    print('Mobile Patient Stats')
    print('-------')
    print('Average Private Room duration - ', mobile_avg_private)
    print('Average Common Room duration - ', mobile_avg_common)
    print('Average Gym duration - ', mobile_avg_gym)

    print('')
    print('Immobile Patient Stats')
    print('-------')
    print('Average Private Room duration - ', immobile_avg_private)
    print('Average Common Room duration - ', immobile_avg_common)
    print('Average Private->Common Queue duration - ', immobile_avg_queue1)
    print('Average Common->Private Queue duration - ', immobile_avg_queue2)
    print('Average Private Room duration combined - ', immobile_avg_private_combined)
    print('Average Common Room duration combined - ', immobile_avg_common_combined)

    print('')
    print('Total Patient Stats')
    print('-------')
    print('Average Common Room duration - ', total_avg_common)
    print('Average Private Room duration - ', total_avg_private)
    print('Average Gym duration - ', mobile_avg_gym)

    print('=======')
    print('Standard Deviation Statistics')
    print('=======')
    print('Mobile Patient Stats')
    print('-------')
    print('Standard Deviation of Private Room duration - ', mobile_std_private)
    print('Standard Deviation of Common Room duration - ', mobile_std_common)
    print('Standard Deviation of Gym duration - ', mobile_std_gym)
    print('Confidence Interval of Private Room duration - ', mobile_ci_private)
    print('Confidence Interval of Common Room duration - ', mobile_ci_common)
    print('Confidence Interval of Gym duration - ', mobile_ci_gym)

    print('')
    print('Immobile Patient Stats')
    print('-------')
    print('Standard Deviation of Private Room duration - ', immobile_std_private)
    print('Standard Deviation of Common Room duration - ', immobile_std_common)
    print('Standard Deviation of Private->Common Queue duration - ', immobile_std_queue1)
    print('Standard Deviation of Common->Private Queue duration - ', immobile_std_queue2)
    print('Standard Deviation of Private Room duration overall - ', immobile_std_private_combined)
    print('Standard Deviation of Common Room duration overall - ', immobile_std_common_combined)
    print('Confidence Interval of Private Room duration - ', immobile_ci_private)
    print('Confidence Interval of Common Room duration - ', immobile_ci_common)
    print('Confidence Interval of Private->Common Queue duration - ', immobile_ci_queue1)
    print('Confidence Interval of Common->Private Queue duration - ', immobile_ci_queue2)

    print('')
    print('Total Patient Stats')
    print('-------')
    print('Standard Deviation of Private Room duration - ', total_std_private)
    print('Standard Deviation of Common Room duration - ', total_std_common)
    print('Standard Deviation of Gym duration - ', mobile_std_gym)
    print('Confidence Interval of Private Room duration - ', total_ci_private)
    print('Confidence Interval of Common Room duration - ', total_ci_common)
    print('Confidence Interval of Gym duration - ', mobile_ci_gym)

    # For convenience of verification and conformity, the results are represented in the format
    # of the output from question 1.
    print('')
    print('Using formatting of Question 1')
    print('-------')

    print('E[Nc]: \t ' + str(total_avg_common) + '\n' +
          'Std[Nc]: ' + str(total_std_common) + '\n' +
          'E[Np]: \t ' + str(total_avg_private) + '\n' +
          'Std[Np]: ' + str(total_std_private) + '\n' +
          'E[Nw]: \t ' + str(mobile_avg_gym) + '\n' +
          'Std[Nw]: ' + str(mobile_std_gym) + '\n')

    print('CI E[Nc]: \t ' + str(total_ci_common) + '\n' +
          'CI E[Np]: \t ' + str(total_ci_private) + '\n' +
          'CI E[Nw]: \t ' + str(mobile_ci_gym) + '\n')