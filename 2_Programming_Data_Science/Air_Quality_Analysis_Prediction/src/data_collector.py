import requests
import pandas as pd
from datetime import datetime, timedelta
from src.config import AQI_API_BASE_URL, AQI_API_TOKEN, CITIES, DATA_DIR
import json
from pathlib import Path


class AirQualityCollector:
    def __init__(self, token: str = AQI_API_TOKEN):
        self.token = token
        self.session = requests.Session()

    def fetch_current_aqi(self, city: str) -> dict:
        url = AQI_API_BASE_URL.format(city=city)
        params = {"token": self.token}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            raise ValueError(f"API error for {city}: {data}")
        return data["data"]

    def parse_aqi_response(self, raw: dict, city: str) -> dict:
        iaqi = raw.get("iaqi", {})
        time_raw = raw.get("time", {})
        ts = time_raw.get("s") or time_raw.get("iso")
        if isinstance(ts, str):
            timestamp = pd.to_datetime(ts)
        else:
            timestamp = pd.Timestamp.now()
        record = {
            "city": city,
            "timestamp": timestamp,
            "aqi": raw.get("aqi"),
        }
        for pollutant in ["pm25", "pm10", "no2", "so2", "co", "o3"]:
            info = iaqi.get(pollutant, {})
            record[pollutant] = info.get("v") if isinstance(info, dict) else None
        return record

    def collect_cities_current(self, cities: list[str] = None) -> pd.DataFrame:
        if cities is None:
            cities = CITIES
        records = []
        for city in cities:
            try:
                raw = self.fetch_current_aqi(city)
                records.append(self.parse_aqi_response(raw, city))
            except Exception as e:
                print(f"Failed to fetch {city}: {e}")
        return pd.DataFrame(records)

    def save_raw(self, df: pd.DataFrame, filename: str = "aqi_current.csv"):
        path = DATA_DIR / "raw" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path

    def load_local_data(self, filepath: str) -> pd.DataFrame:
        return pd.read_csv(filepath, parse_dates=["timestamp"])


class MeteorologicalCollector:
    """Placeholder — would integrate with OpenWeatherMap or similar API."""

    def fetch_weather(self, city: str) -> dict:
        return {"city": city, "temperature": None, "humidity": None, "wind_speed": None, "pressure": None}


class TrafficCollector:
    """Placeholder — would integrate with traffic data APIs."""

    def fetch_traffic(self, city: str) -> dict:
        return {"city": city, "traffic_index": None}
