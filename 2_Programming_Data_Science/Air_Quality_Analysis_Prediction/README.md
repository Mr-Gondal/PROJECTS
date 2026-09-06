# PROJECT 2.3: Air Quality Analysis & Prediction Model — Pakistan

An interactive **web dashboard** analyzing air quality across 5 major Pakistan cities — Lahore, Karachi, Islamabad, Peshawar, and Quetta. Features live AQI monitoring, trend analysis, pollutant correlation, and ML-powered predictions.

> **Honest data note:** in demo mode the dashboard uses a **clearly-labelled synthetic 90-day series** so it runs with zero setup. Live mode pulls real readings from the **OpenWeatherMap Air Pollution API**. Model metrics shown in the *Predict* tab are **computed live on a chronological hold-out split** — they are never hard-coded, and on synthetic data they demonstrate the pipeline rather than real-world forecasting skill.

---

## ✨ Features

| Feature | Description |
|---|---|
| **📊 Overview** | At-a-glance AQI status per city, 7-day-window trend deltas, "as of" timestamp |
| **🔬 Analytics** | Correlation heatmaps, pollutant composition, daily-average AQI trends |
| **🤖 Predict** | ML pollutant prediction with live-computed test metrics (MAE / RMSE / R²) |
| **🇺🇸 EPA AQI** | PM2.5/PM10 → AQI via US EPA **2024 breakpoints** with correct truncation |
| **📈 Interactive Charts** | Plotly-powered zoom, pan, and hover tooltips |

## 🧠 ML Models

- **Random Forest**, **Gradient Boosting**, **Linear Regression** — predicting PM2.5, PM10, NO2, SO2, CO, or O3.

**Training protocol** (leakage-free, see `src/model.py`):

1. Rows sorted by timestamp → first 80% = train, last 20% = test (**chronological split**, not random)
2. `StandardScaler` fit **on the training split only**
3. Median imputation learned **from the training split only** and persisted with the model

Model artifacts (`.joblib`) are **not committed** — regenerate locally with `python main.py --input data/raw/aqi_sample.csv --train`.

---

## 🛠️ Tech Stack

`Python` `Streamlit` `Scikit-learn` `Pandas` `Plotly` `Matplotlib` `OpenWeatherMap API`

## 📁 Project Structure

```
├── app.py                  # 🌐 Streamlit web dashboard (main)
├── main.py                 # CLI pipeline (alternative)
├── requirements.txt        # Dependencies
├── src/
│   ├── config.py           # Configuration & env/secrets handling
│   ├── aqi_scale.py        # EPA 2024 AQI conversion (pure, unit-tested)
│   ├── data_collector.py   # OpenWeatherMap API client
│   ├── analyzer.py         # Analysis & visualization
│   ├── model.py            # ML models (leakage-free protocol)
│   └── sample_data.py      # Synthetic demo-data generator
├── data/                   # Raw & processed data (generated, git-ignored)
├── models/                 # Trained ML models (generated, git-ignored)
└── figures/                # Generated plots (git-ignored)
```

---

## 🏃 Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the dashboard
streamlit run app.py

# 3. Open http://localhost:8501 in your browser
```

> No API key required — demo data is generated automatically on first run.

### CLI Mode (alternative)

```bash
python main.py --input data/raw/aqi_sample.csv --analyze --train   # analyze + train
python main.py --all                                               # fetch → analyze → train (needs API key)
python main.py --predict some_new_measurements.csv                 # batch predictions
```

---

## 🌐 Deployment (Free)

### Option 1: Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"Deploy an app"** → select your repo → branch → `app.py`
4. Done — you get a public URL instantly

### Option 2: Hugging Face Spaces

1. Create a Space → select **Streamlit** SDK
2. Upload the files (or link GitHub repo)
3. Space builds and deploys automatically

---

## 🔌 Live Data (Optional)

To use real-time data:

1. Get a free API key from [openweathermap.org](https://openweathermap.org/api/air-pollution)
2. Paste it in the dashboard sidebar under **"Live API"**, or set it as an environment variable:
   - Linux/macOS: `export OWM_API_TOKEN=your_key`
   - Windows: `set OWM_API_TOKEN=your_key`
3. Or for Streamlit Cloud: add `OWM_API_TOKEN` in *Settings → Secrets*

> The variable name is **`OWM_API_TOKEN`** (used by `src/config.py`, `main.py`, and the dashboard). Live snapshots are appended to the demo history so trend charts keep working.

---

## 📸 Screenshots

*(Add screenshots here after deployment)*

---

## 🧪 Tests

AQI conversion logic is unit-tested at the repository root:

```bash
pip install pytest
pytest tests/ -q
```

---

Built for the **Programming & Data Science** portfolio track.
