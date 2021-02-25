import os
import csv
import math
from collections import defaultdict

class BusDataParser:
    """
    Parses and organizes real-time or historical bus data files containing columns like:
      - Type
      - Stop
      - Actual arr
      - Actual dep
      - Sched. arr
      - Sched. dep
      - Diff. arr
      - Diff. dep
      - Odometer
      - Sched. total distance
      - Distance
      - Graphic
      - V [mph]
      - RouteID
      - TripID
      - StartStopID
      - EndStopID
      - TravelTime
    After loading, provides methods for:
      - Accessing data for each route/trip
      - Aggregating travel-time stats
      - Building segments of data (StartStopID -> EndStopID times)
      - Generating average speed/delay reports
    """

    def __init__(self):
       
        self.raw_records = []

     
        self.route_records = defaultdict(list)
        self.trip_records = defaultdict(list)
       
        self.segments_data = defaultdict(list)

        self.route_stats_cache = {}
        self.trip_stats_cache = {}

    def parse_file(self, csv_filepath):
        """
        Parse a single bus data CSV file and incorporate into internal data structures.
        """
        if not os.path.isfile(csv_filepath):
            print(f"[BusDataParser] File not found: {csv_filepath}")
            return

        with open(csv_filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rec = {}
            
                for k,v in row.items():
                    rec[k.strip()] = v.strip() if isinstance(v, str) else v

               
                route_id = rec.get('RouteID')
                trip_id = rec.get('TripID')
                s_stop = rec.get('StartStopID')
                e_stop = rec.get('EndStopID')
                ttime = rec.get('TravelTime')

                # Convert numeric fields to floats or ints where appropriate
                if ttime is not None and ttime != '':
                    try:
                        rec['TravelTime'] = float(ttime)
                    except ValueError:
                        rec['TravelTime'] = None

                odom = rec.get('Odometer')
                if odom:
                    try:
                        rec['Odometer'] = float(odom)
                    except ValueError:
                        rec['Odometer'] = None

                self.raw_records.append(rec)

                if route_id:
                    self.route_records[route_id].append(rec)
                if trip_id:
                    self.trip_records[trip_id].append(rec)
                if route_id and s_stop and e_stop:
                    if rec['TravelTime'] is not None:
                        key = (route_id, s_stop, e_stop)
                        self.segments_data[key].append(rec['TravelTime'])

    def parse_folder(self, folder_path):
        """
        Parse all .csv files in a given folder.
        """
        if not os.path.isdir(folder_path):
            print(f"[BusDataParser] Folder not found: {folder_path}")
            return
        for fn in os.listdir(folder_path):
            if fn.lower().endswith('.csv'):
                full_path = os.path.join(folder_path, fn)
                self.parse_file(full_path)

    def get_all_records(self):
        return self.raw_records

    def get_route_records(self, route_id):
        return self.route_records.get(route_id, [])

    def get_trip_records(self, trip_id):
        return self.trip_records.get(trip_id, [])

    def build_segment_times(self):
        """
        Builds an aggregated dictionary for quick distribution stats:
          (RouteID, StartStopID, EndStopID) -> [list_of_travel_times].
        """
        segs = defaultdict(list)
        for rec in self.raw_records:
            rid = rec.get('RouteID')
            s = rec.get('StartStopID')
            e = rec.get('EndStopID')
            t = rec.get('TravelTime')
            if rid and s and e and t is not None:
                segs[(rid,s,e)].append(t)
        self.segments_data = segs

    def get_segment_times(self, route_id, start_stop, end_stop):
        """
        Returns a list of all travel times recorded between start_stop and end_stop for the given route.
        """
        return self.segments_data.get((route_id, start_stop, end_stop), [])

    def compute_basic_stats(self, values):
        """
        Given a list of numeric values, returns a dict with count, mean, std, min, max.
        """
        if not values:
            return {'count':0, 'mean':None, 'std':None, 'min':None, 'max':None}
        cnt = len(values)
        mn = sum(values)/cnt
        vr = sum([(x-mn)**2 for x in values])/(cnt-1) if cnt>1 else 0
        stdv = math.sqrt(vr)
        return {
            'count': cnt,
            'mean': mn,
            'std': stdv,
            'min': min(values),
            'max': max(values)
        }

    def generate_route_stats(self, route_id):
        """
        Generate summary stats for a route. For instance:
          - total trips
          - average travel time across route
          - average speed (if data present)
          - typical delays
        Caches the result in self.route_stats_cache.
        """
        recs = self.route_records.get(route_id, [])
        if not recs:
            return {}
        # Travel times
        tt_list = [r['TravelTime'] for r in recs if r.get('TravelTime') is not None]
        stats_tt = self.compute_basic_stats(tt_list)
        # Speeds
        speed_list = []
        for r in recs:
            v = r.get('V [mph]')
            if v:
                try:
                    speed_list.append(float(v))
                except ValueError:
                    pass
        stats_spd = self.compute_basic_stats(speed_list)

        arr_delays = []
        dep_delays = []
        for r in recs:
            d_arr = r.get('Diff. arr')
            d_dep = r.get('Diff. dep')
            if d_arr:
                arr_delays.append(_parse_time_diff(d_arr))
            if d_dep:
                dep_delays.append(_parse_time_diff(d_dep))
        stats_arr_del = self.compute_basic_stats([x for x in arr_delays if x is not None])
        stats_dep_del = self.compute_basic_stats([x for x in dep_delays if x is not None])

        out = {
            'num_records': len(recs),
            'travel_time_stats': stats_tt,
            'speed_stats': stats_spd,
            'arrival_delay_stats': stats_arr_del,
            'departure_delay_stats': stats_dep_del
        }
        self.route_stats_cache[route_id] = out
        return out

    def generate_trip_stats(self, trip_id):
        """
        Generate summary stats for a single Trip across the entire data set.
        (If there are multiple entries for the same trip, we aggregate them.)
        """
        recs = self.trip_records.get(trip_id, [])
        if not recs:
            return {}
        tt_list = [r['TravelTime'] for r in recs if r.get('TravelTime') is not None]
        stats_tt = self.compute_basic_stats(tt_list)
        out = {
            'trip_id': trip_id,
            'num_records': len(recs),
            'travel_time_stats': stats_tt
        }
        self.trip_stats_cache[trip_id] = out
        return out

    def build_travel_time_per_trip_route(self):
        """
        Example method:
        Returns structure for each (RouteID, TripID) -> average travel time.
        """
        out = {}
        for rec in self.raw_records:
            rid = rec.get('RouteID')
            tid = rec.get('TripID')
            t  = rec.get('TravelTime')
            if rid and tid and t is not None:
                out.setdefault((rid, tid), []).append(t)
        for k,v in out.items():
            out[k] = sum(v)/len(v)
        return out

def _parse_time_diff(diff_str):
    """
    If diff_str is something like '0:02:36' representing hh:mm:ss or mm:ss,
    parse it into total seconds. Otherwise return None if invalid.
    """
    if not diff_str: return None
    parts = diff_str.split(':')
    try:
        if len(parts)==3:
            hh, mm, ss = parts
        elif len(parts)==2:
            hh = 0
            mm, ss = parts
        else:
            return None
        hh, mm, ss = int(hh), int(mm), int(ss)
        return hh*3600 + mm*60 + ss
    except:
        return None
