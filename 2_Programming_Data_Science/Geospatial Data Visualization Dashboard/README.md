# Geospatial Data Visualization Dashboard

A comprehensive interactive dashboard for visualizing geospatial data of Pakistan using Python, Streamlit, Plotly, and Folium.

## Features

- 🗺️ Interactive maps with multiple layers
- 📊 Dynamic charts and visualizations
- 🔍 Filtering capabilities by region, time, and data type
- 📈 Time series analysis
- 🏙️ Urban & rural data comparison
- 🌡️ Climate data visualization
- 👥 Population density mapping

## Tech Stack

- **Streamlit** - Web framework
- **Folium** - Interactive maps
- **Plotly** - Charts and graphs
- **GeoPandas** - Geospatial data handling
- **Pandas** - Data manipulation
- **NumPy** - Numerical operations

## Project Structure

```
Geospatial Data Visualization Dashboard/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── STEP_BY_STEP.md          # Detailed development guide
├── modules/
│   ├── __init__.py
│   ├── maps.py              # Map creation functions
│   ├── charts.py            # Chart creation functions
│   ├── data_loader.py       # Data loading utilities
│   └── filters.py           # Filtering components
├── data/
│   └── sample_data/         # Sample datasets
└── assets/
    └── styles.css           # Custom styling
```

## Quick Start

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Dashboard Sections

1. **Home** - Overview and key statistics
2. **Population Analysis** - Population density and distribution
3. **Climate Data** - Temperature and precipitation patterns
4. **Administrative Boundaries** - Province and district maps
5. **Time Series** - Temporal data analysis

## Author

**Haris Hussain** - GIS Analyst | Geospatial Data Specialist