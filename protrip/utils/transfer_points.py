def find_transfer_points(network):
    c = {}
    for rid, route in network.routes.items():
        for s in route.stops:
            if s.id not in c:
                c[s.id] = set()
            c[s.id].add(rid)
    transfers = {}
    for k,v in c.items():
        if len(v)>1:
            transfers[k]=v
    return transfers

def is_transfer_stop(network, stop_id):
    rid_set = set()
    for rid, r in network.routes.items():
        for s in r.stops:
            if s.id==stop_id:
                rid_set.add(rid)
    return len(rid_set)>1

def find_common_transfers(network, route1, route2):
    stops1 = {s.id for s in route1.stops}
    stops2 = {s.id for s in route2.stops}
    return stops1.intersection(stops2)
