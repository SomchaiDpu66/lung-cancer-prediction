import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import math
from menu import show_sidebar, show_cookie_banner

# --- 1. ตั้งค่า Page ---
st.set_page_config(page_title="LungGuard AI - Dashboard",
                   page_icon="🛡️", layout="wide")

# --- 2. 🎨 Custom CSS สไตล์ Modern UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Prompt', sans-serif !important; }
    
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px; border: 1px solid #E2E8F0; transition: all 0.3s ease;
    }
    
    .stButton>button {
        border-radius: 12px; font-weight: 500; transition: all 0.3s ease; border: 1px solid #E2E8F0;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    
    .stButton>button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6); color: white; border-radius: 12px; font-weight: 600; border: none;
    }
    .stButton>button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px); box-shadow: 0 8px 15px rgba(59, 130, 246, 0.4);
    }
    
    div[data-testid="stContainer"] {
        border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #F1F5F9; padding: 10px; background-color: white;
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
show_cookie_banner()  # 👈 เพิ่มบรรทัดนี้ลงไป!

# --- 4. หัวข้อหลักแบบมีโลโก้ ---
col_logo, col_title = st.columns([0.05, 0.95])
with col_logo:
    st.image("shield.png", width=55)
with col_title:
    st.markdown("<h2 style='color: #1E3A8A; margin-top: -5px; font-weight: 800;'>LungGuard AI</h2>",
                unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; margin-top: -15px;'>ระบบวิเคราะห์ความเสี่ยงและแดชบอร์ดสุขภาพ</p>",
                unsafe_allow_html=True)

st.write("")

# --- 5. สร้าง Tabs ---
tab1, tab2 = st.tabs(["🎯 หน้าหลักและทำนายผล", "📊 แดชบอร์ดและรายงาน"])

with tab1:
    col_input, col_result = st.columns([1.8, 1.2])

    with col_input:
        with st.container(border=True):
            st.subheader("ข้อมูลพื้นฐานและอาการ")
            c1, c2 = st.columns(2)
            age = c1.number_input("อายุ (ปี)", 18, 100, 45, key="age_input")
            gender_label = c2.selectbox(
                "เพศ", ["ชาย", "หญิง"], key="gender_input")
            gender_val = 1 if gender_label == "ชาย" else 2

            st.divider()
            st.write("👉 **เลือกอาการที่ท่านพบ**")
            t1, t2, t3 = st.tabs(
                ["🚬 พฤติกรรม", "🤒 อาการทั่วไป", "🫁 ทางเดินหายใจ/ประวัติ"])

            with t1:
                smoking = st.checkbox("มีการสูบบุหรี่", key="chk_smoking")
                alcohol_consuming = st.checkbox(
                    "ดื่มแอลกอฮอล์เป็นประจำ", key="chk_alcohol")
                peer_pressure = st.checkbox(
                    "สัมผัสควันบุหรี่มือสอง", key="chk_peer")
                chronic_disease = st.checkbox(
                    "มีโรคประจำตัวเรื้อรัง", key="chk_chronic")

            with t2:
                fatigue = st.checkbox("ความอ่อนเพลีย", key="chk_fatigue")
                allergy = st.checkbox("โรคภูมิแพ้", key="chk_allergy")
                swallowing_difficulty = st.checkbox(
                    "การกลืนลำบาก", key="chk_swallowing")
                yellow_fingers = st.checkbox("นิ้วเหลือง", key="chk_yellow")
                anxiety = st.checkbox("ความวิตกกังวล", key="chk_anxiety")

            with t3:
                shortness_of_breath = st.checkbox(
                    "หายใจลำบาก/ถี่", key="chk_shortness")
                coughing = st.checkbox(
                    "มีอาการไอ/ระคายเคืองคอ", key="chk_coughing")
                wheezing = st.checkbox("หายใจมีเสียงวี้ด", key="chk_wheezing")
                chest_pain = st.checkbox("เจ็บหน้าอก", key="chk_chest")

    with col_result:
        st.subheader("🎯 ผลการคัดแยก")

        submitted = st.button("🔍 ประมวลผลทำนายผล",
                              type="primary", use_container_width=True)

        if submitted:
            payload = {
                # เปลี่ยน key เป็น pta_username และดึงค่า username จาก session
                "pta_username": st.session_state.get('username', 'guest_user'),
                "age": int(age),
                "gender": int(gender_val),
                "smoking": 2 if smoking else 1,
                "yellow_fingers": 2 if yellow_fingers else 1,
                "anxiety": 2 if anxiety else 1,
                "peer_pressure": 2 if peer_pressure else 1,
                "chronic_disease": 2 if chronic_disease else 1,
                "fatigue": 2 if fatigue else 1,
                "allergy": 2 if allergy else 1,
                "wheezing": 2 if wheezing else 1,
                "alcohol_consuming": 2 if alcohol_consuming else 1,
                "coughing": 2 if coughing else 1,
                "shortness_of_breath": 2 if shortness_of_breath else 1,
                "swallowing_difficulty": 2 if swallowing_difficulty else 1,
                "chest_pain": 2 if chest_pain else 1
            }
            st.session_state['current_payload'] = payload

            try:
                with st.spinner('AI กำลังประมวลผล...'):
                    res = requests.post(
                        "https://lung-cancer-prediction-production.up.railway.app/predict", json=payload, timeout=10)
                    if res.status_code == 200:
                        st.session_state['api_result'] = res.json()
                    else:
                        st.error(
                            f"❌ Error {res.status_code}: {res.json().get('message', 'Unknown Error')}")
            except Exception as e:
                st.error(f"❌ ไม่สามารถติดต่อ Server ได้: {e}")

        # ==========================================
        # 🌟 แสดงผลลัพธ์และระบบจำลอง (Simulation) 🌟
        # ==========================================
        if st.session_state.get('api_result'):
            data = st.session_state['api_result']
            color = "#E11D48" if data['prediction'] == "YES" else "#10B981"

            # 1. กล่องแสดงผลลัพธ์หลัก
            st.markdown(f"""
                <div style="padding: 20px; border-radius: 16px; border-top: 8px solid {color}; background-color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 15px; text-align: center;">
                    <h2 style="color: {color}; margin: 0;">{"⚠️ พบความเสี่ยงสูง" if data['prediction'] == "YES" else "✅ อยู่ในเกณฑ์ปกติ"}</h2>
                    <p style="font-size: 20px; margin: 10px 0;">ความน่าจะเป็น: <b>{data['probability']}%</b></p>
                </div>
            """, unsafe_allow_html=True)

            # 2. 🚨 กล่องคำแนะนำสำหรับผู้มีความเสี่ยงสูง
            if data['prediction'] == "YES":
                st.markdown("""
                    <div style='background-color: #FEE2E2; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: center;'>
                        <span style='color: #B91C1C; font-weight: 600;'>🚨 แนะนำให้ตรวจคัดกรองเพิ่มเติมที่สถานพยาบาลใกล้บ้าน</span>
                    </div>
                """, unsafe_allow_html=True)
                st.write("")
                if st.button("🏥 ค้นหาศูนย์คัดกรองใกล้ฉัน", type="primary", use_container_width=True):
                    st.switch_page("pages/screening_centers.py")

            # 3. 🔍 AI Insights
            if "top_insight" in data:
                st.markdown(f"""
                    <div style='background-color: #F8FAFC; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #3B82F6;'>
                        <b>🔍 AI Insights:</b> {data['top_insight']['thai_detail']}
                    </div>
                """, unsafe_allow_html=True)

            st.divider()

            # 4. 🧪 ระบบจำลองการปรับเปลี่ยนพฤติกรรม แยก 3 กลุ่มระดับความเสี่ยง
            payload = st.session_state.get('current_payload', {})
            modifiable_factors = []

            # 🔴 กลุ่มอาการบ่งชี้ความเสี่ยงสูง
            if payload.get('shortness_of_breath') == 2:
                modifiable_factors.append(
                    ("shortness_of_breath", "🫁 หากปัญหาการหายใจดีขึ้น", "กลุ่มเสี่ยงสูง"))
            if payload.get('coughing') == 2:
                modifiable_factors.append(
                    ("coughing", "🗣️ หากอาการระคายเคืองคอหายไป", "กลุ่มเสี่ยงสูง"))
            if payload.get('allergy') == 2:
                modifiable_factors.append(
                    ("allergy", "🤧 หากควบคุมอาการภูมิแพ้ได้", "กลุ่มเสี่ยงสูง"))
            if payload.get('fatigue') == 2:
                modifiable_factors.append(
                    ("fatigue", "🔋 หากหายจากอาการอ่อนเพลีย", "กลุ่มเสี่ยงสูง"))
            if payload.get('swallowing_difficulty') == 2:
                modifiable_factors.append(
                    ("swallowing_difficulty", "🍲 หากการกลืนลำบากดีขึ้น", "กลุ่มเสี่ยงสูง"))

            # 🟠 กลุ่มปัจจัยเสี่ยงพฤติกรรมหลัก
            if payload.get('smoking') == 2:
                modifiable_factors.append(
                    ("smoking", "🚭 หากเลิกสูบบุหรี่", "พฤติกรรมหลัก"))

            # 🔵 กลุ่มปัจจัยร่วม
            if payload.get('alcohol_consuming') == 2:
                modifiable_factors.append(
                    ("alcohol_consuming", "🍷 หากงดดื่มแอลกอฮอล์", "ปัจจัยร่วม"))

            if len(modifiable_factors) > 0:
                st.markdown(
                    "<h3 style='color: #0F172A; font-size: 20px;'>🧪 จำลองการปรับปรุงสุขภาพ</h3>", unsafe_allow_html=True)

                sim_payload = payload.copy()
                cols = st.columns(2)

                # แสดง Checkbox พร้อมบอกระดับกลุ่มความเสี่ยงในวงเล็บ
                for idx, (factor_key, label, group) in enumerate(modifiable_factors):
                    with cols[idx % 2]:
                        is_simulated = st.checkbox(
                            f"{label} [{group}]", value=False, key=f"sim_{factor_key}")
                        if is_simulated:
                            sim_payload[factor_key] = 1

                def calculate_simulated_risk(sim_data):
                    RISK_FACTORS_DB = {
                        "smoking": {"or": 2.59, "impact_weight": 2.0},
                        "breathing_issue": {"or": 7.13, "impact_weight": 1.5},
                        "throat_discomfort": {"or": 10.86, "impact_weight": 1.5},
                        "allergy": {"or": 6.46, "impact_weight": 1.2},
                        "fatigue": {"or": 5.87, "impact_weight": 1.2},
                        "swallowing_difficulty": {"or": 4.40, "impact_weight": 1.2},
                        "alcohol_consumption": {"or": 1.91, "impact_weight": 1.0},
                        "age": {"or": 1.01, "impact_weight": 1.0}
                    }
                    total = 0
                    max_score = 0
                    user_inp = {
                        "smoking": sim_data.get("smoking", 1),
                        "breathing_issue": sim_data.get("shortness_of_breath", 1),
                        "throat_discomfort": sim_data.get("coughing", 1),
                        "allergy": sim_data.get("allergy", 1),
                        "fatigue": sim_data.get("fatigue", 1),
                        "swallowing_difficulty": sim_data.get("swallowing_difficulty", 1),
                        "alcohol_consumption": sim_data.get("alcohol_consuming", 1)
                    }
                    for key, info in RISK_FACTORS_DB.items():
                        w = math.log(info["or"] if info["or"] > 1 else 1.1)
                        item_max = w * info["impact_weight"]
                        max_score += item_max

                        is_active = False
                        if key == "age":
                            if sim_data.get("age", 0) > 45:
                                is_active = True
                        elif user_inp.get(key) == 2:
                            is_active = True

                        if is_active:
                            total += item_max

                    res = round((total / max_score) * 100,
                                2) if max_score > 0 else 0
                    if sim_data.get("age", 0) < 35 and res > 30:
                        res = 28.0
                    return round(res, 2)

                new_risk = calculate_simulated_risk(sim_payload)
                old_risk = data['probability']

                if new_risk < old_risk:
                    diff = round(old_risk - new_risk, 2)
                    st.markdown(f"""
                        <div style='background-color: #D1FAE5; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                            <span style='color: #065F46; font-weight: 600;'>✨ ความเสี่ยงจะลดลงเหลือ {new_risk}% (ลดลง {diff}%)</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='background-color: #F8FAFC; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                            <span style='color: #475569; font-weight: 600;'>⚡ ความเสี่ยงปัจจุบันของคุณคือ {old_risk}%</span>
                        </div>
                    """, unsafe_allow_html=True)


# --- เนื้อหาหน้าแดชบอร์ด (tab2) ---
with tab2:
    st.markdown("<h2>📊 รายงานการวิเคราะห์และประวัติย้อนหลัง</h2>",
                unsafe_allow_html=True)

    color_map = {
        'กลุ่มอาการบ่งชี้ความเสี่ยงสูง': '#E11D48',
        'ปัจจัยเสี่ยงพฤติกรรมหลัก': '#EA580C',
        'กลุ่มปัจจัยร่วม': '#3B82F6'
    }

    if st.session_state.get('api_result'):
        st.markdown("### 🎯 ผลการประเมินความเสี่ยงของคุณ (รอบล่าสุด)")
        res = st.session_state['api_result']
        c_dash1, c_dash2 = st.columns(2)

        with c_dash1:
            with st.container(border=True):
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=res['probability'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#1E3A8A"},
                        'steps': [
                            {'range': [0, 40], 'color': "#10B981"},
                            {'range': [40, 70], 'color': "#F59E0B"},
                            {'range': [70, 100], 'color': "#E11D48"}
                        ]
                    },
                    title={'text': "คะแนนความเสี่ยงรวม (%)"}
                ))
                fig_gauge.update_layout(height=300, margin=dict(t=50, b=0))
                st.plotly_chart(fig_gauge, use_container_width=True)

        with c_dash2:
            insight = res.get("top_insight", {})
            st.markdown("#### 🔍 ปัจจัยที่ส่งผลต่อคุณมากที่สุด")
            st.success(f"**ปัจจัยสำคัญ:** {insight.get('feature', 'N/A')}")
            st.info(f"**ระดับความเสี่ยง:** {insight.get('level', 'N/A')}")
            st.warning(
                f"**ค่าสถิติ (Odds Ratio):** {insight.get('odds_ratio', 1.0)} เท่า")
    else:
        st.info(
            "💡 กรุณาทำการประเมินที่หน้าแรก (Tab 1) เพื่อดูผลวิเคราะห์ความเสี่ยงรอบปัจจุบันของคุณครับ")

    st.divider()

    st.markdown("### 📈 แนวโน้มความเสี่ยงย้อนหลังของคุณ")
    st.caption(
        "💡 **คลิกที่จุดบนกราฟเส้น** เพื่อดูปัจจัยเสี่ยงและค่าทำนายของวันนั้นๆ อย่างละเอียด")

    selected_payload = st.session_state.get('current_payload', None)
    selected_score = st.session_state.get('api_result', {}).get(
        'probability', 0) if st.session_state.get('api_result') else None
    chart_title_suffix = "<span style='color: #10B981;'>(ข้อมูลรอบปัจจุบัน)</span>"

    try:
        # เปลี่ยนจาก id_card เป็น username
        user_id = st.session_state.get('username')
        history_res = requests.get(
            # ปรับ Path ให้ตรงกับ API ใหม่
            f"https://lung-cancer-prediction-production.up.railway.app/user/user/{user_id}",
            timeout=5
        )

        if history_res.status_code == 200:
            history_data = history_res.json()
            if len(history_data) > 0:
                df_hist = pd.DataFrame(history_data)
                df_hist['created_at'] = pd.to_datetime(df_hist['created_at'])

                fig_line = px.line(
                    df_hist, x='created_at', y='risk_score', markers=True,
                    labels={'created_at': 'วันที่ตรวจ',
                            'risk_score': 'คะแนนความเสี่ยง (%)'},
                    title=""
                )
                fig_line.update_traces(
                    line_color='#3B82F6', marker=dict(size=12))
                fig_line.update_layout(height=350, margin=dict(t=20, b=20))

                event = st.plotly_chart(fig_line, use_container_width=True,
                                        on_select="rerun", selection_mode="points", key="hist_chart")

                if event and hasattr(event, "selection") and event.selection.points:
                    pt = event.selection.points[0]
                    pt_index = pt.get("point_index", pt.get("pointIndex"))

                    if pt_index is not None:
                        row_data = df_hist.iloc[pt_index]
                        try:
                            features_str = row_data.get('features_data', '{}')
                            if pd.isna(features_str) or not features_str:
                                features_str = '{}'

                            selected_payload = json.loads(features_str)
                            selected_score = row_data.get('risk_score', 0)

                            date_str = row_data['created_at'].strftime(
                                "%d/%m/%Y เวลา %H:%M")
                            chart_title_suffix = f"<span style='color: #E11D48;'>(ประวัติเมื่อ: {date_str})</span>"
                        except Exception:
                            st.warning(
                                "⚠️ ข้อมูลในวันดังกล่าวเป็นข้อมูลเก่าที่ยังไม่มีการบันทึกอาการ")
                            selected_payload = {}
            else:
                st.write("📭 ยังไม่มีข้อมูลประวัติการทำนายในระบบ")
        else:
            st.error(
                f"❌ ไม่สามารถดึงข้อมูลได้ (Status Code: {history_res.status_code})")
    except Exception as e:
        st.error(f"⚠️ ขัดข้องในการเชื่อมต่อฐานข้อมูล")

    if selected_payload is not None and len(selected_payload) > 0:
        st.divider()
        st.markdown(
            f"### 🔬 รายละเอียดปัจจัยเสี่ยง {chart_title_suffix}", unsafe_allow_html=True)

        if selected_score is not None:
            score_color = "#E11D48" if selected_score > 40 else (
                "#F59E0B" if selected_score > 28 else "#10B981")
            st.markdown(
                f"**คะแนนความเสี่ยงประเมินได้:** <span style='color: {score_color}; font-size: 1.5em; font-weight: bold;'>{selected_score}%</span>", unsafe_allow_html=True)

        active_features = []
        active_ors = []
        active_levels = []

        if selected_payload.get('shortness_of_breath') == 2:
            active_features.append('ปัญหาการหายใจ')
            active_ors.append(7.13)
            active_levels.append('กลุ่มอาการบ่งชี้ความเสี่ยงสูง')
        if selected_payload.get('coughing') == 2:
            active_features.append('อาการไอ/ระคายเคืองคอ')
            active_ors.append(10.86)
            active_levels.append('กลุ่มอาการบ่งชี้ความเสี่ยงสูง')
        if selected_payload.get('allergy') == 2:
            active_features.append('โรคภูมิแพ้')
            active_ors.append(6.46)
            active_levels.append('กลุ่มอาการบ่งชี้ความเสี่ยงสูง')
        if selected_payload.get('fatigue') == 2:
            active_features.append('ความอ่อนเพลีย')
            active_ors.append(5.87)
            active_levels.append('กลุ่มอาการบ่งชี้ความเสี่ยงสูง')
        if selected_payload.get('swallowing_difficulty') == 2:
            active_features.append('การกลืนลำบาก')
            active_ors.append(4.40)
            active_levels.append('กลุ่มอาการบ่งชี้ความเสี่ยงสูง')

        if selected_payload.get('smoking') == 2:
            active_features.append('การสูบบุหรี่')
            active_ors.append(2.59)
            active_levels.append('ปัจจัยเสี่ยงพฤติกรรมหลัก')

        if selected_payload.get('alcohol_consuming') == 2:
            active_features.append('การดื่มแอลกอฮอล์')
            active_ors.append(1.91)
            active_levels.append('กลุ่มปัจจัยร่วม')
        if selected_payload.get('age', 0) > 45:
            active_features.append('อายุ > 45 ปี')
            active_ors.append(1.01)
            active_levels.append('กลุ่มปัจจัยร่วม')

        if len(active_features) > 0:
            df_user_risk = pd.DataFrame({
                'ปัจจัยเสี่ยง (Features)': active_features,
                'Odds Ratio': active_ors,
                'ระดับความเสี่ยง': active_levels
            }).sort_values(by='Odds Ratio', ascending=True)

            fig_bar = px.bar(
                df_user_risk, x='Odds Ratio', y='ปัจจัยเสี่ยง (Features)', orientation='h',
                color='ระดับความเสี่ยง', color_discrete_map=color_map, text='Odds Ratio'
            )
            fig_bar.update_traces(textposition='outside',
                                  marker_line_color='black', marker_line_width=1)

            chart_height = max(150, len(active_features) * 50 + 100)
            fig_bar.update_layout(height=chart_height, margin=dict(
                l=20, r=40, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

            st.caption(
                f"📌 **สรุป:** พบปัจจัยเสี่ยงที่มีนัยสำคัญทางสถิติทั้งหมด **{len(active_features)}** ปัจจัย ในรอบการประเมินนี้")
        else:
            st.success(
                "✅ จากข้อมูลประวัติในรอบนี้ ไม่พบปัจจัยเสี่ยงหลักที่มีนัยสำคัญทางสถิติครับ")
