# -*- coding: utf-8 -*-
"""
Author: Pranay Thangeda
Email: contact@prny.me
"""

import uuid
import dataprocessing as dp


# Route class
class Route:

    def __init__(self, name, nodelist, starttimes):
        self.name = name
        self.nodes = nodelist
        self.nodesloc = None
        self.list_starttimes = starttimes
        self.node_initial = nodelist[0]
        self.node_terminal = nodelist[-1]
        self.transferstops = None
        self.meantimes = None


    def load_meantimes(self, model):
        """
        Load the expected value of travel times on all the edges in the
        route
        """
        meantimes = []
        for pair in zip(self.nodes[:-1], self.nodes[1:]):
            meantimes.append(model.mean[(pair[0],pair[1])])
        self.meantimes = meantimes


    def load_nodelocations(self, G):
        """
        Extracts the latitude and longitude data of every stop
        """
        loclist = []
        for node in self.nodes:
            loclist.append((G.node[node]['stop_lat'], G.node[node]['stop_lon']))
        self.nodesloc = tuple(loclist)

    def load_transferstops(self, routes_dict):
        """
        Takes a route object and dictionary of all routes as inputs and generates
        all transfer states of the route
        """
        transferstops = set()
        nodelist1 = self.nodes
        for routename, nodelist2 in routes_dict.items():
            if routename != self.name:
                commonnodes = set(nodelist1).intersection(nodelist2)
                indices_common = sorted([nodelist1.index(x) for x in commonnodes])
                indices_transferstops = []
                if len(indices_common) != 0:
                    indices_transferstops = [x  for x, y in zip(indices_common[:-1], indices_common[1:]) if x + 1 < y]
                    indices_transferstops.append(indices_common[-1])
                    transferstops.update([nodelist1[x] for x in indices_transferstops])
        self.transferstops = tuple(transferstops)


    def initialize(self, route_dict):
        pass


# Trip class
class Trip:

    def __init__(self, start_time, route):
        self.start_time = start_time
        self.route = route
        self.history = None
        self.lastnode = self.route.node_initial
        self.elapsedtime = 0

# Traveler class
class Trav:

    def __init__(self, origin, destination, time_budget, alpha, start_time):
        self.t_start = start_time
        self.node_origin = origin
        self.node_dest = destination
        self.t_budget = time_budget
        self.alpha = alpha
        self.node_current = self.node_origin

# Extract service day details for running simulation



def simulate(t_begin, t_end, t_step, travelers_list, routes_list):
"""
Function that simulates the trip routing and optimal planning in the transit network
"""
    t = t_begin

    while t <= t_end:

       # Calculate the least expected time from a given node to dest
    def optimal_choice(G, traveler, routes_list, alpha, t_budget):
        """Finds the optimal path from start node to
        end node based on the both the objectives
        """

        # LET Cost
        costs = dict()
        for trip in trip_yta:
            index = trip['route'].index(trip['current_node'])
            nodelist = trip['route'][index:]

            cost = 0
            path = list(zip(nodelist[:-1], nodelist[1:]))
            for pair in path:
                dist = G[pair[0]][pair[1]][0]['traveltime']
                for option in dist:
                    cost += option[0]*option[1]

            costs.update({trip['name']: {'let': cost}})

        # Reliability - Prob of ontime arrival
        for trip in trip_yta:

            # identify trip location
            for i in range(len(time_values)-1):
                if time_budget < time_values[0]:
                    reli = 0
                elif time_budget > time_values[3]:
                     print('Time budget high. All paths are highly reliable')
                     reli = 1
                else:
                    if time_values[i] <= time_budget < time_values[i+1]:
                        index = i
                        break

            # Store data
            costs[trip['name']]['reli'] = reli

        # Balance reliability and least expected travel time
        max_let = 0
        for route in routes_list:
            if costs[route]['let'] > max_let:
                max_let = costs[route]['let']

        for trip in active_trips:
           combined_cost = alpha*costs[trip]['let']/max_let - (1 - alpha)*costs[trip]['reli'])
           costs[trip]['total_cost']  = combined_cost

        # Selecting trip with max total_cost
        key_max = max(costs.keys(), key=(lambda k: costs[k]['total_cost']))
        for trips in trip_yta:
            if trip['name'] == key_max:
                out_trip = trip

        return out_trip

    # Sample edge travel time from the given ditribution
    def sample_edgetime(G, trip):
        current_node = trip['current_node']

        try:
            next_node = trip['route'][trip['route'].index(current_node)+1]
        except IndexError:
            raise Exception('There is no next node. Check sample_edgetime')

        traveltime_dist = G[current_node][next_node][0]['traveltime']

        # random selection
        flip = random.random()
        prob = 0
        for pair in traveltime_dist:
            prob += pair[1]
            if flip <= prob:
                tt_sample = pair[0]
                break

        return (tt_sample, next_node)

    # Initialize for trip route simulation
    agent_route = []
    agent_cnode = start
    agent_pnode = start
    sim_time = 0
    run_status = True

    while True:

        # ------------- tripes running simulation segment -------------------

        for trip in active_trips:

            # First time step travel time
            if sim_time == 0:
                (time_nextedge, next_node) = sample_edgetime(G, trip)
                trip['next_node'] = next_node
                trip['arrival_time'].update({next_node: trip['arrival_time'][trip['current_node']] + time_nextedge})

            # loop for every time step till all tripes reach dest
            if trip['arrival_time'][trip['next_node']] == sim_time:

                # Update time on previous edge and current node
                G[trip['current_node']][trip['next_node']][0]['traveltime'] = [(trip['arrival_time'][trip['next_node']] - trip['arrival_time'][trip['current_node']], 1)]
                trip['current_node'] = trip['next_node']

                # Sample time for edge next_node -> node after that, if exists
                if trip['current_node'] != dest:
                    (time_nextedge, nextnext_node) = sample_edgetime(G, trip)

                    # Update next node
                    trip['next_node'] = nextnext_node
                    trip['arrival_time'].update({trip['next_node']: trip['arrival_time'][trip['current_node']] + time_nextedge})

        # Break condition
        for trip in trips_list:
            if trip['current_node']:
                print('All tripes reached the destination.')
                break

        # ------------ Agent Decision Making and Routing Segment -------------

        # Decision step - new decision if start or exchange node
        if G.node[agent_cnode]['code'] in {3, 4}:

            # Possible options at current exchange point
            trip_yta = []  # list of tripes yta at agent_cnode
            for trip in [red, blue]:
                if agent_cnode in trip['route']:
                    if trip['route'].index(trip['current_node']) <= trip['route'].index(agent_cnode):
                        trip_yta.append(trip)

            # If all other tripes already left
            if len(trip_yta) == 1:
                agent_trip = trip_yta[0]

            # If more than one possible tripes
            else:
                agent_trip = optimal_choice(G, trip_yta, agent_cnode,
                                          agent_route, alpha, time_budget)

                if agent_cnode not in agent_trip['route']:
                    raise Exception('Optimal route does not go through current node of agent. Check optimal_choice again.')

            if agent_trip['current_node'] == agent_cnode:
                # Storing route data once action is taken
                agent_pnode = agent_cnode
                agent_cnode = agent_trip['next_node']
                agent_route.append((agent_pnode, agent_cnode, agent_trip['arrival_time'][agent_trip['next_node']] - agent_trip['arrival_time'][agent_trip['current_node']], agent_trip['name']))

        # If destination reached
        elif G.node[agent_cnode]['code'] == 2:
            if run_status:
                print('Agent reached destination.')
                run_status = False

        # Non exchange points - Following predecided optimal routes
        else:

            # Route and time saving step
            if agent_trip['current_node'] == agent_cnode:

                # Store data then update current and next states
                agent_pnode = agent_cnode
                agent_cnode = agent_trip['next_node']
                agent_route.append((agent_pnode, agent_cnode, agent_trip['arrival_time'][agent_trip['next_node']] - agent_trip['arrival_time'][agent_trip['current_node']], agent_trip['name']))

        # Update while loop simualtion time
        sim_time += 1

    return G, red, blue, agent_route

    t += t_step





