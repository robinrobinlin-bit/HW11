import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from services.database import query_all_regions, query_region_forecasts
from services.prediction_service import PredictionService, CSV_FILE

# Page configuration
st.set_page_config(
    page_title="AI 氣溫預測 (AI Prediction)",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .model-info-box {
        background-color: rgba(88, 166, 255, 0.1);
        border: 1px solid #58a6ff;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 機器學習氣溫預測模型 (ML Regressor Predictions)")
st.markdown("""
本模組藉由分析氣候資料，運行 **RandomForest (隨機森林)** 與 **XGBoost (極限梯度提升)** 迴歸模型，預測分區高低溫趨勢。
""")

# Model Summary Info
st.markdown("""
<div class="model-info-box">
    <span style="font-weight: bold; color: #58a6ff;">🧠 模型運行狀態：</span><br/>
    <ul>
        <li><b>Regressor 1:</b> RandomForestRegressor (包含 100 棵決策樹，限制最大深度以防止過擬合)</li>
        <li><b>Regressor 2:</b> XGBoostRegressor (XGBRegressor，梯度提升樹，基於殘差優化擬合)</li>
        <li><b>模型保存路徑:</b> models/ (已序列化持久保存)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

regions_list = query_all_regions()

if not regions_list:
    st.warning("資料庫目前為空。請先執行氣象數據抓取！")
else:
    # Sidebar control elements
    st.markdown("### 🎛️ 預測參數設定")
    col_s1, col_s2, col_s3 = st.columns([1.5, 1.5, 1])
    
    with col_s1:
        selected_region = st.selectbox(
            "選擇預測地區：",
            options=regions_list,
            key="ai_prediction_region_selector"
        )
    with col_s2:
        horizon = st.radio(
            "🔮 預測時間跨度：",
            options=["未來 24 小時 (Diurnal Hourly)", "未來 7 天 (Daily Forecast)"],
            horizontal=True
        )
    with col_s3:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 重新訓練 ML 模型", use_container_width=True):
            with st.spinner("正在對 RandomForest 與 XGBoost 進行模型擬合中..."):
                try:
                    PredictionService.train_models()
                    st.success("🎉 模型已成功訓練並保存至 models/ 檔案夾！")
                except Exception as e:
                    st.error(f"訓練失敗: {e}")
                    
    # Generate Predictions
    with st.spinner("載入模型預測數據中..."):
        df_pred = PredictionService.predict_temperature(selected_region)
        df_base = query_region_forecasts(selected_region)
        
    if df_pred.empty:
        st.info("尚無數據。")
    else:
        # Display predictions depending on horizon selection
        if horizon == "未來 7 天 (Daily Forecast)":
            st.markdown("### 📈 7天高低溫模型對比預測曲線 (RandomForest vs XGBoost vs CWA)")
            
            fig = go.Figure()
            
            # CWA Baseline
            fig.add_trace(go.Scatter(x=df_base["dataDate"], y=df_base["maxt"], mode="lines+markers", name="CWA 官方最高溫", line=dict(dash="dash", color="#8b949e")))
            fig.add_trace(go.Scatter(x=df_base["dataDate"], y=df_base["mint"], mode="lines+markers", name="CWA 官方最低溫", line=dict(dash="dash", color="#484f58")))
            
            # RandomForest
            fig.add_trace(go.Scatter(x=df_pred["dataDate"], y=df_pred["rf_maxt"], mode="lines+markers", name="RF 預測最高溫", line=dict(color="#ff7b72", width=2.5)))
            fig.add_trace(go.Scatter(x=df_pred["dataDate"], y=df_pred["rf_mint"], mode="lines+markers", name="RF 預測最低溫", line=dict(color="#58a6ff", width=2.5)))
            
            # XGBoost
            fig.add_trace(go.Scatter(x=df_pred["dataDate"], y=df_pred["xgb_maxt"], mode="lines+markers", name="XGB 預測最高溫", line=dict(color="#d2a8ff", width=2.5)))
            fig.add_trace(go.Scatter(x=df_pred["dataDate"], y=df_pred["xgb_mint"], mode="lines+markers", name="XGB 預測最低溫", line=dict(color="#bc8cff", width=2.5)))
            
            fig.update_layout(
                xaxis_title="預報日期",
                yaxis_title="氣溫 (°C)",
                margin=dict(l=40, r=40, t=20, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.markdown("### 📋 數據對照表")
            df_display = pd.merge(df_base[["dataDate", "mint", "maxt"]], df_pred, on="dataDate")
            df_display = df_display[["dataDate", "mint", "rf_mint", "xgb_mint", "maxt", "rf_maxt", "xgb_maxt"]]
            df_display.columns = ["預報日期", "CWA 最低", "RF 最低", "XGB 最低", "CWA 最高", "RF 最高", "XGB 最高"]
            
            st.dataframe(df_display.style.format("{:.1f} °C", subset=["CWA 最低", "RF 最低", "XGB 最低", "CWA 最高", "RF 最高", "XGB 最高"]), use_container_width=True, hide_index=True)
            
        else: # 24 Hours Diurnal Hourly Forecast
            st.markdown("### 📈 明日 24 小時逐時溫度分佈 (Sine Diurnal Cycle Model)")
            
            df_24h = PredictionService.predict_next_24_hours(selected_region)
            
            fig_24 = go.Figure()
            fig_24.add_trace(go.Scatter(x=df_24h["hour"], y=df_24h["rf_predicted_temp"], mode="lines+markers", name="RandomForest 逐時預估", line=dict(color="#58a6ff", width=3)))
            fig_24.add_trace(go.Scatter(x=df_24h["hour"], y=df_24h["xgb_predicted_temp"], mode="lines+markers", name="XGBoost 逐時預估", line=dict(color="#d2a8ff", width=3)))
            
            fig_24.update_layout(
                xaxis_title="時間 (Hour)",
                yaxis_title="氣溫 (°C)",
                margin=dict(l=40, r=40, t=20, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_24, use_container_width=True)
            
            # Data table
            st.markdown("### 📋 逐時預估數據表")
            df_24_display = df_24h.copy()
            df_24_display.columns = ["時間", "RandomForest 預測值", "XGBoost 預測值"]
            st.dataframe(df_24_display.style.format("{:.1f} °C", subset=["RandomForest 預測值", "XGBoost 預測值"]), use_container_width=True, hide_index=True)

        # ----------------- CSV EXPORT DOWNLOAD BUTTON -----------------
        st.markdown("---")
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
                csv_data = f.read()
            st.download_button(
                label="📥 匯出預測結果為 CSV 檔案",
                data=csv_data,
                file_name=f"{selected_region}_predictions.csv",
                mime="text/csv",
                use_container_width=True
            )
