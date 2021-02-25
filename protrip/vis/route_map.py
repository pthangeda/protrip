import math
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from matplotlib.colors import ListedColormap
import random
from ..core.data_model import TransitNetwork

def plot_route_map(network, figsize=(10,8)):
    fig, ax = plt.subplots(figsize=figsize)
    routes_cmap = ListedColormap(["#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(len(network.routes))])
    lines = []
    idx = 0
    rid_to_idx = {}
    for i, r in enumerate(network.routes.values()):
        rid_to_idx[r.id] = i
    for r in network.routes.values():
        c = routes_cmap(rid_to_idx[r.id])
        for e in r.edges:
            s1 = network.get_stop(e.start)
            s2 = network.get_stop(e.end)
            if s1 and s2:
                lines.append(((s1.lon, s1.lat),(s2.lon, s2.lat),c))
    lc = []
    for l in lines:
        lc.append([(l[0][0], l[0][1]),(l[1][0], l[1][1])])
    coll = mc.LineCollection(lc, array=[l[2] for l in lines], cmap=routes_cmap, linewidths=2)
    ax.add_collection(coll)
    xs = []
    ys = []
    for s in network.stops.values():
        xs.append(s.lon)
        ys.append(s.lat)
    ax.scatter(xs, ys, color="black", s=10)
    for s in network.stops.values():
        ax.text(s.lon+0.0002, s.lat+0.0002, s.name, fontsize=8, rotation=random.randint(0,10))
    ax.autoscale()
    ax.set_aspect('equal')
    plt.show()

def show_selected_routes(network, route_ids):
    fig, ax = plt.subplots()
    for r in network.routes.values():
        c = "#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
        if r.id in route_ids:
            for e in r.edges:
                st1 = network.get_stop(e.start)
                st2 = network.get_stop(e.end)
                if st1 and st2:
                    ax.plot([st1.lon, st2.lon],[st1.lat, st2.lat], c=c, linewidth=3)
    for s in network.stops.values():
        ax.scatter(s.lon, s.lat, color="black", s=12)
    ax.autoscale()
    ax.set_aspect('equal')
    plt.show()

def overlay_transfer_points(network, transfer_stops):
    fig, ax = plt.subplots()
    col = []
    for r in network.routes.values():
        c = "#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
        for e in r.edges:
            st1 = network.get_stop(e.start)
            st2 = network.get_stop(e.end)
            if st1 and st2:
                ax.plot([st1.lon, st2.lon],[st1.lat, st2.lat], color=c, alpha=0.5, linewidth=1)
    for ts in transfer_stops:
        stp = network.get_stop(ts)
        if stp:
            ax.scatter(stp.lon, stp.lat, color="red", s=40, marker="s")
    ax.autoscale()
    ax.set_aspect('equal')
    plt.show()
