# -*- coding: utf-8 -*-
"""
Description:

Author: Pranay Thangeda
License: MIT License
Email: contact@prny.me
Description: Use the data in Graph G for particular predetermined routes and
find the distribution of the data. Use 13S and Green as two competing paths.
Generate plots of distributions for graph.
"""

import warnings
import numpy as np
import pandas as pd
import scipy.stats as st
import matplotlib
import matplotlib.pyplot as plt
import dataprocessing as dp
import numpy as np
import seaborn as sns



# Function to fit normal distribution to time data between two nodes
def fit_dist(G, node1, node2):

    # fitting normal distribution between nodes
    time_data = list(G[node1][node2]['time_data'].values())

    if time_data == []:
        raise Exception('no time data between the nodes')

    params = st.norm.fit(time_data)
    return params

# Fit a multivariate normal distribution for travel time on all edges on the route
def fit_mulitvariatenormal(G, route):
    pass
    # return the distribution as some parameter

def find_conditional(node1, node2, data, dist):
    pass
    # Given data of travel time between different edges, find the conditional
    # distribution of travel time on rest of the edges and then find the
    # reliability and expected value


# Function that calculates distibution of a path assuming independence of road edges.
def calc_pathdist():
    pass

# Find covariance of travel time on edges (node1, node2) and (node3, node4)
def calc_cov(G, node1, node2, node3, node4):

    if G.has_edge(node1, node2) and G.has_edge(node3, node4):
        dict_edge1 = G[node1][node2]['time_data']
        dict_edge2 = G[node3][node4]['time_data']

        # Extract data samples with same indices in both
        common_trips = dict_edge1.keys() & dict_edge2.keys()

        if len(common_trips) in [0, 1]:
            raise Exception('Cannot find correlation. No or only one common data points between edges')

        timedata_edge1 = [dict_edge1.get(key) for key in common_trips]
        timedata_edge2 = [dict_edge2.get(key) for key in common_trips]

        # Covariance
        cov = np.cov(timedata_edge1,timedata_edge2)[0][1]
        plt.figure(figsize=(6,4))
        sns.jointplot(timedata_edge1, timedata_edge2)
        plt.savefig('jointdist.png')

        return cov

    else:
        raise Exception('Cannot find covariance. One or both of the edges dont exist')


# Function that calculates expected travel time between two nodes using data samples
def calc_et(G, node1, node2):

    if G.has_edge(node1, node2):
        time_data = list(G[node1][node2]['time_data'].values())
        expected_time = np.mean(time_data)
        return expected_time
    else:
        raise Exception('No edge exists between the two nodes')

# ==============================================
if __name__ == "__main__":

    # Specifying routes - green and silver

    green_dt2iu = ['Lincoln Square Garage South,8', 'Green & Race (NW Corner),4',
         'Green & Cedar (NE Corner),1', 'Green & Birch (NE Corner),1',
         'Green & Orchard (NE Corner),1', 'Green & Busey (NE Corner),1',
         'Green & Gregory (NW Far Side),1', 'Green & Goodwin (NW Far Side),8',
         'Illini Union (North Side Shelter),2']


    silver_dt2iu = ['Lincoln Square Garage South,8','Springfield & Birch (NE Corner),1',
          'Springfield at Phillips Rec. Ctr (North),2', 'Springfield & Busey (NE Corner),1',
          'Springfield & Gregory St. (NE Corner),1', 'Springfield & Harvey (NE Corner),1',
          'Goodwin at Ceramics Building,1', 'Green & Goodwin (NW Far Side),8',
          'Illini Union (Island Shelter),9']

    green_dt2dt = ['Lincoln Square Garage South,8', 'Green & Race (NW Corner),4',
                   'Green & Cedar (NE Corner),1', 'Green & Birch (NE Corner),1',
                   'Green & Orchard (NE Corner),1', 'Green & Busey (NE Corner),1',
                   'Green & Gregory (NW Far Side),1', 'Green & Goodwin (NW Far Side),8',
                   'Illini Union (North Side Shelter),2', 'Green & Sixth (NE Corner),1',
                   'Green & Fourth (NE Corner),1', 'Green & Second (NE Corner),1',
                   'Green & Locust (NE Corner),1', 'Green & Neil (NE Far Side),5', 'Neil & Springfield (SE Corner),2',
                   'Neil & Marshall (SE Corner),2', 'Walnut & Logan (SE Corner),2', 'Walnut & University (SE Corner),2', 'Illinois Terminal (Platform A)']


    orange_dt2dt = ['Lincoln Square Courthouse,2', 'Save A Lot (East Side),2', 'Broadway & University (SE Corner),2',
                     'Broadway & Park (NW Far Side),8', 'Park & Central (NE Corner),1', 'Church & Orchard (NE Corner),1',
                     'Coler & Church (NE Corner),1', 'Church & Busey (NE Corner),1', 'Lincoln & Park (West Side),4',
                     'Campus Circle (North Side),2', 'University & Goodwin (NE Corner),1', 'Goodwin & Park (NW Far Side),8',
                     'Park & Romine (North Side),1', 'Park & Wright (NE Corner),1', 'University & Sixth (NW Far Side),8',
                     'University & Fourth (NE Corner),1', 'University & Second (NE Corner),1', 'Illinois Terminal (Platform A),1']

    yellow_iu2dt = ['Wright & Healey (East Side),2', 'White & Wright (SE Corner),2',
                    'White Street Mid-Block (North Side),2', 'White & Second (NE Corner),1', 'White & First (NE Corner),1',
                    'Illinois Terminal (Platform C),5']

    gy_dt2dt = green_dt2iu + yellow_iu2dt

    ROOT_PATH = 'D:\\Repos\\riskaware-planning'
#    G, list_trips = dp.extract_data(ROOT_PATH)
    node1, node2 =  'Springfield at Phillips Rec. Ctr (North),2', 'Springfield & Busey (NE Corner),1'
    node3, node4 =   'Springfield & Busey (NE Corner),1', 'Springfield & Gregory St. (NE Corner),1'
#    data = list(G[node1][node2]['time_data'].values())
#    plt.figure(figsize=(6,4))
#    sns.distplot(data, kde=False, fit=st.lognorm, color='b')
#    plt.xlabel('travel time (sec)')
#    plt.ylabel('probability')
#    plt.savefig('lognormal.png')
#    params = st.lognorm.fit(data)

    cov = calc_cov(G, node1, node2, node3, node4)

    # Find the expected travel time and reliability for given budget
    def find_reli(G, route, time_budget):

        mean = []
        sd = []
        temp = list(zip(route[:-1], route[1:]))
        for pair in zip(temp[:-1],temp[1:]):
            ((node1, node2), (node3, node4)) = pair
            dist_param = fit_dist(G, node1, node2)
            (mean_temp, sd_temp) = dist_param
            mean.append(mean_temp)
            sd.append(sd_temp)

        mean_path = sum(mean)
        sd_path = np.sqrt(sum(np.square(np.asarray(sd))))
        dist = st.norm(loc=mean_path, scale=sd_path)
        reli = dist.cdf(time_budget)
        return  reli, mean_path


    # Calculating for different routes
    reli_orange, mean_orange = find_reli(G, orange_dt2dt, 500)
    reli_green, mean_green = find_reli(G, green_dt2dt, 500)


    # Calculating for green plus orange
    reli_hybrid, mean_hybrid = find_reli(G, gy_dt2dt, 500)


# Dependent structure

# Building Model
    # Calculate covariances
    # Calculate means - Build multivariate normal
    # Take a sample - consider bus times

    # Run time simulations

#
#




