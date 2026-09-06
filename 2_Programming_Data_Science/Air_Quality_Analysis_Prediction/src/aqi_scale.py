"""US EPA AQI conversion utilities (2024 breakpoint update).

Pure functions with **zero third-party dependencies** so they can be
unit-tested and reused anywhere (dashboard, CLI, tests).

Why this module exists
----------------------
The previous implementation lived in ``src/data_collector.py`` and used
*closed* concentration bands taken straight from the EPA table
(e.g. 0.0-12.0, 12.1-35.4).  Concentrations landing between the bands
(12.05, 35.45, ...) matched **no** band and fell through to a default that
returned **AQI 0 ("Good")** — dangerously wrong for a health dashboard.

The EPA rule is to **truncate** the concentration to the resolution of the
breakpoint table (0.1 µg/m³ for PM2.5, 1 µg/m³ for PM10) *before* the band
lookup.  Truncation makes the bands contiguous and removes the gap bug
entirely.

Breakpoints follow the US EPA AQI final rule update of May 2024
(PM2.5 "Good" ceiling lowered to 9.0 µg/m³; upper bands adjusted).
PM10 breakpoints are unchanged from the legacy table.
Reference: https://www.epa.gov/system/files/documents/2024-05/2024-aqi-updates.pdf
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Breakpoint tables: (conc_low, conc_high, aqi_low, aqi_high)
# ---------------------------------------------------------------------------
PM25_BANDS = [
    (0.0, 9.0, 0, 50),        # Good
    (9.1, 35.4, 51, 100),     # Moderate
    (35.5, 55.4, 101, 150),   # Unhealthy for Sensitive Groups
    (55.5, 125.4, 151, 200),  # Unhealthy
    (125.5, 225.4, 201, 300), # Very Unhealthy
    (225.5, 425.4, 301, 500), # Hazardous
]

PM10_BANDS = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 604, 301, 500),
]

# AQI category (label, color) — single source of truth for the whole app
AQI_CATEGORIES = [
    (50,  "Good",                     "#52b788"),
    (100, "Moderate",                 "#f9c74f"),
    (150, "Unhealthy (Sensitive)",    "#f8961e"),
    (200, "Unhealthy",                "#e63946"),
    (300, "Very Unhealthy",           "#9d4edd"),
    (500, "Hazardous",                "#6a040f"),
]


def _is_valid_number(value) -> bool:
    if value is None:
        return False
    try:
        f = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(f) and f >= 0.0


def _piecewise_aqi(conc: float, bands, resolution: float) -> int:
    """Map a concentration to AQI using truncation + piecewise linear I-Q."""
    # EPA rule: truncate (floor) to the table's resolution — never round.
    # The tiny epsilon compensates for binary-float artifacts so that
    # e.g. 9.1 is treated as exactly 9.1 (not 9.099999… → 9.0).
    c = math.floor(conc / resolution + 1e-9) * resolution
    c = round(c, 6)

    for c_lo, c_hi, i_lo, i_hi in bands:
        if c <= c_hi:
            if c_hi == c_lo:
                return i_lo
            frac = (c - c_lo) / (c_hi - c_lo)
            return int(round(i_lo + frac * (i_hi - i_lo)))

    # Above the top of the scale → cap at the maximum AQI
    return bands[-1][3]


def pm25_to_aqi(pm25: Optional[float]) -> Optional[int]:
    """Convert PM2.5 concentration (µg/m³, 24-h) to US EPA AQI (2024 bands)."""
    if not _is_valid_number(pm25):
        return None
    return _piecewise_aqi(float(pm25), PM25_BANDS, resolution=0.1)


def pm10_to_aqi(pm10: Optional[float]) -> Optional[int]:
    """Convert PM10 concentration (µg/m³, 24-h) to US EPA AQI."""
    if not _is_valid_number(pm10):
        return None
    return _piecewise_aqi(float(pm10), PM10_BANDS, resolution=1.0)


def aqi_from_pollutant(target: str, value: Optional[float]) -> Optional[int]:
    """AQI from a predicted pollutant value, if that pollutant has a scale.

    Only PM2.5 and PM10 have implemented breakpoints; other pollutants
    (NO2, SO2, CO, O3) use different units/averaging periods and return
    ``None`` so the UI can show the raw concentration instead of a
    misleading category.
    """
    converters = {"pm25": pm25_to_aqi, "pm10": pm10_to_aqi}
    conv = converters.get(target.lower())
    return conv(value) if conv else None


def aqi_category(aqi: Optional[float]) -> Tuple[str, str]:
    """Return (label, hex_color) for an AQI value."""
    if aqi is None or not _is_valid_number(aqi):
        return "No Data", "#6c757d"
    for ceiling, label, color in AQI_CATEGORIES:
        if aqi <= ceiling:
            return label, color
    return AQI_CATEGORIES[-1][1], AQI_CATEGORIES[-1][2]
