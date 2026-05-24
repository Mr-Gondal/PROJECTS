"""
classifier.py — Unsupervised Land Use / Land Cover (LULC) classification.

Uses KMeans clustering on a multi-band feature matrix, then automatically
assigns semantic class labels (Water, Vegetation, Urban, etc.) by
inspecting cluster centroid values on the spectral indices.

This approach mirrors operational LULC workflows where no labelled training
data is available but domain knowledge about spectral behaviour is used to
interpret clusters.
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.config import (
    DEFAULT_CLUSTERS,
    DEFAULT_PIXEL_SIZE_M,
    IMAGE_SIZE,
    LULC_CLASSES,
)


class LULCClassifier:
    """
    KMeans-based LULC classifier with automatic cluster labelling.

    Workflow
    --------
    1. `fit(feature_matrix)`          — scale & fit KMeans
    2. `predict(feature_matrix)`      — return raw cluster labels
    3. `auto_label_clusters(...)`     — map clusters → semantic classes
    4. `classify_image(bands, indices)` — end-to-end convenience wrapper
    """

    def __init__(self, n_clusters: int = DEFAULT_CLUSTERS, random_state: int = 42) -> None:
        self.n_clusters    = n_clusters
        self.random_state  = random_state
        self._scaler       = StandardScaler()
        self._kmeans: KMeans | None = None
        self._cluster_to_class: dict[int, int] = {}

    # ------------------------------------------------------------------
    # Core fit / predict
    # ------------------------------------------------------------------

    def fit(self, feature_matrix: np.ndarray) -> "LULCClassifier":
        """
        Fit StandardScaler + KMeans on the pixel feature matrix.

        Parameters
        ----------
        feature_matrix : np.ndarray shape (n_pixels, n_features)

        Returns
        -------
        self  (for method chaining)
        """
        scaled = self._scaler.fit_transform(feature_matrix)
        self._kmeans = KMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            n_init=10,
            max_iter=300,
            random_state=self.random_state,
        )
        self._kmeans.fit(scaled)
        return self

    def predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels for every pixel.

        Returns
        -------
        np.ndarray shape (n_pixels,) dtype int
        """
        if self._kmeans is None:
            raise RuntimeError("Call fit() before predict().")
        scaled = self._scaler.transform(feature_matrix)
        return self._kmeans.predict(scaled)

    # ------------------------------------------------------------------
    # Automatic semantic labelling
    # ------------------------------------------------------------------

    def auto_label_clusters(
        self,
        cluster_labels: np.ndarray,
        indices_dict: dict[str, np.ndarray],
    ) -> dict[int, int]:
        """
        Map raw KMeans cluster IDs → LULC class IDs using spectral logic.

        Rules (applied in priority order)
        ----------------------------------
        • Highest mean NDWI cluster          → 0  Water
        • Highest mean NDVI cluster          → 1  Dense Vegetation
        • Second-highest mean NDVI cluster   → 2  Sparse Vegetation
        • Highest mean NDBI cluster          → 3  Urban/Built-up
        • Remaining cluster(s)              → 4  Bare Soil

        Parameters
        ----------
        cluster_labels : 1-D int array  (n_pixels,)
        indices_dict   : {'ndvi': arr, 'ndwi': arr, 'ndbi': arr}

        Returns
        -------
        dict  {cluster_id: lulc_class_id}
        """
        ndvi_flat = indices_dict["ndvi"].ravel()
        ndwi_flat = indices_dict["ndwi"].ravel()
        ndbi_flat = indices_dict["ndbi"].ravel()

        cluster_ids = sorted(set(cluster_labels.tolist()))
        n = len(cluster_ids)

        # Compute per-cluster means
        mean_ndvi: dict[int, float] = {}
        mean_ndwi: dict[int, float] = {}
        mean_ndbi: dict[int, float] = {}

        for cid in cluster_ids:
            mask = cluster_labels == cid
            mean_ndvi[cid] = float(np.mean(ndvi_flat[mask]))
            mean_ndwi[cid] = float(np.mean(ndwi_flat[mask]))
            mean_ndbi[cid] = float(np.mean(ndbi_flat[mask]))

        # Sort clusters by each index descending
        by_ndwi = sorted(cluster_ids, key=lambda c: mean_ndwi[c], reverse=True)
        by_ndvi = sorted(cluster_ids, key=lambda c: mean_ndvi[c], reverse=True)
        by_ndbi = sorted(cluster_ids, key=lambda c: mean_ndbi[c], reverse=True)

        assignment: dict[int, int] = {}
        used: set[int] = set()

        # 1. Water — highest NDWI (and NDWI must be positive to avoid false hits)
        water_cid = by_ndwi[0]
        if mean_ndwi[water_cid] > -0.3:
            assignment[water_cid] = 0
            used.add(water_cid)

        # 2. Dense vegetation — highest NDVI among remaining
        for cid in by_ndvi:
            if cid not in used:
                assignment[cid] = 1
                used.add(cid)
                break

        # 3. Sparse vegetation — second-highest NDVI (if n ≥ 3)
        if n >= 3:
            for cid in by_ndvi:
                if cid not in used:
                    assignment[cid] = 2
                    used.add(cid)
                    break

        # 4. Urban — highest NDBI among remaining
        for cid in by_ndbi:
            if cid not in used:
                assignment[cid] = 3
                used.add(cid)
                break

        # 5. Bare soil — all remaining
        for cid in cluster_ids:
            if cid not in used:
                assignment[cid] = 4

        self._cluster_to_class = assignment
        return assignment

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_class_statistics(
        self,
        classified_map: np.ndarray,
        pixel_size_m: float = DEFAULT_PIXEL_SIZE_M,
    ) -> dict[str, dict]:
        """
        Compute area statistics per LULC class.

        Parameters
        ----------
        classified_map : 2-D int array with LULC class IDs
        pixel_size_m   : native pixel size in metres

        Returns
        -------
        dict: {class_name: {pixel_count, area_km2, percentage}}
        """
        total_pixels = classified_map.size
        pixel_area_km2 = (pixel_size_m ** 2) / 1e6     # m² → km²
        stats: dict[str, dict] = {}

        for class_id, class_name in LULC_CLASSES.items():
            count = int(np.sum(classified_map == class_id))
            area_km2 = count * pixel_area_km2
            pct = (count / total_pixels * 100) if total_pixels > 0 else 0.0
            stats[class_name] = {
                "pixel_count": count,
                "area_km2":    round(area_km2, 4),
                "percentage":  round(pct, 2),
                "class_id":    class_id,
                "color":       self._get_class_color(class_id),
            }

        return stats

    # ------------------------------------------------------------------
    # End-to-end convenience
    # ------------------------------------------------------------------

    def classify_image(
        self,
        bands: dict[str, np.ndarray],
        indices: dict[str, np.ndarray],
    ) -> tuple[np.ndarray, dict[str, dict]]:
        """
        Full pipeline: feature stacking → KMeans → semantic labelling → stats.

        Parameters
        ----------
        bands   : {band_id: (rows, cols)} float32 arrays
        indices : {index_name: (rows, cols)} float32 arrays

        Returns
        -------
        classified_map : np.ndarray(rows, cols) with LULC class IDs
        class_stats    : dict from get_class_statistics()
        """
        from src.processor import SatelliteProcessor  # avoid circular import

        rows, cols = next(iter(bands.values())).shape
        feature_matrix = SatelliteProcessor.stack_features(bands, indices)

        self.fit(feature_matrix)
        raw_labels = self.predict(feature_matrix)
        cluster_map = self.auto_label_clusters(raw_labels, indices)

        # Remap cluster IDs → LULC class IDs
        lulc_flat = np.vectorize(lambda c: cluster_map.get(c, 4))(raw_labels)
        classified_map = lulc_flat.reshape(rows, cols).astype(np.int32)

        stats = self.get_class_statistics(classified_map)
        return classified_map, stats

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_class_color(class_id: int) -> str:
        from src.config import LULC_COLORS
        return LULC_COLORS.get(class_id, "#888888")

    def get_cluster_centroids(self) -> np.ndarray | None:
        """Return un-scaled centroid coordinates (or None if not fitted)."""
        if self._kmeans is None:
            return None
        return self._scaler.inverse_transform(self._kmeans.cluster_centers_)
