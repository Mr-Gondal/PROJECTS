"""
validator.py — Data Validation stage of the Spatial ETL Pipeline.

Provides a structured validation framework that checks:
  - Schema conformance (columns, data types)
  - Spatial bounds (Pakistan geographic extents)
  - Completeness (null/missing ratios)
  - Uniqueness (no duplicate primary keys)
  - Custom dataset-level assertions

Results are returned as ValidationReport dataclasses and can be
rendered as human-readable reports.

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.config import PAKISTAN_BBOX

logger = logging.getLogger(__name__)


@dataclass
class ValidationCheck:
    """Result of a single validation check."""
    name:        str
    status:      str          # "PASS", "WARN", "FAIL"
    description: str
    details:     str  = ""
    records_affected: int = 0


@dataclass
class ValidationReport:
    """Aggregated validation report for one dataset."""
    dataset_name: str
    total_records: int
    checks: list[ValidationCheck] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.status == "PASS")

    @property
    def warned(self) -> int:
        return sum(1 for c in self.checks if c.status == "WARN")

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if c.status == "FAIL")

    @property
    def overall_status(self) -> str:
        if self.failed > 0:
            return "FAIL"
        if self.warned > 0:
            return "WARN"
        return "PASS"

    @property
    def quality_score(self) -> float:
        """0-100 quality score: PASS=2pts, WARN=1pt, FAIL=0pt per check."""
        if not self.checks:
            return 0.0
        max_pts = len(self.checks) * 2
        actual  = sum({"PASS": 2, "WARN": 1, "FAIL": 0}[c.status] for c in self.checks)
        return round(actual / max_pts * 100, 1) if max_pts > 0 else 0.0


class DataValidator:
    """
    Structured data quality validation for ETL pipeline datasets.

    Each validation method returns a ValidationCheck; the main entry
    point run_full_validation() composes them into a ValidationReport.
    """

    # ─── Schema Validation ────────────────────────────────────────────────────
    @staticmethod
    def validate_schema(
        df: pd.DataFrame,
        expected_columns: list[str],
        expected_types: dict[str, type] | None = None,
    ) -> ValidationCheck:
        """
        Verify that required columns exist and (optionally) have correct dtypes.

        Args:
            df:               DataFrame to validate
            expected_columns: list of column names that must be present
            expected_types:   optional {col: dtype_class} to check against
        """
        missing = [c for c in expected_columns if c not in df.columns]
        type_errors: list[str] = []

        if expected_types:
            for col, expected_type in expected_types.items():
                if col in df.columns:
                    actual = df[col].dtype
                    # Loose check: numpy numeric types satisfy 'float' or 'int'
                    if expected_type in (float, int):
                        if not np.issubdtype(actual, np.number):
                            type_errors.append(
                                f"{col}: expected numeric, got {actual}"
                            )
                    elif expected_type is str:
                        if actual != object:
                            type_errors.append(
                                f"{col}: expected str/object, got {actual}"
                            )

        issues = missing + type_errors
        if missing:
            return ValidationCheck(
                name="schema_check",
                status="FAIL",
                description="Required columns present and typed correctly",
                details=f"Missing columns: {missing}; Type errors: {type_errors}",
                records_affected=len(df),
            )
        if type_errors:
            return ValidationCheck(
                name="schema_check",
                status="WARN",
                description="Required columns present and typed correctly",
                details=f"Type mismatches: {type_errors}",
            )
        return ValidationCheck(
            name="schema_check",
            status="PASS",
            description="Required columns present and typed correctly",
            details=f"All {len(expected_columns)} expected columns found",
        )

    # ─── Spatial Bounds ───────────────────────────────────────────────────────
    @staticmethod
    def validate_spatial_bounds(
        df: pd.DataFrame,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
    ) -> ValidationCheck:
        """
        Check that all coordinate pairs fall within Pakistan's bounding box.

        Pakistan BBOX: lon 60-77.5°E, lat 23-37.5°N
        """
        name = "spatial_bounds_check"
        if lat_col not in df.columns or lon_col not in df.columns:
            return ValidationCheck(
                name=name,
                status="WARN",
                description="All coordinates within Pakistan bounding box",
                details=f"Coordinate columns '{lat_col}'/'{lon_col}' not found — skipped",
            )

        out_lat = df[
            (df[lat_col] < PAKISTAN_BBOX["min_lat"]) |
            (df[lat_col] > PAKISTAN_BBOX["max_lat"])
        ]
        out_lon = df[
            (df[lon_col] < PAKISTAN_BBOX["min_lon"]) |
            (df[lon_col] > PAKISTAN_BBOX["max_lon"])
        ]
        violations = pd.concat([out_lat, out_lon]).drop_duplicates()

        if len(violations) > 0:
            return ValidationCheck(
                name=name,
                status="FAIL",
                description="All coordinates within Pakistan bounding box",
                details=(
                    f"{len(violations)} record(s) outside Pakistan BBOX "
                    f"(lat {PAKISTAN_BBOX['min_lat']}-{PAKISTAN_BBOX['max_lat']}, "
                    f"lon {PAKISTAN_BBOX['min_lon']}-{PAKISTAN_BBOX['max_lon']})"
                ),
                records_affected=len(violations),
            )
        return ValidationCheck(
            name=name,
            status="PASS",
            description="All coordinates within Pakistan bounding box",
            details=f"All {len(df)} records within Pakistan bounds",
        )

    # ─── Completeness ─────────────────────────────────────────────────────────
    @staticmethod
    def validate_completeness(
        df: pd.DataFrame, required_cols: list[str]
    ) -> ValidationCheck:
        """
        Check null percentages in required columns.

        Thresholds: >0% nulls → WARN, >5% nulls → FAIL
        """
        name = "completeness_check"
        issues: list[str] = []
        worst_pct = 0.0

        for col in required_cols:
            if col not in df.columns:
                issues.append(f"{col}: column missing entirely")
                worst_pct = 100.0
                continue
            null_pct = df[col].isna().mean() * 100
            if null_pct > 0:
                issues.append(f"{col}: {null_pct:.1f}% nulls")
                worst_pct = max(worst_pct, null_pct)

        if worst_pct > 5:
            status  = "FAIL"
        elif worst_pct > 0:
            status  = "WARN"
        else:
            status  = "PASS"

        return ValidationCheck(
            name=name,
            status=status,
            description=f"Null check on {len(required_cols)} required column(s)",
            details="; ".join(issues) if issues else "No nulls detected",
            records_affected=int(df[required_cols].isna().any(axis=1).sum())
            if all(c in df.columns for c in required_cols) else 0,
        )

    # ─── Uniqueness ───────────────────────────────────────────────────────────
    @staticmethod
    def validate_uniqueness(
        df: pd.DataFrame, key_cols: list[str]
    ) -> ValidationCheck:
        """
        Verify there are no duplicate rows on the specified key column(s).
        """
        name = "uniqueness_check"
        available = [c for c in key_cols if c in df.columns]
        if not available:
            return ValidationCheck(
                name=name,
                status="WARN",
                description=f"No duplicate keys on {key_cols}",
                details="Key columns not present — check skipped",
            )

        duplicates = df[df.duplicated(subset=available, keep=False)]
        if len(duplicates) > 0:
            return ValidationCheck(
                name=name,
                status="FAIL",
                description=f"No duplicate keys on {available}",
                details=f"{len(duplicates)} duplicate rows on {available}",
                records_affected=len(duplicates),
            )
        return ValidationCheck(
            name=name,
            status="PASS",
            description=f"No duplicate keys on {available}",
            details=f"All {len(df)} records unique on {available}",
        )

    # ─── Value Range Checks ───────────────────────────────────────────────────
    @staticmethod
    def validate_value_ranges(
        df: pd.DataFrame, range_rules: dict[str, tuple[float, float]]
    ) -> ValidationCheck:
        """
        Check that numeric columns fall within expected value ranges.

        Args:
            range_rules: {column: (min_value, max_value)}
        """
        name = "value_range_check"
        violations: list[str] = []

        for col, (lo, hi) in range_rules.items():
            if col not in df.columns:
                continue
            out_of_range = df[(df[col] < lo) | (df[col] > hi)]
            if len(out_of_range) > 0:
                violations.append(
                    f"{col}: {len(out_of_range)} values outside [{lo}, {hi}]"
                )

        if violations:
            return ValidationCheck(
                name=name,
                status="WARN",
                description="Numeric columns within expected ranges",
                details="; ".join(violations),
                records_affected=len(violations),
            )
        return ValidationCheck(
            name=name,
            status="PASS",
            description="Numeric columns within expected ranges",
            details=f"All {len(range_rules)} range checks passed",
        )

    # ─── Full Validation ──────────────────────────────────────────────────────
    def run_full_validation(
        self,
        df: pd.DataFrame,
        dataset_name: str,
    ) -> ValidationReport:
        """
        Run the complete validation suite appropriate for the given dataset.

        Automatically selects relevant checks based on dataset_name.

        Args:
            df:           DataFrame to validate
            dataset_name: one of 'census', 'environmental', 'land_use',
                          'infrastructure', 'districts'

        Returns:
            ValidationReport with all check results
        """
        logger.info(f"Running full validation for [{dataset_name}] ({len(df)} rows)")
        report = ValidationReport(dataset_name=dataset_name, total_records=len(df))

        # ── Dataset-specific configuration ────────────────────────────────────
        configs = {
            "census": {
                "expected_columns": [
                    "district", "province", "population", "pop_density",
                    "urban_pct", "growth_rate_pct", "literacy_rate",
                ],
                "required_cols": ["district", "province", "population"],
                "key_cols":       ["district"],
                "lat_col": "latitude", "lon_col": "longitude",
                "range_rules": {
                    "urban_pct":       (0, 100),
                    "rural_pct":       (0, 100),
                    "growth_rate_pct": (0, 10),
                    "literacy_rate":   (0, 100),
                },
            },
            "environmental": {
                "expected_columns": [
                    "city", "month", "aqi", "pm25", "pm10", "no2",
                ],
                "required_cols": ["city", "aqi", "pm25"],
                "key_cols":      ["city", "month"],
                "lat_col": "latitude", "lon_col": "longitude",
                "range_rules": {
                    "aqi":  (0, 500),
                    "pm25": (0, 500),
                    "pm10": (0, 600),
                    "no2":  (0, 300),
                    "month": (1, 12),
                },
            },
            "land_use": {
                "expected_columns": [
                    "district", "agricultural_pct", "urban_pct",
                    "forest_pct", "water_pct", "barren_pct",
                ],
                "required_cols": ["district", "agricultural_pct"],
                "key_cols":      ["district"],
                "range_rules": {
                    "agricultural_pct": (0, 100),
                    "urban_pct":        (0, 100),
                    "forest_pct":       (0, 100),
                    "water_pct":        (0, 100),
                    "barren_pct":       (0, 100),
                },
            },
            "infrastructure": {
                "expected_columns": [
                    "district", "hospitals", "schools_total",
                    "electricity_access_pct",
                ],
                "required_cols": ["district", "hospitals"],
                "key_cols":      ["district"],
                "range_rules": {
                    "electricity_access_pct": (0, 100),
                    "internet_access_pct":    (0, 100),
                    "hospitals":              (0, 500),
                },
            },
        }

        cfg = configs.get(dataset_name, {
            "expected_columns": list(df.columns[:5]),
            "required_cols":    list(df.columns[:2]),
            "key_cols":         list(df.columns[:1]),
            "range_rules":      {},
        })

        # Run checks
        report.checks.append(
            self.validate_schema(df, cfg["expected_columns"])
        )
        report.checks.append(
            self.validate_completeness(df, cfg["required_cols"])
        )
        report.checks.append(
            self.validate_uniqueness(df, cfg["key_cols"])
        )
        if cfg.get("range_rules"):
            report.checks.append(
                self.validate_value_ranges(df, cfg["range_rules"])
            )
        if cfg.get("lat_col") and cfg.get("lon_col"):
            report.checks.append(
                self.validate_spatial_bounds(
                    df,
                    lat_col=cfg["lat_col"],
                    lon_col=cfg["lon_col"],
                )
            )

        logger.info(
            f"Validation [{dataset_name}]: "
            f"PASS={report.passed}, WARN={report.warned}, FAIL={report.failed} "
            f"| Score={report.quality_score}"
        )
        return report

    # ─── Report Formatter ─────────────────────────────────────────────────────
    @staticmethod
    def generate_validation_report(reports: list[ValidationReport]) -> str:
        """
        Format a list of ValidationReports into a human-readable string.

        Args:
            reports: list of ValidationReport objects

        Returns:
            Formatted multi-line string suitable for CLI or log output
        """
        lines = [
            "╔══════════════════════════════════════════════════════════╗",
            "║          DATA QUALITY VALIDATION REPORT                  ║",
            "╚══════════════════════════════════════════════════════════╝",
        ]
        status_icons = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}

        for rpt in reports:
            icon = status_icons.get(rpt.overall_status, "❓")
            lines.append(f"\n{icon} Dataset: [{rpt.dataset_name.upper()}]")
            lines.append(f"   Records: {rpt.total_records:,} | "
                         f"Score: {rpt.quality_score:.1f}/100 | "
                         f"Status: {rpt.overall_status}")
            lines.append(f"   Checks → PASS:{rpt.passed} | "
                         f"WARN:{rpt.warned} | FAIL:{rpt.failed}")
            lines.append("   " + "─" * 54)
            for chk in rpt.checks:
                chk_icon = status_icons.get(chk.status, "❓")
                lines.append(f"   {chk_icon} {chk.name}: {chk.details[:80]}")

        lines.append("\n" + "═" * 60)
        all_pass = sum(r.passed  for r in reports)
        all_warn = sum(r.warned  for r in reports)
        all_fail = sum(r.failed  for r in reports)
        avg_score = (sum(r.quality_score for r in reports) / len(reports)
                     if reports else 0)
        lines.append(f"OVERALL → PASS:{all_pass} | WARN:{all_warn} | "
                     f"FAIL:{all_fail} | Avg Score: {avg_score:.1f}/100")
        return "\n".join(lines)
