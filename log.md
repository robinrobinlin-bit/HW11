# Development Log - Weather Forecast & Live Map

### 2026-07-04 09:55
- Set up python virtual environment and installed dependencies (`requests`, `pandas`, `streamlit`, `folium`, `streamlit-folium`, `python-dotenv`).
- Created initial `requirements.txt`.

### 2026-07-04 10:02
- Implemented CWA weather forecast client (`fetch_weather.py`) to fetch data from CWA API `F-A0012-001` (Weekly Regional Forecasts).
- Implemented `json.dumps()` observations for raw and parsed JSON datasets.

### 2026-07-04 10:04
- Implemented SQLite database connector (`weather_db.py`).
- Created `TemperatureForecasts` table in `data.db` with proper auto-incrementing ID, region, date, min and max temperature columns.

### 2026-07-04 10:05
- Created verification script `verify_db.py` to run distinct region list and Central region forecast query checks.

### 2026-07-04 10:28
- Updated Streamlit UI (`app.py`) to replicate the classmate's dark-theme Leaflet dashboard layout.
- Implemented CWA live weather station observation client (`fetch_observations.py`) targeting API `O-A0003-001` (10-minute weather observations).
- Added left panel metrics cards showing maximum temperature, minimum temperature, max rainfall, and maximum wind speed across all 362 active stations in Taiwan.
- Integrated NCDR weather warnings accordion summary panel.
- Added Leaflet map overlays with color-coded temperature bubbles and checkbox toggles.

### 2026-07-04 10:33
- Unified env config to read `CWA_TOKEN` from `.env`.
- Updated `fetch_weather.py` and `fetch_observations.py` to load CWA API Token correctly.

### 2026-07-04 10:38
- Fixed markdown rendering bug in Streamlit (HTML tag indentation causing text code blocks) by wrapping raw strings with `textwrap.dedent`.
