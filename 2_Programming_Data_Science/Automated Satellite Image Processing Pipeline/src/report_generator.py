"""
report_generator.py — HTML report generation for the satellite pipeline.

Produces a self-contained, dark-themed HTML report embedding:
  • Scene / acquisition metadata
  • Spectral indices summary (with sparkline bar charts in HTML)
  • LULC classification table and pie-chart image
  • Change detection summary table
  • Processing provenance

No external templating engines are used — all HTML is built with f-strings
so the module has zero additional dependencies beyond the project requirements.
"""

from __future__ import annotations

import base64
import io
from datetime import datetime
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from src.config import (
    CHANGE_COLORS,
    LULC_CLASSES,
    LULC_COLORS,
    REPORT_ACCENT_COLOR,
    REPORT_DARK_BG,
    REPORT_TITLE,
)


# ---------------------------------------------------------------------------
# Internal plot helpers
# ---------------------------------------------------------------------------

def _pie_chart_b64(stats: dict[str, dict], title: str = "LULC") -> str:
    """Render a pie chart for class statistics and return base64 PNG."""
    labels = []
    sizes  = []
    colors = []

    for class_name, s in stats.items():
        if s["pixel_count"] > 0:
            labels.append(f"{class_name}\n{s['percentage']:.1f}%")
            sizes.append(s["pixel_count"])
            colors.append(s.get("color", "#888888"))

    if not sizes:
        return ""

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    fig.patch.set_facecolor(REPORT_DARK_BG)
    ax.set_facecolor(REPORT_DARK_BG)

    wedges, texts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        startangle=90,
        wedgeprops={"edgecolor": "#222233", "linewidth": 1.5},
    )
    ax.legend(
        wedges,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.30),
        ncol=2,
        fontsize=8,
        facecolor="#12121e",
        edgecolor="#333355",
        labelcolor="white",
    )
    ax.set_title(title, color="white", fontsize=12, pad=10)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _index_histogram_b64(index_arr: np.ndarray, title: str, color: str) -> str:
    """Render a histogram for a spectral index and return base64 PNG."""
    valid = index_arr[~np.isnan(index_arr)].ravel()
    if valid.size == 0:
        return ""

    fig, ax = plt.subplots(figsize=(4, 2.5), dpi=90)
    fig.patch.set_facecolor(REPORT_DARK_BG)
    ax.set_facecolor("#0a0a1a")

    ax.hist(valid, bins=50, color=color, alpha=0.80, edgecolor="none")
    ax.axvline(float(np.mean(valid)), color="white", linewidth=1.5,
               linestyle="--", label=f"μ={np.mean(valid):.2f}")
    ax.set_title(title, color="white", fontsize=9)
    ax.tick_params(colors="gray", labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333344")
    ax.legend(fontsize=7, facecolor="#0d1117", labelcolor="white", edgecolor="#444")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_REPORT_CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: {REPORT_DARK_BG};
    color: #e0e0f0;
    padding: 24px;
    line-height: 1.6;
  }}
  h1 {{ font-size: 2rem; font-weight: 700; color: {REPORT_ACCENT_COLOR}; margin-bottom: 4px; }}
  h2 {{ font-size: 1.2rem; font-weight: 600; color: #a0b4d0; margin: 28px 0 12px; border-bottom: 1px solid #2a2a44; padding-bottom: 6px; }}
  h3 {{ font-size: 1rem; font-weight: 600; color: #c0c0e0; margin: 16px 0 8px; }}
  .subtitle {{ color: #6a7a9a; font-size: 0.95rem; margin-bottom: 20px; }}
  .meta-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px; margin-bottom: 24px;
  }}
  .meta-card {{
    background: rgba(255,255,255,0.04); border: 1px solid rgba(100,120,255,0.2);
    border-radius: 10px; padding: 14px 16px;
  }}
  .meta-card .label {{ font-size: 0.7rem; color: #6a7a9a; text-transform: uppercase; letter-spacing: 0.08em; }}
  .meta-card .value {{ font-size: 1.1rem; font-weight: 600; color: #e0e0f0; margin-top: 4px; }}
  table {{
    width: 100%; border-collapse: collapse; font-size: 0.88rem; margin-top: 10px;
  }}
  th {{
    background: rgba(100,120,255,0.15); color: {REPORT_ACCENT_COLOR};
    padding: 10px 14px; text-align: left; font-weight: 600; font-size: 0.8rem;
    text-transform: uppercase; letter-spacing: 0.05em;
  }}
  td {{ padding: 9px 14px; border-bottom: 1px solid #1e1e2e; }}
  tr:hover {{ background: rgba(255,255,255,0.03); }}
  .swatch {{
    display: inline-block; width: 12px; height: 12px;
    border-radius: 3px; margin-right: 6px; vertical-align: middle;
  }}
  .chart-row {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 16px 0; }}
  .chart-box {{ background: rgba(255,255,255,0.03); border: 1px solid #2a2a44; border-radius: 10px; padding: 12px; }}
  .chart-box img {{ max-width: 100%; border-radius: 6px; }}
  .footer {{ margin-top: 40px; text-align: center; font-size: 0.75rem; color: #4a5a7a; }}
  .badge {{
    display: inline-block; background: rgba(74,158,255,0.15); border: 1px solid rgba(74,158,255,0.4);
    color: {REPORT_ACCENT_COLOR}; border-radius: 20px; padding: 3px 12px; font-size: 0.75rem; margin: 2px;
  }}
  .summary-bar {{
    background: rgba(255,255,255,0.03); border-left: 3px solid {REPORT_ACCENT_COLOR};
    padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 10px 0; font-size: 0.9rem;
  }}
</style>
"""


# ---------------------------------------------------------------------------
# Main report class
# ---------------------------------------------------------------------------

class ReportGenerator:
    """
    Generates a self-contained dark-themed HTML analysis report.

    All charts are embedded as base64 PNGs so the HTML file is fully
    portable (no external URLs required).
    """

    def generate_html_report(
        self,
        region: str,
        date_range: tuple[str, str],
        metadata: dict[str, Any],
        indices_dict: dict[str, np.ndarray],
        lulc_stats: dict[str, dict],
        change_stats: dict[str, dict],
        index_stats: dict[str, dict] | None = None,
    ) -> str:
        """
        Build and return a complete HTML report string.

        Parameters
        ----------
        region       : region name (e.g. 'Lahore')
        date_range   : (start_date, end_date) strings
        metadata     : scene metadata dict from SyntheticSTACClient
        indices_dict : {'ndvi': arr, 'ndwi': arr, 'ndbi': arr, 'evi': arr}
        lulc_stats   : output of LULCClassifier.get_class_statistics()
        change_stats : output of ChangeDetector.get_change_statistics()
        index_stats  : optional per-index statistics dict
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        start_date, end_date = date_range

        # -- Charts -----------------------------------------------------------
        lulc_pie_b64 = _pie_chart_b64(lulc_stats, "LULC Classification")
        change_pie_b64 = _pie_chart_b64(change_stats, "Change Detection")

        ndvi_hist_b64 = _index_histogram_b64(
            indices_dict.get("ndvi", np.zeros((10, 10))),
            "NDVI Distribution", "#2d8a4e"
        )
        ndwi_hist_b64 = _index_histogram_b64(
            indices_dict.get("ndwi", np.zeros((10, 10))),
            "NDWI Distribution", "#1a6faf"
        )
        ndbi_hist_b64 = _index_histogram_b64(
            indices_dict.get("ndbi", np.zeros((10, 10))),
            "NDBI Distribution", "#c0392b"
        )

        # -- Meta cards -------------------------------------------------------
        meta_cards = self._render_meta_cards(region, start_date, end_date, metadata)

        # -- Spectral indices summary -----------------------------------------
        idx_rows = ""
        if index_stats:
            idx_colors = {"ndvi": "#2d8a4e", "ndwi": "#1a6faf", "ndbi": "#c0392b", "evi": "#8e44ad"}
            for name, s in index_stats.items():
                color = idx_colors.get(name, "#888")
                idx_rows += f"""
                <tr>
                  <td><span class="swatch" style="background:{color};"></span>{name.upper()}</td>
                  <td>{s.get('mean', 0):.4f}</td>
                  <td>{s.get('std', 0):.4f}</td>
                  <td>{s.get('min', 0):.4f}</td>
                  <td>{s.get('max', 0):.4f}</td>
                  <td>{s.get('p50', 0):.4f}</td>
                </tr>"""

        # -- LULC table -------------------------------------------------------
        lulc_rows = ""
        for class_name, s in lulc_stats.items():
            color = s.get("color", "#888")
            lulc_rows += f"""
            <tr>
              <td><span class="swatch" style="background:{color};"></span>{class_name}</td>
              <td>{s['pixel_count']:,}</td>
              <td>{s['area_km2']:.4f}</td>
              <td>{s['percentage']:.2f}%</td>
            </tr>"""

        # -- Change table -----------------------------------------------------
        change_rows = ""
        for class_name, s in change_stats.items():
            color = s.get("color", "#888")
            change_rows += f"""
            <tr>
              <td><span class="swatch" style="background:{color};"></span>{class_name}</td>
              <td>{s['pixel_count']:,}</td>
              <td>{s['area_km2']:.4f}</td>
              <td>{s['percentage']:.2f}%</td>
            </tr>"""

        # -- Dominant change -------------------------------------------------
        dominant_change = max(
            ((k, v) for k, v in change_stats.items() if k != "No Change"),
            key=lambda x: x[1]["percentage"],
            default=("No Change", {"percentage": 0})
        )

        # -- Assemble HTML ---------------------------------------------------
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{REPORT_TITLE} — {region}</title>
  {_REPORT_CSS}
</head>
<body>

  <!-- ===== HEADER ===== -->
  <h1>🛰️ {REPORT_TITLE}</h1>
  <p class="subtitle">
    Region: <strong>{region}</strong> &nbsp;|&nbsp;
    Period: <strong>{start_date}</strong> → <strong>{end_date}</strong> &nbsp;|&nbsp;
    Generated: <strong>{now}</strong>
  </p>
  <div>
    <span class="badge">Sentinel-2 L2A</span>
    <span class="badge">Synthetic Data</span>
    <span class="badge">KMeans LULC</span>
    <span class="badge">Bi-temporal Change</span>
  </div>

  <!-- ===== META ===== -->
  <h2>📡 Acquisition Metadata</h2>
  {meta_cards}

  <!-- ===== SPECTRAL INDICES ===== -->
  <h2>📈 Spectral Indices Summary</h2>
  <div class="chart-row">
    {"<div class='chart-box'><img src='data:image/png;base64," + ndvi_hist_b64 + "'/></div>" if ndvi_hist_b64 else ""}
    {"<div class='chart-box'><img src='data:image/png;base64," + ndwi_hist_b64 + "'/></div>" if ndwi_hist_b64 else ""}
    {"<div class='chart-box'><img src='data:image/png;base64," + ndbi_hist_b64 + "'/></div>" if ndbi_hist_b64 else ""}
  </div>
  {"<table><thead><tr><th>Index</th><th>Mean</th><th>Std Dev</th><th>Min</th><th>Max</th><th>Median</th></tr></thead><tbody>" + idx_rows + "</tbody></table>" if idx_rows else ""}

  <!-- ===== LULC ===== -->
  <h2>🗺️ Land Use / Land Cover Classification</h2>
  <div class="chart-row">
    {"<div class='chart-box'><img src='data:image/png;base64," + lulc_pie_b64 + "' style='width:280px;'/></div>" if lulc_pie_b64 else ""}
    <div style="flex:1; min-width:280px;">
      <table>
        <thead><tr><th>Class</th><th>Pixels</th><th>Area (km²)</th><th>Coverage</th></tr></thead>
        <tbody>{lulc_rows}</tbody>
      </table>
    </div>
  </div>

  <!-- ===== CHANGE DETECTION ===== -->
  <h2>🔄 Change Detection (2020 → 2024)</h2>
  <div class="summary-bar">
    Dominant change: <strong>{dominant_change[0]}</strong>
    ({dominant_change[1].get('percentage', 0):.1f}% of scene)
  </div>
  <div class="chart-row">
    {"<div class='chart-box'><img src='data:image/png;base64," + change_pie_b64 + "' style='width:260px;'/></div>" if change_pie_b64 else ""}
    <div style="flex:1; min-width:280px;">
      <table>
        <thead><tr><th>Change Class</th><th>Pixels</th><th>Area (km²)</th><th>Coverage</th></tr></thead>
        <tbody>{change_rows}</tbody>
      </table>
    </div>
  </div>

  <!-- ===== FOOTER ===== -->
  <div class="footer">
    <p>Pakistan Earth Observation Dashboard &nbsp;|&nbsp; Haris Hussain, University of Punjab, Lahore</p>
    <p>Powered by Sentinel-2 synthetic data &bull; scikit-learn KMeans &bull; Python {self._py_version()}</p>
  </div>

</body>
</html>"""
        return html

    # ------------------------------------------------------------------
    def _render_meta_cards(
        self,
        region: str,
        start_date: str,
        end_date: str,
        metadata: dict,
    ) -> str:
        items = [
            ("Region",      region),
            ("Platform",    metadata.get("platform", "Sentinel-2A")),
            ("Level",       metadata.get("processing_level", "L2A")),
            ("Date Range",  f"{start_date} → {end_date}"),
            ("Scenes",      str(metadata.get("n_scenes", "—"))),
            ("Cloud Cover", f"{metadata.get('cloud_cover', '—')} %"),
            ("Pixel Size",  f"{metadata.get('pixel_size_m', 10)} m"),
            ("Bands",       ", ".join(metadata.get("bands_available", ["B02–B11"]))),
        ]
        cards = ""
        for label, value in items:
            cards += f"""
            <div class="meta-card">
              <div class="label">{label}</div>
              <div class="value">{value}</div>
            </div>"""
        return f'<div class="meta-grid">{cards}</div>'

    @staticmethod
    def _py_version() -> str:
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
