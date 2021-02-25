import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import math
import numpy as np
from ..core.simulator import TransitSimulator

def animate_routes(network):
    fig, ax = plt.subplots()
    lines = []
    for r in network.routes.values():
        color = np.random.rand(3,)
        for e in r.edges:
            s1 = network.get_stop(e.start)
            s2 = network.get_stop(e.end)
            if s1 and s2:
                line, = ax.plot([s1.lon, s2.lon],[s1.lat, s2.lat], color=color, linewidth=1)
                lines.append(line)
    ax.set_aspect('equal')
    def update(frame):
        for ln in lines:
            ln.set_linewidth(random.uniform(0.5,4.0))
        return lines
    anim = FuncAnimation(fig, update, frames=50, interval=300, blit=False)
    plt.show()

def animate_stop_positions(network):
    fig, ax = plt.subplots()
    sc = ax.scatter([],[], s=20, c='blue')
    stops = list(network.stops.values())
    ax.set_aspect('equal')
    def init():
        ax.set_xlim(min(s.lon for s in stops)-0.01, max(s.lon for s in stops)+0.01)
        ax.set_ylim(min(s.lat for s in stops)-0.01, max(s.lat for s in stops)+0.01)
        return sc,
    def update(frame):
        x = []
        y = []
        for s in stops:
            x.append(s.lon + math.sin(frame*0.1)*0.0001)
            y.append(s.lat + math.cos(frame*0.1)*0.0001)
        sc.set_offsets(np.column_stack([x,y]))
        return sc,
    anim = FuncAnimation(fig, update, frames=100, init_func=init, interval=200, blit=False)
    plt.show()

def animate_simulation(sim, network, frames=30):
    fig, ax = plt.subplots()
    sc = ax.scatter([],[], s=50, c='red')
    for r in network.routes.values():
        col = np.random.rand(3,)
        for e in r.edges:
            s1 = network.get_stop(e.start)
            s2 = network.get_stop(e.end)
            if s1 and s2:
                ax.plot([s1.lon, s2.lon],[s1.lat, s2.lat], color=col, linewidth=1)
    ax.set_aspect('equal')
    def init():
        ax.set_xlim(min(s.lon for s in network.stops.values())-0.01, max(s.lon for s in network.stops.values())+0.01)
        ax.set_ylim(min(s.lat for s in network.stops.values())-0.01, max(s.lat for s in network.stops.values())+0.01)
        return sc,
    def update(frame):
        sim.step()
        x = []
        y = []
        for t, info in sim.active_trips.items():
            if info['current_index']<len(info['edges']):
                e = info['edges'][info['current_index']]
                s1 = network.get_stop(e.start)
                s2 = network.get_stop(e.end)
                if s1 and s2:
                    f = info['time_in_current']/20.0
                    xx = s1.lon + (s2.lon - s1.lon)*f
                    yy = s1.lat + (s2.lat - s1.lat)*f
                    x.append(xx)
                    y.append(yy)
        sc.set_offsets(np.column_stack([x,y]))
        return sc,
    ani = FuncAnimation(fig, update, frames=frames, init_func=init, interval=500, blit=False)
    plt.show()
