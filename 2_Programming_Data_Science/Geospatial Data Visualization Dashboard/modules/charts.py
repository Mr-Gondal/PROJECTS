"""
Charts Module - Chart and Graph Creation Functions
===================================================

This module provides functions for creating interactive charts using Plotly.
All charts are optimized for Streamlit integration.

Key Features:
    - Bar charts for comparisons
    - Pie charts for distributions
    - Line charts for time series
    - Scatter geo for geographic plots
    - Area charts for cumulative data

Dependencies:
    - plotly
    - pandas

Author: Haris Hussain - GIS Analyst | Geospatial Data Specialist
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List, Dict
import numpy as np


# Color schemes for charts
COLOR_SCHEMES = {
    'population': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
    'climate': ['#1a5276', '#2980b9', '#3498db', '#5dade2', '#85c1e9', '#aed6f1'],
    'economy': ['#27ae60', '#2ecc71', '#58d68d', '#82e0aa', '#abebc6', '#d5f5e3'],
    'default': px.colors.qualitative.Set2
}


def create_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    color_continuous_scale: str = 'Viridis',
    orientation: str = 'v',
    barmode: str = 'group',
    height: int = 500,
    show_values: bool = True
) -> go.Figure:
    """
    Create an interactive bar chart.

    Parameters:
        data (pd.DataFrame): Data to plot.
        x (str): Column name for x-axis.
        y (str): Column name for y-axis.
        title (str): Chart title.
        color (str, optional): Column for color coding.
        color_continuous_scale (str): Color scale name.
        orientation (str): 'v' for vertical, 'h' for horizontal.
        barmode (str): 'group', 'stack', or 'overlay'.
        height (int): Chart height in pixels.
        show_values (bool): Show values on bars.

    Returns:
        go.Figure: Plotly figure object.

    Example:
        >>> fig = create_bar_chart(
        ...     df, x='province', y='population',
        ...     title='Population by Province'
        ... )
    """
    fig = px.bar(
        data,
        x=x if orientation == 'v' else y,
        y=y if orientation == 'v' else x,
        color=color,
        color_continuous_scale=color_continuous_scale,
        orientation=orientation,
        barmode=barmode,
        title=title,
        height=height
    )

    # Update layout
    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_tickangle=-45,
        font=dict(size=12)
    )

    # Add value labels on bars
    if show_values:
        fig.update_traces(texttemplate='%{y:.2s}', textposition='outside')

    return fig


def create_pie_chart(
    data: pd.DataFrame,
    values: str,
    names: str,
    title: str,
    hole: float = 0.0,
    colors: Optional[List[str]] = None,
    height: int = 500,
    show_legend: bool = True
) -> go.Figure:
    """
    Create an interactive pie chart.

    Parameters:
        data (pd.DataFrame): Data to plot.
        values (str): Column name for values.
        names (str): Column name for labels.
        title (str): Chart title.
        hole (float): Size of center hole (0-1). Use 0.4 for donut chart.
        colors (list, optional): Custom color list.
        height (int): Chart height in pixels.
        show_legend (bool): Show legend.

    Returns:
        go.Figure: Plotly figure object.

    Example:
        >>> fig = create_pie_chart(
        ...     df, values='population', names='province',
        ...     title='Population Distribution', hole=0.4
        ... )
    """
    fig = px.pie(
        data,
        values=values,
        names=names,
        title=title,
        hole=hole,
        color_discrete_sequence=colors or COLOR_SCHEMES['population']
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        pull=[0.05 if i == 0 else 0 for i in range(len(data))]
    )

    fig.update_layout(
        template='plotly_white',
        showlegend=show_legend,
        height=height,
        font=dict(size=12)
    )

    return fig


def create_line_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    line_shape: str = 'linear',
    markers: bool = True,
    height: int = 500,
    show_range_slider: bool = False
) -> go.Figure:
    """
    Create an interactive line chart for time series data.

    Parameters:
        data (pd.DataFrame): Data to plot.
        x (str): Column name for x-axis (usually time).
        y (str): Column name for y-axis.
        title (str): Chart title.
        color (str, optional): Column for grouping lines.
        line_shape (str): 'linear', 'spline', 'hv', 'vh', 'hvh', 'vhv'.
        markers (bool): Show data point markers.
        height (int): Chart height in pixels.
        show_range_slider (bool): Show range slider below chart.

    Returns:
        go.Figure: Plotly figure object.

    Example:
        >>> fig = create_line_chart(
        ...     df, x='year', y='temperature',
        ...     title='Temperature Trend (2015-2024)'
        ... )
    """
    fig = px.line(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        markers=markers,
        line_shape=line_shape,
        height=height
    )

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        xaxis_title=x.capitalize(),
        yaxis_title=y.capitalize(),
        font=dict(size=12)
    )

    if show_range_slider:
        fig.update_xaxes(rangeslider_visible=True)

    return fig


def create_area_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: int = 500,
    group_stacking: bool = True
) -> go.Figure:
    """
    Create an interactive area chart.

    Parameters:
        data (pd.DataFrame): Data to plot.
        x (str): Column name for x-axis.
        y (str): Column name for y-axis.
        title (str): Chart title.
        color (str, optional): Column for grouping areas.
        height (int): Chart height in pixels.
        group_stacking (bool): Stack groups.

    Returns:
        go.Figure: Plotly figure object.

    Example:
        >>> fig = create_area_chart(
        ...     df, x='year', y='value',
        ...     title='Cumulative Growth', color='category'
        ... )
    """
    fig = px.area(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        height=height
    )

    fig.update_layout(
        template='plotly_white',
        hovermode='x unified',
        font=dict(size=12)
    )

    if group_stacking:
        fig.update_layout(barmode='stack')

    return fig


def create_scatter_geo(
    data: pd.DataFrame,
    lat: str,
    lon: str,
    size: Optional[str] = None,
    color: Optional[str] = None,
    hover_name: Optional[str] = None,
    title: str = 'Geographic Distribution',
    height: int = 600,
    zoom: int = 4,
    center: dict = None
) -> go.Figure:
    """
    Create an interactive geographic scatter plot.

    Parameters:
        data (pd.DataFrame): Data to plot.
        lat (str): Column name for latitude.
        lon (str): Column name for longitude.
        size (str, optional): Column for marker size.
        color (str, optional): Column for marker color.
        hover_name (str, optional): Column for hover text.
        title (str): Chart title.
        height (int): Chart height in pixels.
        zoom (int): Map zoom level.
        center (dict, optional): Map center {'lat': x, 'lon': y}.

    Returns:
        go.Figure: Plotly figure object.

    Example:
        >>> fig = create_scatter_geo(
        ...     df, lat='latitude', lon='longitude',
        ...     size='population', color='density',
        ...     title='Population Distribution in Pakistan'
        ... )
    """
    # Default center on Pakistan
    if center is None:
        center = {'lat': 30.3753, 'lon': 69.3451}

    fig = px.scatter_geo(
        data,
        lat=lat,
        lon=lon,
        size=size,
        color=color,
        hover_name=hover_name,
        title=title,
        height=height,
        projection='natural earth'
    )

    fig.update_geos(
        center=center,
        projection_scale=zoom,
        showcountries=True,
        countrycolor='gray',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        showocean=True,
        oceancolor='rgb(204, 229, 255)',
        coastline=True
    )

    fig.update_layout(
        template='plotly_white',
        font=dict(size=12)
    )

    return fig


def create_comparison_chart(
    data: pd.DataFrame,
    x: str,
    y_columns: List[str],
    title: str,
    chart_type: str = 'bar',
    height: int = 500
) -> go.Figure:
    """
    Create a comparison chart with multiple series.

    Parameters:
        data (pd.DataFrame): Data to plot.
        x (str): Column name for x-axis.
        y_columns (list): List of column names for y-axis.
        title (str): Chart title.
        chart_type (str): 'bar' or 'line'.
        height (int): Chart height in pixels.

    Returns:
        go.Figure: Plotly figure object.

    Example:
        >>> fig = create_comparison_chart(
        ...     df, x='province',
        ...     y_columns=['population_2015', 'population_2024'],
        ...     title='Population Growth Comparison'
        ... )
    """
    fig = go.Figure()

    colors = COLOR_SCHEMES['default']

    for i, col in enumerate(y_columns):
        if chart_type == 'bar':
            fig.add_trace(go.Bar(
                name=col,
                x=data[x],
                y=data[col],
                marker_color=colors[i % len(colors)]
            ))
        else:
            fig.add_trace(go.Scatter(
                name=col,
                x=data[x],
                y=data[col],
                mode='lines+markers',
                line=dict(color=colors[i % len(colors)])
            ))

    fig.update_layout(
        title=title,
        barmode='group' if chart_type == 'bar' else None,
        template='plotly_white',
        height=height,
        hovermode='x unified',
        font=dict(size=12)
    )

    return fig


def create_multi_chart_dashboard(
    data: pd.DataFrame,
    charts_config: List[Dict],
    title: str = 'Dashboard',
    height: int = 800
) -> go.Figure:
    """
    Create a multi-chart dashboard in a single figure.

    Parameters:
        data (pd.DataFrame): Data to plot.
        charts_config (list): List of chart configurations.
            Each config is a dict with keys: 'type', 'x', 'y', 'title'.
        title (str): Overall dashboard title.
        height (int): Total dashboard height in pixels.

    Returns:
        go.Figure: Plotly figure with subplots.

    Example:
        >>> config = [
        ...     {'type': 'bar', 'x': 'province', 'y': 'population', 'title': 'Population'},
        ...     {'type': 'pie', 'values': 'population', 'names': 'province', 'title': 'Distribution'}
        ... ]
        >>> fig = create_multi_chart_dashboard(df, config)
    """
    rows = (len(charts_config) + 1) // 2
    fig = make_subplots(
        rows=rows,
        cols=2,
        subplot_titles=[c['title'] for c in charts_config]
    )

    for i, config in enumerate(charts_config):
        row = (i // 2) + 1
        col = (i % 2) + 1

        if config['type'] == 'bar':
            fig.add_trace(
                go.Bar(x=data[config['x']], y=data[config['y']]),
                row=row, col=col
            )
        elif config['type'] == 'line':
            fig.add_trace(
                go.Scatter(x=data[config['x']], y=data[config['y']], mode='lines+markers'),
                row=row, col=col
            )

    fig.update_layout(
        title=title,
        height=height,
        showlegend=False,
        template='plotly_white'
    )

    return fig