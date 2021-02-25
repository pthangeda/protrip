import pytest
import math
from protrip.core.data_model import TransitNetwork, Stop, Route, Trip
from protrip.core.distributions import DistributionManager
from protrip.core.simulator import TransitSimulator

@pytest.fixture
def small_net_and_sim():
    net = TransitNetwork()
    s1 = Stop("S1","FirstStop",40.0,-88.0)
    s2 = Stop("S2","SecondStop",40.01,-88.01)
    s3 = Stop("S3","ThirdStop",40.02,-88.02)
    for st in [s1,s2,s3]:
        net.add_stop(st)
    r = Route("R9","Route9",[s1,s2,s3])
    net.add_route(r)
    bus_data = [
        {"RouteID":"R9","TripID":"T9","StartStopID":"S1","EndStopID":"S2","TravelTime":"250"},
        {"RouteID":"R9","TripID":"T9","StartStopID":"S2","EndStopID":"S3","TravelTime":"300"}
    ]
    dm = DistributionManager(net,bus_data)
    dm.build_initial_models()
    sim = TransitSimulator(net, dm, step_size=0.001)
    trip_obj = Trip("T9",r,30000)
    net.add_trip(trip_obj)
    sim.initialize_trip("T9")
    return net, dm, sim

def test_sim_step(small_net_and_sim):
    net, dm, sim = small_net_and_sim
    for _ in range(1000):
        sim.step()
    assert sim.current_time==1.0
    assert len(sim.active_trips)==1
    for _ in range(30000):
        sim.step()
    assert len(sim.active_trips)==0

def test_sim_multi_init(small_net_and_sim):
    net, dm, sim = small_net_and_sim
    sim.initialize_trip("T9")
    sim.initialize_trip("T9") 
    assert len(sim.active_trips)==1
    for _ in range(5000):
        sim.step()
    assert len(sim.active_trips)==1
    for _ in range(350000):
        sim.step()
    assert len(sim.active_trips)==0

def test_sim_run_function(small_net_and_sim):
    net, dm, sim = small_net_and_sim
    sim.run(0.5)
    assert sim.current_time==0.5
    sim.run(1.5)
    assert sim.current_time==2.0
