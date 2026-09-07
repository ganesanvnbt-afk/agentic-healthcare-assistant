# 🚀 Complete Deployment Guide for Streamlit Community Cloud

This guide provides step-by-step instructions for deploying your **PulseMind Agentic Healthcare Assistant** live to the web for free using **Streamlit Community Cloud** (or Hugging Face Spaces).

---

## 📋 Prerequisites
1. A **GitHub Account** ([github.com](https://github.com)).
2. Git installed on your computer ([git-scm.com](https://git-scm.com)).
3. Your project files in `agentic_healthcare_assistant`.

---

## 🛠️ Step-by-Step Streamlit Cloud Deployment

### Step 1: Initialize Git and Push Code to GitHub

1. Open **Command Prompt** or **PowerShell** and navigate to your project folder:
   ```cmd
   cd C:\Users\sharv\.gemini\antigravity-ide\scratch\agentic_healthcare_assistant
   ```

2. Initialize Git repository and commit your files:
   ```cmd
   git init
   git add .
   git commit -m "Initial commit of Agentic Healthcare Assistant"
   ```

3. Create a **New Repository** on GitHub:
   - Go to [github.com/new](https://github.com/new).
   - Name your repository (e.g., `agentic-healthcare-assistant`).
   - Set visibility to **Public** (required for free Streamlit Cloud hosting).
   - Click **Create repository**.

4. Link and push your local code to GitHub:
   ```cmd
   git remote add origin https://github.com/ganesanvnbt-afk/agentic-healthcare-assistant.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Deploy on Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
2. Click the **"New app"** button.
3. Select **"Use existing repo"**.
4. Fill in the deployment details:
   - **Repository**: `YOUR_GITHUB_USERNAME/agentic-healthcare-assistant`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy!"** 🚀

---

### Step 3: Verify Your Live App
Streamlit Cloud will automatically build your app and install all dependencies from `requirements.txt`. Within 1–2 minutes, your app will be live at a public URL like:
`https://agentic-healthcare-assistant.streamlit.app`

---

## 🌟 Key Cloud Features Included in this Repository
- **Automatic Seed DB Initialization**: `app.py` automatically initializes SQLite and FAISS vector indices on first launch.
- **Production Theme Config**: `.streamlit/config.toml` ensures dark medical slate theme renders automatically.
- **Zero API Key Requirement Out-of-the-Box**: Uses local embedding and deterministic fallback tools so the app never crashes on cloud deployment.

---

## 💡 Alternative Option: Deploying on Hugging Face Spaces
If you prefer Hugging Face Spaces:
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Select **Streamlit** as the Space SDK.
3. Upload/push your project files.
4. Your app will automatically build and run live on Hugging Face!
