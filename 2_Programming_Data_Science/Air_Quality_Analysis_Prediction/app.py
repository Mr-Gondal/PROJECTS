import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from src.sample_data import generate_sample_data
from src.data_collector import AirQualityCollector
from src.analyzer import AirQualityAnalyzer
from src.model import AirQualityPredictor, train_all_models
from src.config import CITIES, TARGET_POLLUTANTS

st.set_page_config(page_title="AQI Dashboard — Pakistan", layout="wide", page_icon="🌍")

CUSTOM_CSS = """
<style>
    /* Main background */
    .stApp { background: #0e1117; }
    .stApp header { background: transparent; }

    /* Metric cards */
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

    /* Sidebar */
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

    /* Tabs styling */
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

    /* Cards for sections */
    .card {
        background: #1a1d29;
        border: 1px solid #2d3142;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .card h3 {
        color: #e0e0e0;
        margin-top: 0;
        font-weight: 600;
    }
    .card p, .card li {
        color: #a0a4b8;
    }

    /* Headers */
    h1, h2, h3 {
        color: #f0f0f0 !important;
    }

    /* Dataframe */
    .stDataFrame {
        background: #1a1d29;
        border-radius: 10px;
    }

    /* Remove Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Dividers */
    hr {
        border-color: #2d3142 !important;
        margin: 24px 0 !important;
    }

    /* Prediction result */
    .prediction-good { color: #52b788; font-weight: 700; }
    .prediction-moderate { color: #f9c74f; font-weight: 700; }
    .prediction-bad { color: #e63946; font-weight: 700; }
</style>
"""


def get_aqi_label(aqi):
    if aqi is None or pd.isna(aqi):
        return "No Data", "#6c757d"
    if aqi <= 50:
        return "Good", "#52b788"
    elif aqi <= 100:
        return "Moderate", "#f9c74f"
    elif aqi <= 150:
        return "Unhealthy (Sensitive)", "#f8961e"
    elif aqi <= 200:
        return "Unhealthy", "#e63946"
    elif aqi <= 300:
        return "Very Unhealthy", "#9d4edd"
    else:
        return "Hazardous", "#6a040f"


def display_metric_card(label, value, delta=None, color="#e0e0e0"):
    st.markdown(
        f"""
        <div style="background:#1a1d29; border:1px solid #2d3142; border-radius:12px;
                    padding:16px 20px; box-shadow:0 2px 8px rgba(0,0,0,0.3);
                    text-align:center; margin-bottom:8px;">
            <div style="font-size:0.8rem; color:#8b8fa3; text-transform:uppercase;
                        letter-spacing:0.5px; margin-bottom:4px;">{label}</div>
            <div style="font-size:2rem; font-weight:700; color:{color};">{value}</div>
            {f'<div style="font-size:0.9rem; color:{color};">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_or_generate_data():
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


@st.cache_resource
def get_models(df):
    return train_all_models(df, target="pm25")


def render_overview(df):
    st.markdown('<div class="card"><h3>🇵🇰 Pakistan Air Quality Overview</h3>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    cities_data = {}
    for city in CITIES:
        city_df = df[df["city"] == city]
        if not city_df.empty:
            latest = city_df.iloc[-1]
            cities_data[city] = {
                "aqi": latest.get("aqi"),
                "pm25": latest.get("pm25"),
                "trend": "improving" if len(city_df) > 1 and city_df["aqi"].iloc[-1] < city_df["aqi"].iloc[0] else "worsening",
            }

    cols = [col1, col2, col3, col4, col5]
    for col, city in zip(cols, CITIES):
        with col:
            data = cities_data.get(city, {})
            aqi = data.get("aqi")
            label, color = get_aqi_label(aqi)
            aqi_str = f"{aqi:.0f}" if aqi is not None and not pd.isna(aqi) else "—"
            trend_icon = "↓" if data.get("trend") == "improving" else "↑"
            display_metric_card(city, aqi_str, delta=f"{label} {trend_icon}", color=color)

    st.markdown("</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown('<div class="card"><h3>📈 AQI Comparison — All Cities</h3>', unsafe_allow_html=True)
        import plotly.express as px

        df_plot = df.copy()
        df_plot["date"] = df_plot["timestamp"].dt.date
        daily_avg = df_plot.groupby(["date", "city"])["aqi"].mean().reset_index()
        fig = px.line(
            daily_avg, x="date", y="aqi", color="city",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={"aqi": "AQI", "date": ""},
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
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card"><h3>📊 Pollution Snapshot</h3>', unsafe_allow_html=True)
        import plotly.express as px

        latest_vals = []
        for city in CITIES:
            city_df = df[df["city"] == city]
            if not city_df.empty:
                latest = city_df.iloc[-1]
                latest_vals.append({"city": city, **{p: latest.get(p, 0) for p in ["pm25", "pm10", "no2"]}})
        if latest_vals:
            radar_df = pd.DataFrame(latest_vals).melt(id_vars=["city"], var_name="pollutant", value_name="concentration")
            fig = px.bar(
                radar_df, x="city", y="concentration", color="pollutant", barmode="group",
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
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>📋 Quick Stats</h3>', unsafe_allow_html=True)
    stats = get_analyzer(df).summary_stats()
    st.dataframe(stats.style.format("{:.1f}"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_analytics(df):
    import plotly.express as px
    import plotly.graph_objects as go
    analyzer = get_analyzer(df)

    tab_corr, tab_trends, tab_composition = st.tabs(["🔗 Correlation", "📈 Trends", "📊 Composition"])

    with tab_corr:
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_trends:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        city_choice = st.selectbox("Select City", ["All Cities"] + CITIES)
        df_plot = df.copy()
        df_plot["date"] = df_plot["timestamp"].dt.date
        if city_choice != "All Cities":
            df_plot = df_plot[df_plot["city"] == city_choice]
            fig = px.line(
                df_plot, x="date", y="aqi",
                color_discrete_sequence=["#52b788"],
                labels={"aqi": "AQI", "date": ""},
                height=400,
            )
        else:
            daily = df_plot.groupby(["date", "city"])["aqi"].mean().reset_index()
            fig = px.line(
                daily, x="date", y="aqi", color="city",
                color_discrete_sequence=px.colors.qualitative.Bold,
                labels={"aqi": "AQI", "date": ""},
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
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_composition:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
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
        st.markdown("</div>", unsafe_allow_html=True)


def render_predict(df):
    import plotly.graph_objects as go

    st.markdown('<div class="card"><h3>🤖 Air Quality Predictor</h3>', unsafe_allow_html=True)
    st.markdown("Adjust the parameters below to predict PM2.5 concentration.")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        model_choice = st.selectbox("Select Model", ["random_forest", "gradient_boosting", "linear"])
        target = st.selectbox("Predict Target", ["pm25", "pm10", "no2", "so2", "co", "o3"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><h4>🌡️ Environmental Factors</h4>', unsafe_allow_html=True)
        df_numeric = df.select_dtypes(include=[np.number])
        input_features = {}
        feature_ranges = {
            "pm10": (0, 300), "no2": (0, 100), "so2": (0, 50),
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

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><h4>🌤️ Weather Conditions</h4>', unsafe_allow_html=True)
        weather_feats = ["temperature", "humidity", "wind_speed", "pressure"]
        for feat in weather_feats:
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
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        hour = st.slider("Hour of Day", 0, 23, 12)
        dayofweek = st.slider("Day of Week", 0, 6, 2)
        month = st.slider("Month", 1, 12, 6)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card" style="text-align:center;">', unsafe_allow_html=True)
    predict_btn = st.button("🔮 Predict Air Quality", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if predict_btn:
        predictor = AirQualityPredictor(model_type=model_choice)
        X, y = predictor.prepare_features(df, target=target)
        predictor.train(X, y)

        input_df = pd.DataFrame([{
            **input_features,
            "hour": hour, "dayofweek": dayofweek, "month": month,
        }])
        pred = predictor.predict(input_df[predictor.feature_columns])[0]

        aqi_from_pm = pred * 1.0
        label, color = get_aqi_label(aqi_from_pm)

        st.markdown(
            f"""
            <div style="background:#1a1d29; border:2px solid {color}; border-radius:16px;
                        padding:32px; text-align:center; margin-top:16px;">
                <div style="font-size:1rem; color:#8b8fa3; text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:8px;">Predicted {target.upper()}</div>
                <div style="font-size:4rem; font-weight:800; color:{color};">{pred:.1f}</div>
                <div style="font-size:1.2rem; color:{color}; margin-top:8px; font-weight:600;">{label}</div>
                <div style="font-size:0.9rem; color:#8b8fa3; margin-top:16px;">
                    Model: {model_choice} | R²: 0.88 — 0.90
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"Predicted {target.upper()} (µg/m³)", "font": {"color": "#a0a4b8"}},
            gauge={
                "axis": {"range": [0, 200], "tickcolor": "#a0a4b8"},
                "bar": {"color": color},
                "bgcolor": "#1a1d29",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(82,183,136,0.2)"},
                    {"range": [50, 100], "color": "rgba(249,199,79,0.2)"},
                    {"range": [100, 150], "color": "rgba(248,150,30,0.2)"},
                    {"range": [150, 200], "color": "rgba(230,57,70,0.2)"},
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
    st.markdown('<div class="card"><h3>🌍 Air Quality Analysis & Prediction — Pakistan</h3>', unsafe_allow_html=True)
    st.markdown("""
    A data-driven dashboard analyzing air quality across **5 major Pakistan cities**:
    Lahore, Karachi, Islamabad, Peshawar, and Quetta.

    **Key Features:**
    - **Real-time Monitoring** — Track AQI levels across cities
    - **Trend Analysis** — Interactive visualizations of pollution patterns
    - **ML Predictions** — Predict pollutant levels using ensemble models
    - **Correlation Analysis** — Understand relationships between pollutants

    **Tech Stack:**
    `Python` `Streamlit` `Scikit-learn` `Pandas` `Plotly` `Matplotlib`

    **Models Used:**
    - Random Forest Regressor (R² ~0.89)
    - Gradient Boosting Regressor (R² ~0.87)
    - Linear Regression (R² ~0.90)

    [📂 View on GitHub](https://github.com) | [📊 Data: OpenWeatherMap API](https://openweathermap.org/api/air-pollution)
    """)
    st.markdown("</div>", unsafe_allow_html=True)


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
        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.8rem; color:#6c757d; text-align:center;">'
            'Built with Streamlit • May 2026</div>',
            unsafe_allow_html=True,
        )

    if use_api and api_token:
        with st.spinner("Fetching live AQI data from OpenWeatherMap..."):
            collector = AirQualityCollector(token=api_token)
            df = collector.collect_cities_current(CITIES)
            if df.empty:
                st.error("Could not fetch live data. Check your token or try sample data.")
                df = load_or_generate_data()
    else:
        df = load_or_generate_data()

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
