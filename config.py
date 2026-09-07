import os

# Project Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database Settings
DB_PATH = os.path.join(BASE_DIR, "healthcare_assistant.db")
FAISS_INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")

# External Trusted API Settings (MedlinePlus / WHO)
MEDLINE_SEARCH_URL = "https://connect.medlineplus.gov/service"
WHO_API_URL = "https://www.who.int/api/news"

# Agent & Model Settings
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.35

# Application Settings
APP_TITLE = "PulseMind Agentic Healthcare Assistant"
APP_SUBTITLE = "Autonomous Medical Workflow & RAG Intelligence Engine"

# Ensure FAISS index directory exists
os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
