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


def ensure_directories(config: dict) -> None:
    for relative_path in config["paths"].values():
        (PROJECT_ROOT / relative_path).mkdir(parents=True, exist_ok=True)


def build_sample_climate_data() -> pd.DataFrame:
    rows = [
        ("Lahore", "Punjab", 2000, "historical", 24.0, 610),
        ("Lahore", "Punjab", 2010, "historical", 24.7, 590),
        ("Lahore", "Punjab", 2020, "historical", 25.5, 560),
        ("Lahore", "Punjab", 2050, "ssp245", 27.2, 525),
        ("Lahore", "Punjab", 2050, "ssp585", 28.4, 500),
        ("Multan", "Punjab", 2000, "historical", 26.1, 240),
        ("Multan", "Punjab", 2010, "historical", 26.8, 225),
        ("Multan", "Punjab", 2020, "historical", 27.6, 210),
        ("Multan", "Punjab", 2050, "ssp245", 29.0, 195),
        ("Multan", "Punjab", 2050, "ssp585", 30.3, 180),
        ("Peshawar", "KPK", 2000, "historical", 21.0, 410),
        ("Peshawar", "KPK", 2010, "historical", 21.8, 395),
        ("Peshawar", "KPK", 2020, "historical", 22.5, 380),
        ("Peshawar", "KPK", 2050, "ssp245", 24.5, 360),
        ("Peshawar", "KPK", 2050, "ssp585", 25.8, 340),
        ("Hyderabad", "Sindh", 2000, "historical", 27.5, 180),
        ("Hyderabad", "Sindh", 2010, "historical", 28.1, 170),
        ("Hyderabad", "Sindh", 2020, "historical", 28.8, 155),
        ("Hyderabad", "Sindh", 2050, "ssp245", 30.2, 145),
        ("Hyderabad", "Sindh", 2050, "ssp585", 31.6, 130),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "district",
            "province",
            "year",
            "scenario",
            "temperature_c",
            "precipitation_mm",
        ],
    )


def write_sample_input(config: dict, force: bool) -> Path:
    sample_path = PROJECT_ROOT / config["inputs"]["district_climate_csv"]
    if sample_path.exists() and not force:
        return sample_path

    sample_path.parent.mkdir(parents=True, exist_ok=True)
    build_sample_climate_data().to_csv(sample_path, index=False)
    return sample_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap the climate agriculture project folders and sample input data."
    )
    parser.add_argument(
        "--force-sample",
        action="store_true",
        help="Overwrite the sample district climate CSV if it already exists.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    ensure_directories(config)
    sample_path = write_sample_input(config, force=args.force_sample)
    print(f"Project structure is ready.")
    print(f"Sample climate dataset available at: {sample_path}")
    print("Replace the sample CSV with WorldClim, CMIP6, or district-level aggregates when ready.")


if __name__ == "__main__":
    main()
