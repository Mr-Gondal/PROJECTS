"""
Geospatial Data Visualization Dashboard for Pakistan
====================================================

A comprehensive interactive dashboard for visualizing geospatial and
statistical data about Pakistan using Streamlit, Plotly, and Folium.

Features:
    - Interactive maps with multiple layers
    - Dynamic charts and visualizations
    - Filtering by province, year, and data type
    - Time series analysis
    - Export functionality

Author: Haris Hussain - GIS Analyst | Geospatial Data Specialist

Usage:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any

# Import local modules
from modules import (
    # Data loaders
    load_province_data,
    load_district_data,
    load_climate_data,
    load_economic_data,
    load_population_time_series,
    get_cities_data,
    get_summary_statistics,
    generate_sample_geojson,
    # Map functions
    create_base_map,
    add_choropleth_layer,
    add_marker_cluster,
    add_layer_control,
    get_province_center,
    # Chart functions
    create_bar_chart,
    create_pie_chart,
    create_line_chart,
    create_scatter_geo,
    create_area_chart,
    # Filter functions
    province_filter,
    year_filter,
    data_type_filter,
    apply_filters,
    color_scale_selector
)

# Third-party imports
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Pakistan Geospatial Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-top: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e7f3ff;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA LOADING (CACHED)
# =============================================================================

@st.cache_data
def load_all_data() -> Dict[str, pd.DataFrame]:
    """Load all datasets and cache them."""
    return {
        'provinces': load_province_data(),
        'districts': load_district_data(),
        'climate': load_climate_data(),
        'economic': load_economic_data(),
        'population_ts': load_population_time_series(),
        'cities': get_cities_data(),
        'geojson': generate_sample_geojson()
    }


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

def render_sidebar() -> str:
    """Render sidebar with navigation and filters."""
    st.sidebar.markdown('<p class="sidebar-header">Navigation</p>', unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Go to",
        ["🏠 Home", "🗺️ Maps", "📊 Charts", "📈 Time Series", "💰 Economy", "🌡️ Climate", "ℹ️ About"],
        key='main_navigation'
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="sidebar-header">Filters</p>', unsafe_allow_html=True)

    return page


def render_filters() -> Dict[str, Any]:
    """Render filter widgets in sidebar."""
    province = province_filter(key='main_province_filter')
    year_start, year_end = year_filter(min_year=2015, max_year=2024, key='main_year_filter')
    data_type = data_type_filter(key='main_data_type_filter')
    color_scale = color_scale_selector(key='main_color_scale')

    return {
        'province': province,
        'year_range': (year_start, year_end),
        'data_type': data_type,
        'color_scale': color_scale
    }


# =============================================================================
# PAGE: HOME
# =============================================================================

def render_home(data: Dict[str, pd.DataFrame]) -> None:
    """Render the home page with overview statistics."""
    st.markdown('<h1 class="main-header">🇵🇰 Pakistan Geospatial Dashboard</h1>', unsafe_allow_html=True)

    st.markdown("""
    Welcome to the **Pakistan Geospatial Data Visualization Dashboard**. This interactive
    platform provides comprehensive insights into Pakistan's demographic, economic, climate,
    and geographic data.
    """)

    # Key Statistics
    st.markdown('<h2 class="sub-header">Key Statistics</h2>', unsafe_allow_html=True)

    stats = get_summary_statistics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Population", f"{stats['total_population']/1e6:.0f}M", "+2.0%")
    with col2:
        st.metric("Total Area", f"{stats['total_area_sqkm']:,} km²", "N/A")
    with col3:
        st.metric("GDP", f"${stats['gdp_billions']}B", "+3.5%")
    with col4:
        st.metric("Literacy Rate", f"{stats['literacy_rate']}%", "+1.2%")

    st.markdown("---")

    # Quick Overview Charts
    st.markdown('<h2 class="sub-header">Quick Overview</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Population by Province
        fig_pop = create_pie_chart(
            data['provinces'],
            values='population',
            names='province',
            title='Population Distribution by Province',
            hole=0.4
        )
        st.plotly_chart(fig_pop, use_container_width=True)

    with col2:
        # GDP Contribution
        fig_gdp = create_bar_chart(
            data['provinces'],
            x='province',
            y='gdp_contribution',
            title='GDP Contribution by Province (%)',
            color='gdp_contribution',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_gdp, use_container_width=True)

    # Province Summary Table
    st.markdown('<h2 class="sub-header">Province Summary</h2>', unsafe_allow_html=True)

    df_display = data['provinces'][['province', 'population', 'area_sqkm', 'population_density', 'literacy_rate']].copy()
    df_display['population'] = df_display['population'].apply(lambda x: f"{x/1e6:.1f}M")
    df_display['area_sqkm'] = df_display['area_sqkm'].apply(lambda x: f"{x:,}")
    df_display.columns = ['Province', 'Population', 'Area (km²)', 'Density (per km²)', 'Literacy Rate (%)']

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Info box
    st.markdown("""
    <div class="info-box">
        <strong>📊 Dashboard Features:</strong>
        <ul>
            <li><b>Maps:</b> Interactive maps with province boundaries and city markers</li>
            <li><b>Charts:</b> Population, economy, and demographic visualizations</li>
            <li><b>Time Series:</b> Historical trends and projections</li>
            <li><b>Climate:</b> Temperature and rainfall data analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE: MAPS
# =============================================================================

def render_maps(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render the maps page with interactive maps."""
    st.markdown('<h1 class="main-header">🗺️ Interactive Maps</h1>', unsafe_allow_html=True)

    # Map Type Selector
    map_type = st.radio(
        "Select Map Type",
        ["Province Choropleth", "City Markers", "Population Heat Map"],
        horizontal=True,
        key='map_type_selector'
    )

    st.markdown("---")

    if map_type == "Province Choropleth":
        render_choropleth_map(data, filters)
    elif map_type == "City Markers":
        render_marker_map(data)
    else:
        render_heatmap(data)


def render_choropleth_map(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render choropleth map with province coloring."""
    st.subheader("Province Choropleth Map")

    # Metric selector
    metric = st.selectbox(
        "Select Metric to Display",
        options=['population', 'population_density', 'literacy_rate', 'gdp_contribution'],
        key='choropleth_metric'
    )

    metric_labels = {
        'population': 'Population',
        'population_density': 'Population Density (per km²)',
        'literacy_rate': 'Literacy Rate (%)',
        'gdp_contribution': 'GDP Contribution (%)'
    }

    # Create base map
    m = create_base_map(center=(30.3753, 69.3451), zoom_start=5)

    # Add choropleth layer
    choropleth = folium.Choropleth(
        geo_data=data['geojson'],
        data=data['provinces'],
        columns=['province', metric],
        key_on='feature.properties.name',
        fill_color=filters['color_scale'],
        fill_opacity=0.7,
        line_opacity=0.8,
        line_weight=2,
        legend_name=metric_labels.get(metric, metric),
        name='Province Data'
    )
    choropleth.add_to(m)

    # Add tooltips
    folium.GeoJson(
        data['geojson'],
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
        tooltip=folium.GeoJsonTooltip(
            fields=['name'],
            aliases=['Province:'],
            localize=True
        )
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Display map
    st_folium(m, width='100%', height=600)

    # Legend/Info
    st.markdown(f"""
    <div class="info-box">
        <strong>Map shows:</strong> {metric_labels.get(metric, metric)} by province.
        <br>Darker colors indicate higher values.
    </div>
    """, unsafe_allow_html=True)


def render_marker_map(data: Dict[str, pd.DataFrame]) -> None:
    """Render map with city markers."""
    st.subheader("Major Cities of Pakistan")

    # Create base map
    m = create_base_map(center=(30.3753, 69.3451), zoom_start=5, tiles='CartoDB positron')

    # Prepare marker data
    locations = []
    for _, row in data['cities'].iterrows():
        locations.append({
            'coords': (row['latitude'], row['longitude']),
            'name': row['city'],
            'pop': f"{row['population_2024']}M",
            'province': row['province']
        })

    # Add marker cluster
    m = add_marker_cluster(m, locations, icon_color='blue', icon_icon='map-marker')

    # Add layer control
    folium.LayerControl().add_to(m)

    # Display map
    st_folium(m, width='100%', height=600)


def render_heatmap(data: Dict[str, pd.DataFrame]) -> None:
    """Render population density heatmap."""
    st.subheader("Population Density Heat Map")

    # Create base map
    m = create_base_map(center=(30.3753, 69.3451), zoom_start=5)

    # Prepare heat data
    heat_data = []
    for _, row in data['cities'].iterrows():
        # Weight by population
        heat_data.append([row['latitude'], row['longitude'], row['population_2024']])

    # Add heatmap
    from folium.plugins import HeatMap
    HeatMap(heat_data, radius=20, blur=15, max_zoom=10).add_to(m)

    # Display map
    st_folium(m, width='100%', height=600)

    st.info("Heat map shows population concentration. Brighter areas indicate higher population density.")


# =============================================================================
# PAGE: CHARTS
# =============================================================================

def render_charts(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render the charts page with various visualizations."""
    st.markdown('<h1 class="main-header">📊 Charts & Visualizations</h1>', unsafe_allow_html=True)

    chart_section = st.radio(
        "Select Chart Section",
        ["Population Analysis", "Area Comparison", "Literacy & Economy"],
        horizontal=True,
        key='chart_section'
    )

    st.markdown("---")

    if chart_section == "Population Analysis":
        render_population_charts(data, filters)
    elif chart_section == "Area Comparison":
        render_area_charts(data, filters)
    else:
        render_economy_charts(data, filters)


def render_population_charts(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render population-related charts."""
    df = data['provinces']

    # Filter by province if selected
    if filters['province'] != 'All':
        df = df[df['province'] == filters['province']]

    col1, col2 = st.columns(2)

    with col1:
        # Population Bar Chart
        fig_bar = create_bar_chart(
            df,
            x='province',
            y='population',
            title='Population by Province',
            color='population',
            color_continuous_scale=filters['color_scale']
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Population Pie Chart
        fig_pie = create_pie_chart(
            df,
            values='population',
            names='province',
            title='Population Distribution',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Population Density
    st.markdown('<h2 class="sub-header">Population Density</h2>', unsafe_allow_html=True)

    fig_density = create_bar_chart(
        data['provinces'],
        x='province',
        y='population_density',
        title='Population Density (people per km²)',
        color='population_density',
        color_continuous_scale='YlOrRd',
        orientation='v'
    )
    st.plotly_chart(fig_density, use_container_width=True)


def render_area_charts(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render area-related charts."""
    col1, col2 = st.columns(2)

    with col1:
        # Area Bar Chart
        fig_area = create_bar_chart(
            data['provinces'],
            x='province',
            y='area_sqkm',
            title='Area by Province (km²)',
            color='area_sqkm',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with col2:
        # Area Pie Chart
        fig_pie = create_pie_chart(
            data['provinces'],
            values='area_sqkm',
            names='province',
            title='Area Distribution',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)


def render_economy_charts(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render economy and literacy charts."""
    col1, col2 = st.columns(2)

    with col1:
        # Literacy Rate
        fig_lit = create_bar_chart(
            data['provinces'],
            x='province',
            y='literacy_rate',
            title='Literacy Rate by Province (%)',
            color='literacy_rate',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_lit, use_container_width=True)

    with col2:
        # GDP Contribution
        fig_gdp = create_pie_chart(
            data['provinces'],
            values='gdp_contribution',
            names='province',
            title='GDP Contribution Distribution',
            hole=0.4
        )
        st.plotly_chart(fig_gdp, use_container_width=True)

    # Economic Indicators
    st.markdown('<h2 class="sub-header">Economic Indicators</h2>', unsafe_allow_html=True)

    df_econ = data['economic']

    col1, col2 = st.columns(2)

    with col1:
        # Unemployment Rate
        fig_unemp = create_bar_chart(
            df_econ,
            x='province',
            y='unemployment',
            title='Unemployment Rate (%)',
            color='unemployment',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_unemp, use_container_width=True)

    with col2:
        # Poverty Rate
        fig_pov = create_bar_chart(
            df_econ,
            x='province',
            y='poverty_rate',
            title='Poverty Rate (%)',
            color='poverty_rate',
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig_pov, use_container_width=True)


# =============================================================================
# PAGE: TIME SERIES
# =============================================================================

def render_time_series(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render time series analysis page."""
    st.markdown('<h1 class="main-header">📈 Time Series Analysis</h1>', unsafe_allow_html=True)

    df = data['population_ts']

    # Apply year filter
    year_start, year_end = filters['year_range']
    df = df[(df['year'] >= year_start) & (df['year'] <= year_end)]

    # Apply province filter
    if filters['province'] != 'All':
        df = df[df['province'] == filters['province']]

    st.markdown(f"""
    <div class="info-box">
        Showing population trends from <strong>{year_start}</strong> to <strong>{year_end}</strong>.
        {f"Filtered to: <strong>{filters['province']}</strong>" if filters['province'] != 'All' else ""}
    </div>
    """, unsafe_allow_html=True)

    # Population Over Time
    st.markdown('<h2 class="sub-header">Population Growth Trend</h2>', unsafe_allow_html=True)

    fig_line = create_line_chart(
        df,
        x='year',
        y='population',
        title='Population Growth by Province',
        color='province',
        markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Growth Rate Comparison
    st.markdown('<h2 class="sub-header">Growth Rate Comparison</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Bar chart for growth rates
        growth_df = data['provinces'][['province', 'population']].copy()
        growth_df['growth_rate'] = ['1.9%', '2.2%', '2.5%', '2.4%', '1.8%', '2.3%']

        fig_growth = create_bar_chart(
            growth_df,
            x='province',
            y='population',
            title='Population with Growth Rate',
            color='population',
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig_growth, use_container_width=True)

    with col2:
        # Population projection
        years_future = list(range(2024, 2031))
        projection_data = []

        for _, row in data['provinces'].iterrows():
            pop = row['population']
            rate = float(dict(zip(['Punjab', 'Sindh', 'KPK', 'Balochistan', 'AJK', 'Gilgit-Baltistan'],
                                   [0.019, 0.022, 0.025, 0.024, 0.018, 0.023]))[row['province']])
            for year in years_future:
                pop = pop * (1 + rate)
                projection_data.append({
                    'province': row['province'],
                    'year': year,
                    'population': pop
                })

        proj_df = pd.DataFrame(projection_data)

        fig_proj = create_line_chart(
            proj_df,
            x='year',
            y='population',
            title='Population Projection (2024-2030)',
            color='province'
        )
        st.plotly_chart(fig_proj, use_container_width=True)


# =============================================================================
# PAGE: ECONOMY
# =============================================================================

def render_economy(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render economy page."""
    st.markdown('<h1 class="main-header">💰 Economic Analysis</h1>', unsafe_allow_html=True)

    df = data['economic']

    # Sector-wise GDP Contribution
    st.markdown('<h2 class="sub-header">Sector-wise GDP Contribution</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Agriculture Avg", f"{df['agriculture'].mean():.1f}%", "Primary Sector")
    with col2:
        st.metric("Industry Avg", f"{df['industry'].mean():.1f}%", "Secondary Sector")
    with col3:
        st.metric("Services Avg", f"{df['services'].mean():.1f}%", "Tertiary Sector")

    # Stacked Bar Chart
    st.markdown("---")

    fig_sector = go.Figure()

    fig_sector.add_trace(go.Bar(
        name='Agriculture',
        x=df['province'],
        y=df['agriculture'],
        marker_color='#2ecc71'
    ))
    fig_sector.add_trace(go.Bar(
        name='Industry',
        x=df['province'],
        y=df['industry'],
        marker_color='#3498db'
    ))
    fig_sector.add_trace(go.Bar(
        name='Services',
        x=df['province'],
        y=df['services'],
        marker_color='#9b59b6'
    ))

    fig_sector.update_layout(
        barmode='stack',
        title='Economic Sector Distribution by Province',
        xaxis_title='Province',
        yaxis_title='Contribution (%)',
        template='plotly_white'
    )

    st.plotly_chart(fig_sector, use_container_width=True)

    # GDP and Economic Indicators
    col1, col2 = st.columns(2)

    with col1:
        fig_gdp = create_bar_chart(
            df,
            x='province',
            y='gdp_billions',
            title='GDP by Province (Billion USD)',
            color='gdp_billions',
            color_continuous_scale='Teal'
        )
        st.plotly_chart(fig_gdp, use_container_width=True)

    with col2:
        fig_unemp = create_bar_chart(
            df,
            x='province',
            y='unemployment',
            title='Unemployment Rate (%)',
            color='unemployment',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_unemp, use_container_width=True)


# =============================================================================
# PAGE: CLIMATE
# =============================================================================

def render_climate(data: Dict[str, pd.DataFrame], filters: Dict[str, Any]) -> None:
    """Render climate data page."""
    st.markdown('<h1 class="main-header">🌡️ Climate Analysis</h1>', unsafe_allow_html=True)

    df = data['climate']

    # Apply year filter
    year_start, year_end = filters['year_range']
    df = df[(df['year'] >= year_start) & (df['year'] <= year_end)]

    # Key Climate Metrics
    col1, col2, col3, col4 = st.columns(4)

    avg_temp = df['avg_temp'].mean()
    avg_rainfall = df['rainfall'].mean()
    avg_humidity = df['humidity'].mean()
    temp_trend = "↑ Increasing" if df['avg_temp'].iloc[-1] > df['avg_temp'].iloc[0] else "↓ Decreasing"

    with col1:
        st.metric("Avg Temperature", f"{avg_temp:.1f}°C", temp_trend)
    with col2:
        st.metric("Avg Rainfall", f"{avg_rainfall:.0f} mm", "Annual")
    with col3:
        st.metric("Avg Humidity", f"{avg_humidity:.1f}%", "Relative")
    with col4:
        st.metric("Extreme Events", f"{df['extreme_events'].max()}", "Max Annual")

    st.markdown("---")

    # Temperature Trend
    st.markdown('<h2 class="sub-header">Temperature Trend</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_temp = create_line_chart(
            df,
            x='year',
            y='avg_temp',
            title='Average Temperature Trend',
            markers=True,
            show_range_slider=False
        )
        fig_temp.update_traces(line=dict(color='#e74c3c', width=3))
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        fig_temp_range = go.Figure()

        fig_temp_range.add_trace(go.Scatter(
            x=df['year'],
            y=df['max_temp'],
            fill=None,
            mode='lines',
            line=dict(color='rgba(231, 76, 60, 0.2)'),
            name='Max Temperature'
        ))
        fig_temp_range.add_trace(go.Scatter(
            x=df['year'],
            y=df['min_temp'],
            fill='tonexty',
            mode='lines',
            line=dict(color='rgba(52, 152, 219, 0.2)'),
            name='Min Temperature'
        ))
        fig_temp_range.add_trace(go.Scatter(
            x=df['year'],
            y=df['avg_temp'],
            mode='lines+markers',
            line=dict(color='#2c3e50', width=2),
            name='Avg Temperature'
        ))

        fig_temp_range.update_layout(
            title='Temperature Range Over Time',
            xaxis_title='Year',
            yaxis_title='Temperature (°C)',
            template='plotly_white'
        )

        st.plotly_chart(fig_temp_range, use_container_width=True)

    # Rainfall Trend
    st.markdown('<h2 class="sub-header">Rainfall Pattern</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_rain = create_area_chart(
            df,
            x='year',
            y='rainfall',
            title='Annual Rainfall Trend',
            color='rainfall'
        )
        st.plotly_chart(fig_rain, use_container_width=True)

    with col2:
        fig_humidity = create_line_chart(
            df,
            x='year',
            y='humidity',
            title='Humidity Trend',
            markers=True
        )
        fig_humidity.update_traces(line=dict(color='#3498db', width=3))
        st.plotly_chart(fig_humidity, use_container_width=True)

    # Climate Change Indicator
    st.markdown('<h2 class="sub-header">Climate Change Indicators</h2>', unsafe_allow_html=True)

    fig_events = create_bar_chart(
        df,
        x='year',
        y='extreme_events',
        title='Extreme Weather Events per Year',
        color='extreme_events',
        color_continuous_scale='YlOrRd'
    )
    st.plotly_chart(fig_events, use_container_width=True)

    st.warning("⚠️ Notice the increasing trend in extreme weather events, correlating with rising temperatures.")


# =============================================================================
# PAGE: ABOUT
# =============================================================================

def render_about() -> None:
    """Render about page."""
    st.markdown('<h1 class="main-header">ℹ️ About This Dashboard</h1>', unsafe_allow_html=True)

    st.markdown("""
    ## Pakistan Geospatial Data Visualization Dashboard

    This interactive dashboard provides comprehensive visualization and analysis of geospatial
    and statistical data for Pakistan.

    ### 🎯 Purpose

    - Visualize Pakistan's demographic, economic, and climate data
    - Provide interactive maps for geographic analysis
    - Enable time series analysis of key indicators
    - Support decision-making with data-driven insights

    ### 📊 Data Sources

    - Population data: Pakistan Bureau of Statistics
    - Climate data: Pakistan Meteorological Department
    - Economic data: Ministry of Finance
    - Geographic data: Survey of Pakistan

    ### 🛠️ Technologies Used

    | Technology | Purpose |
    |------------|---------|
    | **Streamlit** | Web framework |
    | **Plotly** | Interactive charts |
    | **Folium** | Interactive maps |
    | **Pandas** | Data manipulation |
    | **GeoPandas** | Geospatial data |

    ### 📁 Project Structure

    ```
    Geospatial Data Visualization Dashboard/
    ├── app.py                    # Main application
    ├── modules/                  # Modular components
    │   ├── maps.py              # Map functions
    │   ├── charts.py            # Chart functions
    │   ├── data_loader.py       # Data loading
    │   └── filters.py           # Filter components
    ├── data/                    # Data files
    ├── requirements.txt         # Dependencies
    └── README.md               # Documentation
    ```

    ### 🚀 Getting Started

    1. Install dependencies: `pip install -r requirements.txt`
    2. Run the app: `streamlit run app.py`
    3. Open browser: `http://localhost:8501`

    ### 👨‍💻 Author

    **Haris Hussain**
    - GIS Analyst | Geospatial Data Specialist
    - Specializing in Remote Sensing, WebGIS, and Data Visualization

    ### 📄 License

    This project is created for educational and portfolio purposes.

    ---

    *Last updated: 2024*
    """)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application function."""
    # Load data
    data = load_all_data()

    # Render sidebar and get navigation
    page = render_sidebar()

    # Render filters
    filters = render_filters()

    # Route to appropriate page
    if page == "🏠 Home":
        render_home(data)
    elif page == "🗺️ Maps":
        render_maps(data, filters)
    elif page == "📊 Charts":
        render_charts(data, filters)
    elif page == "📈 Time Series":
        render_time_series(data, filters)
    elif page == "💰 Economy":
        render_economy(data, filters)
    elif page == "🌡️ Climate":
        render_climate(data, filters)
    else:
        render_about()


if __name__ == "__main__":
    main()