"""
app.py — Pakistan Earth Observation Dashboard
=============================================
A premium Streamlit application providing an end-to-end satellite image
processing pipeline with synthetic Sentinel-2 data.

Features
--------
• Region-specific synthetic Sentinel-2 band generation
• Spectral index computation (NDVI, NDWI, NDBI, EVI)
• Unsupervised LULC classification (KMeans + semantic auto-labelling)
• Bi-temporal change detection (2020 → 2024)
• Interactive Plotly visualisations
• Folium map with LULC overlay
• Downloadable self-contained HTML report

Author : Haris Hussain — University of Punjab, Lahore
"""

from __future__ import annotations

import time
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── project modules ──────────────────────────────────────────────────────────
from src.change_detector import ChangeDetector
from src.classifier import LULCClassifier
from src.config import (
    CHANGE_COLORS,
    LULC_CLASSES,
    LULC_COLORS,
    REGIONS,
)
from src.processor import SatelliteProcessor
from src.report_generator import ReportGenerator
from src.stac_client import SyntheticSTACClient
from src.utils import (
    array_to_colormap_image,
    create_folium_map,
    format_area,
    get_season,
    lulc_map_to_rgb_image,
    rgb_array_to_base64,
)

# =============================================================================
# Page config — MUST be the first Streamlit call
# =============================================================================
st.set_page_config(
    page_title="Pakistan EO Dashboard | Satellite Pipeline",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# Global CSS — dark space theme with glassmorphism
# =============================================================================
GLOBAL_CSS = """
<style>
/* ── Root & body ── */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 20%, #0c0c2a 0%, #050510 60%, #000008 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: rgba(10, 10, 30, 0.95) !important;
    border-right: 1px solid rgba(100, 120, 255, 0.2);
}

/* ── Glass card ── */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(100, 120, 255, 0.25);
    border-radius: 16px;
    padding: 20px 24px;
    margin: 10px 0;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
}
.glass-card-blue {
    background: rgba(30, 50, 120, 0.12);
    border: 1px solid rgba(74, 158, 255, 0.35);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, rgba(30,40,120,0.4) 0%, rgba(10,15,60,0.6) 100%);
    border: 1px solid rgba(100,120,255,0.3);
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 24px;
    text-align: center;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #4a9eff, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
    margin-bottom: 8px;
}
.hero-sub {
    font-size: 1.05rem;
    color: #94a3b8;
    margin-bottom: 16px;
}

/* ── Metric cards ── */
.metric-row { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }
.metric-card {
    flex: 1; min-width: 160px;
    background: rgba(20, 25, 60, 0.5);
    border: 1px solid rgba(100, 120, 255, 0.3);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.metric-card .m-label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-card .m-value { font-size: 1.8rem; font-weight: 700; color: #e2e8f0; margin: 4px 0; }
.metric-card .m-delta { font-size: 0.78rem; color: #38bdf8; }

/* ── Section headers ── */
.section-header {
    font-size: 1.1rem; font-weight: 700;
    color: #a78bfa; margin: 20px 0 10px;
    border-bottom: 1px solid rgba(167,139,250,0.2);
    padding-bottom: 6px;
}

/* ── Tag badges ── */
.badge {
    display: inline-block;
    background: rgba(74,158,255,0.12);
    border: 1px solid rgba(74,158,255,0.3);
    color: #4a9eff;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    margin: 3px;
}

/* ── Table ── */
.styled-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.styled-table th {
    background: rgba(100,120,255,0.12);
    color: #94a3b8;
    padding: 10px 14px;
    text-align: left;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.styled-table td { padding: 9px 14px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.styled-table tr:hover td { background: rgba(255,255,255,0.03); }

/* ── Progress ── */
[data-testid="stProgress"] > div { background: rgba(74,158,255,0.2); border-radius: 4px; }

/* ── Streamlit metric override ── */
[data-testid="metric-container"] {
    background: rgba(15, 20, 50, 0.5);
    border: 1px solid rgba(100,120,255,0.2);
    border-radius: 12px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] { color: #e2e8f0 !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; }

/* ── Sidebar widgets ── */
[data-testid="stSidebar"] label { color: #a0aec0 !important; font-size: 0.85rem !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #a0aec0 !important; }
[data-testid="stSidebar"] .stSlider label { color: #a0aec0 !important; }

/* ── Tab styling ── */
[data-testid="stTabs"] button {
    color: #64748b !important;
    font-size: 0.9rem !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #4a9eff !important;
    border-bottom-color: #4a9eff !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #050510; }
::-webkit-scrollbar-thumb { background: rgba(100,120,255,0.3); border-radius: 3px; }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# =============================================================================
# Plotly theme
# =============================================================================
PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,12,35,0.6)",
        font=dict(color="#c0c8e0", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
        colorway=["#4a9eff", "#38bdf8", "#a78bfa", "#34d399", "#f472b6", "#fb923c"],
    )
)


def apply_template(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        margin=dict(l=20, r=20, t=40, b=20),
        font_family="Inter, sans-serif",
    )
    return fig


# =============================================================================
# Session-state initialisation
# =============================================================================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "results" not in st.session_state:
    st.session_state.results = {}


# =============================================================================
# ── SIDEBAR ──────────────────────────────────────────────────────────────────
# =============================================================================
with st.sidebar:
    st.markdown(
        "<div style='text-align:center; margin-bottom:16px;'>"
        "<span style='font-size:2.5rem;'>🛰️</span><br>"
        "<span style='font-size:1.1rem; font-weight:700; color:#4a9eff;'>EO Pipeline</span><br>"
        "<span style='font-size:0.72rem; color:#475569;'>Pakistan Remote Sensing</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Region ──────────────────────────────────────────────────────────────
    st.markdown("**📍 Study Region**")
    region_name = st.selectbox(
        "Select Region",
        options=list(REGIONS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    bbox = REGIONS[region_name]
    st.caption(
        f"Bbox: [{bbox[0]:.2f}, {bbox[1]:.2f}, {bbox[2]:.2f}, {bbox[3]:.2f}]"
    )

    st.divider()

    # ── Date range ───────────────────────────────────────────────────────────
    st.markdown("**📅 Analysis Period**")
    col_s, col_e = st.columns(2)
    with col_s:
        date_start = st.date_input("Start", value=date(2020, 1, 1), label_visibility="visible")
    with col_e:
        date_end = st.date_input("End", value=date(2024, 12, 31), label_visibility="visible")

    st.divider()

    # ── Cloud cover ──────────────────────────────────────────────────────────
    st.markdown("**☁️ Max Cloud Cover**")
    max_cloud = st.slider(
        "Max Cloud Cover (%)", min_value=0, max_value=30, value=10, step=1,
        label_visibility="collapsed",
    )
    st.caption(f"Filter: ≤ {max_cloud}% cloud cover")

    st.divider()

    # ── Clustering ───────────────────────────────────────────────────────────
    st.markdown("**🔢 LULC Clusters**")
    n_clusters = st.slider(
        "Number of LULC Clusters", min_value=3, max_value=7, value=5, step=1,
        label_visibility="collapsed",
    )
    st.caption(f"KMeans with {n_clusters} clusters")

    st.divider()

    # ── Run button ────────────────────────────────────────────────────────────
    run_analysis = st.button(
        "🚀  Run Analysis",
        use_container_width=True,
        type="primary",
    )

    st.divider()
    st.markdown(
        "<div style='font-size:0.72rem; color:#374151; text-align:center;'>"
        "Haris Hussain · University of Punjab<br>"
        "Space Science · Remote Sensing</div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# ── MAIN AREA ────────────────────────────────────────────────────────────────
# =============================================================================

# ── Hero banner (always visible) ─────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-banner">
      <div class="hero-title">🛰️ Automated Satellite Image Processing Pipeline</div>
      <div class="hero-sub">
        Cloud-native Earth Observation for Pakistan &nbsp;|&nbsp; Sentinel-2 · KMeans LULC · Change Detection
      </div>
      <div>
        <span class="badge">Spectral Indices</span>
        <span class="badge">LULC Classification</span>
        <span class="badge">Change Detection</span>
        <span class="badge">HTML Reports</span>
        <span class="badge">Synthetic Data</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# ── PIPELINE EXECUTION ───────────────────────────────────────────────────────
# =============================================================================
if run_analysis:
    progress_placeholder = st.empty()
    status_placeholder   = st.empty()

    with progress_placeholder.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        progress_bar = st.progress(0, text="🔍 Querying STAC catalogue…")

        # ── Step 1: STAC query ───────────────────────────────────────────────
        status_placeholder.info("Step 1/5 — Querying Sentinel-2 metadata…")
        client   = SyntheticSTACClient()
        metadata = client.query_sentinel2(
            region_name=region_name,
            date_start=str(date_start),
            date_end=str(date_end),
            max_cloud_cover=float(max_cloud),
        )
        time.sleep(0.3)
        progress_bar.progress(20, text="📡 Loading spectral bands…")

        # ── Step 2: Load bands ───────────────────────────────────────────────
        status_placeholder.info("Step 2/5 — Loading synthetic Sentinel-2 bands…")
        scene_id = metadata["scene_id"]
        bands    = client.load_bands(region_name, scene_id)
        time.sleep(0.3)
        progress_bar.progress(40, text="📐 Computing spectral indices…")

        # ── Step 3: Spectral indices ──────────────────────────────────────────
        status_placeholder.info("Step 3/5 — Computing spectral indices…")
        proc    = SatelliteProcessor()
        indices = proc.compute_all_indices(bands)
        idx_stats = proc.get_index_statistics(indices)
        time.sleep(0.3)
        progress_bar.progress(55, text="🗺️ Running LULC classification…")

        # ── Step 4: LULC ─────────────────────────────────────────────────────
        status_placeholder.info("Step 4/5 — KMeans LULC classification…")
        classifier   = LULCClassifier(n_clusters=n_clusters)
        lulc_map, lulc_stats = classifier.classify_image(bands, indices)
        time.sleep(0.4)
        progress_bar.progress(75, text="🔄 Running change detection…")

        # ── Step 5: Change detection ─────────────────────────────────────────
        status_placeholder.info("Step 5/5 — Bi-temporal change detection (2020→2024)…")
        bands_t1, bands_t2 = client.generate_multi_temporal(region_name, years=[2020, 2024])
        detector           = ChangeDetector()
        change_results     = detector.detect_all_changes(bands_t1, bands_t2)
        time.sleep(0.3)
        progress_bar.progress(95, text="📄 Generating report…")

        # ── Report ───────────────────────────────────────────────────────────
        reporter = ReportGenerator()
        html_report = reporter.generate_html_report(
            region=region_name,
            date_range=(str(date_start), str(date_end)),
            metadata=metadata,
            indices_dict=indices,
            lulc_stats=lulc_stats,
            change_stats=change_results["statistics"],
            index_stats=idx_stats,
        )

        # ── LULC RGB image ────────────────────────────────────────────────────
        lulc_rgb   = lulc_map_to_rgb_image(lulc_map, LULC_COLORS)
        lulc_b64   = rgb_array_to_base64(lulc_rgb)
        rgb_comp   = proc.create_rgb_composite(bands)

        progress_bar.progress(100, text="✅ Analysis complete!")
        st.markdown("</div>", unsafe_allow_html=True)

    # Store in session state
    st.session_state.analysis_done = True
    st.session_state.results = {
        "metadata":       metadata,
        "bands":          bands,
        "indices":        indices,
        "idx_stats":      idx_stats,
        "lulc_map":       lulc_map,
        "lulc_stats":     lulc_stats,
        "change_results": change_results,
        "html_report":    html_report,
        "lulc_rgb":       lulc_rgb,
        "lulc_b64":       lulc_b64,
        "rgb_comp":       rgb_comp,
        "region_name":    region_name,
        "date_start":     str(date_start),
        "date_end":       str(date_end),
        "bbox":           bbox,
    }

    progress_placeholder.empty()
    status_placeholder.success(f"✅ Analysis complete for **{region_name}** ({n_clusters} LULC classes)!")

# =============================================================================
# ── RESULTS DISPLAY ──────────────────────────────────────────────────────────
# =============================================================================
if st.session_state.analysis_done and st.session_state.results:
    R = st.session_state.results   # shorthand

    # ── Top metric cards ──────────────────────────────────────────────────────
    m_ndvi  = float(np.mean(R["indices"]["ndvi"]))
    m_ndwi  = float(np.mean(R["indices"]["ndwi"]))
    m_ndbi  = float(np.mean(R["indices"]["ndbi"]))
    veg_pct = sum(
        v["percentage"] for k, v in R["lulc_stats"].items()
        if "Vegetation" in k
    )
    urban_pct = R["lulc_stats"].get("Urban/Built-up", {}).get("percentage", 0)
    n_scenes  = R["metadata"].get("n_scenes", "—")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Mean NDVI",  f"{m_ndvi:.3f}",  "Vegetation Health")
    c2.metric("Mean NDWI",  f"{m_ndwi:.3f}",  "Water Index")
    c3.metric("Mean NDBI",  f"{m_ndbi:.3f}",  "Built-up Index")
    c4.metric("Vegetation", f"{veg_pct:.1f}%", "Scene Coverage")
    c5.metric("Urban",      f"{urban_pct:.1f}%", "Scene Coverage")
    c6.metric("Scenes",     str(n_scenes),    "Available")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_maps, tab_indices, tab_lulc, tab_change, tab_report = st.tabs([
        "🗺️ Maps",
        "📊 Spectral Indices",
        "🌿 Land Cover",
        "🔄 Change Detection",
        "📄 Report",
    ])

    # =========================================================================
    # TAB 1 — Maps
    # =========================================================================
    with tab_maps:
        st.markdown('<p class="section-header">Spectral & Classification Maps</p>', unsafe_allow_html=True)

        col_ndvi, col_lulc = st.columns(2)

        with col_ndvi:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("NDVI Map")
            ndvi_arr = R["indices"]["ndvi"]
            fig_ndvi = px.imshow(
                ndvi_arr,
                color_continuous_scale="RdYlGn",
                zmin=-0.2, zmax=0.8,
                title=f"NDVI — {R['region_name']}",
                labels={"color": "NDVI"},
                aspect="equal",
            )
            fig_ndvi = apply_template(fig_ndvi)
            fig_ndvi.update_layout(coloraxis_colorbar=dict(title="NDVI", tickfont_color="#94a3b8"))
            st.plotly_chart(fig_ndvi, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_lulc:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("LULC Classification Map")
            # Build discrete colourscale for Plotly
            lulc_arr = R["lulc_map"].astype(float)
            fig_lulc = px.imshow(
                R["lulc_rgb"],
                title=f"LULC — {R['region_name']}",
                aspect="equal",
            )
            fig_lulc = apply_template(fig_lulc)
            fig_lulc.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_lulc, use_container_width=True)

            # Legend
            legend_html = "<div style='display:flex; flex-wrap:wrap; gap:8px; margin-top:8px;'>"
            for cid, cname in LULC_CLASSES.items():
                color = LULC_COLORS[cid]
                legend_html += (
                    f"<span style='background:{color}; color:white; border-radius:6px; "
                    f"padding:3px 10px; font-size:0.75rem;'>{cname}</span>"
                )
            legend_html += "</div>"
            st.markdown(legend_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Folium map ────────────────────────────────────────────────────────
        st.markdown('<p class="section-header">Interactive Map</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        try:
            from streamlit_folium import st_folium
            fmap = create_folium_map(
                region_name=R["region_name"],
                bbox=R["bbox"],
                lulc_b64=R["lulc_b64"],
            )
            st_folium(fmap, width=None, height=420, returned_objects=[])
        except ImportError:
            st.info("Install `streamlit-folium` to see the interactive map.")
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2 — Spectral Indices
    # =========================================================================
    with tab_indices:
        st.markdown('<p class="section-header">Spectral Index Heatmaps</p>', unsafe_allow_html=True)

        idx_cfg = [
            ("ndvi", "NDVI",  "RdYlGn",  (-0.2, 0.8)),
            ("ndwi", "NDWI",  "Blues",   (-0.5, 0.5)),
            ("ndbi", "NDBI",  "OrRd",    (-0.5, 0.5)),
            ("evi",  "EVI",   "Greens",  (-0.2, 1.0)),
        ]

        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        cols = [row1_col1, row1_col2, row2_col1, row2_col2]

        for (key, label, cmap, zrange), col in zip(idx_cfg, cols):
            with col:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                arr = R["indices"][key]
                fig = px.imshow(
                    arr,
                    color_continuous_scale=cmap,
                    zmin=zrange[0], zmax=zrange[1],
                    title=f"{label} Heatmap",
                    labels={"color": label},
                    aspect="equal",
                )
                apply_template(fig)
                fig.update_layout(coloraxis_colorbar=dict(title=label, tickfont_color="#94a3b8"))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ── Index statistics table ─────────────────────────────────────────────
        st.markdown('<p class="section-header">Index Statistics</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        stats_rows = []
        for name, s in R["idx_stats"].items():
            stats_rows.append({
                "Index": name.upper(),
                "Mean":   round(s["mean"], 4),
                "Std":    round(s["std"],  4),
                "Min":    round(s["min"],  4),
                "Max":    round(s["max"],  4),
                "Median": round(s["p50"],  4),
                "P5":     round(s["p5"],   4),
                "P95":    round(s["p95"],  4),
            })
        df_stats = pd.DataFrame(stats_rows)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

        # ── Violin / box comparison ───────────────────────────────────────────
        st.markdown('<p class="section-header">Distribution Comparison</p>', unsafe_allow_html=True)
        flat_data = []
        for name in ["ndvi", "ndwi", "ndbi", "evi"]:
            arr_flat = R["indices"][name].ravel()
            for v in arr_flat:
                flat_data.append({"Index": name.upper(), "Value": float(v)})
        df_dist = pd.DataFrame(flat_data)
        fig_box = px.violin(
            df_dist, x="Index", y="Value", color="Index",
            box=True, points=False,
            color_discrete_sequence=["#2d8a4e", "#1a6faf", "#c0392b", "#8e44ad"],
            title="Spectral Index Value Distributions",
        )
        apply_template(fig_box)
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 3 — Land Cover
    # =========================================================================
    with tab_lulc:
        st.markdown('<p class="section-header">Land Use / Land Cover Analysis</p>', unsafe_allow_html=True)

        col_pie, col_bar = st.columns([1, 1])

        with col_pie:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            labels = list(R["lulc_stats"].keys())
            values = [v["pixel_count"] for v in R["lulc_stats"].values()]
            colors = [v["color"] for v in R["lulc_stats"].values()]
            fig_pie = go.Figure(go.Pie(
                labels=labels, values=values,
                marker=dict(colors=colors, line=dict(color="#0d1117", width=2)),
                hole=0.42,
                textinfo="label+percent",
                textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{label}</b><br>Pixels: %{value:,}<br>%{percent}<extra></extra>",
            ))
            fig_pie.update_layout(
                title=dict(text="LULC Class Distribution", font=dict(color="#a78bfa", size=14)),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c0c8e0"),
                margin=dict(l=10, r=10, t=50, b=10),
                showlegend=True,
                legend=dict(
                    font=dict(color="#94a3b8", size=11),
                    bgcolor="rgba(0,0,0,0)",
                ),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_bar:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            class_names   = list(R["lulc_stats"].keys())
            area_values   = [v["area_km2"] for v in R["lulc_stats"].values()]
            bar_colors    = [v["color"] for v in R["lulc_stats"].values()]
            fig_bar = go.Figure(go.Bar(
                x=class_names,
                y=area_values,
                marker=dict(color=bar_colors, line=dict(color="#0d1117", width=1)),
                hovertemplate="<b>%{x}</b><br>Area: %{y:.4f} km²<extra></extra>",
                text=[f"{a:.4f} km²" for a in area_values],
                textposition="outside",
                textfont=dict(color="#94a3b8", size=10),
            ))
            fig_bar.update_layout(
                title=dict(text="Area Coverage by LULC Class (km²)", font=dict(color="#a78bfa", size=14)),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10,12,35,0.6)",
                font=dict(color="#c0c8e0"),
                margin=dict(l=20, r=20, t=50, b=80),
                xaxis=dict(tickangle=-30, gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Area (km²)"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── LULC stats table ─────────────────────────────────────────────────
        st.markdown('<p class="section-header">Detailed LULC Statistics</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        rows = []
        for class_name, s in R["lulc_stats"].items():
            rows.append({
                "Class":      class_name,
                "Pixels":     f"{s['pixel_count']:,}",
                "Area (km²)": f"{s['area_km2']:.4f}",
                "Coverage %": f"{s['percentage']:.2f}%",
                "Color":      s.get("color", "#888"),
            })
        df_lulc = pd.DataFrame(rows)
        st.dataframe(df_lulc.drop(columns=["Color"]), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 4 — Change Detection
    # =========================================================================
    with tab_change:
        st.markdown('<p class="section-header">Bi-temporal Change Detection (2020 → 2024)</p>', unsafe_allow_html=True)

        cr = R["change_results"]

        # ── NDVI side-by-side ─────────────────────────────────────────────────
        col_t1, col_t2, col_diff = st.columns(3)

        with col_t1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig_t1 = px.imshow(
                cr["ndvi_t1"], color_continuous_scale="RdYlGn",
                zmin=-0.2, zmax=0.8, title="NDVI — 2020", aspect="equal",
            )
            apply_template(fig_t1)
            st.plotly_chart(fig_t1, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_t2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig_t2 = px.imshow(
                cr["ndvi_t2"], color_continuous_scale="RdYlGn",
                zmin=-0.2, zmax=0.8, title="NDVI — 2024", aspect="equal",
            )
            apply_template(fig_t2)
            st.plotly_chart(fig_t2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_diff:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig_diff = px.imshow(
                cr["ndvi_diff"], color_continuous_scale="RdBu",
                zmin=-0.3, zmax=0.3, title="NDVI Change (ΔV)", aspect="equal",
            )
            apply_template(fig_diff)
            st.plotly_chart(fig_diff, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Semantic change map ───────────────────────────────────────────────
        st.markdown('<p class="section-header">Semantic Change Classification</p>', unsafe_allow_html=True)

        col_cmap, col_cstats = st.columns([1, 1])

        with col_cmap:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            change_rgb = lulc_map_to_rgb_image(cr["change_map"], CHANGE_COLORS)
            fig_change = px.imshow(change_rgb, title="Change Map", aspect="equal")
            apply_template(fig_change)
            fig_change.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_change, use_container_width=True)

            from src.config import CHANGE_CLASSES
            legend_html = "<div style='display:flex; flex-wrap:wrap; gap:8px; margin-top:4px;'>"
            for cid, cname in CHANGE_CLASSES.items():
                color = CHANGE_COLORS[cid]
                legend_html += (
                    f"<span style='background:{color}; color:white; border-radius:6px; "
                    f"padding:3px 10px; font-size:0.75rem;'>{cname}</span>"
                )
            legend_html += "</div>"
            st.markdown(legend_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cstats:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            ch_labels = list(cr["statistics"].keys())
            ch_values = [v["pixel_count"] for v in cr["statistics"].values()]
            ch_colors = [v.get("color", "#888") for v in cr["statistics"].values()]

            fig_cpie = go.Figure(go.Pie(
                labels=ch_labels, values=ch_values,
                marker=dict(colors=ch_colors, line=dict(color="#0d1117", width=2)),
                hole=0.40,
                textinfo="label+percent",
                textfont=dict(size=10, color="white"),
            ))
            fig_cpie.update_layout(
                title=dict(text="Change Class Distribution", font=dict(color="#a78bfa", size=13)),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#c0c8e0"),
                margin=dict(l=10, r=10, t=50, b=10),
                showlegend=False,
            )
            st.plotly_chart(fig_cpie, use_container_width=True)

            # Stats table
            ch_rows = []
            for cname, s in cr["statistics"].items():
                ch_rows.append({
                    "Change Class": cname,
                    "Area (km²)":   f"{s['area_km2']:.4f}",
                    "Coverage %":   f"{s['percentage']:.2f}%",
                })
            st.dataframe(pd.DataFrame(ch_rows), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 5 — Report
    # =========================================================================
    with tab_report:
        st.markdown('<p class="section-header">Downloadable Analysis Report</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        col_dl, col_info = st.columns([1, 2])
        with col_dl:
            st.download_button(
                label="⬇️  Download HTML Report",
                data=R["html_report"],
                file_name=f"EO_Report_{R['region_name']}_{R['date_start']}_{R['date_end']}.html",
                mime="text/html",
                use_container_width=True,
            )
            st.caption("Open in any modern browser — fully self-contained.")

        with col_info:
            st.markdown(
                f"""
                <div class="glass-card-blue">
                  <b>Report Contents</b><br>
                  📡 Acquisition metadata &nbsp;|&nbsp;
                  📈 Spectral index histograms &nbsp;|&nbsp;
                  🗺️ LULC statistics table &nbsp;|&nbsp;
                  🔄 Change detection summary &nbsp;|&nbsp;
                  📊 Embedded charts (base64 PNG)
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Inline preview
        st.markdown('<p class="section-header">Report Preview</p>', unsafe_allow_html=True)
        import streamlit.components.v1 as components
        components.html(R["html_report"], height=800, scrolling=True)


# =============================================================================
# ── HERO PLACEHOLDERS (before any analysis) ───────────────────────────────────
# =============================================================================
else:
    # Animated placeholder metric cards
    st.markdown(
        """
        <div class="metric-row">
          <div class="metric-card">
            <div class="m-label">Mean NDVI</div>
            <div class="m-value" style="color:#2d8a4e;">—</div>
            <div class="m-delta">Run analysis to compute</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Mean NDWI</div>
            <div class="m-value" style="color:#1a6faf;">—</div>
            <div class="m-delta">Run analysis to compute</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Urban Cover</div>
            <div class="m-value" style="color:#c0392b;">—</div>
            <div class="m-delta">Run analysis to compute</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Vegetation</div>
            <div class="m-value" style="color:#8ab87a;">—</div>
            <div class="m-delta">Run analysis to compute</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Change Area</div>
            <div class="m-value" style="color:#e67e22;">—</div>
            <div class="m-delta">Run analysis to compute</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Scenes</div>
            <div class="m-value" style="color:#4a9eff;">—</div>
            <div class="m-delta">Run analysis to compute</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Getting-started guide
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Select a region** from the sidebar (Lahore, Karachi, Islamabad, Gilgit, Peshawar)
    2. **Set the analysis period** — default is 2020–2024 for change detection
    3. **Adjust cloud cover threshold** and number of LULC clusters
    4. Click **🚀 Run Analysis** to execute the full pipeline

    The pipeline will:
    - Generate synthetic Sentinel-2 L2A imagery with realistic spectral profiles
    - Compute NDVI, NDWI, NDBI and EVI spectral indices
    - Run KMeans clustering with automatic LULC semantic labelling
    - Perform bi-temporal change detection (2020 → 2024)
    - Produce an interactive Folium map and downloadable HTML report
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📐 Pipeline Architecture")
    st.code(
        """
        STAC Query  →  Band Loading  →  Spectral Indices
              ↓                              ↓
        Cloud Mask              NDVI · NDWI · NDBI · EVI
              ↓                              ↓
        Feature Matrix  →  KMeans  →  Auto-Label Clusters
                                            ↓
        LULC Map + Statistics       Change Detection
              ↓                            ↓
              └────── HTML Report + Folium Map ──────┘
        """,
        language="text",
    )
    st.markdown("</div>", unsafe_allow_html=True)
