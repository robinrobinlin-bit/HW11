import streamlit as st
import pandas as pd
from services.windy_service import WindyService, TAIWAN_CITIES_COORDS
from services.database import query_region_forecasts

# Page configuration
st.set_page_config(
    page_title="Windy API 聯動地圖 (Windy Map)",
    page_icon="🌀",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .status-badge-green {
        background-color: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-block;
        font-weight: 500;
        margin-bottom: 12px;
    }
    
    .status-badge-yellow {
        background-color: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-block;
        font-weight: 500;
        margin-bottom: 12px;
    }
    
    .forecast-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f0f6fc;
        border-bottom: 1px solid #30363d;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    
    .map-frame-box {
        border: 1px solid #30363d;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🌀 Windy API 經緯度聯動天氣地圖")
st.write("結合 Windy 官方大氣環流粒子模擬與中央氣象署 (CWA) 本地資料庫預報，選取特定縣市即可自動重定地圖視角，並呈現所屬海區一週氣溫趨勢。")

# ----------------- API KEY STATUS -----------------
api_key_configured = WindyService.is_api_key_configured()
if api_key_configured:
    st.markdown('<div class="status-badge-green">🟢 Windy API 授權金鑰：已載入 (WINDY_API_KEY)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-badge-yellow">⚪ Windy API 授權金鑰：未設定 (採用公用免費微件渲染模式)</div>', unsafe_allow_html=True)

# ----------------- SIDEBAR OR TOP SELECTORS -----------------
col_sel1, col_sel2 = st.columns([1, 1])
with col_sel1:
    selected_city = st.selectbox(
        "📍 選擇連動縣市：",
        options=list(TAIWAN_CITIES_COORDS.keys()),
        index=0
    )
with col_sel2:
    selected_layer = st.selectbox(
        "🗺️ 選擇 Windy 粒子圖層：",
        options=["Temperature", "Wind", "Rain", "Clouds", "Pressure"],
        index=1
    )

city_data = TAIWAN_CITIES_COORDS[selected_city]
lat, lon, mapped_region = city_data["lat"], city_data["lon"], city_data["region"]

# ----------------- MAIN LAYOUT: MAP (LEFT), CWA FORECAST (RIGHT) -----------------
col_map, col_forecast = st.columns([3, 1.4], gap="large")

with col_map:
    st.markdown(f"### 🌐 Windy {selected_layer} 動態視角 ({selected_city} 周邊)")
    embed_url = WindyService.get_synced_embed_url(selected_layer, lat, lon, zoom=8)
    
    # Render interactive map
    st.components.v1.iframe(src=embed_url, height=520, width=780)
    st.caption(f"座標定位點：北緯 {lat}°，東經 {lon}° | 地圖同步重定位中...")

with col_forecast:
    st.markdown(f"### 📅 {selected_city} 氣候預報 (CWA)")
    st.markdown(f"<div style='font-size:0.85rem; color:#8b949e; margin-bottom:12px;'>對照區域：{mapped_region}</div>", unsafe_allow_html=True)
    
    df_region_fc = query_region_forecasts(mapped_region)
    
    if df_region_fc.empty:
        st.warning("資料庫目前無此區域之一週預報。請先更新資料庫！")
    else:
        # Style forecast output
        display_fc = df_region_fc[["dataDate", "mint", "maxt"]].copy()
        display_fc.columns = ["預報日期", "最低溫", "最高溫"]
        
        st.dataframe(
            display_fc.style.format({
                "最低溫": "{:.1f} °C",
                "最高溫": "{:.1f} °C"
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Add simple visual bar forecast representation
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("<b>🌡️ 氣溫區間預覽：</b>", unsafe_allow_html=True)
        for idx, row in display_fc.iterrows():
            st.markdown(f"""
            <div style="background-color:rgba(255,255,255,0.05); padding:6px 12px; border-radius:6px; margin-bottom:6px; display:flex; justify-content:space-between; font-size:0.82rem;">
                <span style="color:#8b949e;">{row['預報日期']}</span>
                <span style="font-weight:bold; color:#58a6ff;">{row['最低溫']:.1f}°C</span> ~ <span style="font-weight:bold; color:#ff7b72;">{row['最高溫']:.1f}°C</span>
            </div>
            """, unsafe_allow_html=True)
