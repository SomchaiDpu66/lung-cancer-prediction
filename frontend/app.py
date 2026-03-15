import streamlit as st
import requests
import os
from menu import show_sidebar, show_cookie_banner


# --- 1. ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LungGuard AI - Login", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="collapsed")

# --- 2. Custom CSS สไตล์ Modern UI (ฟอนต์ Prompt & ความนุ่มนวล) ---
st.markdown("""
    <style>
    /* 🌟 นำเข้าฟอนต์ Prompt จาก Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');
    
    /* บังคับใช้ฟอนต์ Prompt ทั้งระบบ */
    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif !important;
    }
    
    /* พื้นหลังหลัก */
    .stApp { background-color: #E2E8F0; }
    
    /* กล่องฝั่งซ้าย (สีน้ำเงิน) */
    [data-testid="column"]:nth-of-type(1) {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px 0 0 24px; /* ปรับให้โค้งมนขึ้น */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: -5px 10px 25px rgba(0,0,0,0.1);
    }
    
    /* กล่องฝั่งขวา (สีขาว) */
    [data-testid="column"]:nth-of-type(2) {
        background: white;
        padding: 3rem;
        border-radius: 0 24px 24px 0; /* ปรับให้โค้งมนขึ้น */
        box-shadow: 10px 10px 25px rgba(0,0,0,0.1);
    }
    
    /* 🌟 ปรับแต่งช่องกรอกข้อมูล (นุ่มนวลและสะอาดตา) */
    .stTextInput>div>div>input {
        border-radius: 12px; /* โค้งมนขึ้น */
        border: 1.5px solid #E2E8F0;
        padding: 12px 15px;
        transition: border-color 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #3B82F6; /* สีเปลี่ยนเมื่อคลิกพิมพ์ */
        box-shadow: 0 0 0 1px #3B82F6;
    }
    
    /* 🌟 ปรับแต่งปุ่ม Sign Up / Sign In (ปุ่มหลัก) */
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        color: white;
        border-radius: 30px; /* ทรงแคปซูล โค้งมนนุ่มนวลสุดๆ */
        padding: 12px 30px;
        font-weight: 600;
        letter-spacing: 0.5px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* ปรับแต่งข้อความ */
    h1, h2, h3 { color: #1E3A8A; font-weight: 700; }
    .white-text, .white-text h1, .white-text h2, .white-text h3, .white-text p { color: white !important; }
    
    /* ซ่อน Header และ Footer ของ Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. ตรวจสถานะ Session และ Mode (Login / Register) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'login'  # เริ่มต้นที่หน้าเข้าสู่ระบบ

# 🌟 เรียกใช้งาน Cookie Banner (ให้ลอยอยู่ด้านล่างสุดของจอ)
show_cookie_banner()


# ฟังก์ชันสลับหน้า

def toggle_mode():
    st.session_state['auth_mode'] = 'register' if st.session_state['auth_mode'] == 'login' else 'login'


# --- 4. โครงสร้าง Layout (จัดตรงกลางหน้าจอ) ---
# ใช้กล่องเปล่าดันซ้ายขวาให้ฟอร์มอยู่ตรงกลาง
spacer_left, main_col1, main_col2, spacer_right = st.columns([1, 3, 5, 1])

# ==========================================
# ฝั่งซ้าย: สีน้ำเงิน (Welcome Area)
# ==========================================
with main_col1:
    st.markdown("<div class='white-text' style='display: flex; flex-direction: column; align-items: center;'>",
                unsafe_allow_html=True)

    # 🌟 เปลี่ยนจรวดเป็นโลโก้ shield.png
    st.image("shield.png", width=90)
    st.markdown("<h1 style='margin-top: 10px; margin-bottom: 5px;'>LungGuard AI</h1>",
                unsafe_allow_html=True)

    if st.session_state['auth_mode'] == 'login':
        st.markdown("<h3 style='margin-top: 20px;'>Welcome</h3>",
                    unsafe_allow_html=True)
        st.write(
            "เข้าสู่ระบบเพื่อใช้งานระบบวิเคราะห์และพยากรณ์ความเสี่ยงโรคมะเร็งปอดด้วย AI")
        st.write("---")
        st.write("ยังไม่มีบัญชีผู้ใช้งานใช่หรือไม่?")
        st.button("สร้างบัญชีใหม่ (Sign Up)",
                  on_click=toggle_mode, key="btn_go_reg")
    else:
        st.markdown("<h3 style='margin-top: 20px;'>Join Us</h3>",
                    unsafe_allow_html=True)
        st.write("ลงทะเบียนเพื่อเริ่มต้นใช้งานระบบคัดกรองความเสี่ยงของคุณ")
        st.write("---")
        st.write("มีบัญชีผู้ใช้งานอยู่แล้ว?")
        st.button("เข้าสู่ระบบ (Sign In)",
                  on_click=toggle_mode, key="btn_go_login")

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# ฝั่งขวา: สีขาว (Form Area)
# ==========================================
with main_col2:

    # ---------------- LOGIN MODE ----------------
    if st.session_state['auth_mode'] == 'login':
        st.markdown("<h2>Sign in to your account</h2>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            user = st.text_input("รหัสบัตรประชาชน (Username)",
                                 placeholder="Enter your ID card number")
            pw = st.text_input(
                "รหัสผ่าน (Password)", type="password", placeholder="Enter your password")

            # เว้นระยะก่อนปุ่มนิดหน่อย
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In")

            if submitted:
                if user and pw:
                    try:
                        with st.spinner('กำลังตรวจสอบข้อมูล...'):
                            res = requests.post(
                                f"https://lung-cancer-api-c1e5.onrender.com/user/login?username={user}&password={pw}")
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state['logged_in'] = True
                                st.session_state['full_name'] = data['full_name']
                                st.session_state['id_card'] = data['id_card']
                                st.success(
                                    "เข้าสู่ระบบสำเร็จ! กำลังพาท่านเข้าสู่หน้าหลัก...")

                                # ให้หน่วงเวลา 1 วินาที เพื่อให้ผู้ใช้เห็นข้อความสีเขียวก่อนเปลี่ยนหน้า
                                import time
                                time.sleep(1)
                                st.switch_page("pages/home.py")
                            else:
                                st.error(
                                    "❌ รหัสบัตรประชาชน หรือ รหัสผ่านไม่ถูกต้อง")

                    # ดักจับเฉพาะ Error จากการยิง API
                    except requests.exceptions.RequestException:
                        st.error(
                            "❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบว่า Backend (main.py) รันอยู่หรือไม่")
                else:
                    st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

    # ---------------- REGISTER MODE ----------------
    else:
        st.markdown("<h2>Create your account</h2>", unsafe_allow_html=True)
        st.write("กรุณากรอกข้อมูลส่วนตัวเพื่อลงทะเบียน")

        with st.form("register_form"):
            # แบ่งเป็น 2 คอลัมน์ย่อยเพื่อให้ดูไม่ยาวเกินไป
            r_col1, r_col2 = st.columns(2)

            with r_col1:
                pta_idcard = st.text_input("รหัสบัตรประชาชน *", max_chars=13)
                pta_firstname = st.text_input("ชื่อจริง *")
                pta_email = st.text_input("อีเมล")
                pta_address_number = st.text_input("บ้านเลขที่/หมู่บ้าน")
                province_code = st.text_input("จังหวัด")
                district_code = st.text_input("ตำบล/แขวง")
                password = st.text_input("ตั้งรหัสผ่าน *", type="password")

            with r_col2:
                ptd_id = st.text_input("รหัสอ้างอิง PTD (ถ้ามี)")
                pta_lastname = st.text_input("นามสกุล *")
                pta_phone = st.text_input("เบอร์โทรศัพท์")
                amphur_code = st.text_input("อำเภอ/เขต")
                zipcode = st.text_input("รหัสไปรษณีย์")
                pta_img = st.text_input("รูปโปรไฟล์ (URL หรือ ว่างไว้ก่อน)")
                password_confirm = st.text_input(
                    "ยืนยันรหัสผ่าน *", type="password")

            st.markdown(
                "<small style='color: gray;'>* โดยการสมัครสมาชิก คุณยอมรับเงื่อนไขและข้อตกลงการใช้งาน (Terms & Conditions)</small>", unsafe_allow_html=True)

            reg_submitted = st.form_submit_button("Sign Up")

            if reg_submitted:
                if not pta_idcard or not pta_firstname or not pta_lastname or not password:
                    st.warning(
                        "กรุณากรอกข้อมูลในช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
                elif password != password_confirm:
                    st.error("❌ รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
                else:
                    # จัดเตรียมข้อมูลส่งให้ API
                    payload = {
                        "pta_idcard": pta_idcard,
                        "pta_firstname": pta_firstname,
                        "pta_lastname": pta_lastname,
                        "pta_address_number": pta_address_number or "-",
                        "pta_email": pta_email or "-",
                        "pta_phone": pta_phone or "-",
                        "pta_img": pta_img or None,
                        "province_code": province_code or "-",
                        "amphur_code": amphur_code or "-",
                        "district_code": district_code or "-",
                        "zipcode": zipcode or "-",
                        "ptd_id": ptd_id or "-",
                        "password": password
                    }

                    try:
                        with st.spinner('กำลังสร้างบัญชีผู้ใช้งาน...'):
                            res = requests.post(
                                "https://lung-cancer-api-c1e5.onrender.com/user/users", json=payload)

                            if res.status_code == 200:
                                st.success(
                                    "🎉 ลงทะเบียนสำเร็จ! กรุณากดปุ่ม 'เข้าสู่ระบบ (Sign In)' ด้านซ้ายมือ")
                            elif res.status_code == 400:
                                st.error(f"❌ {res.json().get('detail')}")
                            else:
                                st.error(
                                    "❌ เกิดข้อผิดพลาดจากระบบ กรุณาลองใหม่อีกครั้ง")
                    except Exception as e:
                        st.error(f"❌ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้: {e}")
