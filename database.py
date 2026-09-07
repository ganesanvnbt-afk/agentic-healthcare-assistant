import sqlite3
import datetime
import json
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        relation TEXT,
        contact_phone TEXT,
        blood_group TEXT,
        allergies TEXT,
        primary_condition TEXT,
        medical_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Patient Records Table (EHR History)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        record_type TEXT NOT NULL, -- Diagnosis, Vital, Clinical Note, Lab Result, Medication
        title TEXT NOT NULL,
        details TEXT NOT NULL,
        doctor_name TEXT,
        severity TEXT DEFAULT 'Normal',
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    );
    """)

    # 3. Doctors Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        qualification TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        consultation_fee REAL NOT NULL,
        room_number TEXT NOT NULL
    );
    """)

    # 4. Doctor Schedules Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctor_schedules (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id TEXT NOT NULL,
        slot_date TEXT NOT NULL, -- YYYY-MM-DD
        slot_time TEXT NOT NULL, -- HH:MM AM/PM
        is_booked INTEGER DEFAULT 0,
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    );
    """)

    # 5. Appointments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        doctor_id TEXT NOT NULL,
        slot_date TEXT NOT NULL,
        slot_time TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'CONFIRMED', -- CONFIRMED, COMPLETED, CANCELLED
        booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    );
    """)

    # 6. Evaluation & System Execution Logs (LLMOps)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_execution_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT NOT NULL,
        prompt TEXT NOT NULL,
        decomposed_goals TEXT NOT NULL, -- JSON string
        tool_calls TEXT NOT NULL, -- JSON string
        overall_success INTEGER NOT NULL, -- 1 or 0
        latency_ms INTEGER NOT NULL,
        relevance_score REAL,
        faithfulness_score REAL,
        hallucination_score REAL,
        evaluation_summary TEXT
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
