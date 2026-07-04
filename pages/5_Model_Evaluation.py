import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    .eval-section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f0f6fc;
        margin-top: 20px;
        margin-bottom: 12px;
        border-left: 4px solid #58a6ff;
        padding-left: 10px;
    }
    .metrics-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 迴歸預測模型定量評估 (Quantitative Model Evaluation)")
st.markdown("""
本分頁展示 **RandomForestRegressor** 與 **XGBoostRegressor** 迴歸模型在測試集上的效能評估指標與特徵貢獻度權重。
""")

# Load metrics
with st.spinner("載入模型評估指標中..."):
    try:
        metrics = PredictionService.get_metrics()
    except Exception:
        metrics = PredictionService.train_models()

rf_m = metrics["rf"]
xgb_m = metrics["xgb"]

# ----------------- SIDE-BY-SIDE METRICS CARD DISPLAY -----------------
st.markdown("<div class='eval-section-title'>📊 迴歸精準度指標對比 (RandomForest vs XGBoost)</div>", unsafe_allow_html=True)

col_rf, col_xgb = st.columns(2, gap="large")

with col_rf:
    st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
    st.markdown("#### 🌳 RandomForestRegressor 表現")
    col_rf1, col_rf2, col_rf3 = st.columns(3)
    with col_rf1:
        st.metric("平均絕對誤差 (MAE)", f"{rf_m['maxt_mae']:.2f} °C", help="Mean Absolute Error")
    with col_rf2:
        st.metric("均方根誤差 (RMSE)", f"{rf_m['maxt_rmse']:.2f} °C", help="Root Mean Squared Error")
    with col_rf3:
        st.metric("判定係數 (R²)", f"{rf_m['maxt_r2']:.2f}", help="Coefficient of Determination")
    st.markdown("</div>", unsafe_allow_html=True)

with col_xgb:
    st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
    st.markdown("#### 🚀 XGBoostRegressor 表現")
    col_xgb1, col_xgb2, col_xgb3 = st.columns(3)
    with col_xgb1:
        st.metric("平均絕對誤差 (MAE)", f"{xgb_m['maxt_mae']:.2f} °C", help="Mean Absolute Error")
    with col_xgb2:
        st.metric("均方根誤差 (RMSE)", f"{xgb_m['maxt_rmse']:.2f} °C", help="Root Mean Squared Error")
    with col_xgb3:
        st.metric("判定係數 (R²)", f"{xgb_m['maxt_r2']:.2f}", help="Coefficient of Determination")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PLOTLY INTERACTIVE SCATTER PLOT (ACTUAL VS PREDICTED) -----------------
st.markdown("<div class='eval-section-title'>🎯 實測值 vs 預測值對角散佈圖 (Actual vs Predicted Scatter)</div>", unsafe_allow_html=True)

df_scatter = PredictionService.get_test_predictions_for_scatter()

col_sc1, col_sc2 = st.columns(2, gap="large")

with col_sc1:
    st.markdown("##### RandomForest 擬合散佈圖")
    if not df_scatter.empty:
        fig_rf_sc = go.Figure()
        
        # Points
        fig_rf_sc.add_trace(go.Scatter(
            x=df_scatter["actual"],
            y=df_scatter["rf_predicted"],
            mode="markers",
            marker=dict(color="#58a6ff", size=8, opacity=0.7),
            name="RF 預測點"
        ))
        
        # Diagonal Line (y=x)
        min_val = min(df_scatter["actual"].min(), df_scatter["rf_predicted"].min())
        max_val = max(df_scatter["actual"].max(), df_scatter["rf_predicted"].max())
        fig_rf_sc.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(color="#ff7b72", dash="dash"),
            name="完美擬合對角線"
        ))
        
        fig_rf_sc.update_layout(
            xaxis_title="實際溫度 (CWA Actual, °C)",
            yaxis_title="RF 預測溫度 (°C)",
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_rf_sc, use_container_width=True)

with col_sc2:
    st.markdown("##### XGBoost 擬合散佈圖")
    if not df_scatter.empty:
        fig_xgb_sc = go.Figure()
        
        # Points
        fig_xgb_sc.add_trace(go.Scatter(
            x=df_scatter["actual"],
            y=df_scatter["xgb_predicted"],
            mode="markers",
            marker=dict(color="#d2a8ff", size=8, opacity=0.7),
            name="XGB 預測點"
        ))
        
        # Diagonal Line (y=x)
        fig_xgb_sc.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(color="#ff7b72", dash="dash"),
            name="完美擬合對角線"
        ))
        
        fig_xgb_sc.update_layout(
            xaxis_title="實際溫度 (CWA Actual, °C)",
            yaxis_title="XGB 預測溫度 (°C)",
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_xgb_sc, use_container_width=True)

# ----------------- PLOTLY BAR CHART (FEATURE IMPORTANCE) -----------------
st.markdown("<div class='eval-section-title'>🔑 機器學習特徵權重重要性比對 (Feature Importances)</div>", unsafe_allow_html=True)

rf_fi = rf_m["maxt_feature_importance"]
xgb_fi = xgb_m["maxt_feature_importance"]

# Build dataframe
features = list(rf_fi.keys())
fi_records = []
for f in features:
    fi_records.append({"Feature": f, "Model": "RandomForest", "Importance": rf_fi[f]})
    fi_records.append({"Feature": f, "Model": "XGBoost", "Importance": xgb_fi[f]})
df_fi = pd.DataFrame(fi_records)

# Translate features to readable names
feature_labels = {
    "region_code": "地區編碼 (Region)",
    "month": "預報月份 (Month)",
    "day": "當月日期 (Day)",
    "dayofweek": "星期代碼 (Weekday)",
    "dayofyear": "年度累計日 (Day of Year)"
}
df_fi["Feature"] = df_fi["Feature"].map(feature_labels)

fig_fi = px.bar(
    df_fi,
    x="Feature",
    y="Importance",
    color="Model",
    barmode="group",
    color_discrete_map={"RandomForest": "#58a6ff", "XGBoost": "#d2a8ff"},
    labels={"Importance": "特徵重要性比例", "Feature": "預測特徵項目"}
)

fig_fi.update_layout(
    margin=dict(l=40, r=40, t=20, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_fi, use_container_width=True)
st.caption("🔍 特徵權重越高代表該變量對於氣溫預估的貢獻與決策樹分裂次數越多。地區與年度累計日通常具有較高權重。")
