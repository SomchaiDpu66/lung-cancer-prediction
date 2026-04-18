import streamlit as st
import requests
import os
from menu import show_sidebar, show_cookie_banner

# --- 1. ตั้งค่า Page ---
st.set_page_config(page_title="LungGuard AI - Profile",
                   page_icon="🛡️", layout="wide")

# --- 2. 🎨 Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
    .stTextInput>div>div>input { border-radius: 10px; border: 1px solid #E2E8F0; transition: all 0.3s ease; }
    .stButton>button { border-radius: 12px; font-weight: 500; }
    .stButton>button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6); color: white; border-radius: 12px; font-weight: 600; border: none;
    }
    div[data-testid="stContainer"] {
        border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #F1F5F9; padding: 20px; background-color: white;
    }
    h1, h2, h3, h4 { color: #1E3A8A; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 3. ตรวจสอบ Login ---
if 'logged_in' not in st.session_state or not st.session_state.get('logged_in'):
    st.warning("⚠️ กรุณาเข้าสู่ระบบก่อน")
    st.switch_page("app.py")
    st.stop()

show_sidebar()
show_cookie_banner()
API_URL = os.environ.get(
    "BACKEND_URL", "https://lung-cancer-prediction-production.up.railway.app")
USER_ID = st.session_state.get('username')


# --- 4. หัวข้อหลัก ---
col_logo, col_title = st.columns([0.05, 0.95])
with col_logo:
    st.image("shield.png", width=55)
with col_title:
    st.markdown("<h2 style='color: #1E3A8A; margin-top: -5px; font-weight: 800;'>LungGuard AI</h2>",
                unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; margin-top: -15px;'>ตั้งค่าและจัดการข้อมูลโปรไฟล์ส่วนตัว</p>",
                unsafe_allow_html=True)

st.write("")

# --- 5. ดึงข้อมูลผู้ใช้ปัจจุบัน ---


@st.cache_data(ttl=5)  # ลด Cache ลงเพื่อให้เห็นรูปใหม่ทันทีที่อัปเดต
def fetch_user_data(username):
    try:
        res = requests.get(f"{API_URL}/user/user/{username}", timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None


user_data = fetch_user_data(USER_ID)

if user_data:
    st.markdown("### 📝 ข้อมูลส่วนตัวของคุณ")
    with st.container(border=True):

        # 🌟 โชว์รูปโปรไฟล์ด้านบนสุด (ทำเป็นวงกลมสวยๆ)
        st.markdown(
            "<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        current_img = user_data.get('pta_img', '')
        if current_img and current_img != '-':
            # เช็คว่าเป็น URL เก่า หรือรูปใหม่ที่อัปโหลดเข้าเซิร์ฟเวอร์
            img_url = current_img if current_img.startswith(
                "http") else f"{API_URL}/uploads/{current_img}"
            st.markdown(f"<img src='{img_url}' style='width: 130px; height: 130px; border-radius: 50%; object-fit: cover; margin-bottom: 20px; border: 3px solid #3B82F6; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        else:
            # รูปร่างจำลองหากยังไม่มีรูปโปรไฟล์
            st.markdown("<div style='width: 130px; height: 130px; border-radius: 50%; background-color: #F1F5F9; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; border: 3px dashed #CBD5E1;'><span style='color: #94A3B8; font-size: 40px;'>👤</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 🌟 ฟอร์มข้อมูลส่วนตัว
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.text_input("รหัสบัตรประชาชน (ไม่สามารถแก้ไขได้)",
                              value=user_data.get('pta_idcard', ''), disabled=True)
                new_fname = st.text_input(
                    "ชื่อจริง *", value=user_data.get('pta_firstname', ''))
                new_email = st.text_input("อีเมล", value=user_data.get(
                    'pta_email', '') if user_data.get('pta_email') != '-' else '')
                new_address = st.text_input("บ้านเลขที่/หมู่บ้าน", value=user_data.get(
                    'pta_address_number', '') if user_data.get('pta_address_number') != '-' else '')
                new_prov = st.text_input("จังหวัด", value=user_data.get(
                    'province_code', '') if user_data.get('province_code') != '-' else '')
                new_dist = st.text_input("ตำบล/แขวง", value=user_data.get(
                    'district_code', '') if user_data.get('district_code') != '-' else '')
                new_pw = st.text_input(
                    "เปลี่ยนรหัสผ่านใหม่ (หากไม่ต้องการเปลี่ยนให้เว้นว่างไว้)", type="password")

            with col2:
                st.text_input("รหัสอ้างอิง PTD", value=user_data.get(
                    'ptd_id', '') if user_data.get('ptd_id') != '-' else '', disabled=True)
                new_lname = st.text_input(
                    "นามสกุล *", value=user_data.get('pta_lastname', ''))
                new_phone = st.text_input("เบอร์โทรศัพท์", value=user_data.get(
                    'pta_phone', '') if user_data.get('pta_phone') != '-' else '')
                new_amphur = st.text_input("อำเภอ/เขต", value=user_data.get(
                    'amphur_code', '') if user_data.get('amphur_code') != '-' else '')
                new_zip = st.text_input("รหัสไปรษณีย์", value=user_data.get(
                    'zipcode', '') if user_data.get('zipcode') != '-' else '')

                # 🌟 เปลี่ยนช่องใส่ URL เป็นปุ่มอัปโหลดไฟล์!
                uploaded_file = st.file_uploader(
                    "เปลี่ยนรูปโปรไฟล์ (อัปโหลดไฟล์ JPG, PNG)", type=["jpg", "jpeg", "png"])

                confirm_pw = st.text_input(
                    "ยืนยันรหัสผ่านใหม่", type="password")

            st.divider()
            submitted = st.form_submit_button(
                "💾 บันทึกการเปลี่ยนแปลง", type="primary")

            if submitted:
                if not new_fname or not new_lname:
                    st.warning("⚠️ กรุณากรอกชื่อและนามสกุลให้ครบถ้วน")
                elif new_pw and new_pw != confirm_pw:
                    st.error("❌ รหัสผ่านใหม่และการยืนยันรหัสผ่านไม่ตรงกัน")
                else:
                    final_img_filename = current_img

                    # 🌟 1. ถ้ามีการเลือกไฟล์รูปภาพ ให้ยิง API ไปอัปโหลดก่อน
                    if uploaded_file is not None:
                        with st.spinner("🖼️ กำลังอัปโหลดรูปภาพ..."):
                            files = {
                                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            upload_res = requests.post(
                                f"{API_URL}/user/upload_image", files=files)
                            if upload_res.status_code == 200:
                                final_img_filename = upload_res.json().get("filename")
                            else:
                                st.error("❌ เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ")
                                st.stop()

                    # 🌟 2. อัปเดตข้อมูลผู้ใช้งานทั้งหมด
                    update_payload = {
                        "pta_firstname": new_fname, "pta_lastname": new_lname,
                        "pta_address_number": new_address or "-", "pta_email": new_email or "-",
                        "pta_phone": new_phone or "-", "pta_img": final_img_filename or "-",
                        "province_code": new_prov or "-", "amphur_code": new_amphur or "-",
                        "district_code": new_dist or "-", "zipcode": new_zip or "-"
                    }
                    if new_pw:
                        update_payload["password"] = new_pw

                    try:
                        with st.spinner("กำลังอัปเดตข้อมูล..."):
                            update_res = requests.put(
                                f"{API_URL}/user/user/{USER_ID}", json=update_payload, timeout=5)
                            if update_res.status_code == 200:
                                st.success(
                                    "✅ อัปเดตข้อมูลส่วนตัวและรูปภาพสำเร็จ!")
                                st.session_state['full_name'] = f"{new_fname} {new_lname}"
                                fetch_user_data.clear()  # ล้าง Cache ให้โหลดรูปใหม่

                                # รีเฟรชหน้าเพื่อให้รูปใหม่ปรากฏทันที
                                import time
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(
                                    f"❌ เกิดข้อผิดพลาด: {update_res.json().get('detail')}")
                    except Exception as e:
                        st.error(f"❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้: {e}")
else:
    st.error("⚠️ ไม่สามารถโหลดข้อมูลผู้ใช้งานจากฐานข้อมูลได้")
