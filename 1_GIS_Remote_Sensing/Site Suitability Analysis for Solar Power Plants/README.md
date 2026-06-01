# ☀️ Site Suitability Analysis for Solar Power Plants in Pakistan

> **Project 1.4** — GIS & Remote Sensing Portfolio  
> **Author:** Haris Hussain | Space Science, University of the Punjab, Lahore  
> **Tool Stack:** Vanilla JS · Chart.js · HTML5 Canvas · GIS Spatial Analysis  

---

## 📌 Project Overview

This project applies **Multi-Criteria Evaluation (MCE)** and **Weighted Overlay Analysis** to systematically identify the most suitable locations for utility-scale solar power plants across Pakistan. The analysis integrates five spatial criteria rasters — solar irradiance (GHI), terrain slope, land cover classification, distance to the national power grid, and distance to road networks — into a single composite suitability index.

The interactive web application presents all analytical results in a self-contained, fully animated visualization tool that simulates a professional GIS energy-planning dashboard.

---

## 🌍 Pakistan Solar Context

| Metric | Value |
|---|---|
| Total solar potential | **2.9 million MW** |
| Current installed solar capacity | ~3,500 MW |
| Peak GHI (Balochistan) | 6.5 kWh/m²/day |
| Average annual sunshine hours | 2,200–3,000 hrs/yr |
| Potential CO₂ reduction | ~120 million tons/yr |
| Target solar share (2030) | 30% of electricity mix |
| Suitable land area (barren + rangeland) | ~59% of Pakistan |

Pakistan receives among the **highest solar irradiance levels in the world**, with Balochistan and Sindh exceeding 2,200–2,400 kWh/m²/yr — well above the threshold for economically viable large-scale solar power.

---

## 🧮 MCE Methodology — Weighted Overlay Analysis

### Framework
The analysis employs **Weighted Linear Combination (WLC)**, a widely-used MCE technique in GIS-based site suitability modeling:

```
S = Σ(wᵢ × xᵢ)     for i = 1 to n criteria
```

Where:
- **S** = composite suitability score (0–1)
- **wᵢ** = weight assigned to criterion i (Σwᵢ = 1)
- **xᵢ** = normalized criterion score (0–1) for each raster cell

### Data Pre-processing Steps
1. **Raster Acquisition** — NASA POWER (GHI), SRTM DEM (slope), ESA WorldCover 2021 (land cover), OSM (roads/grid)
2. **Reprojection** — All rasters projected to `UTM Zone 42N (EPSG:32642)`
3. **Resampling** — Unified 250m × 250m spatial resolution
4. **Normalization** — Linear min-max normalization per criterion layer
5. **Exclusion Zones** — Urban areas, protected forests, water bodies set to score = 0
6. **Overlay** — Weighted sum of all normalized layers

### Normalization Method
```
x_normalized = (x - x_min) / (x_max - x_min)          # direct (GHI, flat slope)
x_normalized = 1 - (x - x_min) / (x_max - x_min)      # inverse (slope: flat = better)
```

---

## ⚖️ Criteria & Default Weights

| # | Criterion | Data Source | Resolution | Default Weight | Rationale |
|---|---|---|---|---|---|
| 1 | **Solar Irradiance (GHI)** | NASA POWER / PVGIS | 50 km → interpolated | **35%** | Primary driver of energy output |
| 2 | **Slope / Terrain** | SRTM DEM | 30m | **20%** | Slopes <5° required for panel mounting |
| 3 | **Land Cover** | ESA WorldCover 2021 | 10m | **20%** | Barren/desert land avoids food security conflicts |
| 4 | **Distance to Power Grid** | NEPRA / OSM | Vector | **15%** | Reduces transmission infrastructure cost |
| 5 | **Distance to Roads** | OpenStreetMap | Vector | **10%** | Affects construction access & O&M logistics |
| — | **Total** | — | — | **100%** | — |

### Land Cover Suitability Scoring
| Land Cover Class | ESA Code | Suitability Score |
|---|---|---|
| Barren / Sparse Vegetation | 60 | 1.00 (Excellent) |
| Shrubland / Rangeland | 20 | 0.75 (Good) |
| Herbaceous Vegetation | 30 | 0.60 (Moderate) |
| Agricultural Land | 40 | 0.20 (Poor — food conflicts) |
| Forest | 10 | 0.00 (Excluded) |
| Urban / Built-up | 50 | 0.00 (Excluded) |
| Water Bodies | 80 | 0.00 (Excluded) |

### Slope Suitability Scoring
| Slope Range | Score | Rationale |
|---|---|---|
| 0 – 2° | 1.00 | Ideal — no additional mounting cost |
| 2 – 5° | 0.80 | Suitable — minor adjustment needed |
| 5 – 10° | 0.50 | Marginal — increased cost |
| 10 – 20° | 0.20 | Poor — significant engineering required |
| > 20° | 0.00 | Excluded — not viable |

---

## 📍 Top 5 Candidate Sites

| Rank | Site Name | Region | Area (km²) | GHI (kWh/m²/yr) | Suitability Score | Est. Capacity (MW) |
|---|---|---|---|---|---|---|
| 1 | **Khuzdar Solar Zone** | Balochistan | 850 | 2,310 | **0.91** | 4,250 |
| 2 | **Thar Desert Complex** | Sindh (Thar) | 1,200 | 2,270 | **0.88** | 6,000 |
| 3 | **Chagai Plateau** | W. Balochistan | 650 | 2,350 | **0.86** | 3,250 |
| 4 | **Rahim Yar Khan Plains** | S. Punjab | 420 | 2,110 | **0.79** | 2,100 |
| 5 | **Sanghar Flatlands** | Central Sindh | 380 | 2,050 | **0.74** | 1,900 |

> Sites were ranked by descending composite WLC score. Final selection also applied minimum contiguous patch area (> 50 km²) and exclusion buffers (5 km from urban, 1 km from water).

---

## ⚡ Energy Potential Formulas

### Annual Energy Output (kWh)
```
E_annual = GHI × A × η × PR
```
| Variable | Description | Typical Value |
|---|---|---|
| GHI | Global Horizontal Irradiance (kWh/m²/yr) | 2,050–2,350 |
| A | Panel/site area (m²) | Site-dependent |
| η | Panel efficiency | 18–22% |
| PR | Performance Ratio (system losses) | 75–85% |

### CO₂ Offset
```
CO₂_offset (kg/yr) = E_annual × 0.433
```
*(0.433 kg CO₂/kWh = Pakistan grid emission factor, NEPRA 2023)*

### Homes Powered
```
Homes = E_annual / 4,500 kWh/yr
```
*(Average Pakistani household: ~4,500 kWh/yr)*

### Revenue Estimate
```
Revenue (PKR) = E_annual × PKR 15/kWh
```
*(Approximate solar tariff per NEPRA net metering regime)*

### Installed Capacity
```
Capacity (MW) = Area (km²) × 1,000 × η × 0.2
```

---

## 🗺 Pakistan Land Cover (ESA WorldCover 2021)

| Class | Area % | Solar Suitable? |
|---|---|---|
| Barren / Desert | 44% | ✅ Yes |
| Agricultural | 28% | ❌ No (food security) |
| Rangeland | 15% | ✅ Yes (partial) |
| Forest | 5% | ❌ No (protected) |
| Urban | 4% | ❌ No |
| Water Bodies | 4% | ❌ No |

> **~59% of Pakistan's land area** is potentially suitable for solar development from a land cover perspective.

---

## 🌞 Monthly GHI Profile (kWh/m²/day)

| Site | Jan | Apr | Jun | Aug | Oct | Dec |
|---|---|---|---|---|---|---|
| Chagai Plateau | 5.0 | 7.3 | 8.2 | 7.6 | 6.4 | 4.7 |
| Khuzdar Solar Zone | 4.8 | 7.1 | 8.0 | 7.4 | 6.2 | 4.5 |
| Thar Desert Complex | 4.6 | 6.9 | 7.8 | 7.2 | 5.9 | 4.3 |
| Rahim Yar Khan | 4.2 | 6.4 | 7.2 | 6.7 | 5.5 | 3.9 |
| Sanghar Flatlands | 4.0 | 6.2 | 7.0 | 6.5 | 5.2 | 3.7 |

**Peak solar season:** May–August across all candidate sites.

---

## 🖥 Web Application Features

| Feature | Description |
|---|---|
| **Interactive Suitability Map** | 60×40 cell grid of Pakistan, color-coded by WLC score, hover to inspect cells |
| **Multi-Criteria Weight Sliders** | Adjust 5 criteria weights in real-time |
| **Animated Site Pins** | 5 recommended sites pulse with glow animation |
| **Monthly GHI Chart** | Chart.js line chart Jan–Dec for all sites |
| **Comparison Bar Chart** | GHI vs Score vs Area for candidate sites |
| **Land Cover Doughnut Chart** | Pakistan land cover with suitability flags |
| **Criteria Weight Polar Chart** | Live polar area chart |
| **Energy Potential Calculator** | Live calculation of output, CO₂ offset, homes, revenue |
| **Pakistan Solar Stats** | Animated number counters for national metrics |

---

## 🛠 Technology Stack

| Category | Technology |
|---|---|
| Structure | HTML5 Semantic Markup |
| Styling | Vanilla CSS (custom properties, Grid, Flexbox, animations) |
| Logic | Vanilla JavaScript (ES6+, Canvas API) |
| Charts | Chart.js 4.4 (CDN) |
| Map | HTML5 Canvas API (custom 2,400-cell raster renderer) |
| Typography | Google Fonts: Orbitron, Inter, JetBrains Mono |
| Deployment | Single self-contained HTML file |

---

## 📚 Key Learning Outcomes

1. **Multi-Criteria Evaluation (MCE)** — Weighted Linear Combination for spatial decision support
2. **Raster Analysis** — Normalization, reclassification, weighted overlay in GIS
3. **Solar Resource Assessment** — Interpreting GHI/DNI data from NASA POWER / PVGIS
4. **Land Suitability Mapping** — ESA WorldCover classification for energy planning
5. **Terrain Analysis** — SRTM slope derivation and impact on solar farm feasibility
6. **Proximity Analysis** — Euclidean distance from infrastructure (roads, grid lines)
7. **Energy Yield Modeling** — Converting solar resource + area into kWh and MW capacity
8. **Data Visualization** — Communicating spatial analysis results interactively

---

## 📂 Project Files

```
Site Suitability Analysis for Solar Power Plants/
├── index.html                     ← Interactive web dashboard (self-contained)
├── README.md                      ← This document
├── GEE_Solar_Site_Suitability.js  ← Google Earth Engine script for real data
└── step_by_step_guide.txt         ← Step-by-step analysis workflow
```

---

## 👤 Author

**Haris Hussain**  
Department of Space Science  
University of the Punjab, Lahore, Pakistan  

Portfolio Project **1.4** — GIS & Remote Sensing  
*"Harnessing spatial analysis to accelerate Pakistan's renewable energy transition."*

---

*Data Sources: NASA POWER · SRTM (USGS) · ESA WorldCover 2021 · OpenStreetMap · NEPRA · IRENA*
