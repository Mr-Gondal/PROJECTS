"""
config.py — Configuration constants for the Spatial Data ETL Pipeline.

Defines paths, database settings, Pakistan geographic data, and pipeline
parameters used across all ETL stages.

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

import os

# ─── Directory Paths ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "spatial_db.sqlite")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# ─── CRS Settings ─────────────────────────────────────────────────────────────
DEFAULT_CRS = "EPSG:4326"           # WGS84 Geographic
PAKISTAN_UTM_CRS = "EPSG:32642"    # UTM Zone 42N — covers Pakistan

# ─── Pakistan Bounding Box ────────────────────────────────────────────────────
PAKISTAN_BBOX = {
    "min_lon": 60.0,
    "max_lon": 77.5,
    "min_lat": 23.0,
    "max_lat": 37.5,
}

# ─── Pakistan Districts ───────────────────────────────────────────────────────
PAKISTAN_DISTRICTS = [
    # Punjab
    {"name": "Lahore",       "province": "Punjab",      "lat": 31.5204, "lon": 74.3587, "area_km2": 1772,  "pop": 13095000},
    {"name": "Faisalabad",   "province": "Punjab",      "lat": 31.4180, "lon": 73.0790, "area_km2": 5856,  "pop": 3640000},
    {"name": "Rawalpindi",   "province": "Punjab",      "lat": 33.5651, "lon": 73.0169, "area_km2": 5286,  "pop": 2230000},
    {"name": "Multan",       "province": "Punjab",      "lat": 30.1575, "lon": 71.5249, "area_km2": 3720,  "pop": 1872000},
    {"name": "Gujranwala",   "province": "Punjab",      "lat": 32.1877, "lon": 74.1945, "area_km2": 3622,  "pop": 2027000},
    {"name": "Sialkot",      "province": "Punjab",      "lat": 32.4945, "lon": 74.5229, "area_km2": 3016,  "pop": 3893000},
    {"name": "Bahawalpur",   "province": "Punjab",      "lat": 29.3956, "lon": 71.6836, "area_km2": 24830, "pop": 3668000},
    {"name": "Sargodha",     "province": "Punjab",      "lat": 32.0836, "lon": 72.6711, "area_km2": 5854,  "pop": 3490000},
    {"name": "Gujrat",       "province": "Punjab",      "lat": 32.5742, "lon": 74.0779, "area_km2": 3192,  "pop": 3101000},
    {"name": "Sahiwal",      "province": "Punjab",      "lat": 30.6682, "lon": 73.1084, "area_km2": 3201,  "pop": 2207000},
    # Sindh
    {"name": "Karachi",      "province": "Sindh",       "lat": 24.8607, "lon": 67.0011, "area_km2": 3527,  "pop": 16094000},
    {"name": "Hyderabad",    "province": "Sindh",       "lat": 25.3960, "lon": 68.3578, "area_km2": 1006,  "pop": 1732000},
    {"name": "Sukkur",       "province": "Sindh",       "lat": 27.7052, "lon": 68.8574, "area_km2": 5165,  "pop": 841000},
    {"name": "Larkana",      "province": "Sindh",       "lat": 27.5590, "lon": 68.2137, "area_km2": 7738,  "pop": 1522000},
    {"name": "Nawabshah",    "province": "Sindh",       "lat": 26.2442, "lon": 68.4100, "area_km2": 4051,  "pop": 1477000},
    # KPK
    {"name": "Peshawar",     "province": "KPK",         "lat": 34.0150, "lon": 71.5249, "area_km2": 1257,  "pop": 2981000},
    {"name": "Mardan",       "province": "KPK",         "lat": 34.1986, "lon": 72.0404, "area_km2": 1632,  "pop": 2373000},
    {"name": "Abbottabad",   "province": "KPK",         "lat": 34.1464, "lon": 73.2117, "area_km2": 1967,  "pop": 1332000},
    {"name": "Swat",         "province": "KPK",         "lat": 35.2227, "lon": 72.4258, "area_km2": 5337,  "pop": 2309000},
    {"name": "Mansehra",     "province": "KPK",         "lat": 34.3333, "lon": 73.2000, "area_km2": 4579,  "pop": 1574000},
    # Balochistan
    {"name": "Quetta",       "province": "Balochistan", "lat": 30.1798, "lon": 66.9750, "area_km2": 2653,  "pop": 1001000},
    {"name": "Turbat",       "province": "Balochistan", "lat": 26.0022, "lon": 63.0440, "area_km2": 44819, "pop": 682000},
    {"name": "Khuzdar",      "province": "Balochistan", "lat": 27.8120, "lon": 66.6270, "area_km2": 37739, "pop": 600000},
    {"name": "Chaman",       "province": "Balochistan", "lat": 30.9126, "lon": 66.4512, "area_km2": 8253,  "pop": 250000},
    {"name": "Gwadar",       "province": "Balochistan", "lat": 25.1216, "lon": 62.3254, "area_km2": 12637, "pop": 91000},
    # ICT / GB / AJK
    {"name": "Islamabad",    "province": "ICT",         "lat": 33.7294, "lon": 73.0931, "area_km2": 906,   "pop": 1145000},
    {"name": "Gilgit",       "province": "GB",          "lat": 35.9220, "lon": 74.3085, "area_km2": 42000, "pop": 330000},
    {"name": "Skardu",       "province": "GB",          "lat": 35.3197, "lon": 75.5464, "area_km2": 55000, "pop": 258000},
    {"name": "Muzaffarabad", "province": "AJK",         "lat": 34.3700, "lon": 73.4700, "area_km2": 1642,  "pop": 725000},
    {"name": "Mirpur",       "province": "AJK",         "lat": 33.1477, "lon": 73.7503, "area_km2": 1010,  "pop": 456000},
]

# ─── Province color mapping (for visualization) ───────────────────────────────
PROVINCE_COLORS = {
    "Punjab":      "#f59e0b",
    "Sindh":       "#3b82f6",
    "KPK":         "#10b981",
    "Balochistan": "#ef4444",
    "ICT":         "#8b5cf6",
    "GB":          "#06b6d4",
    "AJK":         "#f97316",
}

# ─── AQI categories ───────────────────────────────────────────────────────────
AQI_CATEGORIES = [
    {"label": "Good",            "min": 0,   "max": 50,  "color": "#22c55e"},
    {"label": "Moderate",        "min": 51,  "max": 100, "color": "#eab308"},
    {"label": "Unhealthy Sens.", "min": 101, "max": 150, "color": "#f97316"},
    {"label": "Unhealthy",       "min": 151, "max": 200, "color": "#ef4444"},
    {"label": "Very Unhealthy",  "min": 201, "max": 300, "color": "#a855f7"},
    {"label": "Hazardous",       "min": 301, "max": 500, "color": "#7f1d1d"},
]

# ─── Population density thresholds (people/km²) ───────────────────────────────
POP_DENSITY_THRESHOLDS = {
    "Very High": 5000,
    "High":      1000,
    "Medium":    300,
    "Low":       0,
}

# ─── Pipeline metadata ────────────────────────────────────────────────────────
PIPELINE_VERSION = "1.0.0"
PIPELINE_NAME    = "Pakistan Spatial ETL"
