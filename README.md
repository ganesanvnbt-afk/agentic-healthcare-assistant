# 🏥 PulseMind Agentic Healthcare Assistant

An autonomous, production-grade **Agentic Healthcare Assistant** combining LLM Agent Planning, Retrieval-Augmented Generation (RAG via FAISS/MedlinePlus/WHO), Electronic Health Records (EHR) management, Doctor Appointment Scheduling, and LLMOps evaluation metrics in a Streamlit web UI.

---

## ⚡ How to Run in Command Prompt / Terminal

Follow these simple steps to run the application on Windows Command Prompt (`cmd.exe`) or PowerShell:

### Step 1: Open Command Prompt and Navigate to Project Directory
```cmd
cd C:\Users\sharv\.gemini\antigravity-ide\scratch\agentic_healthcare_assistant
```
*(If you extracted the zip file elsewhere, navigate to that extracted folder instead).*

---

### Step 2: Install Required Dependencies
Run the following command to install required Python libraries:
```cmd
pip install -r requirements.txt
```

---

### Step 3: Initialize Database & Vector Store (Seed Data)
Pre-populate the SQLite database and FAISS vector indices with sample patient profiles (including the 70-year-old CKD patient Arthur Pendelton), Nephrologists, calendar slots, and Medline/WHO clinical articles:
```cmd
python seed_data.py
```

---

### Step 4: Launch the Streamlit Web Application
Start the Streamlit dashboard server:
```cmd
streamlit run app.py
```

Once executed, your terminal will display:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```
Open **`http://localhost:8501`** in your Google Chrome, Edge, or default web browser!

---

## 🚀 Quick Launch (Shortcut Script)
You can also launch the app instantly by running:
```cmd
run_app.bat
```
or double-clicking **`run_app.bat`** in File Explorer!

---

## 🧪 How to Test Agent Scenario via CLI (Headless Mode)
To test the agent planner execution on the Capstone scenario directly from Command Prompt without opening a browser:
```cmd
python -c "from agent_planner import HealthcareAgentPlanner; planner = HealthcareAgentPlanner(); res = planner.execute_plan('My 70-year-old father has chronic kidney disease. I want to book a nephrologist for him. Also, can you summarize latest treatment methods?'); print(res['final_response']); print('\nEVALUATION METRICS:', res['evaluation_metrics'])"
```

---

## 📁 Key File Structure
- `app.py` - Main Streamlit multi-tab user interface.
- `agent_planner.py` - Agent Planner & Goal Decomposition engine.
- `vector_db.py` - FAISS & TF-IDF vector database for EHR and Medline/WHO documents.
- `memory.py` - Short-term chat history & long-term vector memory context.
- `evaluator.py` - QAEvalChain performance evaluation module.
- `database.py` - SQLite database setup for Patients, Doctors, Slots, Appointments, and Logs.
- `tools/` - Doctor schedule tool, Patient EHR tool, Medical Search tool, and RAG tool.
- `seed_data.py` - Database & vector store pre-populator.
- `requirements.txt` - Project dependencies list.
