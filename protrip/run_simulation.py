# -*- coding: utf-8 -*-
"""
Description: Main file to run the simulation of all the trips in the transit
network
Author: Pranay Thangeda
Email: contact@prny.me
"""

import dataprocessing as dp
import datamodeling as dm
from simulation import *


ROOT_PATH = # Path to your folder here

# Extract data
if 'G' in locals():
    pass
else:
    G, list_tripshapes = dp.extract_data(ROOT_PATH, 'cumtd_gtfs')

# Import routes and build probablistic model
routes_dict = dp.import_routes(ROOT_PATH, 'sample_routes')
TTM = dm.Model(G, routes_dict)

# Build route objects
routeobjects = []
for route_name, route_nodes in routes_dict.items():
    ro = Route(route_name, route_nodes, [])
    ro.load_nodelocations(G)
    ro.load_transferstops(routes_dict)
    ro.load_meantimes(TTM)
    routeobjects.append(ro)

# Declare user inputs
origin = ['Lincoln Square Garage South,8', 'Lincoln Square Courthouse,2']
destination = ['Illinois Terminal (Platform B),2', 'Illinois Terminal (Platform A),1', 'Illinois Terminal (Platform C),5']
t_budget = 600 # tim budget in seconds
t_departure = 64800 # departure time in seconds (since start of the day)
alpha = 0.4 # user delay tolerance

traveler = Trav(origin, destination, t_budget,alpha, t_departure)

# Run simulation
ROOT_PATH = 'D:\\Repos\\riskaware-planning'
t_begin, t_end = dp.service_times(ROOT_PATH, 'cumtd_gtfs')
t_step = 1
policy = simulate(t_begin, t_end, t_step, traveler, routes_dict)









