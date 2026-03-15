import streamlit as st
import os
import requests

# 🌟 ฟังก์ชันดึงรูปโปรไฟล์ (ตั้ง Cache ไว้ 10 วินาที เพื่อไม่ให้แอปช้าตอนเปลี่ยนหน้า)


@st.cache_data(ttl=10)
def get_profile_icon(id_card):
    try:
        API_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8001")
        res = requests.get(f"{API_URL}/user/user/{id_card}", timeout=3)
        if res.status_code == 200:
            data = res.json()
            img = data.get('pta_img')
            if img and img != '-':
                # เช็คว่าเป็นลิงก์เว็บเก่า หรือไฟล์อัปโหลดใหม่
                if str(img).startswith('http'):
                    return img
                else:
                    return f"{API_URL}/uploads/{img}"
    except:
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

        # 🌟 จัดการรูปไอคอนผู้ใช้งาน
        user_id = st.session_state.get('id_card')
        # ค่าเริ่มต้นถ้าไม่มีรูป
        img_html = "<span style='font-size: 18px; margin-right: 5px;'>👤</span>"

        if user_id:
            img_url = get_profile_icon(user_id)
            if img_url:
                # ถ้ามีรูป ให้สร้าง Tag รูปภาพแบบวงกลม (Avatar)
                img_html = f"<img src='{img_url}' style='width: 26px; height: 26px; border-radius: 50%; object-fit: cover; border: 1.5px solid #3B82F6; margin-right: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>"

        # แสดงรูปภาพคู่กับชื่อผู้ใช้งาน (ใช้ Flexbox เพื่อให้กึ่งกลางพอดีเป๊ะ)
        st.markdown(f"""
            <div style='color: #64748B; font-size: 14px; margin-top: -10px; margin-bottom: 10px; display: flex; align-items: center;'>
                {img_html} 
                <span>ผู้ใช้งาน: <b>{st.session_state.get('full_name', 'แขกผู้เยือน')}</b></span>
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
            st.session_state['api_result'] = None
            st.session_state['current_payload'] = None
            st.session_state['age_input'] = 45
            st.session_state['gender_input'] = "ชาย"

            checkbox_keys = ['chk_smoking', 'chk_alcohol', 'chk_peer', 'chk_chronic', 'chk_fatigue', 'chk_allergy',
                             'chk_swallowing', 'chk_yellow', 'chk_anxiety', 'chk_shortness', 'chk_coughing', 'chk_wheezing', 'chk_chest']
            for key in checkbox_keys:
                st.session_state[key] = False
            st.rerun()

        st.write("")

        if st.button("🚪 ออกจากระบบ", type="primary", use_container_width=True):
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
