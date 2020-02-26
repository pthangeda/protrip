# -*- coding: utf-8 -*-
"""
Description:

Author: Pranay Thangeda
License: MIT License
Email: contact@prny.me
Created on Tue Feb  4 17:37:33 2020
"""

import pandas as pd
import os

ROOT_PATH = 'D:\\Repos\\riskaware-planning'
gtfs_path = os.path.join(ROOT_PATH, 'cumtd_gtfs')
df_stops = pd.read_csv(gtfs_path+'\stops.txt')