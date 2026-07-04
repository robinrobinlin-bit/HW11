import streamlit as st
from services.windy_service import WindyService

# Page configuration
st.set_page_config(
    page_title="Windy 動態氣象圖 (Windy Map)",
    page_icon="🌀",
    layout="wide"
)

# Custom styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .panel-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
    }
    .panel-title {
        color: #f0f6fc;
        font-size: 1.1rem;
        font-weight: 700;
        border-bottom: 1px solid #30363d;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌀 Windy 動態氣象模擬地圖")
st.write("此部分完整嵌入 Windy.com 粒子流體大氣數值預測模型。提供雷達回波降雨與動態大氣雲層模擬的可視化展示。")

# 2-Column layout: center map, right settings
col_map, col_settings = st.columns([4, 1.2], gap="medium")

# Layer state
if "windy_active_layer" not in st.session_state:
    st.session_state.windy_active_layer = "雷達"

with col_map:
    # Fetch iframe URL
    embed_url = WindyService.get_embed_url(st.session_state.windy_active_layer)
    st.components.v1.iframe(src=embed_url, height=520, width=820)
    
    st.caption("🔍 滑鼠滾輪可縮放地圖，左鍵拖曳可移動視野。右下角播放鍵可預覽大氣流場未來演變趨勢。")

with col_settings:
    st.markdown("""<div class="panel-box">
<div class="panel-title">Windy 圖層控制</div>
</div>""", unsafe_allow_html=True)
    
    windy_layers = ["雷達", "天氣"]
    for wl in windy_layers:
        btn_type = "primary" if st.session_state.windy_active_layer == wl else "secondary"
        icon = "📡 " if wl == "雷達" else "🌤️ "
        label = f"{icon}動態雷達降雨" if wl == "雷達" else f"{icon}即時衛星雲圖"
        if st.button(label, key=f"btn_windy_page_{wl}", type=btn_type, use_container_width=True):
            st.session_state.windy_active_layer = wl
            st.rerun()
            
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""<div style="background-color:#0d1117; border: 1px solid #30363d; border-radius:8px; padding:12px; font-size:0.75rem; color:#8b949e; line-height:1.4;">
<b>圖層說明：</b><br/>
• <b>動態雷達降雨：</b> 整合全球氣象雷達與降雨回波，顯示實時及預測累積降雨粒子。<br/>
• <b>即時衛星雲圖：</b> 渲染低軌道氣象衛星紅外線/可見光雲層分佈，搭配高空風向流粒子。
</div>""", unsafe_allow_html=True)
