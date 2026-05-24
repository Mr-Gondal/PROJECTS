"""
app.py — Streamlit Dashboard for the Spatial Data ETL Pipeline.

Provides an interactive monitoring and exploration interface for the
Pakistan GIS Data ETL Pipeline including:
  - Live pipeline execution with progress tracking
  - Spatial district explorer (folium + plotly maps)
  - Data quality validation dashboard
  - SQL explorer for ad-hoc analysis
  - Analytics charts (AQI, population, land-use)

Author: Haris Hussain
Project: Spatial Data ETL Pipeline | Pakistan Geospatial Data Platform
"""

import os
import sys
import time
import uuid
import logging
import datetime
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─── Path setup (run from project root) ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")

from src.config import DB_PATH, PROVINCE_COLORS, PAKISTAN_DISTRICTS
from src.extractor  import DataExtractor
from src.transformer import DataTransformer
from src.loader      import DataLoader
from src.validator   import DataValidator
from src.monitor     import PipelineMonitor

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spatial Data ETL Pipeline",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS — Industrial dark theme with amber accents ────────────────────
st.markdown("""
<style>
  /* ── Root & fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600;700&display=swap');

  :root {
    --bg-primary:   #0a0e1a;
    --bg-secondary: #0f1629;
    --bg-card:      rgba(245,158,11,0.04);
    --border-card:  rgba(245,158,11,0.20);
    --amber:        #f59e0b;
    --amber-dark:   #d97706;
    --amber-glow:   rgba(245,158,11,0.15);
    --text-primary: #f1f5f9;
    --text-muted:   #94a3b8;
    --success:      #22c55e;
    --warning:      #f59e0b;
    --danger:       #ef4444;
    --info:         #3b82f6;
  }

  /* Global background */
  .stApp { background: var(--bg-primary) !important; font-family: 'Inter', sans-serif; }
  .main .block-container { padding: 1.5rem 2rem; max-width: 1600px; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1629 0%, #0a0e1a 100%) !important;
    border-right: 1px solid rgba(245,158,11,0.15) !important;
  }
  [data-testid="stSidebar"] .stMarkdown h1,
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 { color: var(--amber) !important; }

  /* Glass cards */
  .glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
  }
  .glass-card:hover { box-shadow: 0 0 20px var(--amber-glow); }

  /* KPI metrics */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  .kpi-card {
    background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(217,119,6,0.04));
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #f59e0b, #d97706);
  }
  .kpi-value {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-family: 'JetBrains Mono', monospace;
  }
  .kpi-label { color: var(--text-muted); font-size: 0.78rem; margin-top: 0.3rem; letter-spacing: 0.05em; text-transform: uppercase; }
  .kpi-delta { font-size: 0.75rem; color: var(--success); margin-top: 0.2rem; }

  /* Status badges */
  .status-running { color: #f59e0b; animation: pulse 1.5s infinite; }
  .status-idle    { color: #22c55e; }
  .status-error   { color: #ef4444; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  /* Pipeline stages */
  .pipeline-stage {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.78rem;
    font-weight: 600; letter-spacing: 0.03em;
  }
  .stage-extract   { background: rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
  .stage-transform { background: rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); }
  .stage-validate  { background: rgba(139,92,246,0.15); color:#a78bfa; border:1px solid rgba(139,92,246,0.3); }
  .stage-load      { background: rgba(34,197,94,0.15);  color:#4ade80; border:1px solid rgba(34,197,94,0.3); }

  /* Tables */
  .stDataFrame { background: var(--bg-secondary) !important; }
  .stDataFrame thead th { background: rgba(245,158,11,0.12) !important; color: var(--amber) !important; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(245,158,11,0.05) !important;
    border-bottom: 1px solid rgba(245,158,11,0.2) !important;
    border-radius: 8px 8px 0 0;
    padding: 0 1rem;
    gap: 0.5rem;
  }
  .stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 500; padding: 0.6rem 1rem;
    border-radius: 6px 6px 0 0;
    transition: all 0.2s;
  }
  .stTabs [aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
    background: rgba(245,158,11,0.08) !important;
  }

  /* Buttons */
  .stButton button {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    color: #0a0e1a !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.03em;
  }
  .stButton button:hover {
    box-shadow: 0 0 20px rgba(245,158,11,0.4) !important;
    transform: translateY(-1px);
  }

  /* Headings */
  h1, h2, h3 { color: var(--text-primary) !important; }
  .amber-text { color: var(--amber); font-weight: 700; }

  /* Code blocks */
  code { font-family: 'JetBrains Mono', monospace; background: rgba(245,158,11,0.08); color: var(--amber); padding: 0.1em 0.4em; border-radius: 4px; }

  /* Select/input */
  .stSelectbox > div > div,
  .stTextArea > div > div { background: var(--bg-secondary) !important; border-color: rgba(245,158,11,0.2) !important; color: var(--text-primary) !important; }

  /* Metric */
  [data-testid="stMetricValue"] { color: var(--amber) !important; }
  [data-testid="stMetricLabel"] { color: var(--text-muted) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helper: apply dark plotly theme ─────────────────────────────────────────
def _dark_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(color="#f59e0b", size=15)),
        paper_bgcolor="#0f1629",
        plot_bgcolor="#0a0e1a",
        font=dict(color="#94a3b8", family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#f1f5f9")),
        margin=dict(t=50, b=30, l=40, r=20),
        coloraxis_colorbar=dict(tickfont=dict(color="#94a3b8")),
        xaxis=dict(
            gridcolor="rgba(245,158,11,0.08)",
            zerolinecolor="rgba(245,158,11,0.15)",
            tickfont=dict(color="#94a3b8"),
        ),
        yaxis=dict(
            gridcolor="rgba(245,158,11,0.08)",
            zerolinecolor="rgba(245,158,11,0.15)",
            tickfont=dict(color="#94a3b8"),
        ),
    )
    return fig


# ─── Session state init ───────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "pipeline_status": "idle",  # idle | running | error | complete
        "last_run_meta":   {},
        "pipeline_log":    [],
        "run_count":       0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()
monitor = PipelineMonitor(DB_PATH)


# ─── Core Pipeline Runner ─────────────────────────────────────────────────────
def run_full_pipeline(
    progress_bar=None,
    status_box=None,
    log_container=None,
) -> dict:
    """Execute the full Extract→Transform→Validate→Load pipeline."""
    logs = []

    def _log(msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{ts}] {msg}")
        st.session_state["pipeline_log"] = logs.copy()
        if log_container:
            log_container.code("\n".join(logs[-20:]), language=None)

    run_id    = str(uuid.uuid4())[:12]
    started   = datetime.datetime.now()
    _log(f"🚀 Pipeline run [{run_id}] started at {started.strftime('%H:%M:%S')}")

    # ── EXTRACT ──
    if progress_bar: progress_bar.progress(5, "Extracting data…")
    if status_box:   status_box.update(label="⏳ Extracting…", state="running")
    _log("📥 STAGE 1: EXTRACT — pulling from simulated sources")
    t0 = time.time()
    extractor = DataExtractor()
    raw = extractor.run_all_extractions()
    extract_time = round(time.time() - t0, 2)
    _log(f"   ✅ Extracted {raw['metadata']['total_records']:,} records in {extract_time}s")
    if progress_bar: progress_bar.progress(30, "Extraction complete")
    time.sleep(0.3)

    # ── TRANSFORM ──
    if progress_bar: progress_bar.progress(35, "Transforming data…")
    if status_box:   status_box.update(label="🔄 Transforming…", state="running")
    _log("🔄 STAGE 2: TRANSFORM — cleaning, reprojecting, enriching")
    t0 = time.time()
    transformer = DataTransformer()
    transformed = transformer.transform_all(raw)
    transform_time = round(time.time() - t0, 2)
    _log(f"   ✅ Transformed {transformed['metadata']['records_transformed']:,} records in {transform_time}s")
    if progress_bar: progress_bar.progress(60, "Transformation complete")
    time.sleep(0.3)

    # ── VALIDATE ──
    if progress_bar: progress_bar.progress(65, "Validating data…")
    if status_box:   status_box.update(label="✅ Validating…", state="running")
    _log("✅ STAGE 3: VALIDATE — running quality checks")
    t0 = time.time()
    validator = DataValidator()
    reports = {}
    for dataset_name in ("census", "environmental", "land_use", "infrastructure"):
        src_df = {
            "census":         transformed["census"],
            "environmental":  transformed["environmental"],
            "land_use":       transformed["land_use"],
            "infrastructure": transformed["infrastructure"],
        }[dataset_name]
        rpt = validator.run_full_validation(src_df, dataset_name)
        reports[dataset_name] = rpt
        _log(f"   [{dataset_name}] Score={rpt.quality_score} | "
             f"PASS={rpt.passed} WARN={rpt.warned} FAIL={rpt.failed}")
    validate_time = round(time.time() - t0, 2)
    avg_score = round(sum(r.quality_score for r in reports.values()) / len(reports), 1)
    _log(f"   ✅ Validation complete in {validate_time}s | Avg score: {avg_score}")
    if progress_bar: progress_bar.progress(80, "Validation complete")
    time.sleep(0.3)

    # ── LOAD ──
    if progress_bar: progress_bar.progress(85, "Loading into database…")
    if status_box:   status_box.update(label="💾 Loading…", state="running")
    _log("💾 STAGE 4: LOAD — inserting into SQLite database")
    t0 = time.time()
    load_stats = DataLoader.load_all(transformed, DB_PATH)
    load_time = round(time.time() - t0, 2)
    _log(f"   ✅ Loaded {load_stats['total_loaded']:,} rows in {load_time}s")
    for tbl, cnt in load_stats["table_stats"].items():
        _log(f"   → {tbl}: {cnt} rows")
    if progress_bar: progress_bar.progress(95, "Load complete")
    time.sleep(0.2)

    # ── LOG RUN METADATA ──
    total_dur = round((datetime.datetime.now() - started).total_seconds(), 2)
    run_meta = {
        "run_id":              run_id,
        "pipeline_name":       "Pakistan Spatial ETL",
        "pipeline_version":    "1.0.0",
        "started_at":          started.isoformat(),
        "completed_at":        datetime.datetime.now().isoformat(),
        "duration_seconds":    total_dur,
        "status":              "SUCCESS",
        "records_extracted":   raw["metadata"]["total_records"],
        "records_transformed": transformed["metadata"]["records_transformed"],
        "records_loaded":      load_stats["total_loaded"],
        "quality_score":       avg_score,
        "error_message":       None,
        "triggered_by":        "streamlit_ui",
    }
    conn = DataLoader.initialize_database(DB_PATH)
    DataLoader.log_pipeline_run(conn, run_meta)
    conn.close()

    if progress_bar: progress_bar.progress(100, "Pipeline complete ✅")
    if status_box:   status_box.update(label="✅ Pipeline complete!", state="complete")

    _log(f"🏁 Pipeline finished in {total_dur}s | Quality score: {avg_score}/100")
    st.session_state["pipeline_status"] = "complete"
    st.session_state["last_run_meta"]   = run_meta
    st.session_state["run_count"]      += 1

    return {
        "run_meta":    run_meta,
        "raw":         raw,
        "transformed": transformed,
        "reports":     reports,
        "load_stats":  load_stats,
    }


def run_extract_only() -> dict:
    """Run extraction only and save raw files."""
    extractor = DataExtractor()
    raw = extractor.run_all_extractions()
    st.session_state["pipeline_log"].append(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
        f"Extraction-only run: {raw['metadata']['total_records']} records"
    )
    return raw


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
      <div style='font-size:2.5rem'>⚙️</div>
      <div style='color:#f59e0b; font-size:1.1rem; font-weight:700; letter-spacing:0.05em'>
        ETL PIPELINE
      </div>
      <div style='color:#64748b; font-size:0.72rem; margin-top:0.2rem'>
        Pakistan Geospatial Platform
      </div>
    </div>
    <hr style='border-color:rgba(245,158,11,0.15); margin: 0.8rem 0;'>
    """, unsafe_allow_html=True)

    # Pipeline controls
    st.markdown("### 🎛️ Pipeline Controls")

    run_full_btn   = st.button("▶️ Run Full Pipeline", use_container_width=True)
    run_extract_btn = st.button("📥 Extract Only",      use_container_width=True)

    st.markdown("<hr style='border-color:rgba(245,158,11,0.1);'>", unsafe_allow_html=True)
    st.markdown("### 🗄️ Database")

    db_exists = os.path.exists(DB_PATH)
    if db_exists:
        db_size = round(os.path.getsize(DB_PATH) / 1024, 1)
        st.success(f"✅ DB Connected ({db_size} KB)")
    else:
        st.warning("⚠️ No database — run pipeline first")

    st.markdown("<hr style='border-color:rgba(245,158,11,0.1);'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")

    random_seed = st.slider("Random Seed", 1, 99, 42)
    show_raw    = st.checkbox("Show Raw Data Mode", value=False)

    st.markdown("<hr style='border-color:rgba(245,158,11,0.1);'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color:#475569; font-size:0.72rem; text-align:center; padding-bottom:1rem'>
      <b style='color:#f59e0b'>Haris Hussain</b><br>
      Space Science | GIS & Remote Sensing<br>
      University of Punjab, Lahore<br><br>
      <span style='font-family:monospace'>v1.0.0</span>
    </div>
    """, unsafe_allow_html=True)


# ─── HEADER ──────────────────────────────────────────────────────────────────
status_color = {"idle": "#22c55e", "running": "#f59e0b",
                "error": "#ef4444", "complete": "#22c55e"}
status_label = {"idle": "● IDLE", "running": "◉ RUNNING",
                "error": "● ERROR", "complete": "● READY"}

current_status = st.session_state["pipeline_status"]

st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;'>
  <div>
    <h1 style='margin:0; font-size:1.8rem; background:linear-gradient(135deg,#f59e0b,#d97706);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;'>
      ⚙️ Spatial Data ETL Pipeline
    </h1>
    <p style='margin:0.2rem 0 0; color:#64748b; font-size:0.85rem;'>
      Pakistan Geospatial Data Platform &nbsp;|&nbsp; Extract · Transform · Validate · Load
    </p>
  </div>
  <div style='text-align:right'>
    <div style='color:{status_color[current_status]}; font-weight:700; font-size:1rem;
                font-family:monospace;'>{status_label[current_status]}</div>
    <div style='color:#475569; font-size:0.72rem; margin-top:0.2rem;'>
      Runs: {st.session_state["run_count"]}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Pipeline stage indicator
st.markdown("""
<div style='display:flex; gap:0.5rem; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap;'>
  <span class='pipeline-stage stage-extract'>📥 EXTRACT</span>
  <span style='color:#475569'>→</span>
  <span class='pipeline-stage stage-transform'>🔄 TRANSFORM</span>
  <span style='color:#475569'>→</span>
  <span class='pipeline-stage stage-validate'>✅ VALIDATE</span>
  <span style='color:#475569'>→</span>
  <span class='pipeline-stage stage-load'>💾 LOAD</span>
  <span style='color:#475569'>→</span>
  <span class='pipeline-stage' style='background:rgba(245,158,11,0.15);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);'>
    🗄️ SQLite DB
  </span>
  <span style='color:#475569'>→</span>
  <span class='pipeline-stage' style='background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3);'>
    📊 Dashboard
  </span>
</div>
""", unsafe_allow_html=True)


# ─── PIPELINE EXECUTION (button handlers) ────────────────────────────────────
if run_full_btn:
    st.session_state["pipeline_status"] = "running"
    with st.status("⚙️ Running ETL Pipeline…", expanded=True) as status_box:
        progress_bar  = st.progress(0, "Initialising…")
        log_container = st.empty()
        result = run_full_pipeline(progress_bar, status_box, log_container)

    meta = result["run_meta"]
    st.markdown("---")
    st.markdown("### ✅ Pipeline Complete — Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records Extracted",   f"{meta['records_extracted']:,}")
    c2.metric("Records Loaded",      f"{meta['records_loaded']:,}")
    c3.metric("Quality Score",       f"{meta['quality_score']}/100")
    c4.metric("Duration",            f"{meta['duration_seconds']}s")
    st.success(f"Run ID: `{meta['run_id']}` | Status: {meta['status']}")
    st.rerun()

if run_extract_btn:
    with st.spinner("📥 Running extraction only…"):
        raw = run_extract_only()
    st.success(f"Extracted {raw['metadata']['total_records']:,} records. Raw files saved to `data/raw/`")


# ─── MAIN TABS ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Pipeline Dashboard",
    "🗺️ Spatial Explorer",
    "📋 Data Tables",
    "✅ Data Quality",
    "🔍 SQL Explorer",
    "📈 Analytics",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: Pipeline Dashboard
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    summary = monitor.get_database_summary()
    table_stats = monitor.get_table_stats()
    recent_runs = monitor.get_recent_runs(20)

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-value'>{summary['total_records']:,}</div>
          <div class='kpi-label'>Total Records in DB</div>
          <div class='kpi-delta'>across all tables</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-value'>{summary['tables_populated']}</div>
          <div class='kpi-label'>Tables Populated</div>
          <div class='kpi-delta'>of 4 data tables</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        score = summary['quality_score']
        score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-value' style='background:linear-gradient(135deg,{score_color},{score_color}88);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{score:.0f}</div>
          <div class='kpi-label'>Quality Score /100</div>
          <div class='kpi-delta'>completeness + bounds</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='kpi-card'>
          <div class='kpi-value' style='font-size:1.1rem;'>{str(summary['last_run_at'])[:16] or 'Never'}</div>
          <div class='kpi-label'>Last Pipeline Run</div>
          <div class='kpi-delta'>{summary['last_run_status']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### 📈 Run History — Records Loaded per Run")
        if len(recent_runs) > 0:
            fig_runs = px.bar(
                recent_runs.sort_values("started_at"),
                x="started_at", y="records_loaded",
                color="quality_score",
                color_continuous_scale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#22c55e"]],
                text="records_loaded",
                custom_data=["run_id", "duration_seconds", "status"],
            )
            fig_runs.update_traces(
                textposition="outside",
                textfont_color="#f59e0b",
                hovertemplate=(
                    "<b>Run</b>: %{customdata[0]}<br>"
                    "Records: %{y:,}<br>"
                    "Duration: %{customdata[1]}s<br>"
                    "Status: %{customdata[2]}"
                ),
            )
            fig_runs = _dark_layout(fig_runs, "Pipeline Run History")
            fig_runs.update_xaxes(tickangle=30, title=None)
            fig_runs.update_yaxes(title="Records Loaded")
            st.plotly_chart(fig_runs, use_container_width=True)
        else:
            st.info("No pipeline runs yet. Click **▶️ Run Full Pipeline** to start.")

    with col_right:
        st.markdown("#### 🗄️ Database Table Status")
        st.markdown("<br>", unsafe_allow_html=True)
        if len(table_stats) > 0:
            st.dataframe(
                table_stats[["table", "row_count", "last_loaded", "status"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Database not initialised yet.")

        if len(recent_runs) > 0:
            st.markdown("#### ⏱️ Recent Pipeline Runs")
            display_cols = ["run_id", "started_at", "status",
                            "records_loaded", "duration_seconds", "quality_score"]
            avail = [c for c in display_cols if c in recent_runs.columns]
            st.dataframe(
                recent_runs[avail].head(5),
                use_container_width=True,
                hide_index=True,
            )

    # Pipeline log
    if st.session_state["pipeline_log"]:
        with st.expander("📝 Pipeline Log (last run)", expanded=False):
            st.code("\n".join(st.session_state["pipeline_log"]), language=None)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: Spatial Explorer
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 🗺️ Pakistan District Spatial Explorer")
    districts_df = DataLoader.query_database(DB_PATH,
        "SELECT * FROM districts LIMIT 200") if os.path.exists(DB_PATH) else pd.DataFrame()

    # If DB empty, generate synthetic data on-the-fly for display
    if len(districts_df) == 0:
        extractor = DataExtractor()
        districts_df = extractor.extract_census_data()
        districts_df.rename(columns={"latitude": "centroid_lat",
                                      "longitude": "centroid_lon"}, inplace=True)
        st.info("💡 Showing synthetic preview — run the pipeline to load into DB.")

    map_col, ctrl_col = st.columns([3, 1])

    with ctrl_col:
        st.markdown("**Map Settings**")
        color_var = st.selectbox("Colour by", [
            "pop_density", "urban_pct", "growth_rate_pct",
            "literacy_rate", "population",
        ], key="map_color")
        map_style = st.selectbox("Map style", [
            "open-street-map", "carto-darkmatter",
            "stamen-terrain", "white-bg",
        ], key="map_style")
        show_labels = st.checkbox("Show district labels", value=True)
        st.markdown("---")
        st.markdown("**Province filter**")
        provinces = sorted(districts_df["province"].dropna().unique().tolist()) \
                    if "province" in districts_df.columns else []
        sel_provinces = st.multiselect("Show provinces", provinces,
                                       default=provinces, key="prov_filter")

    if sel_provinces and "province" in districts_df.columns:
        plot_df = districts_df[districts_df["province"].isin(sel_provinces)].copy()
    else:
        plot_df = districts_df.copy()

    lat_col = "centroid_lat" if "centroid_lat" in plot_df.columns else "latitude"
    lon_col = "centroid_lon" if "centroid_lon" in plot_df.columns else "longitude"
    name_col = "name" if "name" in plot_df.columns else "district"

    plot_df = plot_df.dropna(subset=[lat_col, lon_col])

    with map_col:
        if len(plot_df) > 0 and color_var in plot_df.columns:
            hover_cols = [name_col, "province", color_var]
            hover_cols = [c for c in hover_cols if c in plot_df.columns]

            fig_map = px.scatter_mapbox(
                plot_df,
                lat=lat_col, lon=lon_col,
                color=color_var,
                size="population" if "population" in plot_df.columns else None,
                size_max=30,
                color_continuous_scale=[
                    [0.0,  "#0f1629"],
                    [0.3,  "#d97706"],
                    [0.7,  "#f59e0b"],
                    [1.0,  "#fbbf24"],
                ],
                hover_name=name_col,
                hover_data={c: True for c in hover_cols},
                mapbox_style=map_style,
                zoom=4.5,
                center={"lat": 30.3, "lon": 69.5},
                opacity=0.85,
                text=name_col if show_labels else None,
            )
            fig_map.update_traces(
                textposition="top center",
                textfont=dict(color="#f59e0b", size=9),
                marker=dict(sizemin=6),
            )
            fig_map.update_layout(
                paper_bgcolor="#0a0e1a",
                mapbox=dict(style=map_style),
                margin=dict(l=0, r=0, t=0, b=0),
                height=560,
                coloraxis_colorbar=dict(
                    title=dict(text=color_var.replace("_", " ").title(), font=dict(color="#f59e0b")),
                    tickfont=dict(color="#94a3b8"),
                    bgcolor="rgba(10,14,26,0.8)",
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning(f"Column `{color_var}` not available. Run the pipeline first.")

    # Province population bar chart
    st.markdown("#### 🏙️ Population by Province")
    if "province" in plot_df.columns and "population" in plot_df.columns:
        prov_pop = (
            plot_df.groupby("province")["population"]
            .sum().reset_index()
            .sort_values("population", ascending=True)
        )
        fig_prov = px.bar(
            prov_pop, y="province", x="population",
            orientation="h",
            color="province",
            color_discrete_map=PROVINCE_COLORS,
            text=prov_pop["population"].apply(lambda x: f"{x/1e6:.1f}M"),
        )
        fig_prov.update_traces(textposition="outside", textfont_color="#f59e0b")
        fig_prov = _dark_layout(fig_prov, "Total Population by Province")
        fig_prov.update_xaxes(title="Population")
        fig_prov.update_yaxes(title=None)
        fig_prov.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_prov, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: Data Tables
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 📋 Database Explorer")

    table_choices = {
        "Districts":          "SELECT * FROM districts",
        "Environmental Data": "SELECT * FROM environmental_data LIMIT 500",
        "Land Use":           "SELECT * FROM land_use",
        "Infrastructure":     "SELECT * FROM infrastructure",
        "Pipeline Runs":      "SELECT * FROM pipeline_runs ORDER BY started_at DESC",
    }

    sel_table = st.selectbox("Select table to explore", list(table_choices.keys()))
    query     = table_choices[sel_table]

    df_table  = DataLoader.query_database(DB_PATH, query)

    if "error" in df_table.columns:
        st.warning("⚠️ Database not available. Run the pipeline first.")
    elif len(df_table) == 0:
        st.info(f"Table is empty. Run the pipeline first.")
    else:
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Rows",    f"{len(df_table):,}")
        col_b.metric("Columns", f"{len(df_table.columns)}")
        col_c.metric("Nulls",   f"{df_table.isna().sum().sum():,}")
        col_d.metric("Memory",  f"{df_table.memory_usage(deep=True).sum() / 1024:.1f} KB")

        # Filters
        exp_filter = st.expander("🔽 Column Filters", expanded=False)
        with exp_filter:
            str_cols = df_table.select_dtypes(include="object").columns.tolist()
            for col in str_cols[:4]:
                uniq = df_table[col].dropna().unique().tolist()
                if 2 <= len(uniq) <= 20:
                    sel = st.multiselect(f"Filter {col}", uniq, default=uniq, key=f"filter_{col}")
                    df_table = df_table[df_table[col].isin(sel)]

        st.dataframe(df_table, use_container_width=True, height=400)

        # Column stats
        if show_raw:
            st.markdown("**Column Statistics**")
            num_df = df_table.select_dtypes(include="number")
            if len(num_df.columns) > 0:
                st.dataframe(num_df.describe().T.round(3), use_container_width=True)

        # Download
        csv = df_table.to_csv(index=False).encode()
        st.download_button(
            f"⬇️ Download {sel_table} as CSV",
            data=csv,
            file_name=f"{sel_table.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: Data Quality
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### ✅ Data Quality Validation Dashboard")

    if not os.path.exists(DB_PATH):
        st.warning("⚠️ No database found. Run the full pipeline to see validation results.")
    else:
        validator = DataValidator()
        datasets  = {
            "census":         DataLoader.query_database(DB_PATH, "SELECT * FROM districts"),
            "environmental":  DataLoader.query_database(DB_PATH, "SELECT * FROM environmental_data"),
            "land_use":       DataLoader.query_database(DB_PATH, "SELECT * FROM land_use"),
            "infrastructure": DataLoader.query_database(DB_PATH, "SELECT * FROM infrastructure"),
        }

        reports = {}
        for ds_name, df_ds in datasets.items():
            if len(df_ds) > 0 and "error" not in df_ds.columns:
                # Rename columns to expected names for validator
                col_renames = {"name": "district"}
                df_ds = df_ds.rename(columns=col_renames)
                # Add lat/lon if centroid exists
                if "centroid_lat" in df_ds.columns:
                    df_ds["latitude"]  = df_ds["centroid_lat"]
                    df_ds["longitude"] = df_ds["centroid_lon"]
                reports[ds_name] = validator.run_full_validation(df_ds, ds_name)

        if not reports:
            st.info("Run the pipeline first to populate validation data.")
        else:
            # Quality score gauge
            overall_score = (sum(r.quality_score for r in reports.values())
                             / len(reports))
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall_score,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Overall Quality Score", "font": {"color": "#f59e0b", "size": 16}},
                number={"font": {"color": "#f59e0b", "size": 40}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#94a3b8",
                             "tickfont": {"color": "#94a3b8"}},
                    "bar":  {"color": "#f59e0b"},
                    "bgcolor": "#0f1629",
                    "bordercolor": "rgba(245,158,11,0.3)",
                    "steps": [
                        {"range": [0,  50], "color": "rgba(239,68,68,0.15)"},
                        {"range": [50, 75], "color": "rgba(245,158,11,0.15)"},
                        {"range": [75, 100],"color": "rgba(34,197,94,0.15)"},
                    ],
                    "threshold": {
                        "line":  {"color": "#22c55e", "width": 3},
                        "thickness": 0.8,
                        "value": 80,
                    },
                },
            ))
            gauge_fig.update_layout(
                paper_bgcolor="#0f1629",
                font=dict(color="#94a3b8"),
                height=280,
                margin=dict(t=40, b=20),
            )

            g_col, checks_col = st.columns([1, 2])
            with g_col:
                st.plotly_chart(gauge_fig, use_container_width=True)
            with checks_col:
                # Summary by dataset
                status_map = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
                summary_rows = []
                for ds, rpt in reports.items():
                    summary_rows.append({
                        "Dataset":    ds.replace("_", " ").title(),
                        "Records":    rpt.total_records,
                        "Score":      f"{rpt.quality_score:.0f}/100",
                        "PASS":       rpt.passed,
                        "WARN":       rpt.warned,
                        "FAIL":       rpt.failed,
                        "Overall":    status_map.get(rpt.overall_status, "❓"),
                    })
                st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

            # Detailed check breakdown
            st.markdown("#### 🔍 Detailed Validation Checks")
            for ds_name, rpt in reports.items():
                with st.expander(
                    f"{status_map.get(rpt.overall_status,'❓')} "
                    f"**{ds_name.replace('_',' ').title()}** — "
                    f"Score: {rpt.quality_score:.0f}/100",
                    expanded=(rpt.overall_status != "PASS"),
                ):
                    for chk in rpt.checks:
                        icon   = status_map.get(chk.status, "❓")
                        color  = {"PASS": "#22c55e", "WARN": "#f59e0b",
                                  "FAIL": "#ef4444"}.get(chk.status, "#94a3b8")
                        st.markdown(
                            f"<div style='padding:0.4rem 0.8rem; margin:0.3rem 0; "
                            f"border-left:3px solid {color}; border-radius:4px; "
                            f"background:rgba(0,0,0,0.2);'>"
                            f"{icon} <b>{chk.name}</b>: {chk.details}</div>",
                            unsafe_allow_html=True,
                        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: SQL Explorer
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### 🔍 SQL Explorer — Ad-hoc Database Queries")

    st.markdown("""
    <div class='glass-card'>
      <b style='color:#f59e0b'>Available Tables:</b>
      <code>districts</code> &nbsp;|&nbsp;
      <code>environmental_data</code> &nbsp;|&nbsp;
      <code>land_use</code> &nbsp;|&nbsp;
      <code>infrastructure</code> &nbsp;|&nbsp;
      <code>pipeline_runs</code>
    </div>
    """, unsafe_allow_html=True)

    # Preset queries
    preset_queries = {
        "Top 10 most populous districts":
            "SELECT name, province, population, pop_density_class\nFROM districts\nORDER BY population DESC\nLIMIT 10",
        "Average AQI by city":
            "SELECT city, ROUND(AVG(aqi),1) AS avg_aqi, ROUND(AVG(pm25),2) AS avg_pm25\nFROM environmental_data\nGROUP BY city\nORDER BY avg_aqi DESC",
        "Land use by province":
            "SELECT province,\n  ROUND(AVG(agricultural_pct),1) AS avg_agri,\n  ROUND(AVG(urban_pct),1) AS avg_urban,\n  ROUND(AVG(forest_pct),1) AS avg_forest\nFROM land_use\nGROUP BY province",
        "Districts with best infrastructure":
            "SELECT district, province, hospitals, schools_total,\n  ROUND(electricity_access_pct,1) AS electricity_pct\nFROM infrastructure\nORDER BY electricity_access_pct DESC\nLIMIT 10",
        "Pipeline run statistics":
            "SELECT run_id, started_at, status, records_loaded,\n  duration_seconds, quality_score\nFROM pipeline_runs\nORDER BY started_at DESC",
        "Districts with high quality score":
            "SELECT name, province, quality_flag, quality_notes\nFROM districts\nWHERE quality_flag = 'PASS'\nORDER BY pop_density DESC\nLIMIT 15",
        "AQI seasonal trends (Lahore)":
            "SELECT month, season, ROUND(AVG(aqi),1) AS avg_aqi,\n  ROUND(AVG(pm25),2) AS avg_pm25\nFROM environmental_data\nWHERE city = 'Lahore'\nGROUP BY month, season\nORDER BY month",
    }

    preset_sel = st.selectbox("📋 Preset Queries", ["(custom)"] + list(preset_queries.keys()))
    default_sql = preset_queries.get(preset_sel, "SELECT * FROM districts LIMIT 10")

    sql_query = st.text_area("SQL Query", value=default_sql, height=140,
                              key="sql_input")

    run_sql = st.button("▶️ Execute Query", key="run_sql")

    if run_sql:
        if not os.path.exists(DB_PATH):
            st.error("Database not found — run the pipeline first.")
        else:
            with st.spinner("Executing…"):
                result_df = DataLoader.query_database(DB_PATH, sql_query)
            if "error" in result_df.columns:
                st.error(f"SQL Error: {result_df['error'].iloc[0]}")
            else:
                st.success(f"✅ Returned {len(result_df):,} rows × {len(result_df.columns)} columns")
                st.dataframe(result_df, use_container_width=True, height=350)
                csv_sql = result_df.to_csv(index=False).encode()
                st.download_button(
                    "⬇️ Download result as CSV",
                    data=csv_sql,
                    file_name="query_result.csv",
                    mime="text/csv",
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: Analytics
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("#### 📈 Geospatial Analytics")

    # ── Load data ──
    env_df    = DataLoader.query_database(DB_PATH, "SELECT * FROM environmental_data") \
                if os.path.exists(DB_PATH) else pd.DataFrame()
    dist_df   = DataLoader.query_database(DB_PATH, "SELECT * FROM districts") \
                if os.path.exists(DB_PATH) else pd.DataFrame()
    lu_df     = DataLoader.query_database(DB_PATH, "SELECT * FROM land_use") \
                if os.path.exists(DB_PATH) else pd.DataFrame()
    infra_df  = DataLoader.query_database(DB_PATH, "SELECT * FROM infrastructure") \
                if os.path.exists(DB_PATH) else pd.DataFrame()

    # Fall back to synthetic if DB empty
    if len(env_df) == 0 or "error" in (env_df.columns if len(env_df) > 0 else []):
        ext = DataExtractor(random_seed=42)
        raw_env = ext.extract_environmental_data()
        trans   = DataTransformer()
        env_df  = trans.normalize_aqi_data(raw_env)
        dist_df = ext.extract_census_data()
        lu_df   = ext.extract_landuse_data()
        infra_df = ext.extract_infrastructure_data()
        st.info("💡 Showing live synthetic data preview — run pipeline to use DB data.")

    row1_c1, row1_c2 = st.columns(2)

    # AQI trend by city
    with row1_c1:
        st.markdown("**🌫️ Monthly AQI Trends by City**")
        if len(env_df) > 0 and "aqi" in env_df.columns:
            city_col = st.multiselect(
                "Select cities", env_df["city"].unique().tolist(),
                default=["Lahore", "Karachi", "Islamabad"]
                if "Lahore" in env_df["city"].values else
                env_df["city"].unique()[:3].tolist(),
                key="aqi_cities",
            )
            aqi_plot = env_df[env_df["city"].isin(city_col)].copy()
            if len(aqi_plot) > 0:
                fig_aqi = px.line(
                    aqi_plot.sort_values("month"),
                    x="month", y="aqi", color="city",
                    markers=True,
                    color_discrete_sequence=[
                        "#f59e0b","#3b82f6","#22c55e","#ef4444",
                        "#a855f7","#06b6d4","#f97316","#ec4899",
                        "#14b8a6","#8b5cf6",
                    ],
                )
                fig_aqi.add_hline(y=100, line_dash="dot",
                                  line_color="rgba(239,68,68,0.5)",
                                  annotation_text="Unhealthy threshold")
                fig_aqi.add_hline(y=50,  line_dash="dot",
                                  line_color="rgba(34,197,94,0.5)",
                                  annotation_text="Moderate threshold")
                fig_aqi = _dark_layout(fig_aqi, "Monthly AQI Trends")
                fig_aqi.update_xaxes(title="Month",
                                     tickvals=list(range(1, 13)),
                                     ticktext=["Jan","Feb","Mar","Apr","May","Jun",
                                               "Jul","Aug","Sep","Oct","Nov","Dec"])
                fig_aqi.update_yaxes(title="AQI")
                st.plotly_chart(fig_aqi, use_container_width=True)

    # Population density distribution
    with row1_c2:
        st.markdown("**👥 Population Distribution by District**")
        if len(dist_df) > 0 and "population" in dist_df.columns:
            name_col2 = "name" if "name" in dist_df.columns else "district"
            top20 = dist_df.nlargest(20, "population").copy()
            prov_col = "province" if "province" in top20.columns else None
            fig_pop = px.bar(
                top20.sort_values("population"),
                y=name_col2, x="population",
                color=prov_col if prov_col else "population",
                color_discrete_map=PROVINCE_COLORS if prov_col else None,
                orientation="h",
                text=top20.sort_values("population")["population"].apply(
                    lambda x: f"{x/1e6:.1f}M"),
            )
            fig_pop.update_traces(textposition="outside", textfont_color="#f1f5f9",
                                  textfont_size=9)
            fig_pop = _dark_layout(fig_pop, "Top 20 Districts by Population")
            fig_pop.update_layout(height=400, showlegend=True)
            fig_pop.update_xaxes(title="Population")
            fig_pop.update_yaxes(title=None)
            st.plotly_chart(fig_pop, use_container_width=True)

    # Land use
    row2_c1, row2_c2 = st.columns(2)

    with row2_c1:
        st.markdown("**🌾 Land Use Composition**")
        if len(lu_df) > 0:
            prov_lu = lu_df.groupby("province")[
                ["agricultural_pct", "urban_pct", "forest_pct",
                 "water_pct", "barren_pct"]
            ].mean().reset_index()

            sel_prov_lu = st.selectbox(
                "Province", prov_lu["province"].tolist(), key="lu_prov")
            row = prov_lu[prov_lu["province"] == sel_prov_lu].iloc[0]

            lu_labels  = ["Agricultural", "Urban", "Forest", "Water", "Barren"]
            lu_values  = [row["agricultural_pct"], row["urban_pct"],
                          row["forest_pct"],       row["water_pct"],
                          row["barren_pct"]]
            lu_colors  = ["#22c55e", "#f59e0b", "#10b981", "#3b82f6", "#94a3b8"]

            fig_pie = go.Figure(go.Pie(
                labels=lu_labels, values=lu_values,
                marker=dict(colors=lu_colors,
                            line=dict(color="#0a0e1a", width=2)),
                hole=0.4,
                textinfo="label+percent",
                textfont=dict(color="#f1f5f9", size=11),
                hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
            ))
            fig_pie.update_layout(
                paper_bgcolor="#0f1629",
                margin=dict(t=10, b=10),
                legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(
                    text=f"<b>{sel_prov_lu}</b>",
                    x=0.5, y=0.5, font_size=13,
                    font_color="#f59e0b", showarrow=False,
                )],
                height=350,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with row2_c2:
        st.markdown("**🏥 Infrastructure Index by Province**")
        if len(infra_df) > 0:
            prov_infra = infra_df.groupby("province").agg(
                hospitals=("hospitals", "sum"),
                schools=("schools_total", "sum"),
                electricity=("electricity_access_pct", "mean"),
                internet=("internet_access_pct", "mean"),
            ).reset_index().sort_values("electricity", ascending=False)

            fig_infra = px.scatter(
                prov_infra,
                x="electricity", y="internet",
                size="hospitals",
                color="province",
                text="province",
                color_discrete_map=PROVINCE_COLORS,
                size_max=40,
            )
            fig_infra.update_traces(
                textposition="top center",
                textfont=dict(color="#f1f5f9", size=10),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Electricity: %{x:.1f}%<br>"
                    "Internet: %{y:.1f}%<br>"
                    "Hospitals: %{marker.size}"
                ),
            )
            fig_infra = _dark_layout(fig_infra, "Infrastructure: Electricity vs Internet Access")
            fig_infra.update_xaxes(title="Electricity Access (%)")
            fig_infra.update_yaxes(title="Internet Access (%)")
            fig_infra.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_infra, use_container_width=True)

    # AQI heatmap
    st.markdown("**🔥 AQI Heatmap — City × Month**")
    if len(env_df) > 0 and "aqi" in env_df.columns:
        pivot = env_df.pivot_table(
            index="city", columns="month", values="aqi", aggfunc="mean"
        )
        if len(pivot) > 0:
            pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun",
                             "Jul","Aug","Sep","Oct","Nov","Dec"]
            fig_heat = px.imshow(
                pivot,
                color_continuous_scale=[
                    [0,    "#0f1629"],
                    [0.15, "#22c55e"],
                    [0.35, "#eab308"],
                    [0.55, "#f97316"],
                    [0.75, "#ef4444"],
                    [1.0,  "#7f1d1d"],
                ],
                aspect="auto",
                text_auto=".0f",
            )
            fig_heat.update_traces(
                textfont=dict(size=9, color="#f1f5f9"),
                hovertemplate="<b>%{y}</b> — %{x}<br>AQI: %{z:.0f}<extra></extra>",
            )
            fig_heat = _dark_layout(fig_heat, "Monthly Average AQI by City (2023)")
            fig_heat.update_layout(
                height=350,
                coloraxis_colorbar=dict(
                    title=dict(text="AQI", font=dict(color="#f59e0b")),
                    tickfont=dict(color="#94a3b8"),
                ),
            )
            fig_heat.update_xaxes(title=None)
            fig_heat.update_yaxes(title=None)
            st.plotly_chart(fig_heat, use_container_width=True)
