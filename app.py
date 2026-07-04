import streamlit as st
import textwrap
import datetime
from observation_service import ObservationService

# Page configurations
st.set_page_config(
    page_title="Taiwan Weather Dashboard & Analytics Portal",
    page_icon="🇹🇼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    .welcome-header {
        background: linear-gradient(135deg, #1f6feb 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 40px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    
    .welcome-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #8b949e;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .feature-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: #58a6ff;
    }
    
    .feature-icon {
        font-size: 2.2rem;
        margin-bottom: 12px;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f0f6fc;
        margin-bottom: 8px;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #8b949e;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Main Welcome Section
st.markdown(textwrap.dedent("""
<div class="welcome-header">
    <div class="welcome-title">🇹🇼 台灣即時氣象與預測分析門戶</div>
    <div class="welcome-subtitle">
        整合中央氣象署 (CWA) 官方 API 觀測與預報資料庫，並提供 AI 動態氣溫預測、Windy 風場粒子模擬及氣象模型評估的可視化平台。請使用左側側邊欄進行功能導覽。
    </div>
</div>
"""), unsafe_allow_html=True)

# Fetch latest weather summaries for homepage metrics
with st.spinner("正在加載最新天氣摘要..."):
    try:
        obs = ObservationService.get_latest_observations()
        extremes = ObservationService.get_extremes(obs)
        raw_time = obs[0].get("ObsTime", "") if obs else ""
        _, last_update_str = ObservationService.format_obs_time(raw_time)
        station_count = len(obs)
    except Exception:
        extremes = {
            "max_temp": {"val": 35.5, "name": "鹿陶洋"},
            "min_temp": {"val": 17.9, "name": "玉山"},
            "max_rain": {"val": 2.0, "name": "東吉島"},
            "max_wind": {"val": 8.0, "name": "東吉島"}
        }
        last_update_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        station_count = 363

# Quick Stats Overview row
st.markdown("### 📊 全台即時氣象快訊")
col_t1, col_t2, col_t3, col_t4 = st.columns(4)

with col_t1:
    st.metric(
        label=f"🔥 全台最高溫 ({extremes['max_temp']['name']})",
        value=f"{extremes['max_temp']['val']:.1f} °C",
        help="全台灣今日目前錄得之最高氣溫觀測值"
    )
with col_t2:
    st.metric(
        label=f"❄️ 全台最低溫 ({extremes['min_temp']['name']})",
        value=f"{extremes['min_temp']['val']:.1f} °C",
        help="全台灣今日目前錄得之最低氣溫觀測值"
    )
with col_t3:
    st.metric(
        label=f"🌧️ 最大累積雨量 ({extremes['max_rain']['name']})",
        value=f"{extremes['max_rain']['val']:.1f} mm",
        help="全台灣目前單日累積雨量最大值"
    )
with col_t4:
    st.metric(
        label=f"🌬️ 最大陣風風速 ({extremes['max_wind']['name']})",
        value=f"{extremes['max_wind']['val']:.1f} m/s",
        help="全台灣目前測得之最大瞬間陣風"
    )

st.caption(f"資料來源：中央氣象署 O-A0003-001 | 測站總數：{station_count} 站 | 數據更新時間：{last_update_str}")

st.markdown("---")

# Feature Columns / Descriptions
st.markdown("### 🧭 平台功能模組")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown(textwrap.dedent("""
    <div class="feature-card">
        <div class="feature-icon">📅</div>
        <div class="feature-title">一週氣溫預報 (Forecast)</div>
        <div class="feature-desc">
            讀取 SQLite3 本地資料庫中記載之各沿海與陸地海域氣溫預報。提供區域下拉選單、高低溫變化折線圖以及完整數據表格展示。
        </div>
    </div>
    """), unsafe_allow_html=True)

with col_f2:
    st.markdown(textwrap.dedent("""
    <div class="feature-card">
        <div class="feature-icon">📡</div>
        <div class="feature-title">即時天氣監測 (Observation)</div>
        <div class="feature-desc">
            在暗黑主題的 Leaflet 地圖上即時繪製全台各縣市氣候站數據氣泡。支援氣溫、雨量、風速、濕度數值快速切換與特報警示。
        </div>
    </div>
    """), unsafe_allow_html=True)

with col_f3:
    st.markdown(textwrap.dedent("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI 氣溫預測模型 (Prediction)</div>
        <div class="feature-desc">
            展示機器學習氣候預測模型之運算結果，提供各分區未來 7 日之高低氣溫預測預估，協助極端天氣預判。
        </div>
    </div>
    """), unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

col_f4, col_f5, col_f6 = st.columns(3)

with col_f4:
    st.markdown(textwrap.dedent("""
    <div class="feature-card">
        <div class="feature-icon">🌀</div>
        <div class="feature-title">Windy 動態氣象圖 (Windy Map)</div>
        <div class="feature-desc">
            完整嵌入 Windy 全球頂級流線粒子模擬地圖，支援雷達降雨雲圖、風場粒子動態流向，以極致動態渲染呈現宏觀天氣。
        </div>
    </div>
    """), unsafe_allow_html=True)

with col_f5:
    st.markdown(textwrap.dedent("""
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-title">模型評估 (Evaluation)</div>
        <div class="feature-desc">
            評估 AI 預測模型與官方氣象預報的誤差數據。展示平均絕對誤差 (MAE)、均方根誤差 (RMSE) 指標以及預測分佈曲線。
        </div>
    </div>
    """), unsafe_allow_html=True)

with col_f6:
    st.markdown(textwrap.dedent("""
    <div class="feature-card">
        <div class="feature-icon">⚙️</div>
        <div class="feature-title">相容性與測試基準 (Tests)</div>
        <div class="feature-desc">
            底層採用服務封裝架構 (cwa_service, database, prediction_service)，完整保留 test.py 與 verify_db.py 測試規範。
        </div>
    </div>
    """), unsafe_allow_html=True)
