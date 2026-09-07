import streamlit as st
import pandas as pd
import json
import datetime
import os

# Page Config - Must be first Streamlit command
st.set_page_config(
    page_title="PulseMind Agentic Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize seed data if database is empty
from seed_data import populate_seed_data
from database import get_connection, init_db

init_db()
conn = get_connection()
c = conn.cursor()
c.execute("SELECT COUNT(*) as cnt FROM patients")
if c.fetchone()["cnt"] == 0:
    populate_seed_data()
conn.close()

from agent_planner import HealthcareAgentPlanner
from tools.patient_db_tool import get_patient_by_id, search_patient_by_query, get_patient_records, add_patient_record, summarize_patient_history
from tools.doctor_schedule_tool import search_doctors, get_doctor_available_slots, book_appointment, get_patient_appointments
from tools.medical_search_tool import search_medline_and_who
from vector_db import patient_vector_store, medical_knowledge_vector_store
from evaluator import HealthcareAgentEvaluator
from ui_components import apply_custom_css, render_header, render_metric_card, plot_llmops_metrics

apply_custom_css()

# Initialize session state objects
if "planner" not in st.session_state:
    st.session_state.planner = HealthcareAgentPlanner()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "latest_trace" not in st.session_state:
    st.session_state.latest_trace = []
if "evaluator" not in st.session_state:
    st.session_state.evaluator = HealthcareAgentEvaluator()

# --- SIDEBAR NAVIGATION & CONTEXT ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/medical-heart.png", width=70)
    st.title("PulseMind AI")
    st.caption("Agentic Healthcare Assistant & RAG Engine")
    
    st.markdown("---")
    st.subheader("🎯 Preset Capstone Scenario")
    sample_prompt = "My 70-year-old father has chronic kidney disease. I want to book a nephrologist for him. Also, can you summarize latest treatment methods?"
    
    if st.button("🚀 Run 70yo CKD Scenario", use_container_width=True, type="primary"):
        st.session_state.selected_prompt = sample_prompt
        
    st.markdown("---")
    st.subheader("⚙️ System Status")
    st.markdown("• **Agent Planner**: `READY (DAG)`")
    st.markdown("• **Vector DB**: `FAISS / TF-IDF Active`")
    st.markdown("• **EHR Database**: `SQLite Connected`")
    st.markdown("• **Medical Sources**: `MedlinePlus & WHO`")
    st.markdown("• **LLMOps**: `QAEvalChain Active`")
    
    st.markdown("---")
    if st.button("🔄 Reset Seed Database", use_container_width=True):
        populate_seed_data()
        st.success("Database re-seeded successfully.")
        st.rerun()

# --- HEADER ---
render_header("PulseMind Agentic Healthcare Assistant", "Autonomous Medical Task Automation • RAG Intelligence • EHR & Doctor Scheduling Engine")

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 Agentic Assistant", 
    "📋 Patient EHR Management", 
    "📅 Doctor & Booking Hub", 
    "📚 Medical RAG Explorer", 
    "📊 LLMOps & System Logs"
])

# ==========================================
# TAB 1: AGENTIC ASSISTANT (CHAT & SCENARIOS)
# ==========================================
with tab1:
    col_chat, col_trace = st.columns([1.6, 1.0])
    
    with col_chat:
        st.markdown("### 💬 Interactive Medical Assistant")
        st.caption("Ask multi-intent requests: book doctors, manage patient history, or query trusted treatments.")
        
        # Scenario Quick Buttons
        st.markdown("**Quick Preset Queries:**")
        q_cols = st.columns(2)
        with q_cols[0]:
            if st.button("🫘 70yo Father CKD & Nephrologist", use_container_width=True):
                st.session_state.selected_prompt = sample_prompt
        with q_cols[1]:
            if st.button("🫁 Eleanor Vance Asthma Treatment", use_container_width=True):
                st.session_state.selected_prompt = "Retrieve history for Eleanor Vance and find latest asthma guidelines from WHO."

        # Handle prompt submission
        user_input = st.text_input("Enter your request:", value=st.session_state.get("selected_prompt", ""), key="user_prompt_input")
        st.session_state.selected_prompt = "" # Reset after input
        
        if st.button("⚡ Execute Agent Workflow", type="primary", use_container_width=True) and user_input:
            with st.spinner("Agent Planner decomposing goals and triggering tool workflow..."):
                result = st.session_state.planner.execute_plan(user_input)
                st.session_state.chat_history.append({"prompt": user_input, "result": result})
                st.session_state.latest_trace = result["trace_steps"]
                
        # Render Chat History
        for item in reversed(st.session_state.chat_history):
            st.markdown(f"**👤 User Query:** {item['prompt']}")
            st.markdown(item["result"]["final_response"])
            
            # Show Metrics Badge
            m = item["result"]["evaluation_metrics"]
            st.markdown(f"""
            <span class="badge-success">Success: {m['overall_success'] == 1}</span>
            <span class="badge-info">Relevance: {m['relevance_score']*100}%</span>
            <span class="badge-info">Faithfulness: {m['faithfulness_score']*100}%</span>
            <span class="badge-info">Latency: {m['latency_ms']}ms</span>
            """, unsafe_allow_html=True)
            st.markdown("---")

    with col_trace:
        st.markdown("### 🧠 Agent Execution & Memory Trace")
        st.caption("Real-time view of sub-goal decomposition and memory lookups.")
        
        if st.session_state.latest_trace:
            st.markdown("#### 📌 Goal Decomposition Breakdown")
            for step in st.session_state.latest_trace:
                st.markdown(f"""
                <div class="trace-card">
                    <div class="trace-step-title">Step {step['step_number']}: {step['goal']}</div>
                    <div style="font-size:13px; color:#94a3b8; margin-top:4px;">
                        <b>Tool:</b> <code>{step['tool_name']}</code>
                    </div>
                    <div style="font-size:12px; margin-top:6px; color:#cbd5e1;">
                        <b>Output:</b> {step['tool_output']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Run an agent scenario to inspect step-by-step goal decomposition and tool outputs.")

        # Short term & long term memory status
        st.markdown("#### 💾 Active Memory Context")
        active_p = st.session_state.planner.short_memory.active_patient_id or "P-1001"
        st.markdown(f"• **Active Patient ID**: `{active_p}`")
        st.markdown("• **Short-Term Context**: `70yo Father, CKD Stage 3`")
        st.markdown("• **Long-Term Vector Index**: `FAISS Patient Summary Index`")

# ==========================================
# TAB 2: PATIENT EHR MANAGEMENT
# ==========================================
with tab2:
    st.markdown("### 📋 Electronic Health Records (EHR) & Patient DB")
    
    col_p1, col_p2 = st.columns([1, 1.2])
    
    with col_p1:
        st.markdown("#### 🔍 Patient Directory")
        p_search = st.text_input("Search patient by name, relation, or condition:", value="")
        patients = search_patient_by_query(p_search if p_search else "father")
        
        selected_patient_id = None
        if patients:
            df_p = pd.DataFrame(patients)[["patient_id", "name", "age", "gender", "relation", "primary_condition"]]
            st.dataframe(df_p, use_container_width=True)
            selected_patient_id = st.selectbox("Select Patient to view/update:", df_p["patient_id"].tolist())
        else:
            st.warning("No patients found.")

        st.markdown("---")
        st.markdown("#### ➕ Add Clinical Record / EHR Note")
        with st.form("add_record_form"):
            r_type = st.selectbox("Record Type", ["Clinical Note", "Diagnosis", "Vital", "Lab Result", "Medication"])
            r_title = st.text_input("Title", value="Nephrology Follow-up")
            r_details = st.text_area("Details / Notes", value="eGFR improved to 45 mL/min. Stable blood pressure.")
            r_doc = st.text_input("Doctor Name", value="Dr. Aris Thorne")
            r_sev = st.selectbox("Severity", ["Normal", "Mild", "Moderate", "Severe"])
            
            if st.form_submit_button("Save & Index Record"):
                if selected_patient_id:
                    res = add_patient_record(selected_patient_id, r_type, r_title, r_details, r_doc, r_sev)
                    st.success(res["message"])
                    st.rerun()

    with col_p2:
        if selected_patient_id:
            st.markdown(f"#### 📄 Comprehensive Medical Summary: `{selected_patient_id}`")
            summary_info = summarize_patient_history(selected_patient_id)
            st.text_area("Clinical History Summary", value=summary_info["summary"], height=220)
            
            st.markdown("#### 🔬 Detailed Historical Records")
            records = get_patient_records(selected_patient_id)
            if records:
                st.dataframe(pd.DataFrame(records)[["timestamp", "record_type", "title", "details", "doctor_name", "severity"]], use_container_width=True)
            else:
                st.info("No clinical records found for this patient.")

# ==========================================
# TAB 3: DOCTOR & BOOKING HUB
# ==========================================
with tab3:
    st.markdown("### 📅 Doctor Schedule & Appointment Booking Hub")
    
    col_d1, col_d2 = st.columns([1.2, 1])
    
    with col_d1:
        st.markdown("#### 👨‍⚕️ Available Doctors & Specialties")
        specialty_filter = st.selectbox("Filter Specialty:", ["All Specialties", "Nephrology", "Cardiology", "Pulmonology", "Endocrinology"])
        
        spec = None if specialty_filter == "All Specialties" else specialty_filter
        doctors = search_doctors(specialty=spec)
        
        if doctors:
            st.dataframe(pd.DataFrame(doctors)[["doctor_id", "name", "specialty", "qualification", "experience_years", "consultation_fee", "room_number"]], use_container_width=True)

        st.markdown("---")
        st.markdown("#### ⏱️ Open Calendar Slots")
        slots = get_doctor_available_slots(specialty=spec)
        if slots:
            st.dataframe(pd.DataFrame(slots)[["schedule_id", "doctor_name", "specialty", "slot_date", "slot_time", "consultation_fee", "room_number"]], use_container_width=True)
        else:
            st.info("No open slots found for selected criteria.")

    with col_d2:
        st.markdown("#### 📑 Active Appointments")
        p_app_id = st.text_input("Filter Appointments by Patient ID:", value="P-1001")
        apps = get_patient_appointments(p_app_id)
        
        if apps:
            for app in apps:
                st.markdown(f"""
                <div style="background:#1e293b; padding:14px; border-radius:10px; margin-bottom:10px; border-left:4px solid #34d399;">
                    <div style="font-weight:700; color:#ffffff;">{app['doctor_name']} ({app['specialty']})</div>
                    <div style="font-size:13px; color:#94a3b8;">📅 Date: {app['slot_date']} at {app['slot_time']} | Room: {app['room_number']}</div>
                    <div style="font-size:12px; color:#cbd5e1; margin-top:4px;">Reason: {app['reason']}</div>
                    <div style="margin-top:6px;"><span class="badge-success">{app['status']}</span></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"No appointments found for Patient ID `{p_app_id}`.")

# ==========================================
# TAB 4: MEDICAL RAG EXPLORER
# ==========================================
with tab4:
    st.markdown("### 📚 Medical Knowledge Base & RAG Explorer")
    st.caption("Search verified guidelines from MedlinePlus (NIH) and World Health Organization (WHO).")
    
    rag_query = st.text_input("Enter disease, symptom, or treatment query:", value="chronic kidney disease latest treatments")
    
    if st.button("🔎 Run RAG Medical Search", type="primary") or rag_query:
        rag_out = search_medline_and_who(rag_query)
        
        st.markdown(f"**Found {rag_out['results_count']} Verified Medical Articles:**")
        
        for doc in rag_out["documents"]:
            st.markdown(f"""
            <div style="background:#0f172a; padding:16px; border-radius:10px; margin-bottom:12px; border:1px solid #334155;">
                <div style="font-weight:700; color:#38bdf8; font-size:16px;">{doc['title']}</div>
                <div style="font-size:12px; color:#34d399; margin-top:2px;"><b>Source:</b> {doc['source']} | <b>Relevance Score:</b> {doc['relevance_score']}</div>
                <div style="font-size:13px; color:#cbd5e1; margin-top:8px;">{doc['snippet']}</div>
                <div style="font-size:11px; margin-top:6px;"><a href="{doc['url']}" target="_blank" style="color:#60a5fa;">🔗 View Source Article</a></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🗄️ Indexed Vector Store Documents (FAISS)")
    all_docs = medical_knowledge_vector_store.get_all_documents()
    if all_docs:
        v_df = pd.DataFrame([{"ID": d["id"], "Content": d["content"][:120] + "...", "Source": d.get("metadata", {}).get("source")} for d in all_docs])
        st.dataframe(v_df, use_container_width=True)

# ==========================================
# TAB 5: LLOPS & SYSTEM LOGS DASHBOARD
# ==========================================
with tab5:
    st.markdown("### 📊 LLMOps Performance & Quality Dashboard")
    st.caption("Automated QAEvalChain metrics, tool success tracking, and execution log inspection.")
    
    metrics = st.session_state.evaluator.get_evaluation_metrics_summary()
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        render_metric_card("Total Agent Runs", metrics["total_runs"])
    with col_m2:
        render_metric_card("Success Rate", f"{metrics['success_rate']}%")
    with col_m3:
        render_metric_card("Avg Relevance", f"{metrics['avg_relevance']*100}%")
    with col_m4:
        render_metric_card("Avg Latency", f"{metrics['avg_latency_ms']} ms")
        
    st.markdown("---")
    plot_llmops_metrics(metrics)
    
    st.markdown("---")
    st.markdown("#### 📜 System Execution Logs")
    if metrics["recent_logs"]:
        st.dataframe(pd.DataFrame(metrics["recent_logs"])[["timestamp", "session_id", "overall_success", "latency_ms", "relevance_score", "faithfulness_score", "evaluation_summary"]], use_container_width=True)
    else:
        st.info("No execution logs recorded yet. Run agent scenarios in Tab 1 to generate metrics.")
