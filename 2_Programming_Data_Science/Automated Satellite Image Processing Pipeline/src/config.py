"""
config.py — Global configuration constants for the Satellite Image Processing Pipeline.

Defines Pakistan region bounding boxes, Sentinel-2 band mappings,
LULC class definitions, colour palettes, and processing defaults.
"""

# ---------------------------------------------------------------------------
# Pakistan regions — bounding boxes [lon_min, lat_min, lon_max, lat_max]
# ---------------------------------------------------------------------------
REGIONS: dict[str, list[float]] = {
    "Lahore":     [74.1, 31.4, 74.6, 31.7],
    "Karachi":    [66.9, 24.8, 67.2, 25.1],
    "Islamabad":  [72.8, 33.5, 73.2, 33.8],
    "Gilgit":     [74.2, 35.8, 74.6, 36.2],
    "Peshawar":   [71.4, 34.0, 71.8, 34.3],
    "Multan":     [71.3, 30.1, 71.6, 30.4],
}

# ---------------------------------------------------------------------------
# Sentinel-2 band definitions (10 m / 20 m resolution bands)
# ---------------------------------------------------------------------------
SENTINEL_BANDS: dict[str, str] = {
    "B02": "Blue",
    "B03": "Green",
    "B04": "Red",
    "B08": "NIR",
    "B11": "SWIR1",
}

# Typical surface-reflectance value ranges (0–1 scale)
BAND_VALUE_RANGES: dict[str, tuple[float, float]] = {
    "B02": (0.02, 0.30),
    "B03": (0.03, 0.35),
    "B04": (0.02, 0.40),
    "B08": (0.05, 0.80),
    "B11": (0.02, 0.60),
}

# ---------------------------------------------------------------------------
# Land Use / Land Cover classes
# ---------------------------------------------------------------------------
LULC_CLASSES: dict[int, str] = {
    0: "Water",
    1: "Dense Vegetation",
    2: "Sparse Vegetation",
    3: "Urban/Built-up",
    4: "Bare Soil",
}

LULC_COLORS: dict[int, str] = {
    0: "#1a6faf",   # water — blue
    1: "#2d8a4e",   # dense veg — dark green
    2: "#8ab87a",   # sparse veg — light green
    3: "#c0392b",   # urban — red
    4: "#d4b483",   # bare soil — tan
}

# Reverse lookup: class name → integer label
LULC_CLASS_IDS: dict[str, int] = {v: k for k, v in LULC_CLASSES.items()}

# ---------------------------------------------------------------------------
# Spectral index thresholds
# ---------------------------------------------------------------------------
INDEX_THRESHOLDS = {
    "ndvi_vegetation":  0.3,    # NDVI > this → vegetation
    "ndwi_water":       0.0,    # NDWI > this → water
    "ndbi_urban":       0.0,    # NDBI > this → urban/built-up
}

# ---------------------------------------------------------------------------
# Image / processing defaults
# ---------------------------------------------------------------------------
IMAGE_SIZE: tuple[int, int] = (100, 100)   # rows × cols of synthetic scene
DEFAULT_CLUSTERS: int = 5
DEFAULT_CLOUD_PCT: float = 10.0            # percent
DEFAULT_PIXEL_SIZE_M: float = 10.0        # Sentinel-2 native resolution (m)

# ---------------------------------------------------------------------------
# Change-detection classes
# ---------------------------------------------------------------------------
CHANGE_CLASSES: dict[int, str] = {
    0: "No Change",
    1: "Vegetation Gain",
    2: "Vegetation Loss",
    3: "Urban Expansion",
    4: "Water Change",
}

CHANGE_COLORS: dict[int, str] = {
    0: "#aaaaaa",   # no change — grey
    1: "#2d8a4e",   # veg gain — green
    2: "#e67e22",   # veg loss — orange
    3: "#c0392b",   # urban expansion — red
    4: "#1a6faf",   # water change — blue
}

# ---------------------------------------------------------------------------
# Report styling
# ---------------------------------------------------------------------------
REPORT_TITLE = "Pakistan Earth Observation Report"
REPORT_ACCENT_COLOR = "#4a9eff"
REPORT_DARK_BG = "#0d1117"
