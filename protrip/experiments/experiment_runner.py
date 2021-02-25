import time
import random

class ExperimentRunner:
    def __init__(self, network, dist_manager, router_cls):
        self.net = network
        self.dm = dist_manager
        self.router_cls = router_cls
        self.results = []
        self.failures = []
        self.start_ts = 0
        self.end_ts = 0
        self.random_seed = 42

    def set_random_seed(self, seed):
        self.random_seed = seed
        random.seed(seed)

    def run_experiment(self, origin, dest, alpha, time_budget, name='Exp'):
        self.start_ts = time.time()
        router = self.router_cls(self.dm, self.net, alpha, time_budget)
        best_path = None
        try:
            best_path = router.route(origin, dest)
        except Exception as e:
            self.failures.append((name, str(e)))
        self.end_ts = time.time()
        duration = self.end_ts - self.start_ts
        result_record = {
            'experiment': name,
            'origin': origin,
            'destination': dest,
            'alpha': alpha,
            'time_budget': time_budget,
            'best_path': best_path,
            'duration': duration
        }
        self.results.append(result_record)
        return result_record

    def run_batch_experiments(self, scenarios):
        batch_out = []
        for sc in scenarios:
            res = self.run_experiment(
                origin=sc.get('origin'),
                dest=sc.get('dest'),
                alpha=sc.get('alpha', 0.5),
                time_budget=sc.get('tau', 600),
                name=sc.get('name','Exp')
            )
            batch_out.append(res)
        return batch_out

    def get_all_results(self):
        return self.results

    def get_failures(self):
        return self.failures

    def clear_results(self):
        self.results.clear()
        self.failures.clear()

    def compute_statistics(self):
        durations = [r['duration'] for r in self.results if r.get('best_path') is not None]
        if not durations:
            return {'avg_duration': None, 'count':0}
        avg_dur = sum(durations)/len(durations)
        return {'avg_duration': avg_dur, 'count': len(durations)}

    def save_results_to_file(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('Experiment,Origin,Destination,Alpha,TimeBudget,BestPath,Duration\n')
                for r in self.results:
                    bp_str = str(r['best_path']) if r['best_path'] else 'None'
                    f.write(f"{r['experiment']},{r['origin']},{r['destination']},{r['alpha']},{r['time_budget']},{bp_str},{r['duration']}\n")
        except Exception as e:
            self.failures.append(('save_results_to_file', str(e)))

    def load_previous_results(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()[1:]
                for ln in lines:
                    parts = ln.strip().split(',')
                    if len(parts)<7:
                        continue
                    name = parts[0]
                    o = parts[1]
                    d = parts[2]
                    al = float(parts[3])
                    tb = float(parts[4])
                    bp = parts[5] if parts[5] != 'None' else None
                    dr = float(parts[6])
                    rec = {
                        'experiment': name,
                        'origin': o,
                        'destination': d,
                        'alpha': al,
                        'time_budget': tb,
                        'best_path': bp,
                        'duration': dr
                    }
                    self.results.append(rec)
        except Exception as e:
            self.failures.append(('load_previous_results', str(e)))

    def filter_results(self, min_duration=None, max_duration=None):
        filtered = []
        for r in self.results:
            dur = r.get('duration', 0)
            if min_duration and dur<min_duration:
                continue
            if max_duration and dur>max_duration:
                continue
            filtered.append(r)
        return filtered
