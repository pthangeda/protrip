import math
import numpy as np
from .reliability import compute_reliability_normal

def weighted_sum(paths, alpha, dist_manager, time_budget):
    best_p = None
    best_val = float('inf')
    for p in paths:
        s = evaluate_path(dist_manager, p, alpha, time_budget)
        if s<best_val:
            best_val = s
            best_p = p
    return best_p

def evaluate_path(dist_manager, path, alpha, time_budget):
    et = 0
    rid_map = {}
    for e in path:
        rid = e[2]
        if rid not in rid_map:
            rid_map[rid] = []
        rid_map[rid].append((e[0], e[1]))
    used = 0
    rel = 1
    for rid,segs in rid_map.items():
        pm = dist_manager.get_distribution_params(rid)
        if not pm:
            m = 30*len(segs)
            v = 15*len(segs)
            remain = time_budget - used
            r = 0
            if remain>=0:
                r = compute_reliability_normal(m, v, remain)
            used += m
            rel *= r
            et += m
        else:
            idxs=[]
            for s,e in segs:
                i = pm['edge_index_map'].get((s,e),None)
                if i is not None:
                    idxs.append(i)
            if idxs:
                mv = pm['mean'][idxs].sum()
                c = pm['cov'][np.ix_(idxs,idxs)]
                var = c.sum() if c.size>1 else c.item() if c.size==1 else 0
                remain = time_budget - used
                r = 0
                if remain>=0:
                    r = compute_reliability_normal(mv, var, remain)
                used += mv
                rel *= r
                et += mv
    return alpha*et - (1-alpha)*rel

def pareto_front(paths, dist_manager, time_budget):
    scores = []
    for p in paths:
        et, rel = path_stats(dist_manager, p, time_budget)
        scores.append((p,et,rel))
    dominated = set()
    for i,(p1,e1,r1) in enumerate(scores):
        for j,(p2,e2,r2) in enumerate(scores):
            if i==j: continue
            if e2<=e1 and r2>=r1 and (e2<e1 or r2>r1):
                dominated.add(i)
    pf = []
    for i,(p,e,r) in enumerate(scores):
        if i not in dominated:
            pf.append((p,e,r))
    return pf

def path_stats(dist_manager, path, time_budget):
    rid_map={}
    for e in path:
        rid_map.setdefault(e[2],[]).append((e[0],e[1]))
    et=0
    used=0
    rel=1
    for rid,segs in rid_map.items():
        pm=dist_manager.get_distribution_params(rid)
        if not pm:
            base=30*len(segs)
            remain=time_budget-used
            r=0
            if remain>=0:
                r=0.5
            et+=base
            used+=base
            rel*=r
        else:
            idx=[]
            for s,e in segs:
                i=pm['edge_index_map'].get((s,e),None)
                if i is not None: idx.append(i)
            mm=0
            vv=0
            if idx:
                mm=pm['mean'][idx].sum()
                c=pm['cov'][np.ix_(idx,idx)]
                vv=c.sum() if c.size>1 else c.item() if c.size==1 else 0
            remain=time_budget-used
            r=0
            if remain>=0:
                r=compute_reliability_normal(mm,vv,remain)
            et+=mm
            used+=mm
            rel*=r
    return et, rel

def combine_objectives(e_time, reliability, alpha):
    return alpha*e_time - (1-alpha)*reliability
