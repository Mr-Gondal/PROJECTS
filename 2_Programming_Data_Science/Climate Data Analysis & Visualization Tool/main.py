"""
main.py
=======
Pakistan Climate Observatory — Command-Line Interface Tool

Provides subcommands for analyzing, exporting, and reporting on
synthetic Pakistan climate data without needing a browser or Streamlit.

Usage examples
--------------
  python main.py analyze --city Lahore --start 1980 --end 2024 --output report.html
  python main.py export  --city all    --format csv   --output climate_data.csv
  python main.py trends  --city Karachi
  python main.py anomalies --city Islamabad --threshold 2.0

Author: Haris Hussain — GIS Analyst & Space Science Researcher
"""

import argparse
import sys
import os
import json
from pathlib import Path

import pandas as pd
import numpy as np

# ── Local imports ──────────────────────────────────────────────────────────
from src.data_generator import generate_climate_dataset, CITY_PROFILES
from src.analysis import (
    compute_annual_trends,
    detect_anomalies,
    compute_seasonal_stats,
    compute_climate_stripes_data,
    compute_drought_index,
    get_trend_statistics,
    project_temperatures,
)
from src.visualizations import (
    plot_temperature_trend,
    plot_precipitation_heatmap,
    plot_climate_stripes,
    plot_seasonal_comparison,
    plot_multi_city_comparison,
    plot_anomaly_timeline,
    plot_drought_index,
    plot_temperature_projection,
)

ALL_CITIES = list(CITY_PROFILES.keys())

# ---------------------------------------------------------------------------
# Shared: load dataset once (global cache)
# ---------------------------------------------------------------------------
_DF_CACHE: pd.DataFrame | None = None


def _get_df() -> pd.DataFrame:
    """Load (and cache) the climate dataset."""
    global _DF_CACHE
    if _DF_CACHE is None:
        print("📡 Generating 50-year Pakistan climate dataset…", flush=True)
        _DF_CACHE = generate_climate_dataset(seed=42)
    return _DF_CACHE


def _resolve_cities(city_arg: str) -> list[str]:
    """
    Resolve the --city argument to a list of city names.
    Accepts 'all' or a single city name.
    """
    if city_arg.lower() == "all":
        return ALL_CITIES
    matched = [c for c in ALL_CITIES if c.lower() == city_arg.lower()]
    if not matched:
        print(
            f"❌ Unknown city '{city_arg}'. Available: {', '.join(ALL_CITIES)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return matched


# ---------------------------------------------------------------------------
# HTML report helpers
# ---------------------------------------------------------------------------

def _chart_to_html(fig) -> str:
    """Convert a Plotly figure to an HTML div string (no full page)."""
    return fig.to_html(include_plotlyjs=False, full_html=False)


def _build_html_report(
    title: str,
    city: str,
    year_start: int,
    year_end: int,
    annual_df: pd.DataFrame,
    charts_html: list[str],
    stats_html: str,
) -> str:
    """
    Build a standalone HTML report with embedded Plotly charts.

    Returns the full HTML string.
    """
    charts_section = "\n".join(
        f'<div class="chart-container">{c}</div>' for c in charts_html
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  :root {{
    --bg: #0a0a0f;
    --card: rgba(255,255,255,0.05);
    --border: rgba(255,255,255,0.10);
    --teal: #00d4ff;
    --coral: #ff6b6b;
    --text: #e0e0e0;
    --muted: rgba(255,255,255,0.5);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: linear-gradient(135deg, #0a0a0f, #0d1117, #0a1628);
    color: var(--text);
    font-family: Inter, Segoe UI, Arial, sans-serif;
    min-height: 100vh;
    padding: 2rem;
  }}
  header {{
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
  }}
  header h1 {{
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #0077b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  header p {{ color: var(--muted); margin-top: 0.5rem; }}
  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
  }}
  .meta-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
  }}
  .meta-card .val {{ font-size: 1.5rem; font-weight: 700; color: var(--teal); }}
  .meta-card .lbl {{ font-size: 0.78rem; color: var(--muted); margin-top: 0.2rem; }}
  .chart-container {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    overflow: hidden;
  }}
  .stats-section {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .stats-section h2 {{ color: var(--teal); margin-bottom: 1rem; font-size: 1.1rem; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }}
  th, td {{ padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--teal); font-weight: 600; }}
  tr:hover td {{ background: rgba(0,212,255,0.04); }}
  footer {{
    text-align: center;
    color: var(--muted);
    font-size: 0.78rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }}
</style>
</head>
<body>

<header>
  <h1>🌡️ Pakistan Climate Observatory</h1>
  <h2 style="color:rgba(255,255,255,0.7);font-size:1.2rem;font-weight:500;margin-top:0.5rem;">
    Climate Analysis Report — {city}
  </h2>
  <p>Period: {year_start} – {year_end} &nbsp;|&nbsp; Generated by Pakistan Climate Observatory CLI</p>
</header>

<div class="stats-section">
  <h2>📊 Trend Statistics</h2>
  {stats_html}
</div>

{charts_section}

<footer>
  Pakistan Climate Observatory &nbsp;|&nbsp;
  NOAA-Inspired Synthetic Dataset (1974–2024) &nbsp;|&nbsp;
  Haris Hussain · Space Science · University of Punjab, Lahore
</footer>

</body>
</html>
"""


def _df_to_html_table(df: pd.DataFrame) -> str:
    """Convert a DataFrame to a styled HTML table."""
    rows = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{v}</td>" for v in row)
        rows += f"<tr>{cells}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"


# ---------------------------------------------------------------------------
# Sub-command: analyze
# ---------------------------------------------------------------------------

def cmd_analyze(args: argparse.Namespace) -> None:
    """
    Generate a full climate analysis report for one city.

    Outputs:
    - Printed summary to stdout
    - Optional HTML report with embedded Plotly charts
    """
    df = _get_df()
    cities = _resolve_cities(args.city)
    city = cities[0]  # analyze works on one city at a time

    # Filter by year range
    mask = (df["year"] >= args.start) & (df["year"] <= args.end)
    city_df = df[mask & (df["city"] == city)]

    if city_df.empty:
        print(f"❌ No data for {city} in range {args.start}–{args.end}.", file=sys.stderr)
        sys.exit(1)

    annual_df = compute_annual_trends(df)
    trend_stats = get_trend_statistics(df)
    city_trend = trend_stats[trend_stats["city"] == city].iloc[0]

    # ── Print summary ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  PAKISTAN CLIMATE OBSERVATORY — {city.upper()}")
    print(f"  Period: {args.start} – {args.end}")
    print(f"{'='*60}")
    print(f"  Average Temperature  : {city_df['temperature_mean'].mean():.2f} °C")
    print(f"  Record High          : {city_df['temperature_max'].max():.1f} °C")
    print(f"  Record Low           : {city_df['temperature_min'].min():.1f} °C")
    print(f"  Total Precipitation  : {city_df['precipitation_mm'].sum():.0f} mm")
    print(f"  Avg Monthly Precip   : {city_df['precipitation_mm'].mean():.1f} mm")
    print(f"  Warming Trend        : {city_trend['slope_per_decade']:+.3f} °C/decade")
    print(f"  R²                   : {city_trend['r_squared']:.4f}")
    print(f"  p-value              : {city_trend['p_value']:.6f}")
    print(f"  Trend Significant    : {'Yes ✅' if city_trend['significant'] else 'No ❌'}")
    print(f"{'='*60}\n")

    # ── HTML report ──────────────────────────────────────────────────────────
    if args.output:
        print(f"📊 Generating HTML report → {args.output}")
        annual_city = annual_df[annual_df["city"] == city]
        anomaly_df = detect_anomalies(df)
        drought_df = compute_drought_index(df)
        seasonal_df = compute_seasonal_stats(df)
        stripes_df = compute_climate_stripes_data(df, city)

        charts = [
            _chart_to_html(plot_temperature_trend(city_df, city)),
            _chart_to_html(plot_climate_stripes(stripes_df, city)),
            _chart_to_html(plot_precipitation_heatmap(city_df, city)),
            _chart_to_html(plot_anomaly_timeline(anomaly_df[anomaly_df["city"] == city], city)),
            _chart_to_html(plot_drought_index(drought_df[drought_df["city"] == city], city)),
            _chart_to_html(plot_seasonal_comparison(seasonal_df, city)),
            _chart_to_html(plot_temperature_projection(annual_city, city, target_year=2035)),
        ]

        stats_df = trend_stats.copy()
        stats_df["significant"] = stats_df["significant"].map({True: "✅", False: "❌"})
        stats_html = _df_to_html_table(stats_df)

        html = _build_html_report(
            title=f"Climate Report — {city}",
            city=city,
            year_start=args.start,
            year_end=args.end,
            annual_df=annual_city,
            charts_html=charts,
            stats_html=stats_html,
        )

        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"✅ Report saved to: {out_path.resolve()}")


# ---------------------------------------------------------------------------
# Sub-command: export
# ---------------------------------------------------------------------------

def cmd_export(args: argparse.Namespace) -> None:
    """
    Export climate data to CSV or JSON for one or all cities.
    """
    df = _get_df()
    cities = _resolve_cities(args.city)
    export_df = df[df["city"].isin(cities)].copy()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format.lower() == "csv":
        export_df.to_csv(out_path, index=False)
        print(f"✅ CSV exported → {out_path.resolve()} ({len(export_df):,} rows)")
    elif args.format.lower() == "json":
        export_df.to_json(out_path, orient="records", indent=2)
        print(f"✅ JSON exported → {out_path.resolve()} ({len(export_df):,} records)")
    else:
        print(f"❌ Unknown format '{args.format}'. Choose: csv | json", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Sub-command: trends
# ---------------------------------------------------------------------------

def cmd_trends(args: argparse.Namespace) -> None:
    """
    Print temperature trend statistics for one or all cities.
    """
    df = _get_df()
    cities = _resolve_cities(args.city)
    trend_stats = get_trend_statistics(df)
    city_stats = trend_stats[trend_stats["city"].isin(cities)].copy()

    print(f"\n{'='*72}")
    print(f"  TEMPERATURE TREND STATISTICS — {args.city.upper()}")
    print(f"  Period: 1974 – 2024   |   Method: OLS Linear Regression")
    print(f"{'='*72}")
    print(
        f"  {'City':<12} {'Slope/yr':>10} {'°C/decade':>10} {'R²':>8} {'p-value':>12} {'Sig':>5}"
    )
    print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*8} {'-'*12} {'-'*5}")
    for _, row in city_stats.iterrows():
        sig = "Yes" if row["significant"] else "No"
        print(
            f"  {row['city']:<12} {row['slope_per_year']:>+10.5f} "
            f"{row['slope_per_decade']:>+10.4f} {row['r_squared']:>8.4f} "
            f"{row['p_value']:>12.6f} {sig:>5}"
        )
    print(f"{'='*72}\n")

    # Projections
    annual_df = compute_annual_trends(df)
    proj_df = project_temperatures(annual_df[annual_df["city"].isin(cities)], target_year=2035)
    print(f"  🔮 Temperature Projections to 2035:")
    print(f"  {'City':<12} {'Current (2024)':>15} {'Projected (2035)':>17} {'Δ (°C)':>8}")
    print(f"  {'-'*12} {'-'*15} {'-'*17} {'-'*8}")
    for _, row in proj_df.iterrows():
        col_name_proj = [c for c in proj_df.columns if "2035" in str(c)][0]
        col_name_delta = [c for c in proj_df.columns if "Δ" in str(c) or "delta" in str(c).lower()][0]
        print(
            f"  {row['city']:<12} {row['current_temp_2024']:>15.2f} "
            f"{row[col_name_proj]:>17.2f} {row[col_name_delta]:>+8.2f}"
        )
    print()


# ---------------------------------------------------------------------------
# Sub-command: anomalies
# ---------------------------------------------------------------------------

def cmd_anomalies(args: argparse.Namespace) -> None:
    """
    Detect and report temperature and precipitation anomalies for a city.
    """
    df = _get_df()
    cities = _resolve_cities(args.city)
    city = cities[0]

    print(f"\n📡 Detecting anomalies for {city} (threshold: {args.threshold}σ)…")
    anomaly_df = detect_anomalies(df, threshold=args.threshold)

    city_anom = anomaly_df[
        (anomaly_df["city"] == city) & anomaly_df["is_temp_anomaly"]
    ].copy()

    city_anom_sorted = city_anom.sort_values("temp_anomaly_magnitude", key=abs, ascending=False)

    total = len(anomaly_df[anomaly_df["city"] == city])
    n_temp = int(city_anom["is_temp_anomaly"].sum())
    n_precip = int(anomaly_df[(anomaly_df["city"] == city)]["is_precip_anomaly"].sum())

    print(f"\n{'='*60}")
    print(f"  ANOMALY REPORT — {city.upper()}")
    print(f"  Threshold: {args.threshold}σ   |   Baseline: 1974–2004")
    print(f"{'='*60}")
    print(f"  Total months analysed        : {total}")
    print(f"  Temperature anomalies        : {n_temp} ({n_temp/total*100:.1f}%)")
    print(f"  Precipitation anomalies      : {n_precip} ({n_precip/total*100:.1f}%)")
    print(f"\n  Top 15 Temperature Anomalies (sorted by |Z-score|):")
    print(f"  {'Year':>6} {'Month':>6} {'Temp (°C)':>10} {'Z-score':>9} {'Type':>8}")
    print(f"  {'-'*6} {'-'*6} {'-'*10} {'-'*9} {'-'*8}")

    month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    for _, row in city_anom_sorted.head(15).iterrows():
        anom_type = "WARM" if row["temp_anomaly_magnitude"] > 0 else "COLD"
        print(
            f"  {int(row['year']):>6} {month_names[int(row['month'])-1]:>6} "
            f"{row['temperature_mean']:>10.2f} {row['temp_anomaly_magnitude']:>+9.3f} {anom_type:>8}"
        )
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pakistan-climate",
        description=(
            "🌡️  Pakistan Climate Observatory — CLI Tool\n"
            "Analyze 50 years of synthetic Pakistan climate data (1974–2024).\n"
            f"Available cities: {', '.join(ALL_CITIES)}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # ── analyze ─────────────────────────────────────────────────────────────
    p_analyze = subparsers.add_parser(
        "analyze",
        help="Analyse climate data for a city and optionally export an HTML report",
    )
    p_analyze.add_argument(
        "--city", required=True,
        help=f"City name or 'all'. Choices: {', '.join(ALL_CITIES)}",
    )
    p_analyze.add_argument("--start", type=int, default=1974, help="Start year (default: 1974)")
    p_analyze.add_argument("--end",   type=int, default=2024, help="End year (default: 2024)")
    p_analyze.add_argument("--output", default=None, help="Output HTML report path (optional)")
    p_analyze.set_defaults(func=cmd_analyze)

    # ── export ───────────────────────────────────────────────────────────────
    p_export = subparsers.add_parser(
        "export",
        help="Export climate dataset to CSV or JSON",
    )
    p_export.add_argument(
        "--city", required=True,
        help="City name or 'all'",
    )
    p_export.add_argument(
        "--format", required=True, choices=["csv", "json"],
        help="Output file format: csv | json",
    )
    p_export.add_argument("--output", required=True, help="Output file path")
    p_export.set_defaults(func=cmd_export)

    # ── trends ───────────────────────────────────────────────────────────────
    p_trends = subparsers.add_parser(
        "trends",
        help="Print temperature trend statistics for a city",
    )
    p_trends.add_argument(
        "--city", required=True,
        help="City name or 'all'",
    )
    p_trends.set_defaults(func=cmd_trends)

    # ── anomalies ────────────────────────────────────────────────────────────
    p_anomalies = subparsers.add_parser(
        "anomalies",
        help="Detect and report climate anomalies for a city",
    )
    p_anomalies.add_argument(
        "--city", required=True,
        help="City name",
    )
    p_anomalies.add_argument(
        "--threshold", type=float, default=1.5,
        help="Anomaly threshold in standard deviations (default: 1.5)",
    )
    p_anomalies.set_defaults(func=cmd_anomalies)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
