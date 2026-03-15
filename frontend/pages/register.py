import streamlit as st
import requests
from datetime import datetime


def show_registration():
    st.title("📝 ลงทะเบียนผู้ใช้งานใหม่")

    with st.form("reg_form"):
        col1, col2 = st.columns(2)

        with col1:
            pta_idcard = st.text_input("รหัสบัตรประชาชน (จะใช้เป็น Username)")
            pta_firstname = st.text_input("ชื่อ")
            pta_lastname = st.text_input("นามสกุล")
            pta_email = st.text_input("อีเมล")
            pta_phone = st.text_input("เบอร์โทร")
            password = st.text_input("รหัสผ่าน", type="password")

        with col2:
            pta_address_number = st.text_input("ที่อยู่บ้านเลขที่")
            province_code = st.text_input("รหัสจังหวัด")
            amphur_code = st.text_input("รหัสอำเภอ")
            district_code = st.text_input("รหัสตำบล")
            zipcode = st.text_input("รหัสไปรษณีย์")
            ptd_id = st.text_input("รหัสอ้างอิงข้อมูล (PTD ID)")

        submitted = st.form_submit_button("ลงทะเบียน")

        if submitted:
            payload = {
                "pta_idcard": pta_idcard,
                "pta_firstname": pta_firstname,
                "pta_lastname": pta_lastname,
                "pta_address_number": pta_address_number,
                "pta_email": pta_email,
                "pta_phone": pta_phone,
                "province_code": province_code,
                "amphur_code": amphur_code,
                "district_code": district_code,
                "zipcode": zipcode,
                "ptd_id": ptd_id,
                "username": pta_idcard,  # ส่งไปก่อน เดี๋ยว Backend จัดการซ้ำให้
                "password": password
            }

            response = requests.post(
                "http://localhost:8000/register", json=payload)
            if response.status_code == 200:
                st.success("ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ")
            else:
                st.error(f"เกิดข้อผิดพลาด: {response.json().get('detail')}")


if __name__ == "__main__":
    show_registration()
