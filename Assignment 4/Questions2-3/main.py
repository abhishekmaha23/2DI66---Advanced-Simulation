import simpy
from util import *
import logging
import time


class HighwaySystem(object):
    def __init__(self, env, graph, bfs_graph, route_path, num_tow_trucks, tow_truck_center_id, preprocessed_routes, tow_truck_mode=False, seed=20, warm_up=0):
        self.env = env
        self.graph = graph
        self.route_path = route_path
        self.road_assist_company = simpy.Resource(env, num_tow_trucks)
        self.bfs_graph = bfs_graph
        self.tow_truck_center_id = tow_truck_center_id
        self.tow_truck_routes = preprocessed_routes
        self.tow_truck_assistance_present = tow_truck_mode
        self.preprocessed_routes = preprocessed_routes
        self.warm_up = warm_up

        self.incident_arrival_dist = get_incident_interarrival(random_state=seed)
        self.incident_duration_dist = get_incident_duration(random_state=seed)
        self.car_arrival_rate_distribution = arrival_rate_distribution(random_state=seed)

        # Stats over all edges - used to generate IDs for the cars
        self.num_ghost_cars_current = 0
        self.num_ghost_cars_overall = 0
        self.num_route_cars_current = 0
        self.num_route_cars_overall = 0
        self.num_incidents_overall = 0
        self.num_incidents_active = 0

        # Q1- Part 1
        self.final_statistics = dict()
        self.final_statistics['time_spent_per_current_number_of_incidents'] = [0 for i in range(150)] # Assuming 150 incidents at most at a time.
        self.final_statistics['last_number_of_incidents_update_time'] = 0
        # Q1 - Part 2, 3
        self.final_statistics['route_travel_times'] = []
        self.final_statistics['route_delay_times'] = []
        self.final_statistics['route_number_delays'] = []
        self.final_statistics['ghost_delay_times'] = []
        self.final_statistics['ghost_number_delays'] = []
        # Q2
        self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'] = []
        self.final_statistics['last_number_of_delayed_route_cars_update_time'] = 0
        self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'] = []
        self.final_statistics['last_number_of_delayed_ghost_cars_update_time'] = 0
        self.final_statistics['time_spent_delayed_per_current_number_of_all_cars'] = []
        self.final_statistics['last_number_of_delayed_all_cars_update_time'] = 0
        self.final_statistics['number_of_currently_delayed_route_cars'] = 0
        self.final_statistics['number_of_currently_delayed_ghost_cars'] = 0
        self.final_statistics['number_of_currently_delayed_all_cars'] = 0
        self.final_statistics['number_of_times_edges_served_by_tow_trucks'] = [0 for i in range(len(self.graph.edges))]

        self.time_statistics = dict()

    def travel_one_link(self, e_id, car_id):
        travel_time = self.graph.edges[e_id].travel_time_distribution.rvs()
        sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' generated for edge ' + str(self.graph.edges[e_id]) + ' with travel time ' + str(round(travel_time, 3)))
        # Add incident time to travel time
        overall_delay = 0
        number_of_delays = 0
        possibly_affecting_incidents = []
        for index, incident_status in enumerate(self.graph.edges[e_id].active_incidents):
            if incident_status is True:
                incident = self.graph.edges[e_id].incidents[index]
                possibly_affecting_incidents.append(incident)
        sorted_affecting_incidents = sorted(possibly_affecting_incidents)
        sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(
            car_id) + ' - Sorted affecting incidents ->' + '#'.join(str(e) for e in sorted_affecting_incidents))
        current_location = 0
        # current_time_point_temp = self.env.now

        for affecting_incident in sorted_affecting_incidents:
            time_taken_to_reach_affecting_incident = travel_time * (affecting_incident.location - current_location)
            time_point_of_reaching_affecting_incident_location = self.env.now + time_taken_to_reach_affecting_incident
            sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(
                car_id) + ' current location - ' + str(current_location))
            sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(
                car_id) + ' time_point_of_reaching_afecting_incident_location ' + str(
                round(time_point_of_reaching_affecting_incident_location, 3)))
            sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(
                car_id) + ' time_taken_to_reach_affecting_incident ' + str(round(time_taken_to_reach_affecting_incident, 3)))
            sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(
                car_id) + ' incident_start_time ' + str(round(affecting_incident.start_time, 3)) + '-- incident_end_time ' + str(
                round(affecting_incident.start_time + affecting_incident.duration, 3)))

            incident_end_time = affecting_incident.start_time + affecting_incident.duration
            if incident_end_time > time_point_of_reaching_affecting_incident_location:
                yield self.env.timeout(time_taken_to_reach_affecting_incident)
                # current_time_point_temp += time_taken_to_reach_affecting_incident
                sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' should be performing travel time yield.timeout(' + str(time_taken_to_reach_affecting_incident) +')')
                incident_delay_time = incident_end_time - time_point_of_reaching_affecting_incident_location
                sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' should be performing incident delay yield.timeout(' + str(incident_delay_time) + ')')

                # Adding statistic before timeout occurs/Removing after timeout ends
                time_spent_with_previous_number_of_delayed_ghost_cars = self.env.now - self.final_statistics['last_number_of_delayed_ghost_cars_update_time']
                self.final_statistics['last_number_of_delayed_ghost_cars_update_time'] = self.env.now
                time_spent_with_previous_number_of_delayed_all_cars = self.env.now - self.final_statistics['last_number_of_delayed_all_cars_update_time']
                self.final_statistics['last_number_of_delayed_all_cars_update_time'] = self.env.now

                # Updating the final_statistic for the time_spent_delayed_per_current_number_of_all_cars parameter
                temp_variable_all = self.final_statistics['time_spent_delayed_per_current_number_of_all_cars']
                while len(temp_variable_all) < self.final_statistics['number_of_currently_delayed_all_cars'] + 2:
                    temp_variable_all.append(0)
                temp_variable_all[self.final_statistics['number_of_currently_delayed_all_cars']] += time_spent_with_previous_number_of_delayed_all_cars
                self.final_statistics['number_of_currently_delayed_all_cars'] += 1

                # Updating the final_statistic for the time_spent_delayed_per_current_number_of_ghost_cars parameter
                temp_variable = self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars']
                while len(temp_variable) < self.final_statistics['number_of_currently_delayed_ghost_cars'] + 2:
                    temp_variable.append(0)
                temp_variable[self.final_statistics['number_of_currently_delayed_ghost_cars']] += time_spent_with_previous_number_of_delayed_ghost_cars
                # try:
                # except IndexError:
                #     self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'].append(time_spent_with_previous_number_of_delayed_ghost_cars)
                sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' current number of delayed_ghost_cars about to increase ' + str(self.final_statistics['number_of_currently_delayed_ghost_cars']) )
                self.final_statistics['number_of_currently_delayed_ghost_cars'] += 1

                # Actual delay time
                yield self.env.timeout(incident_delay_time)

                sim_log('DEBUG', self.env, e_id,
                        ':Ghost car ' + str(car_id) + 'current number of delayed_ghost_cars about to decrease ' + str(
                            self.final_statistics['number_of_currently_delayed_ghost_cars']))

                # All cars delay reduction handling
                post_time_spent_with_previous_number_of_delayed_all_cars = self.env.now - self.final_statistics[
                    'last_number_of_delayed_all_cars_update_time']
                self.final_statistics['last_number_of_delayed_all_cars_update_time'] = self.env.now
                while len(temp_variable_all) < self.final_statistics['number_of_currently_delayed_all_cars'] + 2:
                    temp_variable_all.append(0)
                self.final_statistics['time_spent_delayed_per_current_number_of_all_cars'][self.final_statistics[
                    'number_of_currently_delayed_all_cars']] += post_time_spent_with_previous_number_of_delayed_all_cars
                self.final_statistics['number_of_currently_delayed_all_cars'] -= 1

                # Ghost car delay reduction handling
                post_time_spent_with_previous_number_of_delayed_ghost_cars = self.env.now - self.final_statistics['last_number_of_delayed_ghost_cars_update_time']
                self.final_statistics['last_number_of_delayed_ghost_cars_update_time'] = self.env.now
                while len(temp_variable) < self.final_statistics['number_of_currently_delayed_ghost_cars'] + 2:
                    temp_variable.append(0)
                self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'][self.final_statistics['number_of_currently_delayed_ghost_cars']] += post_time_spent_with_previous_number_of_delayed_ghost_cars
                # except IndexError:
                #     self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'].append(post_time_spent_with_previous_number_of_delayed_ghost_cars)
                self.final_statistics['number_of_currently_delayed_ghost_cars'] -= 1

                overall_delay += incident_delay_time
                number_of_delays += 1
                current_location = affecting_incident.location
            else:
                # Won't reach incident in time, so skipping.
                sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' skipping affecting incident ' + str(affecting_incident.incident_id))

        # Handle reaching the end of the link
        end_of_link = 1
        time_taken_to_reach_end_of_link = travel_time * (end_of_link - current_location)
        # time_point_of_reaching_end_of_link = current_time_point_temp + time_taken_to_reach_end_of_link
        time_point_of_reaching_end_of_link = self.env.now + time_taken_to_reach_end_of_link
        sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' should be performing travel time yield.timeout(' + str(time_taken_to_reach_end_of_link) + ')')
        sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' will reach end at ' + str(time_point_of_reaching_end_of_link))
        yield self.env.timeout(time_taken_to_reach_end_of_link)
        self.final_statistics['ghost_delay_times'].append(overall_delay)
        self.final_statistics['ghost_number_delays'].append(number_of_delays)
        sim_log('DEBUG', self.env, e_id, ':Ghost car ' + str(car_id) + ' exiting having taken ' + str(round(travel_time, 3)) + ' time')
        self.num_ghost_cars_current -= 1

    def travel_route(self, car_id):
        start_time = self.env.now
        overall_delay = 0
        number_of_delays = 0
        sim_log('DEBUG', self.env, self.route_path[0], ':Route car ' + str(car_id) + ' entering at edge ' + str(self.graph.edges[self.route_path[0]]))

        for edge_id in self.route_path:
            # Should be a list of edge IDs, not actual edges
            travel_time = self.graph.edges[edge_id].travel_time_distribution.rvs()
            sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(
                car_id) + ' begins travel for edge ' + str(self.graph.edges[edge_id]) + ' with travel time ' + str(
                round(travel_time, 3)))

            possibly_affecting_incidents = []
            for index, incident_status in enumerate(self.graph.edges[edge_id].active_incidents):
                if incident_status is True:
                    incident = self.graph.edges[edge_id].incidents[index]
                    possibly_affecting_incidents.append(incident)
            sorted_affecting_incidents = sorted(possibly_affecting_incidents)
            sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' - Sorted incidents ->' + '#'.join(str(e) for e in sorted_affecting_incidents))
            current_location = 0
            # current_time_point_temp = self.env.now

            for affecting_incident in sorted_affecting_incidents:
                time_taken_to_reach_affecting_incident = travel_time * (affecting_incident.location - current_location)
                time_point_of_reaching_affecting_incident_location = self.env.now + time_taken_to_reach_affecting_incident
                # sim_log('DEBUG', self.env, e_id, ':Route car ' + str(
                #     car_id) + ' current time_point_temp - ' + str(current_time_point_temp))
                sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' current location - ' + str(current_location))
                sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' time_point_of_reaching_afecting_incident_location ' + str(round(time_point_of_reaching_affecting_incident_location, 3)))
                sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' time_taken_to_reach_affecting_incident ' + str(round(time_taken_to_reach_affecting_incident, 3)))
                sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' incident_start_time ' + str(round(affecting_incident.start_time, 3)) + '-- incident_end_time ' + str(round(affecting_incident.start_time + affecting_incident.duration, 3)))

                incident_end_time = affecting_incident.start_time + affecting_incident.duration
                if incident_end_time > time_point_of_reaching_affecting_incident_location:
                    # current_time_point_temp += time_taken_to_reach_affecting_incident
                    sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' should be performing incident travel time yield.timeout(' + str(time_taken_to_reach_affecting_incident) + ')')
                    yield self.env.timeout(time_taken_to_reach_affecting_incident)
                    incident_delay_time = incident_end_time - time_point_of_reaching_affecting_incident_location
                    sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' should be performing incident delay yield.timeout(' + str(incident_delay_time) + ')')


                    # Adding statistic before timeout occurs/Removing after timeout ends
                    # time_spent_with_previous_number_of_delayed_route_cars = self.env.now - self.final_statistics[
                    #     'last_number_of_delayed_route_cars_update_time']
                    # self.final_statistics['last_number_of_delayed_route_cars_update_time'] = self.env.now
                    # try:
                    #     self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'][self.final_statistics['number_of_currently_delayed_route_cars']] += time_spent_with_previous_number_of_delayed_route_cars
                    # except IndexError:
                    #     self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'].append(time_spent_with_previous_number_of_delayed_route_cars)
                    # sim_log('DEBUG', self.env, edge_id, ':Route car ' + str(
                    #     car_id) + 'current number of delayed_route_cars about to increase ' + str(
                    #     self.final_statistics['number_of_currently_delayed_route_cars']))
                    # self.final_statistics['number_of_currently_delayed_route_cars'] += 1

                    time_spent_with_previous_number_of_delayed_all_cars = self.env.now - self.final_statistics[
                        'last_number_of_delayed_all_cars_update_time']
                    self.final_statistics['last_number_of_delayed_all_cars_update_time'] = self.env.now

                    # Updating the final_statistic for the time_spent_delayed_per_current_number_of_all_cars parameter
                    temp_variable_all = self.final_statistics['time_spent_delayed_per_current_number_of_all_cars']
                    while len(temp_variable_all) < self.final_statistics['number_of_currently_delayed_all_cars'] + 2:
                        temp_variable_all.append(0)
                    temp_variable_all[self.final_statistics[
                        'number_of_currently_delayed_all_cars']] += time_spent_with_previous_number_of_delayed_all_cars
                    self.final_statistics['number_of_currently_delayed_all_cars'] += 1


                    time_spent_with_previous_number_of_delayed_route_cars = self.env.now - self.final_statistics['last_number_of_delayed_route_cars_update_time']

                    self.final_statistics['last_number_of_delayed_route_cars_update_time'] = self.env.now

                    # Updating the final_statistic for the time_spent_delayed_per_current_number_of_route_cars parameter
                    temp_variable = self.final_statistics['time_spent_delayed_per_current_number_of_route_cars']
                    while len(temp_variable) < self.final_statistics['number_of_currently_delayed_route_cars'] + 2:
                        temp_variable.append(0)
                    temp_variable[self.final_statistics[
                        'number_of_currently_delayed_route_cars']] += time_spent_with_previous_number_of_delayed_route_cars
                    # try:
                    # except IndexError:
                    #     self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'].append(time_spent_with_previous_number_of_delayed_ghost_cars)
                    sim_log('DEBUG', self.env, edge_id, ':Route car ' + str(
                        car_id) + ' current number of delayed_route_cars about to increase ' + str(
                        self.final_statistics['number_of_currently_delayed_route_cars']))
                    self.final_statistics['number_of_currently_delayed_route_cars'] += 1

                    logging.debug('time spent delayed on route cars -' + str(
                        self.final_statistics['time_spent_delayed_per_current_number_of_route_cars']))
                    logging.debug('time spent delayed on ghost cars -' + str(
                        self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars']))
                    logging.debug('time spent delayed all cars -' + str(
                        self.final_statistics['time_spent_delayed_per_current_number_of_all_cars']))

                    # Actual delay time
                    yield self.env.timeout(incident_delay_time)

                    # Handling all cars delay reduction
                    post_time_spent_with_previous_number_of_delayed_all_cars = self.env.now - self.final_statistics[
                        'last_number_of_delayed_all_cars_update_time']
                    self.final_statistics['last_number_of_delayed_all_cars_update_time'] = self.env.now
                    while len(temp_variable_all) < self.final_statistics['number_of_currently_delayed_all_cars'] + 2:
                        temp_variable_all.append(0)
                    self.final_statistics['time_spent_delayed_per_current_number_of_all_cars'][self.final_statistics[
                        'number_of_currently_delayed_all_cars']] += post_time_spent_with_previous_number_of_delayed_all_cars
                    self.final_statistics['number_of_currently_delayed_all_cars'] -= 1

                    # Handling ghost car delay reduction
                    sim_log('DEBUG', self.env, edge_id,
                            ':Route car ' + str(
                                car_id) + 'current number of delayed_route_cars about to decrease ' + str(
                                self.final_statistics['number_of_currently_delayed_route_cars']))
                    post_time_spent_with_previous_number_of_delayed_route_cars = self.env.now - self.final_statistics[
                        'last_number_of_delayed_route_cars_update_time']
                    self.final_statistics['last_number_of_delayed_route_cars_update_time'] = self.env.now
                    while len(temp_variable) < self.final_statistics['number_of_currently_delayed_route_cars'] + 2:
                        temp_variable.append(0)
                    self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'][self.final_statistics[
                        'number_of_currently_delayed_route_cars']] += post_time_spent_with_previous_number_of_delayed_route_cars
                    # except IndexError:
                    #     self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'].append(post_time_spent_with_previous_number_of_delayed_ghost_cars)
                    self.final_statistics['number_of_currently_delayed_route_cars'] -= 1


                    # sim_log('DEBUG', self.env, edge_id,
                    #         ':Route car ' + str(
                    #             car_id) + 'current number of delayed_route_cars about to decrease ' + str(
                    #             self.final_statistics['number_of_currently_delayed_route_cars']))
                    # post_time_spent_with_previous_number_of_delayed_route_cars = self.env.now - self.final_statistics[
                    #     'last_number_of_delayed_route_cars_update_time']
                    # self.final_statistics['last_number_of_delayed_route_cars_update_time'] = self.env.now
                    # try:
                    #     self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'][
                    #         self.final_statistics[
                    #             'number_of_currently_delayed_ghost_cars']] += post_time_spent_with_previous_number_of_delayed_route_cars
                    # except IndexError:
                    #     self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'].append(
                    #         post_time_spent_with_previous_number_of_delayed_route_cars)
                    # self.final_statistics['number_of_currently_delayed_route_cars'] -= 1

                    logging.debug('time spent delayed on route cars -' + str(
                        self.final_statistics['time_spent_delayed_per_current_number_of_route_cars']))
                    logging.debug('time spent delayed on ghost cars -' + str(
                        self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars']))
                    logging.debug('time spent delayed all cars -' + str(
                        self.final_statistics['time_spent_delayed_per_current_number_of_all_cars']))

                    overall_delay += incident_delay_time
                    number_of_delays += 1
                    # current_time_point_temp += incident_delay_time
                    sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' current location orig ' + str(current_location))
                    current_location = affecting_incident.location
                    sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' current location changed to incident ' + str(current_location))
                else:
                    # Won't reach incident in time, so skipping.
                    sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' skipping affecting incident ' + str(affecting_incident.incident_id))

            # Handle reaching the end of the link
            sim_log('DEBUG', self.env, edge_id,  ':Route car ' + str(car_id) + ' current location - ' + str(current_location))
            end_of_link = 1
            time_taken_to_reach_end_of_link = travel_time * (end_of_link - current_location)
            # time_point_of_reaching_end_of_link = current_time_point_temp + time_taken_to_reach_end_of_link
            time_point_of_reaching_end_of_link = self.env.now + time_taken_to_reach_end_of_link
            sim_log('DEBUG', self.env, edge_id, ':Route car ' + str(car_id) + ' should be performing final travel time yield.timeout(' + str(time_taken_to_reach_end_of_link) + ')')
            sim_log('DEBUG', self.env, edge_id, ':Route car ' + str(car_id) + ' will reach end at ' + str(time_point_of_reaching_end_of_link))
            yield self.env.timeout(time_taken_to_reach_end_of_link)
        sim_log('DEBUG', self.env, self.route_path[-1], ':Route car ' + str(car_id) + ' is exiting having taken ' + str(round(travel_time, 3)))
        self.num_route_cars_current -= 1
        overall_travel_time = self.env.now - start_time
        self.final_statistics['route_delay_times'].append(overall_delay)
        self.final_statistics['route_number_delays'].append(number_of_delays)
        self.final_statistics['route_travel_times'].append(overall_travel_time)

    def incident_handler(self, incident, e_id):
        # Handle entering incident into graph
        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' occurring at point ' + str(round(incident.location,3)) + ' taking ' + str(round(incident.duration, 3)) + ' time on edge ' + str(self.graph.edges[e_id]) )
        self.graph.edges[e_id].incidents.append(incident)
        self.graph.edges[e_id].active_incidents.append(True)

        if self.tow_truck_assistance_present is True:
            time_taken_for_tow_truck_to_reach_incident = 0
            edge_times_taken_by_tow_truck_to_reach_incident = []
            link_start_point = self.graph.edges[e_id].source_id
            for path_edge_index in self.preprocessed_routes[link_start_point]:
                time = self.graph.edges[path_edge_index].travel_time_distribution.rvs()
                time_taken_for_tow_truck_to_reach_incident += time
                edge_times_taken_by_tow_truck_to_reach_incident.append(time)
            time_on_current_edge = self.graph.edges[e_id].travel_time_distribution.rvs()
            time_taken_for_tow_truck_to_reach_incident += (time_on_current_edge*incident.location)
            edge_times_taken_by_tow_truck_to_reach_incident.append(time_on_current_edge*incident.location)

            # An incident can only wait for a certain amount of time.
            # If the tow truck can't arrive in enough time to help an incident, then the two truck might
            # as well not be called.
            # Representing this as a intensely limiting condition.
            # This kinda foreshadows that very few incidents outside a certain threshold from the tow_truck
            # center will be attended to.
            patience = incident.duration - time_taken_for_tow_truck_to_reach_incident
            sim_log('DEBUG', self.env, e_id, ':Incident ' + str(
                incident.incident_id) + ' has patience ' + str(round(patience, 3)) + ' due to tow_truck_time ' + str(round(time_taken_for_tow_truck_to_reach_incident, 3)))

            if patience < 0:
                # Means the amount of possible time that the incident could be reduced by, since it gets cleared as
                # soon as the tow truck will arrive. If no time is saved, then the tow truck is not going to make
                # a difference, so we're going to assume that the incident is treated normally as a timeout event.
                yield self.env.timeout(incident.duration)
                sim_log('DEBUG', self.env, e_id, ':Incident ' + str(
                    incident.incident_id) + ' ending at point ' + str(round(incident.location, 3)) + " (couldn't be helped " +
                                                                                           "by a tow truck) (NO TOW TRUCK ASSISTANCE POSSIBLE)")

                # Handle removing incident from graph
                time_spent_current_number_of_incidents = self.env.now - self.final_statistics['last_number_of_incidents_update_time']
                self.final_statistics['last_number_of_incidents_update_time'] = self.env.now
                self.final_statistics['time_spent_per_current_number_of_incidents'][self.num_incidents_active] += time_spent_current_number_of_incidents
                self.num_incidents_active -= 1
                self.graph.edges[e_id].active_incidents[incident.edge_incident_id] = False
            else:
                # Tow truck resource will be released as soon as the with-block ends, so within the block
                # everything must be handled- tow-truck arrival, incident handling and tow-truck return.
                # We are aided by the fact that there are 2 things to handle.
                # Incident duration needs to be changed in the system, so that other cars can keep working through them.
                # Tow-truck routing will be handled within this thread, and so must return of the tow_truck.
                # Thus because both steps are handled within this block, we have to change the status of the incident
                # within this block instead of outside.
                sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' has travel_for_tow_truck as ' + str(round(time_taken_for_tow_truck_to_reach_incident, 3)) + ' along path ' + str(self.preprocessed_routes[link_start_point]))
                with self.road_assist_company.request() as req:
                    results = yield req | self.env.timeout(patience)
                    if req in results:
                        # Waited for the amount of patience that was possible.
                        # A tow truck became available before the patience ran out.
                        self.final_statistics['number_of_times_edges_served_by_tow_trucks'][e_id] += 1
                        wait_time = self.env.now - incident.start_time
                        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' tow-truck available after waiting for ' + str(round(wait_time, 3)))
                        remaining_time = time_taken_for_tow_truck_to_reach_incident
                        # Calculating the time taken for tow_truck to reach incident
                        self.graph.edges[e_id].incidents[incident.edge_incident_id].duration = wait_time + remaining_time
                        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' duration changed to ' + str(round(wait_time + remaining_time, 3)))
                        yield self.env.timeout(remaining_time)
                        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' ending ' + " (actually helped by a tow truck) (TOW TRUCK ASSISTANCE RECEIVED)")
                        # Handle removing incident from graph
                        time_spent_current_number_of_incidents = self.env.now - self.final_statistics['last_number_of_incidents_update_time']
                        self.final_statistics['last_number_of_incidents_update_time'] = self.env.now
                        self.final_statistics['time_spent_per_current_number_of_incidents'][self.num_incidents_active] += time_spent_current_number_of_incidents
                        self.num_incidents_active -= 1
                        self.graph.edges[e_id].active_incidents[incident.edge_incident_id] = False

                        # Must handle return journey of tow_truck, since it takes similar time returning, just with a factor of 0.9
                        time_taken_for_tow_truck_to_return = 0
                        for path_edge_index in self.preprocessed_routes[link_start_point]:
                            time_internal = self.graph.edges[path_edge_index].travel_time_distribution.rvs()
                            time_taken_for_tow_truck_to_return += time_internal
                        return_time_on_current_edge = self.graph.edges[e_id].travel_time_distribution.rvs()
                        time_taken_for_tow_truck_to_return += (return_time_on_current_edge * incident.location)
                        # Slower when returning.
                        time_taken_for_tow_truck_to_return = time_taken_for_tow_truck_to_return * (1 / 0.9)
                        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' tow_truck starting on return journey of length ' + str(round(time_taken_for_tow_truck_to_return, 3)))
                        yield self.env.timeout(time_taken_for_tow_truck_to_return)
                        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' tow_truck returned to available position')
                    else:
                        # Patience ran out and tow truck did not get available
                        remaining_time = incident.duration - patience
                        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' patience timed out.')
                        yield self.env.timeout(remaining_time)
                        sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' ending ' + " (tried to wait but couldn't be helped by a tow truck) (NO TOW TRUCK ASSISTANCE RECEIVED)")

                        # Handle removing incident from graph
                        time_spent_current_number_of_incidents = self.env.now - self.final_statistics['last_number_of_incidents_update_time']
                        self.final_statistics['last_number_of_incidents_update_time'] = self.env.now
                        self.final_statistics['time_spent_per_current_number_of_incidents'][self.num_incidents_active] += time_spent_current_number_of_incidents
                        self.num_incidents_active -= 1
                        self.graph.edges[e_id].active_incidents[incident.edge_incident_id] = False
        else:
            # Normal use case of incident duration where tow truck assistance does not happen.
            yield self.env.timeout(incident.duration)
            sim_log('DEBUG', self.env, e_id, ':Incident ' + str(incident.incident_id) + ' ending at point ' + str(round(incident.location, 3)) + " (couldn't be helped by a tow truck) (NO TOW TRUCK ASSISTANCE POSSIBLE)")

            # Handle removing incident from graph
            time_spent_current_number_of_incidents = self.env.now - self.final_statistics['last_number_of_incidents_update_time']
            self.final_statistics['last_number_of_incidents_update_time'] = self.env.now
            self.final_statistics['time_spent_per_current_number_of_incidents'][self.num_incidents_active] += time_spent_current_number_of_incidents
            self.num_incidents_active -= 1
            self.graph.edges[e_id].active_incidents[incident.edge_incident_id] = False

    def perform_final_processing(self):
        # Calculating average number of incidents based on weights given by time spent with each number of incidents
        weighted_sum = 0
        for i in range(len(self.final_statistics['time_spent_per_current_number_of_incidents'])):
            weighted_sum += i * self.final_statistics['time_spent_per_current_number_of_incidents'][i]
        temp_sum =sum(self.final_statistics['time_spent_per_current_number_of_incidents'])
        if temp_sum != 0:
            weighted_average = weighted_sum / temp_sum
        else:
            weighted_average = 0
        self.final_statistics['average_number_of_incidents'] = weighted_average

        # self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'] = []
        # self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'] = []
        #
        weighted_sum = 0
        if sum(self.final_statistics['time_spent_delayed_per_current_number_of_route_cars']) != 0:
            # logging.info('Route-car probabilities-' +str(self.final_statistics['time_spent_delayed_per_current_number_of_route_cars']))
            for i in range(len(self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'])):
                weighted_sum += i * self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'][i]
            weighted_average = weighted_sum / sum(self.final_statistics['time_spent_delayed_per_current_number_of_route_cars'])
            self.final_statistics['average_time_of_delay_of_route_cars'] = weighted_average
        else:
            # print('Found no route car delays')
            self.final_statistics['average_time_of_delay_of_route_cars'] = 0

        weighted_sum = 0
        # print()
        if sum(self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars']) != 0:
            # logging.info('Ghost-car probabilities-' + str(self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars']))
            for i in range(len(self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'])):
                weighted_sum += i * self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'][i]
            weighted_average = weighted_sum / sum(self.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'])
            self.final_statistics['average_time_of_delay_of_ghost_cars'] = weighted_average
        else:
            # print('Found no ghost car delays')
            self.final_statistics['average_time_of_delay_of_ghost_cars'] = 0

        weighted_sum = 0
        # print()
        if sum(self.final_statistics['time_spent_delayed_per_current_number_of_all_cars']) != 0:
            logging.info('All-car probabilities-' + str(self.final_statistics['time_spent_delayed_per_current_number_of_all_cars']))
            for i in range(len(self.final_statistics['time_spent_delayed_per_current_number_of_all_cars'])):
                weighted_sum += i * self.final_statistics['time_spent_delayed_per_current_number_of_all_cars'][i]
            weighted_average = weighted_sum / sum(self.final_statistics['time_spent_delayed_per_current_number_of_all_cars'])
            self.final_statistics['average_time_of_delay_of_all_cars'] = weighted_average
        else:
            # print('Found no all car delays')
            self.final_statistics['average_time_of_delay_of_all_cars'] = 0

        # self.final_statistics['time_spent_delayed_per_current_number_of_all_cars'] = []


def sim_log(level, env, edge_id, msg):
    if level is 'DEBUG':
        logging.debug(str(round(env.now, 3)) + ':\t\t' + str(edge_id) + ' ' + msg)
    elif level is 'INFO':
        logging.info(str(round(env.now, 3)) + ':\t\t' + str(edge_id) + ' ' + msg)


def incident_occurrence(env, system, edge_id):
    while True:
        yield env.timeout(system.incident_arrival_dist.rvs())
        edge_incident_id = len(system.graph.edges[edge_id].incidents)
        incident_id = system.num_incidents_overall
        time_spent_current_number_of_incidents = env.now - system.final_statistics['last_number_of_incidents_update_time']
        system.final_statistics['last_number_of_incidents_update_time'] = env.now
        system.final_statistics['time_spent_per_current_number_of_incidents'][system.num_incidents_active] += time_spent_current_number_of_incidents
        system.num_incidents_overall += 1
        system.num_incidents_active += 1
        location = random.random()
        original_duration = system.incident_duration_dist.rvs()
        # Getting negative values, must handle
        while original_duration < 0:
            original_duration = system.incident_duration_dist.rvs()
        incident = Incident(incident_id, edge_incident_id, edge_id, location, original_duration, env.now)
        env.process(system.incident_handler(incident, edge_id))


def route_car_arrival(env, system):
    while True:
        yield env.timeout(system.car_arrival_rate_distribution.rvs())
        car_id = system.num_route_cars_overall
        system.num_route_cars_overall += 1
        system.num_route_cars_current += 1
        env.process(system.travel_route(car_id))


# Producer function for ghost cars per edge
def ghost_car_arrival(env, system, e_id):
    while True:
        yield env.timeout(system.car_arrival_rate_distribution.rvs())
        ghost_car_id = system.num_ghost_cars_overall
        system.num_ghost_cars_overall += 1
        system.num_ghost_cars_current += 1
        env.process(system.travel_one_link(e_id, ghost_car_id))


def warm_up_reset(env, system, warmup_time):
    yield env.timeout(warmup_time)
    # print(system.final_statistics['time_spent_per_current_number_of_incidents'])
    # Resetting all possible final statistics to a value that doesn't spark joy
    # system.num_ghost_cars_current = 0
    system.num_ghost_cars_overall = 0
    # system.num_route_cars_current = 0
    system.num_route_cars_overall = 0
    # system.num_incidents_active = 0
    system.num_incidents_overall = 0
    # system.final_statistics = dict()
    system.final_statistics['time_spent_per_current_number_of_incidents'] = [0 for i in range(150)]  # Assuming 150 incidents at most at a time.
    system.final_statistics['last_number_of_incidents_update_time'] = env.now
    # Q1 - Part 2, 3
    system.final_statistics['route_travel_times'] = []
    system.final_statistics['route_delay_times'] = []
    system.final_statistics['route_number_delays'] = []
    system.final_statistics['ghost_delay_times'] = []
    system.final_statistics['ghost_number_delays'] = []
    # Q2
    system.final_statistics['time_spent_delayed_per_current_number_of_route_cars'] = [0 for i in range(system.final_statistics['number_of_currently_delayed_route_cars'] + 2)]
    system.final_statistics['last_number_of_delayed_route_cars_update_time'] = env.now
    system.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'] = [0 for i in range(system.final_statistics['number_of_currently_delayed_ghost_cars'] + 2)]
    system.final_statistics['last_number_of_delayed_ghost_cars_update_time'] = env.now
    system.final_statistics['time_spent_delayed_per_current_number_of_all_cars'] = [0 for i in range(system.final_statistics['number_of_currently_delayed_all_cars'] + 2)]
    system.final_statistics['last_number_of_delayed_all_cars_update_time'] = env.now
    # print(system.final_statistics['time_spent_per_current_number_of_incidents'])
    # system.final_statistics['time_spent_delayed_per_current_number_of_all_cars'] = []
    # system.final_statistics['number_of_currently_delayed_route_cars'] = 0
    # system.final_statistics['number_of_currently_delayed_ghost_cars'] = 0


def get_system_statistics(env, system, rate=100):
    # system.time_statistics['number_of_ghost_cars_at_time'] = []
    # system.time_statistics['number_of_route_cars_at_time'] = []
    # system.time_statistics['number_of_current_incidents'] = []
    # system.time_statistics['time'] = []
    while True:
        yield env.timeout(rate)
        logging.info('Currently at time - ' + str(env.now))
        # system.time_statistics['number_of_ghost_cars_at_time'].append(system.num_ghost_cars_current)
        # system.time_statistics['number_of_route_cars_at_time'].append(system.num_route_cars_current)
        # system.time_statistics['number_of_current_incidents'].append(system.num_incidents_active)
        # system.time_statistics['time'].append(env.now)


def run_simulation(simulation_id, seed, end_time, stats_step_size=100, graph_type='Toy', tow_truck_mode=False, warm_up=0, number_of_tow_trucks=None):
    random.seed(seed)
    rate_of_stats = stats_step_size

    env = simpy.Environment()

    if graph_type is 'Toy1':
        graph, route_path = build_toy_graph()
    elif graph_type is 'Toy2':
        graph, route_path = build_toy_graphs_meaner_big_brother()
        tow_truck_center_id = 2
        if number_of_tow_trucks is None:
            num_tow_trucks = 10
        else:
            num_tow_trucks = number_of_tow_trucks
    elif graph_type is 'Highway':
        graph, route_path = build_highway_graph()
        tow_truck_center_id = 17
        if number_of_tow_trucks is None:
            num_tow_trucks = 16
        else:
            num_tow_trucks = number_of_tow_trucks

    bfs_graph = build_bfs_graph(graph)
    preprocessed_routes = compute_optimal_paths_from_center(graph, bfs_graph, tow_truck_center_id)

    system = HighwaySystem(env, graph, bfs_graph, route_path, num_tow_trucks, tow_truck_center_id, preprocessed_routes, tow_truck_mode, seed=seed, warm_up=warm_up)

    logging.debug('Index: Edge')
    for edge_id, edge in enumerate(system.graph.edges):
        # logging.info(str(edge_id) + ':\t' + str(edge))
        # if edge_id not in route_path:
        #     env.process(ghost_car_arrival(env, system, edge_id))
        env.process(incident_occurrence(env, system, edge_id))
    # env.process(route_car_arrival(env, system))
    env.process(get_system_statistics(env, system, rate_of_stats))
    env.process(warm_up_reset(env, system, warm_up))
    logging.info('===========')
    start_time = time.time()
    logging.info('Simulation '+str(simulation_id) + ' starts')

    env.run(until=end_time)
    system.perform_final_processing()

    logging.info('Simulation '+str(simulation_id) + ' ends, taking time ' + str(time.time() - start_time))

    logging.info('---------------')
    # logging.info('Simulation '+str(simulation_id) + ' final statistics')
    # for key, value in enumerate(system.final_statistics):
    #     logging.info(str(value) + ':' + str(system.final_statistics[value]))

    # logging.info('Simulation '+str(simulation_id) + ' time statistics')
    # for key, value in enumerate(system.time_statistics):
    #     logging.info(str(value) + ':' + str(system.time_statistics[value]))
    logging.info('---------------')
    # Must print out only relevant statistics

    logging.info('maximum number of route cars delayed at a time-' + str(len(system.final_statistics['time_spent_delayed_per_current_number_of_route_cars'])))
    logging.info('maximum number of ghost cars delayed at a time-' + str(len(system.final_statistics['time_spent_delayed_per_current_number_of_ghost_cars'])))
    logging.info('maximum number of all cars delayed at a time-' + str(len(system.final_statistics['time_spent_delayed_per_current_number_of_all_cars'])))
    logging.info('average number of ghost cars delayed-' + str(system.final_statistics['average_time_of_delay_of_ghost_cars']))
    logging.info('average number of route cars delayed-' + str(system.final_statistics['average_time_of_delay_of_route_cars']))
    logging.info('average number of all cars delayed-' + str(system.final_statistics['average_time_of_delay_of_all_cars']))

    # for i in system_stats_over_time:
    #     logging.info(i)
    logging.info('system.final_statistics[time_spent_per_current_number_of_incidents] : ' + str(system.final_statistics['time_spent_per_current_number_of_incidents']))
    logging.info('sum of times:' + str(sum(system.final_statistics['time_spent_per_current_number_of_incidents'])))
    logging.info('average number of incidents' + str(system.final_statistics['average_number_of_incidents']))
    # weighted_sum = 0
    # for i in range(len(system.final_statistics['time_spent_per_current_number_of_incidents'])):
    #     weighted_sum += i*system.final_statistics['time_spent_per_current_number_of_incidents'][i]
    # logging.info('weighted_sum: '+ str(weighted_sum))

    # print(system.final_statistics['time_spent_per_current_number_of_incidents'])
    # logging.info('weighted_average')
    # logging.info(weighted_sum/sum(system.final_statistics['time_spent_per_current_number_of_incidents']))
    return system







