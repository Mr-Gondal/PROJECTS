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

CITIES = ["Lahore", "Karachi", "Islamabad", "Peshawar", "Quetta"]

CITY_COORDS = {
    "Lahore":    (31.5204, 74.3587),
    "Karachi":   (24.8607, 67.0011),
    "Islamabad": (33.6844, 73.0479),
    "Peshawar":  (34.0151, 71.5249),
    "Quetta":    (30.1798, 66.9750),
}

OWM_API_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

def get_api_token() -> str:
    token = os.getenv("OWM_API_TOKEN", "")
    if not token:
        try:
            import streamlit as st
            token = st.secrets.get("OWM_API_TOKEN", "")
        except Exception:
            pass
    return token

OWM_API_TOKEN = get_api_token()

TARGET_POLLUTANTS = ["pm25", "pm10", "no2", "so2", "co", "o3"]

TRAIN_TEST_SPLIT = 0.8
RANDOM_STATE = 42
