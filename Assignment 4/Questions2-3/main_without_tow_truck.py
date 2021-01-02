from main import run_simulation
from numpy import std, mean
from collections import Counter
import matplotlib.pyplot as plt
import logging
from util import ci, group_into_bins


def motivation_simulation_length():
    # 1. Simulating for identifying a final simulation time
    # Using number of runs = 5
    graph_type = 'Highway' # Toy1, Toy2, Highway
    # number_of_runs = 1
    number_of_runs = 5
    end_times = [i for i in range(100, 1600, 100)]
    # end_times = [100, 150, 200]
    # print(end_times)
    sim_time_stats = [[] for i in range(len(end_times))]
    for i, ival in enumerate(end_times):
        for j in range(number_of_runs):
            system = run_simulation(simulation_id=str(ival) + '-' + str(j), seed=20+i+j, end_time=ival, stats_step_size=50, graph_type=graph_type, tow_truck_mode=False, warm_up=100)
            # system = run_simulation(simulation_id=str(ival) + '-' + str(j), seed=20+i+j, end_time=ival, stats_step_size=50, graph_type=graph_type, tow_truck_mode=False)
            sim_time_stats[i].append(system.final_statistics)

    # keys = ['number_of_ghost_cars_at_time', 'number_of_route_cars_at_time', 'number_of_current_incidents', 'Average number of incidents']
    # keys = ['number_of_current_incidents', 'Average number of incidents']
    keys = ['average_number_of_incidents']

    for key in keys:
        plot = plt.figure()
        plt.ylabel(key)
        plt.xlabel('Simulation Time')
        # i = 0
        for idx, end_time in enumerate(end_times):
            for sim_time_stat in sim_time_stats[idx]:
                # i+=1
                plt.plot(end_time, sim_time_stat[key], 'bo')

        print(i)
        # left, right = plt.xlim()
        # plt.xlim(100, right)
        bottom, top = plt.ylim()
        plt.ylim(0, top)
        plt.show()


def motivation_number_runs():
    # 2. Simulating with identified simulation length, getting a reasonable number of runs.
    # Using simulation_length = 1500, and discarding the first 100 items as the system takes this time to warm-up
    run_sizes = [i for i in range(1, 50)]
    graph_type = 'Highway'
    run_size_stats = [[] for i in range(len(run_sizes))]
    trial_per_run_size = 5
    # sim_time_stats.append[]
    # for run_size in run_sizes:
    for index, run_size in enumerate(run_sizes):
        for trial in range(trial_per_run_size):
            values = []
            for run in range(run_size):
                system = run_simulation('Run-' + str(run_size) + '-' + str(trial), seed=run_size+run+trial, end_time=1600, stats_step_size=50, graph_type=graph_type, tow_truck_mode=False, warm_up=100)
                values.append(system.final_statistics['average_number_of_incidents'])
            run_size_stats[index].append(mean(values))

    key = 'average_number_of_incidents'

    plot = plt.figure()
    plt.ylabel('Average number of Incidents')
    plt.xlabel('Run Size')
    for idx, run_size in enumerate(run_sizes):
        for value in run_size_stats[idx]:
            print('Run_size', run_size)
            print(value)
            plt.plot([run_size], value, 'bo')
    plt.show()

def perf_measure_1():
    # 1. For individual vehicles: distribution of the travel time (mean, standard deviation, plot
    # a histogram). Indicate which part of the travel time is caused by the delay. Present
    # results on the number of incidents they encounter on average (again: mean, standard
    # deviation, distribution).

    # Travel time on the route between A to B
    # Probability of minutes of time taken for the travel along the route. Ghost cars not necessary, or included.
    graph_type = 'Highway'
    system = run_simulation('Measure-1', seed=30, end_time=1600, stats_step_size=50, graph_type=graph_type, tow_truck_mode=False, warm_up=100)
    travel_times_list = system.final_statistics['route_travel_times']
    delay_times_list = system.final_statistics['route_delay_times']
    number_delays_list = system.final_statistics['route_number_delays']
    print('Travel Times List for Route Cars')
    print(travel_times_list)
    print(len(travel_times_list))

    # Graph 1
    rounded_travel_times_list = [round(i) for i in travel_times_list]
    max_travel_time = max(rounded_travel_times_list)
    counts_travel_times = Counter(rounded_travel_times_list)
    list_of_times = []
    print('Rounded Travel Times List', rounded_travel_times_list)
    for i in range(int(max_travel_time) + 1):
        list_of_times.append(counts_travel_times[i])
    print(list_of_times) # Must be X-axis
    print('Count of travel times -', list_of_times)
    plot = plt.figure()
    plt.ylabel('Probability')
    plt.xlabel('Total Travel Time')
    plt.xlim(50, max_travel_time)
    plt.plot([i for i in range(len(list_of_times))], [j/sum(list_of_times) for j in list_of_times])
    plt.show()

    # Graph 2
    rounded_delay_times_list = [round(i) for i in delay_times_list]
    max_delay_time = max(rounded_delay_times_list)
    counts_delay_times = Counter(rounded_delay_times_list)
    list_of_delay_times = []
    print('Rounded Delay Times List', rounded_delay_times_list)
    for i in range(1, int(max_delay_time) + 1):
        list_of_delay_times.append(counts_delay_times[i])
    print(list_of_delay_times) # Must be X-axis
    print('Count of delay times -', list_of_delay_times)
    plot = plt.figure()
    plt.ylabel('Probability')
    plt.xlabel('Total Delay Time')
    plt.xlim(1, max_delay_time)
    plt.plot([i for i in range(len(list_of_delay_times))], [j/sum(list_of_delay_times) for j in list_of_delay_times])
    plt.show()

    # Graph 3
    # Showing the distribution of the number of incidents in a single route travel
    print(number_delays_list)
    counts_number_delays = Counter(number_delays_list)
    list_of_number_delays = []
    for i in range(max(number_delays_list) + 1):
        list_of_number_delays.append(counts_number_delays[i])
    print('Counts of number of delays', list_of_number_delays)
    plot = plt.figure()
    plt.xlabel('Numbers of incidents')
    plt.ylabel('Probability')
    # plt.xlim(1, max_delay_time)
    plt.bar([i for i in range(len(list_of_number_delays))], [j / sum(list_of_number_delays) for j in list_of_number_delays])
    plt.show()

    # CI calculation
    travel_times_list = []
    delay_times_list = []
    number_delays_list = []
    for i in range(run_size):
        system = run_simulation('Measure-1', seed=None, end_time=1600, stats_step_size=50, graph_type=graph_type,
                                tow_truck_mode=False, warm_up=100)
        travel_times_list += system.final_statistics['route_travel_times']
        delay_times_list += system.final_statistics['route_delay_times']
        number_delays_list += system.final_statistics['route_number_delays']
    print('\n')
    print('Number of Route Travel Times - ', len(travel_times_list))
    mean_route_travel_time = sum(travel_times_list) / len(travel_times_list)
    std_route_travel_time = std(travel_times_list)
    print('Mean of Route Travel Time -', mean_route_travel_time)
    print('Standard Deviation of Route Travel Time -', std_route_travel_time)
    halfwidth_route_travel_time = ci(std_route_travel_time, run_size)
    print('Halfwidth of Route Travel Time -', halfwidth_route_travel_time)
    print('Range - ', mean_route_travel_time - halfwidth_route_travel_time, mean_route_travel_time + halfwidth_route_travel_time)
    # Also do CI calculation
    print('\n')
    print('Number of Delay Travel Times - ', len(delay_times_list))
    mean_delay_time = sum(delay_times_list) / len(delay_times_list)
    std_delay_time = std(delay_times_list)
    print('Mean of Delay Travel Time -', mean_delay_time)
    print('Standard Deviation of Delay Travel Time -', std_delay_time)
    halfwidth_delay_time = ci(std_delay_time, run_size)
    print('Halfwidth of Delay Travel Time -', halfwidth_delay_time)
    print('Range - ', mean_delay_time - halfwidth_delay_time, mean_delay_time + halfwidth_delay_time)
    print('\n')
    print('Number of Delays - ', len(number_delays_list))
    mean_delay_number = sum(number_delays_list) / len(number_delays_list)
    std_delay_number = std(number_delays_list)
    print('Mean of Delay Travel Time -', mean_delay_number)
    print('Standard Deviation of Delay Travel Time -', std_delay_number)
    halfwidth_delay_number = ci(std_delay_number, run_size)
    print('Halfwidth of Delay Travel Time -', halfwidth_delay_number)
    print('Range - ', mean_delay_number - halfwidth_delay_number, mean_delay_number + halfwidth_delay_number)




def perf_measure_2():

    # 2. For the network: distribution of the number of delayed vehicles at any arbitrary epoch.
    # Formulated differently, we would like to see a table where you simulate for k = 0; 1; 2; : : :
    # the fraction of time that exactly k vehicles are being delayed (consider it as being stuck
    # in a traffic jam).
    # Note that, in order to determine the second performance measure (number of
    # delayed vehicles in the network), it actually matters how many vehicles are driving in the
    # whole network. So now you need to add random vehicles in the network that drive between
    # the highway junctions. This part does not have to be implemented very realistically. You
    # may even assume that vehicles enter the network randomly at each of the nodes, travel one
    # link, and then leave the network again. For these vehicles, no origin-destination routing is
    # required. Only vehicles travelling from A to B have a fixed route. Our advice is to keep
    # it simple: do not introduce too many model parameters, like number of vehicles per hour
    # travelling on each link. You are allowed to assume that this rate is equal for all links.

    graph_type = 'Highway'
    system = run_simulation('Measure-2-vis', seed=40, end_time=1600, stats_step_size=50, graph_type=graph_type, tow_truck_mode=False, warm_up=100)
    times_delayed_per_number_of_cars = system.final_statistics['time_spent_delayed_per_current_number_of_all_cars']
    # print('Time spent per number of delayed cars', times_delayed_per_number_of_cars)
    print('len', len(times_delayed_per_number_of_cars))

    data = [(i, times_delayed_per_number_of_cars[i]) for i in range(len(times_delayed_per_number_of_cars))]
    x, y, bin_width = group_into_bins(data)
    print('x', x)
    print('y', y)
    print('len(y)', len(y))
    min_non_zero_delayed_cars = 0
    max_non_zero_delayed_cars = len(y) - 1
    # comparison = 0
    i = 0
    while i < len(y) and y[i] == 0:
        min_non_zero_delayed_cars += 1
        i += 1
        # i = x[i+1]
    i = len(y) - 1
    while i > 0 and y[i] == 0:
        max_non_zero_delayed_cars -= 1
        i -= 1
    print('max_non_zero_delayed_cars', max_non_zero_delayed_cars)
    print('min_non_zero_delayed_cars', min_non_zero_delayed_cars)

    plt.xlabel('Numbers of delayed cars (with Tow Trucks)')
    plt.ylabel('Fraction of time spent')
    plt.xlim(x[min_non_zero_delayed_cars] - 1, x[max_non_zero_delayed_cars])
    plt.bar(x, [j / sum(y) for j in y], width=bin_width * 0.8)
    plt.show()

    average_number_of_delayed_cars = []
    # CI calculation
    for i in range(run_size):
        system = run_simulation('Measure-2' + str(i), seed=i, end_time=1600, stats_step_size=50, graph_type=graph_type,
                                tow_truck_mode=False, warm_up=100)
        print('Run -', i)
        average_number_of_delayed_cars.append(system.final_statistics['average_time_of_delay_of_all_cars'])

    mean_number_of_delayed_cars = sum(average_number_of_delayed_cars) / len(average_number_of_delayed_cars)
    std_number_of_delayed_cars = std(average_number_of_delayed_cars)
    print('Mean of Delayed Cars -', mean_number_of_delayed_cars)
    print('Standard Deviation of Delayed Cars -', std_number_of_delayed_cars)
    halfwidth_number_of_delayed_cars = ci(std_number_of_delayed_cars, run_size)
    print('Halfwidth of Delayed Cars -', halfwidth_number_of_delayed_cars)
    print('Range - ', mean_number_of_delayed_cars - halfwidth_number_of_delayed_cars,
          mean_number_of_delayed_cars + halfwidth_number_of_delayed_cars)


def perf_measure_3():

    # For incidents: distribution of the number of incidents in the whole network, at any
    # arbitrary epoch. This is similar to the previous question, but now for the fraction of time
    # that exactly k incidents are taking place simultaneously in the network

    graph_type = 'Highway'
    system = run_simulation('Measure-3-vis', seed=40, end_time=1600, stats_step_size=50, graph_type=graph_type,
                            tow_truck_mode=False, warm_up=100)
    times_fraction_per_number_of_incidents = system.final_statistics['time_spent_per_current_number_of_incidents']
    # rounded_times = [round(i) for i in times_fraction_per_number_of_incidents]
    # print(rounded_times)
    # counts_number_delays = Counter(number_delays_list)
    # list_of_number_delays = []
    # for i in range(max(number_delays_list) + 1):
    #     list_of_number_delays.append(counts_number_delays[i])
    print('Counts of time spent per number of incidents', times_fraction_per_number_of_incidents)
    print('len', len(times_fraction_per_number_of_incidents))
    min_non_zero_incidents = 0
    max_non_zero_incidents = len(times_fraction_per_number_of_incidents)
    i = 0
    while i < len(times_fraction_per_number_of_incidents) and times_fraction_per_number_of_incidents[i] == 0:
        min_non_zero_incidents += 1
        i += 1
    i = len(times_fraction_per_number_of_incidents) - 1
    while i > 0 and times_fraction_per_number_of_incidents[i] == 0:
        max_non_zero_incidents -= 1
        i -= 1
    print('max_non_zero_incidents', max_non_zero_incidents)
    print('min_non_zero_incidents', min_non_zero_incidents)

    plot = plt.figure()
    plt.xlabel('Numbers of incidents')
    plt.ylabel('Fraction of time spent')
    plt.xlim(min_non_zero_incidents - 1, max_non_zero_incidents)
    plt.bar([i for i in range(len(times_fraction_per_number_of_incidents))], [j / sum(times_fraction_per_number_of_incidents) for j in times_fraction_per_number_of_incidents])
    plt.show()

    average_number_of_incidents = []
    # CI calculation
    for i in range(run_size):
        system = run_simulation('Measure-3' + str(i), seed=i, end_time=1600, stats_step_size=50, graph_type=graph_type,
                                tow_truck_mode=False, warm_up=100)
        print('Run -', i)
        average_number_of_incidents.append(system.final_statistics['average_number_of_incidents'])

    mean_number_of_incidents = sum(average_number_of_incidents) / len(average_number_of_incidents)
    std_number_of_incidents = std(average_number_of_incidents)
    print('Mean of Number of Incidents -', mean_number_of_incidents)
    print('Standard Deviation of Number of Incidents -', std_number_of_incidents)
    halfwidth_number_of_incidents = ci(std_number_of_incidents, run_size)
    print('Halfwidth of Number of Incidents -', halfwidth_number_of_incidents)
    print('Range - ', mean_number_of_incidents - halfwidth_number_of_incidents, mean_number_of_incidents + halfwidth_number_of_incidents)


if __name__ == '__main__':
    logging.basicConfig(filename='highway-measure2-Final-1-10.log', level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')
    run_size = 20
    # run_size = 5
    # motivation_simulation_length()
    # motivation_number_runs()
    # perf_measure_1()
    perf_measure_2()
    # perf_measure_3()