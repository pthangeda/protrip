import math
from ..algorithms.shortest_path import dijkstra_or_breadth
from ..core.multiobjective import multiobjective_route_evaluation, compute_objective_value
from ..algorithms.mo_optimization import evaluate_path
from ..algorithms.reliability import compute_reliability_normal

class OnlineAdaptiveRouter:
    def __init__(self, distribution_manager, network, alpha=0.5, time_budget=600, single_transfer=True, multi_transfer=False):
        self.dm = distribution_manager
        self.net = network
        self.alpha = alpha
        self.budget = time_budget
        self.single_transfer = single_transfer
        self.multi_transfer = multi_transfer
        self.transfer_points = {}
        self.build_transfer_points()

    def build_transfer_points(self):
        counts = {}
        for rid,route in self.net.routes.items():
            for s in route.stops:
                counts[s.id] = counts.get(s.id, set())
                counts[s.id].add(rid)
        for sid,v in counts.items():
            if len(v)>1:
                self.transfer_points[sid] = v

    def route(self, origin_id, dest_id):
        if not self.multi_transfer:
            if self.single_transfer:
                return self.best_single_transfer_path(origin_id, dest_id)
            else:
                return self.direct_or_fail(origin_id, dest_id)
        else:
            return self.best_multi_transfer_path(origin_id, dest_id)

    def direct_or_fail(self, origin_id, dest_id):
        cands = dijkstra_or_breadth(self.net, origin_id, dest_id)
        best = None
        best_val = float('inf')
        for path in cands:
            val = multiobjective_route_evaluation(self.dm, path, self.alpha, self.budget)
            if val<best_val:
                best_val=val
                best=path
        return best

    def best_single_transfer_path(self, origin_id, dest_id):
        direct_cands = dijkstra_or_breadth(self.net, origin_id, dest_id)
        best_direct = None
        best_dscore = float('inf')
        for d in direct_cands:
            sc = multiobjective_route_evaluation(self.dm, d, self.alpha, self.budget)
            if sc<best_dscore:
                best_dscore=sc
                best_direct=d
        best_combo = None
        best_cscore = float('inf')
        for tstop in self.transfer_points:
            cand1 = dijkstra_or_breadth(self.net, origin_id, tstop)
            cand2 = dijkstra_or_breadth(self.net, tstop, dest_id)
            for c1 in cand1:
                v1 = evaluate_path(self.dm, c1, self.alpha, self.budget)
                if v1>99999:
                    continue
                t1 = self._expected_reliability(c1)
                remain = self.budget - self._expected_time(c1)
                for c2 in cand2:
                    v2 = evaluate_path(self.dm, c2, self.alpha, remain)
                    if v2>99999:
                        continue
                    t2 = self._expected_reliability(c2)
                    tot_et = self._expected_time(c1)+self._expected_time(c2)
                    tot_rel = t1*t2
                    tot_val = compute_objective_value(tot_et, tot_rel, self.alpha, 1.0)
                    if tot_val<best_cscore:
                        best_cscore=tot_val
                        best_combo=c1+c2
        if best_direct is None and best_combo is None:
            return None
        if best_direct is not None and best_combo is not None:
            return best_direct if best_dscore<best_cscore else best_combo
        if best_direct is None:
            return best_combo
        return best_direct

    def best_multi_transfer_path(self, origin_id, dest_id):
        cands = dijkstra_or_breadth(self.net, origin_id, dest_id)
        best_val = float('inf')
        best_path = None
        for p in cands:
            v = multiobjective_route_evaluation(self.dm, p, self.alpha, self.budget)
            if v<best_val:
                best_val=v
                best_path=p
        paths_to_expand = [p for p in cands if len(p)>0]
        expanded_best = best_path
        expanded_val = best_val
        for path in paths_to_expand:
            segs = self._split_on_transfer(path)
            if len(segs)<2:
                continue
            tot_et=0
            tot_rel=1
            used_time=0
            for idx, seg in enumerate(segs):
                me, mv = self._segment_mean_var(seg)
                remain = self.budget - used_time
                r = compute_reliability_normal(me, mv, remain)
                tot_et+=me
                tot_rel*=r
                used_time+=me
            val = compute_objective_value(tot_et, tot_rel, self.alpha, 1.0)
            if val<expanded_val:
                expanded_val=val
                expanded_best=path
        return expanded_best

    def _split_on_transfer(self, path):
        groups = []
        temp = []
        for edge in path:
            temp.append(edge)
            end_stop = edge[1]
            if end_stop in self.transfer_points:
                groups.append(temp)
                temp=[]
        if temp:
            groups.append(temp)
        return groups

    def _expected_time(self, path):
        rid_segments = {}
        s=0
        for edge in path:
            rid = edge[2]
            if rid not in rid_segments:
                rid_segments[rid]=[]
            rid_segments[rid].append((edge[0],edge[1]))
        for rid,segs in rid_segments.items():
            p = self.dm.get_distribution_params(rid)
            if p:
                idxs = []
                for (st,en) in segs:
                    i = p['edge_index_map'].get((st,en), None)
                    if i is not None: idxs.append(i)
                if idxs:
                    m = sum(p['mean'][idxs])
                    s+=m
            else:
                s+=30*len(segs)
        return s

    def _expected_reliability(self, path):
        rid_segs={}
        used=0
        rel=1
        for edge in path:
            rid=edge[2]
            if rid not in rid_segs:
                rid_segs[rid]=[]
            rid_segs[rid].append((edge[0],edge[1]))
        for rid, segs in rid_segs.items():
            p=self.dm.get_distribution_params(rid)
            if not p: 
                m=30*len(segs)
                v=15*len(segs)
                remain=self.budget-used
                r=0
                if remain>=0:
                    r=self._cdf_normal(remain,m,math.sqrt(v))
                rel*=r
                used+=m
                continue
            idxs=[]
            for (st,en) in segs:
                i=p['edge_index_map'].get((st,en),None)
                if i is not None: idxs.append(i)
            if not idxs:
                continue
            m = p['mean'][idxs].sum()
            c = p['cov'][np.ix_(idxs,idxs)]
            v = c.sum() if c.size>1 else c.item() if c.size==1 else 0
            remain=self.budget-used
            r=0
            if remain>=0:
                r=self._cdf_normal(remain,m,math.sqrt(abs(v)))
            rel*=r
            used+=m
        return rel

    def _cdf_normal(self, x, mean, stdev):
        if stdev<1e-9:
            if mean<=x: return 1.0
            return 0.0
        z=(x-mean)/stdev
        return 0.5*(1+math.erf(z/1.4142135623730951))

    def update_and_route(self, origin_id, dest_id, observed_route_id, observed_edges, observed_times):
        self.dm.update_online(observed_route_id, observed_edges, observed_times)
        return self.route(origin_id, dest_id)

    def _segment_mean_var(self, seg):
        rid_map={}
        for e in seg:
            if e[2] not in rid_map:
                rid_map[e[2]]=[]
            rid_map[e[2]].append((e[0],e[1]))
        mt=0
        vv=0
        for rid, pairs in rid_map.items():
            param=self.dm.get_distribution_params(rid)
            if not param:
                mt+=30*len(pairs)
                vv+=20*len(pairs)
            else:
                idxs=[]
                for (s,e) in pairs:
                    i=param['edge_index_map'].get((s,e),None)
                    if i is not None: idxs.append(i)
                m=0
                c=0
                if idxs:
                    m=param['mean'][idxs].sum()
                    cmat=param['cov'][np.ix_(idxs,idxs)]
                    if cmat.size>1: c=cmat.sum()
                    elif cmat.size==1: c=cmat.item()
                mt+=m
                vv+=c
        return mt, vv
