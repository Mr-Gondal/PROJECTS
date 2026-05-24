"""
extractor.py — Data Extraction stage of the Spatial ETL Pipeline.

Simulates pulling data from multiple heterogeneous sources:
  - Census databases (government statistics)
  - Environmental monitoring APIs
  - Land-use classification results
  - Infrastructure GIS databases
  - GeoJSON boundary files

All data is synthetically generated using numpy/pandas with realistic
Pakistan-specific distributions. No external network calls needed.

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

import os
import json
import logging
import datetime
import numpy as np
import pandas as pd
from shapely.geometry import Point, mapping

from src.config import (
    PAKISTAN_DISTRICTS, RAW_DATA_DIR, LOG_DIR,
    PAKISTAN_BBOX
)

# ─── Logger setup ─────────────────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)

logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Handles the EXTRACT stage of the ETL pipeline.

    Simulates connecting to and pulling data from multiple spatial
    data sources relevant to Pakistan GIS/census/environmental datasets.
    """

    def __init__(self, random_seed: int = 42):
        self.rng = np.random.default_rng(random_seed)
        self.extraction_log: list[dict] = []

    # ─── Census Data ──────────────────────────────────────────────────────────
    def extract_census_data(self) -> pd.DataFrame:
        """
        Simulate extraction from Pakistan Bureau of Statistics census database.

        Generates 30 district-level demographic records with:
        - Population figures (with realistic noise)
        - Urban/rural split percentages
        - Annual population growth rates
        - Dependency ratios and literacy rates
        """
        logger.info("Extracting census data from simulated PBS source…")
        districts = PAKISTAN_DISTRICTS.copy()

        records = []
        for d in districts:
            base_pop = d["pop"]
            area     = d["area_km2"]

            # Realistic urban percentages by province
            urban_base = {
                "Punjab": 0.42, "Sindh": 0.52, "KPK": 0.22,
                "Balochistan": 0.28, "ICT": 0.97, "GB": 0.18, "AJK": 0.30,
            }.get(d["province"], 0.35)

            urban_pct   = float(np.clip(urban_base + self.rng.normal(0, 0.05), 0.1, 0.98))
            growth_rate = float(np.clip(self.rng.normal(2.0, 0.5), 0.5, 4.5))
            pop_density = base_pop / area
            literacy    = float(np.clip(
                {"Punjab": 62, "Sindh": 55, "KPK": 53, "Balochistan": 44,
                 "ICT": 88, "GB": 60, "AJK": 65}.get(d["province"], 55)
                + self.rng.normal(0, 5), 20, 99))
            dependency  = float(np.clip(self.rng.normal(68, 8), 40, 95))
            households  = int(base_pop / self.rng.uniform(5.5, 7.5))

            records.append({
                "district":          d["name"],
                "province":          d["province"],
                "latitude":          d["lat"],
                "longitude":         d["lon"],
                "area_km2":          area,
                "population":        base_pop,
                "pop_density":       round(pop_density, 2),
                "urban_pct":         round(urban_pct * 100, 1),
                "rural_pct":         round((1 - urban_pct) * 100, 1),
                "growth_rate_pct":   round(growth_rate, 2),
                "literacy_rate":     round(literacy, 1),
                "dependency_ratio":  round(dependency, 1),
                "households":        households,
                "census_year":       2023,
                "source":            "PBS_SyntheticCensus_2023",
            })

        df = pd.DataFrame(records)
        # Introduce a few intentional quality issues for the validator to catch
        df.loc[2, "urban_pct"] = -5.0      # invalid negative
        df.loc[7, "growth_rate_pct"] = None  # missing value
        self._log_extraction("census", len(df))
        return df

    # ─── Environmental / AQI Data ─────────────────────────────────────────────
    def extract_environmental_data(self) -> pd.DataFrame:
        """
        Simulate extraction from Pakistan Environmental Protection Agency API.

        Generates 12-month × 10-city daily AQI + pollutant readings.
        Uses seasonal variation to mimic real winter smog patterns in Punjab.
        """
        logger.info("Extracting environmental data from simulated PEPA source…")

        cities = [
            {"name": "Lahore",     "lat": 31.5204, "lon": 74.3587, "base_aqi": 185},
            {"name": "Karachi",    "lat": 24.8607, "lon": 67.0011, "base_aqi": 140},
            {"name": "Islamabad",  "lat": 33.7294, "lon": 73.0931, "base_aqi":  95},
            {"name": "Peshawar",   "lat": 34.0150, "lon": 71.5249, "base_aqi": 155},
            {"name": "Faisalabad", "lat": 31.4180, "lon": 73.0790, "base_aqi": 165},
            {"name": "Multan",     "lat": 30.1575, "lon": 71.5249, "base_aqi": 170},
            {"name": "Quetta",     "lat": 30.1798, "lon": 66.9750, "base_aqi": 110},
            {"name": "Gujranwala", "lat": 32.1877, "lon": 74.1945, "base_aqi": 175},
            {"name": "Rawalpindi", "lat": 33.5651, "lon": 73.0169, "base_aqi": 120},
            {"name": "Hyderabad",  "lat": 25.3960, "lon": 68.3578, "base_aqi": 130},
        ]

        records = []
        for city in cities:
            for month in range(1, 13):
                # Winter smog peak Nov-Feb in Punjab
                seasonal_factor = 1.0
                if city["name"] in ("Lahore", "Faisalabad", "Gujranwala", "Multan"):
                    if month in (11, 12, 1, 2):
                        seasonal_factor = 1.6
                    elif month in (3, 10):
                        seasonal_factor = 1.2

                aqi    = float(np.clip(city["base_aqi"] * seasonal_factor
                                       + self.rng.normal(0, 20), 10, 450))
                pm25   = float(np.clip(aqi * 0.45 + self.rng.normal(0, 5), 1, 200))
                pm10   = float(np.clip(pm25 * 1.8 + self.rng.normal(0, 8), 2, 400))
                no2    = float(np.clip(self.rng.normal(40, 15), 5, 200))
                o3     = float(np.clip(self.rng.normal(60, 20), 5, 200))
                so2    = float(np.clip(self.rng.normal(25, 10), 1, 120))
                temp   = float(self.rng.uniform(5, 45))
                humid  = float(self.rng.uniform(20, 95))

                records.append({
                    "city":        city["name"],
                    "latitude":    city["lat"],
                    "longitude":   city["lon"],
                    "year":        2023,
                    "month":       month,
                    "date":        f"2023-{month:02d}-15",
                    "aqi":         round(aqi, 1),
                    "pm25":        round(pm25, 2),
                    "pm10":        round(pm10, 2),
                    "no2":         round(no2, 2),
                    "o3":          round(o3, 2),
                    "so2":         round(so2, 2),
                    "temperature": round(temp, 1),
                    "humidity":    round(humid, 1),
                    "source":      "PEPA_SyntheticMonitor_2023",
                })

        df = pd.DataFrame(records)
        self._log_extraction("environmental", len(df))
        return df

    # ─── Land-use Data ────────────────────────────────────────────────────────
    def extract_landuse_data(self) -> pd.DataFrame:
        """
        Simulate extraction from remote-sensing land-use classification.

        Generates per-district land cover percentages summing to 100%.
        Distributions reflect known Pakistan land-use patterns.
        """
        logger.info("Extracting land-use data from simulated SUPARCO source…")

        records = []
        for d in PAKISTAN_DISTRICTS:
            province = d["province"]

            # Province-typical base land-cover fractions
            base = {
                "Punjab":      {"agri": 60, "urban": 10, "forest":  5, "water": 3, "barren": 22},
                "Sindh":       {"agri": 45, "urban":  8, "forest":  3, "water": 8, "barren": 36},
                "KPK":         {"agri": 20, "urban":  5, "forest": 35, "water": 4, "barren": 36},
                "Balochistan": {"agri":  5, "urban":  2, "forest":  5, "water": 1, "barren": 87},
                "ICT":         {"agri": 15, "urban": 45, "forest": 30, "water": 2, "barren":  8},
                "GB":          {"agri":  5, "urban":  3, "forest": 20, "water": 5, "barren": 67},
                "AJK":         {"agri": 12, "urban":  6, "forest": 40, "water": 5, "barren": 37},
            }.get(province, {"agri": 30, "urban": 10, "forest": 10, "water": 5, "barren": 45})

            # Add noise
            vals = {k: max(0, v + float(self.rng.normal(0, 3)))
                    for k, v in base.items()}
            total = sum(vals.values())
            vals  = {k: round(v / total * 100, 2) for k, v in vals.items()}

            records.append({
                "district":         d["name"],
                "province":         d["province"],
                "agricultural_pct": vals["agri"],
                "urban_pct":        vals["urban"],
                "forest_pct":       vals["forest"],
                "water_pct":        vals["water"],
                "barren_pct":       vals["barren"],
                "ndvi_mean":        round(float(self.rng.uniform(0.05, 0.55)), 3),
                "ndwi_mean":        round(float(self.rng.uniform(-0.3, 0.3)), 3),
                "classification_date": "2023-06-15",
                "source":           "SUPARCO_LandCover_2023",
            })

        df = pd.DataFrame(records)
        self._log_extraction("land_use", len(df))
        return df

    # ─── Infrastructure Data ──────────────────────────────────────────────────
    def extract_infrastructure_data(self) -> pd.DataFrame:
        """
        Simulate extraction from Pakistan's National Infrastructure database.

        Generates per-district counts/densities for key infrastructure
        indicators: roads, health facilities, schools, power access.
        """
        logger.info("Extracting infrastructure data from simulated NHA/HEC source…")

        records = []
        for d in PAKISTAN_DISTRICTS:
            pop   = d["pop"]
            area  = d["area_km2"]
            prov  = d["province"]

            # Infrastructure quality proxy by province
            infra_factor = {
                "Punjab": 1.4, "ICT": 2.0, "Sindh": 1.0,
                "KPK": 0.9, "Balochistan": 0.5, "GB": 0.4, "AJK": 0.7,
            }.get(prov, 1.0)

            road_density_km_per_km2 = round(
                float(np.clip(infra_factor * self.rng.uniform(0.2, 1.5), 0.05, 3.0)), 3)
            hospitals   = max(1, int(pop / 200000 * infra_factor
                                     + self.rng.integers(-2, 4)))
            clinics     = max(2, int(pop / 50000  * infra_factor
                                     + self.rng.integers(-5, 10)))
            schools     = max(5, int(pop / 10000  * infra_factor
                                     + self.rng.integers(-10, 20)))
            universities = max(0, int(pop / 500000 * infra_factor
                                      + self.rng.integers(0, 3)))
            electricity_access = float(np.clip(
                {"Punjab": 90, "ICT": 99, "Sindh": 80,
                 "KPK": 75, "Balochistan": 55, "GB": 60, "AJK": 70
                }.get(prov, 70) + self.rng.normal(0, 5), 20, 100))
            internet_access = float(np.clip(
                electricity_access * 0.6 + self.rng.normal(0, 5), 5, 98))

            records.append({
                "district":               d["name"],
                "province":               d["province"],
                "road_density_km_km2":    road_density_km_per_km2,
                "total_roads_km":         round(road_density_km_per_km2 * area, 1),
                "hospitals":              hospitals,
                "basic_health_units":     clinics,
                "schools_total":          schools,
                "universities":           universities,
                "electricity_access_pct": round(electricity_access, 1),
                "internet_access_pct":    round(internet_access, 1),
                "source":                 "NHA_HEC_Synthetic_2023",
            })

        df = pd.DataFrame(records)
        self._log_extraction("infrastructure", len(df))
        return df

    # ─── GeoJSON Boundaries ───────────────────────────────────────────────────
    def extract_geojson_source(self) -> dict:
        """
        Simulate extraction of district boundary GeoJSON from a spatial API.

        Creates simplified circular/polygonal proxy boundaries by buffering
        district centroids — avoids any shapefile dependencies.
        """
        logger.info("Extracting GeoJSON boundaries from simulated spatial API…")
        features = []
        for d in PAKISTAN_DISTRICTS:
            # Create a simplified hexagonal polygon around the centroid
            center = Point(d["lon"], d["lat"])
            # Buffer radius proportional to area (approx degrees)
            radius_deg = (d["area_km2"] ** 0.5) / 111.0  # 1 deg ≈ 111 km
            polygon = center.buffer(radius_deg, resolution=6)  # hexagon

            feature = {
                "type": "Feature",
                "geometry": mapping(polygon),
                "properties": {
                    "name":      d["name"],
                    "province":  d["province"],
                    "area_km2":  d["area_km2"],
                    "pop":       d["pop"],
                    "centroid_lat": d["lat"],
                    "centroid_lon": d["lon"],
                },
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "features": features,
        }
        self._log_extraction("geojson_boundaries", len(features))
        return geojson

    # ─── Run All Extractions ──────────────────────────────────────────────────
    def run_all_extractions(self) -> dict:
        """
        Execute the complete extraction stage.

        Runs all individual extractors, saves raw CSV outputs to disk,
        and returns a summary dictionary of extracted DataFrames plus metadata.
        """
        logger.info("═══ Starting EXTRACTION stage ═══")
        start = datetime.datetime.now()

        census    = self.extract_census_data()
        env       = self.extract_environmental_data()
        landuse   = self.extract_landuse_data()
        infra     = self.extract_infrastructure_data()
        geojson   = self.extract_geojson_source()

        # Persist raw CSVs
        census.to_csv(os.path.join(RAW_DATA_DIR, "census_raw.csv"),      index=False)
        env.to_csv(   os.path.join(RAW_DATA_DIR, "environmental_raw.csv"), index=False)
        landuse.to_csv(os.path.join(RAW_DATA_DIR, "land_use_raw.csv"),    index=False)
        infra.to_csv(  os.path.join(RAW_DATA_DIR, "infrastructure_raw.csv"), index=False)

        # Save GeoJSON
        geojson_path = os.path.join(RAW_DATA_DIR, "districts_boundaries.geojson")
        with open(geojson_path, "w") as f:
            json.dump(geojson, f, indent=2)

        duration = (datetime.datetime.now() - start).total_seconds()
        total_records = len(census) + len(env) + len(landuse) + len(infra)

        logger.info(f"Extraction complete: {total_records} records in {duration:.2f}s")

        return {
            "census":         census,
            "environmental":  env,
            "land_use":       landuse,
            "infrastructure": infra,
            "geojson":        geojson,
            "metadata": {
                "total_records":   total_records,
                "duration_seconds": round(duration, 3),
                "extraction_log":   self.extraction_log,
                "raw_files": {
                    "census":       os.path.join(RAW_DATA_DIR, "census_raw.csv"),
                    "environmental": os.path.join(RAW_DATA_DIR, "environmental_raw.csv"),
                    "land_use":     os.path.join(RAW_DATA_DIR, "land_use_raw.csv"),
                    "infrastructure": os.path.join(RAW_DATA_DIR, "infrastructure_raw.csv"),
                    "geojson":      geojson_path,
                },
            },
        }

    # ─── Internal helpers ─────────────────────────────────────────────────────
    def _log_extraction(self, source_name: str, record_count: int):
        entry = {
            "source":      source_name,
            "records":     record_count,
            "timestamp":   datetime.datetime.now().isoformat(),
            "status":      "success",
        }
        self.extraction_log.append(entry)
        logger.debug(f"Extracted {record_count} records from [{source_name}]")
