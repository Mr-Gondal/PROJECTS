#!/usr/bin/env python3
"""
Air Quality Analysis & Prediction Model
Analyze air quality data from Pakistan cities, identify trends,
and build prediction models using machine learning.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from src.config import CITIES, FIGURES_DIR, MODELS_DIR, DATA_DIR
from src.data_collector import AirQualityCollector
from src.analyzer import AirQualityAnalyzer
from src.model import AirQualityPredictor, train_all_models


def parse_args():
    parser = argparse.ArgumentParser(description="Air Quality Analysis & Prediction Pipeline")
    parser.add_argument("--fetch", action="store_true", help="Fetch fresh AQI data from API")
    parser.add_argument("--input", type=str, help="Path to input CSV data file")
    parser.add_argument("--analyze", action="store_true", help="Run analysis and generate visualizations")
    parser.add_argument("--train", action="store_true", help="Train ML prediction models")
    parser.add_argument("--target", type=str, default="pm25", choices=["pm25", "pm10", "no2", "so2", "co", "o3"])
    parser.add_argument("--predict", type=str, help="Run prediction on a new CSV file")
    parser.add_argument("--all", action="store_true", help="Run full pipeline: fetch → analyze → train")
    return parser.parse_args()


def run_fetch() -> pd.DataFrame:
    print("[1/3] Fetching AQI data for Pakistan cities...")
    collector = AirQualityCollector()
    df = collector.collect_cities_current(CITIES)
    path = collector.save_raw(df)
    print(f"      Saved {len(df)} records to {path}")
    return df


def run_analysis(df: pd.DataFrame):
    print("[2/3] Running analysis and generating visualizations...")
    analyzer = AirQualityAnalyzer(df)
    stats = analyzer.summary_stats()
    print("\nSummary Statistics:\n", stats)

    report = analyzer.generate_report()
    print(f"\nRecords: {report['record_count']}")
    print(f"Cities:  {report['cities']}")
    print(f"Date range: {report['date_range'][0]} to {report['date_range'][1]}")

    analyzer.plot_correlation_heatmap(save=True)
    analyzer.plot_pollutant_composition(save=True)
    analyzer.plot_aqi_trends(save=True)
    for city in df["city"].unique():
        analyzer.plot_aqi_trends(city=city, save=True)
    print(f"      Figures saved to {FIGURES_DIR}")


def run_training(df: pd.DataFrame, target: str = "pm25"):
    print(f"[3/3] Training models to predict '{target}'...")
    results = train_all_models(df, target=target)
    for name, metrics in results.items():
        print(f"\n  {name}:")
        for key, val in metrics.items():
            print(f"    {key}: {val:.4f}")


def run_prediction(input_path: str, model_path: str = None):
    print("Running prediction on new data...")
    df = pd.read_csv(input_path)
    if model_path is None:
        model_path = MODELS_DIR / "aqi_predictor_random_forest.joblib"
    predictor = AirQualityPredictor()
    predictor.load(str(model_path))
    X, _ = predictor.prepare_features(df, target="pm25")
    preds = predictor.predict(X)
    df["predicted_pm25"] = preds
    out_path = Path(input_path).stem + "_predicted.csv"
    df.to_csv(out_path, index=False)
    print(f"Predictions saved to {out_path}")


def main():
    args = parse_args()

    if args.all:
        df = run_fetch()
        run_analysis(df)
        run_training(df, args.target)
        return

    if args.fetch:
        df = run_fetch()
    elif args.input:
        df = pd.read_csv(args.input, parse_dates=["timestamp"])
    else:
        print("No data source specified. Use --fetch or --input.")
        sys.exit(1)

    if args.analyze:
        run_analysis(df)
    if args.train:
        run_training(df, args.target)
    if args.predict:
        run_prediction(args.predict)

    print("\nDone.")


if __name__ == "__main__":
    main()
