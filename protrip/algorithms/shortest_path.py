from collections import defaultdict, deque

def dijkstra_or_breadth(network, origin, destination):
    cands = []
    visited = set()
    queue = deque([(origin, [])])
    while queue:
        cur, path = queue.popleft()
        if cur == destination:
            cands.append(path)
        if cur in visited:
            continue
        visited.add(cur)
        neighbors = network.get_neighbors(cur)
        for nb, rid in neighbors:
            new_path = path + [(cur, nb, rid)]
            queue.append((nb, new_path))
    return cands

def all_pairs_shortest_path(network):
    nodes = list(network.stops.keys())
    dist = {}
    for n in nodes:
        dist[n] = {}
        for m in nodes:
            if n == m:
                dist[n][m] = (0, [])
            else:
                dist[n][m] = (float('inf'), [])
    for n in nodes:
        neighbors = network.get_neighbors(n)
        for nb, rid in neighbors:
            dist[n][nb] = (1, [(n, nb, rid)])
    for k in nodes:
        for i in nodes:
            for j in nodes:
                di, pi = dist[i][k]
                dk, pk = dist[k][j]
                if di + dk < dist[i][j][0]:
                    dist[i][j] = (di + dk, pi + pk)
    return dist

def route_exists(network, origin, destination):
    visited = set()
    stack = [origin]
    while stack:
        x = stack.pop()
        if x == destination:
            return True
        if x not in visited:
            visited.add(x)
            for nb, _ in network.get_neighbors(x):
                if nb not in visited:
                    stack.append(nb)
    return False
