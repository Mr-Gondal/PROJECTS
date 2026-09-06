import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from src.config import OWM_API_URL, OWM_API_TOKEN, CITIES, CITY_COORDS, DATA_DIR
from src.aqi_scale import pm25_to_aqi, pm10_to_aqi


class AirQualityCollector:
    """Fetch current air-pollution data from the OpenWeatherMap API.

    Note: AQI conversion lives in ``src/aqi_scale.py`` (US EPA 2024
    breakpoints, truncation-based — no band-gap fall-through).
    Timestamps are stored as timezone-aware UTC so results do not depend
    on the machine's local timezone.
    """

    def __init__(self, token: str = OWM_API_TOKEN):
        if not token:
            raise ValueError(
                "OpenWeatherMap API token is missing. Set the OWM_API_TOKEN "
                "environment variable (or Streamlit secret) or pass token=... "
                "explicitly. Get a free key: https://openweathermap.org/api"
            )
        self.token = token
        self.session = requests.Session()

    def fetch_city_data(self, city: str) -> dict:
        lat, lon = CITY_COORDS[city]
        resp = self.session.get(
            OWM_API_URL,
            params={"lat": lat, "lon": lon, "appid": self.token},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if "list" not in data or not data["list"]:
            raise ValueError(f"Empty response for {city}")
        return data["list"][0]

    def parse_response(self, raw: dict, city: str) -> dict:
        main = raw.get("main", {})
        comp = raw.get("components", {})

        pm25 = comp.get("pm2_5")
        pm10 = comp.get("pm10")
        # US EPA AQI from PM2.5 (primary), fall back to PM10 if PM2.5 missing
        us_aqi = pm25_to_aqi(pm25)
        if us_aqi is None:
            us_aqi = pm10_to_aqi(pm10)

        dt = raw.get("dt")
        timestamp = (
            datetime.fromtimestamp(int(dt), tz=timezone.utc)
            if dt
            else datetime.now(timezone.utc)
        )

        return {
            "city": city,
            "timestamp": timestamp,
            "aqi": us_aqi,
            "pm25": pm25,
            "pm10": pm10,
            "no2": comp.get("no2"),
            "so2": comp.get("so2"),
            "co": comp.get("co"),
            "o3": comp.get("o3"),
        }

    def collect_cities_current(self, cities: list[str] = None) -> pd.DataFrame:
        if cities is None:
            cities = CITIES
        records = []
        for city in cities:
            try:
                raw = self.fetch_city_data(city)
                records.append(self.parse_response(raw, city))
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
