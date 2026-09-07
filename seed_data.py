import sqlite3
import datetime
from database import init_db, get_connection
from vector_db import patient_vector_store, medical_knowledge_vector_store

def populate_seed_data():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Clear existing seed data for clean initialization
    cursor.execute("DELETE FROM patients")
    cursor.execute("DELETE FROM patient_records")
    cursor.execute("DELETE FROM doctors")
    cursor.execute("DELETE FROM doctor_schedules")
    cursor.execute("DELETE FROM appointments")

    # 2. Add Patients
    patients = [
        ("P-1001", "Arthur Pendelton", 70, "Male", "Father", "+1 (555) 234-5678", "O+", "Sulfa Drugs", "Chronic Kidney Disease Stage 3", "70-year-old male with history of Stage 3 CKD (eGFR 42 mL/min/1.73m2), Essential Hypertension, and Type 2 Diabetes Mellitus."),
        ("P-1002", "Eleanor Vance", 45, "Female", "Self", "+1 (555) 876-5432", "A+", "Penicillin", "Bronchial Asthma", "45-year-old female with moderate persistent asthma managed with inhalers."),
        ("P-1003", "Marcus Miller", 62, "Male", "Husband", "+1 (555) 432-1098", "B-", "None", "Coronary Artery Disease", "62-year-old male post-stent placement, on antiplatelet therapy.")
    ]

    cursor.executemany("""
        INSERT INTO patients (patient_id, name, age, gender, relation, contact_phone, blood_group, allergies, primary_condition, medical_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, patients)

    # 3. Add EHR Clinical Records
    records = [
        ("P-1001", "Diagnosis", "CKD Stage 3 Evaluation", "eGFR: 42 mL/min/1.73m2, Serum Creatinine: 1.8 mg/dL. Urine albumin-to-creatinine ratio (uACR): 180 mg/g. BP: 134/82 mmHg.", "Dr. Aris Thorne", "Moderate"),
        ("P-1001", "Medication", "SGLT2 Inhibitor Prescription", "Prescribed Dapagliflozin 10mg once daily to slow CKD progression and provide renal protection.", "Dr. Aris Thorne", "Normal"),
        ("P-1001", "Vital", "Blood Pressure & Glucose Check", "BP: 128/78 mmHg, Fasting Blood Sugar: 118 mg/dL, HbA1c: 6.8%.", "Nurse Practitioner", "Normal"),
        ("P-1002", "Diagnosis", "Asthma Exacerbation", "Mild wheezing in bilateral upper lobes. Peak Flow: 350 L/min.", "Dr. Michael Chen", "Mild")
    ]

    cursor.executemany("""
        INSERT INTO patient_records (patient_id, record_type, title, details, doctor_name, severity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, records)

    # 4. Add Doctors
    doctors = [
        ("DOC-201", "Dr. Aris Thorne", "Nephrology", "MD, FASN (Nephrology & Renal Medicine)", 18, 200.0, "Building A, Suite 302"),
        ("DOC-202", "Dr. Sarah Jenkins", "Cardiology", "MD, FACC (Interventional Cardiology)", 15, 220.0, "Building B, Suite 105"),
        ("DOC-203", "Dr. Michael Chen", "Pulmonology", "MD, FCCP (Respiratory Medicine)", 12, 180.0, "Building A, Suite 210"),
        ("DOC-204", "Dr. Elena Rostova", "Endocrinology", "MD, PhD (Diabetes & Metabolism)", 14, 190.0, "Building C, Suite 401")
    ]

    cursor.executemany("""
        INSERT INTO doctors (doctor_id, name, specialty, qualification, experience_years, consultation_fee, room_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, doctors)

    # 5. Add Doctor Schedules
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    day_after = today + datetime.timedelta(days=2)

    schedules = [
        ("DOC-201", tomorrow.strftime("%Y-%m-%d"), "09:00 AM", 0),
        ("DOC-201", tomorrow.strftime("%Y-%m-%d"), "10:30 AM", 0),
        ("DOC-201", tomorrow.strftime("%Y-%m-%d"), "02:00 PM", 0),
        ("DOC-201", day_after.strftime("%Y-%m-%d"), "11:00 AM", 0),
        ("DOC-202", tomorrow.strftime("%Y-%m-%d"), "10:00 AM", 0),
        ("DOC-203", tomorrow.strftime("%Y-%m-%d"), "03:00 PM", 0)
    ]

    cursor.executemany("""
        INSERT INTO doctor_schedules (doctor_id, slot_date, slot_time, is_booked)
        VALUES (?, ?, ?, ?)
    """, schedules)

    conn.commit()
    conn.close()

    # 6. Index Seed Patient Records into FAISS Vector Database
    patient_vector_docs = [
        {
            "id": "pdoc_1",
            "content": "Patient Arthur Pendelton (P-1001), 70 year old male father. History of Chronic Kidney Disease Stage 3, eGFR 42 mL/min/1.73m2, Serum Creatinine 1.8 mg/dL, Hypertension, Type 2 Diabetes. Allergy: Sulfa Drugs.",
            "metadata": {"patient_id": "P-1001", "record_type": "Summary"}
        },
        {
            "id": "pdoc_2",
            "content": "Patient Eleanor Vance (P-1002), 45 year old female. Moderate persistent bronchial asthma managed with inhalers. Allergy: Penicillin.",
            "metadata": {"patient_id": "P-1002", "record_type": "Summary"}
        }
    ]
    patient_vector_store.add_documents(patient_vector_docs)

    # 7. Index MedlinePlus & WHO Medical Documents into Vector Store
    medical_docs = [
        {
            "id": "medline_ckd_1",
            "content": "MedlinePlus Guidelines on Chronic Kidney Disease (CKD) Management: CKD Stage 3 (eGFR 30-59 mL/min/1.73m2) requires aggressive blood pressure management (target < 130/80 mmHg), administration of SGLT2 inhibitors (Dapagliflozin/Empagliflozin) to reduce risk of kidney failure, non-steroidal MRA (Finerenone) for diabetic kidney disease, and strict dietary sodium control (<2000 mg/day). Avoid nephrotoxic NSAIDs.",
            "metadata": {"source": "MedlinePlus NIH", "title": "Chronic Kidney Disease Management & Pharmacotherapy", "url": "https://medlineplus.gov/chronickidneydisease.html"}
        },
        {
            "id": "who_ckd_2",
            "content": "World Health Organization (WHO) Fact Sheet on Kidney Health & Noncommunicable Diseases: Global recommendations call for early screening of high-risk populations (hypertension, diabetes), routine urine albumin testing, timely nephrologist referral, cardiovascular disease risk reduction, and avoiding unmonitored herbal supplements or nephrotoxic analgesics.",
            "metadata": {"source": "World Health Organization (WHO)", "title": "WHO Global Guidelines for CKD Prevention & Care", "url": "https://www.who.int/news-room/fact-sheets/detail/chronic-kidney-disease"}
        },
        {
            "id": "medline_hypertension_3",
            "content": "MedlinePlus Guidelines on Hypertension in Kidney Disease: First-line antihypertensive agents for patients with proteinuria include ACE inhibitors (e.g. Lisinopril) or Angiotensin Receptor Blockers (ARBs, e.g. Losartan). Monitor serum potassium and creatinine within 2 weeks of initiation.",
            "metadata": {"source": "MedlinePlus NIH", "title": "Hypertension & Renal Protection Guidelines", "url": "https://medlineplus.gov/highbloodpressure.html"}
        }
    ]
    medical_knowledge_vector_store.add_documents(medical_docs)

    print("Seed data & FAISS vector indices initialized successfully.")

if __name__ == "__main__":
    populate_seed_data()
