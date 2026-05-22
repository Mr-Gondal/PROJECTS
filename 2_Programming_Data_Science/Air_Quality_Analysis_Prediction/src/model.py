import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from src.config import TARGET_POLLUTANTS, TRAIN_TEST_SPLIT, RANDOM_STATE, MODELS_DIR
from pathlib import Path


class AirQualityPredictor:
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None

    def _build_model(self):
        if self.model_type == "random_forest":
            return RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
        elif self.model_type == "gradient_boosting":
            return GradientBoostingRegressor(n_estimators=150, random_state=RANDOM_STATE)
        else:
            return LinearRegression()

    def prepare_features(self, df: pd.DataFrame, target: str = "pm25") -> tuple:
        features = [c for c in TARGET_POLLUTANTS if c in df.columns and c != target]
        weather_cols = [c for c in df.columns if c in ["temperature", "humidity", "wind_speed", "pressure"]]
        feature_cols = features + weather_cols

        if "hour" not in df.columns:
            df = df.copy()
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df["hour"] = df["timestamp"].dt.hour
                df["dayofweek"] = df["timestamp"].dt.dayofweek
                df["month"] = df["timestamp"].dt.month
            feature_cols += ["hour", "dayofweek", "month"]

        self.feature_columns = feature_cols
        X = df[feature_cols].fillna(df[feature_cols].median())
        y = df[target].fillna(df[target].median())
        return X, y

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=1 - TRAIN_TEST_SPLIT, random_state=RANDOM_STATE
        )
        self.model = self._build_model()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }
        return {"metrics": metrics, "y_test": y_test, "y_pred": y_pred}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def save(self, path: str = None):
        if path is None:
            path = MODELS_DIR / f"aqi_predictor_{self.model_type}.joblib"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "scaler": self.scaler, "features": self.feature_columns}, path)

    def load(self, path: str):
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_columns = data["features"]


def train_all_models(df: pd.DataFrame, target: str = "pm25") -> dict:
    results = {}
    for model_type in ["random_forest", "gradient_boosting", "linear"]:
        predictor = AirQualityPredictor(model_type=model_type)
        X, y = predictor.prepare_features(df, target)
        result = predictor.train(X, y)
        predictor.save()
        results[model_type] = result["metrics"]
    return results
