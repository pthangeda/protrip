import math
import matplotlib.pyplot as plt
import numpy as np

def highlight_transfers(network, transfer_stops):
    fig, ax = plt.subplots()
    for r in network.routes.values():
        c = np.random.rand(3,)
        for e in r.edges:
            s1 = network.get_stop(e.start)
            s2 = network.get_stop(e.end)
            if s1 and s2:
                ax.plot([s1.lon, s2.lon],[s1.lat, s2.lat], color=c, linewidth=1)
    for ts in transfer_stops:
        st = network.get_stop(ts)
        if st:
            ax.scatter(st.lon, st.lat, color='red', s=40, marker="s")
    ax.set_aspect('equal')
    plt.show()

def animate_transfer_activity(network, simulator, frames=30):
    fig, ax = plt.subplots()
    sc = ax.scatter([], [], c='red', s=40)
    for r in network.routes.values():
        cc = np.random.rand(3,)
        for e in r.edges:
            s1 = network.get_stop(e.start)
            s2 = network.get_stop(e.end)
            if s1 and s2:
                ax.plot([s1.lon, s2.lon],[s1.lat, s2.lat], c=cc, linewidth=1, alpha=0.3)
    def init():
        ax.set_xlim(min(s.lon for s in network.stops.values())-0.01, max(s.lon for s in network.stops.values())+0.01)
        ax.set_ylim(min(s.lat for s in network.stops.values())-0.01, max(s.lat for s in network.stops.values())+0.01)
        return sc,
    def update(i):
        simulator.step()
        xz = []
        yz = []
        for t, info in simulator.active_trips.items():
            if info['current_index']<len(info['edges']):
                ed = info['edges'][info['current_index']]
                s1 = network.get_stop(ed.start)
                s2 = network.get_stop(ed.end)
                if s1 and s2:
                    f = info['time_in_current']/30.0
                    xz.append(s1.lon + f*(s2.lon - s1.lon))
                    yz.append(s1.lat + f*(s2.lat - s1.lat))
        sc.set_offsets(np.column_stack([xz,yz]))
        return sc,
    import matplotlib.animation as animation
    ani = animation.FuncAnimation(fig, update, frames=frames, init_func=init, interval=500, blit=False)
    ax.set_aspect('equal')
    plt.show()

def plot_transfer_statistics(stats):
    fig, ax = plt.subplots()
    keys = [k for k in stats]
    vals = [stats[k] for k in stats]
    ax.bar(keys, vals, color='orange')
    plt.xticks(rotation=45)
    plt.show()
