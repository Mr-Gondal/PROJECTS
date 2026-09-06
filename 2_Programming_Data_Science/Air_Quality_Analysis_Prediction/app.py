import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from src.sample_data import generate_sample_data
from src.data_collector import AirQualityCollector
from src.analyzer import AirQualityAnalyzer
from src.model import AirQualityPredictor, train_all_models, MIN_TRAIN_ROWS
from src.config import CITIES, TARGET_POLLUTANTS
from src.aqi_scale import aqi_category, aqi_from_pollutant

st.set_page_config(page_title="AQI Dashboard — Pakistan", page_icon="🌍", layout="wide")

CUSTOM_CSS = """
<style>
    .stApp { background: #0e1117; }
    .stApp header { background: transparent; }

    div[data-testid="metric-container"] {
        background: #1a1d29;
        border: 1px solid #2d3142;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] > label {
        font-size: 0.85rem !important;
        color: #8b8fa3 !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] > div[data-testid="metric-value"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] {
        background: #11141f;
        border-right: 1px solid #1e2235;
    }
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        background: #2d6a4f;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 0;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #40916c;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #1a1d29;
        padding: 4px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        color: #8b8fa3;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #2d6a4f !important;
        color: white !important;
    }

    /* Section headings rendered as a single self-contained element */
    .section-title {
        background: #1a1d29;
        border: 1px solid #2d3142;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 16px;
        color: #e0e0e0;
        font-weight: 600;
        font-size: 1.15rem;
    }
    .section-subtitle {
        color: #a0a4b8;
        font-size: 0.9rem;
        margin: 8px 0 12px 0;
    }

    h1, h2, h3 { color: #f0f0f0 !important; }

    .stDataFrame { background: #1a1d29; border-radius: 10px; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    hr { border-color: #2d3142 !important; margin: 24px 0 !important; }
</style>
"""


def get_aqi_label(aqi):
    return aqi_category(aqi)


def section(title: str, subtitle: str = None):
    """Render a section heading as ONE valid, self-contained HTML block."""
    html = f'<div class="section-title">{title}</div>'
    if subtitle:
        html += f'<div class="section-subtitle">{subtitle}</div>'
    st.markdown(html, unsafe_allow_html=True)


@st.cache_data
def load_or_generate_data():
    """Load the bundled sample history, or synthesise a fresh one.

    The sample CSV is a *generated demo artifact* (not real measurements);
    if it is absent (fresh clone) a new series ending today is generated so
    the dashboard never shows stale "current" readings.
    """
    sample_path = Path(__file__).parent / "data" / "raw" / "aqi_sample.csv"
    if sample_path.exists():
        df = pd.read_csv(sample_path, parse_dates=["timestamp"])
        if len(df) >= 450:
            return df
    df = generate_sample_data(days=90)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(sample_path, index=False)
    return df


@st.cache_resource
def get_analyzer(df):
    return AirQualityAnalyzer(df)


@st.cache_resource(show_spinner="Training model…")
def get_trained_predictor(df, model_type: str, target: str):
    """Train once per (model_type, target) and cache — no retrain per click.

    Returns (predictor, metrics_dict) with metrics computed on a
    chronological hold-out split (see src/model.py for the protocol).
    """
    predictor = AirQualityPredictor(model_type=model_type)
    X, y = predictor.prepare_features(df, target=target)
    result = predictor.train(X, y)
    return predictor, result["metrics"]


def city_trend(series: pd.Series, window: int = 7) -> str:
    """Compare the mean of the last `window` points vs the previous window.

    More meaningful than comparing just the first and last points.
    """
    if len(series) < 2 * window:
        window = max(1, len(series) // 4)
    if len(series) < 2:
        return "insufficient data"
    recent = series.iloc[-window:].mean()
    previous = series.iloc[-2 * window:-window].mean()
    if pd.isna(previous) or pd.isna(recent):
        return "insufficient data"
    if recent < previous * 0.97:
        return "improving"
    elif recent > previous * 1.03:
        return "worsening"
    return "stable"


def render_overview(df):
    section("🇵🇰 Pakistan Air Quality Overview")

    # Honest "as of" line — shows the timestamp of the newest reading
    newest = pd.to_datetime(df["timestamp"]).max()
    st.caption(f"Most recent reading in loaded data: {newest.strftime('%Y-%m-%d %H:%M UTC')}")

    cols = st.columns(5)
    for col, city in zip(cols, CITIES):
        city_df = df[df["city"] == city].sort_values("timestamp")
        with col:
            if city_df.empty:
                st.metric(city, "—")
                continue
            latest = city_df.iloc[-1]
            aqi = latest.get("aqi")
            label, color = get_aqi_label(aqi)
            aqi_str = f"{aqi:.0f}" if aqi is not None and not pd.isna(aqi) else "—"
            trend = city_trend(city_df["aqi"])
            icon = {"improving": "↓", "worsening": "↑", "stable": "→"}.get(trend, "")
            st.metric(city, aqi_str, delta=f"{label} {icon}", delta_color="off")

    left, right = st.columns([1, 1])

    with left:
        section("📈 AQI Comparison — All Cities")
        import plotly.express as px

        df_plot = df.copy()
        df_plot["date"] = pd.to_datetime(df_plot["timestamp"]).dt.date
        daily_avg = df_plot.groupby(["date", "city"])["aqi"].mean().reset_index()
        fig = px.line(
            daily_avg, x="date", y="aqi", color="city",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={"aqi": "AQI (PM2.5 basis)", "date": ""},
            height=350,
        )
        fig.update_layout(
            plot_bgcolor="#1a1d29", paper_bgcolor="#1a1d29",
            font_color="#a0a4b8", margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        fig.update_xaxes(gridcolor="#2d3142")
        fig.update_yaxes(gridcolor="#2d3142")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        section("📊 Pollution Snapshot", "Latest reading per city")
        import plotly.express as px

        latest_vals = []
        for city in CITIES:
            city_df = df[df["city"] == city].sort_values("timestamp")
            if not city_df.empty:
                latest = city_df.iloc[-1]
                latest_vals.append({"city": city, **{p: latest.get(p, 0) for p in ["pm25", "pm10", "no2"]}})
        if latest_vals:
            snapshot_df = pd.DataFrame(latest_vals).melt(id_vars=["city"], var_name="pollutant", value_name="concentration")
            fig = px.bar(
                snapshot_df, x="city", y="concentration", color="pollutant", barmode="group",
                color_discrete_sequence=["#52b788", "#f9c74f", "#e63946"],
                labels={"concentration": "µg/m³", "city": ""},
                height=350,
            )
            fig.update_layout(
                plot_bgcolor="#1a1d29", paper_bgcolor="#1a1d29",
                font_color="#a0a4b8", margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            )
            fig.update_xaxes(gridcolor="#2d3142")
            fig.update_yaxes(gridcolor="#2d3142")
            st.plotly_chart(fig, use_container_width=True)

    section("📋 Quick Stats", "Distribution of pollutant concentrations in the loaded data")
    stats = get_analyzer(df).summary_stats()
    st.dataframe(stats.style.format("{:.1f}"), use_container_width=True)


def render_analytics(df):
    import plotly.express as px
    analyzer = get_analyzer(df)

    tab_corr, tab_trends, tab_composition = st.tabs(["🔗 Correlation", "📈 Trends", "📊 Composition"])

    with tab_corr:
        corr = analyzer.correlation_matrix()
        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            height=500,
        )
        fig.update_layout(
            plot_bgcolor="#1a1d29", paper_bgcolor="#1a1d29",
            font_color="#a0a4b8", margin=dict(l=20, r=20, t=20, b=20),
            title="Pollutant Correlation Matrix",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_trends:
        city_choice = st.selectbox("Select City", ["All Cities"] + CITIES)
        df_plot = df.copy()
        df_plot["date"] = pd.to_datetime(df_plot["timestamp"]).dt.date
        if city_choice != "All Cities":
            df_plot = df_plot[df_plot["city"] == city_choice]
            fig = px.line(
                df_plot, x="date", y="aqi",
                color_discrete_sequence=["#52b788"],
                labels={"aqi": "AQI (PM2.5 basis)", "date": ""},
                height=400,
            )
        else:
            daily = df_plot.groupby(["date", "city"])["aqi"].mean().reset_index()
            fig = px.line(
                daily, x="date", y="aqi", color="city",
                color_discrete_sequence=px.colors.qualitative.Bold,
                labels={"aqi": "AQI (PM2.5 basis)", "date": ""},
                height=400,
            )
        fig.update_layout(
            plot_bgcolor="#1a1d29", paper_bgcolor="#1a1d29",
            font_color="#a0a4b8", margin=dict(l=20, r=20, t=20, b=20),
            title=f"AQI Trend — {city_choice}",
        )
        fig.update_xaxes(gridcolor="#2d3142")
        fig.update_yaxes(gridcolor="#2d3142")
        st.plotly_chart(fig, use_container_width=True)

    with tab_composition:
        city_filter = st.selectbox("Filter by City", ["All"] + CITIES, key="comp_city")
        df_filtered = df if city_filter == "All" else df[df["city"] == city_filter]
        mean_vals = {p: df_filtered[p].mean() for p in TARGET_POLLUTANTS if p in df_filtered.columns}
        comp_df = pd.DataFrame(list(mean_vals.items()), columns=["Pollutant", "Mean Concentration"])

        fig = px.bar(
            comp_df, x="Pollutant", y="Mean Concentration",
            color="Pollutant", color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"Mean Concentration": "µg/m³"},
            height=400,
        )
        fig.update_layout(
            plot_bgcolor="#1a1d29", paper_bgcolor="#1a1d29",
            font_color="#a0a4b8", margin=dict(l=20, r=20, t=20, b=20),
            title=f"Average Pollutant Levels — {city_filter}",
            showlegend=False,
        )
        fig.update_xaxes(gridcolor="#2d3142")
        fig.update_yaxes(gridcolor="#2d3142")
        st.plotly_chart(fig, use_container_width=True)


def render_predict(df):
    import plotly.graph_objects as go
    import math

    section("🤖 Air Quality Predictor",
            "Adjust the parameters below to predict a pollutant concentration "
            "with a model trained on the loaded history.")

    col1, col2 = st.columns([1, 1])

    with col1:
        model_choice = st.selectbox("Select Model", ["random_forest", "gradient_boosting", "linear"])
        target = st.selectbox("Predict Target", TARGET_POLLUTANTS)

        section("🌡️ Environmental Factors")
        df_numeric = df.select_dtypes(include=[np.number])
        input_features = {}
        feature_ranges = {
            "pm25": (0, 300), "pm10": (0, 300), "no2": (0, 100), "so2": (0, 50),
            "co": (0, 10), "o3": (0, 150),
            "temperature": (0, 50), "humidity": (0, 100),
            "wind_speed": (0, 30), "pressure": (980, 1030),
        }
        other_pollutants = [p for p in TARGET_POLLUTANTS if p != target]
        for feat in other_pollutants:
            if feat in df_numeric.columns:
                lo, hi = feature_ranges.get(feat, (float(df_numeric[feat].min()), float(df_numeric[feat].max())))
                if hi <= lo:
                    hi = lo + 10
                default = float(df_numeric[feat].median())
                default = max(lo, min(hi, default))
                if pd.isna(default):
                    default = (lo + hi) / 2
                input_features[feat] = st.slider(f"{feat.upper()} (µg/m³)", lo, hi, default, 0.1)

    with col2:
        section("🌤️ Weather Conditions")
        for feat in ["temperature", "humidity", "wind_speed", "pressure"]:
            if feat in df_numeric.columns:
                lo, hi = feature_ranges.get(feat, (float(df_numeric[feat].min()), float(df_numeric[feat].max())))
                if hi <= lo:
                    hi = lo + 10
                default = float(df_numeric[feat].median())
                default = max(lo, min(hi, default))
                if pd.isna(default):
                    default = (lo + hi) / 2
                input_features[feat] = st.slider(
                    feat.replace("_", " ").title(), lo, hi, default, 0.1
                )

        hour = st.slider("Hour of Day", 0, 23, 12)
        dayofweek = st.slider("Day of Week", 0, 6, 2)
        month = st.slider("Month", 1, 12, 6)

    if len(df) < MIN_TRAIN_ROWS:
        st.warning(f"Not enough history to train ({len(df)} rows < {MIN_TRAIN_ROWS}). "
                   "Load the sample dataset or collect more API data first.")
        return

    if st.button("🔮 Predict Air Quality", type="primary", use_container_width=True):
        try:
            predictor, metrics = get_trained_predictor(df, model_choice, target)
        except ValueError as exc:
            st.error(str(exc))
            return

        input_df = pd.DataFrame([{
            **input_features,
            "hour": hour, "dayofweek": dayofweek, "month": month,
        }])
        pred = predictor.predict(input_df)[0]

        # AQI category is only valid where a µg/m³→AQI scale exists (PM2.5/PM10).
        # For NO2/SO2/CO/O3 the raw concentration is shown instead of a
        # misleading category (each has different units/averaging windows).
        aqi_equiv = aqi_from_pollutant(target, float(pred))
        if aqi_equiv is not None:
            label, color = get_aqi_label(aqi_equiv)
            headline = f"AQI ≈ {aqi_equiv}"
        else:
            label, color = "No AQI scale for this pollutant", "#8b8fa3"
            headline = ""

        metrics_line = (
            f"Model: {model_choice} · test MAE {metrics['mae']:.1f} · "
            f"RMSE {metrics['rmse']:.1f} · R² {metrics['r2']:.2f} "
            f"({metrics['n_train']} train / {metrics['n_test']} test rows, chronological split)"
        )

        st.markdown(
            f"""
            <div style="background:#1a1d29; border:2px solid {color}; border-radius:16px;
                        padding:32px; text-align:center; margin-top:16px;">
                <div style="font-size:1rem; color:#8b8fa3; text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:8px;">Predicted {target.upper()}</div>
                <div style="font-size:4rem; font-weight:800; color:{color};">{pred:.1f} µg/m³</div>
                <div style="font-size:1.2rem; color:{color}; margin-top:8px; font-weight:600;">
                    {headline + ' · ' if headline else ''}{label}</div>
                <div style="font-size:0.85rem; color:#8b8fa3; margin-top:16px;">{metrics_line}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Metrics are computed live on a chronological hold-out split — "
                   "not hard-coded. Sample data is synthetic; treat R² as a pipeline "
                   "demonstration, not real-world skill.")

        gauge_max = max(200, math.ceil(pred * 1.2 / 50) * 50)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"Predicted {target.upper()} (µg/m³)", "font": {"color": "#a0a4b8"}},
            gauge={
                "axis": {"range": [0, gauge_max], "tickcolor": "#a0a4b8"},
                "bar": {"color": color},
                "bgcolor": "#1a1d29",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(82,183,136,0.2)"},
                    {"range": [50, 100], "color": "rgba(249,199,79,0.2)"},
                    {"range": [100, 150], "color": "rgba(248,150,30,0.2)"},
                    {"range": [150, gauge_max], "color": "rgba(230,57,70,0.2)"},
                ],
            },
        ))
        fig.update_layout(
            height=280,
            paper_bgcolor="#1a1d29",
            font={"color": "#a0a4b8"},
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)


def render_about():
    section("🌍 Air Quality Analysis & Prediction — Pakistan")
    st.markdown(
        """
A data-driven dashboard analyzing air quality across **5 major Pakistan cities**:
Lahore, Karachi, Islamabad, Peshawar, and Quetta.

**Key Features**
- **Live Monitoring** — pull current readings from the OpenWeatherMap air-pollution API
- **Trend Analysis** — daily-average AQI trends and pollutant correlations
- **ML Predictions** — Random Forest / Gradient Boosting / Linear Regression,
  trained on a **chronological hold-out split** with test metrics computed live
  and displayed next to every prediction (never hard-coded)
- **EPA-correct AQI** — PM2.5/PM10 → AQI conversion uses the US EPA 2024
  breakpoints with proper concentration truncation

**Data sources**
- *Live mode*: OpenWeatherMap Air Pollution API (one current snapshot per city)
- *Demo mode*: clearly-labelled synthetic 90-day series (values are correlated
  by construction, so model metrics on demo data demonstrate the pipeline,
  not real-world forecasting skill)

**Tech Stack**: `Python` `Streamlit` `scikit-learn` `Pandas` `Plotly`

**Model training protocol** (see `src/model.py`): rows sorted by time →
first 80% train / last 20% test → scaler and median imputation fit on the
training split only.
        """
    )


def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 🌍 AQI Pakistan")
        st.markdown("---")
        st.markdown("**Navigation**")
        page = st.radio(
            "", ["📊 Overview", "🔬 Analytics", "🤖 Predict", "ℹ️ About"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown("**Data Source**")
        use_api = st.toggle("Live API (OpenWeatherMap)", value=False)
        api_token = ""
        if use_api:
            api_token = st.text_input("OWM API Key", type="password")
            st.caption("Key is used in-memory for this session only.")
        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.8rem; color:#6c757d; text-align:center;">'
            'Built with Streamlit</div>',
            unsafe_allow_html=True,
        )

    df = None
    if use_api and api_token:
        with st.spinner("Fetching live data from OpenWeatherMap..."):
            try:
                collector = AirQualityCollector(token=api_token)
                live_df = collector.collect_cities_current(CITIES)
            except ValueError as exc:
                st.error(str(exc))
                live_df = pd.DataFrame()
            except Exception:
                live_df = pd.DataFrame()

        if live_df.empty:
            st.warning("Live API unavailable — falling back to demo data.")
            df = load_or_generate_data()
            st.caption("📊 Showing demo data with all pollutants.")
        else:
            # Merge the live snapshot onto the historical series so trend
            # charts and metrics keep working (live rows simply extend it).
            history = load_or_generate_data()
            history["source"] = "history"
            live_df["source"] = "live"
            df = pd.concat([history, live_df], ignore_index=True)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df = df.sort_values("timestamp").reset_index(drop=True)
            st.info("Showing live readings (appended to the demo history so trends remain visible).")
            st.caption("Live rows lack weather fields; prediction models impute them from training medians.")
    else:
        df = load_or_generate_data()
        st.caption("📊 Showing clearly-labelled demo data. Toggle 'Live API' in the sidebar for real-time readings.")

    if page == "📊 Overview":
        render_overview(df)
    elif page == "🔬 Analytics":
        render_analytics(df)
    elif page == "🤖 Predict":
        render_predict(df)
    elif page == "ℹ️ About":
        render_about()


if __name__ == "__main__":
    main()
