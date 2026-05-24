"""
loader.py — Data Loading stage of the Spatial ETL Pipeline.

Manages the SQLite database (simulating PostGIS for portfolio purposes):
  - Schema initialisation with proper typed columns
  - Insert / upsert operations for each dataset table
  - Pipeline run audit log
  - Query utility for arbitrary SELECT statements

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

import os
import logging
import datetime
import sqlite3
import pandas as pd

from src.config import DB_PATH

logger = logging.getLogger(__name__)

# ─── DDL Statements ───────────────────────────────────────────────────────────
_DDL = {
    "districts": """
        CREATE TABLE IF NOT EXISTS districts (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL UNIQUE,
            province         TEXT,
            area_km2         REAL,
            population       INTEGER,
            pop_density      REAL,
            pop_density_class TEXT,
            urban_pct        REAL,
            rural_pct        REAL,
            growth_rate_pct  REAL,
            literacy_rate    REAL,
            dependency_ratio REAL,
            households       INTEGER,
            urbanisation_class TEXT,
            centroid_lat     REAL,
            centroid_lon     REAL,
            area_km2_computed REAL,
            perimeter_m      REAL,
            compactness      REAL,
            geometry_wkt     TEXT,
            quality_flag     TEXT DEFAULT 'PASS',
            quality_notes    TEXT,
            loaded_at        TEXT,
            census_year      INTEGER,
            source           TEXT
        )
    """,
    "environmental_data": """
        CREATE TABLE IF NOT EXISTS environmental_data (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            city         TEXT,
            latitude     REAL,
            longitude    REAL,
            year         INTEGER,
            month        INTEGER,
            date         TEXT,
            aqi          REAL,
            aqi_normalised REAL,
            health_risk  TEXT,
            pm25         REAL,
            pm10         REAL,
            no2          REAL,
            o3           REAL,
            so2          REAL,
            temperature  REAL,
            humidity     REAL,
            pm25_3month_avg REAL,
            season       TEXT,
            quality_flag TEXT DEFAULT 'PASS',
            quality_notes TEXT,
            loaded_at    TEXT,
            source       TEXT
        )
    """,
    "land_use": """
        CREATE TABLE IF NOT EXISTS land_use (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            district         TEXT,
            province         TEXT,
            agricultural_pct REAL,
            urban_pct        REAL,
            forest_pct       REAL,
            water_pct        REAL,
            barren_pct       REAL,
            ndvi_mean        REAL,
            ndwi_mean        REAL,
            classification_date TEXT,
            quality_flag     TEXT DEFAULT 'PASS',
            quality_notes    TEXT,
            loaded_at        TEXT,
            source           TEXT
        )
    """,
    "infrastructure": """
        CREATE TABLE IF NOT EXISTS infrastructure (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            district               TEXT,
            province               TEXT,
            road_density_km_km2    REAL,
            total_roads_km         REAL,
            hospitals              INTEGER,
            basic_health_units     INTEGER,
            schools_total          INTEGER,
            universities           INTEGER,
            electricity_access_pct REAL,
            internet_access_pct    REAL,
            quality_flag           TEXT DEFAULT 'PASS',
            quality_notes          TEXT,
            loaded_at              TEXT,
            source                 TEXT
        )
    """,
    "pipeline_runs": """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id              TEXT UNIQUE,
            pipeline_name       TEXT,
            pipeline_version    TEXT,
            started_at          TEXT,
            completed_at        TEXT,
            duration_seconds    REAL,
            status              TEXT,
            records_extracted   INTEGER,
            records_transformed INTEGER,
            records_loaded      INTEGER,
            quality_score       REAL,
            error_message       TEXT,
            triggered_by        TEXT
        )
    """,
}


class DataLoader:
    """
    Handles the LOAD stage of the ETL pipeline.

    Manages a SQLite database that acts as a lightweight spatial data
    warehouse, simulating a PostGIS database for portfolio demonstration.
    """

    # ─── Database Initialisation ──────────────────────────────────────────────
    @staticmethod
    def initialize_database(db_path: str = DB_PATH) -> sqlite3.Connection:
        """
        Create the SQLite database and all required tables.

        Args:
            db_path: Path to the .sqlite file (created if absent)

        Returns:
            Open sqlite3.Connection with row_factory set
        """
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        logger.info(f"Initialising database at {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        # Enable WAL mode for better concurrent read performance
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")

        for table_name, ddl in _DDL.items():
            conn.execute(ddl)
            logger.debug(f"Table '{table_name}' ready")

        conn.commit()
        logger.info("Database initialisation complete")
        return conn

    # ─── District Loading ─────────────────────────────────────────────────────
    @staticmethod
    def load_districts(
        conn: sqlite3.Connection, districts_df: pd.DataFrame
    ) -> int:
        """
        Insert or replace district records into the districts table.

        Uses INSERT OR REPLACE to handle re-runs gracefully (upsert behaviour).

        Returns:
            Number of rows inserted/updated
        """
        logger.info(f"Loading {len(districts_df)} districts…")
        ts = datetime.datetime.now().isoformat()
        df = districts_df.copy()
        df["loaded_at"] = ts

        # Select only columns present in the target table schema
        target_cols = [
            "name", "province", "area_km2", "population", "pop_density",
            "pop_density_class", "urban_pct", "rural_pct", "growth_rate_pct",
            "literacy_rate", "dependency_ratio", "households",
            "urbanisation_class", "centroid_lat", "centroid_lon",
            "area_km2_computed", "perimeter_m", "compactness",
            "geometry_wkt", "quality_flag", "quality_notes",
            "loaded_at", "census_year", "source",
        ]
        available = [c for c in target_cols if c in df.columns]
        df = df[available]

        df.to_sql("districts", conn, if_exists="replace", index=False,
                  method="multi", chunksize=500)
        conn.commit()
        logger.info(f"Districts loaded: {len(df)} rows")
        return len(df)

    # ─── Environmental Loading ────────────────────────────────────────────────
    @staticmethod
    def load_environmental(
        conn: sqlite3.Connection, env_df: pd.DataFrame
    ) -> int:
        """
        Insert environmental/AQI records into the environmental_data table.
        """
        logger.info(f"Loading {len(env_df)} environmental records…")
        ts = datetime.datetime.now().isoformat()
        df = env_df.copy()
        df["loaded_at"] = ts

        target_cols = [
            "city", "latitude", "longitude", "year", "month", "date",
            "aqi", "aqi_normalised", "health_risk",
            "pm25", "pm10", "no2", "o3", "so2",
            "temperature", "humidity", "pm25_3month_avg", "season",
            "quality_flag", "quality_notes", "loaded_at", "source",
        ]
        available = [c for c in target_cols if c in df.columns]
        df = df[available]

        df.to_sql("environmental_data", conn, if_exists="replace",
                  index=False, method="multi", chunksize=500)
        conn.commit()
        logger.info(f"Environmental data loaded: {len(df)} rows")
        return len(df)

    # ─── Land-use Loading ─────────────────────────────────────────────────────
    @staticmethod
    def load_land_use(conn: sqlite3.Connection, lu_df: pd.DataFrame) -> int:
        """Insert land-use classification records."""
        logger.info(f"Loading {len(lu_df)} land-use records…")
        ts = datetime.datetime.now().isoformat()
        df = lu_df.copy()
        df["loaded_at"] = ts

        target_cols = [
            "district", "province", "agricultural_pct", "urban_pct",
            "forest_pct", "water_pct", "barren_pct", "ndvi_mean", "ndwi_mean",
            "classification_date", "quality_flag", "quality_notes",
            "loaded_at", "source",
        ]
        available = [c for c in target_cols if c in df.columns]
        df = df[available]

        df.to_sql("land_use", conn, if_exists="replace", index=False,
                  method="multi", chunksize=500)
        conn.commit()
        logger.info(f"Land use loaded: {len(df)} rows")
        return len(df)

    # ─── Infrastructure Loading ───────────────────────────────────────────────
    @staticmethod
    def load_infrastructure(
        conn: sqlite3.Connection, infra_df: pd.DataFrame
    ) -> int:
        """Insert infrastructure records."""
        logger.info(f"Loading {len(infra_df)} infrastructure records…")
        ts = datetime.datetime.now().isoformat()
        df = infra_df.copy()
        df["loaded_at"] = ts

        target_cols = [
            "district", "province", "road_density_km_km2", "total_roads_km",
            "hospitals", "basic_health_units", "schools_total", "universities",
            "electricity_access_pct", "internet_access_pct",
            "quality_flag", "quality_notes", "loaded_at", "source",
        ]
        available = [c for c in target_cols if c in df.columns]
        df = df[available]

        df.to_sql("infrastructure", conn, if_exists="replace", index=False,
                  method="multi", chunksize=500)
        conn.commit()
        logger.info(f"Infrastructure loaded: {len(df)} rows")
        return len(df)

    # ─── Pipeline Run Logging ─────────────────────────────────────────────────
    @staticmethod
    def log_pipeline_run(
        conn: sqlite3.Connection, run_metadata: dict
    ) -> None:
        """
        Record pipeline execution metadata in the pipeline_runs audit table.

        Args:
            run_metadata: dict with keys matching pipeline_runs schema
        """
        logger.info("Logging pipeline run metadata…")
        df = pd.DataFrame([run_metadata])
        df.to_sql("pipeline_runs", conn, if_exists="append", index=False)
        conn.commit()
        logger.info(f"Pipeline run [{run_metadata.get('run_id')}] logged")

    # ─── Master Load Orchestrator ─────────────────────────────────────────────
    @classmethod
    def load_all(
        cls, transformed_data: dict, db_path: str = DB_PATH
    ) -> dict:
        """
        Execute the complete load stage.

        Args:
            transformed_data: dict returned by DataTransformer.transform_all()
            db_path: path to target SQLite database

        Returns:
            dict with load statistics per table
        """
        logger.info("═══ Starting LOAD stage ═══")
        start = datetime.datetime.now()
        conn = cls.initialize_database(db_path)

        stats: dict[str, int] = {}
        errors: list[str] = []

        try:
            stats["districts"]    = cls.load_districts(conn, transformed_data["districts"])
            stats["environmental"]= cls.load_environmental(conn, transformed_data["environmental"])
            stats["land_use"]     = cls.load_land_use(conn, transformed_data["land_use"])
            stats["infrastructure"]= cls.load_infrastructure(conn, transformed_data["infrastructure"])
        except Exception as exc:
            errors.append(str(exc))
            logger.error(f"Load error: {exc}", exc_info=True)

        duration = (datetime.datetime.now() - start).total_seconds()
        total_loaded = sum(stats.values())

        logger.info(f"Load complete: {total_loaded} total rows in {duration:.2f}s")
        conn.close()

        return {
            "table_stats":      stats,
            "total_loaded":     total_loaded,
            "duration_seconds": round(duration, 3),
            "errors":           errors,
        }

    # ─── Query Utility ────────────────────────────────────────────────────────
    @staticmethod
    def query_database(
        db_path: str = DB_PATH, sql_query: str = "SELECT 1"
    ) -> pd.DataFrame:
        """
        Execute a SELECT query against the SQLite database.

        Args:
            db_path:   path to the SQLite file
            sql_query: any valid SQLite SELECT statement

        Returns:
            pandas DataFrame with query results
        """
        if not os.path.exists(db_path):
            return pd.DataFrame({"error": ["Database not found — run the pipeline first"]})
        try:
            conn = sqlite3.connect(db_path)
            df   = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df
        except Exception as exc:
            return pd.DataFrame({"error": [str(exc)]})
