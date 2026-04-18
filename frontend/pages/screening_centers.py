from menu import show_sidebar  # ดึงฟังก์ชันมาจากไฟล์ menu.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="ศูนย์คัดกรองใกล้คุณ", layout="wide")
show_sidebar()  # สั่งให้แสดง Sidebar

# --- ตรวจสอบสิทธิ์และการประเมินความเสี่ยง ---
if 'api_result' not in st.session_state or st.session_state['api_result'] is None:
    st.warning("⚠️ โปรดทำการประเมินความเสี่ยงที่หน้าหลักก่อน")
    if st.button("🔙 ไปหน้าหลัก"):
        st.switch_page("pages/home.py")
    st.stop()

data = st.session_state['api_result']
prediction = data.get("prediction", "NO")

st.markdown("<h1>📍 ศูนย์คัดกรองมะเร็งปอดใกล้คุณ</h1>", unsafe_allow_html=True)

if prediction == "YES":
    st.error(
        "📢 ระบบวิเคราะห์ว่าคุณมีความเสี่ยงสูง แนะนำให้เข้าพบแพทย์เพื่อรับการตรวจ Low-dose CT Scan")

    # ข้อมูลจำลองพิกัดโรงพยาบาลหลัก (ในงานจริงสามารถใช้ Google Maps API ดึง Dynamic ได้)
    # ตัวอย่างพิกัดศูนย์มะเร็งชั้นนำ
    hospital_data = pd.DataFrame([
        {"name": "สถาบันมะเร็งแห่งชาติ", "lat": 13.7672,
            "lon": 100.5277, "type": "รัฐบาล"},
        {"name": "ศูนย์มะเร็ง รพ.วัฒโนสถ", "lat": 13.7485,
            "lon": 100.5827, "type": "เอกชน"},
        {"name": "ศูนย์มะเร็งตรงเป้า รพ.จุฬารัตน์ 9",
            "lat": 13.6775, "lon": 100.7223, "type": "เอกชน"},
        {"name": "โรงพยาบาลมะเร็งกรุงเทพ", "lat": 13.7791,
            "lon": 100.5426, "type": "เอกชน"},
    ])

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🗺️ แผนที่พิกัดศูนย์คัดกรอง")
        # แสดงผลด้วย Map ของ Streamlit หรือ Plotly
        st.map(hospital_data)

    with col2:
        st.subheader("🏥 รายชื่อสถานพยาบาลที่แนะนำ")
        for index, row in hospital_data.iterrows():
            with st.expander(f"📍 {row['name']}"):
                st.write(f"ประเภท: {row['type']}")
                st.markdown(
                    f"[🔗 ดูเส้นทางบน Google Maps](https://www.google.com/maps/search/{row['name']})")

else:
    st.success(
        "✅ ความเสี่ยงของคุณอยู่ในระดับต่ำ อย่างไรก็ตามควรตรวจสุขภาพประจำปีอย่างสม่ำเสมอ")
    st.info("คุณสามารถดูรายชื่อโรงพยาบาลเผื่อไว้สำหรับการตรวจเช็คในอนาคตได้")
    # แสดงรายชื่อแบบสั้นๆ หรือตารางข้อมูลทั่วไป
