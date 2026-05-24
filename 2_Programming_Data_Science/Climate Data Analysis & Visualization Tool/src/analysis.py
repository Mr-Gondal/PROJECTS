"""
src/analysis.py
===============
Statistical analysis functions for Pakistan climate data.

Includes:
- Annual trend computation with linear regression slope
- Temperature and precipitation anomaly detection
- Seasonal aggregation by decade
- Climate stripes data preparation
- SPI-like drought index computation

All functions accept a pandas DataFrame as produced by
``src.data_generator.generate_climate_dataset()``.

Author: Haris Hussain
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Season mapping (meteorological)
# ---------------------------------------------------------------------------
SEASON_MAP = {
    12: "Winter",
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Monsoon",
    10: "Monsoon",
    11: "Monsoon",
}

# Baseline period for anomaly calculations
BASELINE_START = 1974
BASELINE_END = 2004


def _assign_season(month: int) -> str:
    """Return season label for a given month number (1–12)."""
    return SEASON_MAP[month]


def _assign_decade(year: int) -> str:
    """Return decade label, e.g. 2010 → '2010s'."""
    return f"{(year // 10) * 10}s"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_annual_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute annual average temperature and precipitation per city,
    plus a warming trend slope (°C per decade) from linear regression.

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame from ``generate_climate_dataset()``.

    Returns
    -------
    pd.DataFrame
        Columns: [year, city, temp_avg, temp_max_avg, temp_min_avg,
                  precip_total, humidity_avg, wind_avg,
                  temp_trend_per_decade]
    """
    # Annual aggregation
    annual = (
        df.groupby(["year", "city"])
        .agg(
            temp_avg=("temperature_mean", "mean"),
            temp_max_avg=("temperature_max", "mean"),
            temp_min_avg=("temperature_min", "mean"),
            precip_total=("precipitation_mm", "sum"),
            humidity_avg=("humidity_pct", "mean"),
            wind_avg=("wind_speed_kmh", "mean"),
        )
        .reset_index()
    )

    # Per-city trend slope via scipy.stats.linregress
    trend_rows = []
    for city, grp in annual.groupby("city"):
        grp_sorted = grp.sort_values("year")
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            grp_sorted["year"], grp_sorted["temp_avg"]
        )
        # slope is °C/year → convert to °C/decade
        trend_rows.append(
            {
                "city": city,
                "temp_trend_per_decade": round(slope * 10, 4),
                "trend_r2": round(r_value**2, 4),
                "trend_p_value": round(p_value, 6),
                "trend_slope_per_year": round(slope, 6),
            }
        )

    trend_df = pd.DataFrame(trend_rows)
    annual = annual.merge(trend_df, on="city", how="left")
    annual[["temp_avg", "temp_max_avg", "temp_min_avg", "humidity_avg", "wind_avg"]] = (
        annual[["temp_avg", "temp_max_avg", "temp_min_avg", "humidity_avg", "wind_avg"]]
        .round(2)
    )
    annual["precip_total"] = annual["precip_total"].round(1)
    return annual


def detect_anomalies(df: pd.DataFrame, threshold: float = 1.5) -> pd.DataFrame:
    """
    Flag monthly records where temperature or precipitation deviates
    more than ``threshold`` standard deviations from the 30-year
    baseline (1974–2004).

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame.
    threshold : float
        Number of standard deviations beyond which a value is anomalous.
        Default is 1.5.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with additional columns:
        [is_temp_anomaly, is_precip_anomaly,
         temp_anomaly_magnitude, precip_anomaly_magnitude]
    """
    result = df.copy()
    result["is_temp_anomaly"] = False
    result["is_precip_anomaly"] = False
    result["temp_anomaly_magnitude"] = 0.0
    result["precip_anomaly_magnitude"] = 0.0

    baseline_mask = (df["year"] >= BASELINE_START) & (df["year"] <= BASELINE_END)

    for city in df["city"].unique():
        for month in range(1, 13):
            mask = (df["city"] == city) & (df["month"] == month)
            base_mask = mask & baseline_mask

            # Baseline stats
            base_temp = df.loc[base_mask, "temperature_mean"]
            base_precip = df.loc[base_mask, "precipitation_mm"]

            temp_mean_base = base_temp.mean()
            temp_std_base = base_temp.std(ddof=1)
            precip_mean_base = base_precip.mean()
            precip_std_base = base_precip.std(ddof=1)

            # Avoid division by zero
            if temp_std_base < 1e-6:
                temp_std_base = 1e-6
            if precip_std_base < 1e-6:
                precip_std_base = 1e-6

            # Z-scores
            temp_z = (df.loc[mask, "temperature_mean"] - temp_mean_base) / temp_std_base
            precip_z = (df.loc[mask, "precipitation_mm"] - precip_mean_base) / precip_std_base

            result.loc[mask, "temp_anomaly_magnitude"] = temp_z.round(3)
            result.loc[mask, "precip_anomaly_magnitude"] = precip_z.round(3)
            result.loc[mask, "is_temp_anomaly"] = temp_z.abs() > threshold
            result.loc[mask, "is_precip_anomaly"] = precip_z.abs() > threshold

    return result


def compute_seasonal_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate climate statistics by season, city, and decade.

    Seasons follow meteorological convention:
    - Winter : Dec, Jan, Feb
    - Spring : Mar, Apr, May
    - Summer : Jun, Jul, Aug
    - Monsoon: Sep, Oct, Nov

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: [city, decade, season, temp_avg, precip_total,
                  humidity_avg, wind_avg, record_count]
    """
    work = df.copy()
    work["season"] = work["month"].map(_assign_season)
    work["decade"] = work["year"].map(_assign_decade)

    seasonal = (
        work.groupby(["city", "decade", "season"])
        .agg(
            temp_avg=("temperature_mean", "mean"),
            precip_total=("precipitation_mm", "sum"),
            humidity_avg=("humidity_pct", "mean"),
            wind_avg=("wind_speed_kmh", "mean"),
            record_count=("temperature_mean", "count"),
        )
        .reset_index()
    )

    seasonal[["temp_avg", "humidity_avg", "wind_avg"]] = (
        seasonal[["temp_avg", "humidity_avg", "wind_avg"]].round(2)
    )
    seasonal["precip_total"] = seasonal["precip_total"].round(1)
    return seasonal


def compute_climate_stripes_data(df: pd.DataFrame, city: str) -> pd.DataFrame:
    """
    Compute annual mean temperature anomaly relative to the
    1974–2004 baseline for a single city — used for Warming Stripes.

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame.
    city : str
        City name (must exist in df['city']).

    Returns
    -------
    pd.DataFrame
        Columns: [year, temp_avg, temp_anomaly]
        Sorted by year ascending.
    """
    city_df = df[df["city"] == city].copy()

    # Annual mean temperature
    annual = (
        city_df.groupby("year")["temperature_mean"]
        .mean()
        .reset_index()
        .rename(columns={"temperature_mean": "temp_avg"})
    )

    # Baseline stats
    base_mask = (annual["year"] >= BASELINE_START) & (annual["year"] <= BASELINE_END)
    baseline_mean = annual.loc[base_mask, "temp_avg"].mean()

    annual["temp_anomaly"] = (annual["temp_avg"] - baseline_mean).round(3)
    return annual.sort_values("year").reset_index(drop=True)


def compute_drought_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a simplified SPI-like standardized drought index for each
    city × month combination across all years.

    The index standardizes monthly precipitation relative to the full
    record, so positive values indicate wetter-than-average months and
    negative values indicate drier-than-average months.

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame.

    Returns
    -------
    pd.DataFrame
        Input DataFrame columns plus:
        [spi, drought_category]
        where drought_category ∈ {Extreme Drought, Severe Drought,
        Moderate Drought, Near Normal, Moderately Wet,
        Very Wet, Extremely Wet}
    """
    result = df.copy()
    result["spi"] = 0.0

    for city in df["city"].unique():
        for month in range(1, 13):
            mask = (df["city"] == city) & (df["month"] == month)
            precip_vals = df.loc[mask, "precipitation_mm"]

            mean_p = precip_vals.mean()
            std_p = precip_vals.std(ddof=1)

            if std_p < 1e-6:
                result.loc[mask, "spi"] = 0.0
            else:
                result.loc[mask, "spi"] = ((precip_vals - mean_p) / std_p).round(3)

    def _categorize(spi: float) -> str:
        if spi <= -2.0:
            return "Extreme Drought"
        elif spi <= -1.5:
            return "Severe Drought"
        elif spi <= -1.0:
            return "Moderate Drought"
        elif spi < 1.0:
            return "Near Normal"
        elif spi < 1.5:
            return "Moderately Wet"
        elif spi < 2.0:
            return "Very Wet"
        else:
            return "Extremely Wet"

    result["drought_category"] = result["spi"].apply(_categorize)
    return result


def get_trend_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a clean summary table of temperature trend statistics for all cities.

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: [city, slope_per_year, slope_per_decade, r_squared,
                  p_value, significant]
    """
    records = []
    for city in df["city"].unique():
        city_annual = (
            df[df["city"] == city]
            .groupby("year")["temperature_mean"]
            .mean()
            .reset_index()
        )
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            city_annual["year"], city_annual["temperature_mean"]
        )
        records.append(
            {
                "city": city,
                "slope_per_year": round(slope, 5),
                "slope_per_decade": round(slope * 10, 4),
                "r_squared": round(r_value**2, 4),
                "p_value": round(p_value, 6),
                "significant": p_value < 0.05,
            }
        )
    return pd.DataFrame(records).sort_values("slope_per_decade", ascending=False).reset_index(drop=True)


def project_temperatures(annual_df: pd.DataFrame, target_year: int = 2035) -> pd.DataFrame:
    """
    Linearly project mean annual temperatures to a future year for all cities.

    Parameters
    ----------
    annual_df : pd.DataFrame
        Annual trends DataFrame from ``compute_annual_trends()``.
    target_year : int
        Year to project to. Default is 2035.

    Returns
    -------
    pd.DataFrame
        Columns: [city, projected_temp, current_temp_2024, warming_delta]
    """
    records = []
    for city, grp in annual_df.groupby("city"):
        grp_s = grp.sort_values("year")
        slope, intercept, *_ = stats.linregress(grp_s["year"], grp_s["temp_avg"])
        proj_temp = round(slope * target_year + intercept, 2)
        current = grp_s[grp_s["year"] == grp_s["year"].max()]["temp_avg"].values[0]
        records.append(
            {
                "city": city,
                f"projected_temp_{target_year}": proj_temp,
                "current_temp_2024": round(current, 2),
                "warming_delta": round(proj_temp - current, 2),
            }
        )
    return pd.DataFrame(records).sort_values("warming_delta", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    from src.data_generator import generate_climate_dataset

    df = generate_climate_dataset()
    print("=== Annual Trends (first 12 rows) ===")
    annual = compute_annual_trends(df)
    print(annual.head(12).to_string(index=False))

    print("\n=== Trend Statistics ===")
    print(get_trend_statistics(df).to_string(index=False))

    print("\n=== Climate Stripes – Lahore (first 10) ===")
    print(compute_climate_stripes_data(df, "Lahore").head(10).to_string(index=False))

    print("\n=== Drought Index – Karachi (first 12) ===")
    drt = compute_drought_index(df)
    print(drt[drt["city"] == "Karachi"].head(12)[["year", "month", "precipitation_mm", "spi", "drought_category"]].to_string(index=False))
