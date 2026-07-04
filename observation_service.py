import datetime
from fetch_observations import fetch_realtime_observations, compute_extremes

class ObservationService:
    """
    Service class to handle CWA station observations and metrics calculations.
    """
    
    @staticmethod
    def get_latest_observations():
        """
        Fetches the latest real-time station observations from CWA.
        """
        return fetch_realtime_observations()
        
    @staticmethod
    def get_extremes(observations):
        """
        Computes the highest/lowest temperatures, max rain, and max wind speed.
        """
        return compute_extremes(observations)
        
    @staticmethod
    def format_obs_time(raw_time):
        """
        Formats CWA ISO timestamp into display strings.
        """
        if not raw_time:
            now = datetime.datetime.now()
            return now.strftime("%m/%d %H:%M"), now.strftime("%Y-%m-%d %H:%M:%S")
        try:
            dt = datetime.datetime.fromisoformat(raw_time)
            return dt.strftime("%m/%d %H:%M"), dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            now = datetime.datetime.now()
            return now.strftime("%m/%d %H:%M"), now.strftime("%Y-%m-%d %H:%M:%S")
