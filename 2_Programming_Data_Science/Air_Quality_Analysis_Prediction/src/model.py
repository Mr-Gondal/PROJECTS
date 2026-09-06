import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path

from src.config import TARGET_POLLUTANTS, TRAIN_TEST_SPLIT, RANDOM_STATE, MODELS_DIR

# Minimum rows required to train a meaningful model. Below this the CLI
# refuses to train instead of printing meaningless metrics.
MIN_TRAIN_ROWS = 30


class AirQualityPredictor:
    """Pollutant regressor with leakage-free training.

    Methodology notes (interview-ready):
    - Rows are sorted by timestamp and split **chronologically**
      (first 80% train / last 20% test) — random splits on time series
      leak the future into training and inflate metrics.
    - The ``StandardScaler`` is fit **on the training split only**, then
      applied to the test split (fit_transform on the full X before
      splitting is a classic leakage bug this class avoids).
    - Missing values are imputed with **training-split medians**, which
      are persisted with the model so ``predict()`` imputes identically.
    """

    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.train_medians_ = None

    def _build_model(self):
        if self.model_type == "random_forest":
            return RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
        elif self.model_type == "gradient_boosting":
            return GradientBoostingRegressor(n_estimators=150, random_state=RANDOM_STATE)
        else:
            return LinearRegression()

    def prepare_features(self, df: pd.DataFrame, target: str = "pm25") -> tuple:
        """Build the feature matrix, sorted chronologically.

        Sorting here matters: ``train()`` splits by position, so the
        returned frames must already be in timestamp order.
        """
        df = df.copy()
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp").reset_index(drop=True)
            df["hour"] = df["timestamp"].dt.hour
            df["dayofweek"] = df["timestamp"].dt.dayofweek
            df["month"] = df["timestamp"].dt.month

        pollutant_features = [c for c in TARGET_POLLUTANTS if c in df.columns and c != target]
        weather_cols = [c for c in df.columns if c in ("temperature", "humidity", "wind_speed", "pressure")]
        calendar_cols = [c for c in ("hour", "dayofweek", "month") if c in df.columns]

        feature_cols = pollutant_features + weather_cols + calendar_cols
        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found in data")

        self.feature_columns = feature_cols
        X = df[feature_cols].astype(float)
        y = df[target].astype(float)
        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        if len(X) < MIN_TRAIN_ROWS:
            raise ValueError(
                f"Not enough rows to train ({len(X)} < {MIN_TRAIN_ROWS}). "
                "Collect more history or train on the bundled sample dataset."
            )

        # --- chronological split (X is sorted by timestamp already) ---
        split = int(len(X) * TRAIN_TEST_SPLIT)
        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        if len(X_test) == 0:
            raise ValueError("Test split is empty — too few rows for evaluation")

        # --- imputation learned from the TRAINING split only ---
        self.train_medians_ = X_train.median()
        X_train = X_train.fillna(self.train_medians_)
        X_test = X_test.fillna(self.train_medians_)

        # --- scaling fit on TRAIN only, applied to both ---
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model = self._build_model()
        self.model.fit(X_train_scaled, y_train)
        y_pred = self.model.predict(X_test_scaled)

        metrics = {
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "r2": float(r2_score(y_test, y_pred)),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
        }
        return {"metrics": metrics, "y_test": y_test, "y_pred": y_pred}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        X = X[self.feature_columns].astype(float)
        if self.train_medians_ is not None:
            X = X.fillna(self.train_medians_)
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def save(self, path: str = None):
        if self.model is None:
            raise ValueError("Nothing to save — train first.")
        if path is None:
            path = MODELS_DIR / f"aqi_predictor_{self.model_type}.joblib"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "scaler": self.scaler,
                "features": self.feature_columns,
                "train_medians": self.train_medians_,
                "model_type": self.model_type,
            },
            path,
        )

    def load(self, path: str):
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_columns = data["features"]
        self.train_medians_ = data.get("train_medians")


def train_all_models(df: pd.DataFrame, target: str = "pm25") -> dict:
    """Train all three model types on the same leakage-free protocol."""
    if len(df) < MIN_TRAIN_ROWS:
        raise ValueError(
            f"Refusing to train on {len(df)} rows (minimum {MIN_TRAIN_ROWS}). "
            "Train on the historical sample dataset or collect more API history."
        )
    results = {}
    for model_type in ("random_forest", "gradient_boosting", "linear"):
        predictor = AirQualityPredictor(model_type=model_type)
        X, y = predictor.prepare_features(df, target=target)
        result = predictor.train(X, y)
        predictor.save()
        results[model_type] = result["metrics"]
    return results
