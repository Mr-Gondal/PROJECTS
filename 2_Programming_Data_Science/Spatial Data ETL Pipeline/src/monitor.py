"""
monitor.py — Pipeline monitoring and observability for the Spatial ETL Pipeline.

Provides statistics and health metrics by querying the SQLite audit tables:
  - Pipeline run history and timing
  - Per-table record counts and freshness
  - Overall data quality scoring
  - Recent run summaries

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

import os
import logging
import sqlite3
import datetime
import pandas as pd

from src.config import DB_PATH

logger = logging.getLogger(__name__)


class PipelineMonitor:
    """
    Observability layer for the ETL pipeline.

    Reads from the SQLite database to expose operational metrics,
    data freshness indicators, and quality scores without requiring
    a separate monitoring service.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection | None:
        """Return connection or None if DB not yet created."""
        if not os.path.exists(self.db_path):
            logger.warning(f"Database not found at {self.db_path}")
            return None
        return sqlite3.connect(self.db_path)

    # ─── Pipeline Run Statistics ──────────────────────────────────────────────
    def get_pipeline_stats(self) -> pd.DataFrame:
        """
        Return all pipeline run records from the audit table.

        Returns empty DataFrame with schema if no runs exist yet.
        """
        conn = self._connect()
        if conn is None:
            return pd.DataFrame(columns=[
                "run_id", "started_at", "status", "records_extracted",
                "records_loaded", "duration_seconds", "quality_score",
            ])
        try:
            df = pd.read_sql_query(
                "SELECT * FROM pipeline_runs ORDER BY started_at DESC",
                conn,
            )
        except Exception:
            df = pd.DataFrame()
        finally:
            conn.close()
        return df

    # ─── Table Statistics ─────────────────────────────────────────────────────
    def get_table_stats(self) -> pd.DataFrame:
        """
        Return row counts and last-loaded timestamps per data table.

        Queries each table individually so a missing table returns 0 rows.
        """
        tables = ["districts", "environmental_data", "land_use", "infrastructure"]
        conn   = self._connect()
        rows   = []

        for table in tables:
            if conn is None:
                rows.append({
                    "table":       table,
                    "row_count":   0,
                    "last_loaded": "—",
                    "status":      "DB not initialised",
                })
                continue
            try:
                count_df = pd.read_sql_query(
                    f"SELECT COUNT(*) AS cnt FROM {table}", conn
                )
                count = int(count_df["cnt"].iloc[0])

                # Try to get last loaded timestamp
                if count > 0 and table != "pipeline_runs":
                    try:
                        ts_df = pd.read_sql_query(
                            f"SELECT MAX(loaded_at) AS last_loaded FROM {table}",
                            conn,
                        )
                        last_loaded = ts_df["last_loaded"].iloc[0] or "—"
                    except Exception:
                        last_loaded = "—"
                else:
                    last_loaded = "—"

                rows.append({
                    "table":       table,
                    "row_count":   count,
                    "last_loaded": str(last_loaded)[:19] if last_loaded else "—",
                    "status":      "✅ Populated" if count > 0 else "⚠️  Empty",
                })
            except Exception as exc:
                rows.append({
                    "table":       table,
                    "row_count":   0,
                    "last_loaded": "—",
                    "status":      f"Error: {exc}",
                })

        if conn:
            conn.close()
        return pd.DataFrame(rows)

    # ─── Quality Score ────────────────────────────────────────────────────────
    def compute_data_quality_score(self) -> float:
        """
        Compute an overall data quality score (0-100) from the loaded data.

        Scoring methodology:
          - Completeness (40 pts): fraction of non-null critical fields
          - Uniqueness  (30 pts): fraction of unique district records
          - Bounds      (30 pts): fraction of coordinates within Pakistan BBOX
        """
        conn = self._connect()
        if conn is None:
            return 0.0

        total_score = 0.0

        try:
            # Completeness (40 pts)
            df_d = pd.read_sql_query(
                "SELECT population, province, pop_density FROM districts", conn
            )
            if len(df_d) > 0:
                completeness = 1 - df_d.isna().mean().mean()
                total_score += completeness * 40

            # Uniqueness (30 pts)
            df_u = pd.read_sql_query(
                "SELECT name FROM districts", conn
            )
            if len(df_u) > 0:
                uniqueness = df_u["name"].nunique() / len(df_u)
                total_score += uniqueness * 30

            # Bounds check (30 pts)
            df_b = pd.read_sql_query(
                """SELECT centroid_lat, centroid_lon FROM districts
                   WHERE centroid_lat IS NOT NULL""",
                conn,
            )
            if len(df_b) > 0:
                in_bounds = (
                    (df_b["centroid_lat"].between(23.0, 37.5)) &
                    (df_b["centroid_lon"].between(60.0, 77.5))
                ).mean()
                total_score += in_bounds * 30

        except Exception as exc:
            logger.warning(f"Quality score computation error: {exc}")
        finally:
            conn.close()

        return round(total_score, 1)

    # ─── Recent Runs ──────────────────────────────────────────────────────────
    def get_recent_runs(self, n: int = 10) -> pd.DataFrame:
        """
        Return the last N pipeline runs, most recent first.

        Args:
            n: number of runs to return

        Returns:
            DataFrame with run_id, started_at, status, records_loaded,
            duration_seconds, quality_score columns
        """
        conn = self._connect()
        if conn is None:
            return pd.DataFrame()
        try:
            df = pd.read_sql_query(
                f"""SELECT run_id, started_at, completed_at, status,
                           records_extracted, records_loaded,
                           duration_seconds, quality_score, error_message
                    FROM pipeline_runs
                    ORDER BY started_at DESC
                    LIMIT {int(n)}""",
                conn,
            )
        except Exception:
            df = pd.DataFrame()
        finally:
            conn.close()
        return df

    # ─── DB Summary ───────────────────────────────────────────────────────────
    def get_database_summary(self) -> dict:
        """
        Return a compact summary dict for display in dashboards.
        """
        table_stats  = self.get_table_stats()
        recent_runs  = self.get_recent_runs(1)
        quality      = self.compute_data_quality_score()

        total_records = int(table_stats["row_count"].sum()) if len(table_stats) else 0
        last_run_at   = (recent_runs["started_at"].iloc[0]
                         if len(recent_runs) else "Never")
        last_status   = (recent_runs["status"].iloc[0]
                         if len(recent_runs) else "N/A")

        return {
            "total_records":   total_records,
            "tables_populated": int((table_stats["row_count"] > 0).sum())
                                if len(table_stats) else 0,
            "quality_score":   quality,
            "last_run_at":     str(last_run_at)[:19],
            "last_run_status": last_status,
            "db_exists":       os.path.exists(self.db_path),
            "db_size_kb":      round(os.path.getsize(self.db_path) / 1024, 1)
                               if os.path.exists(self.db_path) else 0,
        }
