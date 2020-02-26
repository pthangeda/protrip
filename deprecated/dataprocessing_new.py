# -*- coding: utf-8 -*-
"""
Description:

Author: Pranay Thangeda
License: MIT License
Email: contact@prny.me
Description: Functions for extracting and processing data from GTFS feed
and historic travel time data from CUMTD
"""

import os
import pandas as pd
import networkx as nx
from tqdm import tqdm
import folium

"""
Known Bugs - Issues

0) For some roads, "stop_name, stop_id number" DOESNOT work. Currently manual
override for certain stops. Should be fixed by 5.

1) Working assumption: It is unlikely that there exists two routes between two
stops such that the routes take two different paths between these
stops without any intermediate stops.

2) Few outliers in the datasheets lead to unreasonable distances and times. Need
to check what is causing the issues: currently tackling by eliminating datapoints
with non positive time and distances, eliminating when difference between sample
distances is greater than 1 and by ignoring edges with very few samples.

3) Visualization module doesnot use road shape file and instead directly plots
a straight line between two stops. (not essential)

4) Fix some edges with high distances or 0 distances and time. Likely due to
node mismatch mentioned in 5). Currently discarding the samples.

5) If node name repeats in Graph G, it overrides existing data with new data.
Ideally no stop names should repeat and CUMTD GTFS has three files. In this case,
they are totally different stops with same names and the numbers ended up matching.
One quick fix is to use stop_code in node naming convention - stop_code is unique
to every stop I believe. Can be fixed but we will have multiple nodes with the
same name as in 'Stop' of datasheets. One way is to create and edge based on
the distances between the nodes under consideration (should be reasonable)

"""

def _add_timedata(G, node1, node2, count_trips, time, distance, trip_shape):
    """
    Create edges based on the trips in the graph along with route shapes
    """
    # Edge already exists
    if G.has_edge(node1, node2):

        if abs(G[node1][node2]['length'] - distance) > 50:
            pass
#            print(abs(G[node1][node2]['length'] - distance))
#            raise Exception('Distances over multiple samples not matching')
        else:
            G[node1][node2]['time_data'][count_trips] = time
            G[node1][node2]['trip_shapes'].add(trip_shape)

    else:
        G.add_edge(node1, node2, time_data = {count_trips:time}, length = distance,
                   trip_shapes = set([trip_shape]))


def _get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h)*3600+int(m)*60+int(s)

def extract_data(ROOT_PATH):

    # Generate graph with stops as nodes (node label = stop_id)
    gtfs_path = os.path.join(ROOT_PATH, 'cumtd_gtfs')
    G = nx.Graph()
    df_stops = pd.read_csv(gtfs_path+'\stops.txt')
    stops = zip(df_stops.stop_id, df_stops.stop_name, df_stops.stop_lat,
                df_stops.stop_lon)

    stops_notationmap = {}
    for stop_id, stop_name, stop_lat, stop_lon in stops:
        node_label = stop_id

        if node_label not in G.nodes:
            stop_newname = stop_name +','+ stop_id[-1]
            G.add_node(node_label, stop_name = stop_newname,
                       stop_lat = stop_lat, stop_lon = stop_lon)
            stops_notationmap.update({stop_id: stop_newname})

        else:
            # If node with the same name exists.

            if G.nodes[node_label]['stop_lat'] == stop_lat and \
            G.nodes[node_label]['stop_lon'] == stop_lon:
                pass
                # Stop with exact same coordinates. Ignore the record.
            else:
                print(node_label)
                raise Exception('stop_id repeating in stops.txt with different \
                                data, check stops.txt file again.')


    # Extract travel time data from csv files and add to graph
    count_files = 0
    count_trips = 0
    list_trips = set() # list of shape names of all trips analyzed
    csv_path = os.path.join(ROOT_PATH, 'cumtd_datasheetsx')
#TODO: Integrate iteration over trips to add trip_shape to the graph entry
    trip_shape = None

    # Iterate over files in the directory
    for filename in tqdm(os.listdir(csv_path)):

       file_path = os.path.join(csv_path, filename)
       df = pd.read_csv(file_path, header=1)
       count_files += 1

       # Select rows with specific values in 'Type' field
       index_interested = df.loc[df.Type.isin(['Stop', 'Drive through'])].index

       # Iterate over indices
       for item in zip(index_interested[0:-1], index_interested[1:]):

           index_alpha, index_beta = item

           # Check if they are consecutive
           if df['No'][index_alpha]+1 ==  df['No'][index_beta]:

               # Extract stop_ids with current stop_newname
               stopid_alpha = [k for k,v in stops_notationmap.items() if v == df['Stop'][index_alpha]]
               stopid_beta = [k for k,v in stops_notationmap.items() if v == df['Stop'][index_beta]]

               # Check if both the stops exist in the stop list
               if len(stopid_alpha) == 0 or len(stopid_beta) == 0:
                   pass
                   #print('Fatal fault')
                   #raise Exception('Stops will have to be in stop list. Check graph again')

               elif len(stopid_alpha) == 1 and len(stopid_beta) == 1:
                   time_alpha = _get_sec(df['Actual dep'][index_alpha])
                   time_beta = _get_sec(df['Actual dep'][index_beta])
                   dist_alpha = df['Sched. total distance'][index_alpha]*1609.34
                   dist_beta = df['Sched. total distance'][index_beta]*1609.34
                   time = time_beta - time_alpha
                   distance = dist_beta - dist_alpha

                   if time < 0 or distance < 0 or distance >= 4506.16:
                       pass
                       print("Time: {} and Distance:  {}".format(time, distance))
                       raise Exception('Time and distance should be positive and bounded.')
                   else:
                       _add_timedata(G, stopid_alpha[0], stopid_beta[0], count_trips, time, distance, trip_shape)

#TODO: Find most likely point in the map by using historical point and GPS co-ordinates
               elif len(stopid_alpha) > 1 or len(stopid_beta) > 1:
                   pass


    # Checks and printing stats
    print("\nNo.of csv data files parsed: {}\n".format(count_files))
    print("No.of trips parsed: {}\n".format(count_trips))

    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()

    if total_edges <= 0:
        raise Exception("Total edges has to be a positive integer.")

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

    return G, list_trips


def visualization(G):

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
        if max_samples == min_samples:
            weight = 1
        else:
            weight = (1-0.4)*(num_samples-min_samples)/(max_samples-min_samples) + 0.4
        folium.PolyLine(locations=points, color='blue', popup=str(num_samples), weight=3*weight, opacity=1).add_to(m)

    # Save map as html file
    m.save('map_extracteddata.html')


# Eliminiate outliers
# Calculate average time data

# ==============================================
if __name__ == "__main__":

    ROOT_PATH = 'D:\\Repos\\riskaware-planning'
    G, list_trips = extract_data(ROOT_PATH)
    visualization(G)