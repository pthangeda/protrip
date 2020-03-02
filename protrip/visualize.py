# -*- coding: utf-8 -*-
"""
Author: Pranay Thangeda
Email: contact@prny.me
Description: Collection of scripts to visualize and animate different components
of the data and the routing policy.
"""
import numpy as np
import folium
import time
import networkx as nx

def animate_routes(G, ro_list):
    """
    Given a list of route objects generates a html animation of the routes in
    the transit network
    """
    # Define and create map with appropriate boundaries
    global_lat = []; global_lon = []
    for route in ro_list:
        for loc in route.nodesloc:
            global_lon.append(loc[1]) #lon
            global_lat.append(loc[0]) #lat
    min_point = [min(global_lat), min(global_lon)]
    max_point =[max(global_lat), max(global_lon)]
    m = folium.Map(zoom_start=1, tiles='cartodbdark_matter')
    m.fit_bounds([min_point, max_point])

    # Baseline time
    t = time.time()

    for route in ro_list:
        path = list(zip(route[:-1], route[1:]))
        lines = []
        for pair in path:

            # Time of the edge
            t_edge = G.edges[pair[0], pair[1],0]['time']

            if 'geometry' in G.edges[pair[0], pair[1], 0]:
                lines.append(dict({'coordinates':
                      [[lon, lat] for lon, lat in G.edges[pair[0], pair[1], 0]['geometry'].coords]+[[G.node[pair[0]]['x'], G.node[pair[0]]['y']]],
                'dates': [time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t)),
                           time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t+t_edge))],
                           'color':'orange'}))

            else:
                lines.append(dict({'coordinates':
                    [[G.node[pair[0]]['x'], G.node[pair[0]]['y']],
                     [G.node[pair[1]]['x'], G.node[pair[1]]['y']]],
                'dates': [time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t)),
                           time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t+t_edge))],
                           'color':'red'}))
            t = t+t_edge

        features = [{'type': 'Feature',
                     'geometry': {
                                'type': 'LineString',
                                'coordinates': line['coordinates'],
                                 },
                     'properties': {'times': line['dates'],
                                    'style': {'color': line['color'],
                                              'weight': line['weight'] if 'weight' in line else 2
                                             }
                                    }
                     }
                for line in lines]


        data = {'type': 'FeatureCollection', 'features': features}
        folium.plugins.TimestampedGeoJson(data,  transition_time=1,
                               period='PT1S', add_last_point=False, date_options='mm:ss').add_to(m)


    # Save map as html file
    m.save('route_animation.html')

def visualize_routes(G):
    """
    Visualize graph with stops and routes along with the number of samples on links
    """

    # Extract nodes data
    stops_all = {}
    lat_data = nx.get_node_attributes(G, 'stop_lat')
    lon_data = nx.get_node_attributes(G, 'stop_lon')
    for node in G.nodes.data():
        name = str(node[0])
        point = [float(node[1]['stop_lat']), float(node[1]['stop_lon'])]
        stops_all[name] = point

    stops_isolated = {}
    nodes_isolated = list(nx.isolates(G))
    for name in nodes_isolated:
        point = [float(lat_data[name]), float(lon_data[name])]
        stops_isolated[name] = point


    # Extract edge data
    edges_list = []
    max_samples = 0
    min_samples = 1e20
    for n1, n2, data in list(G.edges(data=True)):
        points = [(lat_data[n1], lon_data[n1]),(lat_data[n2], lon_data[n2])]
        num_samples = len(data['time_data'])
        if num_samples > max_samples:
            max_samples = num_samples
        if num_samples < min_samples:
            min_samples = num_samples

        if num_samples <= 0:
            pass
        else:
            edges_list.append([num_samples, points])

    # Baseline map
    global_lat = []; global_lon = []
    for name, point in stops_all.items():
        global_lat.append(point[0])
        global_lon.append(point[1])

    min_point = [min(global_lat), min(global_lon)]
    max_point =[max(global_lat), max(global_lon)]
    m = folium.Map(zoom_start=1, tiles='cartodbdark_matter')
    m.fit_bounds([min_point, max_point])

    # Plot all stops
    for stop_name, stop_point in stops_all.items():

        if stop_point in list(stops_isolated.values()):
            folium.CircleMarker(location=[float(stop_point[0]), float(stop_point[1])],
                        radius= 1,
                        popup = stop_name,
                        color="#ed0e37",
                        fill=True).add_to(m)
        else:
            folium.CircleMarker(location=[float(stop_point[0]), float(stop_point[1])],
                        radius= 1,
                        popup = stop_name,
                        color="#00ff00",
                        fill=True).add_to(m)
    # Plot all edges
    for edge in edges_list:
        num_samples = edge[0]
        points = edge[1]
        # scaling between 0.4 and 1
        weight = (1-0.4)*(num_samples-min_samples)/(max_samples-min_samples) + 0.4
        folium.PolyLine(locations=points, color='blue', popup=str(num_samples), weight=3*weight, opacity=1).add_to(m)

    # Save map as html file
    m.save('map_extracteddata.html')