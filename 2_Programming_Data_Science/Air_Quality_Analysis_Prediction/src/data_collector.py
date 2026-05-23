import requests
import pandas as pd
import numpy as np
from datetime import datetime
from src.config import OWM_API_URL, OWM_API_TOKEN, CITIES, CITY_COORDS, DATA_DIR


def _pm25_to_aqi(pm25: float) -> int:
    if pm25 is None or np.isnan(pm25):
        return None
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]
    for clo, chi, aqi_lo, aqi_hi in breakpoints:
        if clo <= pm25 <= chi:
            return round(((aqi_hi - aqi_lo) / (chi - clo)) * (pm25 - clo) + aqi_lo)
    return 500 if pm25 > 500 else 0


def _pm10_to_aqi(pm10: float) -> int:
    if pm10 is None or np.isnan(pm10):
        return None
    breakpoints = [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500),
    ]
    for clo, chi, aqi_lo, aqi_hi in breakpoints:
        if clo <= pm10 <= chi:
            return round(((aqi_hi - aqi_lo) / (chi - clo)) * (pm10 - clo) + aqi_lo)
    return 500 if pm10 > 604 else 0


class AirQualityCollector:
    def __init__(self, token: str = OWM_API_TOKEN):
        self.token = token
        self.session = requests.Session()

    def fetch_city_data(self, city: str) -> dict:
        lat, lon = CITY_COORDS[city]
        resp = self.session.get(OWM_API_URL, params={"lat": lat, "lon": lon, "appid": self.token})
        resp.raise_for_status()
        data = resp.json()
        if "list" not in data or not data["list"]:
            raise ValueError(f"Empty response for {city}")
        return data["list"][0]

    def parse_response(self, raw: dict, city: str) -> dict:
        main = raw.get("main", {})
        comp = raw.get("components", {})

        owm_aqi = main.get("aqi")
        pm25 = comp.get("pm2_5")
        pm10 = comp.get("pm10")
        us_aqi = _pm25_to_aqi(pm25)
        if us_aqi is None:
            us_aqi = _pm10_to_aqi(pm10)

        record = {
            "city": city,
            "timestamp": datetime.fromtimestamp(raw.get("dt", 0)),
            "aqi": us_aqi,
            "pm25": pm25,
            "pm10": pm10,
            "no2": comp.get("no2"),
            "so2": comp.get("so2"),
            "co": comp.get("co"),
            "o3": comp.get("o3"),
        }
        return record

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
