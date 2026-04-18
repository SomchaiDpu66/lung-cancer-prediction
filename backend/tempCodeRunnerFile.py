import sqlite3
import hashlib
import os
import json
from datetime import datetime

# กำหนด Path ของฐานข้อมูลไว้ในโฟลเดอร์ backend
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. สร้างตารางผู้ใช้งาน
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, full_name TEXT)''')

    # 2. สร้างตารางประวัติการทำนาย (เชื่อมโยงด้วย username)
    c.execute('''CREATE TABLE IF NOT EXISTS prediction_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  date TEXT,
                  risk_score REAL,
                  prediction TEXT,
                  symptoms_json TEXT,
                  FOREIGN KEY (username) REFERENCES users (username))''')

    conn.commit()
    conn.close()
    print("✅ Database & Tables initialized successfully!")

# --- ฟังก์ชันสำหรับจัดการผู้ใช้ ---


def add_user(username, password, full_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users VALUES (?, ?, ?)",
                  (username, hashed_pw, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- ฟังก์ชันสำหรับบันทึกประวัติลง Database ---


def save_prediction(username, score, prediction, symptoms_dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # แปลง dict อาการเป็น JSON string เพื่อเก็บในตาราง
    symptoms_json = json.dumps(symptoms_dict)

    c.execute('''INSERT INTO prediction_history (username, date, risk_score, prediction, symptoms_json) 
                 VALUES (?, ?, ?, ?, ?)''', (username, date_str, score, prediction, symptoms_json))
    conn.commit()
    conn.close()

# --- ฟังก์ชันสำหรับดึงประวัติเฉพาะบุคคล ---


def get_user_history(username):
    conn = sqlite3.connect(DB_PATH)
    # ใช้ row_factory เพื่อให้ผลลัพธ์เป็น dict ที่เรียกใช้ง่าย
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM prediction_history WHERE username=? ORDER BY date DESC", (username,))
    rows = c.fetchall()
    conn.close()
    return rows
