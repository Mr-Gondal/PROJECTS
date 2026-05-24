"""
transformer.py — Data Transformation stage of the Spatial ETL Pipeline.

Applies a full suite of geospatial and tabular transformations:
  - Data cleaning and standardisation
  - Coordinate reprojection (WGS84 → UTM 42N)
  - Spatial enrichment via attribute joins
  - Quality flagging and outlier detection
  - Spatial metric computation (area, perimeter, compactness)
  - AQI normalisation and health-risk categorisation

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

import logging
import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape
from pyproj import Transformer as ProjTransformer

from src.config import (
    PAKISTAN_UTM_CRS, DEFAULT_CRS, AQI_CATEGORIES,
    POP_DENSITY_THRESHOLDS, PROCESSED_DIR
)

import os
os.makedirs(PROCESSED_DIR, exist_ok=True)

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Handles the TRANSFORM stage of the ETL pipeline.

    Processes raw extracted data into analysis-ready datasets with
    standardised schemas, quality flags, and enriched spatial attributes.
    """

    # ─── Census Cleaning ──────────────────────────────────────────────────────
    def clean_census_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardise the raw census DataFrame.

        Steps:
          1. Fix invalid negative percentages (clamp to valid range)
          2. Fill missing growth_rate_pct with province median
          3. Standardise province name capitalisation
          4. Add pop_density_class: Very High / High / Medium / Low
          5. Add urbanisation_class: Highly Urban / Mixed / Rural
        """
        logger.info("Cleaning census data…")
        df = df.copy()

        # 1. Clamp percentage columns to [0, 100]
        for col in ("urban_pct", "rural_pct"):
            if col in df.columns:
                df[col] = df[col].clip(0, 100)

        # Ensure rural_pct is complement of urban_pct
        if "urban_pct" in df.columns and "rural_pct" in df.columns:
            df["rural_pct"] = (100 - df["urban_pct"]).round(1)

        # 2. Fill missing growth rate with province median
        if "growth_rate_pct" in df.columns:
            df["growth_rate_pct"] = pd.to_numeric(df["growth_rate_pct"], errors="coerce")
            prov_medians = df.groupby("province")["growth_rate_pct"].transform("median")
            df["growth_rate_pct"] = df["growth_rate_pct"].fillna(prov_medians)

        # 3. Standardise province names
        province_map = {
            "punjab": "Punjab", "sindh": "Sindh", "kpk": "KPK",
            "khyber pakhtunkhwa": "KPK", "balochistan": "Balochistan",
            "ict": "ICT", "gb": "GB", "ajk": "AJK",
        }
        df["province"] = df["province"].str.strip().apply(
            lambda x: province_map.get(x.lower(), x) if isinstance(x, str) else x
        )

        # 4. Pop density class
        def _density_class(density: float) -> str:
            if density >= 5000: return "Very High"
            if density >= 1000: return "High"
            if density >= 300:  return "Medium"
            return "Low"

        df["pop_density_class"] = df["pop_density"].apply(_density_class)

        # 5. Urbanisation class
        def _urban_class(pct: float) -> str:
            if pct >= 60: return "Highly Urban"
            if pct >= 35: return "Mixed"
            return "Rural"

        df["urbanisation_class"] = df["urban_pct"].apply(_urban_class)

        # 6. Remove complete duplicates
        before = len(df)
        df = df.drop_duplicates(subset=["district"])
        after  = len(df)
        if before != after:
            logger.warning(f"Dropped {before - after} duplicate district rows in census")

        logger.info(f"Census cleaning complete: {len(df)} districts")
        return df.reset_index(drop=True)

    # ─── Coordinate Reprojection ──────────────────────────────────────────────
    def reproject_coordinates(
        self,
        gdf: gpd.GeoDataFrame,
        from_crs: str = DEFAULT_CRS,
        to_crs: str = PAKISTAN_UTM_CRS,
    ) -> gpd.GeoDataFrame:
        """
        Reproject a GeoDataFrame between coordinate reference systems.

        Default: WGS84 (EPSG:4326) → UTM Zone 42N (EPSG:32642)
        UTM 42N is the standard projected CRS for Pakistan, enabling
        metric-unit spatial calculations (area in m², distances in m).
        """
        logger.info(f"Reprojecting from {from_crs} → {to_crs}…")
        if gdf.crs is None:
            gdf = gdf.set_crs(from_crs)
        projected = gdf.to_crs(to_crs)
        logger.info(f"Reprojection complete: {len(projected)} features")
        return projected

    # ─── Spatial Enrichment ───────────────────────────────────────────────────
    def enrich_spatial_data(
        self, districts_gdf: gpd.GeoDataFrame, census_df: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """
        Spatial join / attribute join to add census fields to geometries.

        Merges district polygons with census tabular data on district name,
        producing a single enriched GeoDataFrame for spatial analysis.
        """
        logger.info("Enriching spatial data with census attributes…")

        # Attribute join on district name
        enriched = districts_gdf.merge(
            census_df.drop(columns=["latitude", "longitude", "area_km2"], errors="ignore"),
            left_on="name",
            right_on="district",
            how="left",
        )

        missing = enriched["population"].isna().sum()
        if missing > 0:
            logger.warning(f"{missing} districts could not be matched to census data")

        logger.info(f"Enrichment complete: {len(enriched)} features with census attributes")
        return enriched

    # ─── Validation & Quality Flagging ────────────────────────────────────────
    def validate_and_flag(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect quality issues and attach quality flags to each row.

        Checks performed:
          - Coordinate bounds (Pakistan BBOX: 60-77°E, 23-37°N)
          - Negative values in numeric columns
          - Null / missing critical fields
          - Statistical outliers (IQR ×1.5 method on numeric columns)

        Adds columns: quality_flag (PASS/WARN/FAIL), quality_notes (str)
        """
        logger.info("Running validate_and_flag…")
        df = df.copy()
        flags = []
        notes_list = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # Pre-compute IQR bounds for outlier detection
        iqr_bounds: dict[str, tuple] = {}
        for col in numeric_cols:
            q1  = df[col].quantile(0.25)
            q3  = df[col].quantile(0.75)
            iqr = q3 - q1
            iqr_bounds[col] = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)

        for idx, row in df.iterrows():
            issues: list[str] = []
            flag = "PASS"

            # Check coordinate bounds (if columns present)
            for lat_col in ("latitude", "lat"):
                if lat_col in df.columns:
                    lat = row.get(lat_col)
                    if pd.notna(lat) and not (23.0 <= lat <= 37.5):
                        issues.append(f"{lat_col}={lat:.3f} out of Pakistan bounds")
                        flag = "FAIL"
            for lon_col in ("longitude", "lon"):
                if lon_col in df.columns:
                    lon = row.get(lon_col)
                    if pd.notna(lon) and not (60.0 <= lon <= 77.5):
                        issues.append(f"{lon_col}={lon:.3f} out of Pakistan bounds")
                        flag = "FAIL"

            # Check negatives in percentage columns
            pct_cols = [c for c in numeric_cols if "pct" in c or "rate" in c]
            for col in pct_cols:
                val = row.get(col)
                if pd.notna(val) and val < 0:
                    issues.append(f"{col}={val:.2f} is negative")
                    flag = "FAIL"

            # Check nulls in critical columns
            critical = [c for c in ("district", "province", "population", "aqi")
                        if c in df.columns]
            for col in critical:
                if pd.isna(row.get(col)):
                    issues.append(f"{col} is null")
                    flag = "WARN" if flag == "PASS" else flag

            # Outlier detection (IQR)
            for col in numeric_cols:
                val = row.get(col)
                if pd.notna(val):
                    lo, hi = iqr_bounds[col]
                    if val < lo or val > hi:
                        issues.append(f"{col}={val:.2f} is an outlier (IQR)")
                        flag = "WARN" if flag == "PASS" else flag

            flags.append(flag)
            notes_list.append("; ".join(issues) if issues else "OK")

        df["quality_flag"]  = flags
        df["quality_notes"] = notes_list

        pass_count = flags.count("PASS")
        warn_count = flags.count("WARN")
        fail_count = flags.count("FAIL")
        logger.info(f"Quality flagging: PASS={pass_count}, WARN={warn_count}, FAIL={fail_count}")
        return df

    # ─── Spatial Metrics ──────────────────────────────────────────────────────
    def compute_spatial_metrics(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Compute geometric/spatial metrics for each district polygon.

        Metrics added:
          - area_m2, area_km2_computed: polygon area
          - perimeter_m: polygon perimeter
          - compactness: Polsby-Popper compactness ratio (0-1, 1=circle)
          - centroid_lat, centroid_lon: centroid coordinates (WGS84)
        """
        logger.info("Computing spatial metrics…")
        gdf = gdf.copy()

        # Work in UTM for metric calculations
        gdf_utm = gdf.to_crs(PAKISTAN_UTM_CRS) if gdf.crs else gdf

        gdf["area_m2"]          = gdf_utm.geometry.area.round(2)
        gdf["area_km2_computed"] = (gdf["area_m2"] / 1e6).round(4)
        gdf["perimeter_m"]      = gdf_utm.geometry.length.round(2)

        # Polsby-Popper compactness: 4π·A / P²
        gdf["compactness"] = (
            4 * np.pi * gdf["area_m2"] / (gdf["perimeter_m"] ** 2)
        ).round(4)

        # Centroid in WGS84
        gdf_wgs = gdf_utm.to_crs(DEFAULT_CRS)
        gdf["centroid_lon"] = gdf_wgs.geometry.centroid.x.round(6)
        gdf["centroid_lat"] = gdf_wgs.geometry.centroid.y.round(6)

        logger.info(f"Spatial metrics computed for {len(gdf)} features")
        return gdf

    # ─── AQI Normalisation ────────────────────────────────────────────────────
    def normalize_aqi_data(self, env_df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardise and categorise AQI measurements.

        Steps:
          1. Normalise AQI to 0-1 scale (min-max per city)
          2. Classify AQI into WHO health-risk categories
          3. Compute rolling 3-month PM2.5 average per city
          4. Add seasonal indicator (Winter / Spring / Summer / Monsoon / Autumn)
        """
        logger.info("Normalising AQI data…")
        df = env_df.copy()

        # 1. Min-max normalise within each city
        df["aqi_normalised"] = (
            df.groupby("city")["aqi"]
            .transform(lambda x: (x - x.min()) / (x.max() - x.min() + 1e-9))
            .round(4)
        )

        # 2. AQI health-risk category
        def _aqi_category(aqi: float) -> str:
            for cat in AQI_CATEGORIES:
                if cat["min"] <= aqi <= cat["max"]:
                    return cat["label"]
            return "Hazardous"

        df["health_risk"] = df["aqi"].apply(_aqi_category)

        # 3. Rolling 3-month PM2.5 (sort by city+month first)
        df = df.sort_values(["city", "month"]).reset_index(drop=True)
        df["pm25_3month_avg"] = (
            df.groupby("city")["pm25"]
            .transform(lambda x: x.rolling(3, min_periods=1).mean())
            .round(3)
        )

        # 4. Seasonal indicator
        def _season(month: int) -> str:
            if month in (12, 1, 2):  return "Winter"
            if month in (3, 4):      return "Spring"
            if month in (5, 6):      return "Summer"
            if month in (7, 8, 9):   return "Monsoon"
            return "Autumn"

        df["season"] = df["month"].apply(_season)

        logger.info("AQI normalisation complete")
        return df

    # ─── Full Transform Pipeline ──────────────────────────────────────────────
    def transform_all(self, raw_data: dict) -> dict:
        """
        Run the complete transformation pipeline on extracted raw data.

        Args:
            raw_data: dict returned by DataExtractor.run_all_extractions()

        Returns:
            dict of transformed DataFrames + metadata
        """
        logger.info("═══ Starting TRANSFORM stage ═══")
        start = datetime.datetime.now()

        # 1. Clean census
        census_clean = self.clean_census_data(raw_data["census"])
        census_flagged = self.validate_and_flag(census_clean)

        # 2. Build GeoDataFrame from GeoJSON
        geojson = raw_data["geojson"]
        features = geojson["features"]
        geometries = [shape(f["geometry"]) for f in features]
        props      = [f["properties"]     for f in features]
        gdf = gpd.GeoDataFrame(props, geometry=geometries, crs=DEFAULT_CRS)

        # 3. Enrich & reproject
        gdf_enriched   = self.enrich_spatial_data(gdf, census_clean)
        gdf_metrics    = self.compute_spatial_metrics(gdf_enriched)
        gdf_projected  = self.reproject_coordinates(gdf_metrics)

        # Convert back to WGS84 for storage (SQLite doesn't support native spatial)
        gdf_wgs84 = gdf_projected.to_crs(DEFAULT_CRS)
        # Serialise geometry to WKT for SQLite storage
        districts_df = pd.DataFrame(gdf_wgs84.drop(columns=["geometry"]))
        districts_df["geometry_wkt"] = gdf_wgs84.geometry.apply(lambda g: g.wkt)

        # 4. Normalise environmental/AQI
        env_normalised = self.normalize_aqi_data(raw_data["environmental"])
        env_flagged    = self.validate_and_flag(env_normalised)

        # 5. Flag land-use and infrastructure
        lu_flagged    = self.validate_and_flag(raw_data["land_use"])
        infra_flagged = self.validate_and_flag(raw_data["infrastructure"])

        # 6. Save processed files
        census_flagged.to_csv(
            os.path.join(PROCESSED_DIR, "census_processed.csv"), index=False)
        env_flagged.to_csv(
            os.path.join(PROCESSED_DIR, "environmental_processed.csv"), index=False)
        lu_flagged.to_csv(
            os.path.join(PROCESSED_DIR, "land_use_processed.csv"), index=False)
        infra_flagged.to_csv(
            os.path.join(PROCESSED_DIR, "infrastructure_processed.csv"), index=False)
        districts_df.to_csv(
            os.path.join(PROCESSED_DIR, "districts_processed.csv"), index=False)

        duration = (datetime.datetime.now() - start).total_seconds()
        logger.info(f"Transform complete in {duration:.2f}s")

        return {
            "census":         census_flagged,
            "environmental":  env_flagged,
            "land_use":       lu_flagged,
            "infrastructure": infra_flagged,
            "districts":      districts_df,
            "gdf":            gdf_wgs84,
            "metadata": {
                "duration_seconds": round(duration, 3),
                "records_transformed": (
                    len(census_flagged) + len(env_flagged)
                    + len(lu_flagged) + len(infra_flagged) + len(districts_df)
                ),
            },
        }
