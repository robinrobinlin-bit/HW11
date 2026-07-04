# HW11 Taiwan Weather Dashboard

| Live Demo: [STREAMLIT_APP](https://my-learning-journey-cusqcaxnqwy92twlrrtpfw.streamlit.app)

This is a modular, multi-page Streamlit Weather Dashboard presenting real-time weather observations, AI-driven temperature forecasting models, and interactive global weather loop visualizations.

## Homepage Premium Layout Features

We have upgraded the Home page (`app.py`) to feature a modern, responsive web dashboard:
- **🎛️ Interactive Sidebar Panel**:
  - **Theme Toggle**: Real-time switching between **深色玻璃 (Dark)** mode (translucent glassmorphism containers) and **簡約明亮 (Light)** mode (clean typography grid).
  - **Region Selector**: Integrates a drop-down selector linking sea forecast areas with land observations to dynamically slice and filter metrics.
  - **Date Selector**: Dynamic calendar selector mapping weather records.
- **⚡ Real-time KPI Card Grid**:
  - Automatically calculates and presents aggregated weather parameters for the selected region: *Current Temperature*, *Relative Humidity*, *Average Wind Speed*, and *Max Cumulative Rainfall*.
- **📊 Plotly Interactive Charts**:
  - **Weekly Forecast Comparison**: Multi-trace line chart comparing Min/Max temperatures.
  - **Wind Speed Distribution**: Sorted vertical bar chart showing wind speed metrics across regional stations.
- **🔄 background Auto-Refresh**:
  - Embeds a hidden refresher to perform a full app data sync every 10 minutes.

---

## Multi-Page Directory Layout

Streamlit's native multi-page sidebar includes 5 custom analytic modules:
1. **📅 1_Forecast**: Weekly sea-area forecast reports from the local SQLite database.
2. **📡 2_Observation**: Dark Leaflet map with numerical value bubble overlays for CWA stations.
3. **🤖 3_AI_Prediction**: Future 7-day temperature projections output by simulated AI regressors.
4. **🌀 4_Windy_Map**: Windy.com animated particle overlays (radar and clouds).
5. **📈 5_Model_Evaluation**: quantitative error metrics calculations (MAE & RMSE charts).

---

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
