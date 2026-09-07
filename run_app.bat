@echo off
echo =========================================================
echo  Starting PulseMind Agentic Healthcare Assistant...
echo =========================================================
cd /d "%~dp0"
echo 1. Checking / Initializing Database & Vector Stores...
python seed_data.py
echo.
echo 2. Launching Streamlit Web App on http://localhost:8501...
streamlit run app.py
pause
