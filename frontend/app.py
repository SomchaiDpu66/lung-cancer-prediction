import streamlit as st
import requests
import os
from menu import show_sidebar, show_cookie_banner

API_URL = "https://lung-cancer-prediction-production.up.railway.app"

# --- 1. ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LungGuard AI - Login", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="collapsed")

# --- 2. Custom CSS (เพิ่ม Responsive Design และปรับสไตล์ปุ่มลืมรหัสผ่าน) ---
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

    /* ซ่อนเส้นขอบฟอร์มเพื่อให้หน้าจอดูกลืนกัน */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }

    .stTextInput>div>div>input { border-radius: 12px; border: 1.5px solid #E2E8F0; padding: 12px 15px; transition: border-color 0.3s ease; }
    .stTextInput>div>div>input:focus { border-color: #3B82F6; box-shadow: 0 0 0 1px #3B82F6; }
    
    /* สไตล์ปุ่มหลัก (Sign In, Sign Up) */
    .stButton>button:not([kind="tertiary"]):not([data-testid="baseButton-tertiary"]) {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        color: white; border-radius: 30px; padding: 12px 30px; font-weight: 600;
        width: 100%; transition: all 0.3s ease;
    }
    .stButton>button:not([kind="tertiary"]):not([data-testid="baseButton-tertiary"]):hover { 
        transform: translateY(-3px); box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4); 
    }

    /* สไตล์ปุ่มข้อความ ลืมรหัสผ่าน (Tertiary Button) */
    .stButton>button[kind="tertiary"], .stButton>button[data-testid="baseButton-tertiary"] {
        background: transparent !important;
        color: #64748B !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        width: auto !important;
        margin-top: -10px; /* ดึงข้อความให้ชิดกับปุ่ม Sign In */
    }
    .stButton>button[kind="tertiary"]:hover, .stButton>button[data-testid="baseButton-tertiary"]:hover {
        color: #3B82F6 !important;
        text-decoration: underline !important;
    }

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


# ปรับฟังก์ชันให้รองรับ 3 โหมด (login, register, forgot_password)
def toggle_mode(mode='login'):
    st.session_state['auth_mode'] = mode


# --- 4. โครงสร้าง Layout ---
spacer_left, main_col1, main_col2, spacer_right = st.columns([1, 3, 5, 1])

# ==========================================
# ฝั่งซ้าย: Welcome Area (อัปเดตรองรับ 3 โหมด)
# ==========================================
with main_col1:
    st.markdown("<div class='white-text' style='display: flex; flex-direction: column; align-items: center;'>",
                unsafe_allow_html=True)
    st.image("shield.png", width=90)
    st.markdown("<h1 style='margin-top: 10px; margin-bottom: 5px;'>LungGuard AI</h1>",
                unsafe_allow_html=True)

    # ---------------- LOGIN MODE ----------------
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
                # [ โค้ดตรวจสอบ User / Pass ของคุณ Kean คงเดิมทั้งหมด ไม่ต้องแก้ ]
                pass  # สมมติว่าเป็นโค้ดเดิม

        # === ✨ นำโค้ด 1 บรรทัดนี้ มาวางอยู่นอกสุดของ st.form (เยื้องให้ตรงกับ with st.form) ===
        st.button("ลืมรหัสผ่าน? (Reset Password)", type="tertiary",
                  on_click=toggle_mode, args=('forgot_password',), key="btn_forgot_text")

    # --- โหมด 2: หน้า Register ---
    elif st.session_state['auth_mode'] == 'register':
        st.markdown("<h3 style='margin-top: 20px;'>Join Us</h3>",
                    unsafe_allow_html=True)
        st.write("ลงทะเบียนเพื่อเริ่มต้นใช้งานระบบคัดกรองความเสี่ยงของคุณ")
        st.write("---")
        st.write("มีบัญชีผู้ใช้งานอยู่แล้ว?")
        st.button("เข้าสู่ระบบ (Sign In)",
                  on_click=toggle_mode, args=('login',), key="btn_go_login")

    # --- โหมด 3: หน้า Forgot Password ---
    elif st.session_state['auth_mode'] == 'forgot_password':
        st.markdown("<h3 style='margin-top: 20px;'>Recover Account</h3>",
                    unsafe_allow_html=True)
        st.write("รีเซ็ตรหัสผ่านของคุณเพื่อกลับเข้าสู่ระบบ")
        st.write("---")
        st.write("นึกรหัสผ่านออกแล้ว?")
        st.button("กลับไปเข้าสู่ระบบ (Sign In)",
                  on_click=toggle_mode, args=('login',), key="btn_back_login")

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

    # ---------------- REGISTER MODE ----------------
    # เปลี่ยนจาก else เป็น elif เพื่อให้รองรับ 3 โหมด
    elif st.session_state['auth_mode'] == 'register':
        st.markdown("<h2>Create your account</h2>", unsafe_allow_html=True)
        st.write("กรุณากรอกข้อมูลส่วนตัวเพื่อลงทะเบียน (ระยะทดสอบระบบ)")

        with st.form("register_form"):
            # 1. Username (เต็มบรรทัด)
            pta_username = st.text_input(
                "ชื่อผู้ใช้งาน (Username) *", placeholder="ตัวอักษรหรือตัวเลข")

            # 2. จัดกลุ่ม ชื่อ-นามสกุล ให้อยู่แถวเดียวกัน (PC จะอยู่ซ้าย-ขวา / Mobile จะเรียงบน-ล่าง)
            name_col1, name_col2 = st.columns(2)
            with name_col1:
                pta_firstname = st.text_input("ชื่อจริง *")
            with name_col2:
                pta_lastname = st.text_input("นามสกุล *")

            # 3. จัดกลุ่ม รหัสผ่าน ให้อยู่แถวเดียวกัน
            pw_col1, pw_col2 = st.columns(2)
            with pw_col1:
                password = st.text_input("ตั้งรหัสผ่าน *", type="password")
            with pw_col2:
                password_confirm = st.text_input(
                    "ยืนยันรหัสผ่าน *", type="password")

            # 4. อีเมล (ช่องสุดท้าย พร้อมบังคับตรวจสอบ)
            pta_email = st.text_input(
                "อีเมล *", placeholder="example@domain.com")

            st.markdown(
                "<small style='color: gray;'>* โดยการสมัครสมาชิก คุณยอมรับเงื่อนไขการใช้งาน</small>", unsafe_allow_html=True)
            reg_submitted = st.form_submit_button("Sign Up")

            if reg_submitted:
                if not pta_username or not pta_firstname or not pta_lastname or not password or not pta_email:
                    st.warning(
                        "⚠️ กรุณากรอกข้อมูลในช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
                elif "@" not in pta_email or "." not in pta_email.split("@")[-1]:
                    st.error(
                        "❌ กรุณากรอกรูปแบบอีเมลให้ถูกต้อง (ต้องมี @ และจุดทศนิยม เช่น user@mail.com)")
                elif password != password_confirm:
                    st.error("❌ รหัสผ่านไม่ตรงกัน")
                else:
                    payload = {
                        "pta_username": pta_username,
                        "pta_firstname": pta_firstname,
                        "pta_lastname": pta_lastname,
                        "pta_email": pta_email,
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
                                    "🎉 ลงทะเบียนสำเร็จ! กำลังพาท่านไปยังหน้าเข้าสู่ระบบ...")
                                import time
                                time.sleep(1.5)
                                st.session_state['auth_mode'] = 'login'
                                st.rerun()
                            else:
                                st.error(
                                    f"❌ {res.json().get('detail', 'เกิดข้อผิดพลาดจากระบบ')}")
                    except Exception as e:
                        st.error(f"❌ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้: {e}")

    # ---------------- FORGOT PASSWORD MODE ----------------
    # เพิ่มบล็อกนี้เข้าไปเป็นโหมดที่ 3
    elif st.session_state['auth_mode'] == 'forgot_password':
        st.markdown("<h2>Reset Password</h2>", unsafe_allow_html=True)
        st.write("กรุณากรอกข้อมูลเพื่อยืนยันตัวตนและตั้งรหัสผ่านใหม่")

        with st.form("reset_password_form"):
            r_user = st.text_input("ชื่อผู้ใช้งาน (Username) *")
            r_email = st.text_input(
                "อีเมลที่ใช้ลงทะเบียน *", placeholder="example@domain.com")

            pw_col1, pw_col2 = st.columns(2)
            with pw_col1:
                r_new_pw = st.text_input("รหัสผ่านใหม่ *", type="password")
            with pw_col2:
                r_new_pw_confirm = st.text_input(
                    "ยืนยันรหัสผ่านใหม่ *", type="password")

            st.markdown("<br>", unsafe_allow_html=True)
            reset_submitted = st.form_submit_button("ยืนยันการเปลี่ยนรหัสผ่าน")

            if reset_submitted:
                if not r_user or not r_email or not r_new_pw:
                    st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
                elif r_new_pw != r_new_pw_confirm:
                    st.error("❌ รหัสผ่านใหม่ไม่ตรงกัน")
                else:
                    payload = {
                        "pta_username": r_user,
                        "pta_email": r_email,
                        "new_password": r_new_pw
                    }
                    try:
                        with st.spinner('กำลังตรวจสอบข้อมูล...'):
                            # ยิง API ไปที่ Endpoint ใหม่สำหรับเปลี่ยนรหัสผ่าน
                            res = requests.put(
                                f"{API_URL}/user/reset-password", json=payload)

                            if res.status_code == 200:
                                st.success(
                                    "✅ เปลี่ยนรหัสผ่านสำเร็จ! กำลังพาท่านกลับไปหน้าเข้าสู่ระบบ...")
                                import time
                                time.sleep(2)
                                st.session_state['auth_mode'] = 'login'
                                st.rerun()
                            else:
                                st.error(
                                    f"❌ {res.json().get('detail', 'เกิดข้อผิดพลาด')}")
                    except Exception as e:
                        st.error("❌ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้")
