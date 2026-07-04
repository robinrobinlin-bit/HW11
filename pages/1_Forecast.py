import streamlit as st
import os
import pandas as pd
from services.database import query_all_regions, query_region_forecasts

# Page configuration
st.set_page_config(
    page_title="一週氣溫預報 (Forecast)",
    page_icon="📅",
    layout="wide"
)

# Custom styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 一週氣溫預報 (Weekly Temperature Forecast)")
st.write("此部分直接從 SQLite 本地資料庫 `data.db` 讀取歷史與最新導入的一週區域氣溫預報數據。")

regions_list = query_all_regions()

if not regions_list:
    st.warning("資料庫目前為空。請先在本地執行 `python fetch_weather.py` 來抓取數據並寫入 SQLite！")
else:
    # Selector dropdown
    selected_f_region = st.selectbox(
        "選擇預報海域/地區：",
        options=regions_list,
        key="weekly_forecast_region_selector"
    )
    
    df_forecast = query_region_forecasts(selected_f_region)
    
    if df_forecast.empty:
        st.info("該地區目前無資料數據。")
    else:
        col_chart, col_table = st.columns([3, 2], gap="large")
        
        with col_chart:
            st.markdown("### 📈 高低氣溫趨勢折線圖")
            chart_df = df_forecast.set_index("dataDate")[["mint", "maxt"]]
            chart_df.columns = ["最低溫 (Min Temp)", "最高溫 (Max Temp)"]
            st.line_chart(chart_df, color=["#58a6ff", "#ff7b72"])
            
        with col_table:
            st.markdown("### 📋 氣溫預報數據表")
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
