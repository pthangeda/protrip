import numpy as np

class DistributionManager:
    """
    Manages the travel-time distributions across all edges/routes.
    Allows for correlated travel times within each route.
    """
    def __init__(self, network, raw_bus_data):
        self.network = network
        self.raw_bus_data = raw_bus_data
        self.models = {}

    def build_initial_models(self):
        """
        Estimates initial mean/cov for each route using raw data.
        Assumes each route's edges can be treated as a multivariate normal distribution.
        """
        for route in self.network.all_routes():
            edges = route.edges
            edge_map = {}
            for i, e in enumerate(edges):
                edge_map[(e.start, e.end)] = i
            M = len(edges)
            data_matrix = []  # each row = [time_e1, time_e2, ..., time_eM]
            # parse raw data for route
            # group trips by route
            trip_records = self._collect_trip_records(route.id)
            # build samples
            for rec in trip_records:
                row = [None]*M
                for (start, end), t in rec.get('segments', {}).items():
                    if (start, end) in edge_map:
                        row[edge_map[(start, end)]] = float(t)
                if not any(v is None for v in row):
                    data_matrix.append(row)
            if len(data_matrix) < 2:
                mean_vec = np.zeros(M)
                cov_mat = np.eye(M)
            else:
                arr = np.array(data_matrix)
                mean_vec = np.mean(arr, axis=0)
                cov_mat = np.cov(arr, rowvar=False)
            self.models[route.id] = {
                'edges': [(e.start, e.end) for e in edges],
                'mean': mean_vec,
                'cov': cov_mat,
                'edge_index_map': edge_map,
                'samples_count': max(1, len(data_matrix))
            }

    def _collect_trip_records(self, route_id):
        # { 'trip_id': X, 'segments': { (start_stop, end_stop): travel_time, ... } }
        grouped = {}
        for row in self.raw_bus_data:
            if row.get('RouteID') == str(route_id):
                tid = row.get('TripID')
                if tid not in grouped:
                    grouped[tid] = {'trip_id': tid, 'segments': {}}
                seg = (row.get('StartStopID'), row.get('EndStopID'))
                if seg[0] and seg[1]:
                    grouped[tid]['segments'][seg] = row.get('TravelTime')
        return list(grouped.values())

    def get_distribution_params(self, route_id):
        return self.models.get(route_id, None)

    def update_online(self, route_id, observed_edges, observed_times):
        """
        ObservedEdges: list of (start_stop, end_stop) for which we have times
        observedTimes: list of floats
        We'll do an approximate update of the route's mean/cov using MLE incremental update.
        """
        model = self.models.get(route_id, None)
        if not model: return
        mean_vec = model['mean']
        cov_mat = model['cov']
        edge_map = model['edge_index_map']
        m_count = model['samples_count']
        for (se, st) in zip(observed_edges, observed_times):
            idx = edge_map.get(se, None)
            if idx is not None:
                old_mu = mean_vec[idx]
                new_mu = (m_count*old_mu + st)/(m_count+1)
                mean_vec[idx] = new_mu
        for (se, st) in zip(observed_edges, observed_times):
            i = edge_map.get(se, None)
            if i is not None:
                diff = (st - mean_vec[i])
                cov_mat[i,i] = (m_count*cov_mat[i,i] + diff*diff)/(m_count+1)
        model['mean'] = mean_vec
        model['cov'] = cov_mat
        model['samples_count'] += 1

    def conditional_distribution(self, route_id, known_segments, known_times):
        model = self.models.get(route_id, None)
        if not model: return None, None, []
        mean = model['mean']
        cov = model['cov']
        edges = model['edges']
        idx_map = model['edge_index_map']
        if len(known_segments)==0:
            return mean, cov, edges
        obs_idx = []
        unobs_idx = []
        for i, e in enumerate(edges):
            if e in known_segments:
                obs_idx.append(i)
            else:
                unobs_idx.append(i)
        obs_idx = np.array(obs_idx)
        unobs_idx = np.array(unobs_idx)
        mo = mean[obs_idx]
        mu = mean[unobs_idx]
        Sigma_oo = cov[np.ix_(obs_idx, obs_idx)]
        Sigma_ou = cov[np.ix_(obs_idx, unobs_idx)]
        Sigma_uo = cov[np.ix_(unobs_idx, obs_idx)]
        Sigma_uu = cov[np.ix_(unobs_idx, unobs_idx)]
        obs_val = np.array(known_times)
        # conditional mean
        try:
            Sigma_oo_inv = np.linalg.inv(Sigma_oo)
            cond_mean = mu + Sigma_uo.dot(Sigma_oo_inv).dot((obs_val - mo))
            cond_cov = Sigma_uu - Sigma_uo.dot(Sigma_oo_inv).dot(Sigma_ou)
        except np.linalg.LinAlgError:
            cond_mean = mu
            cond_cov = Sigma_uu
        unobs_edges = [edges[i] for i in unobs_idx]
        return cond_mean, cond_cov, unobs_edges
