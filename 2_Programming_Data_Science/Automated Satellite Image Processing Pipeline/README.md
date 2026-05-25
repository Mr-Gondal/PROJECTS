# 🛰️ Automated Satellite Image Processing Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-3776ab?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-ff4b4b?style=flat-square&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-KMeans%20LULC-f7931e?style=flat-square&logo=scikit-learn&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Raster%20Processing-013243?style=flat-square&logo=numpy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**A cloud-native Earth Observation pipeline for Pakistan — spectral analysis, unsupervised land cover classification, and bi-temporal change detection. Fully offline with production-ready architecture.**

[Features](#-features) • [How It Works](#-how-it-works) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Project Structure](#-project-structure)

</div>

---

## 📌 Overview

This project demonstrates a **professional-grade satellite image processing pipeline** applied to major Pakistani cities. It replicates the full workflow used by Earth Observation (EO) scientists — from raw satellite band ingestion, through spectral index computation and machine learning classification, to automated report generation.

> **Portfolio Note:** The data layer uses a synthetic Sentinel-2 generator with realistic biophysical profiles (no API keys needed). The processing, ML, and visualization layers are identical to what would be used with real STAC/Sentinel-2 data — simply swap `SyntheticSTACClient` for `pystac_client`.

**Regions covered:** Lahore · Karachi · Islamabad · Gilgit · Peshawar · Multan

---

## ✨ Features

- 🛰️ **Sentinel-2 Band Simulation** — Realistic surface reflectance arrays with per-city biophysical profiles and seasonal NDVI modulation
- 📐 **Spectral Index Engine** — NDVI, NDWI, NDBI, and EVI computed with proper band arithmetic
- 🗺️ **LULC Classification** — KMeans clustering with intelligent **automatic semantic labelling** (no training data needed)
- 🔄 **Change Detection** — Bi-temporal comparison (2020 → 2024) quantifying urban expansion and vegetation change
- 📊 **Interactive Dashboard** — Streamlit app with dark space theme, Plotly heatmaps, folium maps, and LULC overlays
- 📄 **HTML Report Generator** — Self-contained downloadable reports with embedded charts and statistics tables
- 💻 **CLI Tool** — Headless pipeline execution via `main.py` with ANSI colour output

---

## 🔬 How It Works

The pipeline runs in **5 sequential stages**. Here is exactly what each stage does:

---

### Stage 1 — STAC Query (`src/stac_client.py`)

In a production system, this stage calls the [Earth Search](https://earth-search.aws.element84.com/v1) or [Planetary Computer](https://planetarycomputer.microsoft.com/) STAC API to search for Sentinel-2 scenes matching a bounding box, date range, and cloud cover threshold.

In this implementation, `SyntheticSTACClient` replicates that API contract exactly:

1. You provide a **region name** (e.g. `"Lahore"`), **start/end dates**, and **max cloud cover %**.
2. The client returns a **scene metadata dictionary** — `scene_id`, `platform`, `processing_level`, `n_scenes`, `bbox`, `cloud_cover` — identical in shape to a real STAC item.
3. Calling `load_bands(region_name, scene_id)` returns a dictionary of **5 Sentinel-2 bands** as NumPy float32 arrays (100×100 pixels):

| Band | Name | Wavelength | Used For |
|------|------|------------|----------|
| B02 | Blue | 490 nm | RGB composite, EVI |
| B03 | Green | 560 nm | RGB composite, NDWI |
| B04 | Red | 665 nm | NDVI, NDBI, RGB |
| B08 | NIR | 842 nm | NDVI, NDWI, NDBI, EVI |
| B11 | SWIR1 | 1610 nm | NDBI |

**What makes the synthetic data realistic:**
- Each region has a **biophysical profile** — fractions of Water / Dense Vegetation / Sparse Vegetation / Urban / Bare Soil that match the real land cover of that city
  - *Lahore*: 50% Urban, 15% Sparse Veg, 21% Bare Soil
  - *Islamabad*: 35% Dense Forest, 24% Urban, 25% Sparse Veg
  - *Gilgit*: 57% Bare Rock, 20% Sparse Veg (alpine)
- Each cover type has **calibrated spectral centroids** (e.g. water has very low NIR, dense vegetation has very high NIR)
- A **seasonal NIR modulation** is applied — vegetation appears greener during July–September (monsoon peak) and browner in winter
- Seeds are **deterministic per region+date** so results are reproducible

---

### Stage 2 — Spectral Index Computation (`src/processor.py`)

The `SatelliteProcessor` class uses **band arithmetic** on the raw arrays to compute four spectral indices. Each index exploits the different way land covers reflect light at different wavelengths:

#### NDVI — Normalised Difference Vegetation Index
```
NDVI = (NIR − Red) / (NIR + Red)      range: −1 to +1
```
- Plants strongly absorb Red (photosynthesis) and strongly reflect NIR (cell structure)
- **NDVI > 0.3** → healthy vegetation  |  **NDVI < 0** → water or urban

#### NDWI — Normalised Difference Water Index *(McFeeters 1996)*
```
NDWI = (Green − NIR) / (Green + NIR)  range: −1 to +1
```
- Water reflects Green but absorbs NIR strongly
- **NDWI > 0** → open water  |  **NDWI < 0** → land

#### NDBI — Normalised Difference Built-up Index *(Zha et al. 2003)*
```
NDBI = (SWIR1 − NIR) / (SWIR1 + NIR) range: −1 to +1
```
- Urban surfaces reflect SWIR more than NIR (opposite of vegetation)
- **NDBI > 0** → built-up / urban  |  **NDBI < 0** → vegetation

#### EVI — Enhanced Vegetation Index
```
EVI = 2.5 × (NIR − Red) / (NIR + 6×Red − 7.5×Blue + 1)
```
- More sensitive than NDVI in dense canopy areas
- Corrects for atmospheric effects and soil background

All indices are computed with **zero-division protection** and clamped to their physical range.

---

### Stage 3 — LULC Classification (`src/classifier.py`)

This is the **most technically impressive** stage. It performs **unsupervised land cover mapping without any labelled training data**.

#### Step 3a — Feature Stacking
All 5 band arrays + 4 index arrays are flattened and stacked into a feature matrix of shape `(10,000 pixels × 9 features)`. NaN pixels (clouds) are imputed with column medians.

#### Step 3b — KMeans Clustering
`StandardScaler` normalises all features to zero mean and unit variance (critical — otherwise high-reflectance NIR would dominate the distance metric). Then `KMeans` with `k-means++` initialisation groups pixels into N clusters (user-selectable, default 5).

#### Step 3c — Automatic Semantic Labelling *(the intelligent part)*
Rather than leaving you with meaningless "Cluster 0, Cluster 1..." labels, the classifier **reads the spectral signatures of each cluster centroid** and assigns real-world class names using domain knowledge:

```
Priority rule-set (applied in order):
  1. Cluster with highest mean NDWI  → Water          (blue)
  2. Cluster with highest mean NDVI  → Dense Veg      (dark green)
  3. Cluster with 2nd-highest NDVI   → Sparse Veg     (light green)
  4. Cluster with highest mean NDBI  → Urban/Built-up (red)
  5. All remaining clusters          → Bare Soil       (tan)
```

This mirrors exactly how expert remote sensing analysts manually label unsupervised classification outputs — just automated.

#### Step 3d — Area Statistics
Each class is measured: pixel count, area in km² (using 10m Sentinel-2 pixel size), and scene coverage percentage.

---

### Stage 4 — Change Detection (`src/change_detector.py`)

Two scenes are generated for the **same region in different years** (2020 and 2024). The 2024 scene has +7% urban fraction to simulate real city growth.

For each index, a **difference map** is computed:
```
ΔNDVI = NDVI(2024) − NDVI(2020)
ΔNDBI = NDBI(2024) − NDBI(2020)
ΔNDWI = NDWI(2024) − NDWI(2020)
```

Pixels are then classified into **5 semantic change classes** using threshold logic (±0.1):

| Class | Condition | Meaning |
|-------|-----------|---------|
| No Change | \|ΔNDVI\| < 0.1 and \|ΔNDBI\| < 0.1 | Stable land cover |
| Vegetation Gain | ΔNDVI > +0.1 | Reforestation / crop growth |
| Vegetation Loss | ΔNDVI < −0.1 | Deforestation / drought stress |
| Urban Expansion | ΔNDBI > +0.1 | New buildings / roads |
| Water Change | \|ΔNDWI\| > +0.1 | Flood / reservoir change |

---

### Stage 5 — Report Generation & Dashboard (`src/report_generator.py`, `app.py`)

The `ReportGenerator` assembles a **self-contained HTML report** using f-string templating with:
- Scene metadata header (region, dates, platform, cloud cover)
- LULC classification table with colour-coded class rows
- Change detection statistics table
- Spectral index summary (mean, std, min, max per index)
- Base64-embedded Matplotlib pie chart (no external dependencies)

The **Streamlit dashboard** (`app.py`) provides 5 interactive tabs:
1. **🗺️ Maps** — NDVI heatmap, LULC RGB map, folium interactive map with LULC overlay
2. **📊 Spectral Indices** — Plotly heatmaps for NDVI/NDWI/NDBI/EVI + violin distribution charts
3. **🌿 Land Cover** — LULC donut pie chart, area bar chart, statistics table
4. **🔄 Change Detection** — Side-by-side NDVI 2020/2024, ΔNDVI map, semantic change pie chart
5. **📄 Report** — Rendered HTML report with download button

---

## 🏗️ Architecture

```
User Input (Region, Dates, Clusters)
           │
           ▼
┌─────────────────────┐
│  SyntheticSTACClient │  ← Mimics real STAC API (pystac-client)
│  stac_client.py      │    Returns scene metadata + band arrays
└──────────┬──────────┘
           │ bands dict {B02, B03, B04, B08, B11}
           ▼
┌─────────────────────┐
│  SatelliteProcessor  │  ← Pure band arithmetic
│  processor.py        │    Computes NDVI, NDWI, NDBI, EVI
└──────────┬──────────┘
           │ indices dict + feature matrix
           ▼
┌─────────────────────┐
│   LULCClassifier     │  ← StandardScaler → KMeans → Auto-label
│   classifier.py      │    Outputs classified 2D map + area stats
└──────────┬──────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌──────────┐  ┌──────────────┐
│  Change  │  │    Report    │
│ Detector │  │  Generator   │
│ (ΔNDVI,  │  │ (HTML report)│
│  ΔNDBI)  │  └──────┬───────┘
└──────┬───┘         │
       │             │
       ▼             ▼
┌──────────────────────────┐
│   Streamlit Dashboard    │  ← Interactive 5-tab web app
│       app.py             │    Plotly + Folium visualizations
└──────────────────────────┘
```

---

## 📁 Project Structure

```
Automated Satellite Image Processing Pipeline/
│
├── app.py                    # 🌐 Streamlit web dashboard (903 lines)
├── main.py                   # 💻 CLI pipeline tool (argparse)
├── requirements.txt          # 📦 Python dependencies
├── IMPLEMENTATION_PLAN.md    # 📝 Original architecture design doc
│
└── src/                      # ⚙️ Core pipeline package
    ├── __init__.py
    ├── config.py             # Regions, bands, LULC classes, colours
    ├── stac_client.py        # Synthetic Sentinel-2 data generator
    ├── processor.py          # NDVI / NDWI / NDBI / EVI computation
    ├── classifier.py         # KMeans LULC + auto semantic labelling
    ├── change_detector.py    # Bi-temporal ΔNDVI / ΔNDBI analysis
    ├── report_generator.py   # Self-contained HTML report builder
    └── utils.py              # Colourmap → base64, Folium map, helpers
```

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/satellite-pipeline.git
cd "Automated Satellite Image Processing Pipeline"

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 💻 Usage

### Streamlit Dashboard

1. Select a **region** (Lahore, Karachi, Islamabad, Gilgit, Peshawar, Multan)
2. Set a **date range** and **cloud cover threshold**
3. Choose the number of **LULC clusters** (3–7)
4. Click **🚀 Run Analysis**
5. Explore the 5 result tabs and download the HTML report

### CLI

```bash
# Run full pipeline for a region
python main.py --region Lahore --start 2020-01 --end 2024-12 --clusters 5

# List all available regions
python main.py --list-regions

# Generate report only (no dashboard)
python main.py --region Karachi --report-only

# Save report to a specific directory
python main.py --region Islamabad --start 2022-01 --end 2023-12 --output reports/
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web dashboard framework |
| `numpy` | Raster array operations |
| `pandas` | Statistics tables |
| `scikit-learn` | KMeans clustering, StandardScaler |
| `plotly` | Interactive Plotly charts |
| `matplotlib` | Colourmap rendering, base64 images |
| `folium` | Interactive Leaflet map |
| `streamlit-folium` | Folium integration for Streamlit |
| `scipy` | Cloud masking (Gaussian filter) |
| `Pillow` | Image utilities |
| `reportlab` | (Available for PDF export extension) |

---

## 🔭 Extending to Real Satellite Data

To connect to real Sentinel-2 imagery, replace `SyntheticSTACClient` with `pystac_client`:

```python
# Real STAC client (requires: pip install pystac-client odc-stac rioxarray)
import pystac_client

catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
items = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=REGIONS["Lahore"],
    datetime="2024-01-01/2024-12-31",
    query={"eo:cloud_cover": {"lt": 10}},
).get_all_items()
```

All downstream modules (`processor.py`, `classifier.py`, `change_detector.py`) work identically with real band arrays.

---

## 📊 Sample Results

| Region | Dominant Class | Urban % | Vegetation % | NDVI Mean |
|--------|---------------|---------|--------------|-----------|
| Lahore | Urban/Built-up | ~50% | ~25% | 0.18 |
| Islamabad | Dense Vegetation | ~24% | ~60% | 0.41 |
| Gilgit | Bare Soil | ~10% | ~28% | 0.12 |
| Karachi | Urban/Built-up | ~55% | ~12% | 0.09 |

*Values based on synthetic biophysical profiles. Real Sentinel-2 data may vary.*

---

## 👨‍💻 Author

**Haris Hussain**
*GIS Analyst | Space Science Undergraduate | Remote Sensing Specialist*
University of Punjab, Lahore, Pakistan
📧 hussainharis946@gmail.com

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<sub>Built with 🛰️ for Earth Observation — Pakistan Remote Sensing Portfolio</sub>
</div>
