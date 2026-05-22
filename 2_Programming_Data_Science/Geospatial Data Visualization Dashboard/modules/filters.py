"""
Filters Module - Streamlit Filter Components
============================================

This module provides reusable filter components for the dashboard.
All filters are designed for easy integration with Streamlit.

Key Features:
    - Province selector
    - Year range slider
    - Data type selector
    - Custom filter combinations

Dependencies:
    - streamlit
    - pandas

Author: Haris Hussain - GIS Analyst | Geospatial Data Specialist
"""

import streamlit as st
import pandas as pd
from typing import List, Tuple, Optional, Dict, Any


def province_filter(
    provinces: Optional[List[str]] = None,
    key: str = 'province_filter',
    include_all: bool = True,
    default: str = 'All'
) -> str:
    """
    Create a province selector filter.

    Parameters:
        provinces (list, optional): List of province names. Default uses all Pakistan provinces.
        key (str): Unique key for Streamlit widget.
        include_all (bool): Include 'All' option.
        default (str): Default selection.

    Returns:
        str: Selected province name.

    Example:
        >>> selected = province_filter()
        >>> if selected != 'All':
        ...     data = data[data['province'] == selected]
    """
    if provinces is None:
        provinces = ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'AJK', 'Gilgit-Baltistan']

    options = ['All'] + provinces if include_all else provinces

    return st.selectbox(
        'Select Province',
        options=options,
        index=options.index(default) if default in options else 0,
        key=key,
        help='Filter data by province'
    )


def year_filter(
    min_year: int = 2015,
    max_year: int = 2024,
    key: str = 'year_filter',
    default_range: Optional[Tuple[int, int]] = None
) -> Tuple[int, int]:
    """
    Create a year range slider filter.

    Parameters:
        min_year (int): Minimum year in range.
        max_year (int): Maximum year in range.
        key (str): Unique key for Streamlit widget.
        default_range (tuple, optional): Default (start, end) year.

    Returns:
        tuple: (start_year, end_year) selected.

    Example:
        >>> start, end = year_filter(2015, 2024)
        >>> data = data[(data['year'] >= start) & (data['year'] <= end)]
    """
    if default_range is None:
        default_range = (min_year, max_year)

    return st.slider(
        'Select Year Range',
        min_value=min_year,
        max_value=max_year,
        value=default_range,
        key=key,
        help='Filter data by year range'
    )


def data_type_filter(
    data_types: Optional[List[str]] = None,
    key: str = 'data_type_filter',
    default: str = 'Population'
) -> str:
    """
    Create a data type selector filter.

    Parameters:
        data_types (list, optional): List of data types.
        key (str): Unique key for Streamlit widget.
        default (str): Default selection.

    Returns:
        str: Selected data type.

    Example:
        >>> data_type = data_type_filter()
        >>> if data_type == 'Population':
        ...     df = load_province_data()
        >>> elif data_type == 'Climate':
        ...     df = load_climate_data()
    """
    if data_types is None:
        data_types = ['Population', 'Climate', 'Economy', 'Health', 'Education']

    return st.radio(
        'Select Data Type',
        options=data_types,
        index=data_types.index(default) if default in data_types else 0,
        key=key,
        horizontal=True,
        help='Choose the type of data to visualize'
    )


def metric_filter(
    metrics: List[str],
    key: str = 'metric_filter',
    label: str = 'Select Metric',
    default: Optional[str] = None
) -> str:
    """
    Create a metric selector filter.

    Parameters:
        metrics (list): List of metric names.
        key (str): Unique key for Streamlit widget.
        label (str): Label for the widget.
        default (str, optional): Default selection.

    Returns:
        str: Selected metric.

    Example:
        >>> metric = metric_filter(['population', 'density', 'area'])
        >>> fig = create_chart(df, x='province', y=metric)
    """
    default_index = metrics.index(default) if default and default in metrics else 0

    return st.selectbox(
        label,
        options=metrics,
        index=default_index,
        key=key
    )


def multi_select_filter(
    options: List[str],
    key: str = 'multi_select_filter',
    label: str = 'Select Items',
    default: Optional[List[str]] = None
) -> List[str]:
    """
    Create a multi-select filter.

    Parameters:
        options (list): List of options.
        key (str): Unique key for Streamlit widget.
        label (str): Label for the widget.
        default (list, optional): Default selections.

    Returns:
        list: Selected options.

    Example:
        >>> selected = multi_select_filter(['Punjab', 'Sindh', 'KPK'])
        >>> data = data[data['province'].isin(selected)]
    """
    return st.multiselect(
        label,
        options=options,
        default=default if default else options[:3],
        key=key,
        help='Select multiple items to include'
    )


def search_filter(
    key: str = 'search_filter',
    placeholder: str = 'Search...'
) -> str:
    """
    Create a search text input filter.

    Parameters:
        key (str): Unique key for Streamlit widget.
        placeholder (str): Placeholder text.

    Returns:
        str: Search query string.

    Example:
        >>> query = search_filter()
        >>> if query:
        ...     data = data[data['name'].str.contains(query, case=False)]
    """
    return st.text_input(
        'Search',
        placeholder=placeholder,
        key=key,
        help='Type to search'
    )


def apply_filters(
    data: pd.DataFrame,
    province: str = 'All',
    year_range: Optional[Tuple[int, int]] = None,
    column_mapping: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Apply all filters to a DataFrame.

    Parameters:
        data (pd.DataFrame): Data to filter.
        province (str): Province to filter by. 'All' for no filter.
        year_range (tuple, optional): (start_year, end_year) to filter.
        column_mapping (dict, optional): Column name mapping.
            Expected keys: 'province', 'year'

    Returns:
        pd.DataFrame: Filtered DataFrame.

    Example:
        >>> filtered_data = apply_filters(
        ...     df,
        ...     province='Punjab',
        ...     year_range=(2018, 2024)
        ... )
    """
    filtered = data.copy()

    # Set column names
    prov_col = column_mapping.get('province', 'province') if column_mapping else 'province'
    year_col = column_mapping.get('year', 'year') if column_mapping else 'year'

    # Apply province filter
    if province != 'All' and prov_col in filtered.columns:
        filtered = filtered[filtered[prov_col] == province]

    # Apply year range filter
    if year_range and year_col in filtered.columns:
        start_year, end_year = year_range
        filtered = filtered[
            (filtered[year_col] >= start_year) &
            (filtered[year_col] <= end_year)
        ]

    return filtered


def create_sidebar_filters() -> Dict[str, Any]:
    """
    Create a standard set of sidebar filters.

    Returns:
        dict: Dictionary with filter values:
            - province: Selected province
            - year_range: Selected year range
            - data_type: Selected data type

    Example:
        >>> filters = create_sidebar_filters()
        >>> province = filters['province']
        >>> year_range = filters['year_range']
    """
    st.sidebar.header('Filters')

    province = province_filter(key='sidebar_province')
    year_range = year_filter(key='sidebar_year')
    data_type = data_type_filter(key='sidebar_data_type')

    return {
        'province': province,
        'year_range': year_range,
        'data_type': data_type
    }


def color_scale_selector(
    key: str = 'color_scale',
    default: str = 'Viridis'
) -> str:
    """
    Create a color scale selector for charts.

    Parameters:
        key (str): Unique key for Streamlit widget.
        default (str): Default color scale.

    Returns:
        str: Selected color scale name.

    Example:
        >>> color = color_scale_selector()
        >>> fig = px.bar(df, x='province', y='value', color_continuous_scale=color)
    """
    color_scales = [
        'Viridis', 'Plasma', 'Inferno', 'Magma', 'Cividis',
        'YlOrRd', 'YlGnBu', 'YlGn', 'Blues', 'Greens',
        'Reds', 'Purples', 'Oranges', 'Teal', 'Cyan'
    ]

    return st.selectbox(
        'Color Scale',
        options=color_scales,
        index=color_scales.index(default) if default in color_scales else 0,
        key=key,
        help='Select color scale for visualization'
    )


def chart_type_selector(
    key: str = 'chart_type',
    default: str = 'Bar'
) -> str:
    """
    Create a chart type selector.

    Parameters:
        key (str): Unique key for Streamlit widget.
        default (str): Default chart type.

    Returns:
        str: Selected chart type.

    Example:
        >>> chart_type = chart_type_selector()
        >>> if chart_type == 'Bar':
        ...     fig = create_bar_chart(df, x, y)
        >>> elif chart_type == 'Pie':
        ...     fig = create_pie_chart(df, values, names)
    """
    chart_types = ['Bar', 'Pie', 'Line', 'Area', 'Scatter']

    return st.radio(
        'Chart Type',
        options=chart_types,
        index=chart_types.index(default) if default in chart_types else 0,
        key=key,
        horizontal=True,
        help='Select visualization type'
    )


def download_button(
    data: pd.DataFrame,
    filename: str = 'data',
    key: str = 'download'
) -> None:
    """
    Create a download button for data export.

    Parameters:
        data (pd.DataFrame): Data to download.
        filename (str): Base filename (without extension).
        key (str): Unique key for Streamlit widget.

    Example:
        >>> download_button(filtered_data, 'population_data')
    """
    csv = data.to_csv(index=False).encode('utf-8')

    st.download_button(
        label='Download Data (CSV)',
        data=csv,
        file_name=f'{filename}.csv',
        mime='text/csv',
        key=key
    )