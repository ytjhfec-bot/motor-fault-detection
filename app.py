import streamlit as st
import pandas as pd
import time

# 1. 網頁配置
st.set_page_config(page_title="馬達即時預警系統", layout="wide")
st.title("⚡ 馬達智慧監控：10分鐘動態模擬演示")

# 2. 載入資料
@st.cache_data
def get_data():
    df = pd.read_csv('motor_data.csv')
    return df

df_full = get_data()

# 3. 側邊欄：控制演示
st.sidebar.header("演示控制")
start_btn = st.sidebar.button("🚀 開始即時監控演示")
speed = st.sidebar.slider("模擬速度 (秒/筆)", 0.1, 1.0, 0.5)

# 4. 建立動態容器 (Placeholders)
# 這些容器會被後面的循環不斷更新內容
metric_row = st.empty()
chart_row = st.empty()
status_row = st.empty()

# 5. 預警閾值
temp_limit = 60
vib_limit = 2.5

# 6. 模擬「動態跳動」的邏輯
if start_btn:
    # 我們從第 1 筆資料開始，逐一增加顯示的資料量
    for i in range(1, len(df_full) + 1):
        # 取得目前為止的數據
        current_view = df_full.iloc[:i]
        latest = current_view.iloc[-1]
        
        # --- 更新上方數值 (Metrics) ---
        with metric_row.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("當前溫度", f"{latest['temperature']}°C")
            c2.metric("X軸振動", f"{latest['vibration_x']}")
            c3.metric("Z軸振動", f"{latest['vibration_z']}")

        # --- 更新中段圖表 (Charts) ---
        with chart_row.container():
            # 只顯示最近的 50 筆數據，讓圖表有「滾動」感
            display_df = current_view.tail(50) 
            st.line_chart(display_df.set_index('timestamp')[['vibration_x', 'vibration_z', 'temperature']])

        # --- 更新下方診斷 (Alerts) ---
        with status_row.container():
            if latest['temperature'] > temp_limit or latest['vibration_x'] > vib_limit:
                st.error(f"🚨 異常警報：{latest['timestamp']} 偵測到數值超標！")
            else:
                st.success("✅ 系統狀態：正常運行中...")

        # 暫停一下，產生動畫效果
        time.sleep(speed)
else:
    st.info("請點擊左側『開始即時監控演示』按鈕來啟動數據模擬。")
