# ⚙️ Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-PostGIS--Sim-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/GeoPandas-GIS-139C5A?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/ETL-Pipeline-F59E0B?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge"/>
</p>

<p align="center">
  <b>Enterprise-grade geospatial ETL pipeline for Pakistan spatial data</b><br>
  <i>Extract → Transform → Validate → Load → Visualise | 30 districts · 7 provinces · Environmental monitoring</i>
</p>

---

## 📌 Overview

This project demonstrates a **production-quality ETL (Extract–Transform–Load) pipeline** for geospatial data, built entirely in Python. It simulates real-world data engineering workflows used by organisations like SUPARCO, PBS (Pakistan Bureau of Statistics), and PEPA (Pakistan Environmental Protection Agency).

The pipeline ingests multi-source spatial data — census records, satellite land-use classifications, environmental sensor readings, and infrastructure databases — applies rigorous transformations and quality checks, loads the results into a structured spatial database, and surfaces everything through an interactive Streamlit dashboard.

> **Portfolio Note**: All data is synthetically generated with realistic Pakistan-specific distributions. No external APIs, databases, or internet connection required.

---

## 🏗️ Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     SPATIAL DATA ETL PIPELINE ARCHITECTURE                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  DATA SOURCES (Simulated)          ETL STAGES                               ║
║  ┌─────────────────────┐           ┌──────────────────────────────────────┐ ║
║  │ 📊 Census Database  │──────────▶│  📥 EXTRACT  (extractor.py)          │ ║
║  │ 🌫️  PEPA AQI API    │──────────▶│  ├─ extract_census_data()            │ ║
║  │ 🛰️  SUPARCO LandUse │──────────▶│  ├─ extract_environmental_data()     │ ║
║  │ 🏥 Infrastructure DB│──────────▶│  ├─ extract_landuse_data()           │ ║
║  │ 🗺️  GeoJSON Bounds  │──────────▶│  ├─ extract_infrastructure_data()    │ ║
║  └─────────────────────┘           │  └─ extract_geojson_source()         │ ║
║                                    └──────────────┬───────────────────────┘ ║
║                                                   ▼                         ║
║  data/raw/ (CSV + GeoJSON)         ┌──────────────────────────────────────┐ ║
║  ┌─────────────────────┐           │  🔄 TRANSFORM  (transformer.py)       │ ║
║  │ census_raw.csv      │           │  ├─ clean_census_data()               │ ║
║  │ environmental_raw   │           │  ├─ reproject_coordinates()           │ ║
║  │ land_use_raw.csv    │           │  │    WGS84 (4326) → UTM 42N (32642) │ ║
║  │ infrastructure_raw  │           │  ├─ enrich_spatial_data()             │ ║
║  │ districts_bounds    │           │  ├─ compute_spatial_metrics()         │ ║
║  │ .geojson            │           │  ├─ validate_and_flag()               │ ║
║  └─────────────────────┘           │  └─ normalize_aqi_data()             │ ║
║                                    └──────────────┬───────────────────────┘ ║
║                                                   ▼                         ║
║                                    ┌──────────────────────────────────────┐ ║
║                                    │  ✅ VALIDATE  (validator.py)          │ ║
║                                    │  ├─ validate_schema()                 │ ║
║                                    │  ├─ validate_spatial_bounds()         │ ║
║                                    │  ├─ validate_completeness()           │ ║
║                                    │  ├─ validate_uniqueness()             │ ║
║                                    │  └─ ValidationReport (dataclass)      │ ║
║                                    └──────────────┬───────────────────────┘ ║
║                                                   ▼                         ║
║                                    ┌──────────────────────────────────────┐ ║
║                                    │  💾 LOAD  (loader.py)                 │ ║
║                                    │  ├─ initialize_database()             │ ║
║                                    │  ├─ load_districts()                  │ ║
║                                    │  ├─ load_environmental()              │ ║
║                                    │  ├─ load_land_use()                   │ ║
║                                    │  ├─ load_infrastructure()             │ ║
║                                    │  └─ log_pipeline_run()               │ ║
║                                    └──────────────┬───────────────────────┘ ║
║                                                   ▼                         ║
║                              ┌───────────────────────────────────────────┐  ║
║                              │  🗄️  SQLite Database (spatial_db.sqlite)   │  ║
║                              │  Tables: districts | environmental_data   │  ║
║                              │          land_use  | infrastructure        │  ║
║                              │          pipeline_runs (audit log)        │  ║
║                              └───────────────────┬───────────────────────┘  ║
║                                                  ▼                          ║
║          ┌──────────────────────────────────────────────────────────────┐   ║
║          │  📊 Streamlit Dashboard (app.py)                             │   ║
║          │  Tab 1: Pipeline Dashboard  │  Tab 4: Data Quality          │   ║
║          │  Tab 2: Spatial Explorer    │  Tab 5: SQL Explorer           │   ║
║          │  Tab 3: Data Tables         │  Tab 6: Analytics              │   ║
║          └──────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## ✨ Features

### 🔄 ETL Pipeline
| Stage | Description | Key Operations |
|-------|-------------|---------------|
| **Extract** | Multi-source data ingestion | Census, AQI API, land-use classification, infrastructure DB, GeoJSON boundaries |
| **Transform** | Spatial & tabular transformation | CRS reprojection (WGS84→UTM42N), attribute joins, spatial metrics, AQI normalisation |
| **Validate** | Automated quality assurance | Schema checks, bounds validation, completeness, uniqueness, IQR outlier detection |
| **Load** | Structured database loading | SQLite upsert operations, audit logging, pipeline run metadata |

### 📊 Dashboard Tabs
- **Pipeline Dashboard** — KPI metrics, run history chart, table status
- **Spatial Explorer** — Interactive Plotly mapbox choropleth coloured by any variable (population density, urban %, AQI, etc.)
- **Data Tables** — Paginated table browser with column filters and CSV export
- **Data Quality** — Quality score gauge (0-100), per-dataset validation breakdown, pass/warn/fail indicators
- **SQL Explorer** — Ad-hoc SQL query interface with 7 preset queries and CSV download
- **Analytics** — AQI trend lines, population distribution, land-use pie charts, infrastructure scatter plot, AQI heatmap

### 🖥️ CLI Tool
```
python main.py run --all              # Full ETL pipeline
python main.py run --extract-only     # Extraction stage only
python main.py run --transform-only   # Transform existing raw data
python main.py status                 # Database and pipeline health
python main.py validate --dataset all # Full quality validation
python main.py query --sql "SELECT * FROM districts LIMIT 10"
python main.py export --table districts --format csv --output districts.csv
python main.py export --table environmental_data --format json --output aqi.json
```

---

## 📁 Project Structure

```
Spatial Data ETL Pipeline/
│
├── app.py                  # Streamlit dashboard (industrial dark theme)
├── main.py                 # CLI entry point (Click-based, ANSI coloured)
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── src/                    # Core ETL package
│   ├── __init__.py
│   ├── config.py           # Constants, Pakistan districts data, CRS config
│   ├── extractor.py        # DataExtractor: 5 extraction methods
│   ├── transformer.py      # DataTransformer: 6 transformation methods
│   ├── loader.py           # DataLoader: SQLite DDL + upsert + query
│   ├── validator.py        # DataValidator: ValidationReport dataclass
│   └── monitor.py          # PipelineMonitor: operational metrics
│
├── data/
│   ├── raw/                # Raw CSVs + GeoJSON (generated at runtime)
│   ├── processed/          # Transformed CSVs (generated at runtime)
│   └── spatial_db.sqlite   # SQLite database (created by pipeline)
│
└── logs/                   # Log files directory
```

---

## 🗃️ Data Schema

### `districts` table (30 records)
| Column | Type | Description |
|--------|------|-------------|
| `name` | TEXT | District name (Lahore, Karachi, …) |
| `province` | TEXT | Province (Punjab, Sindh, KPK, Balochistan, ICT, GB, AJK) |
| `population` | INTEGER | 2023 estimated population |
| `pop_density` | REAL | Persons per km² |
| `pop_density_class` | TEXT | Very High / High / Medium / Low |
| `urban_pct` | REAL | Urban population % |
| `literacy_rate` | REAL | District literacy % |
| `compactness` | REAL | Polsby-Popper shape compactness (0-1) |
| `geometry_wkt` | TEXT | District polygon in WKT format |
| `quality_flag` | TEXT | PASS / WARN / FAIL |

### `environmental_data` table (120 records)
Monthly AQI + pollutant readings (PM2.5, PM10, NO₂, O₃, SO₂) for 10 cities with seasonal smog simulation.

### `land_use` table (30 records)
Per-district land cover percentages: Agricultural, Urban, Forest, Water, Barren — derived from simulated SUPARCO satellite classification.

### `infrastructure` table (30 records)
Road density, hospitals, schools, universities, electricity access %, internet access % per district.

### `pipeline_runs` table (audit log)
Full run metadata: run_id, timestamps, record counts, quality scores, triggered_by.

---

## 🔧 Installation & Usage

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone / navigate to project
```bash
cd "Spatial Data ETL Pipeline"
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the ETL pipeline (CLI)
```bash
python main.py run --all
```

### 5. Launch the Streamlit dashboard
```bash
streamlit run app.py
```

### 6. Check pipeline status
```bash
python main.py status
```

---

## 📊 Data Sources (Simulated)

All data is **synthetically generated** in Python using realistic distributions:

| Source | Simulated From | Records |
|--------|---------------|---------|
| PBS Census 2023 | Pakistan Bureau of Statistics | 30 districts |
| PEPA Environmental API | Pakistan EPA monitoring network | 120 city-month records |
| SUPARCO Land Cover | Satellite classification results | 30 districts |
| NHA/HEC Infrastructure | National infrastructure database | 30 districts |
| GeoJSON Boundaries | District polygon boundaries | 30 polygons (Shapely buffers) |

---

## 🗺️ Geographic Coverage

Pakistan — 30 districts across 7 administrative divisions:

| Province | Districts Covered |
|----------|------------------|
| **Punjab** | Lahore, Faisalabad, Rawalpindi, Multan, Gujranwala, Sialkot, Bahawalpur, Sargodha, Gujrat, Sahiwal |
| **Sindh** | Karachi, Hyderabad, Sukkur, Larkana, Nawabshah |
| **KPK** | Peshawar, Mardan, Abbottabad, Swat, Mansehra |
| **Balochistan** | Quetta, Turbat, Khuzdar, Chaman, Gwadar |
| **ICT** | Islamabad |
| **GB** | Gilgit, Skardu |
| **AJK** | Muzaffarabad, Mirpur |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core language |
| **Pandas / NumPy** | Tabular data manipulation |
| **GeoPandas** | Geospatial DataFrame operations |
| **Shapely** | Geometry creation and operations |
| **PyProj** | Coordinate reference system transformations |
| **SQLite3** | Embedded spatial database (PostGIS simulation) |
| **Streamlit** | Interactive web dashboard |
| **Plotly** | Interactive charts and maps |
| **Folium** | Leaflet.js map integration |
| **Click** | CLI framework |
| **tqdm** | Progress bars |

---

## 📈 Validation Methodology

The quality scoring system operates on a 100-point scale:

```
Quality Score = Completeness (40pts) + Uniqueness (30pts) + Bounds (30pts)

Per-dataset score = Σ(check_scores) / Σ(max_scores) × 100
  PASS check → 2 points
  WARN check → 1 point
  FAIL check → 0 points
```

Checks performed:
- **Schema Validation** — required columns present and correctly typed
- **Spatial Bounds** — all coordinates within Pakistan BBOX (60-77.5°E, 23-37.5°N)
- **Completeness** — null percentage in critical fields (>0%=WARN, >5%=FAIL)
- **Uniqueness** — no duplicate primary keys
- **Value Ranges** — percentages in [0,100], AQI in [0,500], months in [1,12]

---

## 👤 Author

**Haris Hussain**
- 🎓 BSc Space Science | University of Punjab, Lahore, Pakistan
- 📊 Specialisation: GIS, Remote Sensing, Environmental Data Science
- 🛠️ Skills: Python, GeoPandas, Rasterio, GDAL, Scikit-learn, Streamlit, Plotly

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.

---

<p align="center">
  Built with ❤️ for Pakistan's geospatial data science community
</p>
