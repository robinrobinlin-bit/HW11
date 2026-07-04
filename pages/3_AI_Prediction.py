import streamlit as st
import pandas as pd
from services.database import query_all_regions, query_region_forecasts
from services.prediction_service import PredictionService

# Page configuration
st.set_page_config(
    page_title="AI 氣溫預測 (AI Prediction)",
    page_icon="🤖",
    layout="wide"
)

# Custom styles
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

st.title("🤖 AI 氣溫預測模型 (AI Temperature Prediction)")
st.markdown("""
此模組呈現機器學習氣象模型之預估結果。AI 預測模型藉由分析歷史數據、風向粒子特徵，輸出各沿海及海域未來一週的高低氣溫預測。
""")

# Model Summary Info
st.markdown("""
<div class="model-info-box">
    <span style="font-weight: bold; color: #58a6ff;">🧠 模型運行資訊：</span><br/>
    <ul>
        <li><b>演算法模型：</b> Gradient Boosting Regressor (梯度提升迴歸器)</li>
        <li><b>訓練特徵值：</b> 氣壓變量、露點溫度、低空風切、大氣對流有效位能 (CAPE)</li>
        <li><b>評估基準：</b> CWA 官方預報作為基準對照 (Baseline)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

regions_list = query_all_regions()

if not regions_list:
    st.warning("資料庫目前為空。請先執行氣象數據抓取！")
else:
    selected_region = st.selectbox(
        "選擇預測地區：",
        options=regions_list,
        key="ai_prediction_region_selector"
    )
    
    # Query Base Forecast
    df_base = query_region_forecasts(selected_region)
    # Query AI Predictions
    df_pred = PredictionService.predict_temperature(selected_region)
    
    if df_base.empty or df_pred.empty:
        st.info("該地區尚無足夠的數據進行 AI 預測模擬。")
    else:
        # Merge for display
        df_merged = pd.merge(df_base, df_pred, on=["regionName", "dataDate"])
        
        col_chart, col_data = st.columns([3, 2], gap="large")
        
        with col_chart:
            st.markdown("### 📈 AI 預估氣溫變化曲線")
            # Build chart dataframe
            chart_df = df_merged.set_index("dataDate")[["predicted_mint", "predicted_maxt"]]
            chart_df.columns = ["AI 預測最低溫", "AI 預測最高溫"]
            st.line_chart(chart_df, color=["#58a6ff", "#ff7b72"])
            
        with col_data:
            st.markdown("### 📋 AI 預測與官方預報對照表")
            display_df = df_merged[["dataDate", "mint", "predicted_mint", "maxt", "predicted_maxt"]].copy()
            display_df.columns = ["日期 (Date)", "官方最低", "AI預測最低", "官方最高", "AI預測最高"]
            
            st.dataframe(
                display_df.style.format({
                    "官方最低": "{:.1f} °C",
                    "AI預測最低": "{:.1f} °C",
                    "官方最高": "{:.1f} °C",
                    "AI預測最高": "{:.1f} °C"
                }),
                use_container_width=True,
                hide_index=True
            )
