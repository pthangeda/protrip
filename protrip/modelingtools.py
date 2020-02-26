# -*- coding: utf-8 -*-
"""
Description: Tools for modeling the data in the transit network

Author: Pranay Thangeda
Email: contact@prny.me
"""

def extract_transferpoints(routes_list):
    """
    Given a list of route objects, create potential transfer points for
    every route in the list. In case of multiple consecutive TP between the
    same two routes, the last TP is considered as the TP and the rest are ignored.
    """

    for route in routes_list:
        route_nodes = route.nodes
        for node in route_nodes:




    # Should this be route object instead of route list? Maybe it should be.

