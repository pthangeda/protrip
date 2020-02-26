# -*- coding: utf-8 -*-
"""
Author: Pranay Thangeda
Email: pranayt2@illinois.edu
Created: Tue Sep 10 20:02:40 2019


"""

# Import required packages
import random
import folium
import osmnx as ox


def busroutes_plot(G, routes_list, impnodes):
    """Plots the bus route and the origin, start and destination points

    Parameters
    ----------
    Self explanatory

    Returns
    -------
    html map file with routes

    """
    # Extract points
    origin = impnodes[0]
    destination = impnodes[1]
    start = impnodes[2]

    # Define and create map with appropriate boundaries
    global_lat = []
    global_lon = []
    c_list = ["red", "blue", "yellow", "magenta", "orange", "white"]
    for route in routes_list:
        for node in route:
            global_lon.append(G.nodes[node]['x'])  # lon
            global_lat.append(G.nodes[node]['y'])  # lat
    min_point = [min(global_lat), min(global_lon)]
    max_point = [max(global_lat), max(global_lon)]
    map_route = folium.Map(zoom_start=1, tiles='cartodbpositron')
    map_route.fit_bounds([min_point, max_point])

    # Add bus routes
    count = 0
    for route in routes_list:
        path = list(zip(route[:-1], route[1:]))
        points = []
        for pair in path:

            if 'geometry' in G.edges[pair[0], pair[1], 0]:
                a = [(lat, lon) for lon, lat in G.edges[pair[0],
                     pair[1], 0]['geometry'].coords]
                points.extend(a)

            else:
                b = [(G.node[pair[0]]['y'], G.node[pair[0]]['x'])]
                c = [(G.node[pair[1]]['y'], G.node[pair[1]]['x'])]
                points.extend(b)
                points.extend(c)

        folium.PolyLine(locations=points, color=c_list[count],
                        weight=6, smooth_factor=2,
                        opacity=0.6).add_to(map_route)
        count += 1

    # Add 0-D-S nodes
    folium.Marker(location=[G.node[origin]['y'], G.node[origin]['x']],
                  popup='Origin',  title='Origin',
                  icon=folium.Icon(color='red')).add_to(map_route)

    folium.Marker(location=[G.node[destination]['y'],
                  G.node[destination]['x']], popup='Destination',
                  title='Destination',
                  icon=folium.Icon(color='green')).add_to(map_route)

    folium.Marker(location=[G.node[start]['y'], G.node[start]['x']],
                  popup='Start', icon=folium.Icon(color='orange'),
                  title='Start').add_to(map_route)

    # Save map as html file
    filepath = "output/bus_routes.html"
    map_route.save(filepath)


def agentroutes_plot(G, routes_list, impnodes):
    """Plots agents routes, origin and destination nodes

    Parameters
    ----------
    Self explanatory

    Returns
    -------
    html map file with routes

    """
    # Extract points
    destination = impnodes[1]
    start = impnodes[2]

    # Define and create map with appropriate boundaries
    global_lat = []
    global_lon = []
    for route in routes_list:
        for element in route:
            for node in [element[0], element[1]]:
                global_lon.append(G.nodes[node]['x'])  # lon
                global_lat.append(G.nodes[node]['y'])  # lat
    min_point = [min(global_lat), min(global_lon)]
    max_point = [max(global_lat), max(global_lon)]
    map_route = folium.Map(zoom_start=1, tiles='cartodbpositron')
    map_route.fit_bounds([min_point, max_point])

    # Add agent routes
    for route in routes_list:
        for element in route:
            points = []
            if 'geometry' in G.edges[element[0], element[1], 0]:
                a = [(lat, lon) for lon, lat in G.edges[element[0],
                     element[1], 0]['geometry'].coords]
                points.extend(a)

            else:
                b = [(G.node[element[0]]['y'], G.node[element[0]]['x'])]
                c = [(G.node[element[1]]['y'], G.node[element[1]]['x'])]
                points.extend(b)
                points.extend(c)

            folium.PolyLine(locations=points, color=element[3],
                            weight=6, smooth_factor=2, popup=element[2],
                            opacity=0.6).add_to(map_route)

    # Add S-D nodes
    folium.Marker(location=[G.node[destination]['y'],
                  G.node[destination]['x']], popup='Destination',
                  title='Destination',
                  icon=folium.Icon(color='green')).add_to(map_route)

    folium.Marker(location=[G.node[start]['y'], G.node[start]['x']],
                  popup='Start', icon=folium.Icon(color='orange'),
                  title='Start').add_to(map_route)

    # Save map as html file
    filepath = "output/agent_routes.html"
    map_route.save(filepath)


def riskaware_planning(G, route_list, impnodes, risk_value=0.5, time_budget=15):
    """Generates the optimal path balancing between least expected travel time
    path and most reliable path. Updates observed travel times online.

       Parameters
       ----------
       Self explanatory.

       Returns
       -------
       Route an agent is supposed to take.

    """

    # Extract variables - routes and important nodes
    [red_route, blue_route] = route_list
    [origin, dest, start] = impnodes

    # Calculate the least expected time from a given node to dest
    def optimal_choice(G, bus_yta, agent_cnode,
                       agent_route, risk_value, time_budget):
        """Finds the optimal path from start node to
        end node. Also returns the least expected travel time value

        """

        # LET Cost
        costs = dict()
        for bus in bus_yta:
            index = bus['route'].index(bus['current_node'])
            nodelist = bus['route'][index:]

            cost = 0
            path = list(zip(nodelist[:-1], nodelist[1:]))
            for pair in path:
                dist = G[pair[0]][pair[1]][0]['traveltime']
                for option in dist:
                    cost += option[0]*option[1]

            costs.update({bus['name']: {'let': cost}})

        # Reliability - Prob of ontime arrival
        for bus in bus_yta:
            time_values = [6, 10, 14, 30]
            cdf_blue = [0.2, 0.45, 0.8, 1]
            cdf_red =  [0.055, 0.245 , 0.57, 1]

            # identify bus location
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

                    if bus['name'] == 'red':
                        reli = cdf_red[index]
                    if bus['name'] == 'blue':
                        reli = cdf_blue[index]

            # Store data
            costs[bus['name']]['reli'] = reli

        # Balance reliability and least expected travel time
        max_reli = max(costs['red']['reli'], costs['blue']['reli'])

        for bus in costs:
           combined_cost = risk_value*costs[bus]['reli']/max_reli + (1 - risk_value)*(1/costs[bus]['let'])/0.0806
           costs[bus]['total_cost']  = combined_cost

        # Selecting bus with max total_cost
        key_max = max(costs.keys(), key=(lambda k: costs[k]['total_cost']))
        for bus in bus_yta:
            if bus['name'] == key_max:
                out_bus = bus

        return out_bus

    # Sample edge travel time from the given ditribution
    def sample_edgetime(G, bus):
        current_node = bus['current_node']

        try:
            next_node = bus['route'][bus['route'].index(current_node)+1]
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

    # Initialize for bus route simulation
    red = dict([('current_node', origin), ('arrival_time', dict([(origin, 0)])), ('next_node', None), ('route', red_route), ('name','red')])
    blue = dict([('current_node', origin), ('arrival_time', dict([(origin, 0)])), ('next_node', None), ('route', blue_route), ('name','blue')])
    agent_route = []
    agent_cnode = start
    agent_pnode = start
    sim_time = 0
    run_status = True

    while True:

        # ------------- Buses running simulation segment -------------------

        for bus in [red, blue]:

            # First time step travel time
            if sim_time == 0:
                (time_nextedge, next_node) = sample_edgetime(G, bus)
                bus['next_node'] = next_node
                bus['arrival_time'].update({next_node: bus['arrival_time'][bus['current_node']] + time_nextedge})

            # loop for every time step till all buses reach dest
            if bus['arrival_time'][bus['next_node']] == sim_time:

                # Update time on previous edge and current node
                G[bus['current_node']][bus['next_node']][0]['traveltime'] = [(bus['arrival_time'][bus['next_node']] - bus['arrival_time'][bus['current_node']], 1)]
                bus['current_node'] = bus['next_node']

                # Sample time for edge next_node -> node after that, if exists
                if bus['current_node'] != dest:
                    (time_nextedge, nextnext_node) = sample_edgetime(G, bus)

                    # Update next node
                    bus['next_node'] = nextnext_node
                    bus['arrival_time'].update({bus['next_node']: bus['arrival_time'][bus['current_node']] + time_nextedge})

        # Break condition
        if red['current_node'] == dest and blue['current_node'] == dest:
            print('All buses reached the destination.')
            break

        # ------------ Agent Decision Making and Routing Segment -------------

        # Decision step - new decision if start or exchange node
        if G.node[agent_cnode]['code'] in {3, 4}:

            # Possible options at current exchange point
            bus_yta = []  # list of buses yta at agent_cnode
            for bus in [red, blue]:
                if agent_cnode in bus['route']:
                    if bus['route'].index(bus['current_node']) <= bus['route'].index(agent_cnode):
                        bus_yta.append(bus)

            # If all other buses already left
            if len(bus_yta) == 1:
                agent_bus = bus_yta[0]

            # If more than one possible buses
            else:
                agent_bus = optimal_choice(G, bus_yta, agent_cnode,
                                          agent_route, risk_value, time_budget)

                if agent_cnode not in agent_bus['route']:
                    raise Exception('Optimal route does not go through current node of agent. Check optimal_choice again.')

            if agent_bus['current_node'] == agent_cnode:
                # Storing route data once action is taken
                agent_pnode = agent_cnode
                agent_cnode = agent_bus['next_node']
                agent_route.append((agent_pnode, agent_cnode, agent_bus['arrival_time'][agent_bus['next_node']] - agent_bus['arrival_time'][agent_bus['current_node']], agent_bus['name']))

        # If destination reached
        elif G.node[agent_cnode]['code'] == 2:
            if run_status:
                print('Agent reached destination.')
                run_status = False

        # Non exchange points - Following predecided optimal routes
        else:

            # Route and time saving step
            if agent_bus['current_node'] == agent_cnode:

                # Store data then update current and next states
                agent_pnode = agent_cnode
                agent_cnode = agent_bus['next_node']
                agent_route.append((agent_pnode, agent_cnode, agent_bus['arrival_time'][agent_bus['next_node']] - agent_bus['arrival_time'][agent_bus['current_node']], agent_bus['name']))

#            # Arrival time at first point - Hardcoded
#            if agent_bus['current_node'] == start:
#                agent_route['nodes'].append((start, sim_time))

        # Update while loop simualtion time
        sim_time += 1

    return G, red, blue, agent_route


def update_exchangepoints(G, route_list):
    """Extracts exchange points for different routes and updates corresponding
       nodes in graph G. Returns G.

    """
    routes_sets = [set(route) for route in route_list]
    if len(routes_sets) == 1:
        raise Exception("There is only one route. No exchange points")
    elif len(routes_sets) == 0:
        raise Exception("The route list has no elements")
    else:
        exchange_points = []
        for set1 in routes_sets:
            if len(routes_sets) == 1:
                break
            routes_sets.remove(set1)
            for set2 in routes_sets:
                exchange_points.append(set1.intersection(set2))
        exchange_points = set.union(*exchange_points)
        for point in exchange_points:
            G.node[point]['code'] = 4

    return G


if __name__ == '__main__':

    # Initialize the graph and set exchange nodes
    G, route_list = initialize(nodeplot=False)
    G = update_exchangepoints(G, route_list)

    # Set origin-destination and start nodes
    impnodes = [37982924, 38054103, 37982924]  # Order - O, D, S
    G.node[impnodes[0]]['code'] = 1
    G.node[impnodes[1]]['code'] = 2
    G.node[impnodes[2]]['code'] = 3

    # Visualize bus routes
    busroutes_plot(G, route_list, impnodes)
#
    # Running simulation
    time_budget = 10
    risk_value = 0.5
    [G, red, blue, agent_route] = riskaware_planning(G, route_list, impnodes, risk_value=risk_value, time_budget=time_budget)

    # Plotting route
    agentroutes_plot(G, [agent_route], impnodes)

    # Printing required information
    for bus in [red, blue]:
        print(" {} bus reached at {} units of time.".format(bus['name'], bus['arrival_time'][impnodes[1]]))

    agent_totaltime = 0
    for element in agent_route:
        agent_totaltime += element[2]
    print("Agent with risk factor {} and time budget {} reached at {} units of time".format(risk_value, time_budget, agent_totaltime))
    print(agent_route)

############### Features
    # let_blue = 14.2
    # let_red = 12.399
    # time_values = [6, 10, 14, 30]
    # cdf_blue = [0.2, 0.45, 0.8, 1]
    # cdf_red =  [0.055, 0.245 , 0.57, 1]

