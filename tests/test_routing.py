import pytest
import math
from protrip.core.routing import OnlineAdaptiveRouter
from protrip.core.data_model import TransitNetwork, Stop, Route
from protrip.core.distributions import DistributionManager

@pytest.fixture
def dist_manager_and_network():
    net = TransitNetwork()
    s1 = Stop("A","Alpha",40.0,-88.0)
    s2 = Stop("B","Beta",40.0,-88.001)
    s3 = Stop("C","Gamma",40.001,-88.002)
    for s in [s1,s2,s3]:
        net.add_stop(s)
    r = Route("X","XRoute",[s1,s2,s3])
    net.add_route(r)
    bus_data = [
        {"RouteID":"X","TripID":"Tx1","StartStopID":"A","EndStopID":"B","TravelTime":"100"},
        {"RouteID":"X","TripID":"Tx1","StartStopID":"B","EndStopID":"C","TravelTime":"120"},
        {"RouteID":"X","TripID":"Tx2","StartStopID":"A","EndStopID":"B","TravelTime":"110"},
        {"RouteID":"X","TripID":"Tx2","StartStopID":"B","EndStopID":"C","TravelTime":"130"}
    ]
    dm = DistributionManager(net,bus_data)
    dm.build_initial_models()
    return dm, net

def test_online_adaptive_route_basic(dist_manager_and_network):
    dm, net = dist_manager_and_network
    router = OnlineAdaptiveRouter(dm, net, alpha=0.3, time_budget=300)
    p = router.route("A","C")
    assert p is not None
    assert len(p)==2
    val1 = p[0][0]
    val2 = p[1][0]
    assert val1=="A"
    assert val2=="B"

def test_online_update_and_reroute(dist_manager_and_network):
    dm, net = dist_manager_and_network
    router = OnlineAdaptiveRouter(dm, net, alpha=0.8, time_budget=999)
    path1 = router.route("A","C")
    dm.update_online("X",[("A","B")],[200.0])
    path2 = router.route("A","C")
    assert path1 is not None
    assert path2 is not None
    assert path1==path2

def test_no_route_scenario():
    net = TransitNetwork()
    dm = DistributionManager(net,[])
    router = OnlineAdaptiveRouter(dm, net, alpha=1, time_budget=600)
    p = router.route("Z1","Z2")
    assert p==None
