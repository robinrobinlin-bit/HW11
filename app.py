import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import datetime
import textwrap
from weather_db import query_all_regions, query_region_forecasts, init_db
from observation_service import ObservationService

# Page configurations
st.set_page_config(
    page_title="Taiwan Real-Time Weather Dashboard",
    page_icon="🇹🇼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Premium Styling for classmate's layout
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Center tab styling */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        background-color: #161b22;
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        border-radius: 6px;
        padding: 8px 24px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #21262d;
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }

    /* Classmate's Dashboard styling */
    .dashboard-panel {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .dashboard-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f0f6fc;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .dashboard-subtitle {
        font-size: 0.85rem;
        color: #8b949e;
        margin-bottom: 16px;
        line-height: 1.5;
    }
    
    .api-badge {
        background-color: #238636;
        color: white;
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .stat-box {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        text-align: left;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #8b949e;
        margin-bottom: 4px;
    }
    
    .stat-val {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 2px;
    }
    
    .stat-val.temp-max { color: #ff7b72; }
    .stat-val.temp-min { color: #58a6ff; }
    .stat-val.rain { color: #79c0ff; }
    .stat-val.wind { color: #d2a8ff; }
    
    .stat-station {
        font-size: 0.7rem;
        color: #8b949e;
    }
    
    /* Warning accordion box */
    .warning-box {
        background-color: rgba(240, 136, 62, 0.1);
        border: 1px solid #f0883e;
        border-radius: 8px;
        padding: 12px;
        margin-top: 12px;
        color: #f0f6fc;
    }
    
    .warning-title {
        font-size: 0.85rem;
        font-weight: bold;
        color: #ff9e3b;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .warning-text {
        font-size: 0.75rem;
        color: #c9d1d9;
        line-height: 1.4;
    }
    
    /* Layer Selector Buttons */
    .layer-title {
        margin-top: 0;
        color: #f0f6fc;
        font-size: 1.1rem;
        border-bottom: 1px solid #30363d;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    
    /* Force left alignment on Streamlit buttons in the right column */
    [data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# Create two tabs: Real-time map (classmate's UI) and Weekly Forecast (original homework reqs)
tab_live, tab_forecast = st.tabs(["📡 即時天氣監測 (Live Map)", "📅 一週氣溫預報 (Weekly Forecast)"])

# ----------------- TAB 1: LIVE OBSERVATIONS DASHBOARD -----------------
with tab_live:
    # Initialize observation state
    if "observations" not in st.session_state:
        st.session_state.observations = ObservationService.get_latest_observations()
        
    obs_list = st.session_state.observations
    extremes = ObservationService.get_extremes(obs_list)
    obs_count = len(obs_list)
    
    # Extract observation time dynamically
    raw_time = obs_list[0].get("ObsTime", "") if obs_list else ""
    obs_time_str, last_update_str = ObservationService.format_obs_time(raw_time)
                
    # 3-column layout mimicking classmate's layout
    col_left, col_center, col_right = st.columns([1.1, 2.2, 1.1], gap="medium")
    
    # Left Dashboard Panel
    with col_left:
        st.markdown(f"""<div class="dashboard-panel">
<div class="dashboard-title">
台灣即時氣象 <span class="api-badge">即時 API</span>
</div>
<div class="dashboard-subtitle">
觀測時間：{obs_time_str}<br/>
資料來源：CWA O-A0003-001<br/>
本次讀取：即時呼叫 CWA API (已更新資料庫)<br/>
測站數量：{obs_count} 站
</div>
<div class="stats-grid">
<div class="stat-box">
<div class="stat-label">最高溫</div>
<div class="stat-val temp-max">{extremes['max_temp']['val']:.1f} <span style="font-size: 0.9rem;">°C</span></div>
<div class="stat-station">{extremes['max_temp']['name']}</div>
</div>
<div class="stat-box">
<div class="stat-label">最低溫</div>
<div class="stat-val temp-min">{extremes['min_temp']['val']:.1f} <span style="font-size: 0.9rem;">°C</span></div>
<div class="stat-station">{extremes['min_temp']['name']}</div>
</div>
<div class="stat-box">
<div class="stat-label">最大雨量</div>
<div class="stat-val rain">{extremes['max_rain']['val']:.1f} <span style="font-size: 0.9rem;">mm</span></div>
<div class="stat-station">{extremes['max_rain']['name']}</div>
</div>
<div class="stat-box">
<div class="stat-label">最大風速</div>
<div class="stat-val wind">{extremes['max_wind']['val']:.1f} <span style="font-size: 0.9rem;">m/s</span></div>
<div class="stat-station">{extremes['max_wind']['name']}</div>
</div>
</div>
<div class="warning-box">
<div class="warning-title">⚠️ 天氣特報 4 則 <span style="font-size:0.75rem; color:#8b949e; font-weight:normal;">來源：NCDR CAP</span></div>
<div class="warning-text">
<b>高溫特報</b> (有效至 17:00)：<br/>
各地高溫炎熱，台南為橙色燈號，有出現38度極端高溫的機率；台北、新北、高雄、屏東、宜蘭、花蓮為橙色燈號，請注意防曬與防暑。<br/>
<span style="color:#ff9e3b; font-size:0.75rem;"><b>強風特報</b> (有效至 23:00)：高雄市、屏東縣、連江縣平均風力6級以上...</span>
</div>
</div>
<div style="background-color:#0d1117; border: 1px solid #30363d; border-radius:8px; padding:12px; margin-top:12px;">
<div style="font-size:0.8rem; color:#8b949e; margin-bottom:4px; font-weight:bold;">📡 資料狀態</div>
<div style="font-size:0.75rem; color:#58a6ff; font-weight:bold;">最後更新</div>
<div style="font-size:0.95rem; color:#58a6ff; font-weight:bold; margin-top:2px;">{last_update_str}</div>
</div>
</div>""", unsafe_allow_html=True)
        
    # Center Panel: Leaflet Dark Map
    with col_center:
        # Layer state variables in session state
        if "active_layer" not in st.session_state:
            st.session_state.active_layer = "氣溫"
        if "show_labels" not in st.session_state:
            st.session_state.show_labels = True
        if "show_borders" not in st.session_state:
            st.session_state.show_borders = True
            
        # Draw Dark Leaflet map centered at Taiwan
        m = folium.Map(location=[23.7, 120.96], zoom_start=8, tiles="CartoDB dark_matter", zoom_control=True)
        
        # Select representative station per county to overlay cleanly on map (one marker per county)
        df_stations = pd.DataFrame(obs_list)
        rep_stations = []
        if not df_stations.empty:
            for county, group in df_stations.groupby("CountyName"):
                # Pick the station with highest value for the active layer
                if st.session_state.active_layer == "氣溫":
                    rep = group.sort_values(by="TEMP", ascending=False).iloc[0]
                elif st.session_state.active_layer == "雨量":
                    rep = group.sort_values(by="RAIN", ascending=False).iloc[0]
                elif st.session_state.active_layer == "風速風向":
                    rep = group.sort_values(by="WDSD", ascending=False).iloc[0]
                elif st.session_state.active_layer == "濕度":
                    rep = group.sort_values(by="HUMD", ascending=False).iloc[0]
                else: # 測站點位
                    rep = group.iloc[0]
                rep_stations.append(rep)
                
        # Draw markers on map
        for s in rep_stations:
            lat, lon = s["lat"], s["lon"]
            name = s["StationName"]
            county = s["CountyName"]
            town = s["TownName"]
            
            # Format value depending on selected layer
            if st.session_state.active_layer == "氣溫":
                val = s["TEMP"]
                label_txt = f"{int(val)}°" if val > -50 else "N/A"
                if val >= 32: color = "#ef4444"
                elif val >= 28: color = "#f97316"
                elif val >= 22: color = "#eab308"
                else: color = "#3b82f6"
            elif st.session_state.active_layer == "雨量":
                val = s["RAIN"]
                label_txt = f"{val}mm"
                color = "#2563eb"
            elif st.session_state.active_layer == "風速風向":
                val = s["WDSD"]
                label_txt = f"{val}m/s"
                color = "#a855f7"
            elif st.session_state.active_layer == "濕度":
                val = s["HUMD"]
                label_txt = f"{val}%"
                color = "#06b6d4"
            else: # 測站點位 / 天氣 / 雷達
                label_txt = name[:2]
                color = "#10b981"
                
            popup_html = f"""
            <div style="font-family: sans-serif; font-size: 0.85rem; width: 180px; color:#333;">
                <b>{county} - {name}</b><br/>
                <hr style="margin: 4px 0; border: 0; border-top: 1px solid #ccc;"/>
                🌡️ 氣溫: {s['TEMP']:.1f} °C<br/>
                💧 濕度: {s['HUMD']}%<br/>
                🌬️ 風速: {s['WDSD']:.1f} m/s<br/>
                🌧️ 雨量: {s['RAIN']:.1f} mm<br/>
                ⏱️ 觀測: 10:00
            </div>
            """
            
            # Add custom text label overlay if checked
            if st.session_state.show_labels:
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f"""<div style="
                            color: white; 
                            background: {color}; 
                            padding: 2px 6px; 
                            border-radius: 10px; 
                            font-weight: bold; 
                            font-size: 0.75rem; 
                            border: 1px solid rgba(255,255,255,0.4); 
                            box-shadow: 0 2px 4px rgba(0,0,0,0.5);
                            white-space: nowrap;
                            text-align: center;
                        ">{label_txt}</div>"""
                    ),
                    popup=folium.Popup(popup_html, max_width=200)
                ).add_to(m)
            else:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=200)
                ).add_to(m)
                
        # Render map based on selected layer
        if st.session_state.active_layer == "雷達":
            windy_url = "https://embed.windy.com/embed2.html?lat=23.7&lon=120.96&zoom=8&level=surface&overlay=radar&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
            st.components.v1.iframe(src=windy_url, height=450, width=650)
        elif st.session_state.active_layer == "天氣":
            windy_url = "https://embed.windy.com/embed2.html?lat=23.7&lon=120.96&zoom=8&level=surface&overlay=clouds&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
            st.components.v1.iframe(src=windy_url, height=450, width=650)
        else:
            st_folium(m, height=450, width=650, key="live_folium_map")
        
        # Bottom Status Bar
        st.markdown("---")
        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            st.markdown(f"<div style='font-size:0.8rem; color:#8b949e; margin-top:8px;'>更新於 {last_update_str}</div>", unsafe_allow_html=True)
        with col_b2:
            if st.button("🔄 重新整理", key="refresh_bottom_button", use_container_width=True):
                st.session_state.observations = ObservationService.get_latest_observations()
                st.rerun()
        
    # Right Settings Panel (圖層)
    with col_right:
        st.markdown("""<div class="dashboard-panel">
<div class="layer-title">圖層 (Layers)</div>
</div>""", unsafe_allow_html=True)
        
        # Vertical button-styled list for active layer
        layers = ["氣溫", "雨量", "雷達", "風速風向", "濕度", "天氣", "測站點位"]
        for l in layers:
            btn_type = "primary" if st.session_state.active_layer == l else "secondary"
            icon = "🌡️ " if l == "氣溫" else "🌧️ " if l == "雨量" else "📡 " if l == "雷達" else "🌬️ " if l == "風速風向" else "💧 " if l == "濕度" else "🌤️ " if l == "天氣" else "📍 "
            if st.button(f"{icon}{l}", key=f"btn_layer_{l}", type=btn_type, use_container_width=True):
                st.session_state.active_layer = l
                st.rerun()
            
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # Checkboxes for toggling map items
        show_labels = st.checkbox("氣溫數字標籤", value=st.session_state.show_labels)
        if show_labels != st.session_state.show_labels:
            st.session_state.show_labels = show_labels
            st.rerun()
            
        show_borders = st.checkbox("縣市界線", value=st.session_state.show_borders)
        if show_borders != st.session_state.show_borders:
            st.session_state.show_borders = show_borders
            st.rerun()
            
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # Temperature color legend
        st.markdown("""<div style="background-color:#0d1117; border: 1px solid #30363d; border-radius:8px; padding:12px;">
<div style="font-size:0.75rem; color:#8b949e; margin-bottom:8px; font-weight:bold;">溫度圖例 (°C)</div>
<div style="height:12px; background: linear-gradient(90deg, #3b82f6 0%, #eab308 50%, #f97316 75%, #ef4444 100%); border-radius:4px;"></div>
<div style="display:flex; justify-content:space-between; font-size:0.65rem; color:#8b949e; margin-top:4px;">
<span>15°C</span>
<span>22°C</span>
<span>28°C</span>
<span>35°C</span>
</div>
</div>""", unsafe_allow_html=True)

# ----------------- TAB 2: WEEKLY FORECASTS (original homework requirements) -----------------
with tab_forecast:
    # Ensure database exists
    if not os.path.exists("data.db"):
        st.info("Database empty. Run the sync command or run fetch_weather.py.")
    else:
        regions_list = query_all_regions()
        if not regions_list:
            st.warning("Database empty. Run fetch_weather.py script to parse weekly forecast temperatures.")
        else:
            st.markdown("### 📅 一週氣溫預報 (Weekly Temperature Forecast)")
            st.write("這部分從 SQLite `data.db` 讀取資料，提供下拉選單切換地區，並使用折線圖與表格顯示一週高低氣溫。")
            
            # Regional selector dropdown
            selected_f_region = st.selectbox(
                "選擇預報海域/地區：",
                options=regions_list,
                key="weekly_forecast_region_selector"
            )
            
            df_forecast = query_region_forecasts(selected_f_region)
            
            if df_forecast.empty:
                st.info("該地區尚無預報數據。")
            else:
                col_chart, col_table = st.columns([3, 2], gap="large")
                
                with col_chart:
                    st.markdown("#### 📈 折線圖 (Temperature Trend)")
                    chart_df = df_forecast.set_index("dataDate")[["mint", "maxt"]]
                    chart_df.columns = ["最低溫 (Min Temp)", "最高溫 (Max Temp)"]
                    st.line_chart(chart_df, color=["#58a6ff", "#ff7b72"])
                    
                with col_table:
                    st.markdown("#### 📋 預報資料表 (Forecast Data Table)")
                    display_df = df_forecast[["dataDate", "mint", "maxt"]].copy()
                    display_df.columns = ["日期 (Date)", "最低氣溫 (Min)", "最高氣溫 (Max)"]
                    st.dataframe(
                        display_df.style.format({
                            "最低氣溫 (Min)": "{:.1f} °C",
                            "最高氣溫 (Max)": "{:.1f} °C"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
