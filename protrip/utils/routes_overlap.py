def overlapping_edges(route_a, route_b):
    eda = set()
    for e in route_a.edges:
        eda.add((e.start, e.end))
    edb = set()
    for e in route_b.edges:
        edb.add((e.start, e.end))
    return eda.intersection(edb)

def overlapping_stops(route_a, route_b):
    sa = {s.id for s in route_a.stops}
    sb = {s.id for s in route_b.stops}
    return sa.intersection(sb)

def overlapping_segments(network, route_id_list):
    if not route_id_list:
        return set()
    if len(route_id_list)==1:
        r = network.get_route(route_id_list[0])
        if not r:
            return set()
        return {(e.start,e.end) for e in r.edges}
    common = None
    for rid in route_id_list:
        ro = network.get_route(rid)
        if not ro:
            return set()
        edgeset = {(e.start,e.end) for e in ro.edges}
        if common is None:
            common = edgeset
        else:
            common = common.intersection(edgeset)
        if not common:
            break
    return common or set()
