import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
FIGURES_DIR = BASE_DIR / "figures"

CITIES = ["Lahore", "Karachi", "Islamabad", "Peshawar", "Quetta"]
AQI_API_BASE_URL = "https://api.waqi.info/feed/{city}/"
AQI_API_TOKEN = os.getenv("AQI_API_TOKEN", "")

TARGET_POLLUTANTS = ["pm25", "pm10", "no2", "so2", "co", "o3"]

TRAIN_TEST_SPLIT = 0.8
RANDOM_STATE = 42
