# -*- coding: utf-8 -*-
"""
Author: Pranay Thangeda
Email: contact@prny.me
Description: Functions for extracting and processing data from GTFS feed
and historic travel time data from CUMTD
"""

import os
import pandas as pd
import networkx as nx
from tqdm import tqdm
import warnings
import folium


def _add_timedata(G, node1, node2, count_trips, time, distance, trip_shape):
    """
    Create edges based on the trips in the graph along with route shapes
    """
    # Edge already exists
    if G.has_edge(node1, node2):

        if abs(G[node1][node2]['length'] - distance) > 50:
            print(abs(G[node1][node2]['length'] - distance))
            warnings.warn('Distances over multiple samples not matching')
        else:
            G[node1][node2]['time_data'][count_trips] = time
            G[node1][node2]['trip_shapes'].add(trip_shape)

    else:
        G.add_edge(node1, node2, time_data = {count_trips:time}, length = distance,
                   trip_shapes = set([trip_shape]))


def _get_sec(time_str):
    """
    Convert HH:MM:SS to seconds
    """
    h, m, s = time_str.split(':')
    return int(h)*3600+int(m)*60+int(s)


def extract_data(ROOT_PATH, gtfs_foldername):
    """
    Extract stops, routes, and travel time data and compile them into a graph
    """
    # Generate graph with stops as nodes
    gtfs_path = os.path.join(ROOT_PATH, gtfs_foldername)
    G = nx.Graph()
    df_stops = pd.read_csv(gtfs_path+'\stops.txt')
    stops = zip(df_stops.stop_id, df_stops.stop_name, df_stops.stop_lat,
                df_stops.stop_lon)

    for stop_id, stop_name, stop_lat, stop_lon in stops:
        node_name = stop_name+',' + stop_id[-1]

#        exceptions = []
#        if stop_name in exceptions:
#            print(stop_name)
#            raise Exception('Current stop is an exception')

        if node_name not in G.nodes:
            G.add_node(node_name, stop_lat = stop_lat,
                       stop_lon = stop_lon)
        else:
            if G.nodes[node_name]['stop_lat'] == stop_lat and G.nodes[node_name]['stop_lon'] == stop_lon:
                pass
            else:
                print(node_name)
                warnings.warn('Stops repeating in stops.txt with different \
                                data, check stops.txt file again.')


    # Extract travel time data from time-table adherence files
    count_files = 0
    count_trips = 0
    list_tripshapes = set() # list of shape names of all trips analyzed
    csv_path = os.path.join(ROOT_PATH, 'cumtd_datasheets')

    # Iterate over files in the directory
    for filename in tqdm(os.listdir(csv_path)):

       file_path = os.path.join(csv_path, filename)
       df = pd.read_csv(file_path, header=1)
       count_files += 1

       # Delete columns with two values in Type and reindex
       index_toremove = df.loc[df.Type.isin(['Stop without doors','Stop with doors','Dead run out', ])].index
       df = df.drop(index_toremove)
       index_trips = df.loc[df.Type.isin(['Additional trip','Trip'])].index

       # Iterate over trips in the file
       for item in zip(index_trips[0:-1], index_trips[1:]):

           index_start, index_end = item
           trip_shape = df.Graphic[index_start][9:]
           list_tripshapes.add(trip_shape)
           count_trips += 1

           # list of stop pairs between index_start and index_end
           stop_pairs = zip(df.index[index_start+1:index_end-1],
                            df.index[index_start+2:index_end])

           for pair in stop_pairs:

               index_1, index_2 = pair

               types_ofnodes = ['Stop', 'Drive through']
               if str(df['Type'][index_1]) not in types_ofnodes or str(df['Type'][index_2]) not in types_ofnodes:
                   continue

               node1 = str(df['Stop'][index_1])
               node2 = str(df['Stop'][index_2])

               if G.has_node(node1) and G.has_node(node2):

                   time_node1 = _get_sec(df['Actual dep'][index_1])
                   time_node2 = _get_sec(df['Actual dep'][index_2])
                   dist_node1 = df['Sched. total distance'][index_1]*1609.34
                   dist_node2 = df['Sched. total distance'][index_2]*1609.34
                   time = time_node2 - time_node1
                   distance = dist_node2 - dist_node1

                   if time < 0 or distance < 0 or distance >= 2000:
                       print(node1); print(node2)
                       print("Time: {} and Distance:  {}".format(time, distance))
                       warnings.warn('Time and distance should be positive and bounded')
                   else:
                       _add_timedata(G, node1, node2, count_trips, time, distance, trip_shape)
               else:
                   print(node1); print(node2)
                   warnings.warn('Stops from data do not exist in graph')

    remove_list = []
    for u,v,data in G.edges(data=True):
        if len(data['time_data']) <= 10:
            remove_list.append((u,v))
    G.remove_edges_from(remove_list)

    # Checks and printing stats
    print("\nNo.of csv data files parsed: {}\n".format(count_files))
    print("No.of trips parsed: {}\n".format(count_trips))

    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()
    inactive_nodes = list(nx.isolates(G))
    num_activenodes = total_nodes - len(inactive_nodes)
    num_samples = 0
    for edge in list(G.edges.data()):
        num_samples += len(edge[2]['time_data'])
    avg_samplecount = num_samples/(total_edges)

    print("Total no.of stops (nodes): {}\n".format(total_nodes))
    print("Total no.of edges (road segements with data): {}\n".format(total_edges))
    print("No.of stops (nodes) with data: {}\n".format(num_activenodes))
    print("Average no.of samples on each road segment: {}\n".format(avg_samplecount))

    return G, list_tripshapes


def service_times(ROOT_PATH, gtfs_foldername):
    """
    Finds the service start and service end times of the transit agency from GTFS file
    """
    gtfs_path = os.path.join(ROOT_PATH, gtfs_foldername)
    df_stoptimes = pd.read_csv(gtfs_path+'\stop_times.txt')
    depart_times = df_stoptimes['departure_time'].str.split(':').apply(lambda x: int(x[0])*3600 + int(x[1])*60 + int(x[2]))

    t_begin = min(depart_times)
    t_end = max(depart_times)

    return (t_begin, t_end)


def import_routes(ROOT_PATH, filename):
    """
    Import route names and their constituent nodes stored in 'filename.csv'
    at ROOT_PATH
    """
    file_path = os.path.join(ROOT_PATH, filename+'.csv')
    df = pd.read_csv(file_path, index_col=0)
    temp = df.to_dict("split")
    routes = dict(zip(temp["index"], temp["data"]))

    for key, value in routes.items():
        value = [v for v in value if str(v) != 'nan']
        routes[key] = tuple(value)

    return routes


def visualization(G):
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

# ==========================================================================
if __name__ == "__main__":

    ROOT_PATH = 'D:\\Repos\\riskaware-planning'
    G, list_tripshapes = extract_data(ROOT_PATH, 'cumtd_gtfs')
    visualization(G)