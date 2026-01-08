import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 網頁配置
st.set_page_config(page_title="馬達智慧監控系統", layout="wide")
st.title("⚡ 馬達振動與溫度即時預警平台")

# 2. 載入資料
@st.cache_data
def load_data():
    df = pd.read_csv('motor_data.xlsx - 工作表1.csv')
    return df

df = load_data()

# 3. 側邊欄設定：預警閾值
st.sidebar.header("預警參數設定")
temp_limit = st.sidebar.slider("溫度警告閾值 (°C)", 40, 100, 60)
vib_limit = st.sidebar.slider("振動警告閾值", 1.0, 5.0, 2.8, step=0.1)

# 4. 主要儀表板內容
col1, col2, col3 = st.columns(3)

# 取得最新一筆數據
latest_data = df.iloc[-1]
current_temp = latest_data['temperature']
current_vib_x = latest_data['vibration_x']
current_vib_z = latest_data['vibration_z']

with col1:
    color = "inverse" if current_temp > temp_limit else "normal"
    st.metric("當前溫度", f"{current_temp} °C", delta=f"{current_temp - temp_limit} °C", delta_color=color)

with col2:
    st.metric("X軸振動", f"{current_vib_x}", delta=f"{current_vib_x - vib_limit:.2f}", delta_color="inverse" if current_vib_x > vib_limit else "normal")

with col3:
    st.metric("Z軸振動", f"{current_vib_z}", delta=f"{current_vib_z - vib_limit:.2f}", delta_color="inverse" if current_vib_z > vib_limit else "normal")

# 5. 數據可視化
st.subheader("📈 歷史趨勢追蹤")
tab1, tab2 = st.tabs(["振動分析", "溫度監控"])

with tab1:
    fig_vib = px.line(df, x='timestamp', y=['vibration_x', 'vibration_z'], title="雙軸振動趨勢")
    fig_vib.add_hline(y=vib_limit, line_dash="dash", line_color="red", annotation_text="警告線")
    st.plotly_chart(fig_vib, use_container_width=True)

with tab2:
    fig_temp = px.area(df, x='timestamp', y='temperature', title="馬達溫度紀錄", color_discrete_sequence=['orange'])
    fig_temp.add_hline(y=temp_limit, line_dash="dash", line_color="red", annotation_text="過熱閾值")
    st.plotly_chart(fig_temp, use_container_width=True)

# 6. 自動診斷預警
st.subheader("🚨 系統診斷訊息")
if current_temp > temp_limit or current_vib_x > vib_limit or current_vib_z > vib_limit:
    st.error(f"⚠️ 警告：偵測到異常！時間：{latest_data['timestamp']}")
    if current_temp > temp_limit:
        st.write("- 異常原因：馬達溫度過高，請檢查散熱系統。")
    if current_vib_x > vib_limit or current_vib_z > vib_limit:
        st.write("- 異常原因：振動幅度異常，可能存在結構鬆動或不平衡。")
else:
    st.success("✅ 系統狀態：運行正常。")