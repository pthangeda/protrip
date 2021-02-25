import pytest
import math
from protrip.core.data_model import TransitNetwork, Stop, Route, Trip, Edge

@pytest.fixture
def simple_network():
    net = TransitNetwork()
    s1 = Stop("S1","Stop1",40.0,-88.0)
    s2 = Stop("S2","Stop2",40.0002,-88.0003)
    s3 = Stop("S3","Stop3",40.0005,-88.0010)
    net.add_stop(s1)
    net.add_stop(s2)
    net.add_stop(s3)
    r = Route("R1","Route One",[s1,s2,s3])
    net.add_route(r)
    t = Trip("T1", r, 36000, {"S1":(36000,36000),"S2":(36120,36130),"S3":(36200,36200)})
    net.add_trip(t)
    return net

def test_add_stops_and_routes(simple_network):
    assert len(simple_network.stops)==3
    assert len(simple_network.routes)==1
    assert "S1" in simple_network.adjacency
    s2_neighbors = simple_network.get_neighbors("S2")
    assert len(s2_neighbors)==1
    assert list(s2_neighbors)[0][0]=="S3"

def test_trip_lookups(simple_network):
    trip = simple_network.get_trip("T1")
    assert trip.id=="T1"
    assert trip.route.id=="R1"
    sched_s2 = trip.scheduled_times.get("S2")
    assert sched_s2==(36120,36130)

def test_edge_structure(simple_network):
    r = simple_network.get_route("R1")
    assert len(r.edges)==2
    e = r.edges[0]
    assert e.start=="S1"
    assert e.end=="S2"
    e2 = r.edges[1]
    assert e2.start=="S2"
    assert e2.end=="S3"
    net = simple_network
    assert len(net.adjacency["S1"])==1
    assert ("S2","R1") in net.adjacency["S1"]
