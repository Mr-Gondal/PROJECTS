# 🌲 Deforestation Detection in Northern Pakistan
### GIS & Remote Sensing Portfolio · Project 1.2

> **Author:** Haris Hussain | **Program:** Space Science | **University:** University of the Punjab, Lahore
> **Project Code:** 1_GIS_Remote_Sensing / Proj-1.2 | **Year:** 2024

---

## 📌 Overview

This project detects and visualizes **forest cover change** in the **KPK (Khyber Pakhtunkhwa) and Gilgit-Baltistan** regions of Northern Pakistan using multi-temporal satellite imagery. The analysis spans **2015–2024**, leveraging Landsat-8/9 OLI imagery processed via Google Earth Engine (GEE) with NDVI differencing and Random Forest classification.

The deliverable is a fully self-contained, interactive **environmental monitoring dashboard** built in HTML/CSS/JavaScript — no server required.

---

## 🛰️ Satellite Data Sources

| Source | Sensor | Resolution | Bands Used | Archive |
|--------|--------|-----------|------------|---------|
| USGS EarthExplorer | Landsat-8 OLI | 30 m | B3, B4, B5, B6 | 2015–2021 |
| USGS EarthExplorer | Landsat-9 OLI-2 | 30 m | B3, B4, B5, B6 | 2021–2024 |
| ESA Copernicus Hub | Sentinel-2 MSI | 10 m | B2, B3, B4, B8 | 2017–2024 |
| Google Earth Engine | Composite | 30–10 m | Seasonal median | 2015–2024 |

**Band Assignments (False-Color Composite):**
- **B5 (NIR)** → Red channel → Dense vegetation appears bright red
- **B4 (Red)** → Green channel → Sparse veg appears pink
- **B3 (Green)** → Blue channel → Water appears dark blue
- **B6 (SWIR-1)** → Used for moisture & burn detection

---

## 🔬 Methodology

### Change Detection Algorithm

```
1. Pre-processing
   ├── Atmospheric correction (LEDAPS/LaSRC)
   ├── Cloud masking (Fmask algorithm, CFMask)
   └── Seasonal composite generation (median, Jun–Sep)

2. Feature Extraction
   ├── NDVI  = (NIR - Red) / (NIR + Red)
   ├── NDWI  = (Green - NIR) / (Green + NIR)
   ├── SAVI  = ((NIR - Red) / (NIR + Red + 0.5)) * 1.5
   └── NBR   = (NIR - SWIR) / (NIR + SWIR)

3. Land Cover Classification
   ├── Random Forest Classifier (500 trees)
   ├── Support Vector Machine (RBF kernel, C=10)
   ├── Training samples: 2,400 ground-truth points
   └── Classes: Dense Forest | Sparse Forest | Deforested | Non-Forest | Water

4. Change Detection
   ├── Post-classification comparison (2015 → 2024)
   ├── NDVI difference raster (ΔNDVIₜ = NDVIₜ₂₀₂₄ - NDVIₜ₂₀₁₅)
   ├── Threshold: ΔNDVI < -0.15 → Deforestation detected
   └── Minimum mapping unit: 0.09 ha (1 pixel × 1 pixel)

5. Accuracy Assessment
   ├── Overall Accuracy: 94.3%
   ├── Kappa Coefficient: 0.91
   └── Validation set: 480 independent points (20/80 split)
```

### Key Spectral Indices

| Index | Formula | Purpose |
|-------|---------|---------|
| NDVI | (NIR - R) / (NIR + R) | Vegetation health & density |
| NDWI | (G - NIR) / (G + NIR) | Water body mapping |
| SAVI | ((NIR - R) / (NIR + R + L)) × (1+L) | Soil-adjusted veg index |
| NBR | (NIR - SWIR) / (NIR + SWIR) | Burn scar detection |
| EVI | 2.5 × (NIR-R)/(NIR+6R-7.5B+1) | Enhanced vegetation index |

---

## ✨ Dashboard Features

| # | Feature | Technology | Description |
|---|---------|-----------|-------------|
| 1 | Before/After Map | Canvas API | 50×35 grid, drag divider to compare 2015 vs 2024 |
| 2 | Change Detection Stats | Vanilla JS | Animated counters for 6 key metrics |
| 3 | Yearly Timeline | Chart.js Line | 2015–2024 forest cover with event annotations |
| 4 | District Comparison | Chart.js Bar | Horizontal bars for 5 KPK/GB districts |
| 5 | Cause Analysis | Chart.js Donut | 5-category deforestation cause breakdown |
| 6 | Satellite Data Panel | HTML/CSS | Sensor metadata, band descriptions, composite info |
| 7 | NDVI Change Panel | Chart.js Bar + Custom | Grouped bars + delta indicators for 5 zones |
| 8 | Alert Feed | Vanilla JS | 5 severity-coded real-time mock alerts |
| — | Particle Background | Canvas API | Floating tree emoji particles |
| — | Data Ticker | CSS Animation | Scrolling live data feed strip |

---

## 📊 District Forest Loss Statistics (2015–2024)

| District | Region | Forest 2015 (km²) | Forest 2024 (km²) | Loss (km²) | Loss (%) | Severity |
|----------|--------|-------------------|-------------------|-----------|---------|---------|
| Kohistan | KPK | 1,820 | 1,303 | 517 | **28.4%** | 🔴 Critical |
| Dir (Upper) | KPK | 1,240 | 966 | 274 | **22.1%** | 🔴 Critical |
| Swat | KPK | 1,580 | 1,269 | 311 | **19.7%** | 🟠 High |
| Chitral | KPK | 2,100 | 1,799 | 301 | **14.3%** | 🟡 Moderate |
| Gilgit-Baltistan | GB | 3,240 | 2,974 | 266 | **8.2%** | 🟢 Lower |
| **Total** | **KPK+GB** | **9,980** | **8,311** | **1,669** | **−16.7%** | — |

---

## 🌿 NDVI Zone Analysis

| Zone | NDVI 2015 | NDVI 2024 | Δ NDVI | % Change | Status |
|------|-----------|-----------|--------|---------|--------|
| Swat Valley | 0.71 | 0.42 | **−0.29** | −40.8% | 🔴 Critical |
| Kohistan Central | 0.74 | 0.38 | **−0.36** | −48.6% | 🔴 Severe |
| Upper Dir | 0.66 | 0.44 | **−0.22** | −33.3% | 🟠 High |
| Chitral Valley | 0.58 | 0.46 | **−0.12** | −20.7% | 🟡 Moderate |
| GB Central | 0.62 | 0.55 | **−0.07** | −11.3% | 🟢 Low |

---

## 🔍 Deforestation Cause Breakdown

| Cause | Share | Notes |
|-------|-------|-------|
| Illegal Logging | 45% | Timber trade, fuelwood extraction |
| Agricultural Expansion | 25% | Terrace farming extending into forest margins |
| Urbanization | 15% | Urban sprawl in KPK valley floors |
| Forest Fires | 10% | Drought-driven fires; 2022 heatwave impact |
| Other | 5% | Infrastructure, mining, landslides |

---

## 🛠️ Tech Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Core Language | HTML5 / CSS3 / JavaScript (ES6+) | Vanilla |
| Charts | Chart.js | 4.4.0 (CDN) |
| Fonts | Google Fonts (Orbitron, Inter, JetBrains Mono) | CDN |
| Remote Sensing | Landsat-8/9 (USGS), Sentinel-2 (ESA) | — |
| Processing Platform | Google Earth Engine | JavaScript API |
| Classification | Random Forest + SVM | GEE built-in |
| Design | Dark mode glassmorphism, CSS animations | Custom |

---

## 📚 Learning Outcomes

1. **Multi-temporal land cover classification** using Landsat OLI imagery
2. **NDVI differencing** for vegetation change quantification
3. **Random Forest classifier** training and accuracy assessment in GEE
4. **Post-classification change detection** and area statistics computation
5. **False-color composite** interpretation for forest mapping
6. **Interactive data visualization** with Chart.js and Canvas API
7. **Environmental dashboard design** with dark mode and animated UI
8. **Spatial analysis** of deforestation drivers in mountain ecosystems

---

## 📁 File Structure

```
Deforestation Detection in Northern Pakistan/
├── index.html          ← Full self-contained dashboard (all-in-one)
└── README.md           ← This file
```

---

## 🚀 How to Run

Simply open `index.html` in any modern browser. No server, no build step, no dependencies to install. All libraries are loaded from CDN.

```bash
# Windows
start index.html

# Or drag & drop into Chrome / Firefox / Edge
```

> **Requirements:** Modern browser with Canvas & Chart.js support (Chrome 90+, Firefox 88+, Edge 90+)

---

## 📜 References & Data Credits

- USGS Landsat Collection 2: https://earthexplorer.usgs.gov
- ESA Copernicus Sentinel Hub: https://scihub.copernicus.eu
- Google Earth Engine: https://earthengine.google.com
- Pakistan Forest Institute (PFI) district-level ground truth
- WWF Pakistan deforestation reports (2019, 2022)
- IPCC Land Use Change Guidelines (2019)

---

*© 2024 Haris Hussain · Space Science · University of the Punjab, Lahore · GIS & Remote Sensing Portfolio · Project 1.2*
