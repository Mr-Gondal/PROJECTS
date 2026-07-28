"""Track kinematics and spatial helper functions."""

from math import atan2, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lon1, lat1, lon2, lat2):
    """Calculate great-circle distance between two lon/lat points."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * atan2(sqrt(a), sqrt(1 - a))


def translation_speed_kmh(distance_km, hours):
    """Calculate storm translation speed in km/h."""
    return distance_km / hours if hours else None
