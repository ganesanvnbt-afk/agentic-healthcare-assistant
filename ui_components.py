import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def apply_custom_css():
    st.markdown("""
    <style>
    /* Main Theme Overrides */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f766e 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 118, 110, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 15px;
        color: #94a3b8;
        margin-top: 6px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 18px;
        border-radius: 12px;
        color: white;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
        border-color: #0d9488;
    }
    
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #2dd4bf;
        margin-top: 4px;
    }
    
    .metric-label {
        font-size: 13px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Step Trace Cards */
    .trace-card {
        background: #0f172a;
        border-left: 4px solid #0d9488;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
        color: #e2e8f0;
    }
    
    .trace-step-title {
        font-weight: 600;
        font-size: 15px;
        color: #38bdf8;
    }

    .badge-success {
        background-color: #064e3b;
        color: #34d399;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-info {
        background-color: #1e3a8a;
        color: #60a5fa;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle):
    st.markdown(f"""
    <div class="header-banner">
        <div class="header-title">🏥 {title}</div>
        <div class="header-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div style="font-size:12px; color:#34d399;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def plot_llmops_metrics(metrics):
    df_recent = pd.DataFrame(metrics.get("recent_logs", []))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge Chart for Success Rate
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = metrics["success_rate"],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Tool Execution Success Rate (%)"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#0d9488"},
                'steps': [
                    {'range': [0, 50], 'color': "#7f1d1d"},
                    {'range': [50, 80], 'color': "#78350f"},
                    {'range': [80, 100], 'color': "#064e3b"}
                ]
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Radar or Bar chart for Scores
        score_data = pd.DataFrame({
            "Metric": ["Relevance", "Faithfulness", "Low Hallucination"],
            "Score": [metrics["avg_relevance"] * 100, metrics["avg_faithfulness"] * 100, (1 - metrics["avg_hallucination"]) * 100]
        })
        fig_bar = px.bar(score_data, x="Metric", y="Score", color="Metric", text_auto=".1f",
                         title="Quality & Precision Breakdown (%)", color_discrete_sequence=["#38bdf8", "#34d399", "#a78bfa"])
        fig_bar.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig_bar, use_container_width=True)

    if not df_recent.empty and "latency_ms" in df_recent.columns:
        fig_lat = px.line(df_recent, y="latency_ms", title="Agent Execution Response Latency (ms)",
                          labels={"index": "Run Index", "latency_ms": "Latency (ms)"}, markers=True)
        fig_lat.update_traces(line_color="#2dd4bf")
        fig_lat.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig_lat, use_container_width=True)
