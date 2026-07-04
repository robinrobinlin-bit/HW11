# Compatibility wrapper pointing to services/cwa_service.py
from services.cwa_service import format_obs_time

class ObservationService:
    """
    Wrapper class routing to services/cwa_service.py for backward compatibility.
    """
    
    @staticmethod
    def get_latest_observations():
        from services.cwa_service import fetch_realtime_observations
        return fetch_realtime_observations()
        
    @staticmethod
    def get_extremes(observations):
        from services.cwa_service import compute_extremes
        return compute_extremes(observations)
        
    @staticmethod
    def format_obs_time(raw_time):
        return format_obs_time(raw_time)
