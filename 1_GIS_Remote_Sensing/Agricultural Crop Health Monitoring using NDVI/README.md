# 🛰 Agricultural Crop Health Monitoring using NDVI

> **Project 1.1 — GIS & Remote Sensing Portfolio**  
> Author: **Haris Hussain** | Space Science, University of the Punjab  
> Technology: Vanilla HTML/CSS/JS · Chart.js · Canvas API · Sentinel-2 Data

---

## 📌 Overview

This project is a fully interactive, browser-based dashboard that simulates **satellite-derived NDVI (Normalized Difference Vegetation Index)** data for monitoring agricultural crop health across the Punjab, Pakistan. It visualizes real-time animated field maps, time-series trends, spectral band comparisons, and yield predictions — all within a single self-contained HTML file.

The app mimics workflows used in professional remote sensing platforms (like QGIS, Google Earth Engine, and ESA SNAP) in a portfolio-ready, visually stunning dark-mode interface with neon accent colors.

---

## 🧮 NDVI Formula

$$NDVI = \frac{NIR - Red}{NIR + Red}$$

| Symbol | Description | Sentinel-2 Band |
|--------|-------------|-----------------|
| NIR    | Near-Infrared reflectance | Band 8 (842 nm) |
| Red    | Visible red reflectance   | Band 4 (665 nm) |

- **Range:** −1.0 to +1.0  
- **Negative values:** Water bodies, clouds, snow  
- **0.0 – 0.2:** Bare soil, stressed/dead vegetation  
- **0.2 – 0.4:** Sparse or stressed crops  
- **0.4 – 0.6:** Moderate/healthy vegetation  
- **> 0.6:** Dense, healthy vegetation canopy  

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **NDVI Map Simulation** | 50×35 animated canvas grid with Perlin-like noise showing real-time NDVI values. Click any cell for metadata. |
| 2 | **NDVI Formula Calculator** | Interactive NIR/Red sliders → live NDVI computation → color swatch output |
| 3 | **Time-Series Chart** | 12-month NDVI trends for Wheat, Rice, Cotton, Sugarcane using Chart.js |
| 4 | **Health Classification Table** | Threshold-based health status with color badges and recommended actions |
| 5 | **Satellite Pass Simulator** | Animated Sentinel-2 ground track canvas with live countdown to next pass |
| 6 | **Band Comparison Chart** | Grouped bar chart of Red vs NIR reflectance across 4 field zones |
| 7 | **Yield Prediction Panel** | Linear regression model (y = a·NDVI + b) with scatter plot visualization |
| 8 | **Metrics Strip** | Real-time top-level KPIs: fields monitored, avg NDVI, stressed & healthy area |

---

## 🏥 Health Classification Thresholds

| NDVI Range | Status    | Badge Color | Estimated Yield |
|-----------|-----------|-------------|-----------------|
| > 0.60    | Excellent | 🟢 Green    | > 4.2 t/ha      |
| 0.40–0.60 | Good      | 🟡 Lime     | 3.0–4.2 t/ha    |
| 0.20–0.40 | Fair      | 🟠 Amber    | 1.5–3.0 t/ha    |
| < 0.20    | Stressed  | 🔴 Red      | < 1.5 t/ha      |

---

## 🛰 Satellite Information — Sentinel-2

| Parameter | Value |
|-----------|-------|
| Satellite | ESA Sentinel-2A / 2B (Copernicus Programme) |
| Orbit Type | Sun-Synchronous (SSO) |
| Altitude | ~786 km |
| Swath Width | 290 km |
| Spatial Resolution | 10 m (Red, NIR bands) |
| Revisit Time | 5 days (with both satellites) |
| Key Bands Used | B4 (Red, 665 nm), B8 (NIR, 842 nm) |
| Coverage | Punjab, Pakistan (29°N–34°N, 70°E–75°E) |

---

## 🎨 NDVI Color Map

```
-1.0  ████  Red         (#FF0000) — Water / Cloud / Bare Rock
 0.0  ████  Yellow      (#FFFF00) — Sparse / Stressed Vegetation
 0.4  ████  Light Green (#90EE90) — Moderate Vegetation
 0.6  ████  Dark Green  (#006400) — Dense, Healthy Canopy
```

---

## 🌾 Crop Zones — Punjab, Pakistan

| Zone   | Crop      | Typical NDVI Peak | Growing Season |
|--------|-----------|-------------------|----------------|
| Zone A | Wheat     | 0.72 (Apr–May)    | Nov → May      |
| Zone B | Rice      | 0.74 (Jul–Sep)    | Jun → Oct      |
| Zone C | Cotton    | 0.68 (Jun–Aug)    | Apr → Oct      |
| Zone D | Sugarcane | 0.65 (year-round) | Mar → Dec      |

---

## 📐 Yield Prediction Model

Linear regression per crop type:

```
Yield (t/ha) = a × NDVI + b
```

| Crop      | a (slope) | b (intercept) |
|-----------|-----------|---------------|
| Wheat     | 5.8       | 0.4           |
| Rice      | 7.2       | 0.3           |
| Cotton    | 4.1       | 0.2           |
| Sugarcane | 42.0      | 5.0           |

---

## ⚙️ Tech Stack

| Component    | Technology |
|--------------|------------|
| Structure    | HTML5 + Semantic markup |
| Styling      | Vanilla CSS (Dark Mode, CSS custom properties, animations) |
| Logic        | Vanilla JavaScript (ES6+) |
| Charts       | Chart.js v4.4 (CDN) |
| Visualization | HTML5 Canvas API |
| Fonts        | Orbitron (headers) · Inter (body) · JetBrains Mono (values) |
| NDVI Noise   | Layered sin/cos (Perlin-like procedural generation) |
| Satellite Sim| SVG + Canvas animation |

---

## 🎓 Learning Outcomes

After completing this project, you will understand:

1. **Remote Sensing Fundamentals** — How NDVI is computed from spectral bands
2. **Satellite Imagery** — Sentinel-2 sensor specifications and revisit cycles
3. **Agricultural Applications** — How vegetation indices relate to crop health & yield
4. **Data Visualization** — Chart.js for scientific time-series and scatter plots
5. **Canvas Programming** — Procedural NDVI map generation with noise functions
6. **Frontend Architecture** — Building rich, self-contained analytical dashboards

---

## 📁 File Structure

```
Agricultural Crop Health Monitoring using NDVI/
├── index.html     ← Single-file application (all-in-one)
└── README.md      ← This documentation file
```

---

## 🚀 Usage

1. Open `index.html` in any modern browser (Chrome, Firefox, Edge)
2. No build step, no server, no dependencies to install
3. Interact with the NDVI map (click cells), adjust formula sliders, change yield inputs

---

## 👤 Author

**Haris Hussain**  
Department of Space Science  
University of the Punjab, Lahore, Pakistan  
Portfolio Project 1.1 — GIS & Remote Sensing Series
