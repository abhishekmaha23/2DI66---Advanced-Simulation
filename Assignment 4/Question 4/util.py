import csv
import random
from collections import deque
from random import Random
from class_Edge import Edge

assignment_source_A = 'DenBosch'
assignment_target_B = 'Rotterdam'

city_ids = dict()
# city_ids
city_ids['DenHaag'] = 1
city_ids['Utrecht'] = 2
city_ids['Rotterdam'] = 3
city_ids['DenBosch'] = 4
city_ids['Breda'] = 5
city_ids['Tilburg'] = 6
city_ids['Eindhoven'] = 7
city_ids['PrinsClausplein'] = 8
city_ids['Gouwe'] = 9
city_ids['Ouderijn'] = 10
city_ids['Lunetten'] = 11
city_ids['Kethelplein'] = 12
city_ids['Terbregseplein'] = 13
city_ids['Benelux'] = 14
city_ids['Vaanplein'] = 15
city_ids['Ridderkerk'] = 16
city_ids['Gorinchem'] = 17
city_ids['Everdingen'] = 18
city_ids['Deil'] = 19
city_ids['Sabina'] = 20
city_ids['Noordhoek'] = 21
city_ids['Klaverpolder'] = 22
city_ids['Zonzeel'] = 23
city_ids['Hooipolder'] = 24
city_ids['Empel'] = 25
city_ids['Hintham'] = 26
city_ids['Zoomland'] = 27
city_ids['DeStok'] = 28
city_ids['Princeville'] = 29
city_ids['StAnnabosch'] = 30
city_ids['Batadorp'] = 31
city_ids['Ekkersweijer'] = 32
city_names = ['', 'DenHaag', 'Utrecht', 'Rotterdam', 'DenBosch', 'Breda', 'Tilburg', 'Eindhoven', 'PrinsClausplein',
              'Gouwe', 'Ouderijn', 'Lunetten', 'Ketherplein', 'Terbregselplein', 'Benelux', 'Vaanplein', 'Riddenkerk',
              'Gorinchem', 'Everdingen', 'Deil', 'Sabina', 'Noordhoek', 'Klaverpolder', 'Zonzeel', 'Hooipolder',
              'Empel', 'Hintham', 'Zoomland', 'DeStok', 'Princeville', 'StAnnabosch', 'Batadorp', 'Ekkersweijer']


def build_toy_graph():
    graph = SystemGraph()
    # print('---')
    graph.nodes.add(Node(1, 'A'))
    graph.nodes.add(Node(2, 'B'))
    graph.nodes.add(Node(3, 'C'))
    route_edge_a = Edge(1, 2, TravelTimeDistribution('Linear', 5))
    route_edge_b = Edge(2, 3, TravelTimeDistribution('Linear', 4))
    graph.edges.append(route_edge_a)
    graph.edges.append(route_edge_b)
    # graph.edges = list(graph.edges)
    # route_path = [route_edge_a, route_edge_b]
    route_path = [0, 1]
    # print(route_path)
    # graph.edges.add(Edge(1, 2, TravelTimeDistribution('Uniform', 4, 8)))
    # graph.edges.add(Edge(2, 3, TravelTimeDistribution('Uniform', 4, 8)))
    # print('----')
    return graph, route_path

def build_toy_graphs_meaner_big_brother():
    graph = SystemGraph()
    # print('---')
    graph.nodes.add(Node(1, 'A'))
    graph.nodes.add(Node(2, 'B'))
    graph.nodes.add(Node(3, 'C'))
    graph.nodes.add(Node(4, 'D'))
    graph.edges.append(Edge(1, 2, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(2, 3, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(3, 4, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(4, 1, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(2, 1, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(3, 2, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(4, 3, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(1, 4, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(1, 3, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(3, 1, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(2, 4, TravelTimeDistribution('Uniform', 4, 8)))
    graph.edges.append(Edge(4, 2, TravelTimeDistribution('Uniform', 4, 8)))
    # graph.edges.append(route_edge_a)
    # graph.edges.append(route_edge_b)
    # graph.edges = list(graph.edges)
    # route_path = [route_edge_a, route_edge_b]
    route_path = [0, 1, 2]
    # print(route_path)
    # graph.edges.add(Edge(1, 2, TravelTimeDistribution('Uniform', 4, 8)))
    # graph.edges.add(Edge(2, 3, TravelTimeDistribution('Uniform', 4, 8)))
    # print('----')
    return graph, route_path

# 3 nodes
# 2 edges
# Ghost cars between A-B and B-C
# Route cars between A-B-C


def build_highway_graph():
    with open('travel_times_links_maps.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        graph = SystemGraph()
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')

                source_name = row[0].replace(" ", "").replace(".", "")
                target_name = row[1].replace(" ", "").replace(".", "")
                graph.edges.append(Edge(city_ids[source_name], city_ids[target_name],
                                     TravelTimeDistribution('Uniform', int(row[2]), int(row[3]))))
                graph.nodes.add(Node(city_ids[source_name], source_name))
                # print(line_count, city_ids[source_name], '->', city_ids[target_name], '=', row[2], 'to', row[3])
                line_count += 1

        # graph.edges = list(graph.edges)
        # print('Number of edges', len(graph.edges))
        # print('Number of nodes', len(graph.nodes))
        # print(graph)

        # Route Path is the set of the following edges - [Den Bosch - Empel - Deil - Gorinchem - Riddenkerk - Rotterdam]
        route_path = [94, 68, 29, 25, 81]

        # print(f'Processed {line_count} edges.')
    return graph, route_path

# 32 nodes
# 50 edges with multiple values per item

def build_bfs_graph(graph):

    # Creating BFS Graph with the following structure
    # The graph is a dict. Keys are node IDs. Values are a list of tuples.
    # The list of tuples is the list of all existing edges.
    # The tuple has format (target_id, index_in_edge_list, Edge object)
    # For the BFS, this is enough to ensure that we can track stuff straight from the node ID of the tow truck station.
    edges = graph.edges
    bfsgraph = dict()
    for vertex in graph.nodes:
        bfsgraph[vertex.id] = []
    # print(bfsgraph)
    for index, edge in enumerate(edges):
        # print(index, edge)
        bfsgraph[edge.source_id].append((edge.target_id, index, edge))
    # print(bfsgraph)
    # for i in bfsgraph[2]:
    #     for j in i:
    #         print(j)
    return bfsgraph


def compute_optimal_paths_from_center(graph, bfsgraph, tow_truck_center_id):
    preprocessed_paths = [[] for i in range(len(graph.nodes) + 1)]
    # preprocessed_paths[tow_truck_center_id] = None
    start_node = tow_truck_center_id
    explored_nodes = deque()
    queued_nodes = deque()
    queued_nodes.append(start_node)

    loop = 0
    while len(queued_nodes) > 0:
        loop += 1
        current_node = queued_nodes.popleft()
        path_so_far_to_current_node = preprocessed_paths[current_node]
        target_tuples = bfsgraph[current_node]
        target_ids = []
        target_edge_ids = []
        for target_tuple in target_tuples:
            target_ids.append(target_tuple[0])
            target_edge_ids.append(target_tuple[1])
            if target_tuple[0] not in explored_nodes:
                new_path = path_so_far_to_current_node.copy()
                new_path.append(target_tuple[1])

                if len(preprocessed_paths[target_tuple[0]]) != 0:
                    length_of_current_path = 0
                    length_of_new_path = 0
                    for edge_index in preprocessed_paths[target_tuple[0]]:
                        length_of_current_path += graph.edges[edge_index].travel_time_distribution.average
                    for edge_index in new_path:
                        length_of_new_path += graph.edges[edge_index].travel_time_distribution.average
                    if length_of_current_path > length_of_new_path:
                        preprocessed_paths[target_tuple[0]] = new_path
                    else:
                        pass
                else:
                    preprocessed_paths[target_tuple[0]] = new_path
                queued_nodes.append(target_tuple[0])
        explored_nodes.append(current_node)
    return preprocessed_paths


def arrival_rate_distribution(type, edge_id=999):
    # Allow multiple variations of distributions
    arrival_random = Random(edge_id)
    if type is 'Ghost':
        return arrival_random.uniform(4, 8)
    elif type is 'Route':
        return arrival_random.uniform(3, 6)


def incident_rate_distribution():
    # Allow multiple variations of distribution occurrence
    # return 3.3
    return random.uniform(4, 8)


def incident_duration_distribution():
    # Allow multiple distributions per day of travel
    return random.uniform(15, 30)


class TravelTimeDistribution:
    def __init__(self, type, param_a=0, param_b=0, param_c=0):
        self.type = type
        if self.type is 'Linear':
            self.rate = param_a
            self.average = param_a
        elif self.type is 'Uniform':
            self.average = (param_a+param_b) / 2
            self.maximum = param_a
            self.minimum = param_b

    def rvs(self):
        if self.type is 'Linear':
            return self.rate
        elif self.type is 'Uniform':
            return random.uniform(self.minimum, self.maximum)


class SystemGraph:
    def __init__(self):
        self.edges = []
        self.nodes = set()

    def __str__(self):
        stri = ''
        for i in self.nodes:
            stri += str(i) + '\t'
        stri += '\n'
        for index, edge in enumerate(self.edges):
            stri += str(index) + ' - ' + str(edge) + '\n'
        return stri

class Node:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return str(self.name) + '=' + str(self.id)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name

    def __hash__(self):
        return hash((self.name, self.id))


class Incident:
    def __init__(self, incident_id, edge_incident_id, edge_id, location, duration, start_time, active=True):
        self.incident_id = incident_id
        self.edge_incident_id = edge_incident_id
        self.edge_id = edge_id
        self.location = location
        self.duration = duration

        self.active = active
        self.start_time = start_time

    def __str__(self):
        return 'Incident ' + str(self.incident_id) + ' on Edge ' + str(self.edge_id) + ' at ' + str(self.location) + \
               ' lasting ' + str(self.duration) + ' long, starting at ' + str(self.start_time)
#
# test_graph, route = build_toy_graph()
# test_graph, route = build_toy_graphs_meaner_big_brother()
# # test_graph, route_path = build_highway_graph()
# # print(test_graph)
# bfsgraph = build_bfs_graph(test_graph)
# print(bfsgraph)
# for key, value in enumerate(bfsgraph):
#     print(value, bfsgraph[value])
# #
# # # route_path = [94, 68, 29, 25, 81]
# # # for index in route_path:
# #     # print('Edge_ID->' + str(index))
# #     # print('Edge ->' + str(test_graph.edges[index]))
# #     # print(city_names[test_graph.edges[index].source_id] + '-' + city_names[test_graph.edges[index].target_id])
# #
# preprocessed_shortest_paths = compute_optimal_paths_from_center(test_graph, bfsgraph, 2)
# print(preprocessed_shortest_paths)

# print(route)
# # build_highway_graph()