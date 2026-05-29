from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml


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
    return pd.read_csv(csv_path)


def range_score(value: float, optimal: list[float], marginal: list[float]) -> float:
    optimal_low, optimal_high = optimal
    marginal_low, marginal_high = marginal

    if optimal_low <= value <= optimal_high:
        return 1.0
    if value < marginal_low or value > marginal_high:
        return 0.0
    if value < optimal_low:
        return (value - marginal_low) / (optimal_low - marginal_low)
    return (marginal_high - value) / (marginal_high - optimal_high)


def classify_score(score: float) -> str:
    if score >= 0.8:
        return "High"
    if score >= 0.55:
        return "Moderate"
    if score >= 0.3:
        return "Marginal"
    return "Unsuitable"


def evaluate_crop_suitability(config: dict, data: pd.DataFrame, scenario: str, year: int) -> pd.DataFrame:
    selected = data[(data["scenario"] == scenario) & (data["year"] == year)].copy()
    if selected.empty:
        raise ValueError(f"No rows found for scenario={scenario!r} and year={year}.")

    weights = config["weights"]
    results: list[dict] = []
    for _, row in selected.iterrows():
        for crop_name, crop_config in config["crops"].items():
            temperature_score = range_score(
                row["temperature_c"],
                crop_config["optimal_temp_c"],
                crop_config["marginal_temp_c"],
            )
            precipitation_score = range_score(
                row["precipitation_mm"],
                crop_config["optimal_precip_mm"],
                crop_config["marginal_precip_mm"],
            )
            suitability_score = (
                weights["temperature"] * temperature_score
                + weights["precipitation"] * precipitation_score
            )
            results.append(
                {
                    "district": row["district"],
                    "province": row["province"],
                    "scenario": scenario,
                    "year": year,
                    "crop": crop_name,
                    "temperature_c": row["temperature_c"],
                    "precipitation_mm": row["precipitation_mm"],
                    "temperature_score": round(temperature_score, 3),
                    "precipitation_score": round(precipitation_score, 3),
                    "suitability_score": round(suitability_score, 3),
                    "suitability_class": classify_score(suitability_score),
                }
            )

    return pd.DataFrame(results)


def save_outputs(config: dict, results: pd.DataFrame, scenario: str, year: int) -> Path:
    processed_dir = PROJECT_ROOT / config["paths"]["processed_data_dir"]
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / f"crop_suitability_{scenario}_{year}.csv"
    results.to_csv(output_path, index=False)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate crop suitability from district climate projections."
    )
    parser.add_argument("--scenario", default="ssp245", help="Climate scenario to evaluate.")
    parser.add_argument("--year", default=2050, type=int, help="Projection year to evaluate.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    climate_data = load_climate_data(config)
    results = evaluate_crop_suitability(config, climate_data, args.scenario, args.year)
    output_path = save_outputs(config, results, args.scenario, args.year)
    print(f"Saved crop suitability results to: {output_path}")


if __name__ == "__main__":
    main()
