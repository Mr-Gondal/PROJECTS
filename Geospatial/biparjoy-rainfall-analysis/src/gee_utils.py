"""Google Earth Engine helpers for GPM IMERG rainfall extraction."""

import ee


def initialize_ee():
    """Initialize Earth Engine, prompting authentication when needed."""
    try:
        ee.Initialize()
    except Exception:
        ee.Authenticate()
        ee.Initialize()


def imerg_collection(start_date, end_date):
    """Return GPM IMERG half-hourly precipitation images for a date range."""
    return (
        ee.ImageCollection("NASA/GPM_L3/IMERG_V06")
        .filterDate(start_date, end_date)
        .select("precipitationCal")
    )


def rainfall_sum(start_date, end_date, region):
    """Return accumulated IMERG precipitation clipped to a region."""
    return imerg_collection(start_date, end_date).sum().clip(region)
