import streamlit as st
import pandas as pd
import time

# 1. 網頁配置
st.set_page_config(page_title="馬達智聯網預警系統", layout="wide")
st.title("⚡ 馬達監控動態演示：即時預警與閾值設定")

# 2. 載入資料 (請確認檔案名為 motor_data.csv)
@st.cache_data
def get_data():
    # 讀取您提供的 600 筆數據
    df = pd.read_csv('motor_data.csv')
    return df

df_full = get_data()

# 3. 側邊欄：保留並強化調整功能
st.sidebar.header("⚙️ 預警參數設定")
# 這些數值可以隨時在側邊欄調整
temp_threshold = st.sidebar.slider("溫度警報閾值 (°C)", 40, 90, 60)
vib_threshold = st.sidebar.slider("振動警報閾值 (X/Z)", 1.0, 5.0, 2.5, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("🎮 演示控制")
speed = st.sidebar.select_slider("數據更新速度", options=[0.1, 0.2, 0.5, 1.0], value=0.2)
start_btn = st.sidebar.button("🚀 開始模擬監控")
stop_btn = st.sidebar.button("🛑 停止/重置")

# 4. 建立介面佈局容器
# 使用 empty() 讓內容可以在同一個地方不斷刷新，而不是一直往下長
metric_placeholder = st.empty()
chart_placeholder = st.empty()
alert_placeholder = st.empty()

# 5. 執行模擬邏輯
if start_btn:
    st.toast("系統啟動中... 開始讀取 10 分鐘歷史數據流")
    
    # 逐行讀取 CSV，模擬數據進來
    for i in range(1, len(df_full) + 1):
        # 取得當前時間點的數據
        current_data = df_full.iloc[:i]
        latest = current_data.iloc[-1]
        
        # --- A. 更新儀表板數據 ---
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)
            # 這裡會根據您在側邊欄設定的門檻，動態顯示 Delta 顏色
            col1.metric("馬達溫度", f"{latest['temperature']}°C", 
                       delta=f"{latest['temperature'] - temp_threshold:.1f}", 
                       delta_color="inverse")
            col2.metric("X軸振動", f"{latest['vibration_x']}", 
                       delta=f"{latest['vibration_x'] - vib_threshold:.2f}", 
                       delta_color="inverse")
            col3.metric("Z軸振動", f"{latest['vibration_z']}", 
                       delta=f"{latest['vibration_z'] - vib_threshold:.2f}", 
                       delta_color="inverse")

        # --- B. 更新趨勢圖 (顯示最近 60 筆，模擬滾動效果) ---
        with chart_placeholder.container():
            display_df = current_data.tail(60).set_index('timestamp')
            st.line_chart(display_df[['vibration_x', 'vibration_z', 'temperature']])

        # --- C. 即時判斷與報警 ---
        with alert_placeholder.container():
            # 判斷是否超過剛才在側邊欄設定的閾值
            is_temp_fault = latest['temperature'] > temp_threshold
            is_vib_fault = (latest['vibration_x'] > vib_threshold) or (latest['vibration_z'] > vib_threshold)
            
            if is_temp_fault or is_vib_fault:
                st.error(f"🚨 【異常預警】時間：{latest['timestamp']}")
                if is_temp_fault: st.write(f"- ⚠️ 溫度過熱：目前 {latest['temperature']}°C > 門檻 {temp_threshold}°C")
                if is_vib_fault: st.write(f"- ⚠️ 振動異常：已超過設定值 {vib_threshold}")
            else:
                st.success("✅ 系統狀態：正常運行中")

        # 控制模擬速度
        time.sleep(speed)
        
        # 如果按下停止按鈕則跳出循環 (Streamlit 的一種基本處理方式)
        if stop_btn:
            st.warning("演示已終止")
            break
else:
    st.info("💡 提示：請先在左側調整「警報閾值」，然後點擊「開始模擬監控」進行演示。")
