import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WINDY_API_KEY = os.getenv("WINDY_API_KEY")

TAIWAN_CITIES_COORDS = {
    "臺北市": {"lat": 25.033, "lon": 121.565, "region": "臺灣北部海面"},
    "新北市": {"lat": 25.012, "lon": 121.465, "region": "臺灣北部海面"},
    "基隆市": {"lat": 25.128, "lon": 121.740, "region": "臺灣北部海面"},
    "桃園市": {"lat": 24.989, "lon": 121.313, "region": "臺灣北部海面"},
    "新竹市": {"lat": 24.813, "lon": 120.967, "region": "臺灣北部海面"},
    "新竹縣": {"lat": 24.838, "lon": 121.010, "region": "臺灣北部海面"},
    "苗栗縣": {"lat": 24.560, "lon": 120.821, "region": "臺灣中部海面"},
    "臺中市": {"lat": 24.147, "lon": 120.673, "region": "臺灣中部海面"},
    "彰化縣": {"lat": 24.081, "lon": 120.538, "region": "臺灣中部海面"},
    "南投縣": {"lat": 23.906, "lon": 120.686, "region": "臺灣中部海面"},
    "雲林縣": {"lat": 23.709, "lon": 120.542, "region": "臺灣中部海面"},
    "嘉義市": {"lat": 23.479, "lon": 120.450, "region": "臺灣南部海面"},
    "嘉義縣": {"lat": 23.459, "lon": 120.293, "region": "臺灣南部海面"},
    "臺南市": {"lat": 22.999, "lon": 120.218, "region": "臺灣南部海面"},
    "高雄市": {"lat": 22.627, "lon": 120.302, "region": "臺灣南部海面"},
    "屏東縣": {"lat": 22.666, "lon": 120.486, "region": "臺灣南部海面"},
    "宜蘭縣": {"lat": 24.757, "lon": 121.753, "region": "臺灣東北部海面"},
    "花蓮縣": {"lat": 23.977, "lon": 121.604, "region": "臺灣東部海面"},
    "臺東縣": {"lat": 22.756, "lon": 121.150, "region": "臺灣東南部海面"},
    "澎湖縣": {"lat": 23.571, "lon": 119.579, "region": "臺灣東南部海面"},
    "金門縣": {"lat": 24.436, "lon": 118.378, "region": "臺灣東南部海面"},
    "連江縣": {"lat": 26.160, "lon": 119.951, "region": "臺灣東南部海面"}
}

class WindyService:
    """
    Service class to handle configurations and embed links for Windy.com maps.
    """
    
    @staticmethod
    def is_api_key_configured():
        """Returns True if a valid WINDY_API_KEY is found in environment variables."""
        return bool(WINDY_API_KEY)
        
    @staticmethod
    def get_embed_url(layer_name):
        """Deprecated: Returns default center embed URL."""
        return WindyService.get_synced_embed_url(layer_name, 23.7, 120.96)
        
    @staticmethod
    def get_synced_embed_url(layer_name, lat, lon, zoom=8):
        """
        Returns the appropriate Windy.com embed URL centered at the selected coordinates.
        Supports standard CWA/Windy layers.
        """
        # Map element layers to Windy overlay keys
        layer_map = {
            "Temperature": "temp",
            "Wind": "wind",
            "Rain": "rain",
            "Clouds": "clouds",
            "Pressure": "pressure",
            # Traditional translations fallback
            "氣溫": "temp",
            "風速風向": "wind",
            "雨量": "rain",
            "雷達": "radar",
            "天氣": "clouds",
            "濕度": "rh"
        }
        
        overlay = layer_map.get(layer_name, "wind")
        
        # If API key is configured, we can append it if Windy premium widget supports it,
        # otherwise we utilize the standard embed parameter format.
        key_param = f"&key={WINDY_API_KEY}" if WINDY_API_KEY else ""
        
        url = (
            f"https://embed.windy.com/embed2.html?"
            f"lat={lat}&lon={lon}&zoom={zoom}&level=surface&overlay={overlay}"
            f"&menu=&message=&marker=&calendar=now&pressure="
            f"&type=map&location=coordinates&detail=&metricWind=default"
            f"&metricTemp=default&radarRange=-1{key_param}"
        )
        return url
