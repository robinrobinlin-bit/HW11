# AI Coding Agent Guidelines - Taiwan Weather Dashboard

This document lists the rules and architectural guidelines that any agentic coding assistant must follow when modifying or maintaining this codebase.

## 1. Credentials Configuration
- All API calls to CWA must load the API Token from the `.env` file.
- The environment variable name is strictly `CWA_TOKEN`.
- Fallbacks to `CWA_API_KEY` are acceptable for backward compatibility, but `CWA_TOKEN` is preferred.
- **Never** hardcode any CWA API Key inside Python scripts.

## 2. SQLite Database Integrity (`data.db`)
- The table `TemperatureForecasts` schema is fixed and must include:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `regionName`: TEXT NOT NULL
  - `dataDate`: TEXT NOT NULL
  - `mint`: REAL
  - `maxt`: REAL
- A UNIQUE constraint is enforced on `(regionName, dataDate)` to prevent duplicate records.
- Always use `INSERT OR REPLACE` (or equivalent upsert statements) when writing forecasts.

## 3. Classmate-Style Visual Layout
- The live observations map must follow the classmate's visual panel design.
- **Left Column**: Metric extremes cards (max temp, min temp, max rain, max wind) with corresponding station names, and NCDR CAP warning accordion box.
- **Center Column**: Main map container. Render the Leaflet dark map (`CartoDB dark_matter`) or the embedded Windy map iframe.
- **Right Column**:图层 (Layers) panel with vertical option buttons, label overlays, and custom HSL/RGB gradient range legends.

## 4. Map Overlays & Windy Integration
- Standard layers: `氣溫` (Air Temp), `雨量` (Rainfall), `風速風向` (Wind), `濕度` (Humidity), and `測站點位` (Stations) must be rendered using `folium` (Leaflet) station markers.
- Animated layers: `雷達` (Radar) and `天氣` (Weather) must load the responsive Windy.com interactive iframe map centered on Taiwan.

## 5. Coding Best Practices
- Keep all multiline HTML strings inside `st.markdown()` blocks left-aligned (0 indentation) to prevent Markdown-it from parsing indentations as raw code blocks.
- Wrap all observation calculations and formatting helpers inside the `ObservationService` static class in `observation_service.py`.
- Run `python test.py` after making edits to verify that unit tests pass.
