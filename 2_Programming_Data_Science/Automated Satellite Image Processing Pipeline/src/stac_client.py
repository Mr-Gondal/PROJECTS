"""
stac_client.py — Synthetic STAC / Sentinel-2 data generator.

Mimics the behaviour of a real STAC API client (e.g., pystac-client) but
generates deterministic, realistic numpy arrays entirely in-memory.
No network calls, no API keys required.

Region-specific biophysical profiles ensure plausible spectral signatures:
  • Lahore / Karachi  → dominant urban fabric
  • Islamabad         → mixed urban + forest
  • Gilgit            → high-altitude rock / sparse vegetation / snow
  • Peshawar          → semi-arid agricultural
  • Multan            → irrigated agriculture / desert fringe
"""

from __future__ import annotations

import hashlib
import math
import random
from datetime import date, datetime
from typing import Any

import numpy as np

from src.config import (
    BAND_VALUE_RANGES,
    IMAGE_SIZE,
    REGIONS,
    SENTINEL_BANDS,
)


# ---------------------------------------------------------------------------
# Per-region biophysical profiles
# Each value is the *fraction* of total pixels assigned to each cover type.
# Cover types (order): water, dense_veg, sparse_veg, urban, bare_soil
# ---------------------------------------------------------------------------
_REGION_PROFILES: dict[str, dict[str, Any]] = {
    "Lahore": {
        "fractions": [0.04, 0.10, 0.15, 0.50, 0.21],
        "climate":   "semi-arid subtropical",
    },
    "Karachi": {
        "fractions": [0.08, 0.04, 0.08, 0.55, 0.25],
        "climate":   "arid coastal",
    },
    "Islamabad": {
        "fractions": [0.06, 0.35, 0.25, 0.24, 0.10],
        "climate":   "humid subtropical",
    },
    "Gilgit": {
        "fractions": [0.05, 0.08, 0.20, 0.10, 0.57],
        "climate":   "alpine",
    },
    "Peshawar": {
        "fractions": [0.03, 0.08, 0.30, 0.35, 0.24],
        "climate":   "semi-arid",
    },
    "Multan": {
        "fractions": [0.04, 0.12, 0.28, 0.28, 0.28],
        "climate":   "hot arid",
    },
}

# Spectral centroids per cover type [B02, B03, B04, B08, B11]
_SPECTRAL_CENTROIDS: dict[str, list[float]] = {
    "water":       [0.08, 0.10, 0.07, 0.04, 0.02],
    "dense_veg":   [0.04, 0.07, 0.04, 0.45, 0.08],
    "sparse_veg":  [0.06, 0.09, 0.07, 0.25, 0.15],
    "urban":       [0.12, 0.13, 0.14, 0.16, 0.20],
    "bare_soil":   [0.14, 0.15, 0.18, 0.22, 0.28],
}

_COVER_NAMES = ["water", "dense_veg", "sparse_veg", "urban", "bare_soil"]
_BANDS_ORDER = ["B02", "B03", "B04", "B08", "B11"]


def _seed_for(region: str, year: int, month: int) -> int:
    """Derive a deterministic integer seed from region + date."""
    key = f"{region}-{year}-{month:02d}"
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)


def _seasonal_ndvi_mod(month: int, climate: str) -> float:
    """Return a ±fraction to modulate NIR (vegetation greenness) by season."""
    # Peak monsoon greenness in July-September for most Pakistan regions
    angle = (month - 7) * math.pi / 6          # 0 at peak month
    base  = 0.12 * math.cos(angle)             # ±0.12 modulation
    if climate == "alpine":
        base *= 0.6   # Gilgit — less seasonal swing
    elif climate == "arid coastal":
        base *= 0.4   # Karachi — minimal seasonality
    return base


def _generate_scene_bands(
    region_name: str,
    year: int,
    month: int,
    rows: int,
    cols: int,
    urban_growth: float = 0.0,
) -> dict[str, np.ndarray]:
    """
    Generate a dict of {band_id: np.ndarray(rows, cols)} with realistic
    surface-reflectance values (0–1 float32).

    Parameters
    ----------
    urban_growth : float
        Extra fraction of pixels converted to urban (for temporal change).
    """
    profile = _REGION_PROFILES.get(region_name, _REGION_PROFILES["Lahore"])
    climate = profile["climate"]
    fractions = list(profile["fractions"])

    # Adjust fractions for urban growth scenario
    if urban_growth > 0:
        urban_idx  = 3
        sparse_idx = 2
        gain = min(urban_growth, fractions[sparse_idx])
        fractions[urban_idx]  += gain
        fractions[sparse_idx] -= gain

    rng = np.random.default_rng(_seed_for(region_name, year, month))
    n_pixels = rows * cols

    # Assign cover types to pixels
    pixel_cover = rng.choice(
        len(_COVER_NAMES),
        size=n_pixels,
        p=[f / sum(fractions) for f in fractions],
    )

    nir_mod = _seasonal_ndvi_mod(month, climate)

    bands: dict[str, np.ndarray] = {}
    for b_idx, band_id in enumerate(_BANDS_ORDER):
        arr = np.zeros(n_pixels, dtype=np.float32)
        for c_idx, cover in enumerate(_COVER_NAMES):
            mask = pixel_cover == c_idx
            centroid = _SPECTRAL_CENTROIDS[cover][b_idx]

            # Seasonal modulation only for NIR channel
            if band_id == "B08":
                centroid = np.clip(centroid + nir_mod, 0.02, 0.90)

            noise_std = centroid * 0.12 + 0.01
            arr[mask] = rng.normal(centroid, noise_std, mask.sum()).astype(np.float32)

        # Global clamp to physical range
        lo, hi = BAND_VALUE_RANGES[band_id]
        arr = np.clip(arr, lo, hi)
        bands[band_id] = arr.reshape(rows, cols)

    return bands


class SyntheticSTACClient:
    """
    Drop-in replacement for a real STAC API client.

    All methods return the same data shapes and types as their real
    counterparts so the rest of the pipeline is API-agnostic.
    """

    def __init__(self, image_size: tuple[int, int] = IMAGE_SIZE) -> None:
        self.rows, self.cols = image_size

    # ------------------------------------------------------------------
    def query_sentinel2(
        self,
        region_name: str,
        date_start: str,
        date_end: str,
        max_cloud_cover: float = 10.0,
    ) -> dict[str, Any]:
        """
        Simulate a STAC item-search query.

        Returns
        -------
        dict with keys:
            scene_id, region, bbox, date_start, date_end,
            cloud_cover, platform, processing_level, n_scenes
        """
        if region_name not in REGIONS:
            raise ValueError(
                f"Unknown region '{region_name}'. "
                f"Available: {list(REGIONS.keys())}"
            )

        # Parse dates to pick a representative month
        try:
            t0 = datetime.strptime(date_start, "%Y-%m")
        except ValueError:
            t0 = datetime.strptime(date_start, "%Y-%m-%d")
        try:
            t1 = datetime.strptime(date_end, "%Y-%m")
        except ValueError:
            t1 = datetime.strptime(date_end, "%Y-%m-%d")

        mid_year  = (t0.year + t1.year) // 2
        mid_month = (t0.month + t1.month) // 2 or 6

        # Synthetic cloud cover
        rng = random.Random(_seed_for(region_name, mid_year, mid_month))
        cloud_cover = round(rng.uniform(1.0, max_cloud_cover), 1)

        # Estimate number of available scenes (roughly 5 per month in the range)
        n_months = max(1, (t1.year - t0.year) * 12 + (t1.month - t0.month))
        n_scenes = n_months * 5

        scene_id = f"S2A_MSI_L2A_{region_name.upper()}_{mid_year}{mid_month:02d}01"

        return {
            "scene_id":         scene_id,
            "region":           region_name,
            "bbox":             REGIONS[region_name],
            "date_start":       date_start,
            "date_end":         date_end,
            "representative_date": f"{mid_year}-{mid_month:02d}-01",
            "cloud_cover":      cloud_cover,
            "platform":         "Sentinel-2A",
            "processing_level": "Level-2A (Surface Reflectance)",
            "n_scenes":         n_scenes,
            "bands_available":  list(SENTINEL_BANDS.keys()),
            "pixel_size_m":     10,
        }

    # ------------------------------------------------------------------
    def load_bands(
        self,
        region_name: str,
        scene_id: str,
    ) -> dict[str, np.ndarray]:
        """
        Load all Sentinel-2 bands for a given scene.

        Returns
        -------
        dict mapping band_id → np.ndarray(rows, cols, dtype=float32)
        """
        # Extract year/month from scene_id suffix (fallback to Jan 2022)
        try:
            ymd = scene_id.split("_")[-1]
            year  = int(ymd[:4])
            month = int(ymd[4:6])
        except (IndexError, ValueError):
            year, month = 2022, 1

        return _generate_scene_bands(
            region_name=region_name,
            year=year,
            month=month,
            rows=self.rows,
            cols=self.cols,
        )

    # ------------------------------------------------------------------
    def generate_multi_temporal(
        self,
        region_name: str,
        years: list[int] | None = None,
    ) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
        """
        Generate two time-step band dicts for change detection.

        The later scene (T2) has slightly more urban cover to simulate
        realistic city growth over the interval.

        Returns
        -------
        (bands_t1, bands_t2) — each a dict of band arrays
        """
        if years is None:
            years = [2020, 2024]

        y1, y2 = years[0], years[-1]

        bands_t1 = _generate_scene_bands(
            region_name=region_name,
            year=y1,
            month=6,       # June — post-monsoon dry
            rows=self.rows,
            cols=self.cols,
            urban_growth=0.0,
        )
        bands_t2 = _generate_scene_bands(
            region_name=region_name,
            year=y2,
            month=6,
            rows=self.rows,
            cols=self.cols,
            urban_growth=0.07,   # ~7 % urban expansion over 4 years
        )
        return bands_t1, bands_t2
