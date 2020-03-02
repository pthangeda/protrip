# -*- coding: utf-8 -*-
"""
Description:

Author: Pranay Thangeda
License: MIT License
Email: contact@prny.me
Created on Mon Oct 14 12:57:30 2019
"""

'''
Script to convert CUMTD travel time data from different routes to a graph where
nodes are bus stops of interest and edges are bus routes between them. The graph
is multidigraph to account for multiple edges between different nodes and each
edge has specifications in terms of travel time distribution and distance
'''

import peartree as pt
import networkx as nx
import osmnx as ox
import numpy as np
import folium
import pandas as pd
import partridge as ptg
import datetime
import random
import dataprocessing
import polyline_offset as poff

############## Select and Extract Routes of Interest ##########################
PATH = 'D:\\Repos\\riskaware-planning\\forpaper\cumtd_gtfs.zip'
desired_date = datetime.date(2019, 3, 5)
service_ids_by_date = ptg.read_service_ids_by_date(PATH)
service_ids = service_ids_by_date.get(desired_date)

# Service IDs of interest
service_ids_interest = frozenset(['SV1 UIMF', 'SV2 UIMF', 'SV3 UIMF', 'R5 MF', 'R2 MF', 'R4 MF', 'R6 UIMF', 'Y1 NONUIMF',
                                  'Y2', 'Y3 NONUIMF', 'Y4', 'Y6 SCH', 'Y7 UIMTH', 'I7 UIMTH', 'I2 UIMTH', 'I5 UIMTH', 'I3 UIF',
                                  'O1 MF', 'O2 MF', 'O3 MF', '04 MF',
                                  'GN7 MF', 'GN2 MF', 'GN3 NOSCH', 'GN4', 'GN5 MF', 'GN6 SCHMF','T1 NONUIMF'])
view = {
    'trips.txt': {'service_id': service_ids_interest},
}
feed = ptg.load_feed(PATH, view)
routes_list = []
route_ids2 = list(feed.routes.route_id)
route_ids = ['TEAL EVENING', 'GREENHOPPER', 'ORANGEHOPPER']
for route in route_ids:
    color = list(feed.routes.loc[feed.routes['route_id'] == route].route_color)[0]
    shape_id = list(feed.trips.loc[feed.trips['route_id'] == route].shape_id)[0]
    rel_shapes = feed.shapes.loc[feed.shapes['shape_id'] == shape_id]
    route_points = list(zip(rel_shapes.shape_pt_lat, rel_shapes.shape_pt_lon))
    routes_list.append([color, route_points])


def stops_plot(G):

    stops_all = {}
    lat_data = nx.get_node_attributes(G, 'stop_lat')
    lon_data = nx.get_node_attributes(G, 'stop_lon')
    for node in G.nodes.data():
        name = str(node[0])
        point = [float(node[1]['stop_lat']), float(node[1]['stop_lon'])]
        stops_all[name] = point

    global_lat = []; global_lon = []
    for name, point in stops_all.items():
        global_lat.append(point[0])
        global_lon.append(point[1])

    min_point = [min(global_lat), min(global_lon)]
    max_point =[max(global_lat), max(global_lon)]
    m = folium.Map(zoom_start=1, tiles='cartodbpositron')
    m.fit_bounds([min_point, max_point])


#     # Plot all stops
#    for stop_name, stop_point in stops_all.items():
#        folium.CircleMarker(location=[float(stop_point[0]), float(stop_point[1])],
#                        radius= 1,
#                        popup = stop_name,
#                        color="#000000",
#                        fill=True, opacity=0.5).add_to(m)

    return m


def routes_plot(routes_list, m):

    # Define and create map with appropriate boundaries
    global_lat = []; global_lon = []
    for route in routes_list:
        for point in route[1]:
            global_lon.append(point[1]) #lon
            global_lat.append(point[0]) #lat
    min_point = [min(global_lat), min(global_lon)]
    max_point =[max(global_lat), max(global_lon)]
#    m = folium.Map(zoom_start=1, tiles='cartodbpositron')
#    m.fit_bounds([min_point, max_point])

    for route in routes_list:
        color = route[0]
        points = route[1]
        folium.PolyLine(locations=points, color='#'+color, weight=6, opacity=1).add_to(m)

    # Save map as html file
    m.save('routes_casestudy.html')

def offset_plot(routes_list, m):

    # Define and create map with appropriate boundaries
    global_lat = []; global_lon = []
    for route in routes_list:
        for point in route[1]:
            global_lon.append(point[1]) #lon
            global_lat.append(point[0]) #lat
    min_point = [min(global_lat), min(global_lon)]
    max_point =[max(global_lat), max(global_lon)]
#    m = folium.Map(zoom_start=1, tiles='cartodbpositron')
#    m.fit_bounds([min_point, max_point])

    for route in routes_list:
        color = route[0]
        points = route[1]
        poff.PolyLineOffset(locations=points, color='#'+color, weight=6, opacity=1, offset=5).add_to(m)

    # Save map as html file
    m.save('routes_forpaper.html')


def add_polygon(shape, m):

    folium.Polygon(shape, color='#808080', opacity=0.1, fill='True', fill_opacity=0.42).add_to(m)
    m.save('routes_casestudy.html')



ROOT_PATH = 'D:\\Repos\\riskaware-planning'
shape = [(40.112827, -88.219315), (40.112769, -88.223979), (40.116356, -88.224056), (40.116397, -88.229009), (40.112727, -88.228901), (40.112658, -88.235397),
         (40.105433, -88.235355), (40.105449, -88.230291), (40.104153, -88.230302), (40.104209, -88.219190),
         (40.105482, -88.219219), (40.112827, -88.219315)]
#G, list_trips = dataprocessing.extract_data(ROOT_PATH)
m = stops_plot(G)
routes_plot(routes_list, m)
add_polygon(shape,m)
#offset_plot(routes_list, m)

