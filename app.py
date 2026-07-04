import streamlit as st
import textwrap
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from observation_service import ObservationService
from services.database import query_all_regions, query_region_forecasts

# Page configurations
st.set_page_config(
    page_title="Taiwan Weather Dashboard",
    page_icon="🇹🇼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.title("🎛️ 氣象監測控制台")

# 1. Theme Selector
theme = st.sidebar.radio(
    "🎨 佈景主題：",
    options=["深色玻璃 (Dark)", "簡約明亮 (Light)"],
    index=0
)

# Injected custom CSS depending on theme
if theme == "深色玻璃 (Dark)":
    css_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        .header-box {
            background: linear-gradient(135deg, #1f6feb 0%, #0d1117 100%);
            border: 1px solid #30363d;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }
        
        .header-title {
            font-size: 2.3rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .kpi-card {
            background: rgba(22, 27, 34, 0.85);
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            text-align: left;
        }
        
        .kpi-title {
            font-size: 0.85rem;
            color: #8b949e;
            font-weight: 500;
            margin-bottom: 6px;
        }
        
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }
        
        .kpi-desc {
            font-size: 0.72rem;
            color: #58a6ff;
        }
        
        .chart-box {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            margin-bottom: 25px;
        }
    </style>
    """
else:
    css_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f6f8fa;
            color: #24292f;
        }
        
        .header-box {
            background: linear-gradient(135deg, #0969da 0%, #f6f8fa 100%);
            border: 1px solid #d0d7de;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .header-title {
            font-size: 2.3rem;
            font-weight: 700;
            color: #ffffff;
        }
        
        .kpi-card {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            text-align: left;
        }
        
        .kpi-title {
            font-size: 0.85rem;
            color: #57606a;
            font-weight: 500;
            margin-bottom: 6px;
        }
        
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #24292f;
            margin-bottom: 4px;
        }
        
        .kpi-desc {
            font-size: 0.72rem;
            color: #0969da;
        }
        
        .chart-box {
            background-color: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            margin-bottom: 25px;
        }
    </style>
    """

st.markdown(css_style, unsafe_allow_html=True)

# 2. Region Selector
regions_db = query_all_regions()
region_options = ["全台地區"] + regions_db
selected_region = st.sidebar.selectbox(
    "🌍 篩選氣象地區：",
    options=region_options,
    index=0
)

# 3. Date Selector
selected_date = st.sidebar.date_input(
    "📅 選擇觀測日期：",
    value=datetime.date.today()
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size:0.8rem; color:#8b949e;'>
<b>系統狀態：</b><br/>
• 10分鐘自動重新整理已啟用<br/>
• 資料庫: data/data.db (正常)
</div>
""", unsafe_allow_html=True)

# ----------------- DATA PREPARATION -----------------
# Get observations
if "observations" not in st.session_state:
    st.session_state.observations = ObservationService.get_latest_observations()

obs_list = st.session_state.observations
extremes = ObservationService.get_extremes(obs_list)
obs_count = len(obs_list)

raw_time = obs_list[0].get("ObsTime", "") if obs_list else ""
_, last_update_str = ObservationService.format_obs_time(raw_time)

# Region mapping to filter observations
REGION_TO_COUNTIES = {
    "全台地區": None,
    "臺灣北部海面": ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣"],
    "臺灣中部海面": ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "臺灣南部海面": ["嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣"],
    "臺灣東北部海面": ["宜蘭縣"],
    "臺灣東部海面": ["花蓮縣"],
    "臺灣東南部海面": ["臺東縣", "澎湖縣", "金門縣", "連江縣"]
}

counties_to_filter = REGION_TO_COUNTIES[selected_region]

# Filter observations
df_obs = pd.DataFrame(obs_list)
if counties_to_filter and not df_obs.empty:
    df_obs_filtered = df_obs[df_obs["CountyName"].isin(counties_to_filter)]
else:
    df_obs_filtered = df_obs

# Filter forecast
if selected_region == "全台地區":
    # Fallback to central region if 'all' is selected
    forecast_region = regions_db[0] if regions_db else "臺灣中部海面"
else:
    forecast_region = selected_region

df_forecast = query_region_forecasts(forecast_region)

# ----------------- DYNAMIC KPI CALCULATIONS -----------------
if not df_obs_filtered.empty:
    # Filter out invalid temperatures
    valid_temps = df_obs_filtered[df_obs_filtered["TEMP"] > -50]["TEMP"]
    avg_temp = valid_temps.mean() if not valid_temps.empty else 0.0
    
    valid_humd = df_obs_filtered[df_obs_filtered["HUMD"] > 0]["HUMD"]
    avg_humd = valid_humd.mean() if not valid_humd.empty else 0.0
    
    valid_wind = df_obs_filtered[df_obs_filtered["WDSD"] >= 0]["WDSD"]
    avg_wind = valid_wind.mean() if not valid_wind.empty else 0.0
    
    valid_rain = df_obs_filtered[df_obs_filtered["RAIN"] >= 0]["RAIN"]
    max_rain = valid_rain.max() if not valid_rain.empty else 0.0
    
    rep_station = df_obs_filtered.iloc[0]["StationName"] if len(df_obs_filtered) == 1 else "區域均值"
else:
    avg_temp, avg_humd, avg_wind, max_rain = 0.0, 0.0, 0.0, 0.0
    rep_station = "無觀測站"

# ----------------- HEADER BOX -----------------
st.markdown(f"""
<div class="header-box">
    <div class="header-title">⚡ 台灣即時氣象監測儀表板</div>
    <div style="font-size:1.05rem; color:#e1e4e8; margin-top:8px; line-height:1.5;">
        當前選取篩選範圍：<b>{selected_region}</b> | 篩選日期：<b>{selected_date}</b><br/>
        資料來源：CWA 自動氣象觀測站 API | 觀測時間：{last_update_str}
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- KPI CARDS ROW -----------------
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌡️ 當前氣溫 (Temperature)</div>
        <div class="kpi-value">{avg_temp:.1f} <span style="font-size:1.2rem;">°C</span></div>
        <div class="kpi-desc">測站來源：{rep_station}</div>
    </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💧 相對濕度 (Humidity)</div>
        <div class="kpi-value">{avg_humd:.1f} <span style="font-size:1.2rem;">%</span></div>
        <div class="kpi-desc">區域平均濕度</div>
    </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌬️ 當前風速 (Wind Speed)</div>
        <div class="kpi-value">{avg_wind:.1f} <span style="font-size:1.2rem;">m/s</span></div>
        <div class="kpi-desc">均風風力表現</div>
    </div>
    """, unsafe_allow_html=True)

with col_k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌧️ 今日最大雨量 (Precipitation)</div>
        <div class="kpi-value">{max_rain:.1f} <span style="font-size:1.2rem;">mm</span></div>
        <div class="kpi-desc">測站最大累積雨量</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

# ----------------- PLOTLY INTERACTIVE CHARTS -----------------
col_c1, col_c2 = st.columns([3, 2], gap="large")

# Chart 1: Interactive Plotly Forecast Min/Max
with col_c1:
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    st.markdown(f"### 📈 {forecast_region} — 一週高低溫預估 (CWA Forecast)")
    
    if not df_forecast.empty:
        fig_forecast = go.Figure()
        
        # Line for MaxT
        fig_forecast.add_trace(go.Scatter(
            x=df_forecast["dataDate"],
            y=df_forecast["maxt"],
            mode="lines+markers",
            name="最高溫 (Max Temp)",
            line=dict(color="#ff7b72", width=3),
            marker=dict(size=8)
        ))
        
        # Line for MinT
        fig_forecast.add_trace(go.Scatter(
            x=df_forecast["dataDate"],
            y=df_forecast["mint"],
            mode="lines+markers",
            name="最低溫 (Min Temp)",
            line=dict(color="#58a6ff", width=3),
            marker=dict(size=8)
        ))
        
        # Apply theme colors to chart background
        paper_bg = "#161b22" if theme == "深色玻璃 (Dark)" else "#ffffff"
        plot_bg = "#0d1117" if theme == "深色玻璃 (Dark)" else "#f6f8fa"
        font_color = "#c9d1d9" if theme == "深色玻璃 (Dark)" else "#24292f"
        grid_color = "#30363d" if theme == "深色玻璃 (Dark)" else "#d0d7de"
        
        fig_forecast.update_layout(
            paper_bgcolor=paper_bg,
            plot_bgcolor=plot_bg,
            font=dict(color=font_color, family="Outfit"),
            xaxis=dict(gridcolor=grid_color, title="預報日期"),
            yaxis=dict(gridcolor=grid_color, title="氣溫 (°C)"),
            margin=dict(l=40, r=40, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.info("資料庫尚無此海域預報資料。")
    st.markdown("</div>", unsafe_allow_html=True)

# Chart 2: Interactive Plotly Station Wind Speed Distribution
with col_c2:
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)
    st.markdown(f"### 🌬️ {selected_region} — 區域測站風速風力分佈")
    
    if not df_obs_filtered.empty:
        # Show top 8 stations for readability
        df_wind_top = df_obs_filtered.sort_values(by="WDSD", ascending=False).head(8)
        
        fig_wind = px.bar(
            df_wind_top,
            x="StationName",
            y="WDSD",
            color="WDSD",
            labels={"StationName": "觀測站名稱", "WDSD": "風速 (m/s)"},
            color_continuous_scale=px.colors.sequential.Purples
        )
        
        paper_bg = "#161b22" if theme == "深色玻璃 (Dark)" else "#ffffff"
        plot_bg = "#0d1117" if theme == "深色玻璃 (Dark)" else "#f6f8fa"
        font_color = "#c9d1d9" if theme == "深色玻璃 (Dark)" else "#24292f"
        grid_color = "#30363d" if theme == "深色玻璃 (Dark)" else "#d0d7de"
        
        fig_wind.update_layout(
            paper_bgcolor=paper_bg,
            plot_bgcolor=plot_bg,
            font=dict(color=font_color, family="Outfit"),
            xaxis=dict(gridcolor=grid_color),
            yaxis=dict(gridcolor=grid_color),
            margin=dict(l=40, r=40, t=20, b=40),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig_wind, use_container_width=True)
    else:
        st.info("當前篩選區間無觀測測站資料。")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- AUTO REFRESH -----------------
# Embed a hidden sandboxed iframe meta-refresher that automatically triggers a Streamlit rerun every 10 minutes (600 seconds)
st.components.v1.html(
    textwrap.dedent("""
    <iframe srcdoc="
        <script>
            setTimeout(function() {
                window.parent.location.reload();
            }, 600000); // 600,000 milliseconds = 10 minutes
        </script>
    " style="display:none; width:0; height:0; border:0;"></iframe>
    """),
    height=0,
    width=0
)
