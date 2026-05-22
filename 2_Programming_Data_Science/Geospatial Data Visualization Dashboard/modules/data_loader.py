"""
Data Loader Module - Data Loading and Processing Utilities
===========================================================

This module provides functions for loading, generating, and processing data.
It includes sample data for Pakistan that can be used for demonstrations.

Key Features:
    - Province-level data for Pakistan
    - District-level data
    - Climate time series data
    - Economic indicators
    - GeoJSON generation for boundaries

Dependencies:
    - pandas
    - numpy
    - geopandas (optional, for shapefile handling)

Author: Haris Hussain - GIS Analyst | Geospatial Data Specialist
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta


def load_province_data() -> pd.DataFrame:
    """
    Load Pakistan province-level data.

    Returns:
        pd.DataFrame: DataFrame with province statistics including:
            - province: Province name
            - population: Total population
            - area_sqkm: Area in square kilometers
            - population_density: People per sq km
            - capital: Capital city
            - latitude: Center latitude
            - longitude: Center longitude
            - literacy_rate: Literacy percentage
            - gdp_contribution: GDP contribution percentage

    Example:
        >>> df = load_province_data()
        >>> print(df.head())
    """
    data = {
        'province': ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'AJK', 'Gilgit-Baltistan'],
        'population': [110000000, 48000000, 35000000, 12000000, 4000000, 1500000],
        'area_sqkm': [205344, 140914, 74521, 347190, 13432, 72520],
        'population_density': [536, 341, 470, 35, 298, 21],
        'capital': ['Lahore', 'Karachi', 'Peshawar', 'Quetta', 'Muzaffarabad', 'Gilgit'],
        'latitude': [31.5204, 24.8607, 34.0151, 30.1798, 34.3528, 35.9206],
        'longitude': [74.3587, 67.0011, 71.5805, 66.9747, 73.4653, 74.3587],
        'literacy_rate': [62.8, 58.5, 52.4, 44.5, 64.8, 58.0],
        'gdp_contribution': [53.2, 30.2, 13.5, 3.5, 2.1, 1.5],
        'major_cities': [
            ['Lahore', 'Faisalabad', 'Rawalpindi', 'Multan', 'Gujranwala'],
            ['Karachi', 'Hyderabad', 'Sukkur', 'Larkana', 'Nawabshah'],
            ['Peshawar', 'Mardan', 'Mingora', 'Kohat', 'Abbottabad'],
            ['Quetta', 'Turbat', 'Khuzdar', 'Chaman', 'Gwadar'],
            ['Muzaffarabad', 'Mirpur', 'Kotli', 'Bhimber', 'Rawalakot'],
            ['Gilgit', 'Skardu', 'Hunza', 'Ghizer', 'Ghanche']
        ]
    }
    return pd.DataFrame(data)


def load_district_data() -> pd.DataFrame:
    """
    Load Pakistan district-level data (sample of major districts).

    Returns:
        pd.DataFrame: DataFrame with district statistics including:
            - district: District name
            - province: Province it belongs to
            - population: District population
            - area_sqkm: Area in square km
            - latitude: District center latitude
            - longitude: District center longitude

    Example:
        >>> df = load_district_data()
        >>> print(df.head())
    """
    data = {
        'district': [
            'Lahore', 'Karachi', 'Faisalabad', 'Rawalpindi', 'Multan',
            'Peshawar', 'Quetta', 'Islamabad', 'Hyderabad', 'Gujranwala',
            'Multan', 'Bahawalpur', 'Sargodha', 'Sialkot', 'Sukkur',
            'Abbottabad', 'Mardan', 'Mingora', 'Muzaffarabad', 'Gilgit',
            'Sahiwal', 'Sheikhupura', 'Jhang', 'Kasur', 'Rahim Yar Khan',
            'Gujrat', 'Jhelum', 'Sialkot', 'Attock', 'Okara'
        ],
        'province': [
            'Punjab', 'Sindh', 'Punjab', 'Punjab', 'Punjab',
            'KPK', 'Balochistan', 'ICT', 'Sindh', 'Punjab',
            'Punjab', 'Punjab', 'Punjab', 'Punjab', 'Sindh',
            'KPK', 'KPK', 'KPK', 'AJK', 'Gilgit-Baltistan',
            'Punjab', 'Punjab', 'Punjab', 'Punjab', 'Punjab',
            'Punjab', 'Punjab', 'Punjab', 'Punjab', 'Punjab'
        ],
        'population': [
            11126763, 14910352, 3203829, 2091711, 1872966,
            1970042, 1001609, 1009816, 1843659, 1527696,
            1872966, 1619862, 1594375, 1455186, 1487218,
            1338592, 1599462, 1180381, 725000, 243000,
            2417000, 2100000, 1525000, 2900000, 1250000,
            2056366, 900000, 1525000, 847000, 1200000
        ],
        'area_sqkm': [
            1772, 3527, 5856, 5286, 3721,
            1257, 2653, 906, 2835, 3622,
            3721, 24830, 5165, 3016, 5165,
            1967, 1632, 1249, 2484, 72520,
            4198, 5960, 8809, 3995, 14891,
            3022, 2713, 3016, 2817, 4577
        ],
        'latitude': [
            31.5204, 24.8607, 31.4504, 33.5651, 30.1575,
            34.0151, 30.1798, 33.6844, 25.3960, 32.1617,
            30.1575, 29.3544, 32.0836, 32.4945, 27.7063,
            34.1466, 34.1982, 34.7857, 34.3528, 35.9206,
            30.6690, 31.7075, 31.3021, 31.1096, 28.4186,
            32.5741, 32.9358, 32.4945, 33.7732, 30.8075
        ],
        'longitude': [
            74.3587, 67.0011, 73.0754, 73.0169, 71.5249,
            71.5805, 66.9747, 73.0479, 68.3575, 74.1885,
            71.5249, 71.6941, 72.6851, 74.5314, 68.8594,
            73.2126, 72.0586, 72.3607, 73.4653, 74.3587,
            73.1054, 74.1968, 72.3101, 74.4500, 70.2992,
            74.0808, 73.7258, 74.5314, 72.3567, 73.4485
        ]
    }
    return pd.DataFrame(data)


def load_climate_data() -> pd.DataFrame:
    """
    Load climate time series data for Pakistan (2015-2024).

    Returns:
        pd.DataFrame: DataFrame with climate data including:
            - year: Year
            - avg_temp: Average temperature (°C)
            - max_temp: Maximum temperature
            - min_temp: Minimum temperature
            - rainfall: Annual rainfall (mm)
            - humidity: Average humidity (%)

    Example:
        >>> df = load_climate_data()
        >>> fig = px.line(df, x='year', y='avg_temp')
    """
    np.random.seed(42)  # For reproducibility
    years = list(range(2015, 2025))

    data = {
        'year': years,
        'avg_temp': [24.5, 24.8, 25.1, 24.7, 25.3, 25.6, 25.2, 25.8, 26.1, 26.4],
        'max_temp': [38.2, 38.5, 39.1, 38.7, 39.4, 39.8, 39.2, 40.1, 40.5, 41.0],
        'min_temp': [12.1, 11.8, 11.5, 12.3, 11.2, 10.9, 11.6, 10.8, 10.5, 10.2],
        'rainfall': [485, 492, 478, 510, 465, 445, 480, 425, 410, 398],
        'humidity': [58.5, 57.8, 59.2, 56.4, 55.1, 54.8, 56.2, 53.9, 52.5, 51.8],
        'extreme_events': [12, 15, 18, 14, 22, 28, 25, 32, 35, 38]
    }

    return pd.DataFrame(data)


def load_economic_data() -> pd.DataFrame:
    """
    Load economic indicators for Pakistan provinces.

    Returns:
        pd.DataFrame: DataFrame with economic data including:
            - province: Province name
            - gdp_billions: GDP in billions USD
            - agriculture: Agriculture contribution (%)
            - industry: Industry contribution (%)
            - services: Services contribution (%)
            - unemployment: Unemployment rate (%)
            - poverty_rate: Poverty rate (%)

    Example:
        >>> df = load_economic_data()
        >>> fig = px.bar(df, x='province', y='gdp_billions')
    """
    data = {
        'province': ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'AJK', 'Gilgit-Baltistan'],
        'gdp_billions': [185, 105, 47, 12, 7, 5],
        'agriculture': [24.5, 18.2, 22.1, 35.5, 28.3, 15.2],
        'industry': [28.1, 42.5, 25.8, 18.2, 15.4, 12.8],
        'services': [47.4, 39.3, 52.1, 46.3, 56.3, 72.0],
        'unemployment': [6.2, 8.5, 9.8, 7.4, 8.1, 5.5],
        'poverty_rate': [24.3, 31.2, 28.5, 42.1, 25.8, 21.4]
    }

    return pd.DataFrame(data)


def load_population_time_series() -> pd.DataFrame:
    """
    Load population time series data (2015-2024).

    Returns:
        pd.DataFrame: Population data by province over time.

    Example:
        >>> df = load_population_time_series()
        >>> fig = px.line(df, x='year', y='population', color='province')
    """
    provinces = ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'AJK', 'Gilgit-Baltistan']
    years = list(range(2015, 2025))

    base_populations = [98700000, 43000000, 28000000, 9500000, 3600000, 1200000]
    growth_rates = [0.019, 0.022, 0.025, 0.024, 0.018, 0.023]

    data = []
    for i, province in enumerate(provinces):
        pop = base_populations[i]
        for year in years:
            data.append({
                'province': province,
                'year': year,
                'population': int(pop),
                'growth_rate': growth_rates[i]
            })
            pop *= (1 + growth_rates[i])

    return pd.DataFrame(data)


def generate_sample_geojson() -> dict:
    """
    Generate a sample GeoJSON for Pakistan province boundaries.

    This creates simplified rectangular boundaries for demonstration.
    For actual use, replace with real shapefile data.

    Returns:
        dict: GeoJSON FeatureCollection.

    Example:
        >>> geojson = generate_sample_geojson()
        >>> # Use with folium.Choropleth
    """
    # Simplified province boundaries (rectangular approximation)
    province_bounds = {
        'Punjab': [[29.5, 69.0], [29.5, 75.5], [33.5, 75.5], [33.5, 69.0]],
        'Sindh': [[23.5, 66.5], [23.5, 71.5], [28.5, 71.5], [28.5, 66.5]],
        'KPK': [[32.5, 69.5], [32.5, 74.5], [36.5, 74.5], [36.5, 69.5]],
        'Balochistan': [[25.0, 61.0], [25.0, 70.0], [32.0, 70.0], [32.0, 61.0]],
        'AJK': [[33.0, 73.0], [33.0, 75.5], [35.5, 75.5], [35.5, 73.0]],
        'Gilgit-Baltistan': [[35.0, 72.0], [35.0, 77.0], [37.5, 77.0], [37.5, 72.0]]
    }

    features = []
    for province, coords in province_bounds.items():
        # Create polygon from coordinates
        polygon = coords + [coords[0]]  # Close the polygon

        feature = {
            'type': 'Feature',
            'properties': {
                'name': province,
                'id': province
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[[c[1], c[0]] for c in polygon]]
            }
        }
        features.append(feature)

    return {
        'type': 'FeatureCollection',
        'features': features
    }


def get_province_centroids() -> Dict[str, tuple]:
    """
    Get centroid coordinates for each province.

    Returns:
        dict: Dictionary mapping province names to (lat, lon) tuples.

    Example:
        >>> centroids = get_province_centroids()
        >>> lahore_coords = centroids['Punjab']
    """
    return {
        'Punjab': (31.5204, 74.3587),
        'Sindh': (25.8943, 68.5247),
        'KPK': (34.9527, 72.3317),
        'Balochistan': (28.4956, 65.1013),
        'AJK': (34.3528, 73.4653),
        'Gilgit-Baltistan': (35.9206, 74.3587),
        'ICT': (33.6844, 73.0479)
    }


def get_cities_data() -> pd.DataFrame:
    """
    Get major cities data for Pakistan.

    Returns:
        pd.DataFrame: Cities with coordinates and population.
    """
    data = {
        'city': [
            'Karachi', 'Lahore', 'Faisalabad', 'Rawalpindi', 'Multan',
            'Peshawar', 'Quetta', 'Islamabad', 'Gujranwala', 'Hyderabad',
            'Sialkot', 'Bahawalpur', 'Sargodha', 'Sukkur', 'Abbottabad'
        ],
        'province': [
            'Sindh', 'Punjab', 'Punjab', 'Punjab', 'Punjab',
            'KPK', 'Balochistan', 'ICT', 'Punjab', 'Sindh',
            'Punjab', 'Punjab', 'Punjab', 'Sindh', 'KPK'
        ],
        'population_2024': [
            16.5, 13.5, 3.8, 2.5, 2.2,
            2.1, 1.2, 1.4, 2.0, 2.0,
            1.7, 1.8, 1.7, 1.6, 1.4
        ],
        'latitude': [
            24.8607, 31.5204, 31.4504, 33.5651, 30.1575,
            34.0151, 30.1798, 33.6844, 32.1617, 25.3960,
            32.4945, 29.3544, 32.0836, 27.7063, 34.1466
        ],
        'longitude': [
            67.0011, 74.3587, 73.0754, 73.0169, 71.5249,
            71.5805, 66.9747, 73.0479, 74.1885, 68.3575,
            74.5314, 71.6941, 72.6851, 68.8594, 73.2126
        ]
    }

    return pd.DataFrame(data)


def get_summary_statistics() -> Dict:
    """
    Get summary statistics for Pakistan.

    Returns:
        dict: Summary statistics including total population, area, etc.
    """
    return {
        'total_population': 241499431,
        'total_area_sqkm': 881913,
        'population_growth_rate': 2.0,
        'literacy_rate': 58.9,
        'provinces': 4,
        'territories': 3,
        'districts': 154,
        'gdp_billions': 376,
        'gdp_growth_rate': 3.5,
        'urban_population_pct': 36.4,
        'rural_population_pct': 63.6
    }