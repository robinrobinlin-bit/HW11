import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import textwrap
import datetime
from observation_service import ObservationService

# Page configuration
st.set_page_config(
    page_title="即時天氣監測 (Observation)",
    page_icon="📡",
    layout="wide"
)

# Custom styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
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
    
    .layer-title {
        margin-top: 0;
        color: #f0f6fc;
        font-size: 1.1rem;
        border-bottom: 1px solid #30363d;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    
    [data-testid="stVerticalBlock"] div.stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# State initialization
if "observations" not in st.session_state:
    st.session_state.observations = ObservationService.get_latest_observations()
    
obs_list = st.session_state.observations
extremes = ObservationService.get_extremes(obs_list)
obs_count = len(obs_list)

# Extract datetime
raw_time = obs_list[0].get("ObsTime", "") if obs_list else ""
obs_time_str, last_update_str = ObservationService.format_obs_time(raw_time)

# 3-column layout
col_left, col_center, col_right = st.columns([1.1, 2.2, 1.1], gap="medium")

# Left Column (Extreme values and NCDR warning)
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

# Center Column (Leaflet Dark Map with observations)
with col_center:
    if "obs_active_layer" not in st.session_state:
        st.session_state.obs_active_layer = "氣溫"
    if "obs_show_labels" not in st.session_state:
        st.session_state.obs_show_labels = True
    if "obs_show_borders" not in st.session_state:
        st.session_state.obs_show_borders = True
        
    m = folium.Map(location=[23.7, 120.96], zoom_start=8, tiles="CartoDB dark_matter", zoom_control=True)
    
    # Filter one representative station per county
    df_stations = pd.DataFrame(obs_list)
    rep_stations = []
    if not df_stations.empty:
        for county, group in df_stations.groupby("CountyName"):
            if st.session_state.obs_active_layer == "氣溫":
                rep = group.sort_values(by="TEMP", ascending=False).iloc[0]
            elif st.session_state.obs_active_layer == "雨量":
                rep = group.sort_values(by="RAIN", ascending=False).iloc[0]
            elif st.session_state.obs_active_layer == "風速風向":
                rep = group.sort_values(by="WDSD", ascending=False).iloc[0]
            else: # 濕度
                rep = group.sort_values(by="HUMD", ascending=False).iloc[0]
            rep_stations.append(rep)
            
    # Draw markers
    for s in rep_stations:
        lat, lon = s["lat"], s["lon"]
        name = s["StationName"]
        county = s["CountyName"]
        
        if st.session_state.obs_active_layer == "氣溫":
            val = s["TEMP"]
            label_txt = f"{int(val)}°" if val > -50 else "N/A"
            color = "#ef4444" if val >= 32 else "#f97316" if val >= 28 else "#eab308" if val >= 22 else "#3b82f6"
        elif st.session_state.obs_active_layer == "雨量":
            val = s["RAIN"]
            label_txt = f"{val}mm"
            color = "#2563eb"
        elif st.session_state.obs_active_layer == "風速風向":
            val = s["WDSD"]
            label_txt = f"{val}m/s"
            color = "#a855f7"
        else: # 濕度
            val = s["HUMD"]
            label_txt = f"{val}%"
            color = "#06b6d4"
            
        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 0.85rem; width: 180px; color:#333;">
            <b>{county} - {name}</b><br/>
            <hr style="margin: 4px 0; border: 0; border-top: 1px solid #ccc;"/>
            🌡️ 氣溫: {s['TEMP']:.1f} °C<br/>
            💧 濕度: {s['HUMD']}%<br/>
            🌬️ 風速: {s['WDSD']:.1f} m/s<br/>
            🌧️ 雨量: {s['RAIN']:.1f} mm
        </div>
        """
        
        if st.session_state.obs_show_labels:
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
            
    st_folium(m, height=450, width=650, key="obs_folium_map")
    
    st.markdown("---")
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        st.markdown(f"<div style='font-size:0.8rem; color:#8b949e; margin-top:8px;'>更新於 {last_update_str}</div>", unsafe_allow_html=True)
    with col_b2:
        if st.button("🔄 重新整理", key="refresh_obs_page", use_container_width=True):
            st.cache_data.clear()
            st.session_state.observations = ObservationService.get_latest_observations()
            st.rerun()

# Right Column (Layer settings and legend)
with col_right:
    st.markdown("""<div class="dashboard-panel">
<div class="layer-title">圖層 (Layers)</div>
</div>""", unsafe_allow_html=True)
    
    layers = ["氣溫", "雨量", "風速風向", "濕度"]
    for l in layers:
        btn_type = "primary" if st.session_state.obs_active_layer == l else "secondary"
        icon = "🌡️ " if l == "氣溫" else "🌧️ " if l == "雨量" else "🌬️ " if l == "風速風向" else "💧 "
        if st.button(f"{icon}{l}", key=f"btn_obs_layer_{l}", type=btn_type, use_container_width=True):
            st.session_state.obs_active_layer = l
            st.rerun()
            
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    show_labels = st.checkbox("顯示測站數值標籤", value=st.session_state.obs_show_labels)
    if show_labels != st.session_state.obs_show_labels:
        st.session_state.obs_show_labels = show_labels
        st.rerun()
        
    show_borders = st.checkbox("顯示縣市界線", value=st.session_state.obs_show_borders)
    if show_borders != st.session_state.obs_show_borders:
        st.session_state.obs_show_borders = show_borders
        st.rerun()
        
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
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
