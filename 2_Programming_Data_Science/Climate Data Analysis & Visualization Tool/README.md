# 🌡️ Pakistan Climate Observatory

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3D4F9F?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Science-150458?style=for-the-badge&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**Interactive 50-year climate data analysis and visualization platform for Pakistan.**  
Explore temperature trends, precipitation patterns, drought indices, and climate change signals across 6 major cities (1974–2024).

[🚀 Launch App](#-quick-start) · [📊 Features](#-features) · [🛠️ Tech Stack](#️-tech-stack) · [📖 Documentation](#-project-structure)

</div>

---

## 📌 Overview

The **Pakistan Climate Observatory** is a full-stack geospatial data science project that demonstrates end-to-end climate data analysis — from synthetic data generation to interactive dashboard visualization. It showcases professional Python skills in time-series analysis, statistical modeling, and geospatial data science applicable to real-world environmental monitoring.

This project uses a **NOAA-inspired synthetic dataset** calibrated to realistic climatological profiles of Pakistani cities, complete with:
- A **+0.025°C/year warming trend** consistent with IPCC South Asia projections
- **Gamma-distributed precipitation** for realistic skewed rainfall patterns
- **Interannual variability** and decadal precipitation shifts

---

## ✨ Features

### 📊 Dashboard (Streamlit)
- 🎨 **Dark Glassmorphism UI** — Custom CSS with backdrop blur, gradient backgrounds, and animated metric cards
- 🌡️ **Warming Stripes** — Ed Hawkins-inspired climate stripe visualization per city
- 📈 **Temperature Trend Analysis** — 10-year rolling average with confidence bands and linear regression
- 🌧️ **Precipitation Heatmap** — Month × Year heatmap revealing monsoon seasonality
- 💧 **SPI Drought Index** — Standardized Precipitation Index with drought category classification
- ⚠️ **Anomaly Detection** — Z-score flagging of temperature and precipitation extremes vs. 1974–2004 baseline
- 📅 **Seasonal Analysis** — Decade-by-season grouped bar charts
- 🕸️ **Radar Chart** — Normalized climate profile comparison across cities
- 🔮 **Temperature Projections** — Linear projection to 2035 with uncertainty cone
- 📥 **CSV Export** — One-click download of full or filtered datasets

### 🖥️ CLI Tool
- `analyze` — Full statistical summary + optional HTML report with embedded charts
- `export` — Export datasets to CSV or JSON
- `trends` — Print OLS regression statistics and decadal projections
- `anomalies` — Detect and rank the most extreme climate events

### 📐 Analysis Engine
- **Mann-Kendall-inspired trend detection** using `scipy.stats.linregress`
- **Anomaly flagging** against 30-year climatological baseline
- **Seasonal aggregation** by meteorological season (DJF/MAM/JJA/SON) per decade
- **Climate stripes data** preparation for any city

---

## 🏙️ Cities Covered

| City | Province | Climate Type | Notable Feature |
|------|----------|-------------|-----------------|
| 🟡 **Lahore** | Punjab | Semi-arid subtropical | Hot summers (~42°C), monsoon July–Sep |
| 🔴 **Karachi** | Sindh | Hot semi-arid | Mild year-round, coastal humidity |
| 🟢 **Islamabad** | Federal Territory | Humid subtropical | Higher spring rainfall, cold winters |
| 🟠 **Peshawar** | KPK | Hot semi-arid | Extreme heat (~44°C), spring rainfall |
| 🟣 **Quetta** | Balochistan | Cold semi-arid | Freezing winters (~-5°C), very dry |
| 🟤 **Multan** | Punjab | Hot desert | Extreme heat (~46°C), dust storms |

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Dashboard** | Streamlit | Interactive web application |
| **Visualization** | Plotly | Interactive charts and heatmaps |
| **Data Processing** | Pandas, NumPy | Data manipulation and generation |
| **Statistics** | SciPy | Linear regression, trend analysis |
| **Styling** | Custom CSS | Glassmorphism dark theme |
| **CLI** | Argparse | Command-line interface |
| **Plots (static)** | Matplotlib, Seaborn | Static analysis outputs |

---

## 📁 Project Structure

```
Climate Data Analysis & Visualization Tool/
├── app.py                    # 🚀 Main Streamlit dashboard
├── main.py                   # 🖥️  CLI analysis tool
├── requirements.txt          # 📦 Python dependencies
├── README.md                 # 📖 This file
└── src/
    ├── __init__.py           # Package init
    ├── data_generator.py     # 🌍 Synthetic climate data generation
    ├── analysis.py           # 📊 Statistical analysis functions
    └── visualizations.py     # 📈 Plotly visualization functions
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip or conda package manager

### Installation

```bash
# 1. Clone or navigate to the project directory
cd "Climate Data Analysis & Visualization Tool"

# 2. Create a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Launch the Dashboard

```bash
streamlit run app.py
```

Then open your browser at **http://localhost:8501** 🎉

---

## 🖥️ CLI Usage

```bash
# Analyze a specific city with an HTML report
python main.py analyze --city Lahore --start 1980 --end 2024 --output report.html

# Export all cities to CSV
python main.py export --city all --format csv --output climate_data.csv

# Export Karachi data to JSON
python main.py export --city Karachi --format json --output karachi.json

# Print trend statistics for Karachi
python main.py trends --city Karachi

# Print trend statistics for all cities
python main.py trends --city all

# Detect anomalies with custom threshold
python main.py anomalies --city Islamabad --threshold 2.0
```

---

## 📊 Analysis Functions Reference

```python
from src.data_generator import generate_climate_dataset
from src.analysis import (
    compute_annual_trends,
    detect_anomalies,
    compute_seasonal_stats,
    compute_climate_stripes_data,
    compute_drought_index,
    get_trend_statistics,
    project_temperatures,
)

# Generate the dataset
df = generate_climate_dataset(seed=42)  # 3,600 rows

# Annual trends with warming slope
annual = compute_annual_trends(df)

# Detect anomalies (>1.5σ from 1974–2004 baseline)
anomalies = detect_anomalies(df, threshold=1.5)

# SPI Drought Index
drought = compute_drought_index(df)

# Trend statistics (OLS regression per city)
stats = get_trend_statistics(df)

# Project to 2035
projections = project_temperatures(annual, target_year=2035)
```

---

## 📸 Screenshots

> **Overview Tab** — Multi-city temperature and precipitation trends with metric cards  
> **Temperature Analysis** — Warming Stripes, trend line with confidence band, anomaly timeline  
> **Precipitation & Drought** — Month×Year heatmap, SPI bar chart, seasonal comparison  
> **Trends & Projections** — Projection chart to 2035, decadal tables, trend statistics  
> **City Comparison** — Box plots, precipitation area chart, radar profile chart  

*Run `streamlit run app.py` to see the live interactive dashboard.*

---

## 🌍 Data Sources & Methodology

- **Dataset**: NOAA-inspired **synthetic** climate data (no real API required)
- **Generation Method**: Numpy random with fixed seed (42) for full reproducibility
- **Temperature Model**: Monthly baseline profiles per city + Gaussian interannual noise (σ=1°C)
- **Precipitation Model**: Gamma-distributed monthly rainfall with shape/scale derived from climatological means
- **Climate Change Signal**: +0.025°C/year warming trend (consistent with IPCC AR6 South Asia projections)
- **Anomaly Detection**: Z-score method against 1974–2004 climatological baseline
- **Drought Index**: Simplified Standardized Precipitation Index (SPI) by standardizing monthly precipitation

---

## 📚 References

- IPCC AR6 Working Group I — Climate Change 2021: The Physical Science Basis
- Pakistan Meteorological Department (PMD) — Historical Climate Data
- Hawkins, E. (2018) — Warming Stripes (ShowYourStripes.info)
- McKee, T.B. et al. (1993) — The Relationship of Drought Frequency and Duration to Time Scales (SPI)

---

## 👨‍💻 Author

**Haris Hussain**  
GIS Analyst & Space Science Researcher  
University of Punjab, Lahore, Pakistan (GPA: 3.47)

- 🔬 Specializations: GIS, Remote Sensing, Environmental Data Science
- 🛠️ Skills: Python · GeoPandas · Rasterio · GDAL · Scikit-learn · Streamlit · Plotly
- 📍 Location: Lahore, Pakistan

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License — Copyright (c) 2024 Haris Hussain
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

<div align="center">

Made with ❤️ in Lahore, Pakistan 🇵🇰  
**Pakistan Climate Observatory** · Built for portfolio & research purposes

</div>
