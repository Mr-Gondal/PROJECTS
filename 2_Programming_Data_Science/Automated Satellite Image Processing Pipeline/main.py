"""
main.py — Command-line interface for the Satellite Image Processing Pipeline.

Usage Examples
--------------
  python main.py --region Lahore --start 2020-01 --end 2024-12 --clusters 5 --output reports/
  python main.py --list-regions
  python main.py --region Karachi --report-only

The CLI produces coloured terminal output and saves an HTML report to the
specified output directory.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path


# ── ANSI colour helpers ───────────────────────────────────────────────────────

class C:
    """ANSI colour codes. Reset with C.RESET."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    # Foreground
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    # Bright foreground
    BRED    = "\033[91m"
    BGREEN  = "\033[92m"
    BYELLOW = "\033[93m"
    BBLUE   = "\033[94m"
    BMAGENTA= "\033[95m"
    BCYAN   = "\033[96m"
    BWHITE  = "\033[97m"


def _enable_windows_ansi() -> None:
    """Enable ANSI escape codes on Windows (requires Python 3.12+ or colorama)."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass  # silently ignore — colours may not render


def cprint(msg: str, color: str = C.WHITE, bold: bool = False, end: str = "\n") -> None:
    """Print with ANSI colour."""
    prefix = C.BOLD if bold else ""
    print(f"{prefix}{color}{msg}{C.RESET}", end=end)


def _banner() -> None:
    lines = [
        f"{C.BCYAN}{C.BOLD}",
        "╔══════════════════════════════════════════════════════════════╗",
        "║   🛰️  Automated Satellite Image Processing Pipeline           ║",
        "║      Pakistan Earth Observation | Sentinel-2 Analysis        ║",
        "║      Author: Haris Hussain · University of Punjab, Lahore   ║",
        "╚══════════════════════════════════════════════════════════════╝",
        f"{C.RESET}",
    ]
    for line in lines:
        print(line)


def _step(n: int, total: int, msg: str) -> None:
    pct = int(n / total * 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    cprint(f"  [{bar}] {pct:3d}%  {msg}", C.BCYAN)


# ── Core pipeline runner ──────────────────────────────────────────────────────

def run_pipeline(
    region: str,
    start: str,
    end: str,
    clusters: int,
    output_dir: Path,
    report_only: bool = False,
) -> int:
    """
    Execute the full EO pipeline and save an HTML report.

    Returns
    -------
    0 on success, 1 on failure.
    """
    from src.change_detector import ChangeDetector
    from src.classifier import LULCClassifier
    from src.config import LULC_CLASSES, REGIONS
    from src.processor import SatelliteProcessor
    from src.report_generator import ReportGenerator
    from src.stac_client import SyntheticSTACClient
    from src.utils import format_area

    if region not in REGIONS:
        cprint(f"  ✗ Unknown region '{region}'.", C.BRED, bold=True)
        cprint(f"    Available: {', '.join(REGIONS.keys())}", C.YELLOW)
        return 1

    total_steps = 5 if not report_only else 3
    step = 0

    cprint(f"\n  Region   : {region}", C.BWHITE, bold=True)
    cprint(f"  Period   : {start} → {end}", C.BWHITE)
    cprint(f"  Clusters : {clusters}", C.BWHITE)
    cprint(f"  Output   : {output_dir}\n", C.BWHITE)

    client = SyntheticSTACClient()

    # ── Step 1: STAC query ────────────────────────────────────────────────────
    step += 1
    _step(step, total_steps, "Querying STAC catalogue…")
    metadata = client.query_sentinel2(region, start, end)
    time.sleep(0.1)
    cprint(
        f"     → {metadata['n_scenes']} scenes | "
        f"Cloud: {metadata['cloud_cover']}% | "
        f"{metadata['platform']}",
        C.DIM,
    )

    # ── Step 2: Load bands ────────────────────────────────────────────────────
    step += 1
    _step(step, total_steps, "Loading synthetic Sentinel-2 bands…")
    bands = client.load_bands(region, metadata["scene_id"])
    cprint(
        f"     → Loaded {len(bands)} bands | "
        f"Shape: {next(iter(bands.values())).shape}",
        C.DIM,
    )

    # ── Step 3: Spectral indices ───────────────────────────────────────────────
    step += 1
    _step(step, total_steps, "Computing spectral indices…")
    proc    = SatelliteProcessor()
    indices = proc.compute_all_indices(bands)
    idx_stats = proc.get_index_statistics(indices)

    import numpy as np
    cprint(
        f"     → NDVI μ={np.mean(indices['ndvi']):.3f} | "
        f"NDWI μ={np.mean(indices['ndwi']):.3f} | "
        f"NDBI μ={np.mean(indices['ndbi']):.3f}",
        C.DIM,
    )

    if report_only:
        # Skip classification and change detection for --report-only
        lulc_stats    = {c: {"pixel_count": 0, "area_km2": 0, "percentage": 0, "color": "#888"} for c in LULC_CLASSES.values()}
        change_stats  = {}
        change_results = {"statistics": change_stats}
    else:
        # ── Step 4: LULC ──────────────────────────────────────────────────────
        step += 1
        _step(step, total_steps, f"Running KMeans LULC classification ({clusters} clusters)…")
        classifier = LULCClassifier(n_clusters=clusters)
        lulc_map, lulc_stats = classifier.classify_image(bands, indices)
        cprint("     → LULC class breakdown:", C.DIM)
        for cname, s in lulc_stats.items():
            cprint(
                f"        {cname:<22} {s['percentage']:5.1f}%   "
                f"{format_area(s['area_km2'])}",
                C.DIM,
            )

        # ── Step 5: Change detection ───────────────────────────────────────────
        step += 1
        _step(step, total_steps, "Bi-temporal change detection (2020 → 2024)…")
        bands_t1, bands_t2 = client.generate_multi_temporal(region, years=[2020, 2024])
        detector = ChangeDetector()
        change_results = detector.detect_all_changes(bands_t1, bands_t2)
        change_stats   = change_results["statistics"]
        cprint("     → Change summary:", C.DIM)
        for cname, s in change_stats.items():
            if s["percentage"] > 0.5:
                cprint(
                    f"        {cname:<22} {s['percentage']:5.1f}%   "
                    f"{format_area(s['area_km2'])}",
                    C.DIM,
                )

    # ── Generate report ────────────────────────────────────────────────────────
    cprint("\n  📄 Generating HTML report…", C.BMAGENTA)
    reporter = ReportGenerator()
    html = reporter.generate_html_report(
        region=region,
        date_range=(start, end),
        metadata=metadata,
        indices_dict=indices,
        lulc_stats=lulc_stats,
        change_stats=change_results.get("statistics", {}),
        index_stats=idx_stats,
    )

    # ── Save report ────────────────────────────────────────────────────────────
    output_dir.mkdir(parents=True, exist_ok=True)
    ts         = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"EO_Report_{region}_{ts}.html"
    report_path.write_text(html, encoding="utf-8")

    cprint(f"\n  ✅  Report saved → {report_path}", C.BGREEN, bold=True)
    return 0


# ── CLI entry-point ───────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    _enable_windows_ansi()
    _banner()

    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Pakistan Satellite Image Processing Pipeline — CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --region Lahore --start 2020-01 --end 2024-12 --clusters 5
  python main.py --region Karachi --output reports/
  python main.py --list-regions
  python main.py --region Gilgit --report-only
        """,
    )

    parser.add_argument(
        "--region", "-r",
        type=str,
        default="Lahore",
        metavar="REGION",
        help="Study region (default: Lahore)",
    )
    parser.add_argument(
        "--start", "-s",
        type=str,
        default="2020-01",
        metavar="YYYY-MM",
        help="Analysis start date (default: 2020-01)",
    )
    parser.add_argument(
        "--end", "-e",
        type=str,
        default="2024-12",
        metavar="YYYY-MM",
        help="Analysis end date (default: 2024-12)",
    )
    parser.add_argument(
        "--clusters", "-c",
        type=int,
        default=5,
        metavar="N",
        help="Number of KMeans clusters for LULC (default: 5)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="reports",
        metavar="DIR",
        help="Output directory for HTML report (default: reports/)",
    )
    parser.add_argument(
        "--list-regions",
        action="store_true",
        help="List all available study regions and exit",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report from spectral indices only (skip LULC + change detection)",
    )

    args = parser.parse_args(argv)

    # ── --list-regions ─────────────────────────────────────────────────────────
    if args.list_regions:
        from src.config import REGIONS
        cprint("\n  Available Study Regions", C.BCYAN, bold=True)
        cprint("  " + "─" * 52, C.DIM)
        for name, bbox in REGIONS.items():
            cprint(
                f"  {name:<12}  lon [{bbox[0]:.2f}, {bbox[2]:.2f}]  "
                f"lat [{bbox[1]:.2f}, {bbox[3]:.2f}]",
                C.BWHITE,
            )
        cprint("")
        sys.exit(0)

    # ── Run pipeline ────────────────────────────────────────────────────────────
    cprint(f"\n  Starting pipeline…", C.BBLUE, bold=True)
    cprint("  " + "─" * 54, C.DIM)

    exit_code = run_pipeline(
        region=args.region,
        start=args.start,
        end=args.end,
        clusters=args.clusters,
        output_dir=Path(args.output),
        report_only=args.report_only,
    )

    cprint("\n" + "  " + "─" * 54, C.DIM)
    if exit_code == 0:
        cprint("  Pipeline finished successfully. 🛰️\n", C.BGREEN, bold=True)
    else:
        cprint("  Pipeline finished with errors.\n", C.BRED, bold=True)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
