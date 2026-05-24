# 🛰️ Automated Satellite Image Processing Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E?logo=scikit-learn&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.26%2B-013243?logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-brightgreen)

**A cloud-native Earth Observation pipeline for Pakistan — built with synthetic Sentinel-2 data, KMeans LULC classification, and bi-temporal change detection.**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Tech Stack](#-tech-stack)

</div>

---

## 📖 Overview

This project implements a **production-grade satellite image processing pipeline** targeting Pakistani cities and landscapes. It demonstrates the complete EO workflow — from STAC catalogue queries through band loading, spectral index computation, unsupervised land cover classification, and bi-temporal change detection — all wrapped in a premium Streamlit dashboard.

**Key innovation:** The pipeline uses a fully synthetic Sentinel-2 data generator that produces statistically realistic imagery without any API keys or network access, making it instantly runnable in offline environments while remaining architecturally identical to a real-world deployment.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🛰️ **Synthetic Sentinel-2** | Region-specific band arrays (B02–B11) with realistic spectral signatures |
| 📐 **Spectral Indices** | NDVI, NDWI, NDBI, EVI — with statistics and violin plot distributions |
| 🗺️ **LULC Classification** | KMeans clustering + automatic semantic labelling (Water, Vegetation, Urban, Bare Soil) |
| 🔄 **Change Detection** | Bi-temporal NDVI/NDBI/NDWI analysis (2020 → 2024) with 5 change classes |
| 🌍 **Interactive Map** | Folium map with LULC image overlay on CartoDB dark tiles |
| 📊 **Plotly Dashboards** | Heatmaps, pie charts, violin plots, side-by-side temporal comparisons |
| 📄 **HTML Reports** | Self-contained downloadable reports with embedded base64 charts |
| 🖥️ **CLI Interface** | Full command-line tool with coloured output and argparse |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Pakistan EO Pipeline                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌────────────────┐    ┌───────────────────┐   │
│  │  STAC Client │    │   Processor    │    │    Classifier     │   │
│  │  (Synthetic) │───▶│  • NDVI/NDWI  │───▶│  • KMeans        │   │
│  │  Sentinel-2  │    │  • NDBI / EVI  │    │  • Auto-labelling│   │
│  │  Band Arrays │    │  • RGB Compos. │    │  • Class stats   │   │
│  └──────────────┘    │  • Cloud Mask  │    └──────────┬────────┘   │
│                      └───────┬────────┘               │            │
│                              │                         │            │
│                      ┌───────▼────────┐    ┌──────────▼────────┐   │
│                      │ Change Detect. │    │  Report Generator │   │
│                      │ • NDVI diff   │    │  • HTML + charts  │   │
│                      │ • NDBI diff   │    │  • Base64 embeds  │   │
│                      │ • Semantic cls │    └──────────┬────────┘   │
│                      └───────┬────────┘               │            │
│                              │                         │            │
│              ┌───────────────▼─────────────────────────▼────────┐  │
│              │           Streamlit App  /  CLI (main.py)        │  │
│              │  5 Tabs: Maps · Indices · LULC · Change · Report │  │
│              └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
Automated Satellite Image Processing Pipeline/
├── app.py                     # 🖥️  Streamlit dashboard (main entry point)
├── main.py                    # ⌨️  CLI interface
├── requirements.txt           # 📦 Python dependencies
├── README.md                  # 📖 This file
├── IMPLEMENTATION_PLAN.md     # 📋 Detailed implementation notes
└── src/
    ├── __init__.py
    ├── config.py              # 🔧 Region bboxes, LULC classes, colours
    ├── stac_client.py         # 🛰️  Synthetic Sentinel-2 data generator
    ├── processor.py           # 📐 Spectral indices, composites, cloud mask
    ├── classifier.py          # 🤖 KMeans LULC classifier + auto-labelling
    ├── change_detector.py     # 🔄 Bi-temporal change detection
    ├── report_generator.py    # 📄 Self-contained HTML report generator
    └── utils.py               # 🔨 GeoJSON, colourmap, Folium, formatters
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (or conda)

### Setup

```bash
# Clone or navigate to project directory
cd "Automated Satellite Image Processing Pipeline"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🎯 Usage

### Streamlit Dashboard

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

**Workflow:**
1. Select a Pakistani city from the sidebar (Lahore, Karachi, Islamabad, Gilgit, Peshawar)
2. Set your analysis date range (2020–2024 recommended for change detection)
3. Adjust max cloud cover and number of LULC clusters
4. Click **🚀 Run Analysis** to run the full pipeline
5. Explore results across 5 tabs: Maps, Spectral Indices, Land Cover, Change Detection, Report

---

### CLI Interface

```bash
# Full pipeline for Lahore
python main.py --region Lahore --start 2020-01 --end 2024-12 --clusters 5 --output reports/

# Karachi with custom output directory
python main.py --region Karachi --start 2021-06 --end 2023-12 --output ./my_reports/

# List all available regions
python main.py --list-regions

# Fast report (indices only, skip LULC + change detection)
python main.py --region Islamabad --report-only

# Short flags
python main.py -r Gilgit -s 2020-01 -e 2024-12 -c 4 -o reports/
```

**CLI Output Example:**
```
╔══════════════════════════════════════════════════════════════╗
║   🛰️  Automated Satellite Image Processing Pipeline           ║
║      Pakistan Earth Observation | Sentinel-2 Analysis        ║
╚══════════════════════════════════════════════════════════════╝

  Region   : Lahore
  Period   : 2020-01 → 2024-12
  Clusters : 5

  [████████████████████] 100%  Bi-temporal change detection (2020 → 2024)…
     → LULC: Urban/Built-up 52.1% | Dense Vegetation 9.8% | ...
     → Change: Urban Expansion 12.3% (1.23 km²)

  ✅  Report saved → reports/EO_Report_Lahore_20240525_143022.html
```

---

## 🗺️ Study Regions

| Region | Lat | Lon | Climate | Dominant LULC |
|---|---|---|---|---|
| **Lahore** | 31.4–31.7°N | 74.1–74.6°E | Semi-arid subtropical | Urban (50%) |
| **Karachi** | 24.8–25.1°N | 66.9–67.2°E | Arid coastal | Urban (55%) |
| **Islamabad** | 33.5–33.8°N | 72.8–73.2°E | Humid subtropical | Mixed forest/urban |
| **Gilgit** | 35.8–36.2°N | 74.2–74.6°E | Alpine | Bare rock/sparse veg |
| **Peshawar** | 34.0–34.3°N | 71.4–71.8°E | Semi-arid | Sparse veg/urban |
| **Multan** | 30.1–30.4°N | 71.3–71.6°E | Hot arid | Agriculture/desert |

---

## 📊 Spectral Indices

| Index | Formula | Range | Interpretation |
|---|---|---|---|
| **NDVI** | (NIR − Red) / (NIR + Red) | −1 to 1 | > 0.3 = vegetation |
| **NDWI** | (Green − NIR) / (Green + NIR) | −1 to 1 | > 0 = water body |
| **NDBI** | (SWIR1 − NIR) / (SWIR1 + NIR) | −1 to 1 | > 0 = built-up |
| **EVI** | 2.5 × (NIR − Red) / (NIR + 6R − 7.5B + 1) | −1 to 2 | Enhanced veg sensitivity |

---

## 🌿 LULC Classes

| Class | Colour | Spectral Signature |
|---|---|---|
| 💧 Water | `#1a6faf` | High NDWI, low NIR |
| 🌲 Dense Vegetation | `#2d8a4e` | High NDVI, high NIR |
| 🌿 Sparse Vegetation | `#8ab87a` | Moderate NDVI |
| 🏙️ Urban/Built-up | `#c0392b` | High NDBI, moderate reflectance |
| 🏜️ Bare Soil | `#d4b483` | High SWIR, low NDVI |

---

## 🔄 Change Classes

| Class | Colour | Detection Logic |
|---|---|---|
| ◻️ No Change | `#aaaaaa` | All indices stable |
| 🌱 Vegetation Gain | `#2d8a4e` | ΔNDVI > 0.10, ΔNDBI < 0 |
| 🔥 Vegetation Loss | `#e67e22` | ΔNDVI < −0.10 |
| 🏗️ Urban Expansion | `#c0392b` | ΔNDBI > 0.10 |
| 💧 Water Change | `#1a6faf` | |ΔNDWI| > 0.10 |

---

## 🛠️ Tech Stack

| Component | Library | Purpose |
|---|---|---|
| **Dashboard** | Streamlit 1.32+ | Interactive web application |
| **ML** | scikit-learn | KMeans clustering, StandardScaler |
| **Arrays** | NumPy | Band arithmetic, raster operations |
| **Dataframes** | Pandas | Statistics tables, CSV export |
| **Charts** | Plotly | Interactive heatmaps, pie/bar charts |
| **Maps** | Folium + streamlit-folium | Leaflet-based map with image overlay |
| **Raster viz** | Matplotlib | Colourmap → base64 PNG for reports |
| **Image** | Pillow | Array-to-image utilities |
| **Reports** | Built-in (f-strings) | Self-contained HTML reports |
| **CLI** | argparse | Command-line interface |

---

## 📸 Screenshots

> Run `streamlit run app.py` and select a region to see the full dashboard.

**Dashboard Tabs:**
- 🗺️ **Maps** — NDVI heatmap + LULC classification side-by-side + Folium interactive map
- 📊 **Spectral Indices** — 4 colourmap heatmaps + violin distribution comparison
- 🌿 **Land Cover** — Donut pie chart + colour-coded bar chart + statistics table
- 🔄 **Change Detection** — 2020/2024 NDVI + difference map + semantic change map
- 📄 **Report** — Inline HTML preview + one-click download

---

## 🔌 Production Deployment

This pipeline is architecturally identical to a real-world deployment. To switch from synthetic to real Sentinel-2 data:

1. Replace `SyntheticSTACClient` with `pystac_client.Client.open("https://earth-search.aws.element84.com/v1")`
2. Update `load_bands()` to use `rasterio.open()` on COG URLs
3. Add authentication (AWS credentials / Copernicus token)

All downstream processing (indices, classification, change detection, reporting) requires **zero changes**.

---

## 📝 Data Note

> **This project uses 100% synthetic data** generated by `src/stac_client.py`. The synthetic bands mimic Sentinel-2 Level-2A surface reflectance with:
> - Region-specific biophysical profiles (urban fraction, vegetation type)
> - Seasonal NDVI modulation (monsoon peak in July–September)
> - Realistic spectral centroids per land cover type
> - Gaussian noise with spatially coherent cloud masking

No real satellite imagery, APIs, or internet access is required.

---

## 👤 Author

**Haris Hussain**
- 🎓 B.Sc. Space Science · University of Punjab, Lahore, Pakistan (GPA 3.47)
- 🌍 Specialisation: GIS, Remote Sensing, Environmental Data Science
- 🛠️ Skills: Python, GeoPandas, Rasterio, GDAL, scikit-learn, Streamlit, Plotly

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute for academic and portfolio purposes.

---

<div align="center">
  <sub>Built for the Pakistan EO portfolio · 2024 · 🛰️</sub>
</div>
