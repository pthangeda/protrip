import math
import time
import matplotlib.pyplot as plt
import numpy as np
from ..core.simulator import TransitSimulator

def show_simulator_state(sim, network):
    fig, ax = plt.subplots()
    for r in network.routes.values():
        c = np.random.rand(3,)
        for e in r.edges:
            s1 = network.get_stop(e.start)
            s2 = network.get_stop(e.end)
            if s1 and s2:
                ax.plot([s1.lon, s2.lon],[s1.lat, s2.lat], color=c, linewidth=1)
    x = []
    y = []
    for t, info in sim.active_trips.items():
        rid = info['route_id']
        idx = info['current_index']
        if idx < len(info['edges']):
            ed = info['edges'][idx]
            st1 = network.get_stop(ed.start)
            st2 = network.get_stop(ed.end)
            if st1 and st2:
                f = info['time_in_current']/30.0
                f = max(0,min(1,f))
                lx = st1.lon + (st2.lon - st1.lon)*f
                ly = st1.lat + (st2.lat - st1.lat)*f
                x.append(lx)
                y.append(ly)
    ax.scatter(x, y, color="red", s=50, marker="o")
    ax.set_aspect('equal')
    plt.show()

def live_simulation_view(sim, network, total_steps=10, step_time=0.5):
    for i in range(total_steps):
        sim.step()
        show_simulator_state(sim, network)
        time.sleep(step_time)

def generate_sim_progress_plot(sim, network, steps=50):
    positions = []
    for i in range(steps):
        sim.step()
        arr = []
        for t, info in sim.active_trips.items():
            if info['current_index'] < len(info['edges']):
                ed = info['edges'][info['current_index']]
                st1 = network.get_stop(ed.start)
                st2 = network.get_stop(ed.end)
                if st1 and st2:
                    frac = info['time_in_current']/30.0
                    lx = st1.lon + (st2.lon - st1.lon)*frac
                    ly = st1.lat + (st2.lat - st1.lat)*frac
                    arr.append((lx, ly))
        positions.append(arr)
    fig, ax = plt.subplots()
    for i, snapshot in enumerate(positions):
        xc = [p[0] for p in snapshot]
        yc = [p[1] for p in snapshot]
        ax.scatter(xc, yc, alpha=(i+1)/steps, s=(i+1)*3)
    ax.set_aspect('equal')
    plt.show()
