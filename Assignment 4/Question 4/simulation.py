# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 16:17:00 2020

@author: s159774
"""

from scipy import stats
from collections import deque
from class_Event import Event
from class_FES import FES
from class_Car import Car
from class_Edge import Edge
from class_TrafficJam import TrafficJam
from util import *
import random
from numpy import std
import matplotlib.pyplot as plt
import numpy as np

    
class Simulation:
    
    def __init__(self, carInterarrival, warmupTime):
        # graph, route_path = build_toy_graph()
        graph, route_path = build_highway_graph()
        
        #print(graph)
        #print('Route_Path')
        #for i in route_path:
        #    print(i)
        #print('-------')
        
        self.graph = graph
        self.route_path = route_path
        self.carInterarrival = carInterarrival
        self.warmupTime = warmupTime
        
        # KPI set-up
        self.delayed_veh = dict() # KPI 2
        self.jams = dict() # KPI 3
        self.travel_time_regular_car = dict() # Key = duration, Value is amount occured
        self.jam_time_regular_car = dict() # Key = duration, Value is amount occured
        self.amount_of_jams_regular_car = dict()

        # Time recordings
        self.last_jam_record_t = 0
        self.last_delayed_veh_record_t = 0
        self.last_arr_regular_car_t = 0
        
    def record(self, dictionary, value, added_time): # Helper function
        if (value) in dictionary.keys():
            dictionary[(value)] += added_time
        else:
            dictionary[(value)] = added_time
        return dictionary
    
    def record_delayed_veh(self, time):
        if(time <= self.warmupTime):
            return
        
        time = time - self.warmupTime
        
        delayed_veh = 0 # counts number of delayed vehicles at time t
        for edge in self.graph.edges:
            if(edge.hasJam()):
                jam = edge.jam
                delayed_veh += jam.getQueueLength()
            
        # Now add to dictionary
        self.delayed_veh = self.record(self.delayed_veh, delayed_veh, time - self.last_delayed_veh_record_t)
        self.last_delayed_veh_record_t = time
        
    def record_jams(self, time):
        if(time <= self.warmupTime):
            return
        
        time = time - self.warmupTime
        no_jams = 0
        for edge in self.graph.edges:
            if(edge.hasJam()):
                no_jams += 1
        self.jams = self.record(self.jams, no_jams, time - self.last_jam_record_t)
        self.last_jam_record_t = time

    def record_arr_regular_car(self, car, time):
        if(time <= self.warmupTime):
            return
        
        time = time - self.warmupTime
        duration = car.arrivalTime - car.departureTime
        if(duration <= 0):
            print("Warning Car is arrived without travel time")
            
        # Now add 1 to the duration
        duration = round(duration)
        if (duration) in self.travel_time_regular_car.keys():
            self.travel_time_regular_car[(duration)] += 1
        else:
            self.travel_time_regular_car[(duration)] = 1
        
        time_in_jam = 0
        for traffic_jam_times in car.traffic_jams: # This instance is NOT a traffic jam
            jam_duration = traffic_jam_times['end'] - traffic_jam_times['start']
            if(traffic_jam_times['end'] <= 0):
                print("WARNING: Car has no traffic jam end")
            if(jam_duration <= 0):
                print("WARNING: The duration of the traffic jam is smaller than 0.")
            time_in_jam += jam_duration
        
        time_in_jam = round(time_in_jam)
        if(time_in_jam >= duration):
            print("WARNING: Car is only in a jam!")

        # Now add 1 to the duration
        if (time_in_jam) in self.jam_time_regular_car.keys():
            self.jam_time_regular_car[(time_in_jam)] += 1
        else:
            self.jam_time_regular_car[(time_in_jam)] = 1
            
        # Add the amount of jams
        jam_amount = len(car.traffic_jams)
        if jam_amount in self.amount_of_jams_regular_car.keys():
            self.amount_of_jams_regular_car[(jam_amount)] += 1
        else:
            self.amount_of_jams_regular_car[(jam_amount)] = 1
            
        self.last_arr_regular_car_t = time
        
    def simulate(self, timelim):
        # -- Initialize variables
        t = 0
        fes = FES()
        edges = self.graph.edges
        
        # -- Set start of simulation
        self.all_traffic_jams = []
        self.events_per_t = dict() # TEMP
        
        # Now create a regular car 
        route = []
        for edge in self.route_path: # Route path contains the integers of the edge in edges list.
            route.append(edges[edge]) # Do the conversion
            
        # Create Ghost Cars and Traffic Jams
        for edge in edges:
            
            # Set a traffic jam on each edge at a specific time
            jam = edge.getNextJam(0)
            fes.add(Event(jam.startTime, jam, "TrafficJamStart"))
            
            # Set a ghost car on each edge
            if(edge not in route):
                nextCar = Car(True, [edge]) # Only route is one edge
                fes.add(Event(self.carInterarrival.rvs(), nextCar, "CarDepature"))


        regularCar = Car(False, route)
        fes.add(Event(self.carInterarrival.rvs(), regularCar, "CarDepature"))
        
        firstRecord = False
        # -- Start real simulation
        while t < timelim + self.warmupTime:
            e = fes.next() # next event
            obj = e.obj
            time = e.time
                
            if(not firstRecord and t > self.warmupTime):
                self.record_delayed_veh(time) 
                firstRecord = True
            # Car arrives at node
            if e.eventtype == "CarArrival":
                if(not obj.isGhost): 
                    if(not obj.isAtDestination()): # If Car is not at destination, then see it as a new depature
                        e.eventtype = "CarDepature"
                    else:
                        obj.destinationArrival(time)
                        self.record_arr_regular_car(obj, time)
                        
             # Car departs from Node
            if e.eventtype == "CarDepature": # Car leaving from an edge (start travel)
                if(obj.newInstance):
                    nextCar = Car(obj.isGhost, obj.route.copy())
                    fes.add(Event(time+self.carInterarrival.rvs(), nextCar, "CarDepature")) # Do the interarrival rate
                nextEdge = obj.nextTravel(time)
                if(nextEdge.hasJam()):
                    time_to_jam = nextEdge.jam.location_on_edge * obj.edge_travel_time
                    fes.add(Event(time + time_to_jam, obj, "CarArrivalJam")) # Car entering an edge
                else:
                    if(not obj.isGhost): # Only regular cars have to have an arrival in this case.
                        fes.add(Event(time+obj.edge_travel_time, obj, "CarArrival")) # Car entering an edge

            # Traffic Jam occurs
            if e.eventtype == "TrafficJamStart":
                if(obj.edge.hasJam()): # Prevent creating a new jam when thhe old one is not resolved.
                    #print("WARNING: A Jam was attempted to be created before te old one was ended.")
                    t = ''
                else:
                    self.record_jams(time)
                    obj.edge.startJam(obj)
                    fes.add(Event(obj.endTime, obj, "TrafficJamEnd"))
                newJam = obj.edge.getNextJam(time)
                fes.add(Event(newJam.startTime, newJam, "TrafficJamStart"))
                
            # Traffic Jam resolves
            if e.eventtype == "TrafficJamEnd":
                if(obj.getQueueLength() > 0):
                    leavingCar = obj.getLeavingCar()
                    obj = leavingCar
                    e.eventtype = "CarDepatureJam"
                else:
                    self.record_jams(time)
                    obj.edge.endJam()
                    
            # Car arrival at Jam
            if e.eventtype == "CarArrivalJam": # Car arriving at a Jam
                if(obj.current_edge.hasJam()): # Check if Jam has been resolved
                    self.record_delayed_veh(time) 
                    trafficJam = obj.current_edge.jam
                    trafficJam.addCar(obj)
                    obj.addTrafficJam(time) # Monitor car in traffic jam
                else:
                    fes.add(Event(obj.edge_depature_time + obj.edge_travel_time, obj, "CarArrival"))
                
            # Car departs from Jam
            if e.eventtype == "CarDepatureJam": # Car leaving from a jam
                trafficJam = obj.current_edge.jam
                trafficJam.removeCar(obj)
                time_in_jam = obj.endTrafficJam(time)
                if(not obj.isGhost):
                    fes.add(Event(obj.edge_depature_time+obj.edge_travel_time+time_in_jam, obj, "CarArrival"))
                if(trafficJam.getQueueLength() > 0):
                    self.record_delayed_veh(time)
                    leavingCar = trafficJam.getLeavingCar()
                    processingTime = trafficJam.getProcessingTime()
                    fes.add(Event(time+processingTime, leavingCar, "CarDepatureJam"))
                else:
                    self.record_jams(time)
                    trafficJam.edge.endJam() # Remove the Jam from the edge
            
            t = time
            
        # Monitor the last things
        self.record_delayed_veh(time)
        self.record_jams(time)
        
        print("Total simulation time:" + str(t))                          
        return (self.delayed_veh, self.jams)



carInterarrivalRate = stats.expon(loc = 0, scale = 1/4) # scale is .25 corresponds to 4 cars per minutes on avg.
sim = Simulation(carInterarrivalRate, 100)
res = sim.simulate(1440) 

""" FOR KPI 1 (distribution of travel time, mean std histogram).
- Information is stored in Car objects
- Indicate which part of the travel time is caused by the delay (realised travel time - initial travel time)
- Loop through all regular cars and store needed info in lists
"""
""" FOR KPI 2 (distribution of number of delayed vehicles at any arbitrary epoch)
- number of delayed vehicles = sum of all cars in the queues (loop through the queues of the jams)
- store the time that k vehicles were delayed after each event (only for car events)  (list or dict)
"""
"""FOR KPI 3 (distribution of the number of incidents in the whole network)
- use len(all_traffic_jams) for the number of incidents
- store time of k incidents at the end of each event (only for jam events) (list or dictionary)
"""


# --- MEASURE 1 ---
# -- TRAVEL TIME -- 
def get_measure_1(sim):
    print("MEASURE 1")
    print("Distribution of travel times")
    x = []
    y = [] 
    sorted_travel_times = {k: v for k, v in sorted(sim.travel_time_regular_car.items(), key=lambda item: item[0])}
    for (key, amount) in sorted_travel_times.items():
        x.append(key)
        y.append(amount)
    y = [i / sum(y) for i in y]
    plt.plot(x, y, label = "Total Travel Time")
    plt.xlabel("Minutes")
    plt.ylabel("Probability")
    plt.show()
    
    all_travel_times = []
    for (key, amount) in sorted_travel_times.items():
        for i in range(0, amount):
            all_travel_times.append(key)
    
    avg_travel_time = sum(all_travel_times) / len(all_travel_times)
    print("Average travel time:" + str(avg_travel_time))
    print("Standard deviation:" + str(np.std(all_travel_times)))
    
    # -- JAM TIME --
    print("Distribution of jam times")
    sorted_travel_times = {k: v for k, v in sorted(sim.jam_time_regular_car.items(), key=lambda item: item[0])}
    x = []
    y = []
    for (key, amount) in sorted_travel_times.items():
        x.append(key)
        y.append(amount)
    x = x[1:]
    y = y[1:]
    y = [i / sum(y) for i in y]
    plt.plot(x, y, label = "Time in Jam")
    plt.title("Time in jam given that there is a jam")
    plt.xlabel("Minutes")
    plt.ylabel("Probability")
    plt.show()
    all_jam_times = []
    for (key, amount) in sorted_travel_times.items():
        for i in range(0, amount):
            all_jam_times.append(key)
    
    avg_jam_time = sum(all_jam_times) / len(all_jam_times)
    print("Average travel time:" + str(avg_jam_time))
    print("Standard deviation:" + str(np.std(all_jam_times)))

    # -- Amount of traffic jams on route --
    print("Number of traffic jams on route")
    sorted_travel_times = {k: v for k, v in sorted(sim.amount_of_jams_regular_car.items(), key=lambda item: item[0])}
    x = []
    y = []
    for (key, amount) in sorted_travel_times.items():
        x.append(key)
        y.append(amount)
    y = [i / sum(y) for i in y]
    plt.bar(x, y, label = "Time in Jam")
    plt.title("Amount of traffic jams on route")
    plt.xlabel("Traffic Jams")
    plt.ylabel("Probability")
    plt.xticks(x, x)
    plt.show()
    all_jam_times = []
    for (key, amount) in sim.amount_of_jams_regular_car.items():
        for i in range(0, amount):
            all_jam_times.append(key)
    
    avg_jam_time = sum(all_jam_times) / len(all_jam_times)
    print("Average travel time:" + str(avg_jam_time))
    print("Standard deviation:" + str(np.std(all_jam_times)))

# --- MEASURE 2 ---
def get_measure_2_old(sim):
    # Number of vehicles in a jam
    x = []
    y = []
    for (key, amount) in sim.delayed_veh.items():
        x.append(key)
        y.append(amount)
    #x = x[1:]
    #y = y[1:]
    y = [i / sum(y) for i in y]
    plt.plot(x, y, label = "Time in Jam")
    plt.xlabel("Number of vehicles in jam")
    plt.ylabel("Fraction of time spent")
get_measure_2_old(sim)

def get_measure_2(sim):
    # Number of vehicles in a jam
    x = []
    y = []
    first = ''
    sorted_delays = {k: v for k, v in sorted(sim.delayed_veh.items(), key=lambda item: item[0])}
    for (key, amount) in sorted_delays.items():
        group = int(key // 1000)
        if(first == ''):
            first = group
        if(len(x) == group - first):
            print(group)
            print('first')
            x.append(group * 1000)
            y.append(amount)
        else:
            y[group - first - 1] += amount

    y = [i / sum(y) for i in y]
    plt.bar(x, y, width=500)
    plt.xticks(x, x)
    plt.xlabel("Number of vehicles in jam")
    plt.ylabel("Fraction of time spent")
    plt.plot()
get_measure_2(sim)

def get_measure_3(sim):
    # --- MEASURE 3 --- 
    x = []
    y = []
    sorted_jams = {k: v for k, v in sorted(sim.jams.items(), key=lambda item: item[0])}
    for (key, amount) in sorted_jams.items():
        x.append(key)
        y.append(amount)
    y = [i / sum(y) for i in y]
    plt.bar(x, y, label = "Time in Jam")
    plt.xlabel("Amount of jams")
    plt.ylabel("Time spent")
