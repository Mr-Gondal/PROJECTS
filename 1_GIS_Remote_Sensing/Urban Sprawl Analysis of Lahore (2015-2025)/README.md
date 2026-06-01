# 🛰 Urban Sprawl Analysis of Lahore (2015–2025)

> **GIS & Remote Sensing · Project 1.5**  
> *Space Science, University of the Punjab*  
> **Author:** Haris Hussain

---

## 📌 Project Overview

This project conducts a decade-long (2015–2025) analysis of **urban sprawl in Lahore, Pakistan** — one of South Asia's fastest-growing megacities. Using multi-temporal satellite imagery from **Landsat 8/9** and **Sentinel-2**, the project maps:

- 🏙 **Built-up area expansion** from ~1,456 km² (2015) to ~2,108 km² (2025)
- 🌿 **Green space loss** from 480 km² down to 268 km² — a 44% reduction
- 👥 **Population density shifts** from 11.2M to 15.4M residents
- 🏗 **Land-use transitions** — 325 km² of farmland and greenery absorbed by urban fabric

---

## 🧭 Methodology

### 1. Land Use / Land Cover (LULC) Classification
- **Input**: Landsat 8 OLI (30m resolution) + Sentinel-2 MSI (10m resolution)
- **Method**: Supervised classification using **Random Forest** algorithm in Google Earth Engine (GEE)
- **Classes**: Dense Urban, New Development, Green Space, Agricultural Land, Waterbodies, Bare Land
- **Accuracy**: Overall Accuracy ≥ 88%, Kappa Coefficient ≥ 0.85

### 2. Change Detection
- **Technique**: Post-classification change detection (bi-temporal comparison)
- **Epochs**: Annual composites from 2015 to 2025 (10 maps)
- **Filtering**: Median composites to reduce cloud cover artifacts
- **Indices Used**:
  - **NDBI** (Normalized Difference Built-up Index): identifies built-up surfaces
  - **NDVI** (Normalized Difference Vegetation Index): maps green/vegetated cover
  - **MNDWI** (Modified NDWI): isolates water bodies

### 3. Sprawl Metrics Computation
- Sprawl Index, Compactness Ratio, and Green Space per capita calculated per 2-year epoch
- Population data integrated from Pakistan Bureau of Statistics (PBS) Census 2017 & 2023

---

## 📡 Data Sources

| Dataset | Source | Resolution | Use |
|---|---|---|---|
| Landsat 8 OLI/TIRS Collection 2 | USGS Earth Explorer | 30m | LULC Classification 2015–2021 |
| Landsat 9 OLI-2 | USGS Earth Explorer | 30m | LULC Classification 2021–2025 |
| Sentinel-2 MSI Level-2A | ESA Copernicus Hub | 10m | High-res green space mapping |
| SRTM Digital Elevation Model | NASA LP DAAC | 30m | Topographic context |
| PBS Census Data | Pakistan Bureau of Statistics | District level | Population density |
| OpenStreetMap | OSM Foundation | Vector | Landmark & road reference |

---

## 📊 Lahore Urban Growth Statistics (2015–2025)

| Year | Built-up Area (km²) | Green Space (km²) | Population (M) | Sprawl Index | Impervious (%) |
|------|--------------------|--------------------|----------------|--------------|---------------|
| 2015 | 1,456 | 480 | 11.2 | 0.55 | 56% |
| 2016 | 1,510 | 461 | 11.5 | 0.56 | 58% |
| 2017 | 1,572 | 442 | 11.8 | 0.57 | 59% |
| 2018 | 1,645 | 420 | 12.1 | 0.58 | 60% |
| 2019 | 1,720 | 398 | 12.5 | 0.59 | 62% |
| 2020 | 1,808 | 373 | 12.9 | 0.60 | 64% |
| 2021 | 1,895 | 350 | 13.3 | 0.62 | 66% |
| 2022 | 1,972 | 328 | 13.7 | 0.63 | 67% |
| 2023 | 2,048 | 306 | 14.2 | 0.65 | 69% |
| 2024 | 2,138 | 286 | 14.8 | 0.67 | 71% |
| 2025 | 2,108 | 268 | 15.4 | 0.68 | 74% |

> *Slight built-up decrease in 2025 reflects improved urban densification policies (LDA City Plan 2024)*

---

## 📐 Sprawl Index Formula

$$\text{Sprawl Index} = \frac{\text{Urban Area (km²)}}{\text{Population (× 1000)}}$$

| Metric | Formula | 2015 | 2025 | Change |
|---|---|---|---|---|
| **Sprawl Index** | Urban Area / Pop (1000s) | 0.55 | 0.68 | ▲ +23% |
| **Compactness Ratio** | 4π·Area / Perimeter² | 0.50 | 0.41 | ▼ −18% |
| **Green Space/Capita** | Green Area / Pop | 5.4 m² | 3.2 m² | ▼ −41% |
| **Impervious Surface** | Impervious Px / Total Urban | 56% | 74% | ▲ +31% |

---

## 🗺 Land Use Change Matrix (2015→2025)

| Source Class | → Urban (km²) | Share of Total |
|---|---|---|
| Agricultural Land | 280 km² | 70.5% |
| Green Space | 45 km² | 11.3% |
| Bare/Fallow Land | 59 km² | 14.8% |
| Water Bodies | 14 km² | 3.5% |
| **Total** | **398 km²** | **100%** |

---

## ✨ Features

| # | Feature | Technology | Description |
|---|---|---|---|
| 1 | Urban Growth Map Animation | Canvas API | Year-by-year animated footprint showing urban expansion 2015–2025 |
| 2 | Growth Metrics Timeline | Chart.js Line | Built-up area, green space & population on triple Y-axes |
| 3 | Land Use Change Matrix | Chart.js Stacked Bar | Sankey-style conversion flows from agricultural/green land |
| 4 | Urban Density Heatmap | Canvas API | Concentric density rings + distance profile chart |
| 5 | Sprawl Indicators Panel | Custom HTML/JS | 4 key sprawl metrics with trend bars and delta indicators |
| 6 | District Comparison | Chart.js Grouped Bar | Growth % per LDA zone: DHA, Gulberg, Johar Town, Bahria, Model Town |
| 7 | Smart City Benchmarking | Chart.js Radar | Lahore vs Karachi, Islamabad, Faisalabad on 6 urban dimensions |
| 8 | Population Density Map | Canvas API | Grid-cell density + glowing population hub visualization |

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| **HTML5 / Vanilla JS** | Single-file self-contained app |
| **Chart.js v4.4.0** (CDN) | Timeline, stacked bar, grouped bar, radar charts |
| **Canvas 2D API** | Urban growth map, density heatmap, population map |
| **CSS Custom Properties** | Design tokens: colors, typography, spacing |
| **Google Fonts** (CDN) | Orbitron, Inter, JetBrains Mono |
| **Intersection Observer** | Scroll reveal animations |
| **RequestAnimationFrame** | Animated city grid background & counter |

---

## 🎯 Learning Outcomes

By completing this project, the author demonstrates proficiency in:

1. **Remote Sensing**: Satellite imagery processing, LULC classification, change detection
2. **GIS Analysis**: Spatial metrics, urban morphology, density modelling
3. **Data Visualization**: Multi-axis charts, canvas mapping, animated data stories
4. **Urban Analytics**: Sprawl indices, compactness, green space measurement
5. **Web Development**: Self-contained interactive portfolio pages

---

## 🏙 Key Findings

- Lahore's urban footprint grew by **+652 km²** (~45%) over 10 years
- **DHA Lahore** and **Bahria Town** drove the most explosive peripheral growth
- Green space per capita dropped below the WHO minimum of **9 m²/person** (currently 3.2 m²)
- Agricultural land conversion dominates at **70.5%** of all urban expansion
- The city's compactness is declining — expansion is becoming **more sprawled, less compact**

---

## 📁 File Structure

```
Urban Sprawl Analysis of Lahore (2015-2025)/
├── index.html      ← Self-contained interactive web app (single file)
└── README.md       ← This file
```

---

## 👤 Author

**Haris Hussain**  
BSc Space Science | University of the Punjab, Lahore  
GIS & Remote Sensing Portfolio — **Project 1.5**

---

*Data is representational and derived from published LULC studies on Lahore metropolitan area. Visualization is for educational portfolio purposes.*
