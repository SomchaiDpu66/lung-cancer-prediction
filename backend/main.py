import math
import os
import joblib
import pandas as pd
import numpy as np
import traceback
import uvicorn
import json
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlalchemy import create_engine

# ==========================================
# ส่วนที่ 1: สร้าง Application Instance
# ==========================================
app = FastAPI(title="Lung Cancer AI API")

# ==========================================
# ส่วนที่ 2: วาง CORS Middleware (ต้องอยู่ตรงนี้เพื่อดักจับทุก Request)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    # ตอน Deploy จริงแนะนำให้เปลี่ยนเป็น URL ของ Streamlit
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ส่วนที่ 3: การตั้งค่าพื้นฐาน (Global Config) & โหลด Model
# ==========================================

# 1. กำหนด BASE_DIR ไว้ด้านนอกสุดเพื่อให้ทุกส่วนเรียกใช้ได้
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. พยายามดึงค่าจากระบบ Railway
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. แก้ไข Prefix สำหรับ PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. ถ้าไม่มี DATABASE_URL (รันในเครื่อง) ให้ใช้ SQLite
if not DATABASE_URL:
    DB_PATH = os.path.join(BASE_DIR, "lung_cancer.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# 5. สร้าง Engine
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={
                           "check_same_thread": False})
else:
    # เพิ่ม pool_pre_ping=True เพื่อช่วยรักษาการเชื่อมต่อกับ Railway ให้เสถียรขึ้น
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 6. โหลด Model (ใช้ BASE_DIR ที่ประกาศไว้บรรทัดแรก)
try:
    model_path = os.path.join(BASE_DIR, "best_model.pkl")
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print("✅ Model loaded successfully!")
    else:
        print(f"❌ Error: Model file NOT FOUND at {model_path}")
        model = None  # ป้องกันแอปพัง แต่จะทำนายไม่ได้
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# --- ปัจจัยเสี่ยง 3 ระดับ ---
RISK_FACTORS_DB = {
    "smoking": {"thai": "การสูบบุหรี่", "level": "ปัจจัยเสี่ยงพฤติกรรมหลัก", "or": 2.59, "impact_weight": 2.0},
    "breathing_issue": {"thai": "ปัญหาการหายใจ/หายใจลำบาก", "level": "กลุ่มอาการบ่งชี้ความเสี่ยงสูง", "or": 7.13, "impact_weight": 1.5},
    "throat_discomfort": {"thai": "อาการไอ/ระคายเคืองคอ", "level": "กลุ่มอาการบ่งชี้ความเสี่ยงสูง", "or": 10.86, "impact_weight": 1.5},
    "allergy": {"thai": "โรคภูมิแพ้", "level": "กลุ่มอาการบ่งชี้ความเสี่ยงสูง", "or": 6.46, "impact_weight": 1.2},
    "fatigue": {"thai": "ความอ่อนเพลีย", "level": "กลุ่มอาการบ่งชี้ความเสี่ยงสูง", "or": 5.87, "impact_weight": 1.2},
    "swallowing_difficulty": {"thai": "การกลืนลำบาก", "level": "กลุ่มอาการบ่งชี้ความเสี่ยงสูง", "or": 4.40, "impact_weight": 1.2},
    "alcohol_consumption": {"thai": "การดื่มแอลกอฮอล์", "level": "กลุ่มปัจจัยร่วม", "or": 1.91, "impact_weight": 1.0},
    "age": {"thai": "ช่วงอายุที่มีความเสี่ยง", "level": "กลุ่มปัจจัยร่วม", "or": 1.01, "impact_weight": 1.0}
}

# ==========================================
# ส่วนที่ 4: นิยามโครงสร้างข้อมูล (SQLModels & Pydantic)
# ==========================================


class User(SQLModel, table=True):
    pta_username: str = Field(primary_key=True, index=True)
    pta_firstname: str
    pta_lastname: str
    pta_address_number: str
    pta_email: str
    pta_phone: str
    pta_img: Optional[str] = Field(default=None)
    province_code: str
    amphur_code: str
    district_code: str
    zipcode: str
    ptd_id: str
    crt_date: datetime = Field(default_factory=datetime.now)
    username: Optional[str] = Field(default=None, index=True)
    password: str


class PredictionHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pta_username: str = Field(foreign_key="user.pta_idcard", index=True)
    risk_score: float
    prediction_result: str
    features_data: str = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.now)


class PredictionInput(BaseModel):
    pta_idcard: str
    age: int
    gender: int
    smoking: int
    yellow_fingers: int
    anxiety: int
    peer_pressure: int
    chronic_disease: int
    fatigue: int
    allergy: int
    wheezing: int
    alcohol_consuming: int
    coughing: int
    shortness_of_breath: int
    swallowing_difficulty: int
    chest_pain: int


class UserUpdate(BaseModel):
    pta_firstname: Optional[str] = None
    pta_lastname: Optional[str] = None
    pta_address_number: Optional[str] = None
    pta_email: Optional[str] = None
    pta_phone: Optional[str] = None
    pta_img: Optional[str] = None
    province_code: Optional[str] = None
    amphur_code: Optional[str] = None
    district_code: Optional[str] = None
    zipcode: Optional[str] = None
    ptd_id: Optional[str] = None
    password: Optional[str] = None

# ==========================================
# ส่วนที่ 5: การทำงานตอน Startup & Mount Static
# ==========================================


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==========================================
# ส่วนที่ 6: API Endpoints ทั้งหมด
# ==========================================


@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "API is running properly"}


@app.get("/user/users", tags=["User"])
def get_users():
    with Session(engine) as session:
        return session.exec(select(User)).all()


@app.post("/user/users", tags=["User"])
def create_user(user_data: User):
    with Session(engine) as session:
        existing_user = session.get(User, user_data.pta_idcard)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="รหัสบัตรประชาชนนี้เคยลงทะเบียนแล้ว")
        user_data.username = user_data.pta_idcard
        session.add(user_data)
        session.commit()
        session.refresh(user_data)
        return user_data


@app.get("/user/users/p", tags=["User"])
def get_users_with_pagination(skip: int = 0, limit: int = 10):
    with Session(engine) as session:
        users = session.exec(select(User).offset(skip).limit(limit)).all()
        return users


@app.get("/user/user/{user_id}", tags=["User"])
def get_user(user_id: str):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้ใช้งาน")
        return user


@app.put("/user/user/{user_id}", tags=["User"])
def update_user(user_id: str, user_update: UserUpdate):
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้ใช้งาน")
        user_data = user_update.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.delete("/user/user/{user_id}", tags=["User"])
def delete_user(user_id: str):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้ใช้งาน")
        session.delete(user)
        session.commit()
        return {"status": "success", "message": f"ลบผู้ใช้งาน {user_id} สำเร็จ"}


@app.post("/user/login", tags=["User"])
def login_user(username: str, password: str):
    with Session(engine) as session:
        statement = select(User).where(
            User.username == username, User.password == password)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        return {"status": "success", "full_name": f"{user.pta_firstname} {user.pta_lastname}", "id_card": user.pta_idcard}


@app.post("/user/upload_image", tags=["User"])
async def upload_image(file: UploadFile = File(...)):
    try:
        ext = file.filename.split('.')[-1]
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = f"uploads/{new_filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        return {"status": "success", "filename": new_filename}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"ไม่สามารถบันทึกไฟล์ได้: {str(e)}")


@app.post("/predict", tags=["Prediction & History"])
async def predict(data: PredictionInput):
    try:
        user_input = {
            "smoking": data.smoking,
            "breathing_issue": data.shortness_of_breath,
            "throat_discomfort": data.coughing,
            "allergy": data.allergy,
            "fatigue": data.fatigue,
            "swallowing_difficulty": data.swallowing_difficulty,
            "alcohol_consumption": data.alcohol_consuming
        }

        total_score = 0
        max_possible_score = 0
        active_factors = []

        for key, info in RISK_FACTORS_DB.items():
            weight = math.log(info["or"] if info["or"] > 1 else 1.1)
            item_max_score = weight * info["impact_weight"]
            max_possible_score += item_max_score

            is_active = False
            if key == "age":
                if data.age > 45:
                    is_active = True
            elif user_input.get(key) == 2:
                is_active = True

            if is_active:
                total_score += item_max_score
                active_factors.append(
                    {"name": info["thai"], "level": info["level"], "or": info["or"]})

        risk_percentage = round(
            (total_score / max_possible_score) * 100, 2) if max_possible_score > 0 else 0

        is_young_patient = data.age < 35
        guardrail_applied = False

        if is_young_patient and risk_percentage > 30:
            risk_percentage = 28.0
            prediction_result = "NO"
            guardrail_applied = True
        else:
            prediction_result = "YES" if risk_percentage > 40 else "NO"

        if active_factors:
            best_insight = max(active_factors, key=lambda x: x["or"])
            top_feature, top_or, top_level = best_insight["name"], best_insight["or"], best_insight["level"]
            if guardrail_applied:
                thai_detail = f"อาการ '{top_feature}' ที่คุณพบ มักเกิดจากโรคทางเดินหายใจทั่วไป โอกาสเป็นมะเร็งปอดมีน้อยมากเนื่องจากคุณอายุเพียง {data.age} ปี แต่แนะนำให้พบแพทย์เพื่อตรวจรักษาอาการเบื้องต้นครับ"
            else:
                thai_detail = f"คุณมีปัจจัยเสี่ยงในกลุ่ม '{top_level}' คือ '{top_feature}' ซึ่งมีค่า Odds Ratio {top_or} เท่า"
        else:
            top_feature, top_or, top_level = "ไม่พบปัจจัยเสี่ยงชัดเจน", 1.0, "ปกติ"
            thai_detail = "ไม่พบปัจจัยเสี่ยงหลักที่มีนัยสำคัญทางสถิติ"

        features_json_str = json.dumps(data.dict())

        with Session(engine) as session:
            new_history = PredictionHistory(
                pta_idcard=data.pta_username,
                risk_score=risk_percentage,
                prediction_result=prediction_result,
                features_data=features_json_str
            )
            session.add(new_history)
            session.commit()

        return {
            "prediction": prediction_result,
            "probability": risk_percentage,
            "top_insight": {
                "feature": top_feature,
                "odds_ratio": top_or,
                "level": top_level,
                "thai_detail": thai_detail
            }
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=400, content={"message": str(e)})


@app.get("/history/{id_card}", tags=["Prediction & History"])
def get_user_history(id_card: str):
    with Session(engine) as session:
        statement = select(PredictionHistory).where(
            PredictionHistory.pta_username == id_card).order_by(PredictionHistory.created_at.desc())
        results = session.exec(statement).all()
        return results


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
