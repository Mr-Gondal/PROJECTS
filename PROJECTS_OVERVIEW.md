# Portfolio Projects Overview

A collection of projects spanning **GIS, Remote Sensing, Data Science & Machine Learning, WebGIS & Web Development, Meteorology & Environmental Science, AI/GIS Integration, and Electronics & Engineering**.

> **Status legend**
> - ✅ **Built** — working code in the folder, runnable today
> - 🚧 **Early-stage** — code exists but runs on a small illustrative dataset
> - 📌 **Spec** — project brief / intended methodology only (no build yet)

**Tech Stack (as actually used in this repo)**: Python, Streamlit, Scikit-learn, Pandas, Plotly, GeoPandas, SQLite, Google Earth Engine (JavaScript), Leaflet, Chart.js, Matplotlib, Folium

---

## 1. GIS & Remote Sensing

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | **Urban Sprawl Analysis of Lahore (2015-2025)** | ✅ Built (GEE script) | FAO GAUL filtered to Pakistan; Landsat multi-temporal NDBI analysis |
| 2 | **Flood Hazard Mapping & Vulnerability Assessment** | ✅ Built (GEE script) | Basic Sentinel-1/DEM workflow — extend when time permits |
| 3 | **Agricultural Crop Health Monitoring using NDVI** | ✅ Built (GEE script) | Sentinel-2 NDVI time series (cloud filter fixed to `< 20%`) |
| 4 | **Deforestation Detection in Northern Pakistan** | ✅ Built (GEE script) | Hansen GFC change analysis, 626-line script |
| 5 | **Site Suitability Analysis for Solar Power Plants** | ✅ Built (GEE script) | MCDA over Punjab, **Pakistan** (country filter fixed from 'India') |

## 2. Programming & Data Science

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | **Automated Satellite Image Processing Pipeline** | ✅ Built | NDVI/NDWI/NDBI/EVI, KMeans LULC, change detection, HTML reports — **synthetic Sentinel-2 data layer (clearly labelled)** |
| 2 | **Spatial Data ETL Pipeline** | ✅ Built | Extract→Transform→Validate→Load to SQLite + dashboard; **read-only hardened SQL Explorer**; synthetic source data (labelled) |
| 3 | **Climate Data Analysis & Visualization Tool** | ✅ Built | Warming stripes, trends, SPI drought index, anomalies — synthetic 50-year dataset (labelled) |
| 4 | **Geospatial Data Visualization Dashboard** | ✅ Built | Folium/Plotly dashboard over curated Pakistan datasets |
| 5 | **Air Quality Analysis & Prediction Model** | ✅ Built | Live OWM API + demo mode; **EPA-2024 AQI conversion (unit-tested)**; leakage-free ML with live-computed metrics |

## 3. WebGIS & Web Development

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | **Interactive Air Quality Monitoring WebGIS** | 📌 Spec | — |
| 2 | **Lahore Traffic Congestion Heat Map** | 📌 Spec | — |
| 3 | **Pakistan Earthquake Tracker & Hazard Map** | ✅ Built | Live USGS API, Leaflet, Chart.js, impact alerts — **XSS-hardened, CSP, pinned CDNs, external JS** |
| 4 | **Heritage Sites of Pakistan - Interactive Tourism Map** | 📌 Spec | — |
| 5 | **Urban Heat Island Detection WebGIS** | 📌 Spec | — |

## 4. Meteorology & Environmental Science

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | **Monsoon Rainfall Pattern Analysis (2010-2024)** | 📌 Spec | CHIRPS + Mann-Kendall planned |
| 2 | **Smog & Air Pollution Hotspot Analysis** | 📌 Spec | MODIS/VIIRS AOD + Getis-Ord planned |
| 3 | **Climate Change Impact on Agricultural Zones** | 🚧 Early-stage | Pipeline runs end-to-end on an illustrative 4-district sample; real WorldClim/CMIP6 ingestion is next |
| 4 | **Wildfire Risk Assessment & Early Warning System** | 📌 Spec | CWRI framework planned |
| 5 | **Glacial Lake Outburst Flood (GLOF) Risk Mapping** | 📌 Spec | Inventory + propagation modelling planned |

## 5. AI & GIS Integration

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | **AI-Powered Land Cover Classification** | 📌 Spec | — |
| 2 | **Building Footprint Extraction from Satellite Imagery** | 📌 Spec | — |
| 3 | **Crop Type Classification using Machine Learning** | 📌 Spec | — |
| 4 | **Flood Extent Mapping with AI** | 📌 Spec | — |
| 5 | **Road Network Extraction using Deep Learning** | 📌 Spec | — |

## 6. Mega Projects

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | **Smart City Dashboard for Lahore** | 📌 Spec | — |
| 2 | **Environmental Monitoring & Climate Change Observatory** | 📌 Spec | — |
| 3 | **Integrated Disaster Management System for Pakistan** | 📌 Spec | — |

## 7. Mini Projects

| # | Project | Status |
|---|---------|--------|
| 1 | Coordinate converter (DD ↔ DMS) | 📌 Spec |
| 2 | Interactive hometown map with landmarks | 📌 Spec |
| 3 | Distance calculator between Pakistan cities | 📌 Spec |
| 4 | Land surface temperature map for Lahore | 📌 Spec |
| 5 | NDVI time-series animation | 📌 Spec |
| 6 | Population density heatmap for Pakistan | 📌 Spec |
| 7 | Elevation profile tool using DEM | 📌 Spec |
| 8 | Geocoding tool for Pakistani addresses | 📌 Spec |
| 9 | Water body detection using NDWI | 📌 Spec |
| 10 | Weather data fetcher & visualizer for Lahore | 📌 Spec |

## 8. Electronics & Engineering

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | RLC Circuit Analysis Suite | ✅ Built | Self-contained interactive HTML simulator |
| 2 | Smart Microgrid Protection Digital Twin | ✅ Built | Self-contained interactive HTML simulator |
| 3–10 | Others (Wokwi simulator, modulation visualizer, classifier, fault detection, IoT dashboard, PCB thermal, link budget, signal analyzer) | 📌 Spec | — |

## Geospatial (standalone case study)

| Project | Status | Notes |
|---|---------|-------|
| **Cyclone Biparjoy rainfall & track analysis** | ✅ Built (notebooks + utils) | GEE/IMERG V07 workflow notebooks, track kinematics utils; EE steps require an authenticated session |
