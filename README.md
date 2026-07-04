# HW11 Taiwan Weather Dashboard

| Live Demo: [STREAMLIT_APP](https://my-learning-journey-cusqcaxnqwy92twlrrtpfw.streamlit.app)

This Streamlit app now has two modes:

* 🗺️ 全臺即時觀測: Taiwan hourly observation map from CWA `O-A0003-001` (with Windy animated Radar & Weather overlays).
* 📈 一週氣溫預報: six-region weekly temperature forecast from the bundled SQLite `data.db`.

The forecast workflow remains unchanged: `app.py` reads `data.db` through `weather_db.py`, and the `TemperatureForecasts` SQL query contract is preserved.

## Data Sources
* **Hourly observations**: [O-A0003-001](https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001)
* **Weekly forecast**: [F-A0012-001](https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-A0012-001)
* **Local forecast snapshot**: `data.db`, `weather_data.csv`, and `artifacts/*.json`

## Local Setup

### 1. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the project root:
```env
CWA_TOKEN=your_cwa_api_key_here
```

### 3. Fetch Forecast Data & Populate Database
Run the fetching script once to initialize `data.db` and query weekly forecast data:
```bash
python fetch_weather.py
```

### 4. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
