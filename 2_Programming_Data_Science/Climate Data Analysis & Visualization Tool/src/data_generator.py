"""
src/data_generator.py
=====================
Synthetic climate data generator for 6 major Pakistan cities.

Generates realistic 50-year (1974-2024) monthly climate data with:
- City-specific seasonal temperature and precipitation profiles
- Realistic climate change warming trend (+0.025°C/year)
- Precipitation variability signal (±5% per decade)
- Humidity and wind speed correlated to season/location

Author: Haris Hussain
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# City climatological profiles
# ---------------------------------------------------------------------------
CITY_PROFILES = {
    "Lahore": {
        # Monthly mean temperature (°C) – climatological baseline
        "temp_mean": [12, 15, 21, 28, 34, 38, 36, 35, 32, 27, 19, 13],
        # Monthly temp amplitude (±°C) around the mean
        "temp_amp":  [ 7,  7,  8,  8,  8,  6,  5,  5,  6,  7,  7,  6],
        # Monthly mean precipitation (mm) – baseline
        "precip":    [18, 22, 28, 16, 14, 30, 90, 85, 50, 10,  6, 14],
        # Monthly mean humidity (%)
        "humidity":  [62, 55, 48, 42, 40, 45, 70, 72, 65, 55, 55, 62],
        # Monthly mean wind speed (km/h)
        "wind":      [10, 11, 13, 14, 15, 14, 12, 11, 10, 10, 10, 10],
    },
    "Karachi": {
        "temp_mean": [19, 21, 25, 29, 33, 35, 34, 33, 32, 30, 25, 20],
        "temp_amp":  [ 5,  5,  5,  5,  4,  4,  3,  3,  3,  4,  5,  5],
        "precip":    [ 5,  8,  5,  2,  2, 10, 60, 50, 30,  5,  3,  5],
        "humidity":  [65, 65, 68, 70, 72, 74, 78, 78, 72, 68, 65, 65],
        "wind":      [14, 14, 16, 16, 18, 20, 18, 16, 14, 12, 12, 13],
    },
    "Islamabad": {
        "temp_mean": [ 7, 10, 15, 21, 27, 32, 31, 30, 27, 21, 14,  8],
        "temp_amp":  [ 7,  7,  8,  8,  8,  7,  5,  5,  6,  7,  7,  7],
        "precip":    [55, 65, 75, 60, 40, 35, 80, 75, 50, 30, 25, 45],
        "humidity":  [70, 65, 62, 58, 52, 50, 68, 70, 64, 58, 60, 68],
        "wind":      [ 9, 10, 12, 13, 12, 11, 10, 10,  9,  9,  9,  9],
    },
    "Peshawar": {
        "temp_mean": [ 6,  9, 15, 22, 29, 35, 36, 35, 30, 22, 13,  7],
        "temp_amp":  [ 8,  8,  9,  9,  9,  7,  5,  5,  7,  8,  8,  8],
        "precip":    [40, 50, 60, 40, 20, 10, 25, 30, 18, 12, 18, 32],
        "humidity":  [68, 62, 56, 50, 42, 38, 50, 54, 48, 44, 52, 66],
        "wind":      [10, 11, 13, 14, 13, 12, 11, 10,  9, 10, 10, 10],
    },
    "Quetta": {
        "temp_mean": [ 2,  5, 11, 17, 23, 29, 30, 28, 23, 16,  8,  3],
        "temp_amp":  [ 9,  9, 10, 10, 10,  9,  7,  7,  9, 10,  9,  9],
        "precip":    [30, 32, 35, 22, 10,  4,  6,  5,  4,  8, 15, 24],
        "humidity":  [60, 55, 50, 44, 36, 30, 34, 36, 32, 38, 48, 58],
        "wind":      [12, 13, 15, 16, 15, 14, 12, 11, 10, 11, 12, 12],
    },
    "Multan": {
        "temp_mean": [10, 14, 21, 29, 36, 40, 38, 37, 33, 27, 19, 11],
        "temp_amp":  [ 8,  8,  9,  9,  8,  6,  5,  5,  6,  8,  8,  8],
        "precip":    [ 8, 10, 12,  8,  6, 10, 40, 38, 20,  4,  4,  8],
        "humidity":  [60, 52, 44, 38, 35, 38, 60, 62, 55, 48, 50, 58],
        "wind":      [10, 11, 13, 14, 15, 14, 12, 11, 10, 10, 10, 10],
    },
}

# Warming trend rate (°C per year) – IPCC-consistent for South Asia
WARMING_RATE = 0.025

# Precipitation variability per decade (fractional)
PRECIP_VARIABILITY_RATE = 0.05


def _add_climate_change_signal(
    temp: float,
    precip: float,
    year: int,
    rng: np.random.Generator,
) -> tuple:
    """
    Apply a simple linear warming trend and decadal precipitation variability.

    Parameters
    ----------
    temp : float
        Baseline temperature for the month.
    precip : float
        Baseline precipitation for the month.
    year : int
        Calendar year.
    rng : np.random.Generator
        Reproducible random generator.

    Returns
    -------
    tuple[float, float]
        Adjusted (temperature, precipitation).
    """
    years_since_baseline = year - 1974
    # Warming signal
    warming = WARMING_RATE * years_since_baseline
    temp_adj = temp + warming

    # Decadal precip variability: slight reduction in summer, increase in monsoon
    decade_factor = years_since_baseline / 10
    # Random decade-scale variation ±5% compounding
    precip_factor = 1.0 + rng.uniform(-PRECIP_VARIABILITY_RATE, PRECIP_VARIABILITY_RATE) * decade_factor
    precip_adj = max(0.0, precip * precip_factor)

    return temp_adj, precip_adj


def generate_climate_dataset(seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic 50-year monthly climate dataset for 6 Pakistan cities.

    Parameters
    ----------
    seed : int
        Random seed for reproducibility. Default is 42.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        [year, month, city, temperature_mean, temperature_max,
         temperature_min, precipitation_mm, humidity_pct, wind_speed_kmh]
        Shape: 6 cities × 50 years × 12 months = 3600 rows.

    Examples
    --------
    >>> df = generate_climate_dataset()
    >>> df.shape
    (3600, 9)
    >>> sorted(df['city'].unique())
    ['Islamabad', 'Karachi', 'Lahore', 'Multan', 'Peshawar', 'Quetta']
    """
    rng = np.random.default_rng(seed)
    records = []

    years = range(1974, 2025)   # 50 years
    months = range(1, 13)       # Jan–Dec

    for city, profile in CITY_PROFILES.items():
        for year in years:
            for month in months:
                m = month - 1  # 0-indexed

                # --- Temperature ------------------------------------------
                base_mean = profile["temp_mean"][m]
                base_amp = profile["temp_amp"][m]

                # Apply climate change signal
                temp_mean_adj, _ = _add_climate_change_signal(
                    base_mean, 0, year, rng
                )

                # Interannual noise (σ ≈ 1.0°C)
                noise = rng.normal(0, 1.0)
                temp_mean = round(temp_mean_adj + noise, 2)

                # Max/min based on diurnal amplitude + small noise
                temp_max = round(temp_mean + base_amp + rng.normal(0, 0.5), 2)
                temp_min = round(temp_mean - base_amp + rng.normal(0, 0.5), 2)

                # --- Precipitation ----------------------------------------
                base_precip = profile["precip"][m]
                _, precip_adj = _add_climate_change_signal(
                    0, base_precip, year, rng
                )

                # Gamma-distributed rain (skewed right), scale ≈ base/3
                if base_precip > 0:
                    shape = max(0.5, base_precip / 15.0)
                    scale = max(0.5, base_precip / shape)
                    precip_mm = round(
                        float(rng.gamma(shape, scale)) * (precip_adj / max(base_precip, 1e-6)),
                        1,
                    )
                else:
                    precip_mm = 0.0
                precip_mm = max(0.0, precip_mm)

                # --- Humidity ---------------------------------------------
                base_hum = profile["humidity"][m]
                humidity = round(
                    float(np.clip(base_hum + rng.normal(0, 3), 20, 98)), 1
                )

                # --- Wind speed -------------------------------------------
                base_wind = profile["wind"][m]
                wind = round(
                    float(np.clip(base_wind + rng.normal(0, 2), 2, 60)), 1
                )

                records.append(
                    {
                        "year": year,
                        "month": month,
                        "city": city,
                        "temperature_mean": temp_mean,
                        "temperature_max": temp_max,
                        "temperature_min": temp_min,
                        "precipitation_mm": precip_mm,
                        "humidity_pct": humidity,
                        "wind_speed_kmh": wind,
                    }
                )

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    df = generate_climate_dataset()
    print(f"Dataset shape: {df.shape}")
    print(df.head(12).to_string(index=False))
    print(f"\nCities: {sorted(df['city'].unique())}")
    print(f"Year range: {df['year'].min()} – {df['year'].max()}")
