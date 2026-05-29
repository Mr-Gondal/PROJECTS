from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "project_config.yaml"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate starter visual outputs for climate trends and crop suitability."
    )
    parser.add_argument("--scenario", default="ssp245", help="Scenario used in suitability results.")
    parser.add_argument("--year", default=2050, type=int, help="Year used in suitability results.")
    return parser.parse_args()


def ensure_output_dir(config: dict) -> Path:
    figure_dir = PROJECT_ROOT / config["paths"]["figure_dir"]
    figure_dir.mkdir(parents=True, exist_ok=True)
    return figure_dir


def plot_temperature_trends(processed_dir: Path, figure_dir: Path) -> Path:
    trends_path = processed_dir / "district_climate_trends.csv"
    if not trends_path.exists():
        raise FileNotFoundError(
            f"Missing trends file: {trends_path}. Run scripts/02_climate_analysis.py first."
        )

    trends = pd.read_csv(trends_path).sort_values("temperature_slope_c_per_year", ascending=False)
    plt.figure(figsize=(10, 6))
    plt.bar(trends["district"], trends["temperature_slope_c_per_year"], color="#c0392b")
    plt.title("Historical Temperature Trend by District")
    plt.ylabel("Slope (C per year)")
    plt.xlabel("District")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    output_path = figure_dir / "temperature_trend_by_district.png"
    plt.savefig(output_path, dpi=200)
    plt.close()
    return output_path


def plot_crop_heatmap(processed_dir: Path, figure_dir: Path, scenario: str, year: int) -> Path:
    suitability_path = processed_dir / f"crop_suitability_{scenario}_{year}.csv"
    if not suitability_path.exists():
        raise FileNotFoundError(
            f"Missing suitability file: {suitability_path}. Run scripts/03_crop_suitability.py first."
        )

    suitability = pd.read_csv(suitability_path)
    heatmap_data = suitability.pivot(index="district", columns="crop", values="suitability_score")

    plt.figure(figsize=(8, 5))
    image = plt.imshow(heatmap_data, cmap="YlGn", vmin=0, vmax=1, aspect="auto")
    plt.colorbar(image, label="Suitability Score")
    plt.title(f"Crop Suitability Scores ({scenario}, {year})")
    plt.xticks(range(len(heatmap_data.columns)), heatmap_data.columns)
    plt.yticks(range(len(heatmap_data.index)), heatmap_data.index)
    plt.tight_layout()

    output_path = figure_dir / f"crop_suitability_heatmap_{scenario}_{year}.png"
    plt.savefig(output_path, dpi=200)
    plt.close()
    return output_path


def main() -> None:
    args = parse_args()
    config = load_config()
    processed_dir = PROJECT_ROOT / config["paths"]["processed_data_dir"]
    figure_dir = ensure_output_dir(config)

    trend_path = plot_temperature_trends(processed_dir, figure_dir)
    heatmap_path = plot_crop_heatmap(processed_dir, figure_dir, args.scenario, args.year)
    print(f"Saved trend figure to: {trend_path}")
    print(f"Saved suitability figure to: {heatmap_path}")


if __name__ == "__main__":
    main()
