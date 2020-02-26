# -*- coding: utf-8 -*-
"""
Description: Misc scripts and test used in the development of code. 

Author: Pranay Thangeda
Email: contact@prny.me
"""

import warnings
import dataprocessing as dp
import pandas as pd
import os

# Import the graph


def initialize(nodeplot):
    """Initializes the graph, travek time and bus routes.

    Parmeters
    ---------
    nodeplot: bool, optional (default=False)
        plots the nodes of graphs and osmids

    """
    # Create simple grid graph in Champaign
    location_point = (40.110860, -88.234501)
    G = ox.graph_from_point(location_point, distance=90, distance_type='bbox',
                            network_type='drive')
    G.add_edge(37982924, 38098327, osmid=2200, maxspeed=25, oneway=True,
               length=155.878)

    # Delete attributes
    att_del_list = ['highway', 'name']
    count = 1
    for u, v, k, data in G.edges(data=True, keys=True):

        # Change osmid
        data['osmid'] = count
        count += 1
        # Delete some attributes
        for att in att_del_list:
            data.pop(att, None)

    # Initialize travel times specific to edges

    # top
    speeds = [10, 20, 30, 40]  # m/sec
    probs = [0.1, 0.3, 0.4, 0.2]
    traveltime = []
    for i, j in zip(speeds, probs):
        traveltime.append((int(data['length']/i), j))  # rounding
    G[37982924][38098327][0]['traveltime'] = traveltime

    # bottom
    speeds = [10, 20, 30, 40]  # m/sec
    probs = [0.05, 0.4, 0.5, 0.05]
    traveltime = []
    for i, j in zip(speeds, probs):
        traveltime.append((int(data['length']/i), j))  # rounding
    G[37982929][38054103][0]['traveltime'] = traveltime

    # left
    speeds = [10, 20, 30, 40]  # m/sec
    probs = [0.3, 0.1, 0.5, 0.1]
    traveltime = []
    for i, j in zip(speeds, probs):
        traveltime.append((int(data['length']/i), j))  # rounding
    G[37982924][37982929][0]['traveltime'] = traveltime

    # right
    speeds = [10, 20, 30, 40]  # m/sec
    probs = [0.1, 0.3, 0.4, 0.2]
    traveltime = []
    for i, j in zip(speeds, probs):
        traveltime.append((int(data['length']/i), j))  # rounding
    G[38098327][38054103][0]['traveltime'] = traveltime

    # Initialize node codes 0 - none, 1 - origin, 2 - dest, 3 - start, 4 - ex
    for u, data in G.nodes(data=True):
        data['code'] = 0

    # Fix bus route nodes
    red = [37982924, 38098327, 38054103]
    blue = [37982924, 37982929, 38054103]

    if nodeplot:
        # Plot edges and nodes with node osmids
        fig, ax = ox.plot_graph(G, node_size=30, node_color='#261CE9',
                                annotate='true')

    route_list = [red, blue]
    return G, route_list


# Check routes
green = ('Sunnycrest Mall (North Side),2', 'Florida & Linden (NE Corner),1', 'Florida & Cottage Grove (NE Corner),1',
         'Cottage Grove & Penn (SE Corner),2', 'Pennsylvania Ct. (South Side),1',
         'Penn & Anderson (NE Corner),1', 'Anderson & Michigan (SE Corner),2', 'Anderson & Fairlawn (NW Far Side),8',
         'Fairlawn (North Side),2', 'Vine & Fairlawn (NE Corner),1', 'Vine & Washington (SE Corner),2',
         'Vine & Oregon (SE Corner),2', 'Vine & Illinois (SE Corner),2', 'Vine & Green (SE Corner),2','Lincoln Square Garage South,8', 'Green & Race (NW Corner),4',
                   'Green & Cedar (NE Corner),1', 'Green & Birch (NE Corner),1',
                   'Green & Orchard (NE Corner),1', 'Green & Busey (NE Corner),1',
                   'Green & Gregory (NW Far Side),1', 'Green & Goodwin (NW Far Side),8',
                   'Illini Union (North Side Shelter),2', 'Green & Sixth (NE Corner),1',
                   'Green & Fourth (NE Corner),1', 'Green & Second (NE Corner),1',
                   'Green & Locust (NE Corner),1', 'Green & Neil (NE Far Side),5', 'Neil & Springfield (SE Corner),2',
                   'Neil & Marshall (SE Corner),2', 'Walnut & Logan (SE Corner),2', 'Walnut & University (SE Corner),2', 'Illinois Terminal (Platform B),2')

orange = ('University & Cottage Grove (NE Corner),1', 'University & Hickory (NE Corner),1', 'University & Sycamore (NE Corner),1',
          'University & Maple (NE Corner),1', 'University & Vine (SW Far Side),7', 'Vine & Water (NW Corner),4','Main & Vine (NW Corner),4',
           'Lincoln Square Courthouse,2', 'Save A Lot (East Side),2', 'Broadway & University (SE Corner),2',
           'Broadway & Park (NW Far Side),8', 'Park & Central (NE Corner),1', 'Church & Orchard (NE Corner),1',
           'Coler & Church (NE Corner),1', 'Church & Busey (NE Corner),1', 'Lincoln & Park (West Side),4',
           'Campus Circle (North Side),2', 'University & Goodwin (NE Corner),1', 'Goodwin & Park (NW Far Side),8',
           'Park & Romine (North Side),1', 'Park & Wright (NE Corner),1', 'University & Sixth (NW Far Side),8',
           'University & Fourth (NE Corner),1', 'University & Second (NE Corner),1', 'Illinois Terminal (Platform A),1')

teal = ('PAR (North Side Shelter),2', 'Penn & Maryland (SE Corner),2', 'Plant Sciences Lab (East Side),2', 'Gregory & Dorner (SE Corner),2',
        'Goodwin & Gregory (NE Corner),1', 'Goodwin & Nevada (SE Corner),2', 'Krannert Center (East Side Shelter),2', 'Green & Goodwin (NW Far Side),8', 'Illini Union (North Side Shelter),2',
        'Wright & Healey (East Side),2', 'White & Wright (SE Corner),2', 'White Street Mid-Block (North Side),2', 'White & Second (NE Corner),1', 'White & First (NE Corner),1',
        'Illinois Terminal (Platform C),5')


def routes_tocsv(routes, filename):
    """
    Export given routes dict with route name as key and
    route nodes list as value to a csv file with name 'filename'
    """
    df = pd.DataFrame.from_dict(routes, orient="index")
    df.to_csv(filename+".csv")


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

def routes_validation(G, routes_list):
    """
    Check if the routes in routes_list exist in transit network G with
    sufficient number of samples.
    """
    num_routes = len(routes_list)
    num_missingnodes = 0
    num_missingedges = 0
    num_minsamples = 10e10

    for route in routes_list:

        for node in route:
            if not G.has_node(node):
                warnings.warn('Node from route doesnot exist in the graph')
                print(node)
                num_missingnodes += 1

        edges = zip(route[0:-1], route[1:])
        for edge in edges:
            if G.has_edge(edge[0], edge[1]):
                num_samples = len(G[edge[0]][edge[1]]['time_data'])
                if num_samples < num_minsamples:
                    num_minsamples = num_samples
            else:
                warnings.warn('Edge required for route does not exist')
                print(edge)
                num_missingedges += 1

    return num_missingnodes, num_missingedges, num_minsamples

ROOT_PATH = 'D:\\Repos\\riskaware-planning'
#☺G, list_tripshapes = dp.extract_data(ROOT_PATH, 'cumtd_gtfs')
routes_list = [teal, orange, green]
n_mn, n_me, n_ms = routes_validation(G, routes_list)

routes_dict = {'green':green, 'orange':orange, 'teal':teal}
routes_tocsv(routes_dict, 'sample_routes')
routes_out = dp.import_routes(ROOT_PATH, 'sample_routes')


