import time
import math
import random
import numpy as np

class TransitSimulator:
    def __init__(self, network, distribution_manager, step_size=1.0):
        self.network = network
        self.dm = distribution_manager
        self.step_size = step_size
        self.current_time = 0
        self.active_trips = {}
        self.completed_trips = {}
        self.random_events = {}
        self.closures = {}
        self.event_prob = 0.01
        self.max_event_duration = 300
        self.max_additional_delay = 120
        self.dwell_times = {}
        self.accumulated_data = {}

    def initialize_trip(self, trip_id):
        trip = self.network.get_trip(trip_id)
        if not trip: return
        if not trip.route: return
        edges = trip.route.edges[:]
        if not edges: return
        self.active_trips[trip_id] = {
            'route_id': trip.route.id,
            'edges': edges,
            'index': 0,
            'time_in_edge': 0,
            'collected': {},
            'start_sim_time': self.current_time,
            'finished': False,
            'skip_next_stop': False,
            'acc_delay': 0
        }

    def step(self):
        self.current_time += self.step_size
        self.generate_random_events()
        self.resolve_active_events()
        finished = []
        for tid, info in self.active_trips.items():
            if info['finished']: 
                finished.append(tid)
                continue
            if info['index']>=len(info['edges']):
                info['finished']=True
                finished.append(tid)
                continue
            rid = info['route_id']
            e = info['edges'][info['index']]
            cmodel = self.dm.get_distribution_params(rid)
            if not cmodel:
                mean_t = 30
                var_t = 10
            else:
                idx = cmodel['edge_index_map'].get((e.start, e.end), None)
                if idx is None:
                    mean_t = 30
                    var_t = 20
                else:
                    mean_t = cmodel['mean'][idx]
                    var_t = cmodel['cov'][idx, idx] if idx<len(cmodel['cov']) else 20
            base_time = random.gauss(mean_t, math.sqrt(abs(var_t)))
            base_time = max(1, base_time)
            if self.closures.get((rid, e.start, e.end), False):
                base_time += self.max_additional_delay
            if info['skip_next_stop']:
                base_time = base_time*0.8
            if self.dwell_times.get((rid,e.end), None):
                base_time += self.dwell_times[(rid,e.end)]
            info['time_in_edge'] += self.step_size
            if info['time_in_edge'] + info['acc_delay'] >= base_time:
                et = info['time_in_edge'] + info['acc_delay']
                info['collected'][(e.start,e.end)] = et
                info['index']+=1
                info['time_in_edge']=0
                info['acc_delay']=0
                if random.random()<0.05:
                    info['skip_next_stop']=True
                else:
                    info['skip_next_stop']=False
        for t in finished:
            rec = self.active_trips[t]
            self.dm.update_online(rec['route_id'], list(rec['collected'].keys()), list(rec['collected'].values()))
            self.completed_trips[t] = rec
            del self.active_trips[t]

    def run(self, duration):
        steps = int(duration/self.step_size)
        for _ in range(steps):
            self.step()
            time.sleep(0.0001)

    def generate_random_events(self):
        if random.random()<self.event_prob:
            rid = random.choice(list(self.network.routes.keys()))
            r = self.network.get_route(rid)
            if r and r.edges:
                eg = random.choice(r.edges)
                self.random_events[(rid,eg.start,eg.end)] = {
                    'start_time': self.current_time,
                    'duration': random.randint(30, self.max_event_duration),
                    'type': 'closure' if random.random()<0.5 else 'delay'
                }

    def resolve_active_events(self):
        expired = []
        for k,v in self.random_events.items():
            st = v['start_time']
            dur = v['duration']
            if self.current_time > (st+dur):
                expired.append(k)
            else:
                if v['type']=='closure':
                    self.closures[k] = True
                else:
                    for tid,info in self.active_trips.items():
                        if info['route_id']==k[0]:
                            if info['index']<len(info['edges']):
                                ce = info['edges'][info['index']]
                                if (ce.start,ce.end)==(k[1],k[2]):
                                    info['acc_delay'] += self.step_size
        for e in expired:
            if e in self.random_events:
                del self.random_events[e]
            if e in self.closures:
                del self.closures[e]

    def get_active_trips(self):
        return self.active_trips

    def get_completed_trips(self):
        return self.completed_trips

    def update_dwell_time(self, route_id, stop_id, dwell_seconds):
        self.dwell_times[(route_id,stop_id)] = dwell_seconds

    def clear_dwell_time(self, route_id, stop_id):
        if (route_id,stop_id) in self.dwell_times:
            del self.dwell_times[(route_id,stop_id)]

    def reset(self):
        self.current_time=0
        self.active_trips={}
        self.completed_trips={}
        self.random_events={}
        self.closures={}
        self.dwell_times={}
        self.accumulated_data={}
