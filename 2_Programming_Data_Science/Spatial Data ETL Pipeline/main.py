"""
main.py — CLI entry point for the Spatial Data ETL Pipeline.

Provides a command-line interface for running and monitoring the ETL pipeline:

  python main.py run --all             Run complete ETL pipeline
  python main.py run --extract-only   Run extraction stage only
  python main.py run --transform-only Run transform on existing raw data
  python main.py status               Show DB and pipeline status
  python main.py query --sql "SELECT ..."  Execute SQL query
  python main.py validate --dataset all   Run validation suite
  python main.py export --table ... --format csv --output ...  Export data

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

import os
import sys
import time
import uuid
import json
import logging
import datetime
import warnings
warnings.filterwarnings("ignore")

# Ensure package root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import click
import pandas as pd

from src.config      import DB_PATH, PIPELINE_VERSION, PIPELINE_NAME
from src.extractor   import DataExtractor
from src.transformer import DataTransformer
from src.loader      import DataLoader
from src.validator   import DataValidator
from src.monitor     import PipelineMonitor

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,   # Suppress info logs in CLI for clean output
    format="%(levelname)s | %(name)s | %(message)s",
)

# ─── ANSI Colour Helpers ──────────────────────────────────────────────────────
class C:
    """ANSI terminal colour codes."""
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    AMBER  = "\033[38;5;214m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    GREY   = "\033[90m"
    WHITE  = "\033[97m"


def _print_header():
    click.echo(f"""
{C.AMBER}{C.BOLD}╔══════════════════════════════════════════════════════════╗
║   ⚙️  Spatial Data ETL Pipeline                          ║
║   Pakistan Geospatial Data Platform  v{PIPELINE_VERSION:<18} ║
║   Author: Haris Hussain | Space Science, UoPunjab        ║
╚══════════════════════════════════════════════════════════╝{C.RESET}
""")


def _stage(name: str, icon: str = "●"):
    click.echo(f"\n{C.AMBER}{C.BOLD}{icon} {name.upper()}{C.RESET}")
    click.echo(f"{C.GREY}{'─' * 56}{C.RESET}")


def _ok(msg: str, t: float | None = None):
    timing = f"{C.GREY}({t:.2f}s){C.RESET}" if t is not None else ""
    click.echo(f"  {C.GREEN}✓{C.RESET} {msg} {timing}")


def _warn(msg: str):
    click.echo(f"  {C.YELLOW}⚠{C.RESET}  {msg}")


def _err(msg: str):
    click.echo(f"  {C.RED}✗{C.RESET}  {msg}")


def _info(msg: str):
    click.echo(f"  {C.CYAN}→{C.RESET} {msg}")


def _kv(key: str, val, width: int = 28):
    click.echo(f"  {C.GREY}{key.ljust(width)}{C.RESET}"
               f"{C.AMBER}{C.BOLD}{val}{C.RESET}")


# ─── CLI Group ────────────────────────────────────────────────────────────────
@click.group()
@click.version_option(version=PIPELINE_VERSION, prog_name=PIPELINE_NAME)
def cli():
    """
    Spatial Data ETL Pipeline — Pakistan GIS Platform CLI

    \b
    Examples:
      python main.py run --all
      python main.py status
      python main.py query --sql "SELECT * FROM districts LIMIT 5"
      python main.py validate --dataset all
      python main.py export --table districts --format csv --output out.csv
    """
    pass


# ─── run command ─────────────────────────────────────────────────────────────
@cli.command()
@click.option("--all",            "run_all",    is_flag=True, help="Run full ETL (default)")
@click.option("--extract-only",   is_flag=True, help="Extraction stage only")
@click.option("--transform-only", is_flag=True, help="Transform existing raw data")
@click.option("--seed",  default=42,  show_default=True, help="Random seed for data generation")
@click.option("--quiet", is_flag=True, help="Suppress detailed log output")
def run(run_all, extract_only, transform_only, seed, quiet):
    """Run the ETL pipeline (full or individual stages)."""
    _print_header()
    run_id  = str(uuid.uuid4())[:12]
    started = datetime.datetime.now()
    click.echo(f"{C.GREY}Run ID: {run_id}  |  Started: {started.strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}")

    # ── EXTRACT ──────────────────────────────────────────────────────────────
    _stage("Stage 1: Extract", "📥")
    t0 = time.time()
    extractor = DataExtractor(random_seed=seed)
    raw = extractor.run_all_extractions()
    t_extract = time.time() - t0

    meta = raw["metadata"]
    _ok(f"Extracted {meta['total_records']:,} records", t_extract)
    for src in meta["extraction_log"]:
        _info(f"{src['source']}: {src['records']} records")

    if extract_only:
        click.echo(f"\n{C.GREEN}{C.BOLD}Extraction complete.{C.RESET} Raw files saved to data/raw/")
        return

    # ── TRANSFORM ────────────────────────────────────────────────────────────
    _stage("Stage 2: Transform", "🔄")
    t0 = time.time()
    transformer = DataTransformer()

    if transform_only:
        # Try to reload from raw CSV files
        try:
            raw_census = pd.read_csv("data/raw/census_raw.csv")
            raw["census"] = raw_census
            _info("Reloaded census from raw CSV")
        except FileNotFoundError:
            _warn("Raw files not found — running extraction first")
            extractor = DataExtractor(random_seed=seed)
            raw = extractor.run_all_extractions()

    transformed = transformer.transform_all(raw)
    t_transform = time.time() - t0
    _ok(f"Transformed {transformed['metadata']['records_transformed']:,} records", t_transform)

    if transform_only:
        click.echo(f"\n{C.GREEN}{C.BOLD}Transform complete.{C.RESET} Processed files saved to data/processed/")
        return

    # ── VALIDATE ─────────────────────────────────────────────────────────────
    _stage("Stage 3: Validate", "✅")
    t0 = time.time()
    validator = DataValidator()
    reports   = {}

    dataset_map = {
        "census":         transformed["census"],
        "environmental":  transformed["environmental"],
        "land_use":       transformed["land_use"],
        "infrastructure": transformed["infrastructure"],
    }
    for ds_name, df_ds in dataset_map.items():
        rpt = validator.run_full_validation(df_ds, ds_name)
        reports[ds_name] = rpt
        status_color = {
            "PASS": C.GREEN, "WARN": C.YELLOW, "FAIL": C.RED
        }.get(rpt.overall_status, C.GREY)
        click.echo(
            f"  {status_color}[{rpt.overall_status}]{C.RESET} "
            f"{ds_name:<20} "
            f"Score: {C.AMBER}{rpt.quality_score:>5.1f}/100{C.RESET}  "
            f"P:{C.GREEN}{rpt.passed}{C.RESET} "
            f"W:{C.YELLOW}{rpt.warned}{C.RESET} "
            f"F:{C.RED}{rpt.failed}{C.RESET}"
        )
    t_validate = time.time() - t0
    avg_score  = sum(r.quality_score for r in reports.values()) / len(reports)
    _ok(f"Validation complete. Average quality score: {avg_score:.1f}/100", t_validate)

    # ── LOAD ─────────────────────────────────────────────────────────────────
    _stage("Stage 4: Load → SQLite", "💾")
    t0 = time.time()
    load_stats = DataLoader.load_all(transformed, DB_PATH)
    t_load     = time.time() - t0
    _ok(f"Loaded {load_stats['total_loaded']:,} total rows", t_load)
    for tbl, cnt in load_stats["table_stats"].items():
        _info(f"  {tbl}: {cnt} rows")
    if load_stats["errors"]:
        for err in load_stats["errors"]:
            _err(err)

    # ── LOG RUN ───────────────────────────────────────────────────────────────
    total_dur = round((datetime.datetime.now() - started).total_seconds(), 2)
    run_meta = {
        "run_id":              run_id,
        "pipeline_name":       PIPELINE_NAME,
        "pipeline_version":    PIPELINE_VERSION,
        "started_at":          started.isoformat(),
        "completed_at":        datetime.datetime.now().isoformat(),
        "duration_seconds":    total_dur,
        "status":              "SUCCESS" if not load_stats["errors"] else "PARTIAL",
        "records_extracted":   raw["metadata"]["total_records"],
        "records_transformed": transformed["metadata"]["records_transformed"],
        "records_loaded":      load_stats["total_loaded"],
        "quality_score":       avg_score,
        "error_message":       "; ".join(load_stats["errors"]) or None,
        "triggered_by":        "cli",
    }
    conn = DataLoader.initialize_database(DB_PATH)
    DataLoader.log_pipeline_run(conn, run_meta)
    conn.close()

    # ── SUMMARY ──────────────────────────────────────────────────────────────
    click.echo(f"\n{C.AMBER}{C.BOLD}{'═' * 56}{C.RESET}")
    click.echo(f"{C.GREEN}{C.BOLD}  PIPELINE COMPLETE  {C.RESET}")
    click.echo(f"{C.AMBER}{C.BOLD}{'═' * 56}{C.RESET}")
    _kv("Run ID",               run_id)
    _kv("Total Duration",       f"{total_dur}s")
    _kv("Records Extracted",    f"{raw['metadata']['total_records']:,}")
    _kv("Records Loaded",       f"{load_stats['total_loaded']:,}")
    _kv("Quality Score",        f"{avg_score:.1f}/100")
    _kv("Database",             DB_PATH)
    click.echo(f"\n{C.GREY}  Launch dashboard: {C.RESET}"
               f"{C.CYAN}streamlit run app.py{C.RESET}\n")


# ─── status command ──────────────────────────────────────────────────────────
@cli.command()
def status():
    """Show current pipeline status and database statistics."""
    _print_header()
    _stage("Pipeline Status", "📊")

    monitor  = PipelineMonitor(DB_PATH)
    summary  = monitor.get_database_summary()
    t_stats  = monitor.get_table_stats()
    runs     = monitor.get_recent_runs(5)

    _kv("Database path",    DB_PATH)
    _kv("DB exists",        "✅ Yes" if summary["db_exists"] else "❌ No")
    _kv("DB size",          f"{summary['db_size_kb']} KB")
    _kv("Total records",    f"{summary['total_records']:,}")
    _kv("Tables populated", f"{summary['tables_populated']}/4")
    _kv("Quality score",    f"{summary['quality_score']:.1f}/100")
    _kv("Last run",         summary["last_run_at"])
    _kv("Last status",      summary["last_run_status"])

    click.echo(f"\n{C.AMBER}  Table Details:{C.RESET}")
    if len(t_stats) > 0:
        for _, row in t_stats.iterrows():
            _info(f"{row['table']:<25} {row['row_count']:>6} rows  {row['status']}")
    else:
        _warn("No table data available.")

    if len(runs) > 0:
        click.echo(f"\n{C.AMBER}  Recent Runs:{C.RESET}")
        for _, row in runs.iterrows():
            s_color = C.GREEN if row.get("status") == "SUCCESS" else C.RED
            click.echo(
                f"  {C.GREY}{str(row.get('started_at',''))[:19]}{C.RESET}  "
                f"{s_color}[{row.get('status','?')}]{C.RESET}  "
                f"Records:{C.AMBER}{row.get('records_loaded',0):>6}{C.RESET}  "
                f"Score:{C.CYAN}{row.get('quality_score',0):>5.1f}{C.RESET}  "
                f"Dur:{row.get('duration_seconds',0):.1f}s"
            )
    click.echo()


# ─── query command ────────────────────────────────────────────────────────────
@cli.command()
@click.option("--sql", required=True, help="SQL SELECT statement to execute")
@click.option("--output", default=None, help="Optional CSV output file path")
@click.option("--limit",  default=50, show_default=True, help="Max rows to display")
def query(sql, output, limit):
    """Execute a SQL query against the pipeline database."""
    _print_header()

    if not os.path.exists(DB_PATH):
        _err(f"Database not found at {DB_PATH}. Run 'python main.py run --all' first.")
        sys.exit(1)

    _stage(f"SQL Query", "🔍")
    click.echo(f"  {C.GREY}{sql}{C.RESET}\n")

    df = DataLoader.query_database(DB_PATH, sql)

    if "error" in df.columns:
        _err(f"Query failed: {df['error'].iloc[0]}")
        sys.exit(1)

    _ok(f"Returned {len(df):,} rows × {len(df.columns)} columns")

    if len(df) > 0:
        display_df = df.head(limit)
        # Pretty-print with pandas
        pd.set_option("display.max_columns", 12)
        pd.set_option("display.width",       120)
        pd.set_option("display.max_colwidth", 30)
        pd.set_option("display.float_format", "{:.3f}".format)
        click.echo(f"\n{C.CYAN}")
        click.echo(display_df.to_string(index=False))
        click.echo(C.RESET)

        if len(df) > limit:
            _warn(f"Showing {limit}/{len(df)} rows. Use --limit N to see more.")

    if output:
        df.to_csv(output, index=False)
        _ok(f"Results saved to {output}")


# ─── validate command ─────────────────────────────────────────────────────────
@cli.command()
@click.option(
    "--dataset",
    default="all",
    type=click.Choice(["all", "census", "environmental", "land_use", "infrastructure"]),
    show_default=True,
    help="Dataset to validate",
)
def validate(dataset):
    """Run data quality validation suite against loaded data."""
    _print_header()
    _stage("Data Validation", "✅")

    if not os.path.exists(DB_PATH):
        _err("Database not found. Run pipeline first.")
        sys.exit(1)

    validator = DataValidator()
    table_map = {
        "census":         "SELECT * FROM districts",
        "environmental":  "SELECT * FROM environmental_data",
        "land_use":       "SELECT * FROM land_use",
        "infrastructure": "SELECT * FROM infrastructure",
    }

    datasets_to_check = list(table_map.keys()) if dataset == "all" else [dataset]
    reports = []

    for ds_name in datasets_to_check:
        df = DataLoader.query_database(DB_PATH, table_map[ds_name])
        if "error" in df.columns or len(df) == 0:
            _warn(f"No data for {ds_name} — skipping")
            continue

        # Rename for validator
        df = df.rename(columns={"name": "district"})
        if "centroid_lat" in df.columns:
            df["latitude"]  = df["centroid_lat"]
            df["longitude"] = df["centroid_lon"]

        rpt = validator.run_full_validation(df, ds_name)
        reports.append(rpt)

    if reports:
        click.echo(f"\n{C.CYAN}")
        click.echo(validator.generate_validation_report(reports))
        click.echo(C.RESET)
    else:
        _warn("No validation reports generated.")


# ─── export command ───────────────────────────────────────────────────────────
@cli.command()
@click.option(
    "--table",
    required=True,
    type=click.Choice(["districts", "environmental_data", "land_use",
                       "infrastructure", "pipeline_runs"]),
    help="Table to export",
)
@click.option(
    "--format", "fmt",
    default="csv",
    type=click.Choice(["csv", "json", "jsonl"]),
    show_default=True,
    help="Output format",
)
@click.option("--output", required=True, help="Output file path")
@click.option("--limit",  default=None, type=int, help="Limit rows exported")
def export(table, fmt, output, limit):
    """Export a database table to CSV or JSON."""
    _print_header()
    _stage(f"Export: {table} → {fmt.upper()}", "📤")

    if not os.path.exists(DB_PATH):
        _err("Database not found. Run pipeline first.")
        sys.exit(1)

    sql = f"SELECT * FROM {table}"
    if limit:
        sql += f" LIMIT {limit}"

    df = DataLoader.query_database(DB_PATH, sql)
    if "error" in df.columns:
        _err(f"Query error: {df['error'].iloc[0]}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)

    if fmt == "csv":
        df.to_csv(output, index=False)
    elif fmt == "json":
        df.to_json(output, orient="records", indent=2)
    elif fmt == "jsonl":
        df.to_json(output, orient="records", lines=True)

    _ok(f"Exported {len(df):,} rows from [{table}] to {output}")


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cli()
