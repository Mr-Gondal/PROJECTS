"""
change_detector.py — Bi-temporal change detection for satellite imagery.

Implements pixel-level difference analysis between two time steps (T1, T2)
using NDVI and NDBI change maps, with thresholded semantic classification
into five change categories.

Typical use-case: detect urban expansion, agricultural land loss,
and water-body fluctuations in Pakistani cities (2020 → 2024).
"""

from __future__ import annotations

import numpy as np

from src.config import (
    CHANGE_CLASSES,
    CHANGE_COLORS,
    DEFAULT_PIXEL_SIZE_M,
)
from src.processor import SatelliteProcessor


class ChangeDetector:
    """
    Computes and classifies land-cover change between two Sentinel-2 scenes.

    All methods are stateless (static / class-methods) so no instantiation
    is required for quick usage, but the class acts as a logical namespace.
    """

    # ------------------------------------------------------------------
    # Difference maps
    # ------------------------------------------------------------------

    @staticmethod
    def compute_ndvi_change(
        ndvi_t1: np.ndarray,
        ndvi_t2: np.ndarray,
    ) -> np.ndarray:
        """
        Pixel-wise NDVI change: ΔV = NDVI_T2 − NDVI_T1.

        Positive values → vegetation gain.
        Negative values → vegetation loss.
        """
        return (ndvi_t2 - ndvi_t1).astype(np.float32)

    @staticmethod
    def compute_ndbi_change(
        ndbi_t1: np.ndarray,
        ndbi_t2: np.ndarray,
    ) -> np.ndarray:
        """
        Pixel-wise NDBI change: ΔB = NDBI_T2 − NDBI_T1.

        Positive values → urban / built-up increase.
        """
        return (ndbi_t2 - ndbi_t1).astype(np.float32)

    @staticmethod
    def compute_ndwi_change(
        ndwi_t1: np.ndarray,
        ndwi_t2: np.ndarray,
    ) -> np.ndarray:
        """
        Pixel-wise NDWI change: ΔW = NDWI_T2 − NDWI_T1.

        Positive values → water increase.
        """
        return (ndwi_t2 - ndwi_t1).astype(np.float32)

    # ------------------------------------------------------------------
    # Semantic classification of change
    # ------------------------------------------------------------------

    @staticmethod
    def classify_change(
        ndvi_diff: np.ndarray,
        ndbi_diff: np.ndarray,
        ndwi_diff: np.ndarray | None = None,
        threshold: float = 0.10,
    ) -> np.ndarray:
        """
        Classify every pixel into a change category.

        Decision logic (evaluated in priority order)
        --------------------------------------------
        ΔV >  threshold AND ΔB < 0   → 1  Vegetation Gain
        ΔV < -threshold              → 2  Vegetation Loss
        ΔB >  threshold              → 3  Urban Expansion
        |ΔW| > threshold (if given)  → 4  Water Change
        else                         → 0  No Change

        Returns
        -------
        change_map : np.ndarray(rows, cols) int32 with CHANGE_CLASSES IDs
        """
        rows, cols = ndvi_diff.shape
        change_map = np.zeros((rows, cols), dtype=np.int32)  # default: No Change

        # Water change (lowest priority, applied first so higher priority
        # classes can overwrite)
        if ndwi_diff is not None:
            water_mask = np.abs(ndwi_diff) > threshold
            change_map[water_mask] = 4

        # Urban expansion
        urban_mask = ndbi_diff > threshold
        change_map[urban_mask] = 3

        # Vegetation loss
        veg_loss_mask = ndvi_diff < -threshold
        change_map[veg_loss_mask] = 2

        # Vegetation gain (highest priority)
        veg_gain_mask = (ndvi_diff > threshold) & (ndbi_diff < 0)
        change_map[veg_gain_mask] = 1

        return change_map

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @staticmethod
    def get_change_statistics(
        change_map: np.ndarray,
        pixel_size_m: float = DEFAULT_PIXEL_SIZE_M,
    ) -> dict[str, dict]:
        """
        Compute area statistics per change class.

        Returns
        -------
        dict: {change_class_name: {pixel_count, area_km2, percentage, color}}
        """
        total_pixels  = change_map.size
        pixel_area_km2 = (pixel_size_m ** 2) / 1e6
        stats: dict[str, dict] = {}

        for class_id, class_name in CHANGE_CLASSES.items():
            count    = int(np.sum(change_map == class_id))
            area_km2 = count * pixel_area_km2
            pct      = (count / total_pixels * 100) if total_pixels > 0 else 0.0
            stats[class_name] = {
                "pixel_count": count,
                "area_km2":    round(area_km2, 4),
                "percentage":  round(pct, 2),
                "class_id":    class_id,
                "color":       CHANGE_COLORS.get(class_id, "#888888"),
            }

        return stats

    # ------------------------------------------------------------------
    # Full pipeline wrapper
    # ------------------------------------------------------------------

    def detect_all_changes(
        self,
        bands_t1: dict[str, np.ndarray],
        bands_t2: dict[str, np.ndarray],
        threshold: float = 0.10,
    ) -> dict:
        """
        Run the complete change-detection pipeline.

        Steps
        -----
        1. Compute spectral indices for T1 and T2.
        2. Derive NDVI / NDBI / NDWI difference maps.
        3. Classify change pixels semantically.
        4. Compute area statistics.

        Returns
        -------
        dict with keys:
            indices_t1, indices_t2,
            ndvi_diff, ndbi_diff, ndwi_diff,
            change_map,
            statistics,
            ndvi_t1, ndvi_t2,   (convenience aliases)
            ndwi_t1, ndwi_t2,
            ndbi_t1, ndbi_t2,
        """
        proc = SatelliteProcessor()
        indices_t1 = proc.compute_all_indices(bands_t1)
        indices_t2 = proc.compute_all_indices(bands_t2)

        ndvi_diff = self.compute_ndvi_change(indices_t1["ndvi"], indices_t2["ndvi"])
        ndbi_diff = self.compute_ndbi_change(indices_t1["ndbi"], indices_t2["ndbi"])
        ndwi_diff = self.compute_ndwi_change(indices_t1["ndwi"], indices_t2["ndwi"])

        change_map = self.classify_change(
            ndvi_diff=ndvi_diff,
            ndbi_diff=ndbi_diff,
            ndwi_diff=ndwi_diff,
            threshold=threshold,
        )
        statistics = self.get_change_statistics(change_map)

        return {
            "indices_t1":  indices_t1,
            "indices_t2":  indices_t2,
            "ndvi_diff":   ndvi_diff,
            "ndbi_diff":   ndbi_diff,
            "ndwi_diff":   ndwi_diff,
            "change_map":  change_map,
            "statistics":  statistics,
            # convenience aliases
            "ndvi_t1": indices_t1["ndvi"],
            "ndvi_t2": indices_t2["ndvi"],
            "ndwi_t1": indices_t1["ndwi"],
            "ndwi_t2": indices_t2["ndwi"],
            "ndbi_t1": indices_t1["ndbi"],
            "ndbi_t2": indices_t2["ndbi"],
        }

    # ------------------------------------------------------------------
    # Summary text
    # ------------------------------------------------------------------

    @staticmethod
    def summarise_changes(statistics: dict[str, dict]) -> str:
        """
        Generate a plain-text one-paragraph summary of change statistics.
        """
        lines = []
        for class_name, s in statistics.items():
            if s["percentage"] > 1.0:
                lines.append(
                    f"{class_name}: {s['area_km2']:.2f} km² ({s['percentage']:.1f}%)"
                )
        return "  |  ".join(lines) if lines else "Minimal detectable change."
