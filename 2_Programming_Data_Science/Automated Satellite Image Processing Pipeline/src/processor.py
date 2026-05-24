"""
processor.py — Core raster processing utilities for the Satellite Image
Processing Pipeline.

Provides band arithmetic (spectral indices), composite generation, cloud
masking, and feature-matrix construction that feed the ML classifier.

All methods are static / pure-function style so they can be used both inside
the Streamlit app and from the CLI without instantiating the class.
"""

from __future__ import annotations

import numpy as np


class SatelliteProcessor:
    """
    Stateless collection of raster-processing operations.

    All methods accept a `bands` dict of the form::

        {band_id: np.ndarray(rows, cols, dtype=float32)}

    where values are surface reflectance in [0, 1].
    """

    # ------------------------------------------------------------------
    # Spectral indices
    # ------------------------------------------------------------------

    @staticmethod
    def compute_ndvi(bands: dict[str, np.ndarray]) -> np.ndarray:
        """
        Normalised Difference Vegetation Index.

        NDVI = (NIR - Red) / (NIR + Red)

        Returns a float32 array in [-1, 1].
        """
        nir = bands["B08"].astype(np.float32)
        red = bands["B04"].astype(np.float32)
        denom = nir + red
        ndvi = np.where(denom > 1e-6, (nir - red) / denom, 0.0)
        return np.clip(ndvi, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def compute_ndwi(bands: dict[str, np.ndarray]) -> np.ndarray:
        """
        Normalised Difference Water Index (McFeeters 1996).

        NDWI = (Green - NIR) / (Green + NIR)

        Returns a float32 array in [-1, 1].
        """
        green = bands["B03"].astype(np.float32)
        nir   = bands["B08"].astype(np.float32)
        denom = green + nir
        ndwi  = np.where(denom > 1e-6, (green - nir) / denom, 0.0)
        return np.clip(ndwi, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def compute_ndbi(bands: dict[str, np.ndarray]) -> np.ndarray:
        """
        Normalised Difference Built-up Index (Zha et al. 2003).

        NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)

        Returns a float32 array in [-1, 1].
        """
        swir1 = bands["B11"].astype(np.float32)
        nir   = bands["B08"].astype(np.float32)
        denom = swir1 + nir
        ndbi  = np.where(denom > 1e-6, (swir1 - nir) / denom, 0.0)
        return np.clip(ndbi, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def compute_evi(bands: dict[str, np.ndarray]) -> np.ndarray:
        """
        Enhanced Vegetation Index.

        EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
        """
        nir  = bands["B08"].astype(np.float32)
        red  = bands["B04"].astype(np.float32)
        blue = bands["B02"].astype(np.float32)
        denom = nir + 6.0 * red - 7.5 * blue + 1.0
        evi = np.where(np.abs(denom) > 1e-6, 2.5 * (nir - red) / denom, 0.0)
        return np.clip(evi, -1.0, 2.0).astype(np.float32)

    # ------------------------------------------------------------------
    # Composite generation
    # ------------------------------------------------------------------

    @staticmethod
    def create_rgb_composite(bands: dict[str, np.ndarray]) -> np.ndarray:
        """
        Build a true-colour RGB array scaled to uint8.

        Returns
        -------
        np.ndarray shape (rows, cols, 3) dtype uint8
        """
        def _normalize(arr: np.ndarray) -> np.ndarray:
            lo, hi = np.percentile(arr, 2), np.percentile(arr, 98)
            if hi - lo < 1e-6:
                return np.zeros_like(arr, dtype=np.uint8)
            scaled = (arr - lo) / (hi - lo)
            return (np.clip(scaled, 0, 1) * 255).astype(np.uint8)

        r = _normalize(bands["B04"])
        g = _normalize(bands["B03"])
        b = _normalize(bands["B02"])
        return np.stack([r, g, b], axis=-1)

    @staticmethod
    def create_false_color_composite(bands: dict[str, np.ndarray]) -> np.ndarray:
        """
        NIR / Red / Green false-colour composite (vegetation appears red).

        Returns
        -------
        np.ndarray shape (rows, cols, 3) dtype uint8
        """
        def _norm(arr: np.ndarray) -> np.ndarray:
            lo, hi = np.percentile(arr, 2), np.percentile(arr, 98)
            if hi - lo < 1e-6:
                return np.zeros_like(arr, dtype=np.uint8)
            return (np.clip((arr - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)

        r = _norm(bands["B08"])
        g = _norm(bands["B04"])
        b = _norm(bands["B03"])
        return np.stack([r, g, b], axis=-1)

    # ------------------------------------------------------------------
    # Derived utilities
    # ------------------------------------------------------------------

    @staticmethod
    def compute_all_indices(bands: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """
        Compute all spectral indices and return them in a single dict.

        Returns
        -------
        dict with keys: 'ndvi', 'ndwi', 'ndbi', 'evi'
        """
        proc = SatelliteProcessor()
        return {
            "ndvi": proc.compute_ndvi(bands),
            "ndwi": proc.compute_ndwi(bands),
            "ndbi": proc.compute_ndbi(bands),
            "evi":  proc.compute_evi(bands),
        }

    @staticmethod
    def apply_cloud_mask(
        bands: dict[str, np.ndarray],
        cloud_percentage: float,
    ) -> dict[str, np.ndarray]:
        """
        Simulate cloud masking by zeroing a fraction of pixels.

        Clouds are modelled as spatially coherent blobs (Gaussian random
        field threshold) rather than uniformly random pixels.

        Parameters
        ----------
        cloud_percentage : float
            Fraction of scene to mask, 0–100.

        Returns
        -------
        A new bands dict with cloudy pixels set to NaN.
        """
        if cloud_percentage <= 0:
            return {k: v.copy() for k, v in bands.items()}

        rows, cols = next(iter(bands.values())).shape
        rng = np.random.default_rng(42)

        # Build a smooth cloud probability field
        noise = rng.standard_normal((rows, cols)).astype(np.float32)
        from scipy.ndimage import gaussian_filter  # type: ignore
        smooth_noise = gaussian_filter(noise, sigma=8)
        threshold = np.percentile(smooth_noise, 100.0 - cloud_percentage)
        cloud_mask = smooth_noise > threshold          # True where cloudy

        masked: dict[str, np.ndarray] = {}
        for band_id, arr in bands.items():
            out = arr.copy()
            out[cloud_mask] = np.nan
            masked[band_id] = out
        return masked

    @staticmethod
    def stack_features(
        bands: dict[str, np.ndarray],
        indices: dict[str, np.ndarray],
    ) -> np.ndarray:
        """
        Concatenate band reflectances and spectral indices into a 2-D
        feature matrix suitable for scikit-learn estimators.

        Pixels that contain NaN in any feature (e.g. masked clouds) are
        filled with the column median.

        Parameters
        ----------
        bands   : {band_id: (rows, cols)} reflectance arrays
        indices : {index_name: (rows, cols)} index arrays

        Returns
        -------
        np.ndarray shape (rows*cols, n_features) dtype float32
        """
        layers: list[np.ndarray] = []

        for band_id in ["B02", "B03", "B04", "B08", "B11"]:
            if band_id in bands:
                layers.append(bands[band_id].ravel())

        for index_name in ["ndvi", "ndwi", "ndbi", "evi"]:
            if index_name in indices:
                layers.append(indices[index_name].ravel())

        matrix = np.column_stack(layers).astype(np.float32)

        # Impute NaN with column medians
        for col_idx in range(matrix.shape[1]):
            col = matrix[:, col_idx]
            nan_mask = np.isnan(col)
            if nan_mask.any():
                median_val = np.nanmedian(col)
                col[nan_mask] = median_val
                matrix[:, col_idx] = col

        return matrix

    @staticmethod
    def get_index_statistics(indices: dict[str, np.ndarray]) -> dict[str, dict]:
        """
        Compute per-index descriptive statistics.

        Returns
        -------
        dict: {index_name: {mean, std, min, max, p5, p25, p50, p75, p95}}
        """
        stats: dict[str, dict] = {}
        for name, arr in indices.items():
            valid = arr[~np.isnan(arr)]
            if valid.size == 0:
                stats[name] = {k: 0.0 for k in ("mean", "std", "min", "max",
                                                   "p5", "p25", "p50", "p75", "p95")}
                continue
            stats[name] = {
                "mean": float(np.mean(valid)),
                "std":  float(np.std(valid)),
                "min":  float(np.min(valid)),
                "max":  float(np.max(valid)),
                "p5":   float(np.percentile(valid, 5)),
                "p25":  float(np.percentile(valid, 25)),
                "p50":  float(np.percentile(valid, 50)),
                "p75":  float(np.percentile(valid, 75)),
                "p95":  float(np.percentile(valid, 95)),
            }
        return stats
