import matplotlib.pyplot as plt
import math
import numpy as np

def show_experiment_outcomes(results):
    fig, ax = plt.subplots()
    for r in results:
        v = r.get('best_path')
        if v:
            length = len(v)
            alpha = r.get('alpha')
            tb = r.get('time_budget')
            ax.scatter(alpha, tb, s=length*20, label=r.get('experiment'), alpha=0.6)
    ax.legend()
    plt.show()

def plot_reliability_vs_time(data):
    fig, ax = plt.subplots()
    x = [d.get('time',0) for d in data]
    y = [d.get('reliability',0.0) for d in data]
    ax.plot(x, y, marker='o')
    ax.set_ylim(0,1.05)
    plt.show()

def plot_multiobjective_front(data):
    fig, ax = plt.subplots()
    e = [d.get('expected_time',0) for d in data]
    r = [d.get('reliability',0) for d in data]
    for i in range(len(e)):
        ax.scatter(e[i], r[i], c=np.random.rand(3,), s=40)
    ax.set_xlim(0, max(e)*1.2 if e else 10)
    ax.set_ylim(0,1.05)
    plt.show()

def route_comparison_plot(route_stats):
    fig, axs = plt.subplots(1,2, figsize=(10,4))
    nm = [rs['route_id'] for rs in route_stats]
    me = [rs['mean_time'] for rs in route_stats]
    cv = [rs['time_var'] for rs in route_stats]
    axs[0].bar(nm, me, color='green')
    axs[1].bar(nm, cv, color='blue')
    fig.tight_layout()
    plt.show()
