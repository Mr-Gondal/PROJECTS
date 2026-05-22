import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.config import CITIES


def generate_sample_data(
    days: int = 90,
    cities: list[str] = None,
    seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)
    if cities is None:
        cities = CITIES

    base_aqi = {"Lahore": 180, "Karachi": 140, "Islamabad": 80, "Peshawar": 120, "Quetta": 100}
    records = []
    now = datetime.now()

    for city in cities:
        for i in range(days):
            ts = now - timedelta(hours=i * 24)
            daily_variation = np.random.normal(0, 20)
            aqi = max(0, base_aqi.get(city, 100) + daily_variation)
            record = {
                "city": city,
                "timestamp": ts,
                "aqi": round(aqi, 1),
                "pm25": round(aqi * 0.6 + np.random.normal(0, 5), 1),
                "pm10": round(aqi * 0.8 + np.random.normal(0, 8), 1),
                "no2": round(np.random.uniform(10, 60), 1),
                "so2": round(np.random.uniform(5, 30), 1),
                "co": round(np.random.uniform(0.5, 4.0), 2),
                "o3": round(np.random.uniform(20, 80), 1),
                "temperature": round(np.random.uniform(15, 40), 1),
                "humidity": round(np.random.uniform(20, 80), 1),
                "wind_speed": round(np.random.uniform(0, 15), 1),
                "pressure": round(np.random.uniform(990, 1020), 1),
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
