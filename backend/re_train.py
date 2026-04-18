import pandas as pd
import joblib
import os
from sklearn.linear_model import LogisticRegression

# 1. จัดการ Path ให้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ชี้ไปที่ไฟล์ CSV ในโฟลเดอร์ data
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "set1_survey lung cancer.csv")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "best_model.pkl")

print(f"กำลังโหลดข้อมูลจาก: {DATA_PATH}")

# 2. โหลดข้อมูล
df = pd.read_csv(DATA_PATH)

# 3. เตรียมข้อมูล (Preprocessing) ให้ตรงกับที่ Web App ใช้
# แปลง GENDER: M=1, F=0
df['GENDER'] = df['GENDER'].map({'M': 1, 'F': 0})
# แปลง LUNG_CANCER: YES=1, NO=0
df['LUNG_CANCER'] = df['LUNG_CANCER'].map({'YES': 1, 'NO': 0})

# กำหนดลำดับ Feature ให้ตรงกับใน main.py เป๊ะๆ
features = [
    'AGE', 'GENDER', 'SMOKING', 'YELLOW_FINGERS', 'ANXIETY',
    'PEER_PRESSURE', 'CHRONIC DISEASE', 'FATIGUE ', 'ALLERGY ', 'WHEEZING',
    'ALCOHOL CONSUMING', 'COUGHING', 'SHORTNESS OF BREATH',
    'SWALLOWING DIFFICULTY', 'CHEST PAIN'
]

X = df[features]
y = df['LUNG_CANCER']

# 4. สร้างและฝึกสอนโมเดลใหม่
print("กำลังฝึกสอนโมเดลใหม่...")
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

# 5. บันทึกโมเดล (จะไปทับไฟล์เดิมที่มีปัญหา)
joblib.dump(model, MODEL_SAVE_PATH)

print(f"✅ สำเร็จ! สร้างไฟล์ {MODEL_SAVE_PATH} ใหม่เรียบร้อยแล้ว")
print("ตอนนี้คุณสามารถรัน python backend/main.py ได้เลยครับ")
