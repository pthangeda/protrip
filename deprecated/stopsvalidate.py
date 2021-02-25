# -*- coding: utf-8 -*-
"""
Description:

Author: Pranay Thangeda
License: MIT License
Email: contact@prny.me
Created on Fri Jan 31 12:16:54 2020
"""

# Import and check if any of the stop IDs in GTFS are same

import os
import pandas as pd
import networkx as nx
from tqdm import tqdm
import folium


ROOT_PATH = 'D:\\Repos\\riskaware-planning'

gtfs_path = os.path.join(ROOT_PATH, 'cumtd_gtfs')
G = nx.Graph()
df_stops = pd.read_csv(gtfs_path+'\stops.txt')
stops = zip(df_stops.stop_id, df_stops.stop_name, df_stops.stop_lat,
                df_stops.stop_lon)

