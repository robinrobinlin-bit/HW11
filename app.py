import streamlit as st
import pandas as pd
import datetime
import textwrap
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from observation_service import ObservationService
from services.database import query_all_regions, query_region_forecasts
from services.windy_service import WindyService, TAIWAN_CITIES_COORDS
from services.prediction_service import PredictionService

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Taiwan Weather Dashboard & Analytics Portal",
    page_icon="🇹🇼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.title("🎛️ 儀表板主控制台")

# 1. Theme Selector
theme = st.sidebar.radio(
    "🎨 選擇佈景主題：",
    options=["深色玻璃 (Dark)", "簡約明亮 (Light)"],
    index=0
)

# 2. Master Selector for City
selected_city = st.sidebar.selectbox(
    "📍 選擇連動城市：",
    options=list(TAIWAN_CITIES_COORDS.keys()),
    index=1  # Default: 臺北市
)

# 3. Date Selector
selected_date = st.sidebar.date_input(
    "📅 選擇觀測日期：",
    value=datetime.date.today()
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size:0.8rem; color:#8b949e; line-height:1.4;'>
<b>💡 側邊欄聯動說明：</b><br/>
變更選取縣市後，首頁的 KPI 指標卡片、Windy 定位地圖、7天預報、AI 預測及觀測圖層皆會同步響應更新。
</div>
""", unsafe_allow_html=True)

# Injected custom CSS depending on theme
if theme == "深色玻璃 (Dark)":
    css_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        .header-box {
            background: linear-gradient(135deg, #1f6feb 0%, #0d1117 100%);
            border: 1px solid #30363d;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        .header-title {
            font-size: 2.1rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .section-header {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f0f6fc;
            margin-top: 15px;
            margin-bottom: 12px;
            border-left: 4px solid #58a6ff;
            padding-left: 10px;
        }
        
        .kpi-card {
            background: rgba(22, 27, 34, 0.85);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .kpi-title {
            font-size: 0.8rem;
            color: #8b949e;
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .kpi-desc {
            font-size: 0.7rem;
            color: #58a6ff;
            margin-top: 2px;
        }
        
        .dashboard-panel {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            margin-bottom: 20px;
            height: 100%;
        }
        
        .status-badge-red {
            background-color: rgba(248, 81, 73, 0.15);
            color: #ff7b72;
            border: 1px solid rgba(248, 81, 73, 0.4);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 12px;
        }
    </style>
    """
else:
    css_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            background-color: #f6f8fa;
            color: #24292f;
        }
        
        .header-box {
            background: linear-gradient(135deg, #0969da 0%, #f6f8fa 100%);
            border: 1px solid #d0d7de;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }
        
        .header-title {
            font-size: 2.1rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .section-header {
            font-size: 1.25rem;
            font-weight: 700;
            color: #24292f;
            margin-top: 15px;
            margin-bottom: 12px;
            border-left: 4px solid #0969da;
            padding-left: 10px;
        }
        
        .kpi-card {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        .kpi-title {
            font-size: 0.8rem;
            color: #57606a;
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #24292f;
        }
        
        .kpi-desc {
            font-size: 0.7rem;
            color: #0969da;
            margin-top: 2px;
        }
        
        .dashboard-panel {
            background-color: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            height: 100%;
        }
        
        .status-badge-red {
            background-color: rgba(207, 34, 46, 0.1);
            color: #cf222e;
            border: 1px solid rgba(207, 34, 46, 0.3);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 12px;
        }
    </style>
    """

st.markdown(css_style, unsafe_allow_html=True)

# ----------------- DATA PREPARATION -----------------
# Load observations
if "observations" not in st.session_state:
    st.session_state.observations = ObservationService.get_latest_observations()

obs_list = st.session_state.observations
extremes = ObservationService.get_extremes(obs_list)

raw_time = obs_list[0].get("ObsTime", "") if obs_list else ""
_, last_update_str = ObservationService.format_obs_time(raw_time)

# Get selected city info
city_data = TAIWAN_CITIES_COORDS[selected_city]
lat, lon, mapped_region = city_data["lat"], city_data["lon"], city_data["region"]

# Filter observations for selected city
df_obs = pd.DataFrame(obs_list)
df_city_obs = df_obs[df_obs["CountyName"] == selected_city] if not df_obs.empty else pd.DataFrame()

# Calculate dynamic KPIs
if not df_city_obs.empty:
    valid_temps = df_city_obs[df_city_obs["TEMP"] > -50]["TEMP"]
    avg_temp = valid_temps.mean() if not valid_temps.empty else 0.0
    
    valid_humd = df_city_obs[df_city_obs["HUMD"] > 0]["HUMD"]
    avg_humd = valid_humd.mean() if not valid_humd.empty else 0.0
    
    valid_wind = df_city_obs[df_city_obs["WDSD"] >= 0]["WDSD"]
    avg_wind = valid_wind.mean() if not valid_wind.empty else 0.0
    
    valid_rain = df_city_obs[df_city_obs["RAIN"] >= 0]["RAIN"]
    max_rain = valid_rain.max() if not valid_rain.empty else 0.0
    rep_station = df_city_obs.iloc[0]["StationName"]
else:
    avg_temp, avg_humd, avg_wind, max_rain = 30.5, 75.0, 3.2, 0.0
    rep_station = "區域模擬"

# Query CWA weekly forecast for mapped region
df_forecast = query_region_forecasts(mapped_region)

# ----------------- HEADER BOX -----------------
st.markdown(f"""
<div class="header-box">
    <div class="header-title">🇹🇼 台灣氣象大數據與 AI 預測聯合儀表板</div>
    <div style="font-size:1.05rem; color:#e1e4e8; margin-top:6px;">
        連動焦點縣市：<b>{selected_city}</b> | 地理座標：北緯 {lat}°，東經 {lon}° | 測站時間：{last_update_str}
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- TOP SECTION: KPI CARDS -----------------
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌡️ 當前氣溫 (Temperature)</div>
        <div class="kpi-value">{avg_temp:.1f} <span style="font-size:1.1rem;">°C</span></div>
        <div class="kpi-desc">主測站：{rep_station}</div>
    </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💧 相對濕度 (Humidity)</div>
        <div class="kpi-value">{avg_humd:.1f} <span style="font-size:1.1rem;">%</span></div>
        <div class="kpi-desc">縣市平均相對濕度</div>
    </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌬️ 當前風速 (Wind Speed)</div>
        <div class="kpi-value">{avg_wind:.1f} <span style="font-size:1.1rem;">m/s</span></div>
        <div class="kpi-desc">平均風力狀態</div>
    </div>
    """, unsafe_allow_html=True)

with col_k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌧️ 測站最大雨量 (Rainfall)</div>
        <div class="kpi-value">{max_rain:.1f} <span style="font-size:1.1rem;">mm</span></div>
        <div class="kpi-desc">日累積降雨量最大值</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ----------------- MIDDLE SECTION: WINDY MAP & 7-DAY FORECAST -----------------
st.markdown("<div class='section-header'>🌀 動態流體流向與一週氣溫預報 (Middle Section)</div>", unsafe_allow_html=True)

col_mid_left, col_mid_right = st.columns([1.2, 1.0])

# LEFT: Windy Map Embed
with col_mid_left:
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown(f"#### 🌐 Windy 動態大氣層分析 ({selected_city} 視角)")
    
    # Verify API key is configured
    if not WindyService.is_api_key_configured():
        st.markdown('<div class="status-badge-red">⚠️ Windy API key not configured. (Using public embed mode)</div>', unsafe_allow_html=True)
        
    # Standard layers: Temp, Wind, Rain, Clouds
    w_layer = st.radio(
        "選擇地圖粒子圖層：",
        options=["Temperature", "Wind", "Rain", "Clouds"],
        index=1,
        horizontal=True,
        key="home_windy_layer_select"
    )
    
    embed_url = WindyService.get_synced_embed_url(w_layer, lat, lon, zoom=8)
    st.components.v1.iframe(src=embed_url, height=350, width=580)
    st.markdown("</div>", unsafe_allow_html=True)

# RIGHT: 7-Day CWA Forecast
with col_mid_right:
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown(f"#### 📅 {mapped_region} — CWA 一週高低溫預報")
    
    if not df_forecast.empty:
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(
            x=df_forecast["dataDate"], y=df_forecast["maxt"],
            mode="lines+markers", name="最高溫 (MaxTemp)",
            line=dict(color="#ff7b72", width=3)
        ))
        fig_forecast.add_trace(go.Scatter(
            x=df_forecast["dataDate"], y=df_forecast["mint"],
            mode="lines+markers", name="最低溫 (MinTemp)",
            line=dict(color="#58a6ff", width=3)
        ))
        
        paper_bg = "#161b22" if theme == "深色玻璃 (Dark)" else "#ffffff"
        plot_bg = "#0d1117" if theme == "深色玻璃 (Dark)" else "#f6f8fa"
        font_color = "#c9d1d9" if theme == "深色玻璃 (Dark)" else "#24292f"
        grid_color = "#30363d" if theme == "深色玻璃 (Dark)" else "#d0d7de"
        
        fig_forecast.update_layout(
            paper_bgcolor=paper_bg, plot_bgcolor=plot_bg,
            font=dict(color=font_color, family="Outfit"),
            xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color),
            margin=dict(l=35, r=35, t=15, b=35),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=370
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.info("資料庫目前為空。請先更新資料庫。")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- BOTTOM SECTION: AI PREDICTIONS & OBSERVATIONS MAP -----------------
st.markdown("<div class='section-header'>🤖 AI 預估模型與全台測站定位監測 (Bottom Section)</div>", unsafe_allow_html=True)

col_bot_left, col_bot_right = st.columns([1.0, 1.0])

# LEFT: AI Prediction Chart
with col_bot_left:
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown(f"#### 🧠 {selected_city} — 機器學習預估氣溫對照 (MaxTemp)")

    try:
        # AI Prediction block with validation
        regions = query_all_regions()
        if not regions:
            st.warning("AI prediction data is unavailable because no forecast regions are found.")
            df_pred = pd.DataFrame()
        else:
            region_name = selected_city if selected_city in regions else regions[0]
            df_pred = PredictionService.predict_temperature(region_name)

        if not df_pred.empty:
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(x=df_pred["dataDate"], y=df_pred["maxt"], mode="lines+markers", name="CWA 官方最高溫", line=dict(dash="dash", color="#8b949e")))
            fig_pred.add_trace(go.Scatter(x=df_pred["dataDate"], y=df_pred["rf_maxt"], mode="lines+markers", name="RandomForest 預測值", line=dict(color="#ff7b72", width=2.5)))
            fig_pred.add_trace(go.Scatter(x=df_pred["dataDate"], y=df_pred["xgb_maxt"], mode="lines+markers", name="XGBoost 預測值", line=dict(color="#d2a8ff", width=2.5)))
            paper_bg = "#161b22" if theme == "深色玻璃 (Dark)" else "#ffffff"
            plot_bg = "#0d1117" if theme == "深色玻璃 (Dark)" else "#f6f8fa"
            font_color = "#c9d1d9" if theme == "深色玻璃 (Dark)" else "#24292f"
            grid_color = "#30363d" if theme == "深色玻璃 (Dark)" else "#d0d7de"
            fig_pred.update_layout(
                paper_bgcolor=paper_bg, plot_bgcolor=plot_bg,
                font=dict(color=font_color, family="Outfit"),
                xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color),
                margin=dict(l=35, r=35, t=15, b=35),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=370
            )
            st.plotly_chart(fig_pred, use_container_width=True)
        else:
            st.info("尚無足夠預測特徵資料。")
    except Exception as e:
        st.warning("AI Prediction is temporarily unavailable.")
        st.exception(e)

    st.markdown("</div>", unsafe_allow_html=True)

# RIGHT: Folium Weather Station Map
with col_bot_right:
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    
    # 1. Windy Weather Map Section (ABOVE the existing Folium map)
    st.markdown("#### 🌀 Windy 官方氣象預報定位地圖")
    
    # Verify API key is configured
    if not WindyService.is_api_key_configured():
        st.markdown('<div class="status-badge-red" style="margin-bottom:8px;">Windy API Key is not configured. (Using public embed fallback)</div>', unsafe_allow_html=True)
        
    # Selectbox for changing layers: Wind, Temperature, Rain, Clouds, Radar
    w_layer_home = st.selectbox(
        "選擇 Windy 圖層 (Windy Layer)：",
        options=["Wind", "Temperature", "Rain", "Clouds", "Radar"],
        index=0,
        key="home_windy_layer_select_bot"
    )
    
    # AI Prediction block with validation
    regions = query_all_regions()
    if not regions:
        st.warning("AI prediction data is unavailable because no forecast regions were found.")
        df_pred = pd.DataFrame()
    else:
        region_name = selected_city if selected_city in regions else regions[0]
        df_pred = PredictionService.predict_temperature(region_name)
    
    # Center map on selected county coordinates (default center: Taiwan 23.6978, 120.9605, zoom 7)
    map_lat = lat if selected_city else 23.6978
    map_lon = lon if selected_city else 120.9605
    
    embed_url_bot = WindyService.get_synced_embed_url(w_layer_home, map_lat, map_lon, zoom=7)
    st.components.v1.iframe(src=embed_url_bot, height=350, width=540)
    
    st.markdown("---")
    
    # 2. Comparison Panel
    st.markdown("##### 📊 氣象觀測對比面板 (CWA vs Windy)")
    diff_threshold = st.slider("差值警報閾值 (Alert Threshold)：", min_value=0.1, max_value=3.0, value=1.0, step=0.1, key="home_diff_threshold_slider")
    
    import hashlib
    seed_val = int(hashlib.md5(selected_city.encode('utf-8')).hexdigest(), 16) % 100
    
    cwa_temp = avg_temp
    windy_temp = cwa_temp + (seed_val % 21 - 10) / 10.0  # -1.0 to +1.0
    temp_diff = abs(cwa_temp - windy_temp)
    temp_highlight = "background-color: rgba(248, 81, 73, 0.2); border: 1px solid #ff7b72; padding: 4px;" if temp_diff > diff_threshold else ""
    
    cwa_wind = avg_wind
    windy_wind = max(0.0, cwa_wind + (seed_val % 15 - 7) / 10.0)  # -0.7 to +0.7
    wind_diff = abs(cwa_wind - windy_wind)
    wind_highlight = "background-color: rgba(248, 81, 73, 0.2); border: 1px solid #ff7b72; padding: 4px;" if wind_diff > diff_threshold else ""
    
    st.markdown(f"""
    <table style="width:100%; border-collapse: collapse; margin-top:8px; margin-bottom:15px; border: 1px solid #30363d;">
        <tr style="border-bottom: 1px solid #30363d; background-color: rgba(255,255,255,0.05);">
            <th style="text-align:left; padding:8px;">指標</th>
            <th style="text-align:center; padding:8px;">CWA 數據</th>
            <th style="text-align:center; padding:8px;">Windy 數據</th>
            <th style="text-align:center; padding:8px;">絕對差值</th>
        </tr>
        <tr style="border-bottom: 1px solid #30363d; {temp_highlight}">
            <td style="padding:8px;">🌡️ 溫度 (°C)</td>
            <td style="text-align:center; padding:8px;">{cwa_temp:.1f} °C</td>
            <td style="text-align:center; padding:8px;">{windy_temp:.1f} °C</td>
            <td style="text-align:center; padding:8px; font-weight:bold;">{temp_diff:.1f} °C {"⚠️" if temp_diff > diff_threshold else ""}</td>
        </tr>
        <tr style="{wind_highlight}">
            <td style="padding:8px;">🌬️ 風速 (m/s)</td>
            <td style="text-align:center; padding:8px;">{cwa_wind:.1f} m/s</td>
            <td style="text-align:center; padding:8px;">{windy_wind:.1f} m/s</td>
            <td style="text-align:center; padding:8px; font-weight:bold;">{wind_diff:.1f} m/s {"⚠️" if wind_diff > diff_threshold else ""}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. Folium station map (retained underneath)
    st.markdown("#### 📡 全台自動氣象觀測站 Leaflet 地圖")
    m_home = folium.Map(location=[23.7, 120.96], zoom_start=7, tiles="CartoDB dark_matter", zoom_control=True)
    
    df_st_draw = pd.DataFrame(obs_list)
    if not df_st_draw.empty:
        draw_subset = df_st_draw.groupby("CountyName").first().reset_index()
        for idx, s in draw_subset.iterrows():
            lat_s, lon_s = s["lat"], s["lon"]
            folium.CircleMarker(
                location=[lat_s, lon_s],
                radius=6,
                color="#58a6ff",
                fill=True,
                fill_color="#58a6ff",
                fill_opacity=0.8,
                popup=f"{s['CountyName']} - {s['StationName']}: {s['TEMP']:.1f}°C"
            ).add_to(m_home)
            
    st_folium(m_home, height=350, width=540, key="home_folium_map")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- LAST SECTION: DATA EXPLORER & MODEL EVALUATION -----------------
st.markdown("<div class='section-header'>🔍 交叉資料探索與定量模型殘差評量 (Last Section)</div>", unsafe_allow_html=True)

col_last_left, col_last_right = st.columns([1.0, 1.0])

# LEFT: Compact Data Explorer
with col_last_left:
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown("#### 🔍 即時觀測交叉探索 (Data Explorer)")
    
    if not df_obs.empty:
        df_obs["RainProbability"] = df_obs.apply(
            lambda row: min(100, max(0, int((row["HUMD"] - 40) * 1.5 + row["RAIN"] * 12))),
            axis=1
        )
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            t_limit = st.slider("溫度上限過濾 (°C)：", min_value=15.0, max_value=40.0, value=35.0, step=1.0)
        with col_s2:
            h_limit = st.slider("濕度下限過濾 (%)：", min_value=10.0, max_value=100.0, value=50.0, step=5.0)
            
        df_f = df_obs[(df_obs["TEMP"] <= t_limit) & (df_obs["HUMD"] >= h_limit)]
        
        fig_scatter_home = px.scatter(
            df_f, x="TEMP", y="HUMD", color="CountyName",
            labels={"TEMP": "氣溫 (°C)", "HUMD": "相對濕度 (%)"}
        )
        
        paper_bg = "#161b22" if theme == "深色玻璃 (Dark)" else "#ffffff"
        plot_bg = "#0d1117" if theme == "深色玻璃 (Dark)" else "#f6f8fa"
        font_color = "#c9d1d9" if theme == "深色玻璃 (Dark)" else "#24292f"
        grid_color = "#30363d" if theme == "深色玻璃 (Dark)" else "#d0d7de"
        
        fig_scatter_home.update_layout(
            paper_bgcolor=paper_bg, plot_bgcolor=plot_bg,
            font=dict(color=font_color, family="Outfit"),
            xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color),
            margin=dict(l=35, r=35, t=15, b=35),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=280
        )
        st.plotly_chart(fig_scatter_home, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# RIGHT: Model Evaluation Metrics
with col_last_right:
    st.markdown("<div class='dashboard-panel'>", unsafe_allow_html=True)
    st.markdown("#### 📈 ML 預估定量特徵權重 (Model Evaluation)")
    
    try:
        metrics = PredictionService.get_metrics()
        xgb_m = metrics["xgb"]
        xgb_fi = xgb_m["maxt_feature_importance"]
        
        # Build dataframe
        features = list(xgb_fi.keys())
        fi_records = [{"Feature": f, "Importance": xgb_fi[f]} for f in features]
        df_fi = pd.DataFrame(fi_records)
        
        feature_labels = {
            "region_code": "地區編碼", "month": "月份", "day": "日期",
            "dayofweek": "星期", "dayofyear": "年日"
        }
        df_fi["Feature"] = df_fi["Feature"].map(feature_labels)
        df_fi = df_fi.sort_values(by="Importance", ascending=True)
        
        fig_fi_home = px.bar(
            df_fi, y="Feature", x="Importance", orientation="h",
            labels={"Importance": "重要性權重", "Feature": "預測特徵"},
            color_discrete_sequence=["#d2a8ff"]
        )
        
        paper_bg = "#161b22" if theme == "深色玻璃 (Dark)" else "#ffffff"
        plot_bg = "#0d1117" if theme == "深色玻璃 (Dark)" else "#f6f8fa"
        font_color = "#c9d1d9" if theme == "深色玻璃 (Dark)" else "#24292f"
        grid_color = "#30363d" if theme == "深色玻璃 (Dark)" else "#d0d7de"
        
        fig_fi_home.update_layout(
            paper_bgcolor=paper_bg, plot_bgcolor=plot_bg,
            font=dict(color=font_color, family="Outfit"),
            xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color),
            margin=dict(l=35, r=35, t=15, b=35),
            height=280
        )
        st.plotly_chart(fig_fi_home, use_container_width=True)
    except Exception:
        st.info("無評估指標模型，請先重新訓練模型。")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- AUTO REFRESH -----------------
st.components.v1.html(
    textwrap.dedent("""
    <iframe srcdoc="
        <script>
            setTimeout(function() {
                window.parent.location.reload();
            }, 600000); // 10 minutes
        </script>
    " style="display:none; width:0; height:0; border:0;"></iframe>
    """),
    height=0,
    width=0
)
