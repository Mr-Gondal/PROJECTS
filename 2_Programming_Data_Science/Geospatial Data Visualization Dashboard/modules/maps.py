"""
Maps Module - Map Creation and Manipulation Functions
======================================================

This module provides functions for creating interactive maps using Folium.
All maps are optimized for Streamlit integration.

Key Features:
    - Base map creation with multiple tile options
    - Choropleth layers for regional data visualization
    - Marker clusters for point data
    - Heat maps for density visualization
    - Layer controls for map customization

Dependencies:
    - folium
    - streamlit_folium
    - geopandas

Author: Haris Hussain - GIS Analyst | Geospatial Data Specialist
"""

import folium
from folium.plugins import MarkerCluster, HeatMap, MeasureControl
from folium.features import GeoJson
import streamlit_folium as st_folium
from typing import List, Dict, Optional, Tuple
import json


def create_base_map(
    center: Tuple[float, float] = (30.3753, 69.3451),
    zoom_start: int = 5,
    tiles: str = 'OpenStreetMap',
    width: str = '100%',
    height: str = '500px'
) -> folium.Map:
    """
    Create a base map centered on Pakistan.

    Parameters:
        center (tuple): (latitude, longitude) center point. Default is Pakistan center.
        zoom_start (int): Initial zoom level. Default is 5.
        tiles (str): Map tile style. Options: 'OpenStreetMap', 'Stamen Terrain',
                     'Stamen Toner', 'CartoDB positron', 'CartoDB dark_matter'
        width (str): Map width in CSS format.
        height (str): Map height in CSS format.

    Returns:
        folium.Map: Base map object ready for layers.

    Example:
        >>> m = create_base_map(center=(31.5204, 74.3587), zoom_start=10)
        >>> # Map centered on Lahore
    """
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles=tiles,
        width=width,
        height=height
    )

    # Add scale control
    folium.plugins.MeasureControl(position='bottomleft').add_to(m)

    return m


def add_choropleth_layer(
    map_obj: folium.Map,
    geo_data: dict,
    data: dict,
    columns: List[str],
    key_on: str = 'feature.properties.name',
    fill_color: str = 'YlOrRd',
    fill_opacity: float = 0.7,
    line_opacity: float = 0.2,
    legend_name: str = 'Value',
    layer_name: str = 'Choropleth'
) -> folium.Map:
    """
    Add a choropleth layer to the map for regional data visualization.

    Parameters:
        map_obj (folium.Map): Map object to add layer to.
        geo_data (dict): GeoJSON data containing geometry.
        data (dict): Data dictionary with values to visualize.
        columns (list): [key_column, value_column] for data mapping.
        key_on (str): JSON path to match features with data.
        fill_color (str): Color scale. Options: 'BuGn', 'BuPu', 'GnBu', 'OrRd',
                          'PuBu', 'PuBuGn', 'PuRd', 'RdPu', 'YlGn', 'YlGnBu',
                          'YlOrBr', 'YlOrRd'
        fill_opacity (float): Opacity of fill color (0-1).
        line_opacity (float): Opacity of border lines (0-1).
        legend_name (str): Title for the legend.
        layer_name (str): Name for the layer control.

    Returns:
        folium.Map: Map with choropleth layer added.

    Example:
        >>> m = create_base_map()
        >>> m = add_choropleth_layer(
        ...     m, geo_data, province_data,
        ...     columns=['province', 'population'],
        ...     legend_name='Population by Province'
        ... )
    """
    choropleth = folium.Choropleth(
        geo_data=geo_data,
        data=data,
        columns=columns,
        key_on=key_on,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        line_opacity=line_opacity,
        legend_name=legend_name,
        name=layer_name
    )
    choropleth.add_to(map_obj)

    # Add tooltips
    folium.GeoJsonTooltip(fields=['name']).add_to(choropleth.geojson)

    return map_obj


def add_marker_cluster(
    map_obj: folium.Map,
    locations: List[Dict],
    popup_content: str = 'name',
    icon_color: str = 'blue',
    icon_icon: str = 'info-sign'
) -> folium.Map:
    """
    Add clustered markers to the map for point data visualization.

    Parameters:
        map_obj (folium.Map): Map object to add markers to.
        locations (list): List of dictionaries with 'coords' (lat, lon) and
                          other properties for popups.
        popup_content (str): Key in location dict to display in popup.
        icon_color (str): Marker icon color. Options: 'red', 'blue', 'green',
                          'purple', 'orange', 'darkred', 'lightred', 'beige',
                          'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
                          'white', 'pink', 'lightblue', 'lightgreen', 'gray',
                          'black', 'lightgray'
        icon_icon (str): FontAwesome icon name.

    Returns:
        folium.Map: Map with marker clusters added.

    Example:
        >>> locations = [
        ...     {'coords': (31.5204, 74.3587), 'name': 'Lahore', 'pop': '11M'},
        ...     {'coords': (24.8607, 67.0011), 'name': 'Karachi', 'pop': '15M'}
        ... ]
        >>> m = add_marker_cluster(m, locations)
    """
    marker_cluster = MarkerCluster(name='Markers')

    for loc in locations:
        coords = loc.get('coords', (0, 0))
        popup = loc.get(popup_content, 'Location')

        # Create detailed popup HTML
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin: 0; color: #333;">{loc.get('name', 'Unknown')}</h4>
            <p style="margin: 5px 0;"><b>Population:</b> {loc.get('pop', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>Coordinates:</b> {coords[0]:.4f}, {coords[1]:.4f}</p>
        </div>
        """

        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=icon_color, icon=icon_icon)
        ).add_to(marker_cluster)

    marker_cluster.add_to(map_obj)
    return map_obj


def add_heatmap(
    map_obj: folium.Map,
    data: List[List[float]],
    radius: int = 15,
    blur: int = 25,
    max_zoom: int = 13,
    name: str = 'Heat Map'
) -> folium.Map:
    """
    Add a heat map layer for density visualization.

    Parameters:
        map_obj (folium.Map): Map object to add heatmap to.
        data (list): List of [latitude, longitude, weight] points.
        radius (int): Radius of each "point" in heatmap.
        blur (int): Amount of blur for smoother visualization.
        max_zoom (int): Maximum zoom level for heatmap intensity.
        name (str): Layer name for control.

    Returns:
        folium.Map: Map with heatmap layer added.

    Example:
        >>> # Population density heat map
        >>> heat_data = [
        ...     [31.5204, 74.3587, 0.8],  # Lahore (high density)
        ...     [24.8607, 67.0011, 1.0],  # Karachi (highest)
        ...     [30.1798, 66.9747, 0.1]   # Quetta (low density)
        ... ]
        >>> m = add_heatmap(m, heat_data)
    """
    HeatMap(
        data,
        radius=radius,
        blur=blur,
        max_zoom=max_zoom,
        name=name
    ).add_to(map_obj)

    return map_obj


def add_layer_control(map_obj: folium.Map) -> folium.Map:
    """
    Add layer control widget to toggle map layers.

    Parameters:
        map_obj (folium.Map): Map object to add control to.

    Returns:
        folium.Map: Map with layer control added.

    Example:
        >>> m = create_base_map()
        >>> m = add_choropleth_layer(m, ...)
        >>> m = add_marker_cluster(m, ...)
        >>> m = add_layer_control(m)
    """
    folium.LayerControl().add_to(map_obj)
    return map_obj


def add_tile_layers(map_obj: folium.Map) -> folium.Map:
    """
    Add multiple tile layer options to the map.

    Parameters:
        map_obj (folium.Map): Map object to add tiles to.

    Returns:
        folium.Map: Map with multiple tile options.
    """
    tiles = {
        'OpenStreetMap': 'OpenStreetMap',
        'Stamen Terrain': 'Stamen Terrain',
        'Stamen Toner': 'Stamen Toner',
        'CartoDB Positron': 'cartodbpositron',
        'CartoDB Dark': 'cartodbdark_matter'
    }

    for name, tile in tiles.items():
        folium.TileLayer(tile, name=name).add_to(map_obj)

    return map_obj


def display_map(map_obj: folium.Map, height: int = 600) -> None:
    """
    Display Folium map in Streamlit.

    Parameters:
        map_obj (folium.Map): Map object to display.
        height (int): Height of the map in pixels.

    Returns:
        None: Displays map in Streamlit app.
    """
    st_folium.st_folium(map_obj, height=height)


# Pakistan Province Centers for Reference
PAKISTAN_PROVINCE_CENTERS = {
    'Punjab': (31.5204, 74.3587),
    'Sindh': (25.8943, 68.5247),
    'KPK': (34.9527, 72.3317),
    'Balochistan': (28.4956, 65.1013),
    'AJK': (34.3528, 73.4653),
    'Gilgit-Baltistan': (35.9206, 74.3587)
}


def get_province_center(province_name: str) -> Tuple[float, float]:
    """
    Get the center coordinates for a Pakistan province.

    Parameters:
        province_name (str): Name of the province.

    Returns:
        tuple: (latitude, longitude) of province center.
    """
    return PAKISTAN_PROVINCE_CENTERS.get(
        province_name,
        (30.3753, 69.3451)  # Default to Pakistan center
    )