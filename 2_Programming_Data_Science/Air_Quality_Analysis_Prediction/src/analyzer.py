import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.config import FIGURES_DIR, CITIES, TARGET_POLLUTANTS
from pathlib import Path


class AirQualityAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare()

    def _prepare(self):
        if "timestamp" in self.df.columns:
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
            self.df.set_index("timestamp", inplace=True)

    def summary_stats(self) -> pd.DataFrame:
        cols = [c for c in TARGET_POLLUTANTS if c in self.df.columns]
        return self.df[cols + ["aqi"]].describe()

    def correlation_matrix(self) -> pd.DataFrame:
        cols = [c for c in TARGET_POLLUTANTS if c in self.df.columns]
        return self.df[cols].corr()

    def plot_correlation_heatmap(self, save: bool = True):
        fig, ax = plt.subplots(figsize=(10, 8))
        corr = self.correlation_matrix()
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        ax.set_title("Pollutant Correlation Matrix")
        if save:
            path = FIGURES_DIR / "correlation_heatmap.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()

    def plot_aqi_trends(self, city: str = None, save: bool = True):
        df = self.df
        if city:
            df = df[df["city"] == city]
        if "aqi" not in df.columns or df["aqi"].isna().all():
            return
        fig, ax = plt.subplots(figsize=(14, 5))
        if city:
            df["aqi"].plot(ax=ax, marker="o", linestyle="-")
        else:
            for c in df["city"].unique():
                subset = df[df["city"] == c]
                subset["aqi"].plot(ax=ax, label=c, marker=".")
            ax.legend()
        ax.set_title(f"Air Quality Index Over Time{' - ' + city if city else ''}")
        ax.set_ylabel("AQI")
        ax.grid(alpha=0.3)
        if save:
            label = city.replace(" ", "_") if city else "all_cities"
            path = FIGURES_DIR / f"aqi_trend_{label}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()

    def plot_pollutant_composition(self, save: bool = True):
        cols = [c for c in TARGET_POLLUTANTS if c in self.df.columns]
        if not cols:
            return
        fig, ax = plt.subplots(figsize=(12, 5))
        self.df[cols].mean().plot(kind="bar", ax=ax, color="steelblue")
        ax.set_title("Average Pollutant Concentrations")
        ax.set_ylabel("Concentration (µg/m³)")
        ax.grid(alpha=0.3, axis="y")
        if save:
            path = FIGURES_DIR / "pollutant_composition.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()

    def generate_report(self) -> dict:
        return {
            "summary": self.summary_stats(),
            "correlation": self.correlation_matrix(),
            "record_count": len(self.df),
            "cities": list(self.df["city"].unique()) if "city" in self.df.columns else [],
            "date_range": [str(self.df.index.min()), str(self.df.index.max())],
        }
