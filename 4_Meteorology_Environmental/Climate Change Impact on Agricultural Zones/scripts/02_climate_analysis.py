from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml
from scipy.stats import linregress


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.yaml"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_climate_data(config: dict) -> pd.DataFrame:
    csv_path = PROJECT_ROOT / config["inputs"]["district_climate_csv"]
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Missing input climate CSV: {csv_path}. Run scripts/01_data_download.py first."
        )
    data = pd.read_csv(csv_path)
    required = {
        "district",
        "province",
        "year",
        "scenario",
        "temperature_c",
        "precipitation_mm",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {sorted(missing)}")
    return data


def compute_baseline_means(data: pd.DataFrame, baseline_start: int, baseline_end: int) -> pd.DataFrame:
    baseline = data[(data["year"] >= baseline_start) & (data["year"] <= baseline_end)].copy()
    baseline = baseline[baseline["scenario"] == "historical"]
    if baseline.empty:
        raise ValueError("No historical observations fall within the configured baseline period.")

    return (
        baseline.groupby(["district", "province"], as_index=False)[
            ["temperature_c", "precipitation_mm"]
        ]
        .mean()
        .rename(
            columns={
                "temperature_c": "baseline_temperature_c",
                "precipitation_mm": "baseline_precipitation_mm",
            }
        )
    )


def compute_anomalies(data: pd.DataFrame, baseline_means: pd.DataFrame) -> pd.DataFrame:
    enriched = data.merge(baseline_means, on=["district", "province"], how="left")
    enriched["temperature_anomaly_c"] = (
        enriched["temperature_c"] - enriched["baseline_temperature_c"]
    )
    enriched["precipitation_anomaly_mm"] = (
        enriched["precipitation_mm"] - enriched["baseline_precipitation_mm"]
    )
    return enriched


def compute_trends(data: pd.DataFrame) -> pd.DataFrame:
    historical = data[data["scenario"] == "historical"].copy()
    trend_rows: list[dict] = []

    for (district, province), group in historical.groupby(["district", "province"]):
        if group["year"].nunique() < 2:
            continue

        temp_fit = linregress(group["year"], group["temperature_c"])
        precip_fit = linregress(group["year"], group["precipitation_mm"])
        trend_rows.append(
            {
                "district": district,
                "province": province,
                "temperature_slope_c_per_year": temp_fit.slope,
                "temperature_rvalue": temp_fit.rvalue,
                "precipitation_slope_mm_per_year": precip_fit.slope,
                "precipitation_rvalue": precip_fit.rvalue,
            }
        )

    return pd.DataFrame(trend_rows)


def save_outputs(config: dict, anomalies: pd.DataFrame, trends: pd.DataFrame) -> tuple[Path, Path]:
    processed_dir = PROJECT_ROOT / config["paths"]["processed_data_dir"]
    processed_dir.mkdir(parents=True, exist_ok=True)
    anomalies_path = processed_dir / "climate_anomalies.csv"
    trends_path = processed_dir / "district_climate_trends.csv"
    anomalies.to_csv(anomalies_path, index=False)
    trends.to_csv(trends_path, index=False)
    return anomalies_path, trends_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute district-level baseline means, anomalies, and climate trends."
    )
    return parser.parse_args()


def main() -> None:
    _ = parse_args()
    config = load_config()
    baseline_start, baseline_end = config["project"]["baseline_years"]
    climate_data = load_climate_data(config)
    baseline_means = compute_baseline_means(climate_data, baseline_start, baseline_end)
    anomalies = compute_anomalies(climate_data, baseline_means)
    trends = compute_trends(climate_data)
    anomalies_path, trends_path = save_outputs(config, anomalies, trends)
    print(f"Saved anomalies to: {anomalies_path}")
    print(f"Saved climate trends to: {trends_path}")


if __name__ == "__main__":
    main()
