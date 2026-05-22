# PROJECT 2.3: Air Quality Analysis & Prediction Model — Pakistan

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Demo-2d6a4f?logo=streamlit)](https://your-app-url.streamlit.app)

An interactive **web dashboard** analyzing air quality across 5 major Pakistan cities — Lahore, Karachi, Islamabad, Peshawar, and Quetta. Features live AQI monitoring, trend analysis, pollutant correlation, and ML-powered predictions.

---

## 🚀 Live Demo

**👉 [View the Dashboard](https://your-app-url.streamlit.app)** (click to deploy — see Deployment below)

---

## ✨ Features

| Feature | Description |
|---|---|
| **📊 Overview** | At-a-glance AQI status for all cities with color-coded health ratings |
| **🔬 Analytics** | Interactive correlation heatmaps, pollutant composition, AQI trends |
| **🤖 Predict** | ML-powered pollutant prediction with adjustable environmental factors |
| **🗺️ City Comparison** | Side-by-side comparison of pollution across cities |
| **📈 Interactive Charts** | Plotly-powered zoom, pan, and hover tooltips |

## 🧠 ML Models

- **Random Forest** — R² ~0.89
- **Gradient Boosting** — R² ~0.87
- **Linear Regression** — R² ~0.90

Predicts PM2.5, PM10, NO2, SO2, CO, and O3 levels.

---

## 🛠️ Tech Stack

`Python` `Streamlit` `Scikit-learn` `Pandas` `Plotly` `Matplotlib` `Seaborn` `WAQI API`

## 📁 Project Structure

```
├── app.py                  # 🌐 Streamlit web dashboard (main)
├── main.py                 # CLI pipeline (alternative)
├── requirements.txt        # Dependencies
├── src/
│   ├── config.py           # Configuration
│   ├── data_collector.py   # AQI API data fetching
│   ├── analyzer.py         # Analysis & visualization
│   ├── model.py            # ML prediction models
│   └── sample_data.py      # Sample data generator
├── data/                   # Raw & processed data
├── models/                 # Trained ML models (.joblib)
└── figures/                # Generated plots
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

> No API key required — sample data loads automatically.

### CLI Mode (alternative)

```bash
python main.py --input data/raw/aqi_sample.csv --analyze --train
```

---

## 🌐 Deployment (Free)

### Option 1: Streamlit Community Cloud (Recommended)

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

1. Get a free API token from [waqi.info](https://waqi.info)
2. Set it in the sidebar of the dashboard under "Live API"
3. Or set in terminal: `set AQI_API_TOKEN=your_token`

---

## 📸 Screenshots

*(Add screenshots here after deployment)*

---

Built for the **Programming & Data Science** portfolio track.
