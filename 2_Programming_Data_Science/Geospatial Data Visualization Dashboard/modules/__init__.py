"""
Geospatial Dashboard Modules
============================

This package contains modular components for the Geospatial Dashboard.

Modules:
    - maps: Map creation and manipulation functions
    - charts: Chart and graph creation functions
    - data_loader: Data loading and processing utilities
    - filters: Streamlit filter components

Author: Haris Hussain - GIS Analyst | Geospatial Data Specialist
"""

from .maps import (
    create_base_map,
    add_choropleth_layer,
    add_marker_cluster,
    add_heatmap,
    add_layer_control
)

from .charts import (
    create_bar_chart,
    create_pie_chart,
    create_line_chart,
    create_scatter_geo,
    create_area_chart
)

from .data_loader import (
    load_province_data,
    load_district_data,
    load_climate_data,
    load_economic_data,
    load_population_time_series,
    get_cities_data,
    get_summary_statistics,
    generate_sample_geojson
)

from .filters import (
    province_filter,
    year_filter,
    data_type_filter,
    apply_filters,
    color_scale_selector
)

__all__ = [
    # Maps
    'create_base_map',
    'add_choropleth_layer',
    'add_marker_cluster',
    'add_heatmap',
    'add_layer_control',

    # Charts
    'create_bar_chart',
    'create_pie_chart',
    'create_line_chart',
    'create_scatter_geo',
    'create_area_chart',

    # Data
    'load_province_data',
    'load_district_data',
    'load_climate_data',
    'load_economic_data',
    'load_population_time_series',
    'get_cities_data',
    'get_summary_statistics',
    'generate_sample_geojson',

    # Filters
    'province_filter',
    'year_filter',
    'data_type_filter',
    'apply_filters',
    'color_scale_selector'
]