import csv
import os
from collections import defaultdict
from ..core.data_model import Stop, Route, Trip, TransitNetwork

def parse_gtfs_folder(folder_path):
    """
    Reads standard GTFS files from folder_path:
      - agency.txt (optional)
      - stops.txt
      - routes.txt
      - trips.txt
      - stop_times.txt
    Builds and returns a TransitNetwork with stops, routes, and trips loaded.
    Minimally, we associate route -> set of stops based on stop_times
    """
    net = TransitNetwork()

    stops_file = os.path.join(folder_path, 'stops.txt')
    routes_file = os.path.join(folder_path, 'routes.txt')
    trips_file = os.path.join(folder_path, 'trips.txt')
    stop_times_file = os.path.join(folder_path, 'stop_times.txt')
    agency_file = os.path.join(folder_path, 'agency.txt')  # optional

    agency_info = {}
    if os.path.isfile(agency_file):
        agency_info = _read_agency_file(agency_file)

    stops_data = {}
    if os.path.isfile(stops_file):
        stops_data = _read_stops_file(stops_file)
        for sid, s in stops_data.items():
            net.add_stop(s)

    routes_data = {}
    if os.path.isfile(routes_file):
        routes_data = _read_routes_file(routes_file, agency_info)
        for rid, r_dict in routes_data.items():
            route_obj = Route(rid, r_dict['route_name'], [])
            net.add_route(route_obj)

    trips_data = {}
    if os.path.isfile(trips_file):
        # returns dict: trip_id -> { 'route_id': ..., 'service_id': ..., 'trip_headsign': ...}
        trips_data = _read_trips_file(trips_file)

    if os.path.isfile(stop_times_file):
        # returns a dict: trip_id -> list of (stop_id, arrival, departure, stop_sequence)
        trip_stop_times = _read_stop_times_file(stop_times_file)
        # Now we can build a route's stop sequence and create Trip objects
        # keyed by trip_id, each referencing route from route_id
        for t_id, lst in trip_stop_times.items():
            if t_id in trips_data:
                route_id = trips_data[t_id]['route_id']
      
                sorted_lst = sorted(lst, key=lambda x: x['stop_sequence'])
      
                r = net.get_route(route_id)
                if not r:
                    # fallback: create a new route if not found
                    r = Route(route_id, "Unknown Route", [])
                    net.add_route(r)
            
                if not r.stops:
                    route_stop_objs = []
                    for s_rec in sorted_lst:
                        sid = s_rec['stop_id']
                        if sid in stops_data:
                            route_stop_objs.append(stops_data[sid])
                  
                    r.stops = route_stop_objs
                   
                    r.edges = []
                    for i in range(len(r.stops) - 1):
                        from_s = r.stops[i].id
                        to_s = r.stops[i+1].id
                        r.edges.append(net.get_route(r.id).edges[i] if i < len(net.get_route(r.id).edges) 
                                       else _make_edge(from_s, to_s, r.id))
                  
                    net.add_route(r)

               
                headsign = trips_data[t_id].get('trip_headsign', 'Unknown')
               
                start_time = 0
                if sorted_lst:
                    stt = sorted_lst[0]['arrival_time_sec']
                    if stt is not None:
                        start_time = stt
                trip_obj = Trip(t_id, r, start_time)
                sched_dict = {}
                for s_rec in sorted_lst:
                    stp_id = s_rec['stop_id']
                    arr_t = s_rec['arrival_time_sec']
                    dep_t = s_rec['departure_time_sec']
                    sched_dict[stp_id] = (arr_t, dep_t)
                trip_obj.scheduled_times = sched_dict
                net.add_trip(trip_obj)

    return net

def _read_agency_file(filepath):
    """
    Returns basic info from agency.txt. If needed, we can map agency_id -> name, etc.
    """
    agency_info = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            agency_id = row.get('agency_id', 'default_agency')
            agency_name = row.get('agency_name', 'Unknown Agency')
            agency_info[agency_id] = agency_name
    return agency_info

def _read_stops_file(filepath):
    stops = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            sid = row.get('stop_id')
            name = row.get('stop_name', '')
            lat = float(row.get('stop_lat', 0.0))
            lon = float(row.get('stop_lon', 0.0))
            stops[sid] = Stop(sid, name, lat, lon)
    return stops

def _read_routes_file(filepath, agency_info):
    routes = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            rid = row.get('route_id')
            agency_id = row.get('agency_id', 'default_agency')
            route_long_name = row.get('route_long_name') or row.get('route_short_name', 'Unnamed Route')
            agency_nm = agency_info.get(agency_id, 'Unknown Agency')
            # You can store additional route info if you like
            routes[rid] = {
                'agency_id': agency_id,
                'agency_name': agency_nm,
                'route_name': route_long_name
            }
    return routes

def _read_trips_file(filepath):
    """
    Return trips_data = {
      trip_id: {
        'route_id': xyz,
        'service_id': abc,
        'trip_headsign': ???,
        ...
      }
    }
    """
    trips = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            t_id = row.get('trip_id')
            rt_id = row.get('route_id')
            sv_id = row.get('service_id')
            headsign = row.get('trip_headsign', '')
            trips[t_id] = {
                'route_id': rt_id,
                'service_id': sv_id,
                'trip_headsign': headsign
            }
    return trips

def _read_stop_times_file(filepath):
    """
    Return structure:
    {
      trip_id: [
        {
          'stop_id': stop_id,
          'arrival_time_sec': int or None,
          'departure_time_sec': int or None,
          'stop_sequence': int
        },
        ...
      ],
      ...
    }
    """
    trip_stop_times = defaultdict(list)
    with open(filepath, 'r', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            t_id = row.get('trip_id')
            s_id = row.get('stop_id')
            seq = int(row.get('stop_sequence', 0))
            arr_str = row.get('arrival_time', '')
            dep_str = row.get('departure_time', '')
            arr_sec = _time_to_sec(arr_str)
            dep_sec = _time_to_sec(dep_str)
            rec = {
                'stop_id': s_id,
                'arrival_time_sec': arr_sec,
                'departure_time_sec': dep_sec,
                'stop_sequence': seq
            }
            trip_stop_times[t_id].append(rec)
    return dict(trip_stop_times)

def _time_to_sec(timestr):
    """
    GTFS times can be HH:MM:SS, might exceed 24h if multi-day (like 27:30:00).
    We'll parse robustly.
    Returns integer seconds from midnight, ignoring day wrap for simplicity.
    """
    if not timestr:
        return None
    parts = timestr.split(':')
    if len(parts) < 2:
        return None
    try:
        h = int(parts[0])
        m = int(parts[1])
        s = int(parts[2]) if len(parts)>2 else 0
        return h*3600 + m*60 + s
    except ValueError:
        return None

def _make_edge(start_stop_id, end_stop_id, route_id):
  
    from ..core.data_model import Edge
    return Edge(start_stop_id, end_stop_id, route_id)
