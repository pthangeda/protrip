import math
import numpy as np

def compute_reliability_normal(mean, var, t):
    if t<0: return 0
    if var<1e-12: return 1 if mean<=t else 0
    z = (t-mean)/math.sqrt(var)
    return 0.5*(1+math.erf(z/1.4142135623730951))

def path_reliability(network, dist_manager, path, time_budget):
    used = 0
    r = 1
    rid_map = {}
    for e in path:
        rid = e[2]
        if rid not in rid_map:
            rid_map[rid] = []
        rid_map[rid].append((e[0], e[1]))
    for rid,segs in rid_map.items():
        pm = dist_manager.get_distribution_params(rid)
        if not pm:
            m = 30*len(segs)
            v = 15*len(segs)
            remain = time_budget - used
            r *= compute_reliability_normal(m, v, remain) if remain>0 else 0
            used += m
        else:
            idxs = []
            for sst, est in segs:
                i = pm['edge_index_map'].get((sst,est), None)
                if i is not None:
                    idxs.append(i)
            if idxs:
                m = pm['mean'][idxs].sum()
                c = pm['cov'][np.ix_(idxs, idxs)]
                var = c.sum() if c.size>1 else c.item() if c.size==1 else 0
                remain = time_budget - used
                r *= compute_reliability_normal(m, var, remain) if remain>0 else 0
                used += m
    return r

def reliability_threshold_paths(paths, network, dist_manager, time_budget, threshold):
    valid = []
    for p in paths:
        rel = path_reliability(network, dist_manager, p, time_budget)
        if rel>=threshold:
            valid.append(p)
    return valid

def reliability_distribution(dist_manager, route_id, times, mean, cov):
    obs = []
    for t in times:
        z = (t - mean)/math.sqrt(cov) if cov>1e-9 else 0
        obs.append(0.5*(1+math.erf(z/1.4142135623730951)))
    return obs
