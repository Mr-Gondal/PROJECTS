"""
src/visualizations.py
======================
Plotly-based interactive visualization functions for the Pakistan
Climate Data Analysis & Visualization Tool.

All charts use the 'plotly_dark' template with a consistent color palette:
  - Teal / Cyan  : #00d4ff  (primary accent)
  - Coral / Red  : #ff6b6b  (warm / anomaly highlight)
  - Amber        : #ffd166  (secondary accent)
  - Green        : #06d6a0  (wet / positive)

Author: Haris Hussain
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats

# ---------------------------------------------------------------------------
# Shared style constants
# ---------------------------------------------------------------------------
TEMPLATE = "plotly_dark"
TEAL = "#00d4ff"
CORAL = "#ff6b6b"
AMBER = "#ffd166"
GREEN = "#06d6a0"
PURPLE = "#b388ff"

CITY_COLORS = {
    "Lahore": TEAL,
    "Karachi": CORAL,
    "Islamabad": GREEN,
    "Peshawar": AMBER,
    "Quetta": PURPLE,
    "Multan": "#ff9f43",
}

PAPER_BG = "rgba(10,10,15,0)"
PLOT_BG = "rgba(13,17,23,0.6)"

FONT_FAMILY = "Inter, Segoe UI, Arial, sans-serif"


def _base_layout(title: str, xaxis_title: str = "", yaxis_title: str = "") -> dict:
    """Return a shared base layout dict for consistent styling."""
    return dict(
        template=TEMPLATE,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family=FONT_FAMILY, size=13, color="#e0e0e0"),
        title=dict(
            text=title,
            font=dict(size=18, color="#ffffff", family=FONT_FAMILY),
            x=0.02,
        ),
        xaxis=dict(
            title=xaxis_title,
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.15)",
            borderwidth=1,
        ),
        margin=dict(l=60, r=30, t=60, b=50),
    )


# ---------------------------------------------------------------------------
# 1. Temperature Trend Chart
# ---------------------------------------------------------------------------

def plot_temperature_trend(df: pd.DataFrame, city: str) -> go.Figure:
    """
    Line chart of monthly mean temperature for a single city with:
    - Raw monthly values (faint)
    - 10-year (120-month) rolling average
    - Confidence band around the rolling average
    - Linear trend line

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame.
    city : str
        City to visualise.

    Returns
    -------
    go.Figure
    """
    city_df = (
        df[df["city"] == city]
        .sort_values(["year", "month"])
        .reset_index(drop=True)
    )

    # Create a continuous time axis (year + month fraction)
    city_df["time"] = city_df["year"] + (city_df["month"] - 1) / 12.0

    raw_temp = city_df["temperature_mean"].values
    time_vals = city_df["time"].values

    # Rolling average (120-month window)
    window = 120
    rolling_mean = (
        pd.Series(raw_temp)
        .rolling(window=window, center=True, min_periods=30)
        .mean()
        .values
    )
    rolling_std = (
        pd.Series(raw_temp)
        .rolling(window=window, center=True, min_periods=30)
        .std()
        .values
    )

    # Linear trend
    slope, intercept, r_val, p_val, _ = stats.linregress(time_vals, raw_temp)
    trend_line = slope * time_vals + intercept

    color = CITY_COLORS.get(city, TEAL)
    fig = go.Figure()

    # Confidence band (±1 std)
    upper = rolling_mean + rolling_std
    lower = rolling_mean - rolling_std

    fig.add_trace(
        go.Scatter(
            x=np.concatenate([time_vals, time_vals[::-1]]),
            y=np.concatenate([upper, lower[::-1]]),
            fill="toself",
            fillcolor=f"rgba(0,212,255,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            name="±1σ Band",
            hoverinfo="skip",
        )
    )

    # Raw monthly values
    fig.add_trace(
        go.Scatter(
            x=time_vals,
            y=raw_temp,
            mode="lines",
            name="Monthly Mean",
            line=dict(color=f"rgba{(*px.colors.hex_to_rgb(color), 0.25)}", width=1),
            hovertemplate="Year: %{x:.2f}<br>Temp: %{y:.1f}°C<extra></extra>",
        )
    )

    # 10-year rolling average
    fig.add_trace(
        go.Scatter(
            x=time_vals,
            y=rolling_mean,
            mode="lines",
            name="10-Year Rolling Mean",
            line=dict(color=color, width=2.5),
            hovertemplate="Year: %{x:.2f}<br>Rolling Avg: %{y:.1f}°C<extra></extra>",
        )
    )

    # Linear trend
    fig.add_trace(
        go.Scatter(
            x=time_vals,
            y=trend_line,
            mode="lines",
            name=f"Linear Trend (R²={r_val**2:.3f})",
            line=dict(color=CORAL, width=2, dash="dash"),
            hoverinfo="skip",
        )
    )

    layout = _base_layout(
        f"🌡️ Temperature Trend — {city} (1974–2024)",
        xaxis_title="Year",
        yaxis_title="Temperature (°C)",
    )
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 2. Precipitation Heatmap
# ---------------------------------------------------------------------------

def plot_precipitation_heatmap(df: pd.DataFrame, city: str) -> go.Figure:
    """
    Month × Year heatmap of monthly precipitation for a single city.

    Parameters
    ----------
    df : pd.DataFrame
        Raw monthly climate DataFrame.
    city : str
        City to visualise.

    Returns
    -------
    go.Figure
    """
    city_df = df[df["city"] == city].copy()

    pivot = city_df.pivot_table(
        index="month", columns="year", values="precipitation_mm", aggfunc="mean"
    )

    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=[month_labels[i - 1] for i in pivot.index],
            colorscale=[
                [0.0, "#0a0a1e"],
                [0.2, "#0d3b6e"],
                [0.5, "#0077b6"],
                [0.75, "#00b4d8"],
                [1.0, "#90e0ef"],
            ],
            colorbar=dict(
                title=dict(text="mm", font=dict(color="#e0e0e0")),
                tickfont=dict(color="#e0e0e0"),
            ),
            hovertemplate="Year: %{x}<br>Month: %{y}<br>Precipitation: %{z:.1f} mm<extra></extra>",
        )
    )

    layout = _base_layout(
        f"🌧️ Monthly Precipitation Heatmap — {city} (1974–2024)",
        xaxis_title="Year",
        yaxis_title="Month",
    )
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 3. Climate Stripes
# ---------------------------------------------------------------------------

def plot_climate_stripes(annual_df: pd.DataFrame, city: str) -> go.Figure:
    """
    Warming Stripes visualization — horizontal bar chart where each bar
    represents one year colored by temperature anomaly relative to
    the 1974–2004 baseline (blue=cool, red=warm).

    Parameters
    ----------
    annual_df : pd.DataFrame
        Output of ``compute_climate_stripes_data(df, city)``.
        Must have columns [year, temp_anomaly].
    city : str
        City label for the chart title.

    Returns
    -------
    go.Figure
    """
    anomalies = annual_df["temp_anomaly"].values
    years = annual_df["year"].values

    max_abs = max(abs(anomalies.max()), abs(anomalies.min()), 0.01)

    # Color map: symmetric blue→white→red
    colorscale = [
        [0.0, "#053061"],
        [0.1, "#2166ac"],
        [0.25, "#4393c3"],
        [0.40, "#92c5de"],
        [0.5, "#f7f7f7"],
        [0.60, "#f4a582"],
        [0.75, "#d6604d"],
        [0.9, "#b2182b"],
        [1.0, "#67001f"],
    ]

    fig = go.Figure()

    for i, (year, anomaly) in enumerate(zip(years, anomalies)):
        # Normalize to [0, 1]
        norm = (anomaly + max_abs) / (2 * max_abs)
        norm = float(np.clip(norm, 0, 1))

        # Interpolate color from colorscale
        def _interp_color(norm_val: float, cs: list) -> str:
            for j in range(len(cs) - 1):
                if cs[j][0] <= norm_val <= cs[j + 1][0]:
                    t = (norm_val - cs[j][0]) / (cs[j + 1][0] - cs[j][0])
                    c0 = px.colors.hex_to_rgb(cs[j][1])
                    c1 = px.colors.hex_to_rgb(cs[j + 1][1])
                    r = int(c0[0] + t * (c1[0] - c0[0]))
                    g = int(c0[1] + t * (c1[1] - c0[1]))
                    b = int(c0[2] + t * (c1[2] - c0[2]))
                    return f"rgb({r},{g},{b})"
            return cs[-1][1]

        color = _interp_color(norm, colorscale)

        fig.add_trace(
            go.Bar(
                x=[1],
                y=[year],
                orientation="h",
                marker_color=color,
                marker_line_width=0,
                width=0.95,
                hovertemplate=f"<b>{year}</b><br>Anomaly: {anomaly:+.2f}°C<extra></extra>",
                showlegend=False,
            )
        )

    # Add colorbar as a dummy scatter
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                colorscale=colorscale,
                cmin=-max_abs,
                cmax=max_abs,
                color=[0],
                colorbar=dict(
                    title=dict(text="Anomaly (°C)", font=dict(color="#e0e0e0")),
                    tickfont=dict(color="#e0e0e0"),
                    thickness=15,
                ),
                showscale=True,
            ),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    layout = _base_layout(
        f"🌈 Climate Warming Stripes — {city} (1974–2024)",
        xaxis_title="",
        yaxis_title="Year",
    )
    layout["xaxis"].update(showticklabels=False, showgrid=False, zeroline=False)
    layout["yaxis"].update(autorange="reversed", dtick=5)
    layout["barmode"] = "stack"
    layout["height"] = 500
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 4. Seasonal Comparison
# ---------------------------------------------------------------------------

def plot_seasonal_comparison(seasonal_df: pd.DataFrame, city: str) -> go.Figure:
    """
    Grouped bar chart of average temperature by season and decade for a city.

    Parameters
    ----------
    seasonal_df : pd.DataFrame
        Output of ``compute_seasonal_stats()``.
    city : str
        City to visualise.

    Returns
    -------
    go.Figure
    """
    city_df = seasonal_df[seasonal_df["city"] == city].copy()

    season_order = ["Winter", "Spring", "Summer", "Monsoon"]
    season_colors = {
        "Winter": "#4fc3f7",
        "Spring": GREEN,
        "Summer": CORAL,
        "Monsoon": AMBER,
    }

    decades = sorted(city_df["decade"].unique())
    fig = go.Figure()

    for season in season_order:
        s_df = city_df[city_df["season"] == season].sort_values("decade")
        fig.add_trace(
            go.Bar(
                x=s_df["decade"],
                y=s_df["temp_avg"],
                name=season,
                marker_color=season_colors[season],
                hovertemplate=f"<b>{season}</b><br>Decade: %{{x}}<br>Avg Temp: %{{y:.1f}}°C<extra></extra>",
            )
        )

    layout = _base_layout(
        f"📅 Seasonal Temperature by Decade — {city}",
        xaxis_title="Decade",
        yaxis_title="Average Temperature (°C)",
    )
    layout["barmode"] = "group"
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 5. Multi-City Comparison
# ---------------------------------------------------------------------------

def plot_multi_city_comparison(annual_df: pd.DataFrame, metric: str = "temp_avg") -> go.Figure:
    """
    Line chart comparing all cities for a given annual metric.

    Parameters
    ----------
    annual_df : pd.DataFrame
        Output of ``compute_annual_trends()``.
    metric : str
        Column name to plot. Default is 'temp_avg'.

    Returns
    -------
    go.Figure
    """
    metric_labels = {
        "temp_avg": ("Average Temperature (°C)", "🌡️ Annual Mean Temperature — All Cities (1974–2024)"),
        "precip_total": ("Precipitation (mm/year)", "🌧️ Annual Total Precipitation — All Cities (1974–2024)"),
        "humidity_avg": ("Humidity (%)", "💧 Annual Mean Humidity — All Cities (1974–2024)"),
        "wind_avg": ("Wind Speed (km/h)", "🌬️ Annual Mean Wind Speed — All Cities (1974–2024)"),
    }

    y_label, title = metric_labels.get(metric, (metric, f"Multi-City: {metric}"))

    fig = go.Figure()

    for city in sorted(annual_df["city"].unique()):
        c_df = annual_df[annual_df["city"] == city].sort_values("year")
        color = CITY_COLORS.get(city, TEAL)
        fig.add_trace(
            go.Scatter(
                x=c_df["year"],
                y=c_df[metric],
                mode="lines",
                name=city,
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{city}</b><br>Year: %{{x}}<br>{y_label}: %{{y:.2f}}<extra></extra>",
            )
        )

    layout = _base_layout(title, xaxis_title="Year", yaxis_title=y_label)
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 6. Anomaly Timeline
# ---------------------------------------------------------------------------

def plot_anomaly_timeline(df: pd.DataFrame, city: str) -> go.Figure:
    """
    Scatter plot showing temperature anomaly magnitude over time for a city.
    Warm anomalies are coral/red; cold anomalies are teal/blue.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``detect_anomalies()`` — must have
        [temp_anomaly_magnitude, is_temp_anomaly] columns.
    city : str
        City to visualise.

    Returns
    -------
    go.Figure
    """
    city_df = df[df["city"] == city].copy().sort_values(["year", "month"])
    city_df["time"] = city_df["year"] + (city_df["month"] - 1) / 12.0

    normal = city_df[~city_df["is_temp_anomaly"]]
    warm_anom = city_df[city_df["is_temp_anomaly"] & (city_df["temp_anomaly_magnitude"] > 0)]
    cold_anom = city_df[city_df["is_temp_anomaly"] & (city_df["temp_anomaly_magnitude"] <= 0)]

    fig = go.Figure()

    # Normal months
    fig.add_trace(
        go.Scatter(
            x=normal["time"],
            y=normal["temp_anomaly_magnitude"],
            mode="markers",
            name="Normal",
            marker=dict(color="rgba(200,200,200,0.25)", size=4),
            hovertemplate="Year: %{x:.2f}<br>Anomaly Z: %{y:.2f}<extra></extra>",
        )
    )

    # Cold anomalies
    fig.add_trace(
        go.Scatter(
            x=cold_anom["time"],
            y=cold_anom["temp_anomaly_magnitude"],
            mode="markers",
            name="Cold Anomaly",
            marker=dict(color=TEAL, size=8, symbol="triangle-down", line=dict(color="white", width=0.5)),
            hovertemplate=(
                "<b>Cold Anomaly</b><br>Year: %{x:.2f}<br>Z-score: %{y:.2f}<extra></extra>"
            ),
        )
    )

    # Warm anomalies
    fig.add_trace(
        go.Scatter(
            x=warm_anom["time"],
            y=warm_anom["temp_anomaly_magnitude"],
            mode="markers",
            name="Warm Anomaly",
            marker=dict(color=CORAL, size=8, symbol="triangle-up", line=dict(color="white", width=0.5)),
            hovertemplate=(
                "<b>Warm Anomaly</b><br>Year: %{x:.2f}<br>Z-score: %{y:.2f}<extra></extra>"
            ),
        )
    )

    # Reference lines
    fig.add_hline(y=1.5, line_dash="dot", line_color=CORAL, opacity=0.5, annotation_text="+1.5σ")
    fig.add_hline(y=-1.5, line_dash="dot", line_color=TEAL, opacity=0.5, annotation_text="-1.5σ")
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)

    layout = _base_layout(
        f"⚠️ Temperature Anomaly Timeline — {city}",
        xaxis_title="Year",
        yaxis_title="Anomaly Z-Score (σ)",
    )
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 7. Drought Index (SPI)
# ---------------------------------------------------------------------------

def plot_drought_index(df: pd.DataFrame, city: str) -> go.Figure:
    """
    Bar chart of the annual mean SPI drought index for a city.
    Positive bars (green) = wetter than average.
    Negative bars (red) = drier than average / drought.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``compute_drought_index()`` — must have [spi] column.
    city : str
        City to visualise.

    Returns
    -------
    go.Figure
    """
    city_df = df[df["city"] == city].copy()

    annual_spi = city_df.groupby("year")["spi"].mean().reset_index()
    annual_spi.columns = ["year", "spi_annual"]
    annual_spi = annual_spi.sort_values("year")

    colors = [
        GREEN if v >= 0 else CORAL for v in annual_spi["spi_annual"]
    ]

    fig = go.Figure(
        go.Bar(
            x=annual_spi["year"],
            y=annual_spi["spi_annual"],
            marker_color=colors,
            hovertemplate="Year: %{x}<br>SPI: %{y:.3f}<extra></extra>",
            name="Annual SPI",
        )
    )

    # Reference lines for drought categories
    for level, label, color in [
        (-1.0, "Moderate Drought", AMBER),
        (-1.5, "Severe Drought", CORAL),
        (-2.0, "Extreme Drought", "#cc0000"),
    ]:
        fig.add_hline(
            y=level,
            line_dash="dot",
            line_color=color,
            opacity=0.6,
            annotation_text=label,
            annotation_font_size=11,
            annotation_font_color=color,
        )

    layout = _base_layout(
        f"💧 SPI Drought Index — {city} (1974–2024)",
        xaxis_title="Year",
        yaxis_title="Standardized Precipitation Index (SPI)",
    )
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 8. Projections Chart
# ---------------------------------------------------------------------------

def plot_temperature_projection(annual_df: pd.DataFrame, city: str, target_year: int = 2035) -> go.Figure:
    """
    Line chart showing historical annual mean temperature and a linear
    projection to ``target_year`` with a shaded uncertainty cone.

    Parameters
    ----------
    annual_df : pd.DataFrame
        Output of ``compute_annual_trends()``.
    city : str
        City to visualise.
    target_year : int
        Year to project to. Default 2035.

    Returns
    -------
    go.Figure
    """
    c_df = annual_df[annual_df["city"] == city].sort_values("year")
    years = c_df["year"].values
    temps = c_df["temp_avg"].values

    slope, intercept, r_val, p_val, std_err = stats.linregress(years, temps)

    proj_years = np.arange(years[-1], target_year + 1)
    proj_temps = slope * proj_years + intercept
    # Uncertainty cone grows with time
    uncertainty = std_err * np.sqrt(1 + (proj_years - years.mean()) ** 2 / np.sum((years - years.mean()) ** 2))

    color = CITY_COLORS.get(city, TEAL)

    fig = go.Figure()

    # Uncertainty cone
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([proj_years, proj_years[::-1]]),
            y=np.concatenate([proj_temps + 2 * uncertainty, (proj_temps - 2 * uncertainty)[::-1]]),
            fill="toself",
            fillcolor="rgba(255,107,107,0.1)",
            line=dict(color="rgba(0,0,0,0)"),
            name="95% Uncertainty",
            hoverinfo="skip",
        )
    )

    # Historical
    fig.add_trace(
        go.Scatter(
            x=years,
            y=temps,
            mode="lines+markers",
            name="Historical",
            line=dict(color=color, width=2),
            marker=dict(size=3),
            hovertemplate="Year: %{x}<br>Temp: %{y:.2f}°C<extra></extra>",
        )
    )

    # Projection
    fig.add_trace(
        go.Scatter(
            x=proj_years,
            y=proj_temps,
            mode="lines",
            name=f"Projection to {target_year}",
            line=dict(color=CORAL, width=2.5, dash="dash"),
            hovertemplate="Year: %{x}<br>Projected: %{y:.2f}°C<extra></extra>",
        )
    )

    layout = _base_layout(
        f"📈 Temperature Projection to {target_year} — {city}",
        xaxis_title="Year",
        yaxis_title="Annual Mean Temperature (°C)",
    )
    fig.update_layout(**layout)
    return fig


if __name__ == "__main__":
    from src.data_generator import generate_climate_dataset
    from src.analysis import (
        compute_annual_trends,
        detect_anomalies,
        compute_seasonal_stats,
        compute_climate_stripes_data,
        compute_drought_index,
    )

    df = generate_climate_dataset()
    annual = compute_annual_trends(df)
    anomaly_df = detect_anomalies(df)
    seasonal_df = compute_seasonal_stats(df)
    stripes_df = compute_climate_stripes_data(df, "Lahore")
    drought_df = compute_drought_index(df)

    fig = plot_temperature_trend(df, "Lahore")
    fig.write_html("temp_trend_test.html")
    print("Charts generated successfully — check temp_trend_test.html")
