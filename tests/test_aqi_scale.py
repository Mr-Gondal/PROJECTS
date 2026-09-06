"""Unit tests for the US EPA AQI conversion (Air Quality project).

These tests pin the exact behaviour that used to be a bug: concentrations
falling between EPA breakpoint bands (12.05, 35.45, ...) must interpolate
into the correct AQI band instead of returning AQI 0 ("Good").
"""

import importlib.util
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "2_Programming_Data_Science" / "Air_Quality_Analysis_Prediction" / "src" / "aqi_scale.py"

spec = importlib.util.spec_from_file_location("aqi_scale", MODULE_PATH)
aqi_scale = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aqi_scale)


class TestPm25Conversion:
    def test_band_gap_values_return_nonzero(self):
        # regression: these used to return AQI 0
        for value in (12.05, 35.45, 55.45, 150.45, 250.45):
            aqi = aqi_scale.pm25_to_aqi(value)
            assert aqi is not None and aqi > 0, f"pm2.5={value} gave {aqi}"

    def test_known_values(self):
        assert aqi_scale.pm25_to_aqi(0.0) == 0
        assert aqi_scale.pm25_to_aqi(9.0) == 50      # top of Good (2024 rule)
        assert aqi_scale.pm25_to_aqi(9.1) == 51      # bottom of Moderate
        assert aqi_scale.pm25_to_aqi(35.4) == 100    # top of Moderate
        assert aqi_scale.pm25_to_aqi(35.5) == 101    # bottom of USG
        assert aqi_scale.pm25_to_aqi(100.0) == 182   # 151 + (100-55.5)/(125.4-55.5)*49

    def test_truncation_not_rounding(self):
        # 35.46 truncates to 35.4 (Moderate), not rounds to 35.5 (USG)
        assert aqi_scale.pm25_to_aqi(35.46) == 100

    def test_above_scale_caps_at_500(self):
        assert aqi_scale.pm25_to_aqi(800.0) == 500
        assert aqi_scale.pm25_to_aqi(425.4) == 500

    def test_invalid_inputs_return_none(self):
        assert aqi_scale.pm25_to_aqi(None) is None
        assert aqi_scale.pm25_to_aqi(float("nan")) is None
        assert aqi_scale.pm25_to_aqi(-5.0) is None
        assert aqi_scale.pm25_to_aqi("junk") is None


class TestPm10Conversion:
    def test_band_edges(self):
        assert aqi_scale.pm10_to_aqi(54) == 50
        assert aqi_scale.pm10_to_aqi(55) == 51
        assert aqi_scale.pm10_to_aqi(154) == 100
        assert aqi_scale.pm10_to_aqi(155) == 101

    def test_gap_values_return_nonzero(self):
        assert aqi_scale.pm10_to_aqi(54.9) == 50     # truncates to 54
        assert aqi_scale.pm10_to_aqi(154.9) == 100   # truncates to 154

    def test_above_scale(self):
        assert aqi_scale.pm10_to_aqi(700) == 500


class TestCategory:
    def test_categories(self):
        assert aqi_scale.aqi_category(30)[0] == "Good"
        assert aqi_scale.aqi_category(75)[0] == "Moderate"
        assert aqi_scale.aqi_category(120)[0] == "Unhealthy (Sensitive)"
        assert aqi_scale.aqi_category(180)[0] == "Unhealthy"
        assert aqi_scale.aqi_category(250)[0] == "Very Unhealthy"
        assert aqi_scale.aqi_category(400)[0] == "Hazardous"
        assert aqi_scale.aqi_category(None)[0] == "No Data"

    def test_aqi_from_pollutant_only_for_scaled_pollutants(self):
        assert aqi_scale.aqi_from_pollutant("pm25", 35.4) == 100
        assert aqi_scale.aqi_from_pollutant("pm10", 54) == 50
        # gases have no implemented µg/m³→AQI scale here — must return None
        assert aqi_scale.aqi_from_pollutant("o3", 120) is None
        assert aqi_scale.aqi_from_pollutant("no2", 40) is None
