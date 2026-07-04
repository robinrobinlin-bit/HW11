import streamlit as st
import pandas as pd
from services.database import query_all_regions, query_region_forecasts
from services.prediction_service import PredictionService

# Page configuration
st.set_page_config(
    page_title="模型評估 (Model Evaluation)",
    page_icon="📈",
    layout="wide"
)

# Custom styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .metrics-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f0f6fc;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 AI 氣溫預測模型評估 (Model Evaluation & Metrics)")
st.markdown("""
此頁面提供機器學習預測模型與中央氣象署 (CWA) 官方預報的定量誤差分析，計算平均絕對誤差 (MAE) 與均方根誤差 (RMSE) 指標。
""")

regions_list = query_all_regions()

if not regions_list:
    st.warning("資料庫目前為空。請先執行氣象數據抓取！")
else:
    selected_region = st.selectbox(
        "選擇評估地區：",
        options=regions_list,
        key="evaluation_region_selector"
    )
    
    # Fetch data
    df_base = query_region_forecasts(selected_region)
    df_pred = PredictionService.predict_temperature(selected_region)
    metrics = PredictionService.calculate_evaluation_metrics(selected_region)
    
    if df_base.empty or df_pred.empty:
        st.info("該地區數據不足以進行誤差評估。")
    else:
        # Show Metrics Cards
        st.markdown("<div class='metrics-header'>📊 預測誤差統計指標 (MAE & RMSE)</div>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric(
                label="最低氣溫平均絕對誤差 (MinT MAE)",
                value=f"{metrics['mint_mae']:.2f} °C",
                help="Mean Absolute Error: 預測最低溫與官方預報平均絕對偏差度"
            )
        with col_m2:
            st.metric(
                label="最低氣溫均方根誤差 (MinT RMSE)",
                value=f"{metrics['mint_rmse']:.2f} °C",
                help="Root Mean Squared Error: 預測最低溫的標準差誤差（對大偏差更敏感）"
            )
        with col_m3:
            st.metric(
                label="最高氣溫平均絕對誤差 (MaxT MAE)",
                value=f"{metrics['maxt_mae']:.2f} °C",
                help="Mean Absolute Error: 預測最高溫與官方預報平均絕對偏差度"
            )
        with col_m4:
            st.metric(
                label="最高氣溫均方根誤差 (MaxT RMSE)",
                value=f"{metrics['maxt_rmse']:.2f} °C",
                help="Root Mean Squared Error: 預測最高溫的標準差誤差"
            )
            
        st.markdown("---")
        
        # Comparison curve
        df_merged = pd.merge(df_base, df_pred, on=["regionName", "dataDate"])
        
        col_curve, col_residuals = st.columns([1, 1], gap="large")
        
        with col_curve:
            st.markdown("### 📈 官方預報 vs AI 預測曲線")
            chart_df = df_merged.set_index("dataDate")[["maxt", "predicted_maxt", "mint", "predicted_mint"]]
            chart_df.columns = ["官方最高溫", "AI預測最高溫", "官方最低溫", "AI預測最低溫"]
            st.line_chart(chart_df, color=["#ff7b72", "#ffb454", "#58a6ff", "#00d2ff"])
            
        with col_residuals:
            st.markdown("### 📊 預測殘差與誤差變量 (Error Residuals)")
            residuals_df = df_merged.set_index("dataDate")[["error_maxt", "error_mint"]]
            residuals_df.columns = ["最高溫預測誤差 (MaxT Error)", "最低溫預測誤差 (MinT Error)"]
            st.bar_chart(residuals_df, color=["#ff9e3b", "#06b6d4"])
            st.caption("🔍 誤差線越接近 0 軸，代表 AI 模型與官方預報的契合度越高，預測越準確。")
