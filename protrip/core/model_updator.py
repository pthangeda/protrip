class ModelUpdater:
    """
    Updates distribution parameters in the DistributionManager.
    """
    def __init__(self, dist_manager):
        self.dm = dist_manager

    def ingest_observation(self, route_id, edges, times):
        """
        edges: list of (start_stop, end_stop)
        times: list of travel times for corresponding edges
        """
        if not edges or not times:
            return
        self.dm.update_online(route_id, edges, times)
