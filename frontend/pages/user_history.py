import streamlit as st
import requests
import pandas as pd
from menu import show_sidebar, show_cookie_banner

st.set_page_config(page_title="ประวัติการใช้งาน", layout="wide")
show_sidebar()
show_cookie_banner()

if not st.session_state.get('logged_in'):
    st.switch_page("app.py")

st.title("📜 ประวัติการบันทึกข้อมูลของคุณ")

user_id = st.session_state['id_card']

# 1. ยิง API ไปขอดึงประวัติของ user_id นี้
try:
    res = requests.get(f"http://127.0.0.1:8001/history/{user_id}")

    if res.status_code == 200:
        history_data = res.json()

        if len(history_data) > 0:
            # 2. แปลงข้อมูล JSON เป็นตาราง DataFrame
            df = pd.DataFrame(history_data)

            # เปลี่ยนชื่อคอลัมน์ให้ดูสวยงาม
            df = df.rename(columns={
                "created_at": "วัน-เวลาที่ตรวจ",
                "risk_score": "ความเสี่ยง (%)",
                "prediction_result": "ผลประเมินเบื้องต้น"
            })

            # จัดรูปแบบวันที่
            df['วัน-เวลาที่ตรวจ'] = pd.to_datetime(
                df['วัน-เวลาที่ตรวจ']).dt.strftime('%Y-%m-%d %H:%M:%S')

            # 3. สร้าง UI สรุปด้านบน (เหมือนในรูปของคุณ)
            col1, col2 = st.columns(2)
            col1.metric("จำนวนการตรวจทั้งหมด", f"{len(df)} ครั้ง")
            col2.metric("ความเสี่ยงล่าสุด", f"{df.iloc[0]['ความเสี่ยง (%)']}%")

            st.divider()

            # 4. แสดงตาราง
            st.subheader("📋 รายการประวัติย้อนหลัง")
            st.dataframe(df[['วัน-เวลาที่ตรวจ', 'ความเสี่ยง (%)',
                         'ผลประเมินเบื้องต้น']], use_container_width=True)

        else:
            st.info(
                "📅 คุณยังไม่มีประวัติการคัดกรองในระบบ ลองไปประเมินความเสี่ยงที่หน้าหลักดูนะครับ")

except Exception as e:
    st.error("❌ ไม่สามารถเชื่อมต่อกับฐานข้อมูลประวัติได้")
