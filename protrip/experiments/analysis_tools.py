import math
import statistics
import random

def analyze_path(path):
    edge_count = len(path) if path else 0
    routes = set()
    for e in path or []:
        routes.add(e[2])
    return {
        'edges_count': edge_count,
        'distinct_routes': len(routes)
    }

def summarize_results(experiment_results):
    summ = []
    for r in experiment_results:
        p = r.get('best_path', None)
        meta = analyze_path(p)
        summ.append({
            'experiment': r.get('experiment'),
            'origin': r.get('origin'),
            'destination': r.get('destination'),
            'alpha': r.get('alpha'),
            'time_budget': r.get('time_budget'),
            'duration': r.get('duration'),
            'edges_count': meta['edges_count'],
            'distinct_routes': meta['distinct_routes']
        })
    return summ

def advanced_statistics(summaries):
    durations = [x['duration'] for x in summaries if x['duration'] is not None]
    edges = [x['edges_count'] for x in summaries if x['edges_count'] is not None]
    if len(durations)<2:
        return {'mean_dur': None, 'stdev_dur':None, 'edge_max':None}
    return {
        'mean_dur': statistics.mean(durations),
        'stdev_dur': statistics.pstdev(durations),
        'edge_max': max(edges) if edges else None
    }

def select_best_experiment(summaries, criterion='duration'):
    if not summaries:
        return None
    if criterion=='duration':
        return min(summaries, key=lambda x: x['duration'] if x['duration'] else float('inf'))
    if criterion=='edges':
        return min(summaries, key=lambda x: x['edges_count'])
    return summaries[0]

def find_outliers(summaries, z_thresh=2.0):
    durs = [x['duration'] for x in summaries if x['duration'] is not None]
    if not durs:
        return []
    mean_v = statistics.mean(durs)
    stdev_v = statistics.pstdev(durs)
    outliers = []
    for rec in summaries:
        dur = rec.get('duration')
        if dur is not None:
            z = (dur - mean_v)/(stdev_v+1e-9)
            if abs(z)>z_thresh:
                outliers.append(rec)
    return outliers

def generate_report_table(summaries):
    rows = []
    for s in summaries:
        rows.append(f"{s['experiment']},{s['origin']},{s['destination']},{s['alpha']},{s['time_budget']},{s['duration']},{s['edges_count']},{s['distinct_routes']}")
    return "\n".join(rows)

def shuffle_summaries(summaries):
    random.shuffle(summaries)
    return summaries

def deep_analysis(summaries, filter_fun=None):
    filtered = [x for x in summaries if not filter_fun or filter_fun(x)]
    stats = advanced_statistics(filtered)
    outliers = find_outliers(filtered)
    return {
        'stats': stats,
        'outliers': outliers,
        'filtered_count': len(filtered)
    }
