import streamlit as st
import os
import requests

# 🌟 ฟังก์ชันดึงรูปโปรไฟล์ (ตั้ง Cache ไว้ 10 วินาที เพื่อไม่ให้แอปช้าตอนเปลี่ยนหน้า)


@st.cache_data(ttl=10)
def get_profile_icon(username):  # เปลี่ยนชื่อ parameter ให้สื่อความหมาย
    if not username:
        return None

    try:
        # ดึง URL จาก Environment หรือใช้ค่า Default ของ Railway
        API_URL = os.environ.get(
            "BACKEND_URL", "https://lung-cancer-prediction-production.up.railway.app")

        # เรียกไปยัง Endpoint ใหม่ที่เราแก้ใน main.py (/user/user/{username})
        res = requests.get(f"{API_URL}/user/user/{username}", timeout=5)

        if res.status_code == 200:
            data = res.json()
            img = data.get('pta_img')

            # ตรวจสอบว่ามีรูปภาพหรือไม่
            if img and img != '-':
                # กรณีที่ 1: เป็น URL เต็มรูปแบบ (เช่นจาก Google หรือเว็บอื่น)
                if str(img).startswith('http'):
                    return img
                # กรณีที่ 2: เป็นชื่อไฟล์ที่อัปโหลดไว้ในเซิร์ฟเวอร์
                else:
                    return f"{API_URL}/uploads/{img}"
    except Exception as e:
        # พิมพ์ Error ลงใน Console เพื่อการตรวจสอบ (ไม่แสดงบนหน้าเว็บ)
        print(f"Debug: Profile icon load failed for {username} - {e}")
        pass

    return None


def show_sidebar():
    with st.sidebar:
        # ==========================================
        # 🌟 1. ส่วน Header โลโก้และชื่อระบบ (Modern UI)
        # ==========================================
        col1, col2 = st.columns([1.2, 3.8])
        with col1:
            st.image("shield.png", use_container_width=True)
        with col2:
            st.markdown(
                "<h3 style='margin-top: 5px; color: #1E3A8A; font-weight: 600;'>LungGuard AI</h3>", unsafe_allow_html=True)

        # ==========================================
        # 🌟 จัดการรูปไอคอนผู้ใช้งาน (Visual Identity & UX)
        # ==========================================
        # แก้ไขจุดที่ 1: เปลี่ยนจาก id_card เป็น username เพื่อดึงข้อมูลให้ถูกต้อง
        current_user = st.session_state.get('username')

        # ค่าเริ่มต้นถ้าไม่มีรูป (Fallback Icon)
        img_html = "<span style='font-size: 22px; margin-right: 10px;'>👤</span>"

        if current_user:
            # เรียกใช้ฟังก์ชันที่ปรับปรุงใหม่ (ใช้ username ในการดึงรูป)
            img_url = get_profile_icon(current_user)
            if img_url:
                # ถ้ามีรูป ให้สร้าง Tag รูปภาพแบบวงกลมพร้อมเงาและขอบ (Modern Avatar)
                img_html = f"""
                    <img src='{img_url}' 
                    style='width: 35px; height: 35px; border-radius: 50%; object-fit: cover; 
                    border: 2px solid #3B82F6; margin-right: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                """

        # แสดงรูปภาพคู่กับชื่อผู้ใช้งาน (เพิ่มความสวยงามและชื่อล็อกอิน)
        st.markdown(f"""
            <div style='background-color: #F8FAFC; padding: 10px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 15px; display: flex; align-items: center;'>
                {img_html} 
                <div style='display: flex; flex-direction: column;'>
                    <span style='color: #64748B; font-size: 11px; line-height: 1;'>ลงชื่อเข้าใช้ในชื่อ</span>
                    <span style='color: #1E293B; font-size: 14px; font-weight: 600;'>{st.session_state.get('full_name', 'แขกผู้เยือน')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ==========================================
        # 📌 2. การนำทาง (Navigation)
        # ==========================================
        st.markdown(
            "<p style='font-weight: 500; color: #1E3A8A; margin-bottom: 10px;'>📌 การนำทาง</p>", unsafe_allow_html=True)

        st.page_link("pages/home.py", label="หน้าหลัก / แดชบอร์ด", icon="🏠")
        st.page_link("pages/profile.py", label="โปรไฟล์ส่วนตัว", icon="👤")
        st.page_link("pages/screening_centers.py",
                     label="ศูนย์คัดกรอง", icon="🔍")
        st.page_link("pages/user_history.py",
                     label="ประวัติการใช้งาน", icon="📅")

        st.divider()

        # ==========================================
        # ⚙️ 3. การจัดการระบบ (Reset / Logout)
        # ==========================================
        if st.button("🔄 ล้างค่าหน้าจอ (เริ่มใหม่)", use_container_width=True):
            # เคลียร์ค่าเฉพาะจุด ไม่ให้กระทบ Login Session
            reset_keys = ['api_result', 'current_payload',
                          'age_input', 'gender_input']
            for key in reset_keys:
                if key in st.session_state:
                    st.session_state[key] = None

            # เคลียร์ Checkbox
            checkbox_keys = ['chk_smoking', 'chk_alcohol', 'chk_peer', 'chk_chronic', 'chk_fatigue', 'chk_allergy',
                             'chk_swallowing', 'chk_yellow', 'chk_anxiety', 'chk_shortness', 'chk_coughing', 'chk_wheezing', 'chk_chest']
            for key in checkbox_keys:
                st.session_state[key] = False
            st.rerun()

        st.write("")

        if st.button("🚪 ออกจากระบบ", type="primary", use_container_width=True):
            # ใช้การเคลียร์เฉพาะข้อมูล User แต่คงสภาพโครงสร้างไว้
            st.session_state.clear()
            st.switch_page("app.py")


def show_cookie_banner():
    # 🌟 1. ตรวจสถานะว่าเคยกดยอมรับคุกกี้ไปหรือยัง
    if 'cookies_accepted' not in st.session_state:
        st.session_state['cookies_accepted'] = False

    # 🌟 2. ถ้ายังไม่ยอมรับ ให้แสดงแบนเนอร์ลอยด้านล่าง
    if not st.session_state['cookies_accepted']:
        # ใช้ CSS CSS :has() เพื่อสั่งให้กล่องนี้ลอยติดขอบล่างของหน้าจอ
        st.markdown("""
            <style>
                div[data-testid="stVerticalBlock"]:has(.cookie-hook) {
                    position: fixed;
                    bottom: 25px;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: white;
                    z-index: 99999;
                    padding: 20px 30px;
                    border-radius: 12px;
                    box-shadow: 0px 10px 40px rgba(0,0,0,0.15);
                    width: 90%;
                    max-width: 1000px;
                    border-left: 6px solid #3B82F6;
                    border-top: 1px solid #F1F5F9;
                    border-right: 1px solid #F1F5F9;
                    border-bottom: 1px solid #F1F5F9;
                }
            </style>
        """, unsafe_allow_html=True)

        with st.container():
            # หมุดล่องหนสำหรับให้ CSS ด้านบนหาตัวกล่องเจอ
            st.markdown('<div class="cookie-hook"></div>',
                        unsafe_allow_html=True)

            # แบ่งเลย์เอาต์ ข้อความ(ซ้าย) ปุ่ม(ขวา)
            c_text, c_btn1, c_btn2 = st.columns([4, 1.2, 1.2])

            with c_text:
                st.markdown("""
                    <p style='margin: 0; font-size: 14px; color: #1E293B; line-height: 1.6;'>
                        <b>เว็บไซต์นี้ใช้คุกกี้ (ข้อมูลสำหรับการค้นคว้าวิจัย)</b><br>
                        เราใช้คุกกี้เพื่อเพิ่มประสิทธิภาพ และประสบการณ์ที่ดีในการใช้งานเว็บไซต์ คุณสามารถเลือกตั้งค่าความยินยอมการใช้คุกกี้ได้ โดยคลิก "การตั้งค่าคุกกี้"
                    </p>
                """, unsafe_allow_html=True)

            with c_btn1:
                # ดันปุ่มลงมาให้อยู่กึ่งกลางข้อความ
                st.markdown("<div style='margin-top: 10px;'></div>",
                            unsafe_allow_html=True)
                if st.button("การตั้งค่าคุกกี้", use_container_width=True):
                    st.info("ส่วนการตั้งค่าคุกกี้กำลังอยู่ในช่วงพัฒนา")

            with c_btn2:
                st.markdown("<div style='margin-top: 10px;'></div>",
                            unsafe_allow_html=True)
                # ปุ่มกดยอมรับสีน้ำเงินเข้ม
                if st.button("ยอมรับทั้งหมด", type="primary", use_container_width=True):
                    st.session_state['cookies_accepted'] = True
                    st.rerun()  # รีเฟรชหน้าเพื่อซ่อนแบนเนอร์
