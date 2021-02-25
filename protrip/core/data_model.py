import math

class Stop:
    def __init__(self, stop_id, name, lat, lon):
        self.id = stop_id
        self.name = name
        self.lat = lat
        self.lon = lon

class Edge:
    def __init__(self, start_stop, end_stop, route_id):
        self.start = start_stop
        self.end = end_stop
        self.route_id = route_id

class Route:
    def __init__(self, route_id, route_name, stop_sequence):
        self.id = route_id
        self.name = route_name
        self.stops = stop_sequence  # ordered list of Stop objects
        self.edges = []
        for i in range(len(self.stops) - 1):
            e = Edge(self.stops[i].id, self.stops[i+1].id, self.id)
            self.edges.append(e)

class Trip:
    def __init__(self, trip_id, route, start_time, scheduled_times=None):
        self.id = trip_id
        self.route = route
        self.start_time = start_time  # e.g. seconds from midnight or datetime
        self.scheduled_times = scheduled_times or {}  # stop_id -> (arr, dep)

class TransitNetwork:
    def __init__(self):
        self.stops = {}   # stop_id -> Stop
        self.routes = {}  # route_id -> Route
        self.trips = {}   # trip_id -> Trip
        self.adjacency = {}  # stop_id -> set of (next_stop_id, route_id)

    def add_stop(self, stop):
        self.stops[stop.id] = stop
        if stop.id not in self.adjacency:
            self.adjacency[stop.id] = set()

    def add_route(self, route):
        self.routes[route.id] = route
        for e in route.edges:
            if e.start not in self.adjacency:
                self.adjacency[e.start] = set()
            self.adjacency[e.start].add((e.end, route.id))

    def add_trip(self, trip):
        self.trips[trip.id] = trip

    def get_stop(self, stop_id):
        return self.stops.get(stop_id, None)

    def get_route(self, route_id):
        return self.routes.get(route_id, None)

    def get_trip(self, trip_id):
        return self.trips.get(trip_id, None)

    def get_neighbors(self, stop_id):
        return self.adjacency.get(stop_id, set())

    def all_stops(self):
        return list(self.stops.values())

    def all_routes(self):
        return list(self.routes.values())

    def all_trips(self):
        return list(self.trips.values())
