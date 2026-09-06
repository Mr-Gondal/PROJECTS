# 🌍 Tech Portfolio — GIS, Data Science, WebGIS & AI

A collection of portfolio projects spanning **Geographic Information Systems**, **Data Science & Machine Learning**, **WebGIS & Web Development**, **Meteorology**, and **AI/GIS Integration**.

> **How this repo is organised (honesty first):** every project folder carries a status —
> **✅ Built** (working code you can run) or **📌 Specification / Planned** (project brief describing
> the target scope, no build yet). Check `PROJECTS_OVERVIEW.md` for the full status table.

---

## 🚀 Quick start (built projects)

| Project | Run it with |
|---|---|
| **Air Quality Dashboard** (`2_Programming_Data_Science/Air_Quality_Analysis_Prediction/`) | `pip install -r requirements.txt && streamlit run app.py` — demo data auto-generates; optional live mode via OpenWeatherMap key |
| **Pakistan Earthquake Tracker** (`3_WebGIS_Web_Development/Pakistan Earthquake Tracker & Hazard Map/`) | open `index.html` — live USGS data, no build step |
| **Spatial Data ETL Pipeline** (`2_Programming_Data_Science/Spatial Data ETL Pipeline/`) | `python main.py run --all` then `streamlit run app.py` |
| **Climate Data Tool** (`2_Programming_Data_Science/Climate Data Analysis & Visualization Tool/`) | `streamlit run app.py` (synthetic 50-year dataset, clearly labelled) |
| **Satellite Image Processing Pipeline** (`2_Programming_Data_Science/Automated Satellite Image Processing Pipeline/`) | `streamlit run app.py` (synthetic Sentinel-2 layer, clearly labelled) |
| **RLC / Microgrid simulators** (`8_Electronics_Engineering/…`) | open `index.html` |

Synthetic-data projects are **labelled as synthetic in their READMEs and in-app** — they demonstrate
pipeline architecture, not real-world measurements.

---

## 🧪 Tests & CI

```bash
pip install pytest
pytest tests/ -q        # AQI conversion (EPA 2024) + read-only SQL guard
```

A ready-made GitHub Actions workflow ships at `.github/workflows/ci.yml` — commit it (repo-owner permissions required) to run the suite on every push.

---

## 🛠️ Tech Stack (actually used in this repo)

`Python` `Streamlit` `Scikit-learn` `Pandas` `Plotly` `GeoPandas` `SQLite` `Google Earth Engine (JavaScript)` `Leaflet` `Chart.js` `Matplotlib` `Folium`

---

## 📂 Layout

| Folder | Area |
|--------|------|
| `1_GIS_Remote_Sensing/` | Google Earth Engine scripts (Sentinel-2, Hansen GFC, SRTM) |
| `2_Programming_Data_Science/` | Streamlit dashboards, ETL pipeline, ML prediction |
| `3_WebGIS_Web_Development/` | Leaflet WebGIS apps |
| `4_Meteorology_Environmental/` | Environmental/climate analyses |
| `5_AI_GIS_Integration/` | AI + GIS project specs |
| `6_Mega_Projects/` | Capstone project specs |
| `7_Mini_Projects/` | Mini project specs |
| `8_Electronics_Engineering/` | Interactive electronics simulators + specs |
| `Geospatial/` | Cyclone Biparjoy rainfall/track analysis (GEE notebooks) |
| `certificates/` | Course certificates |

---

## 🔒 Security practices demonstrated

- **Read-only SQL surface** — the ETL dashboard's SQL Explorer validates queries (single `SELECT`/`WITH`/`EXPLAIN` only) **and** opens SQLite via `mode=ro` + `PRAGMA query_only=ON`
- **XSS-hardened WebGIS** — the Earthquake Tracker escapes all API-sourced strings, pins CDN versions (SRI on Leaflet), uses a CSP with no inline handlers, and `rel="noopener noreferrer"` on external links
- **No secrets in git** — API keys via env vars / Streamlit secrets only; generated artifacts (models, DBs, CSVs) are git-ignored
- **Leakage-free ML** — chronological train/test split, scaler + imputation fit on the training split only, metrics computed live (never hard-coded)

---

## 📄 License

MIT — see [LICENSE](LICENSE).
