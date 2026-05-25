"""
app.py
======
Pakistan Climate Observatory — Streamlit Dashboard

Interactive 50-year climate data analysis and visualization tool
for 6 major Pakistani cities (1974–2024).

Run with:
    streamlit run app.py

Author: Haris Hussain — GIS Analyst & Space Science Researcher
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

from src.data_generator import generate_climate_dataset
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

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="🌡️ Pakistan Climate Observatory",
    page_icon="🌡️",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — Dark Glassmorphism Theme
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ── Global Background ─────────────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a1628 100%);
    background-attachment: fixed;
}

/* ── Hide default Streamlit chrome ─────────────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Glass card ─────────────────────────────────────────────────────────── */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 16px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 1.5rem;
    margin: 0.5rem 0;
}

/* ── Metric card ─────────────────────────────────────────────────────────── */
.metric-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.10), rgba(0,212,255,0.02));
    border: 1px solid rgba(0, 212, 255, 0.30);
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #00d4ff;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-delta {
    font-size: 0.9rem;
    color: #06d6a0;
    margin-top: 0.2rem;
}
.metric-delta-neg {
    font-size: 0.9rem;
    color: #ff6b6b;
    margin-top: 0.2rem;
}

/* ── Warning metric card ──────────────────────────────────────────────── */
.metric-card-warn {
    background: linear-gradient(135deg, rgba(255,107,107,0.10), rgba(255,107,107,0.02));
    border: 1px solid rgba(255, 107, 107, 0.35);
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.metric-card-warn .metric-value {
    color: #ff6b6b;
}

/* ── Sidebar styling ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(10, 10, 20, 0.85);
    border-right: 1px solid rgba(0, 212, 255, 0.15);
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #00d4ff;
}

/* ── Tab styling ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.65);
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(0, 212, 255, 0.15) !important;
    color: #00d4ff !important;
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
}

/* ── Section header ─────────────────────────────────────────────────────── */
.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #00d4ff;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    margin-bottom: 1rem;
}

/* ── Plotly container rounding ──────────────────────────────────────────── */
.element-container iframe,
[data-testid="stPlotlyChart"] {
    border-radius: 12px;
}

/* ── DataFrame style ─────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

/* ── Download button ─────────────────────────────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,212,255,0.05));
    border: 1px solid rgba(0,212,255,0.4);
    color: #00d4ff;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stDownloadButton > button:hover {
    background: rgba(0,212,255,0.25);
    box-shadow: 0 4px 20px rgba(0,212,255,0.25);
    transform: translateY(-1px);
}

/* ── Header banner ───────────────────────────────────────────────────────── */
.banner {
    background: linear-gradient(90deg, rgba(0,212,255,0.15) 0%, rgba(0,100,200,0.08) 50%, rgba(0,212,255,0.05) 100%);
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.banner h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #0077b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.banner p {
    color: rgba(255,255,255,0.65);
    margin: 0.4rem 0 0;
    font-size: 0.95rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="🌍 Generating 50 years of climate data…")
def load_data():
    """Load and pre-process all climate data and derived datasets."""
    df = generate_climate_dataset(seed=42)
    annual_df = compute_annual_trends(df)
    seasonal_df = compute_seasonal_stats(df)
    anomaly_df = detect_anomalies(df, threshold=1.5)
    drought_df = compute_drought_index(df)
    trend_stats = get_trend_statistics(df)
    return df, annual_df, seasonal_df, anomaly_df, drought_df, trend_stats


df, annual_df, seasonal_df, anomaly_df, drought_df, trend_stats = load_data()

ALL_CITIES = sorted(df["city"].unique().tolist())
ALL_YEARS = sorted(df["year"].unique().tolist())

# ---------------------------------------------------------------------------
# Sidebar — Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🌡️ Pakistan Climate Observatory")
    st.markdown("---")

    st.markdown("### 🏙️ City Selection")
    selected_cities = st.multiselect(
        "Select Cities",
        options=ALL_CITIES,
        default=ALL_CITIES,
        help="Choose one or more cities to analyse",
    )
    if not selected_cities:
        selected_cities = ALL_CITIES

    primary_city = st.selectbox(
        "Primary City (for single-city charts)",
        options=selected_cities,
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📅 Time Range")
    year_range = st.slider(
        "Year Range",
        min_value=1974,
        max_value=2024,
        value=(1974, 2024),
        step=1,
    )

    st.markdown("---")
    st.markdown("### 🌿 Season Filter")
    season_filter = st.multiselect(
        "Seasons",
        options=["Winter", "Spring", "Summer", "Monsoon"],
        default=["Winter", "Spring", "Summer", "Monsoon"],
    )
    if not season_filter:
        season_filter = ["Winter", "Spring", "Summer", "Monsoon"]

    st.markdown("---")
    st.markdown("### 📊 Variable")
    variable = st.radio(
        "Show Variable",
        options=["Temperature", "Precipitation", "Both"],
        index=2,
    )

    st.markdown("---")
    st.markdown("### ⚙️ Analysis Settings")
    anomaly_threshold = st.slider(
        "Anomaly Threshold (σ)",
        min_value=1.0,
        max_value=3.0,
        value=1.5,
        step=0.1,
        help="Standard deviations from baseline to flag as anomaly",
    )

    projection_year = st.slider(
        "Projection Year",
        min_value=2025,
        max_value=2050,
        value=2035,
        step=1,
    )

    st.markdown("---")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.4);font-size:0.78rem;'>"
        "📡 NOAA-Inspired Synthetic Dataset<br>"
        "🎓 Haris Hussain — Space Science, UoP<br>"
        "🗓️ Data period: 1974–2024"
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Filter dataframes by sidebar selections
# ---------------------------------------------------------------------------
year_mask = (df["year"] >= year_range[0]) & (df["year"] <= year_range[1])
city_mask = df["city"].isin(selected_cities)
filtered_df = df[year_mask & city_mask].copy()

year_mask_ann = (annual_df["year"] >= year_range[0]) & (annual_df["year"] <= year_range[1])
filtered_annual = annual_df[year_mask_ann & annual_df["city"].isin(selected_cities)].copy()

# Re-compute anomalies with sidebar threshold
@st.cache_data(show_spinner=False)
def get_anomaly_df(threshold: float):
    return detect_anomalies(df, threshold=threshold)

anomaly_df_filtered = get_anomaly_df(anomaly_threshold)
anom_filtered = anomaly_df_filtered[
    (anomaly_df_filtered["year"] >= year_range[0])
    & (anomaly_df_filtered["year"] <= year_range[1])
    & anomaly_df_filtered["city"].isin(selected_cities)
]

filtered_seasonal = seasonal_df[seasonal_df["city"].isin(selected_cities)].copy()
filtered_drought = drought_df[
    (drought_df["year"] >= year_range[0])
    & (drought_df["year"] <= year_range[1])
    & drought_df["city"].isin(selected_cities)
].copy()


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="banner">
        <h1>🌡️ Pakistan Climate Observatory</h1>
        <p>
            Interactive analysis of 50 years of climate data across 6 major Pakistani cities.
            Explore temperature trends, precipitation patterns, drought indices, and climate change signals
            from 1974 to 2024.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper: render metric card HTML
# ---------------------------------------------------------------------------
def metric_card(icon: str, label: str, value: str, delta: str = "", warn: bool = False) -> str:
    card_class = "metric-card-warn" if warn else "metric-card"
    delta_class = "metric-delta-neg" if warn else "metric-delta"
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="{card_class}">
        <div style="font-size:1.6rem">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """


# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "📊 Overview",
    "🌡️ Temperature Analysis",
    "🌧️ Precipitation & Drought",
    "📈 Trends & Projections",
    "🏙️ City Comparison",
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[0]:
    # ── Metric cards ────────────────────────────────────────────────────────
    avg_temp = filtered_df["temperature_mean"].mean()
    total_precip = filtered_df["precipitation_mm"].sum()
    warming_rate = trend_stats[trend_stats["city"] == primary_city]["slope_per_decade"].values[0] if primary_city in trend_stats["city"].values else 0.0
    anomaly_count = int(anom_filtered["is_temp_anomaly"].sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            metric_card("🌡️", f"Avg Temperature ({primary_city})", f"{avg_temp:.1f}°C", f"↑ {warming_rate:+.2f}°C/decade"),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            metric_card("🌧️", "Total Precipitation (selected)", f"{total_precip/1000:.1f}k mm"),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            metric_card("📈", f"Warming Rate ({primary_city})", f"{warming_rate:+.3f}°C/dec", warn=warming_rate > 0),
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            metric_card("⚠️", "Temp Anomalies Detected", f"{anomaly_count:,}", f"threshold: {anomaly_threshold}σ", warn=True),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Multi-city temperature chart ────────────────────────────────────────
    st.markdown('<div class="section-header">Annual Mean Temperature — All Selected Cities</div>', unsafe_allow_html=True)
    if variable in ("Temperature", "Both"):
        fig_temp = plot_multi_city_comparison(filtered_annual, "temp_avg")
        st.plotly_chart(fig_temp, use_container_width=True)

    # ── Multi-city precipitation chart ─────────────────────────────────────
    if variable in ("Precipitation", "Both"):
        st.markdown('<div class="section-header">Annual Total Precipitation — All Selected Cities</div>', unsafe_allow_html=True)
        fig_precip = plot_multi_city_comparison(filtered_annual, "precip_total")
        st.plotly_chart(fig_precip, use_container_width=True)

    # ── Quick summary table ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 City Summary Statistics</div>', unsafe_allow_html=True)
    summary = (
        filtered_df.groupby("city")
        .agg(
            avg_temp=("temperature_mean", "mean"),
            max_temp=("temperature_max", "max"),
            min_temp=("temperature_min", "min"),
            avg_precip_monthly=("precipitation_mm", "mean"),
            avg_humidity=("humidity_pct", "mean"),
        )
        .round(2)
        .reset_index()
        .rename(columns={
            "city": "City",
            "avg_temp": "Avg Temp (°C)",
            "max_temp": "Record High (°C)",
            "min_temp": "Record Low (°C)",
            "avg_precip_monthly": "Avg Monthly Precip (mm)",
            "avg_humidity": "Avg Humidity (%)",
        })
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — TEMPERATURE ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[1]:
    st.markdown(f'<div class="section-header">🌈 Climate Warming Stripes — {primary_city}</div>', unsafe_allow_html=True)
    stripes_data = compute_climate_stripes_data(df[df["city"] == primary_city], primary_city)
    fig_stripes = plot_climate_stripes(stripes_data, primary_city)
    st.plotly_chart(fig_stripes, use_container_width=True)

    st.markdown(
        "<div style='color:rgba(255,255,255,0.5);font-size:0.82rem;padding:0.5rem 0 1rem;'>"
        "Each stripe represents one year. Blue = cooler than 1974–2004 baseline; "
        "Red = warmer than baseline. Inspired by Ed Hawkins' #ShowYourStripes."
        "</div>",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.markdown(f'<div class="section-header">📉 Temperature Trend with Rolling Average — {primary_city}</div>', unsafe_allow_html=True)
        fig_trend = plot_temperature_trend(
            filtered_df[filtered_df["city"] == primary_city], primary_city
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.markdown(f'<div class="section-header">⚠️ Anomaly Timeline — {primary_city}</div>', unsafe_allow_html=True)
        fig_anom = plot_anomaly_timeline(
            anom_filtered[anom_filtered["city"] == primary_city], primary_city
        )
        st.plotly_chart(fig_anom, use_container_width=True)

    # ── Anomaly stats ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Anomaly Statistics by City</div>', unsafe_allow_html=True)
    anom_stats = (
        anom_filtered.groupby("city")
        .agg(
            total_months=("temperature_mean", "count"),
            temp_anomalies=("is_temp_anomaly", "sum"),
            precip_anomalies=("is_precip_anomaly", "sum"),
            warm_anomalies=("temp_anomaly_magnitude", lambda x: (x > anomaly_threshold).sum()),
            cold_anomalies=("temp_anomaly_magnitude", lambda x: (x < -anomaly_threshold).sum()),
        )
        .reset_index()
    )
    anom_stats["anomaly_pct"] = (anom_stats["temp_anomalies"] / anom_stats["total_months"] * 100).round(1)
    anom_stats.columns = ["City", "Total Months", "Temp Anomalies", "Precip Anomalies",
                          "Warm Events", "Cold Events", "Anomaly %"]
    st.dataframe(anom_stats, use_container_width=True, hide_index=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — PRECIPITATION & DROUGHT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[2]:
    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        st.markdown(f'<div class="section-header">🗓️ Precipitation Heatmap — {primary_city}</div>', unsafe_allow_html=True)
        fig_heatmap = plot_precipitation_heatmap(
            filtered_df[filtered_df["city"] == primary_city], primary_city
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with col_p2:
        st.markdown(f'<div class="section-header">💧 SPI Drought Index — {primary_city}</div>', unsafe_allow_html=True)
        fig_drought = plot_drought_index(
            filtered_drought[filtered_drought["city"] == primary_city], primary_city
        )
        st.plotly_chart(fig_drought, use_container_width=True)

    st.markdown(f'<div class="section-header">📅 Seasonal Comparison by Decade — {primary_city}</div>', unsafe_allow_html=True)
    seasonal_filtered = filtered_seasonal[
        filtered_seasonal["season"].isin(season_filter)
    ]
    fig_seasonal = plot_seasonal_comparison(seasonal_filtered, primary_city)
    st.plotly_chart(fig_seasonal, use_container_width=True)

    # ── Drought category breakdown ──────────────────────────────────────────
    st.markdown('<div class="section-header">🏜️ Drought Category Breakdown (All Selected Cities)</div>', unsafe_allow_html=True)
    drought_cats = (
        filtered_drought.groupby(["city", "drought_category"])
        .size()
        .reset_index(name="month_count")
    )
    drought_pivot = drought_cats.pivot_table(
        index="city", columns="drought_category", values="month_count", fill_value=0
    ).reset_index()
    st.dataframe(drought_pivot, use_container_width=True, hide_index=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — TRENDS & PROJECTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[3]:
    col_t1, col_t2 = st.columns([3, 2])

    with col_t1:
        st.markdown(f'<div class="section-header">📈 Temperature Projection to {projection_year} — {primary_city}</div>', unsafe_allow_html=True)
        fig_proj = plot_temperature_projection(filtered_annual, primary_city, target_year=projection_year)
        st.plotly_chart(fig_proj, use_container_width=True)

    with col_t2:
        st.markdown('<div class="section-header">🔬 Trend Statistics by City</div>', unsafe_allow_html=True)
        ts_display = trend_stats[trend_stats["city"].isin(selected_cities)].copy()
        ts_display["significant"] = ts_display["significant"].map({True: "✅ Yes", False: "❌ No"})
        ts_display.columns = ["City", "Slope/yr (°C)", "Slope/decade (°C)", "R²", "p-value", "Significant"]
        st.dataframe(ts_display, use_container_width=True, hide_index=True)

    # ── Decadal comparison table ────────────────────────────────────────────
    st.markdown('<div class="section-header">📆 Decadal Temperature Averages — All Cities</div>', unsafe_allow_html=True)

    filtered_df_copy = filtered_df.copy()
    filtered_df_copy["decade"] = (filtered_df_copy["year"] // 10 * 10).astype(str) + "s"
    decadal = (
        filtered_df_copy.groupby(["city", "decade"])["temperature_mean"]
        .mean()
        .round(2)
        .reset_index()
    )
    decadal_pivot = decadal.pivot_table(
        index="city", columns="decade", values="temperature_mean"
    ).reset_index()
    decadal_pivot.columns.name = None
    st.dataframe(decadal_pivot, use_container_width=True, hide_index=True)

    # ── Projection table ─────────────────────────────────────────────────────
    st.markdown(f'<div class="section-header">🔮 Temperature Projections to {projection_year}</div>', unsafe_allow_html=True)
    proj_df = project_temperatures(
        annual_df[annual_df["city"].isin(selected_cities)], target_year=projection_year
    )
    proj_df.columns = [
        "City",
        f"Projected Temp {projection_year} (°C)",
        "Current Temp 2024 (°C)",
        f"Δ vs 2024 (°C)",
    ]
    st.dataframe(proj_df, use_container_width=True, hide_index=True)

    # ── Multi-city humidity and wind ────────────────────────────────────────
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown('<div class="section-header">💧 Annual Humidity Trends</div>', unsafe_allow_html=True)
        fig_hum = plot_multi_city_comparison(filtered_annual, "humidity_avg")
        st.plotly_chart(fig_hum, use_container_width=True)
    with col_h2:
        st.markdown('<div class="section-header">🌬️ Annual Wind Speed Trends</div>', unsafe_allow_html=True)
        fig_wind = plot_multi_city_comparison(filtered_annual, "wind_avg")
        st.plotly_chart(fig_wind, use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5 — CITY COMPARISON
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tabs[4]:
    st.markdown('<div class="section-header">🏙️ Side-by-Side City Climate Profiles</div>', unsafe_allow_html=True)

    # City selector for detailed comparison
    compare_cities = st.multiselect(
        "Select cities to compare (max 3 recommended for clarity)",
        options=selected_cities,
        default=selected_cities[:3] if len(selected_cities) >= 3 else selected_cities,
        key="compare_cities_selector",
    )

    if len(compare_cities) < 2:
        st.info("ℹ️ Please select at least 2 cities to compare.")
    else:
        # Monthly temperature profiles (box plots per city)
        st.markdown('<div class="section-header">📦 Monthly Temperature Distribution</div>', unsafe_allow_html=True)

        from plotly.subplots import make_subplots
        from src.visualizations import CITY_COLORS, TEMPLATE, PAPER_BG, PLOT_BG, FONT_FAMILY

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        fig_box = go.Figure()
        for city in compare_cities:
            city_data = filtered_df[filtered_df["city"] == city]
            fig_box.add_trace(
                go.Box(
                    x=city_data["month"].map(lambda m: month_names[m - 1]),
                    y=city_data["temperature_mean"],
                    name=city,
                    marker_color=CITY_COLORS.get(city, "#00d4ff"),
                    boxmean=True,
                    hovertemplate=f"<b>{city}</b><br>Month: %{{x}}<br>Temp: %{{y:.1f}}°C<extra></extra>",
                )
            )
        fig_box.update_layout(
            template=TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(family=FONT_FAMILY, color="#e0e0e0"),
            title=dict(text="Monthly Temperature Distribution by City", font=dict(size=16, color="#ffffff")),
            boxmode="group",
            xaxis=dict(title="Month", gridcolor="rgba(255,255,255,0.06)", categoryorder="array",
                       categoryarray=month_names),
            yaxis=dict(title="Temperature (°C)", gridcolor="rgba(255,255,255,0.06)"),
            legend=dict(bgcolor="rgba(255,255,255,0.04)", bordercolor="rgba(255,255,255,0.15)", borderwidth=1),
            margin=dict(l=60, r=30, t=60, b=50),
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # Annual precipitation comparison
        st.markdown('<div class="section-header">🌧️ Annual Precipitation Comparison</div>', unsafe_allow_html=True)
        fig_bar_precip = go.Figure()
        for city in compare_cities:
            c_data = filtered_annual[filtered_annual["city"] == city].sort_values("year")
            fig_bar_precip.add_trace(
                go.Scatter(
                    x=c_data["year"],
                    y=c_data["precip_total"],
                    mode="lines",
                    name=city,
                    line=dict(color=CITY_COLORS.get(city, "#00d4ff"), width=2),
                    fill="tozeroy",
                    fillcolor=f"rgba{(*px.colors.hex_to_rgb(CITY_COLORS.get(city, '#00d4ff')), 0.07)}",
                    hovertemplate=f"<b>{city}</b><br>Year: %{{x}}<br>Precip: %{{y:.1f}} mm<extra></extra>",
                )
            )
        fig_bar_precip.update_layout(
            template=TEMPLATE,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(family=FONT_FAMILY, color="#e0e0e0"),
            title=dict(text="Annual Total Precipitation", font=dict(size=16, color="#ffffff")),
            xaxis=dict(title="Year", gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title="Precipitation (mm/year)", gridcolor="rgba(255,255,255,0.06)"),
            legend=dict(bgcolor="rgba(255,255,255,0.04)", bordercolor="rgba(255,255,255,0.15)", borderwidth=1),
            margin=dict(l=60, r=30, t=60, b=50),
        )
        st.plotly_chart(fig_bar_precip, use_container_width=True)

        # Radar chart for climate profile comparison
        st.markdown('<div class="section-header">🕸️ Normalized Climate Profile Radar</div>', unsafe_allow_html=True)

        radar_metrics = ["temp_avg", "precip_total", "humidity_avg", "wind_avg", "temp_max_avg"]
        radar_labels = ["Avg Temp", "Annual Precip", "Humidity", "Wind Speed", "Max Temp"]

        radar_data = (
            filtered_annual[filtered_annual["city"].isin(compare_cities)]
            .groupby("city")[radar_metrics]
            .mean()
            .reset_index()
        )

        # Normalize 0-1 per metric
        for col in radar_metrics:
            col_min = radar_data[col].min()
            col_max = radar_data[col].max()
            if col_max > col_min:
                radar_data[col] = (radar_data[col] - col_min) / (col_max - col_min)
            else:
                radar_data[col] = 0.5

        fig_radar = go.Figure()
        for _, row in radar_data.iterrows():
            city = row["city"]
            values = [row[m] for m in radar_metrics]
            values.append(values[0])  # close polygon
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=radar_labels + [radar_labels[0]],
                    fill="toself",
                    name=city,
                    line=dict(color=CITY_COLORS.get(city, "#00d4ff")),
                    fillcolor=f"rgba{(*px.colors.hex_to_rgb(CITY_COLORS.get(city, '#00d4ff')), 0.12)}",
                )
            )
        fig_radar.update_layout(
            template=TEMPLATE,
            paper_bgcolor=PAPER_BG,
            font=dict(family=FONT_FAMILY, color="#e0e0e0"),
            polar=dict(
                bgcolor="rgba(13,17,23,0.6)",
                radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            ),
            title=dict(text="Normalized Climate Profile (0 = lowest, 1 = highest)", font=dict(size=15, color="#ffffff")),
            showlegend=True,
            legend=dict(bgcolor="rgba(255,255,255,0.04)", bordercolor="rgba(255,255,255,0.15)", borderwidth=1),
            margin=dict(l=60, r=60, t=60, b=60),
        )
        st.plotly_chart(fig_radar, use_container_width=True)


# ---------------------------------------------------------------------------
# Bottom: Data Download
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown('<div class="section-header">⬇️ Download Climate Dataset</div>', unsafe_allow_html=True)

col_dl1, col_dl2, col_dl3 = st.columns([2, 1, 1])

with col_dl1:
    st.markdown(
        "<div style='color:rgba(255,255,255,0.6);font-size:0.9rem;'>"
        "Download the full synthetic climate dataset (50 years × 6 cities × 12 months = 3,600 rows) "
        "in CSV format for your own analysis."
        "</div>",
        unsafe_allow_html=True,
    )

with col_dl2:
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv_bytes,
        file_name="pakistan_climate_data_1974_2024.csv",
        mime="text/csv",
    )

with col_dl3:
    # Download filtered dataset
    filtered_csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=filtered_csv,
        file_name="pakistan_climate_filtered.csv",
        mime="text/csv",
    )

# Footer
st.markdown(
    """
    <div style="text-align:center;color:rgba(255,255,255,0.3);font-size:0.78rem;margin-top:2rem;padding:1rem;">
        🌍 Pakistan Climate Observatory &nbsp;|&nbsp;
        Built with Streamlit & Plotly &nbsp;|&nbsp;
        NOAA-Inspired Synthetic Dataset (1974–2024) &nbsp;|&nbsp;
        Haris Hussain · Space Science · University of Punjab, Lahore
    </div>
    """,
    unsafe_allow_html=True,
)
