import streamlit as st
import requests
import os
from menu import show_sidebar, show_cookie_banner

API_URL = "https://lung-cancer-prediction-production.up.railway.app"

# --- 1. ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LungGuard AI - Login", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="collapsed")

# --- 2. Custom CSS (เพิ่ม Responsive Design สำหรับมือถือ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
    .stApp { background-color: #E2E8F0; }
    
    /* สไตล์สำหรับ Desktop */
    [data-testid="column"]:nth-of-type(1) {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        color: white; padding: 3rem 2rem; border-radius: 24px 0 0 24px;
        display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
        box-shadow: -5px 10px 25px rgba(0,0,0,0.1);
    }
    [data-testid="column"]:nth-of-type(2) {
        background: white; padding: 3rem; border-radius: 0 24px 24px 0;
        box-shadow: 10px 10px 25px rgba(0,0,0,0.1);
    }
    
    /* 📱 Responsive Design สำหรับหน้าจอมือถือ (Mobile/Tablet) */
    @media (max-width: 768px) {
        [data-testid="column"]:nth-of-type(1) {
            border-radius: 24px 24px 0 0 !important; /* เปลี่ยนให้ขอบมนด้านบนแทน */
            padding: 2rem 1.5rem !important;
        }
        [data-testid="column"]:nth-of-type(2) {
            border-radius: 0 0 24px 24px !important; /* เปลี่ยนให้ขอบมนด้านล่าง */
            padding: 2rem 1.5rem !important;
        }
    }

    .stTextInput>div>div>input { border-radius: 12px; border: 1.5px solid #E2E8F0; padding: 12px 15px; transition: border-color 0.3s ease; }
    .stTextInput>div>div>input:focus { border-color: #3B82F6; box-shadow: 0 0 0 1px #3B82F6; }
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        color: white; border-radius: 30px; padding: 12px 30px; font-weight: 600;
        width: 100%; transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4); }
    h1, h2, h3 { color: #1E3A8A; font-weight: 700; }
    .white-text, .white-text h1, .white-text h2, .white-text h3, .white-text p { color: white !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. ตรวจสถานะ Session ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'login'

show_cookie_banner()


def toggle_mode():
    st.session_state['auth_mode'] = 'register' if st.session_state['auth_mode'] == 'login' else 'login'


# --- 4. โครงสร้าง Layout ---
spacer_left, main_col1, main_col2, spacer_right = st.columns([1, 3, 5, 1])

# ==========================================
# ฝั่งซ้าย: Welcome Area (คงเดิม)
# ==========================================
with main_col1:
    st.markdown("<div class='white-text' style='display: flex; flex-direction: column; align-items: center;'>",
                unsafe_allow_html=True)
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
# ฝั่งขวา: Form Area
# ==========================================
with main_col2:
    # ---------------- LOGIN MODE (คงเดิม) ----------------
    if st.session_state['auth_mode'] == 'login':
        st.markdown("<h2>Sign in to your account</h2>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            user = st.text_input("ชื่อผู้ใช้งาน (Username)",
                                 placeholder="กรุณากรอกชื่อผู้ใช้งาน")
            pw = st.text_input(
                "รหัสผ่าน (Password)", type="password", placeholder="Enter your password")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In")

            if submitted:
                if user and pw:
                    try:
                        with st.spinner('กำลังตรวจสอบข้อมูล...'):
                            res = requests.post(
                                f"{API_URL}/user/login?username={user}&password={pw}")
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state['logged_in'] = True
                                st.session_state['full_name'] = data.get(
                                    'full_name')

                                current_user = data.get('username') or user
                                st.session_state['username'] = current_user

                                st.success(
                                    "เข้าสู่ระบบสำเร็จ! กำลังพาท่านเข้าสู่หน้าหลัก...")
                                import time
                                time.sleep(1)
                                st.switch_page("pages/home.py")
                            else:
                                st.error(
                                    "❌ ชื่อผู้ใช้งาน หรือ รหัสผ่านไม่ถูกต้อง")
                    except requests.exceptions.RequestException:
                        st.error("❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้")
                else:
                    st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

    # ---------------- REGISTER MODE (ปรับปรุงใหม่ ลดฟิลด์) ----------------
    else:
        st.markdown("<h2>Create your account</h2>", unsafe_allow_html=True)
        st.write("กรุณากรอกข้อมูลส่วนตัวเพื่อลงทะเบียน (ระยะทดสอบระบบ)")

        with st.form("register_form"):
            # แบ่งเป็น 2 คอลัมน์ให้ดูสวยงามและไม่ยาวเกินไป
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                pta_username = st.text_input(
                    "ชื่อผู้ใช้งาน (Username) *", placeholder="ตัวอักษรหรือตัวเลข")
                pta_firstname = st.text_input("ชื่อจริง *")
                password = st.text_input("ตั้งรหัสผ่าน *", type="password")

            with r_col2:
                pta_email = st.text_input("อีเมล")
                pta_lastname = st.text_input("นามสกุล *")
                password_confirm = st.text_input(
                    "ยืนยันรหัสผ่าน *", type="password")

            st.markdown(
                "<small style='color: gray;'>* โดยการสมัครสมาชิก คุณยอมรับเงื่อนไขการใช้งาน</small>", unsafe_allow_html=True)
            reg_submitted = st.form_submit_button("Sign Up")

            if reg_submitted:
                if not pta_username or not pta_firstname or not pta_lastname or not password:
                    st.warning(
                        "กรุณากรอกข้อมูลในช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
                elif password != password_confirm:
                    st.error("❌ รหัสผ่านไม่ตรงกัน")
                else:
                    # จัดเตรียม Payload ส่งให้ API (ฟิลด์ที่ตัดออกไป จะถูกส่งเป็นค่า Default)
                    payload = {
                        "pta_username": pta_username,
                        "pta_firstname": pta_firstname,
                        "pta_lastname": pta_lastname,
                        "pta_email": pta_email or "-",
                        "password": password,

                        # --- ข้อมูลที่ซ่อนไว้เพื่อลดภาระผู้ทดสอบ (ยัดค่า Default กัน API Error) ---
                        "pta_address_number": "-",
                        "pta_phone": "-",
                        "pta_img": None,
                        "province_code": "-",
                        "amphur_code": "-",
                        "district_code": "-",
                        "zipcode": "-",
                        "ptd_id": "-"
                    }

                    try:
                        with st.spinner('กำลังสร้างบัญชีผู้ใช้งาน...'):
                            res = requests.post(
                                f"{API_URL}/user/users", json=payload)
                            if res.status_code == 200:
                                st.success(
                                    "🎉 ลงทะเบียนสำเร็จ! กรุณากดปุ่ม 'เข้าสู่ระบบ (Sign In)' ด้านซ้ายมือ")
                            else:
                                st.error(
                                    f"❌ {res.json().get('detail', 'เกิดข้อผิดพลาดจากระบบ')}")
                    except Exception as e:
                        st.error(f"❌ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้: {e}")
