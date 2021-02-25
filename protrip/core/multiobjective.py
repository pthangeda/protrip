import math
import numpy as np
from ..algorithms.reliability import compute_reliability_normal

def compute_objective_value(exp_time, reliability, alpha, beta=1.0):
    return alpha*exp_time*beta - (1-alpha)*reliability

def multiobjective_route_evaluation(dist_mgr, path, alpha, time_budget):
    """
    For each (route_id, stop_sequence) in path, compute expected time & reliability
    """
    route_grouping = {}
    for edge in path:
        rid = edge[2]
        if rid not in route_grouping:
            route_grouping[rid] = []
        route_grouping[rid].append((edge[0], edge[1]))
    total_expected = 0


    cumul_time = 0
    cumul_reli = 1.0
    for rid, segs in route_grouping.items():
        params = dist_mgr.get_distribution_params(rid)
        if not params:
            continue
        mean = params['mean']
        cov  = params['cov']
        e_map = params['edge_index_map']
        idxs = [ e_map[(s,e)] for (s,e) in segs if (s,e) in e_map ]
        sub_mean = mean[idxs]
        sub_cov  = cov[np.ix_(idxs, idxs)]
        seg_et = sub_mean.sum()
        total_expected += seg_et
       
        if len(idxs)==0:
            continue
        m = sub_mean.sum()
        v = np.sum(sub_cov) if sub_cov.size > 1 else sub_cov.item() if sub_cov.size==1 else 0
        remaining = time_budget - cumul_time
        r = compute_reliability_normal(m, v, remaining)
        cumul_reli *= r
        cumul_time += seg_et
    return compute_objective_value(total_expected, cumul_reli, alpha, 1.0)
