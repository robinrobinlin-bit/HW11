import os
import json
import requests
import datetime
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CWA APIs
FORECAST_API_URL = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0012-001"
OBSERVATIONS_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"

TARGET_REGIONS = [
    "臺灣北部海面",
    "臺灣中部海面",
    "臺灣南部海面",
    "臺灣東北部海面",
    "臺灣東部海面",
    "臺灣東南部海面"
]

TAIWAN_COUNTIES = {
    "基隆市": [25.13, 121.74],
    "臺北市": [25.03, 121.56],
    "新北市": [25.01, 121.46],
    "桃園市": [24.99, 121.31],
    "新竹市": [24.81, 120.97],
    "新竹縣": [24.83, 121.01],
    "苗栗縣": [24.56, 120.82],
    "臺中市": [24.15, 120.68],
    "彰化縣": [24.08, 120.54],
    "南投縣": [23.91, 120.69],
    "雲林縣": [23.71, 120.54],
    "嘉義市": [23.48, 120.45],
    "嘉義縣": [23.46, 120.30],
    "臺南市": [23.00, 120.20],
    "高雄市": [22.63, 120.30],
    "屏東縣": [22.67, 120.49],
    "宜蘭縣": [24.75, 121.75],
    "花蓮縣": [23.98, 121.60],
    "臺東縣": [22.76, 121.15],
    "澎湖縣": [23.57, 119.57],
    "金門縣": [24.44, 118.38],
    "連江縣": [26.16, 119.95]
}

# ==================== WEEKLY FORECAST SERVICES ====================

def generate_mock_forecast_json():
    """Generates high-fidelity mock weather forecast data."""
    print("[INFO] Generating mock weather forecast data...")
    today = datetime.date.today()
    locations = []
    
    temp_ranges = {
        "臺灣北部海面": (25, 30),
        "臺灣中部海面": (26, 32),
        "臺灣南部海面": (27, 33),
        "臺灣東北部海面": (24, 29),
        "臺灣東部海面": (25, 31),
        "臺灣東南部海面": (26, 32)
    }
    
    for loc_name in TARGET_REGIONS:
        min_base, max_base = temp_ranges[loc_name]
        mint_time_series = []
        maxt_time_series = []
        
        for i in range(7):
            forecast_date = today + datetime.timedelta(days=i)
            day_offset = (i * 7) % 3 - 1
            mint_val = min_base + day_offset
            maxt_val = max_base + day_offset
            
            start_str = f"{forecast_date}T12:00:00+08:00"
            end_str = f"{forecast_date + datetime.timedelta(days=1)}T00:00:00+08:00"
            
            mint_time_series.append({
                "startTime": start_str,
                "endTime": end_str,
                "parameter": {"parameterName": str(mint_val), "parameterUnit": "C"}
            })
            maxt_time_series.append({
                "startTime": start_str,
                "endTime": end_str,
                "parameter": {"parameterName": str(maxt_val), "parameterUnit": "C"}
            })
            
        locations.append({
            "locationName": loc_name,
            "weatherElement": [
                {"elementName": "MinT", "time": mint_time_series},
                {"elementName": "MaxT", "time": maxt_time_series}
            ]
        })
        
    return {
        "cwaopendata": {
            "dataset": {
                "locations": {
                    "location": locations
                }
            }
        }
    }

def _raw_fetch_forecast() -> dict:
    """Uncached core logic for forecast queries."""
    api_key = os.getenv("CWA_TOKEN") or os.getenv("CWA_API_KEY")
    if not api_key:
        print("[WARNING] CWA API key not found. Using mock forecast data.")
        return generate_mock_forecast_json()
        
    params = {"Authorization": api_key, "format": "JSON"}
    try:
        print(f"[INFO] Fetching forecast from CWA: {FORECAST_API_URL}...")
        response = requests.get(FORECAST_API_URL, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] API failed with status {response.status_code}. Using mock forecast.")
            return generate_mock_forecast_json()
    except Exception as e:
        print(f"[ERROR] Connection error: {e}. Using mock forecast.")
        return generate_mock_forecast_json()

def fetch_weather_forecast() -> dict:
    """Fetches regional weekly weather forecasts from CWA API (with 30-min Streamlit cache)."""
    try:
        import streamlit as st
        # Wrapped cached function inside
        @st.cache_data(ttl=1800)
        def _cached_fetch() -> dict:
            return _raw_fetch_forecast()
        return _cached_fetch()
    except Exception:
        # Fallback if called outside Streamlit context (e.g. standalone test scripts)
        return _raw_fetch_forecast()

def extract_forecast_temperature(data: dict) -> list:
    """Parses forecast JSON and extracts MinT and MaxT values."""
    root_key = "cwaopendata" if "cwaopendata" in data else "cwbopendata" if "cwbopendata" in data else None
    if not root_key:
        print("[WARNING] Unknown root key. Falling back to mock data.")
        return extract_forecast_temperature(generate_mock_forecast_json())
        
    locations = data[root_key].get("dataset", {}).get("locations", {}).get("location", [])
    extracted_data = []
    api_lacks_temp = False
    
    for loc in locations:
        loc_name = loc.get("locationName")
        is_target = any(target in loc_name for target in TARGET_REGIONS) or any(loc_name in target for target in TARGET_REGIONS)
        if not is_target:
            continue
            
        elements = loc.get("weatherElement", [])
        mint_times, maxt_times = [], []
        for elem in elements:
            elem_name = elem.get("elementName", "")
            if elem_name in ["MinT", "mint"]:
                mint_times = elem.get("time", [])
            elif elem_name in ["MaxT", "maxt"]:
                maxt_times = elem.get("time", [])
                
        if not mint_times or not maxt_times:
            api_lacks_temp = True
            continue
            
        for t_min, t_max in zip(mint_times, maxt_times):
            start_time = t_min.get("startTime", "")
            if not start_time:
                continue
            date_str = start_time.split("T")[0]
            mint_val = float(t_min.get("parameter", {}).get("parameterName", 0))
            maxt_val = float(t_max.get("parameter", {}).get("parameterName", 0))
            
            extracted_data.append({
                "regionName": loc_name,
                "dataDate": date_str,
                "mint": mint_val,
                "maxt": maxt_val
            })
            
    if api_lacks_temp or not extracted_data:
        print("[INFO] Forecast response missing temperatures. Injecting mock forecast values...")
        return extract_forecast_temperature(generate_mock_forecast_json())
        
    return extracted_data

# ==================== LIVE OBSERVATIONS SERVICES ====================

def generate_mock_observations():
    """Generates mock observations for 362 stations."""
    stations = []
    special_stations = [
        {"name": "竹田國中", "county": "屏東縣", "lat": 22.58, "lon": 120.52, "temp": 35.5, "rain": 2.0, "wind": 2.5},
        {"name": "玉山", "county": "南投縣", "lat": 23.47, "lon": 120.95, "temp": 17.9, "rain": 0.0, "wind": 4.2},
        {"name": "鹿陶洋", "county": "臺南市", "lat": 23.12, "lon": 120.48, "temp": 35.5, "rain": 1.0, "wind": 3.1},
        {"name": "東吉島", "county": "澎湖縣", "lat": 23.26, "lon": 119.67, "temp": 30.2, "rain": 0.0, "wind": 8.0}
    ]
    
    for s in special_stations:
        stations.append({
            "StationName": s["name"],
            "StationId": f"MOCK{random.randint(1000, 9999)}",
            "ObsTime": "2026-07-04T10:30:00+08:00",
            "lat": s["lat"],
            "lon": s["lon"],
            "CountyName": s["county"],
            "TownName": "觀測站",
            "TEMP": s["temp"],
            "HUMD": random.randint(55, 85),
            "WDSD": s["wind"],
            "RAIN": s["rain"]
        })
        
    counties_list = list(TAIWAN_COUNTIES.keys())
    for i in range(358):
        county = random.choice(counties_list)
        base_lat, base_lon = TAIWAN_COUNTIES[county]
        lat = base_lat + random.uniform(-0.15, 0.15)
        lon = base_lon + random.uniform(-0.15, 0.15)
        
        is_mountain = random.random() < 0.05
        temp = round(random.uniform(16.0, 22.0), 1) if is_mountain else round(random.uniform(28.0, 34.5), 1)
        rain = round(random.choice([0.0]*15 + [0.5, 1.0, 1.5]), 1)
        wind = round(random.uniform(0.5, 6.5), 1)
        humidity = random.randint(60, 90)
        
        stations.append({
            "StationName": f"{county}測站{i+1}",
            "StationId": f"MOCK{i+1000:04d}",
            "ObsTime": "2026-07-04T10:30:00+08:00",
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "CountyName": county,
            "TownName": "觀測鎮",
            "TEMP": temp,
            "HUMD": humidity,
            "WDSD": wind,
            "RAIN": rain
        })
        
    return stations

def _raw_fetch_observations():
    """Uncached core logic for CWA observations API."""
    api_key = os.getenv("CWA_TOKEN") or os.getenv("CWA_API_KEY")
    if not api_key:
        print("[WARNING] CWA API key not found. Using mock observations.")
        return generate_mock_observations()
        
    params = {"Authorization": api_key, "format": "JSON"}
    try:
        print(f"[INFO] Fetching observations from CWA: {OBSERVATIONS_API_URL}...")
        response = requests.get(OBSERVATIONS_API_URL, params=params, timeout=15)
        if response.status_code == 200:
            raw_data = response.json()
            stations_raw = raw_data.get("records", {}).get("Station", [])
            parsed_stations = []
            
            for s in stations_raw:
                try:
                    wgs84_coords = None
                    coords = s.get("GeoInfo", {}).get("Coordinates", [])
                    for coord in coords:
                        if coord.get("CoordinateName") == "WGS84":
                            wgs84_coords = coord
                            break
                    if not wgs84_coords and coords:
                        wgs84_coords = coords[0]
                        
                    lat = float(wgs84_coords.get("StationLatitude", 0)) if wgs84_coords else 0.0
                    lon = float(wgs84_coords.get("StationLongitude", 0)) if wgs84_coords else 0.0
                    if lat == 0.0 or lon == 0.0:
                        continue
                        
                    elements = s.get("WeatherElement", {})
                    temp_str = elements.get("AirTemperature", "-99")
                    temp = float(temp_str) if temp_str not in ["-99", "-99.0", "None", ""] else -99.0
                    
                    rain_now = elements.get("Now", {})
                    rain_str = rain_now.get("Precipitation", "0.0") if isinstance(rain_now, dict) else "0.0"
                    rain = float(rain_str) if float(rain_str) >= 0 else 0.0
                    
                    wind_str = elements.get("WindSpeed", "0.0")
                    wind = float(wind_str) if float(wind_str) >= 0 else 0.0
                    
                    humd_str = elements.get("RelativeHumidity", "0")
                    humd = int(humd_str) if humd_str not in ["-99", "None", ""] else 0
                    
                    parsed_stations.append({
                        "StationName": s.get("StationName", "未知"),
                        "StationId": s.get("StationId", "未知"),
                        "ObsTime": s.get("ObsTime", {}).get("DateTime", ""),
                        "lat": lat,
                        "lon": lon,
                        "CountyName": s.get("GeoInfo", {}).get("CountyName", "未知"),
                        "TownName": s.get("GeoInfo", {}).get("TownName", "未知"),
                        "TEMP": temp,
                        "HUMD": humd,
                        "WDSD": wind,
                        "RAIN": rain
                    })
                except Exception:
                    continue
                    
            if not parsed_stations:
                return generate_mock_observations()
            return parsed_stations
        else:
            print(f"[ERROR] API failed with status {response.status_code}. Using mock observations.")
            return generate_mock_observations()
    except Exception as e:
        print(f"[ERROR] Connection error: {e}. Using mock observations.")
        return generate_mock_observations()

def fetch_realtime_observations():
    """Fetches live weather station observations from CWA API (with 5-min Streamlit cache)."""
    try:
        import streamlit as st
        # Wrapped cached function inside
        @st.cache_data(ttl=300)
        def _cached_fetch():
            return _raw_fetch_observations()
        return _cached_fetch()
    except Exception:
        # Fallback if called outside Streamlit context
        return _raw_fetch_observations()

def compute_extremes(stations):
    """Computes high temperature, low temperature, max rainfall, and max wind speed."""
    valid_temp_stations = [s for s in stations if s["TEMP"] > -50]
    
    max_temp_st = max(valid_temp_stations, key=lambda x: x["TEMP"]) if valid_temp_stations else None
    min_temp_st = min(valid_temp_stations, key=lambda x: x["TEMP"]) if valid_temp_stations else None
    max_rain_st = max(stations, key=lambda x: x["RAIN"]) if stations else None
    max_wind_st = max(stations, key=lambda x: x["WDSD"]) if stations else None
    
    return {
        "max_temp": {"val": max_temp_st["TEMP"], "name": max_temp_st["StationName"]} if max_temp_st else {"val": 0.0, "name": "無"},
        "min_temp": {"val": min_temp_st["TEMP"], "name": min_temp_st["StationName"]} if min_temp_st else {"val": 0.0, "name": "無"},
        "max_rain": {"val": max_rain_st["RAIN"], "name": max_rain_st["StationName"]} if max_rain_st else {"val": 0.0, "name": "無"},
        "max_wind": {"val": max_wind_st["WDSD"], "name": max_wind_st["StationName"]} if max_wind_st else {"val": 0.0, "name": "無"}
    }

def format_obs_time(raw_time):
    """Formats raw CWA observation ISO datetime strings into display timestamps."""
    if not raw_time:
        now = datetime.datetime.now()
        return now.strftime("%m/%d %H:%M"), now.strftime("%Y-%m-%d %H:%M:%S")
    try:
        dt = datetime.datetime.fromisoformat(raw_time)
        return dt.strftime("%m/%d %H:%M"), dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        now = datetime.datetime.now()
        return now.strftime("%m/%d %H:%M"), now.strftime("%Y-%m-%d %H:%M:%S")
