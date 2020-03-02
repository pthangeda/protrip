# -*- coding: utf-8 -*-
"""
Author: Pranay Thangeda
Email: contact@prny.me
Description: Tools for developing and updating the probabilistic travel time
model of a given transit network
"""

import numpy as np

class Model:

    def __init__(self, G, routes_dict):
        self.mean = self._calcmean(G, routes_dict)
        self.cov = self._calccov(G, routes_dict)
        self.numsamples = self._calcnumsamples(G, routes_dict)

    def _calcmean(self, G, routes_dict):
        """
        Evaluate mean time on edges in the road network using travel time
        samples.
        """
        mean = dict()
        for route_name, route_nodes in routes_dict.items():
            for pair in zip(route_nodes[:-1], route_nodes[1:]):

                if G.has_edge(pair[0], pair[1]):
                    time_data = list(G[pair[0]][pair[1]]['time_data'].values())

                    if len(time_data) == 0:
                        raise Exception('No data samples on the given edge')
                    else:
                        mean[pair] = np.mean(time_data)
                else:
                    raise Exception('Non existent edge in the route.')
        return mean


    def _calcnumsamples(self, G, routes_dict):
        """
        Calculate the number of samples on each valid route in the graph.
        """
        numsamples = dict()
        for route_name, route_nodes in routes_dict.items():
            num_samples = np.Inf
            for pair in zip(route_nodes[:-1], route_nodes[1:]):
                if G.has_edge(pair[0], pair[1]):
                    time_data = list(G[pair[0]][pair[1]]['time_data'].values())
                    n = len(time_data)
                    if n == 0:
                        raise Exception('No data samples on the given edge')
                    elif n < num_samples:
                        num_samples = n
                else:
                    raise Exception('Non existent edge in the route.')

            if num_samples == 0:
                raise Exception('An edge on the route has no samples')
            elif num_samples == np.Inf:
                raise Exception('No edge has valid number of samples')
            else:
                numsamples[route_name] = num_samples
        return numsamples

    def _calccov(self, G, routes_dict):
        """
        Calculate the covariance between different edges of a given route.
        """
        cov = dict()
        for route_name1, route_nodes1 in routes_dict.items():
            for pair1 in zip(route_nodes1[:-1], route_nodes1[1:]):
                for route_name2, route_nodes2 in routes_dict.items():
                    for pair2 in zip(route_nodes2[:-1], route_nodes2[1:]):

                        if G.has_edge(pair1[0], pair1[1]) and G.has_edge(pair2[0], pair2[1]):
                            dict_edge1 = G[pair1[0]][pair1[1]]['time_data']
                            dict_edge2 = G[pair2[0]][pair2[1]]['time_data']
                            common_trips = dict_edge1.keys() & dict_edge2.keys()

                            if len(common_trips) in [0, 1]:
                                cov[(pair1, pair2)] = 0
                            else:
                                timedata_edge1 = [dict_edge1.get(key) for key in common_trips]
                                timedata_edge2 = [dict_edge2.get(key) for key in common_trips]
                                cov[(pair1, pair2)] = np.cov(timedata_edge1,timedata_edge2)[0][1]
                        else:
                            raise Exception('Requested edges do not exist in the graph')
        return cov

    def calc_routemean(self, route):
        """
        Calculate the expected value of travel time on a given route object
        """
        nodelist = route.nodes
        meanlist = []
        for pair in zip(nodelist[:-1], nodelist[1:]):
            mean = self.mean[pair]
            meanlist.append[mean]
        return meanlist

    def calc_pathmean(self, path):
        """
        Calculate the expected travel time of a given path expressed as a series
        of nodes that denotes the path in the transit graph
        """
        nodelist = path
        meanlist = []
        for pair in zip(nodelist[:-1], nodelist[1:]):
            mean = self.mean[pair]
            meanlist.append[mean]
        return meanlist

    def updatemodel(self, trip):
        """
        Update the travel time model based on the latest recorded sample
        """
        pass

        time_sample = trip.history
        num_samples = trip.route.numsamples



# ==============================================
if __name__ == "__main__":
    pass
    # Add test code




