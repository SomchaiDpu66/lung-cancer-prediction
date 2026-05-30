import streamlit as st
import requests
import pandas as pd
from menu import show_sidebar, show_cookie_banner
from datetime import datetime


def to_thai_datetime(date_str):
    if not date_str or pd.isna(date_str):
        return "-"
    try:
        # ลบตัวอักษร T (ถ้ามี) และเศษเสี้ยววินาทีออก เพื่อให้เหลือแค่ "YYYY-MM-DD HH:MM:SS"
        clean_date = str(date_str).replace("T", " ").split(".")[0]
        dt = datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S")

        # รายชื่อเดือนภาษาไทยแบบย่อ
        thai_months = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                       "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]

        # แปลง ค.ศ. เป็น พ.ศ.
        thai_year = dt.year + 543

        # จัดรูปแบบข้อความ เช่น "29 พ.ค. 2569 เวลา 10:02 น."
        return f"{dt.day} {thai_months[dt.month]} {thai_year} เวลา {dt.strftime('%H:%M')} น."
    except Exception:
        # หากเกิดข้อผิดพลาดในการแปลง จะแสดงข้อมูลดิบแบบเดิม
        return date_str


st.set_page_config(page_title="ประวัติการใช้งาน", layout="wide")

# เรียกใช้ sidebar ที่เราปรับปรุงโชว์รูปโปรไฟล์แล้ว
show_sidebar()
show_cookie_banner()

if not st.session_state.get('logged_in'):
    st.switch_page("app.py")

st.title("📜 ประวัติการบันทึกข้อมูลของคุณ")

# --- [แก้ไขจุดที่ 1: เปลี่ยนจาก id_card เป็น username] ---
user_id = st.session_state.get('username')

# 1. ยิง API ไปขอดึงประวัติของ username นี้
try:
    # --- [แก้ไขจุดที่ 2: ตรวจสอบ URL ให้ตรงกับ Backend ใหม่] ---
    # มั่นใจว่า API ที่ Backend ใช้ Path: /history/{username}
    res = requests.get(
        f"https://lung-cancer-prediction-production.up.railway.app/history/{user_id}",
        timeout=5
    )

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

            # === 🌟 ย้ายโค้ดแปลงภาษาไทยมาไว้ตรงนี้ (ทำข้อมูลให้เสร็จก่อนโชว์) ===
            if 'วัน-เวลาที่ตรวจ' in df.columns:
                df['วัน-เวลาที่ตรวจ'] = df['วัน-เวลาที่ตรวจ'].apply(
                    to_thai_datetime)

            # 3. สร้าง UI สรุปด้านบน
            col1, col2 = st.columns(2)
            col1.metric("จำนวนการตรวจทั้งหมด", f"{len(df)} ครั้ง")

            # ดึงค่าความเสี่ยงล่าสุด (แถวบนสุด)
            latest_risk = df.iloc[0]['ความเสี่ยง (%)']
            col2.metric("ความเสี่ยงล่าสุด", f"{latest_risk}%")

            st.divider()

            # 4. แสดงตาราง
            st.subheader("📋 รายการประวัติย้อนหลัง")
            # เลือกเฉพาะคอลัมน์ที่ต้องการแสดง
            st.dataframe(df[['วัน-เวลาที่ตรวจ', 'ความเสี่ยง (%)',
                         'ผลประเมินเบื้องต้น']], use_container_width=True)

        else:
            st.info(
                "📅 คุณยังไม่มีประวัติการคัดกรองในระบบ ลองไปประเมินความเสี่ยงที่หน้าหลักดูนะครับ")
    else:
        st.error(f"❌ ไม่สามารถดึงข้อมูลได้ (Status Code: {res.status_code})")

except Exception as e:
    # เพิ่มการแสดง Error เบื้องต้นเพื่อช่วยในการ Debug
    st.error(f"❌ ไม่สามารถเชื่อมต่อกับฐานข้อมูลประวัติได้")
    print(f"Debug History Page: {str(e)}")
