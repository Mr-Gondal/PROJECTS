import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

from src.config import CITIES


def generate_sample_data(
    days: int = 90,
    cities: list[str] = None,
    seed: int = 42
) -> pd.DataFrame:
    """Generate synthetic demo data (clearly labelled as such).

    This is **demo data for portfolio purposes** — pollutant values are
    correlated by construction, so high R² on this dataset is expected and
    must NOT be presented as real-world model skill.
    """
    rng = np.random.default_rng(seed)
    if cities is None:
        cities = CITIES

    base_aqi = {"Lahore": 180, "Karachi": 140, "Islamabad": 80, "Peshawar": 120, "Quetta": 100}
    records = []
    now = datetime.now(timezone.utc)
    season = np.arange(days) * 2 * np.pi / 365.0

    for city in cities:
        for i in range(days):
            ts = now - timedelta(hours=i * 24)
            # Mild seasonal wave + daily noise keeps the synthetic series
            # from being pure white noise around a constant.
            daily_variation = rng.normal(0, 20) + 10 * np.cos(season[days - 1 - i])
            aqi = max(0, base_aqi.get(city, 100) + daily_variation)
            record = {
                "city": city,
                "timestamp": ts,
                "aqi": round(aqi, 1),
                "pm25": round(aqi * 0.6 + rng.normal(0, 5), 1),
                "pm10": round(aqi * 0.8 + rng.normal(0, 8), 1),
                "no2": round(rng.uniform(10, 60), 1),
                "so2": round(rng.uniform(5, 30), 1),
                "co": round(rng.uniform(0.5, 4.0), 2),
                "o3": round(rng.uniform(20, 80), 1),
                "temperature": round(rng.uniform(15, 40), 1),
                "humidity": round(rng.uniform(20, 80), 1),
                "wind_speed": round(rng.uniform(0, 15), 1),
                "pressure": round(rng.uniform(990, 1020), 1),
            }
            records.append(record)

    df = pd.DataFrame(records)
    df.sort_values(["city", "timestamp"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


if __name__ == "__main__":
    df = generate_sample_data()
    path = __import__("src.config", fromlist=[""]).DATA_DIR / "raw" / "aqi_sample.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Generated sample data: {len(df)} rows → {path}")
