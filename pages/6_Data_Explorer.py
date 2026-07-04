import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from observation_service import ObservationService

# Page configuration
st.set_page_config(
    page_title="資料探索者 (Data Explorer)",
    page_icon="🔍",
    layout="wide"
)

# Custom styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .explorer-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .sidebar-label {
        font-size: 0.9rem;
        font-weight: bold;
        color: #58a6ff;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 全台氣象資料多維度探索器")
st.write("讀取全台自動觀測站即時氣象大數據，提供 6 大維度交叉篩選及 5 大統計交互圖表分析，支援快速導出 CSV。")

# ----------------- DATA PREPARATION -----------------
with st.spinner("正在讀取並初始化觀測大數據..."):
    obs_list = ObservationService.get_latest_observations()
    
if not obs_list:
    st.error("無法取得即時觀測數據，請檢查網路連線或金鑰狀態！")
else:
    df_raw = pd.DataFrame(obs_list)
    # Parse dates and calculate rain probability on the fly
    df_raw["Date"] = df_raw["ObsTime"].apply(lambda x: x.split("T")[0] if x else str(datetime.date.today()))
    df_raw["RainProbability"] = df_raw.apply(
        lambda row: min(100, max(0, int((row["HUMD"] - 40) * 1.5 + row["RAIN"] * 12))),
        axis=1
    )
    
    # ----------------- INTERACTIVE SIDEBAR FILTERS (6 FILTERS) -----------------
    st.sidebar.title("🎛️ 多維度數據過濾")
    
    # Filter 1: County (Multi-select)
    all_counties = sorted(df_raw["CountyName"].unique().tolist())
    selected_counties = st.sidebar.multiselect(
        "🗺️ 縣市名稱：",
        options=all_counties,
        default=all_counties[:3], # Default select first 3 counties to keep graphs neat initially
        help="可多選，留空代表不限"
    )
    
    # Filter 2: Township (Multi-select, dynamically linked)
    if selected_counties:
        df_town_filtered = df_raw[df_raw["CountyName"].isin(selected_counties)]
    else:
        df_town_filtered = df_raw
    all_townships = sorted(df_town_filtered["TownName"].unique().tolist())
    selected_townships = st.sidebar.multiselect(
        "🏘️ 鄉鎮市區：",
        options=all_townships,
        help="僅顯示符合所選縣市之鄉鎮市區"
    )
    
    # Filter 3: Date (Multi-select)
    all_dates = sorted(df_raw["Date"].unique().tolist())
    selected_dates = st.sidebar.multiselect(
        "📅 觀測日期：",
        options=all_dates,
        default=all_dates
    )
    
    # Filter 4: Temperature Range (Slider)
    min_temp = float(df_raw["TEMP"].min())
    max_temp = float(df_raw["TEMP"].max())
    temp_range = st.sidebar.slider(
        "🌡️ 氣溫區間 (°C)：",
        min_value=min_temp,
        max_value=max_temp,
        value=(min_temp, max_temp),
        step=0.5
    )
    
    # Filter 5: Rain Probability Range (Slider)
    rain_range = st.sidebar.slider(
        "🌧️ 降雨機率 (%)：",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=5
    )
    
    # Filter 6: Humidity Range (Slider)
    humd_range = st.sidebar.slider(
        "💧 相對濕度 (%)：",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=5
    )
    
    # Apply filters
    df_filtered = df_raw.copy()
    if selected_counties:
        df_filtered = df_filtered[df_filtered["CountyName"].isin(selected_counties)]
    if selected_townships:
        df_filtered = df_filtered[df_filtered["TownName"].isin(selected_townships)]
    if selected_dates:
        df_filtered = df_filtered[df_filtered["Date"].isin(selected_dates)]
        
    df_filtered = df_filtered[
        (df_filtered["TEMP"] >= temp_range[0]) & 
        (df_filtered["TEMP"] <= temp_range[1]) &
        (df_filtered["RainProbability"] >= rain_range[0]) &
        (df_filtered["RainProbability"] <= rain_range[1]) &
        (df_filtered["HUMD"] >= humd_range[0]) &
        (df_filtered["HUMD"] <= humd_range[1])
    ]
    
    # ----------------- DISPLAY RESULTS AND CHARTS -----------------
    if df_filtered.empty:
        st.warning("⚠️ 沒有符合篩選條件的觀測站數據，請調整側邊欄的篩選條件！")
    else:
        st.markdown(f"🎉 **已篩選出 {len(df_filtered)} 筆自動測站觀測數據**")
        
        # Display main interactive dataframe
        st.dataframe(
            df_filtered[["StationName", "CountyName", "TownName", "TEMP", "HUMD", "WDSD", "RAIN", "RainProbability", "Date"]].rename(columns={
                "StationName": "測站名稱",
                "CountyName": "縣市",
                "TownName": "鄉鎮區",
                "TEMP": "氣溫 (°C)",
                "HUMD": "濕度 (%)",
                "WDSD": "風速 (m/s)",
                "RAIN": "雨量 (mm)",
                "RainProbability": "預估降雨率 (%)",
                "Date": "觀測日期"
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # CSV Export Downloader
        csv_data = df_filtered.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 匯出過濾後資料為 CSV 檔案",
            data=csv_data,
            file_name=f"CWA_filtered_observations_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # ----------------- 5 VISUALIZATIONS GRID -----------------
        st.markdown("### 📊 交叉統計交互可視化")
        
        # Row 1: Line Chart & Scatter Plot
        col_r1_1, col_r1_2 = st.columns(2, gap="large")
        
        with col_r1_1:
            st.markdown("<div class='explorer-card'>", unsafe_allow_html=True)
            st.markdown("#### 📈 縣市平均溫度對比 (Line Chart)")
            df_avg = df_filtered.groupby("CountyName")["TEMP"].mean().reset_index()
            fig_line = px.line(
                df_avg,
                x="CountyName",
                y="TEMP",
                markers=True,
                labels={"TEMP": "平均溫度 (°C)", "CountyName": "縣市"},
                color_discrete_sequence=["#58a6ff"]
            )
            fig_line.update_layout(margin=dict(l=40, r=40, t=10, b=40))
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_r1_2:
            st.markdown("<div class='explorer-card'>", unsafe_allow_html=True)
            st.markdown("#### 🎯 溫度 vs 濕度 氣泡分佈 (Scatter Plot)")
            fig_scatter = px.scatter(
                df_filtered,
                x="TEMP",
                y="HUMD",
                color="CountyName",
                size="RAIN",
                hover_name="StationName",
                labels={"TEMP": "溫度 (°C)", "HUMD": "相對濕度 (%)", "CountyName": "縣市"},
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig_scatter.update_layout(margin=dict(l=40, r=40, t=10, b=40))
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Row 2: Box Plot & Heatmap
        col_r2_1, col_r2_2 = st.columns(2, gap="large")
        
        with col_r2_1:
            st.markdown("<div class='explorer-card'>", unsafe_allow_html=True)
            st.markdown("#### 📦 各縣市溫度區間分佈 (Box Plot)")
            fig_box = px.box(
                df_filtered,
                x="CountyName",
                y="TEMP",
                color="CountyName",
                labels={"TEMP": "溫度 (°C)", "CountyName": "縣市"}
            )
            fig_box.update_layout(margin=dict(l=40, r=40, t=10, b=40))
            st.plotly_chart(fig_box, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_r2_2:
            st.markdown("<div class='explorer-card'>", unsafe_allow_html=True)
            st.markdown("#### 🌡️ 氣象屬性相關性矩陣 (Heatmap)")
            corr = df_filtered[["TEMP", "HUMD", "WDSD", "RAIN", "RainProbability"]].corr()
            fig_heat = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale="RdBu_r",
                aspect="auto"
            )
            fig_heat.update_layout(margin=dict(l=40, r=40, t=10, b=40))
            st.plotly_chart(fig_heat, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Row 3: Histogram (Full width)
        st.markdown("<div class='explorer-card'>", unsafe_allow_html=True)
        st.markdown("#### 🌧️ 降雨雨量強度分佈頻率 (Histogram)")
        fig_hist = px.histogram(
            df_filtered,
            x="RAIN",
            nbins=15,
            labels={"RAIN": "雨量 (mm)", "count": "測站數"},
            color_discrete_sequence=["#58a6ff"]
        )
        fig_hist.update_layout(
            margin=dict(l=40, r=40, t=10, b=40),
            yaxis_title="出現頻率 (測站數)"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
