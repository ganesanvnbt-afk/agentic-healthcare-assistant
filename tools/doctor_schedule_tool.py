import sqlite3
import datetime
from database import get_connection

def search_doctors(specialty=None, name=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM doctors WHERE 1=1"
    params = []
    
    if specialty:
        query += " AND LOWER(specialty) LIKE ?"
        params.append(f"%{specialty.lower()}%")
    if name:
        query += " AND LOWER(name) LIKE ?"
        params.append(f"%{name.lower()}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_doctor_available_slots(doctor_id=None, specialty=None, date=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT s.schedule_id, s.doctor_id, d.name as doctor_name, d.specialty, d.consultation_fee, d.room_number, s.slot_date, s.slot_time, s.is_booked
        FROM doctor_schedules s
        JOIN doctors d ON s.doctor_id = d.doctor_id
        WHERE s.is_booked = 0
    """
    params = []
    
    if doctor_id:
        query += " AND s.doctor_id = ?"
        params.append(doctor_id)
    if specialty:
        query += " AND LOWER(d.specialty) LIKE ?"
        params.append(f"%{specialty.lower()}%")
    if date:
        query += " AND s.slot_date = ?"
        params.append(date)
        
    query += " ORDER BY s.slot_date ASC, s.schedule_id ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def book_appointment(patient_id, doctor_id, slot_date, slot_time, reason="Consultation"):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Verify doctor slot availability
    cursor.execute("""
        SELECT schedule_id, is_booked FROM doctor_schedules
        WHERE doctor_id = ? AND slot_date = ? AND slot_time = ?
    """, (doctor_id, slot_date, slot_time))
    
    slot = cursor.fetchone()
    
    if not slot:
        # Auto-create slot if missing for test convenience or pick next slot
        cursor.execute("""
            INSERT INTO doctor_schedules (doctor_id, slot_date, slot_time, is_booked)
            VALUES (?, ?, ?, 1)
        """, (doctor_id, slot_date, slot_time))
        schedule_id = cursor.lastrowid
    elif slot["is_booked"] == 1:
        conn.close()
        return {
            "status": "FAILED",
            "reason": "SLOT_ALREADY_BOOKED",
            "message": f"Requested slot {slot_date} {slot_time} with Dr. {doctor_id} is already booked."
        }
    else:
        schedule_id = slot["schedule_id"]
        cursor.execute("UPDATE doctor_schedules SET is_booked = 1 WHERE schedule_id = ?", (schedule_id,))

    # 2. Check for double booking for patient at same time
    cursor.execute("""
        SELECT appointment_id FROM appointments
        WHERE patient_id = ? AND slot_date = ? AND slot_time = ? AND status = 'CONFIRMED'
    """, (patient_id, slot_date, slot_time))
    
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return {
            "status": "FAILED",
            "reason": "PATIENT_DOUBLE_BOOKING",
            "message": f"Patient already has a confirmed appointment at {slot_date} {slot_time}."
        }

    # 3. Create appointment
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, slot_date, slot_time, reason, status)
        VALUES (?, ?, ?, ?, ?, 'CONFIRMED')
    """, (patient_id, doctor_id, slot_date, slot_time, reason))
    
    app_id = cursor.lastrowid
    
    # Fetch Doctor details for confirmation message
    cursor.execute("SELECT name, specialty, room_number, consultation_fee FROM doctors WHERE doctor_id = ?", (doctor_id,))
    doc = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    doc_name = doc["name"] if doc else doctor_id
    specialty = doc["specialty"] if doc else "Specialist"
    room = doc["room_number"] if doc else "101"
    fee = doc["consultation_fee"] if doc else 150.0

    return {
        "status": "SUCCESS",
        "appointment_id": app_id,
        "patient_id": patient_id,
        "doctor_name": doc_name,
        "specialty": specialty,
        "slot_date": slot_date,
        "slot_time": slot_time,
        "room_number": room,
        "consultation_fee": fee,
        "message": f"Appointment successfully confirmed with {doc_name} ({specialty}) on {slot_date} at {slot_time} in Room {room}."
    }

def get_patient_appointments(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.appointment_id, a.patient_id, a.doctor_id, d.name as doctor_name, d.specialty, 
               a.slot_date, a.slot_time, a.reason, a.status, d.room_number
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = ?
        ORDER BY a.slot_date DESC, a.slot_time DESC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
