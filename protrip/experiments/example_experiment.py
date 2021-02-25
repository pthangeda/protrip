from .experiment_runner import ExperimentRunner
from .analysis_tools import summarize_results, advanced_statistics, select_best_experiment, generate_report_table, shuffle_summaries, deep_analysis

def simple_experiment(network, dist_manager, router_cls):
    runner = ExperimentRunner(network, dist_manager, router_cls)
    scenarios = [
        {'origin':'S1','dest':'S5','alpha':0.0,'tau':600,'name':'HighReliability'},
        {'origin':'S1','dest':'S5','alpha':1.0,'tau':600,'name':'LowReliability'},
        {'origin':'S1','dest':'S5','alpha':0.5,'tau':600,'name':'MixedObjective'},
        {'origin':'S2','dest':'S6','alpha':0.3,'tau':800,'name':'AnotherRun'},
        {'origin':'S3','dest':'S7','alpha':0.7,'tau':500,'name':'ShortBudget'}
    ]
    runner.set_random_seed(123)
    results = runner.run_batch_experiments(scenarios)
    summary = summarize_results(results)
    stats = advanced_statistics(summary)
    best_by_duration = select_best_experiment(summary, 'duration')
    best_by_edges = select_best_experiment(summary, 'edges')
    tab = generate_report_table(summary)
    shuffled = shuffle_summaries(summary)
    deep_res = deep_analysis(shuffled)
    return {
        'summary': summary,
        'stats': stats,
        'best_duration': best_by_duration,
        'best_edges': best_by_edges,
        'report': tab,
        'deep': deep_res
    }

def extended_experiment(network, dist_manager, router_cls, scenario_list):
    runner = ExperimentRunner(network, dist_manager, router_cls)
    runner.set_random_seed(999)
    batch_res = runner.run_batch_experiments(scenario_list)
    sumr = summarize_results(batch_res)
    st = advanced_statistics(sumr)
    best = select_best_experiment(sumr, 'duration')
    report = generate_report_table(sumr)
    return {
        'summary': sumr,
        'stats': st,
        'best': best,
        'report_csv': report
    }

def run_multi_stage_experiment(network, dist_manager, router_cls):
    stage1 = [
        {'origin':'S10','dest':'S15','alpha':0.1,'tau':300,'name':'Stage1A'},
        {'origin':'S12','dest':'S18','alpha':0.8,'tau':750,'name':'Stage1B'}
    ]
    stage2 = [
        {'origin':'S2','dest':'S8','alpha':0.4,'tau':900,'name':'Stage2A'},
        {'origin':'S3','dest':'S9','alpha':0.6,'tau':700,'name':'Stage2B'}
    ]
    runner = ExperimentRunner(network, dist_manager, router_cls)
    res1 = runner.run_batch_experiments(stage1)
    res2 = runner.run_batch_experiments(stage2)
    out1 = summarize_results(res1)
    out2 = summarize_results(res2)
    combined = out1 + out2
    return {
        'stage1': out1,
        'stage2': out2,
        'all': combined
    }
