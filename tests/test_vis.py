import pytest
import os
import matplotlib
matplotlib.use('Agg')
from protrip.core.data_model import TransitNetwork, Stop, Route
from protrip.vis.route_map import plot_route_map, show_selected_routes, overlay_transfer_points
from protrip.vis.simulator_view import show_simulator_state, generate_sim_progress_plot
from protrip.core.distributions import DistributionManager
from protrip.core.simulator import TransitSimulator

@pytest.fixture
def basic_network():
    net = TransitNetwork()
    s1 = Stop("A","StopA",40.0,-88.0)
    s2 = Stop("B","StopB",40.001,-88.002)
    net.add_stop(s1)
    net.add_stop(s2)
    r = Route("XY","XYRoute",[s1,s2])
    net.add_route(r)
    return net

def test_plot_route_map(basic_network):
    try:
        plot_route_map(basic_network,(5,4))
    except Exception as e:
        assert False

def test_show_selected_routes(basic_network):
    try:
        show_selected_routes(basic_network,["XY"])
    except:
        assert False

def test_overlay_transfer_points(basic_network):
    try:
        overlay_transfer_points(basic_network,["A"])
    except:
        assert False

def test_simulator_view_plot(basic_network):
    dist = DistributionManager(basic_network,[])
    dist.build_initial_models()
    sim = TransitSimulator(basic_network,dist,step_size=0.0001)
    try:
        show_simulator_state(sim,basic_network)
        generate_sim_progress_plot(sim,basic_network,steps=10)
    except:
        assert False
