"""
utils.py — Shared utility helpers for the Satellite Image Processing Pipeline.

Provides:
  • GeoJSON helpers (bbox → polygon)
  • Array → colourmap → base64 PNG conversion
  • Folium map builder with image overlay
  • Human-friendly formatting functions
  • Season detection for Pakistan climate
"""

from __future__ import annotations

import base64
import io
from typing import Any

import folium  # type: ignore
import matplotlib
matplotlib.use("Agg")   # headless backend — must be set before pyplot import
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


# ---------------------------------------------------------------------------
# GeoJSON helpers
# ---------------------------------------------------------------------------

def bbox_to_polygon(bbox: list[float]) -> dict[str, Any]:
    """
    Convert a bounding box to a GeoJSON Polygon feature.

    Parameters
    ----------
    bbox : [lon_min, lat_min, lon_max, lat_max]

    Returns
    -------
    GeoJSON-compatible dict (Feature with Polygon geometry)
    """
    lon_min, lat_min, lon_max, lat_max = bbox
    coords = [
        [lon_min, lat_min],
        [lon_max, lat_min],
        [lon_max, lat_max],
        [lon_min, lat_max],
        [lon_min, lat_min],  # close ring
    ]
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords],
        },
        "properties": {},
    }


# ---------------------------------------------------------------------------
# Array → colourmap → base64 PNG
# ---------------------------------------------------------------------------

def array_to_colormap_image(
    arr: np.ndarray,
    colormap: str = "RdYlGn",
    vmin: float | None = None,
    vmax: float | None = None,
    figsize: tuple[float, float] = (4, 4),
    dpi: int = 100,
) -> str:
    """
    Render a 2-D float array as a colourmap PNG and return it as a
    base64-encoded string suitable for embedding in HTML or Streamlit.

    Parameters
    ----------
    arr      : 2-D float array
    colormap : matplotlib colourmap name
    vmin     : minimum value for colourmap normalisation
    vmax     : maximum value for colourmap normalisation
    figsize  : (width_inches, height_inches)
    dpi      : resolution

    Returns
    -------
    str  — base64-encoded PNG (no 'data:' prefix)
    """
    if vmin is None:
        vmin = float(np.nanmin(arr))
    if vmax is None:
        vmax = float(np.nanmax(arr))

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    im = ax.imshow(arr, cmap=colormap, vmin=vmin, vmax=vmax, interpolation="bilinear")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.axis("off")
    fig.patch.set_facecolor("#0d1117")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def lulc_map_to_rgb_image(
    classified_map: np.ndarray,
    color_dict: dict[int, str],
) -> np.ndarray:
    """
    Convert a 2-D integer LULC map to an RGB uint8 image using a colour dict.

    Parameters
    ----------
    classified_map : (rows, cols) int array of class IDs
    color_dict     : {class_id: hex_color_string}

    Returns
    -------
    np.ndarray shape (rows, cols, 3) dtype uint8
    """
    rows, cols = classified_map.shape
    rgb = np.zeros((rows, cols, 3), dtype=np.uint8)
    for class_id, hex_color in color_dict.items():
        mask = classified_map == class_id
        r, g, b = [int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)]
        rgb[mask] = [r, g, b]
    return rgb


def rgb_array_to_base64(rgb: np.ndarray, dpi: int = 100) -> str:
    """
    Convert an (H, W, 3) uint8 RGB array to a base64-encoded PNG string.
    """
    fig, ax = plt.subplots(figsize=(rgb.shape[1] / dpi, rgb.shape[0] / dpi), dpi=dpi)
    ax.imshow(rgb, interpolation="nearest")
    ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ---------------------------------------------------------------------------
# Folium map builder
# ---------------------------------------------------------------------------

def create_folium_map(
    region_name: str,
    bbox: list[float],
    lulc_b64: str | None = None,
    zoom_start: int = 11,
) -> folium.Map:
    """
    Create a Folium map centred on the region with optional LULC overlay.

    Parameters
    ----------
    region_name : display name for tooltips
    bbox        : [lon_min, lat_min, lon_max, lat_max]
    lulc_b64    : base64-encoded PNG to overlay on the map (or None)
    zoom_start  : initial zoom level

    Returns
    -------
    folium.Map  ready to be embedded via streamlit_folium
    """
    lon_min, lat_min, lon_max, lat_max = bbox
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2

    fmap = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="CartoDB dark_matter",
        attr="© CartoDB © OpenStreetMap",
    )

    # Bounding-box rectangle
    folium.Rectangle(
        bounds=[[lat_min, lon_min], [lat_max, lon_max]],
        color="#4a9eff",
        fill=True,
        fill_color="#4a9eff",
        fill_opacity=0.08,
        weight=2,
        tooltip=f"{region_name} — Study Area",
    ).add_to(fmap)

    # LULC image overlay
    if lulc_b64:
        folium.raster_layers.ImageOverlay(
            image=f"data:image/png;base64,{lulc_b64}",
            bounds=[[lat_min, lon_min], [lat_max, lon_max]],
            opacity=0.65,
            name="LULC Classification",
        ).add_to(fmap)

    # Region marker
    folium.Marker(
        location=[center_lat, center_lon],
        tooltip=region_name,
        icon=folium.Icon(color="blue", icon="satellite", prefix="fa"),
    ).add_to(fmap)

    folium.LayerControl().add_to(fmap)
    return fmap


# ---------------------------------------------------------------------------
# Human-friendly formatters
# ---------------------------------------------------------------------------

def format_area(km2: float) -> str:
    """
    Format an area in km² with thousands separator.

    Examples
    --------
    >>> format_area(1234.5)
    '1,234.5 km²'
    >>> format_area(0.0123)
    '0.01 km²'
    """
    if km2 >= 10:
        return f"{km2:,.1f} km²"
    elif km2 >= 0.01:
        return f"{km2:.2f} km²"
    else:
        return f"{km2:.4f} km²"


def format_percentage(pct: float) -> str:
    """Return '12.3 %' formatted string."""
    return f"{pct:.1f} %"


def get_season(month: int) -> str:
    """
    Return the Pakistan / South-Asia climatological season for a given month.

    Seasons:
      Winter  — Dec, Jan, Feb
      Spring  — Mar, Apr
      Summer  — May, Jun
      Monsoon — Jul, Aug, Sep
      Autumn  — Oct, Nov
    """
    seasons: dict[int, str] = {
        1: "Winter",  2: "Winter",
        3: "Spring",  4: "Spring",
        5: "Summer",  6: "Summer",
        7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
        10: "Autumn", 11: "Autumn",
        12: "Winter",
    }
    return seasons.get(month, "Unknown")


# ---------------------------------------------------------------------------
# Plotly colourscale helpers
# ---------------------------------------------------------------------------

def lulc_plotly_colorscale(color_dict: dict[int, str]) -> list[list]:
    """
    Build a Plotly discrete colourscale from the LULC colour dict.

    Plotly expects a list of [normalised_value, hex_color] pairs.
    """
    n = len(color_dict)
    scale = []
    for i, (class_id, color) in enumerate(sorted(color_dict.items())):
        lo = i / n
        hi = (i + 1) / n
        scale.append([lo, color])
        scale.append([hi, color])
    return scale


def change_plotly_colorscale(color_dict: dict[int, str]) -> list[list]:
    """Same as lulc_plotly_colorscale but for change-class colour dicts."""
    return lulc_plotly_colorscale(color_dict)


# ---------------------------------------------------------------------------
# Scene metadata helpers
# ---------------------------------------------------------------------------

def describe_scene(metadata: dict) -> str:
    """One-line human-readable scene description."""
    return (
        f"{metadata.get('platform', 'Sentinel-2')} | "
        f"{metadata.get('processing_level', 'L2A')} | "
        f"{metadata.get('representative_date', 'N/A')} | "
        f"Cloud: {metadata.get('cloud_cover', '—')}%"
    )
