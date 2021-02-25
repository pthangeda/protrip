# -*- coding: utf-8 -*-
"""
Description: Misc scripts used in development of the code

Author: Pranay Thangeda
Email: contact@prny.me
"""

import warnings
import dataprocessing as dp
import pandas as pd
import os


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


