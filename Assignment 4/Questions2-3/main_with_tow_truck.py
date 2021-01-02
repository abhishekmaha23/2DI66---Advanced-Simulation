from main import run_simulation
from numpy import std, mean
from collections import Counter
import matplotlib.pyplot as plt
import logging
# from util import ci, group_into_bins
import util

def motivation_simulation_length():
    # 1. Simulating for identifying a final simulation time
    # Using number of runs = 5
    graph_type = 'Highway' # Toy1, Toy2, Highway
    # number_of_runs = 1
    number_of_runs = 5
    end_times = [i for i in range(51, 1600, 100)]
    # end_times = [150, 300, 450]
    # print(end_times)
    sim_time_stats = [[] for i in range(len(end_times))]
    for i, ival in enumerate(end_times):
        for j in range(number_of_runs):
            system = run_simulation(simulation_id=str(ival) + '-' + str(j), seed=None, end_time=ival, stats_step_size=50, graph_type=graph_type, tow_truck_mode=True, warm_up=100)
            sim_time_stats[i].append((system.time_statistics['time'], system.final_statistics))

    # keys = ['number_of_ghost_cars_at_time', 'number_of_route_cars_at_time', 'number_of_current_incidents', 'Average number of incidents']
    # keys = ['number_of_current_incidents', 'Average number of incidents']
    keys = ['average_number_of_incidents']
    #
    for key in keys:
        plot = plt.figure()
        plt.ylabel(key)
        plt.xlabel('Simulation Time')
        for idx, end_time in enumerate(end_times):
            for sim_time_stat in sim_time_stats[idx]:
                plt.plot(end_time, sim_time_stat[1][key], 'bo')
        plt.show()


def motivation_number_runs():
    # 2. Simulating with identified simulation length, getting a reasonable number of runs.
    # Using simulation_length = 1500, and discarding the first 100 items as the system takes this time to warm-up
    run_sizes = [i for i in range(0, 10)]
    graph_type = 'Highway'
    sim_time_stats = []
    for run_size in run_sizes:
        # sim_time_stats.append[]
        for i in range(run_size):
            system = run_simulation(seed=None, end_time=1500, stats_step_size=50, graph_type=graph_type, tow_truck_mode=True)
            sim_time_stats[-1].append(system.time_statistics[-1])
    key = 'Average number of incidents'
    plot = plt.figure()
    plt.ylabel(key)
    plt.xlabel('Simulation Time')
    for idx, val in enumerate(run_sizes):
        run_time = run_sizes[idx]
        for run in sim_time_stats:
            for stat_tuple in run:
                plt.plot([stat_tuple[0]], [stat_tuple[1][key]], 'o')
    plt.show()


def motivation_number_tow_trucks():
    graph_type = 'Highway'  # Toy1, Toy2, Highway
    # number_of_runs = 1
    number_of_runs = 20
    tow_truck_numbers = [i for i in range(1, 26)]
    # tow_truck_numbers = [1, 6, 11, 16]
    # end_times = [150, 300, 450]
    # print(end_times)
    sim_time_stats = [[] for i in range(len(tow_truck_numbers))]
    for i, ival in enumerate(tow_truck_numbers):
        for j in range(number_of_runs):
            system = run_simulation(simulation_id=str('tow_truck_number-') + str(ival) + '-' + str(j), seed=None, end_time=1600,
                                    stats_step_size=50, graph_type=graph_type, tow_truck_mode=True, warm_up=100, number_of_tow_trucks=ival)
            sim_time_stats[i].append((str(ival)+str(j) , system.final_statistics))
    # keys = ['number_of_ghost_cars_at_time', 'number_of_route_cars_at_time', 'number_of_current_incidents', 'Average number of incidents']
    # keys = ['number_of_current_incidents', 'Average number of incidents']
    keys = ['average_number_of_incidents']

    for key in keys:
        plot = plt.figure()

        # plt.ylim()
        plt.xticks([i for i in range(1, 40, 5)], [i for i in range(1, 40, 5)])
        plt.ylabel(key)
        plt.xlabel('Number of tow trucks')
        for idx, tow_truck_number in enumerate(tow_truck_numbers):
            for sim_time_stat in sim_time_stats[idx]:
                plt.plot(tow_truck_number, sim_time_stat[1][key], 'bo')
        bottom, top = plt.ylim()
        plt.xlim(0, 25)
        plt.ylim(0, top)
        plt.show()


def perf_measure_1():
    # 1. For individual vehicles: distribution of the travel time (mean, standard deviation, plot
    # a histogram). Indicate which part of the travel time is caused by the delay. Present
    # results on the number of incidents they encounter on average (again: mean, standard
    # deviation, distribution).

    # Travel time on the route between A to B
    # Probability of minutes of time taken for the travel along the route. Ghost cars not necessary, or included.
    graph_type = 'Highway'
    system = run_simulation('Measure-1', seed=30, end_time=1600, stats_step_size=50, graph_type=graph_type, tow_truck_mode=True, warm_up=100)
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
                                tow_truck_mode=True, warm_up=100)
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
    system = run_simulation('Measure-2-vis', seed=40, end_time=1600, stats_step_size=50, graph_type=graph_type, tow_truck_mode=True, warm_up=100)
    times_delayed_per_number_of_cars = system.final_statistics['time_spent_delayed_per_current_number_of_all_cars']
    print('Time spent per number of delayed cars', times_delayed_per_number_of_cars)
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
                                tow_truck_mode=True, warm_up=100)
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
                            tow_truck_mode=True, warm_up=100)
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
    plt.xlabel('Numbers of incidents (With tow trucks)')
    plt.ylabel('Fraction of time spent')
    plt.xlim(min_non_zero_incidents - 1, max_non_zero_incidents)
    plt.xticks([i for i in range(min_non_zero_incidents -1, max_non_zero_incidents)], [i for i in range(min_non_zero_incidents -1, max_non_zero_incidents)])
    plt.bar([i for i in range(len(times_fraction_per_number_of_incidents))], [j / sum(times_fraction_per_number_of_incidents) for j in times_fraction_per_number_of_incidents])
    plt.show()

    average_number_of_incidents = []
    # CI calculation
    for i in range(run_size):
        system = run_simulation('Measure-3' + str(i), seed=i, end_time=1600, stats_step_size=50, graph_type=graph_type,
                                tow_truck_mode=True, warm_up=100)
        print('Run -', i)
        average_number_of_incidents.append(system.final_statistics['average_number_of_incidents'])

    mean_number_of_incidents = sum(average_number_of_incidents) / len(average_number_of_incidents)
    std_number_of_incidents = std(average_number_of_incidents)
    print('Mean of Route Travel Time -', mean_number_of_incidents)
    print('Standard Deviation of Route Travel Time -', std_number_of_incidents)
    halfwidth_number_of_incidents = ci(std_number_of_incidents, run_size)
    print('Halfwidth of Route Travel Time -', halfwidth_number_of_incidents)
    print('Range - ', mean_number_of_incidents - halfwidth_number_of_incidents, mean_number_of_incidents + halfwidth_number_of_incidents)


def variance_of_performance_measures_with_tow_trucks():
    # tow_truck_numbers = [5, 10, 15, 16, 20]
    tow_truck_numbers = [i for i in range(1, 26)]
    # tow_truck_numbers = [20, 30]
    run_size_int = 5

    travel_x = []
    travel_y = []
    delays_x = []
    delays_y = []
    num_delays_x = []
    num_delays_y = []
    incidents_x = []
    incidents_y = []

    for tow_truck_number in tow_truck_numbers:
        travel_times_list = []
        number_delays_list = []
        delay_times_list = []
        average_number_of_incidents = []
        for run in range(run_size_int):
            graph_type = 'Highway'
            system = run_simulation('Variance-' + str(tow_truck_number)+ str('-') + str(run), seed=40+tow_truck_number + run, end_time=1600, stats_step_size=50, graph_type=graph_type,
                                    tow_truck_mode=True, warm_up=100, number_of_tow_trucks=tow_truck_number)
            travel_times_list.append(mean(system.final_statistics['route_travel_times']))
            delay_times_list.append(mean(system.final_statistics['route_delay_times']))
            number_delays_list.append(mean(system.final_statistics['route_number_delays']))
            average_number_of_incidents.append(system.final_statistics['average_number_of_incidents'])
        travel_y += travel_times_list
        travel_x += [tow_truck_number for i in range(run_size_int)]
        delays_y += delay_times_list
        delays_x += [tow_truck_number for i in range(run_size_int)]
        num_delays_y += number_delays_list
        num_delays_x += [tow_truck_number for i in range(run_size_int)]
        incidents_y += average_number_of_incidents
        incidents_x += [tow_truck_number for i in range(run_size_int)]

    print('Average travel times -', travel_y)
    print('Average delay times -', delays_y)
    print('Number of delays -', num_delays_y)
    print('Average number of incidents -', incidents_y)
    print('Tow truck numbers -', incidents_x)

    plot = plt.figure()
    plt.xlabel('Number of tow trucks')
    plt.ylabel('Average route travel time')
    plt.plot(travel_x, travel_y, 'bo')
    # bottom, top = plt.ylim()
    # plt.ylim(bottom=0, top=top)
    plt.xticks(incidents_x, incidents_x)
    plt.show()

    plot = plt.figure()
    plt.xlabel('Number of tow trucks')
    plt.ylabel('Average delay time')
    plt.plot(delays_x, delays_y, 'bo')
    # bottom, top = plt.ylim()
    # plt.ylim(bottom=0, top=top)
    plt.xticks(incidents_x, incidents_x)
    plt.show()

    plot = plt.figure()
    plt.xlabel('Number of tow trucks')
    plt.ylabel('Average number of delays')
    plt.plot(num_delays_x, num_delays_y, 'bo')
    bottom, top = plt.ylim()
    plt.ylim(bottom=0, top=top)
    plt.xticks(incidents_x, incidents_x)
    plt.show()

    plot = plt.figure()
    plt.xlabel('Number of tow trucks')
    plt.ylabel('Numbers of incidents (With tow trucks)')
    plt.plot(incidents_x, incidents_y, 'bo')
    bottom, top = plt.ylim()
    plt.ylim(bottom=0, top=top)
    plt.xticks(incidents_x, incidents_x)
    plt.show()

def stats_of_edges_served_by_tow_trucks():
    graph_type = 'Highway'
    edge_numbers =[0 for i in range(100)]
    for i in range(run_size):
        system = run_simulation('EdgesServed-', seed=100+i, end_time=1600, stats_step_size=50, graph_type=graph_type, tow_truck_mode=True, warm_up=100)
        print(system.final_statistics['number_of_times_edges_served_by_tow_trucks'])
        edge_numbers = list(map(sum, zip(edge_numbers, system.final_statistics['number_of_times_edges_served_by_tow_trucks'])))
    edge_numbers =[i/run_size for i in edge_numbers]
    print(edge_numbers)
    # edge_numbers = system.final_statistics['number_of_times_edges_served_by_tow_trucks']
    # edge_numbers = [0, 1, 0, 4, 5, 5, 1, 5, 4, 9, 3, 10, 6, 2, 4, 2, 5, 2, 3, 4, 6, 5, 4, 1, 6, 9, 5, 2, 9, 3, 5, 8, 6, 2, 2, 2, 4, 4, 3, 6, 2, 5, 1, 1, 4, 1, 2, 2, 2, 3, 3, 1, 3, 5, 2, 2, 3, 9, 8, 3, 3, 3, 4, 6, 0, 6, 3, 1, 4, 7, 5, 3, 2, 1, 3, 3, 2, 5, 3, 1, 4, 3, 4, 10, 2, 6, 3, 3, 2, 4, 1, 4, 7, 3, 2, 3, 1, 3, 1, 0]
    # graph, route_path = util.build_highway_graph()
    edge_num_dict = dict()
    for key, val in enumerate(edge_numbers):
        edge_num_dict[key] = val
    sorted_edge_nums = sorted(edge_num_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[0:15]
    print(sorted_edge_nums)
    x = []
    y = []
    for edge in sorted_edge_nums:
        edge_id = edge[0]
        source_node = system.graph.edges[edge_id].source_id
        target_node = system.graph.edges[edge_id].target_id
        x.append(util.city_names[source_node] + '-' + util.city_names[target_node])
        y.append(edge[1])

    plot = plt.figure()
    plt.xlabel('Highway link')
    plt.ylabel('Numbers of times reached by tow trucks')

    # plt.plot(incidents_x, incidents_y, 'bo')
    plt.bar(x, y)
    plt.xticks(x, x, rotation='vertical')
    plt.subplots_adjust(bottom=0.40)
    # plt.margins(0.2)
    # bottom, top = plt.ylim()
    # plt.ylim(bottom=0, top=top)
    # plt.xticks(incidents_x, incidents_x)
    plt.show()

def get_list_of_edges_with_freq():
    frequencies = [2.9, 3.1, 2.55, 2.6, 3.5, 3.45, 3.3, 4.2, 4.35, 4.55, 5.45, 3.7, 3.65, 3.55, 2.8, 3.2, 2.3, 2.6, 4.65, 4.35, 4.25, 4.65, 4.1, 4.95, 4.1, 6.4, 5.95, 5.2, 5.6, 4.75, 5.4, 5.25, 4.05, 2.45, 2.55, 2.85, 3.9, 2.45, 2.5, 3.5, 2.25, 3.55, 3.1, 2.0, 1.6, 2.4, 3.1, 1.95, 3.2, 3.5, 3.8, 4.0, 3.1, 4.95, 3.85, 3.75, 3.4, 5.45, 2.85, 2.0, 2.3, 2.7, 2.15, 3.3, 4.2, 4.2, 2.85, 3.8, 5.05, 5.3, 6.35, 4.6, 1.9, 2.6, 2.9, 2.75, 2.25, 2.0, 2.9, 2.8, 2.1, 3.15, 2.3, 3.75, 2.85, 2.75, 2.3, 3.2, 1.65, 2.5, 1.85, 2.6, 2.55, 2.9, 2.7, 3.6, 2.95, 4.05, 2.7, 3.3]
    graph, route_path = util.build_highway_graph()
    edge_num_dict = dict()
    for key, val in enumerate(frequencies):
        edge_num_dict[key] = val
    sorted_edge_nums = sorted(edge_num_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    print(sorted_edge_nums)
    output_string = ''
    max_frequencies = max(frequencies)
    min_frequencies = 0
    print(max_frequencies)
    state = ''
    for edge in sorted_edge_nums:
        source_node = util.city_names[graph.edges[edge[0]].source_id]
        target_node = util.city_names[graph.edges[edge[0]].target_id]
        freq = edge[1]
        if freq > 0 and freq < 2.33 :
            state = 'Green'
        elif freq >=2.33 and freq < 4.67:
            state = 'Yellow'
        elif freq>= 4.67:
            state = 'Red'
        output_string += str(source_node) + '-' + str(target_node) + '--\t\t' + str(freq) + '\t'  + state + '\n'

    print(output_string)

if __name__ == '__main__':
    logging.basicConfig(filename='highway-tow-variance3.log', level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')
    run_size = 20
    # motivation_simulation_length()
    # motivation_number_tow_trucks()
    # perf_measure_1()
    # perf_measure_2()
    # perf_measure_3()
    # variance_of_performance_measures_with_tow_trucks()
    # stats_of_edges_served_by_tow_trucks()
    get_list_of_edges_with_freq()