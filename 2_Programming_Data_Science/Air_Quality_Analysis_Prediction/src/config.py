import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
FIGURES_DIR = BASE_DIR / "figures"

CITIES = ["Lahore", "Karachi", "Islamabad", "Peshawar"]
AQI_API_BASE_URL = "https://api.waqi.info/feed/{city}/"

def get_api_token() -> str:
    token = os.getenv("AQI_API_TOKEN", "")
    if not token:
        try:
            import streamlit as st
            token = st.secrets.get("AQI_API_TOKEN", "")
        except Exception:
            pass
    return token

AQI_API_TOKEN = get_api_token()

TARGET_POLLUTANTS = ["pm25", "pm10", "no2", "so2", "co", "o3"]

TRAIN_TEST_SPLIT = 0.8
RANDOM_STATE = 42
