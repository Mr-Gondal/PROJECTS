# Agricultural Crop Health Monitoring using NDVI

**Author:** Haris Hussain  
**Institution:** University of the Punjab, Lahore — Space Science  
**Date:** 2025  
**Platform:** Google Earth Engine (JavaScript API)  
**Satellite:** Sentinel-2 (10 m resolution)

---

## Overview

This project implements a remote sensing workflow on Google Earth Engine (GEE) to monitor agricultural crop health in the Punjab region of Pakistan using the Normalized Difference Vegetation Index (NDVI). Punjab is the breadbasket of Pakistan, contributing over 50% of the country's food grain production. Monitoring crop health at scale is critical for food security, irrigation scheduling, fertilizer management, and early detection of pest or water stress.

The script ingests Sentinel-2 Harmonized Surface Reflectance imagery over a user-defined area of interest (AOI), applies cloud masking, calculates NDVI and additional vegetation indices (EVI, NDRE, SAVI), generates monthly NDVI composites, classifies crop health into five categories (stressed to very healthy), detects NDVI anomalies as stress indicators, and exports GeoTIFF rasters and CSV statistics to Google Drive. Seasonal composites for Kharif (monsoon) and Rabi (winter) growing seasons are also supported.

This project demonstrates end-to-end proficiency in satellite image processing, vegetation index theory, time series analysis, and geospatial data export — all within the GEE JavaScript environment.

---

## Data Sources

| Dataset | Source | Resolution | Bands Used | Purpose |
|---------|--------|-----------|------------|---------|
| Sentinel-2 MSI Surface Reflectance (Harmonized) | [COPERNICUS/S2_SR_HARMONIZED](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED) | 10 m (B2, B3, B4, B8) / 20 m (B5, B8A, QA60) | B2 (Blue), B4 (Red), B5 (Red Edge), B8 (NIR), B8A (Narrow NIR), QA60 (Cloud mask) | NDVI, EVI, NDRE, SAVI, cloud masking |

---

## Methodology

1. **Data Acquisition** — Load the Sentinel-2 SR Harmonized collection, filter by AOI bounds and date range, and discard scenes with >20% cloud cover.
2. **Cloud Masking** — Apply a bitmask on the QA60 band (bits 10 and 11) to remove cloud and cirrus pixels.
3. **NDVI Calculation** — Compute NDVI per scene using the normalized difference between NIR (B8) and Red (B4).
4. **Additional Indices** — Compute EVI, NDRE, and SAVI for multi-index vegetation analysis.
5. **Time Series & Monthly Composites** — Generate an NDVI time series chart and create median monthly composites.
6. **Crop Health Classification** — Reclassify NDVI into five health categories using empirically defined thresholds.
7. **Stress Detection** — Compute the NDVI anomaly (per-image deviation from the multi-temporal mean) to flag stress areas.
8. **Seasonal Analysis** — Generate composite NDVI images for Kharif and Rabi growing seasons.
9. **Export** — Export NDVI, health classification, mean NDVI, peak NDVI (yield proxy), and time-series statistics to Google Drive.

---

## Key Formulas

### NDVI — Normalized Difference Vegetation Index

```
NDVI = (NIR - Red) / (NIR + Red)
```

NIR = Sentinel-2 Band 8 (842 nm), Red = Sentinel-2 Band 4 (665 nm). Range: -1 to +1. Values >0.6 indicate dense healthy vegetation.

### EVI — Enhanced Vegetation Index

```
EVI = 2.5 * ((NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1))
```

Reduces atmospheric and soil background effects; more sensitive in high-biomass regions.

### NDRE — Normalized Difference Red Edge

```
NDRE = (NIR - Red Edge) / (NIR + Red Edge)
```

NIR = Band 8A (865 nm), Red Edge = Band 5 (705 nm). Sensitive to chlorophyll content in mid-to-late stage crops.

### SAVI — Soil Adjusted Vegetation Index

```
SAVI = 1.5 * ((NIR - Red) / (NIR + Red + 0.5))
```

Minimizes soil brightness influence in areas with partial canopy cover.

---

## Results

The script produces the following outputs that are visualized on the GEE map and exported as GeoTIFF files:

- **Latest NDVI Layer:** False-color composite showing NDVI values from 0 to 1. Dark green indicates dense, healthy vegetation; brown/white indicates bare soil or sparse cover.
- **Crop Health Classification:** Five-class thematic map — Stressed (red), Moderate Stress (orange), Moderate (yellow), Healthy (light green), Very Healthy (dark green).
- **Mean NDVI:** Multi-temporal average NDVI across the entire analysis period.
- **NDVI Time Series Chart:** Line plot of mean NDVI over time, capturing phenological cycles.
- **NDVI Anomaly:** Per-image deviation from the long-term mean, highlighting stress events.
- **Seasonal Composites:** Kharif and Rabi season median NDVI maps.
- **Peak NDVI (Yield Proxy):** Maximum NDVI observed, usable as a relative yield indicator.

*Figure 1: NDVI map of Punjab agricultural zones. Green areas show healthy vegetation (NDVI > 0.6), red areas show stressed or bare land.*

*Figure 2: Crop health classification output. The five-class scheme enables rapid assessment of field-level vegetation condition.*

---

## How to Reproduce

1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Copy and paste the entire script from [`GEE_NDVI_Crop_Health_Monitoring.js`](GEE_NDVI_Crop_Health_Monitoring.js) into a new script.
3. Define your Area of Interest (AOI) — either draw a polygon manually using the geometry tools, uncomment the rectangle for Punjab, or upload a shapefile.
4. Adjust the `startDate` and `endDate` variables as needed (default: Jan 2024 – Dec 2025).
5. Click **Run** to execute the script. The map will display the AOI boundary, latest NDVI, health classification, and mean NDVI.
6. Inspect the **Console** tab for image count, NDVI statistics, and the time series chart.
7. In the **Tasks** tab, click each export task to initiate the transfer to your Google Drive.
8. Downloaded GeoTIFFs can be opened in QGIS, ArcGIS, or any GIS software. Apply the NDVI palette (brown → yellow → green) or the health classification palette (red → yellow → green) for visualization.

---

## Accuracy Assessment

NDVI is a continuous biophysical index, not a categorical land-cover product, so traditional accuracy metrics (overall accuracy, kappa, confusion matrix) do not directly apply. However, the following validation approaches are recommended:

- **Field Spectroradiometer Measurements:** Collect in-situ reflectance with a field spectroradiometer and compare calculated NDVI with satellite-derived NDVI at coincident dates (RMSE, R²).
- **Crop Yield Correlation:** Regress peak NDVI against actual crop yield data from agricultural statistics to validate NDVI as a yield proxy.
- **Visual Inspection:** Cross-reference NDVI anomaly maps with known pest/drought reports from the Punjab Agriculture Department.

---

## Limitations

- **Cloud Cover:** Punjab experiences significant cloud cover during the monsoon season (July–September), reducing the number of usable images. The script filters scenes with >20% cloud cover, which may result in data gaps during peak growing months.
- **Spatial Resolution:** 10 m resolution is suitable for field-scale analysis but may miss sub-field variability or narrow agricultural strips.
- **Temporal Resolution:** Sentinel-2 has a 5-day revisit time, but cloud cover can reduce effective temporal sampling to 15–30 days.
- **Ground Truth:** This analysis is currently unvalidated against field measurements. All conclusions should be treated as indicative until cross-referenced with in-situ data.
- **NDVI Saturation:** NDVI saturates in dense, multi-layer canopies (e.g., mature sugarcane or rice), where indices like EVI or NDRE are more appropriate.

---

## Learning Outcomes

This project demonstrates the following skills:

- **Google Earth Engine JavaScript API** — Image collection filtering, mapping functions, reducers, charts, and export tasks
- **Sentinel-2 Processing** — Surface reflectance loading, cloud masking (QA60 bitmask), band math
- **Vegetation Indices** — NDVI, EVI, NDRE, SAVI computation and interpretation
- **Time Series Analysis** — Multi-temporal composites, anomaly detection, and seasonal aggregation
- **GIS Workflow** — AOI definition, GeoTIFF export, and GIS-ready data production
- **Remote Sensing Theory** — Spectral response of vegetation, atmospheric correction principles, index thresholds

---

## Files in This Folder

| File | Description |
|------|-------------|
| `GEE_NDVI_Crop_Health_Monitoring.js` | Full Google Earth Engine JavaScript script |
| `Step_by_Step_Guide.txt` | Non-technical walkthrough for using the GEE script |
| `outputs/` | Directory for exported GeoTIFFs and CSV statistics |
| `README.md` | Project documentation (this file) |

---

## Google Earth Engine Code

The full GEE JavaScript code is available in [`GEE_NDVI_Crop_Health_Monitoring.js`](GEE_NDVI_Crop_Health_Monitoring.js) and reproduced below:

```javascript
// ============================================================================
// PROJECT 1.3: Agricultural Crop Health Monitoring using NDVI
// Region: Punjab Agricultural Areas
// Satellite: Sentinel-2 (Harmonized Surface Reflectance)
// Purpose: Monitor crop health, detect stress, analyze NDVI time series
// ============================================================================

// ============================================================================
// SECTION 1: DEFINE AREA OF INTEREST (AOI)
// ============================================================================

// Option 1: Draw your AOI manually in GEE Code Editor using the geometry tools
// Then assign it to a variable called 'aoi'

// Option 2: Define Punjab region coordinates (example - adjust as needed)
var aoi = ee.Geometry.Rectangle([71.5, 29.2, 75.5, 32.5]); // Punjab region

// Option 3: Upload a shapefile of your specific study area
// Go to Assets -> Upload -> Shapefile, then import it here
// var aoi = ee.FeatureCollection('users/your_username/your_shapefile');

// ============================================================================
// SECTION 2: SET TIME PARAMETERS
// ============================================================================

// Define the time period for analysis (adjust dates as needed)
var endDate = ee.Date('2025-12-31');
var startDate = ee.Date('2024-01-01');

// For current date analysis, uncomment these lines:
// var endDate = ee.Date(Date.now());
// var startDate = endDate.advance(-12, 'month'); // Last 12 months

print('Analysis Period:', startDate, 'to', endDate);

// ============================================================================
// SECTION 3: LOAD AND FILTER SENTINEL-2 IMAGERY
// ============================================================================

// Load Sentinel-2 Surface Reflectance (harmonized)
var s2Collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi)
  .filterDate(startDate, endDate)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 0));

print('Total Sentinel-2 images found:', s2Collection.size());

// ============================================================================
// SECTION 4: CLOUD MASKING FUNCTION
// ============================================================================

// Function to mask clouds based on QA60 band
function maskS2clouds(image) {
  var qa = image.select('QA60');
  
  // Bits 10 and 11 are clouds and cirrus, respectively
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  
  // Both flags should be set to zero, indicating clear sky
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
              .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  
  return image.updateMask(mask)
    .copyProperties(image, ['system:time_start', 'system:index']);
}

// Apply cloud masking
var s2CloudMasked = s2Collection.map(maskS2clouds);
print('Cloud-masked images:', s2CloudMasked.size());

// ============================================================================
// SECTION 5: CALCULATE NDVI
// ============================================================================

// Function to calculate NDVI
function calculateNDVI(image) {
  // NDVI = (NIR - Red) / (NIR + Red)
  // Sentinel-2: B8 = NIR, B4 = Red
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  
  return image.addBands(ndvi)
    .copyProperties(image, ['system:time_start', 'system:index']);
}

// Apply NDVI calculation to all images
var s2WithNDVI = s2CloudMasked.map(calculateNDVI);

// ============================================================================
// SECTION 6: CALCULATE ADDITIONAL VEGETATION INDICES (OPTIONAL)
// ============================================================================

// Function to calculate multiple vegetation indices
function addVegetationIndices(image) {
  // EVI - Enhanced Vegetation Index
  var evi = image.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
      'NIR': image.select('B8'),
      'RED': image.select('B4'),
      'BLUE': image.select('B2')
    }).rename('EVI');
  
  // NDRE - Normalized Difference Red Edge
  var ndre = image.normalizedDifference(['B8A', 'B5']).rename('NDRE');
  
  // SAVI - Soil Adjusted Vegetation Index
  var savi = image.expression(
    '((NIR - RED) / (NIR + RED + 0.5)) * 1.5', {
      'NIR': image.select('B8'),
      'RED': image.select('B4')
    }).rename('SAVI');
  
  return image.addBands([evi, ndre, savi])
    .copyProperties(image, ['system:time_start', 'system:index']);
}

var s2WithIndices = s2WithNDVI.map(addVegetationIndices);

// ============================================================================
// SECTION 7: CREATE NDVI TIME SERIES CHART
// ============================================================================

// Generate time series chart of mean NDVI
var ndviChart = ui.Chart.image.series({
  imageCollection: s2WithNDVI.select('NDVI'),
  region: aoi,
  reducer: ee.Reducer.mean(),
  scale: 10,
  xProperty: 'system:time_start'
}).setOptions({
  title: 'NDVI Time Series - Punjab Agricultural Region',
  hAxis: {title: 'Date'},
  vAxis: {title: 'Mean NDVI', minValue: 0, maxValue: 1},
  lineWidth: 2,
  colors: ['2ca02c'],
  pointSize: 4,
  legend: {position: 'none'}
});

print('NDVI Time Series Chart:', ndviChart);

// ============================================================================
// SECTION 8: CREATE MONTHLY NDVI COMPOSITES
// ============================================================================

// Function to create monthly composites
function createMonthlyComposites() {
  var months = ee.List.sequence(0, endDate.difference(startDate, 'month').subtract(1));
  
  var monthlyComposites = months.map(function(m) {
    m = ee.Number(m);
    var monthStart = startDate.advance(m, 'month');
    var monthEnd = monthStart.advance(1, 'month');
    
    // Get median NDVI for the month
    var monthlyNDVI = s2WithNDVI
      .filterDate(monthStart, monthEnd)
      .select('NDVI')
      .median()
      .set('system:time_start', monthStart.millis())
      .set('month', monthStart.format('YYYY-MM'));
    
    return monthlyNDVI;
  });
  
  return ee.ImageCollection.fromImages(monthlyComposites);
}

var monthlyNDVI = createMonthlyComposites();
print('Monthly NDVI composites created:', monthlyNDVI.size());

// ============================================================================
// SECTION 9: CROP HEALTH CLASSIFICATION
// ============================================================================

// Define NDVI thresholds for crop health
// NDVI > 0.7: Very healthy/dense vegetation
// NDVI 0.5-0.7: Healthy vegetation
// NDVI 0.3-0.5: Moderate vegetation/stress beginning
// NDVI 0.2-0.3: Stressed vegetation
// NDVI < 0.2: Bare soil/no vegetation

function classifyCropHealth(ndviImage) {
  var health = ndviImage.expression(
    'b(0) > 0.7 ? 5 : ' +  // Very Healthy
    'b(0) > 0.5 ? 4 : ' +  // Healthy
    'b(0) > 0.3 ? 3 : ' +  // Moderate
    'b(0) > 0.2 ? 2 : 1',  // Stressed
    {
      'b(0)': ndviImage.select('NDVI')
    }
  ).rename('Health_Class');
  
  return ndviImage.addBands(health);
}

// Apply classification to most recent image
var latestImage = s2WithNDVI.sort('system:time_start', false).first();
var classifiedHealth = classifyCropHealth(latestImage);

// ============================================================================
// SECTION 10: DETECT VEGETATION STRESS AREAS
// ============================================================================

// Calculate NDVI anomaly (deviation from mean)
var meanNDVI = s2WithNDVI.select('NDVI').mean();

// Find images with below-average NDVI (potential stress)
var stressDetection = s2WithNDVI.map(function(image) {
  var ndvi = image.select('NDVI');
  var anomaly = ndvi.subtract(meanNDVI).rename('NDVI_Anomaly');
  return image.addBands(anomaly)
    .copyProperties(image, ['system:time_start', 'system:index']);
});

// ============================================================================
// SECTION 11: VISUALIZATION
// ============================================================================

// NDVI visualization parameters
var ndviVis = {
  min: 0,
  max: 1,
  palette: [
    'FFFFFF', // White (no data/snow)
    'CE7E45', // Brown (bare soil)
    'F1D659', // Light yellow (sparse vegetation)
    'E6D343', // Yellow
    'D4C832', // Yellow-green
    '9CC32A', // Light green
    '63A638', // Green
    '2D8C31', // Dark green
    '1A6B25', // Very dark green (dense vegetation)
    '0D4A1C'  // Darkest green
  ]
};

// Health classification visualization
var healthVis = {
  min: 1,
  max: 5,
  palette: ['FF0000', 'FF7F00', 'FFFF00', '9ACD32', '00FF00']
  // Red (Stressed), Orange, Yellow, Light Green, Green (Very Healthy)
};

// Add layers to map
Map.centerObject(aoi, 8);
Map.addLayer(aoi, {color: 'red'}, 'Area of Interest');

// Add latest NDVI
if (latestImage) {
  var latestNDVI = latestImage.select('NDVI').clip(aoi);
  Map.addLayer(latestNDVI, ndviVis, 'Latest NDVI');
  
  // Add classified health
  var healthClass = classifiedHealth.select('Health_Class').clip(aoi);
  Map.addLayer(healthClass, healthVis, 'Crop Health Classification');
}

// Add mean NDVI
Map.addLayer(meanNDVI.clip(aoi), ndviVis, 'Mean NDVI');

// Add legend
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }
});

var legendTitle = ui.Label({
  value: 'Crop Health Classification',
  style: {
    fontWeight: 'bold',
    fontSize: '16px',
    margin: '0 0 4px 0'
  }
});
legend.add(legendTitle);

var labels = ['Stressed (0.0-0.2)', 'Moderate Stress (0.2-0.3)', 
              'Moderate (0.3-0.5)', 'Healthy (0.5-0.7)', 'Very Healthy (>0.7)'];
var colors = ['FF0000', 'FF7F00', 'FFFF00', '9ACD32', '00FF00'];

for (var i = 0; i < 5; i++) {
  var color = colors[i];
  var label = labels[i];
  
  var row = ui.Panel({
    widgets: [
      ui.Label({
        style: {
          backgroundColor: color,
          padding: '10px',
          marginRight: '8px'
        }
      }),
      ui.Label({
        value: label,
        style: {margin: '0 0 4px 0'}
      })
    ],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
  legend.add(row);
}

Map.add(legend);

// ============================================================================
// SECTION 12: STATISTICS AND ANALYSIS
// ============================================================================

// Calculate regional statistics
var regionalStats = s2WithNDVI.select('NDVI').map(function(image) {
  var stats = image.reduceRegion({
    reducer: ee.Reducer.mean().combine({
      reducer2: ee.Reducer.stdDev(),
      sharedInputs: true
    }).combine({
      reducer2: ee.Reducer.minMax(),
      sharedInputs: true
    }),
    geometry: aoi,
    scale: 10,
    maxPixels: 1e13
  });
  
  return ee.Feature(null, stats)
    .set('system:time_start', image.get('system:time_start'));
});

// Print statistics
print('NDVI Statistics (latest image):', 
  latestImage.select('NDVI').reduceRegion({
    reducer: ee.Reducer.mean().combine({
      reducer2: ee.Reducer.stdDev(),
      sharedInputs: true
    }).combine({
      reducer2: ee.Reducer.minMax(),
      sharedInputs: true
    }),
    geometry: aoi,
    scale: 10,
    maxPixels: 1e13
  }));

// ============================================================================
// SECTION 13: EXPORT RESULTS TO GOOGLE DRIVE
// ============================================================================

// Export latest NDVI image
Export.image.toDrive({
  image: latestImage.select('NDVI').clip(aoi),
  description: 'Latest_NDVI_Punjab',
  folder: 'Crop_Health_Monitoring',
  fileNamePrefix: 'NDVI_Punjab_' + ee.Date(latestImage.get('system:time_start')).format('YYYY_MM_dd').getInfo(),
  region: aoi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export crop health classification
Export.image.toDrive({
  image: classifiedHealth.select('Health_Class').clip(aoi),
  description: 'Crop_Health_Classification',
  folder: 'Crop_Health_Monitoring',
  fileNamePrefix: 'Health_Class_Punjab_' + ee.Date(latestImage.get('system:time_start')).format('YYYY_MM_dd').getInfo(),
  region: aoi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export mean NDVI
Export.image.toDrive({
  image: meanNDVI.clip(aoi),
  description: 'Mean_NDVI_Punjab',
  folder: 'Crop_Health_Monitoring',
  fileNamePrefix: 'Mean_NDVI_Punjab_' + startDate.format('YYYY_MM_dd').getInfo() + '_to_' + endDate.format('YYYY_MM_dd').getInfo(),
  region: aoi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export NDVI time series as CSV
Export.table.toDrive({
  collection: regionalStats,
  description: 'NDVI_Time_Series_Statistics',
  folder: 'Crop_Health_Monitoring',
  fileNamePrefix: 'NDVI_Stats_Punjab',
  fileFormat: 'CSV'
});

// ============================================================================
// SECTION 14: CREATE SEASONAL ANALYSIS (OPTIONAL)
// ============================================================================

// Define growing seasons for Punjab (adjust based on your crops)
// Kharif season (monsoon crops): April - October
// Rabi season (winter crops): November - March

function createSeasonalComposite(year, season) {
  var startMonth, endMonth;
  
  if (season === 'Kharif') {
    startMonth = 4; // April
    endMonth = 10;  // October
  } else {
    startMonth = 11; // November
    endMonth = 3;    // March
  }
  
  var startDate = ee.Date.fromYMD(year, startMonth, 1);
  var endDate = (season === 'Kharif') ? 
    ee.Date.fromYMD(year, endMonth, 31) : 
    ee.Date.fromYMD(year + 1, endMonth, 31);
  
  var seasonalNDVI = s2WithNDVI
    .filterDate(startDate, endDate)
    .select('NDVI')
    .median()
    .set('season', season)
    .set('year', year);
  
  return seasonalNDVI;
}

// Example: Create seasonal composites for 2024
var kharif2024 = createSeasonalComposite(2024, 'Kharif');
var rabi2024 = createSeasonalComposite(2024, 'Rabi');

// Uncomment to visualize seasonal composites
// Map.addLayer(kharif2024.clip(aoi), ndviVis, 'Kharif 2024 NDVI');
// Map.addLayer(rabi2024.clip(aoi), ndviVis, 'Rabi 2024 NDVI');

// ============================================================================
// SECTION 15: YIELD ESTIMATION INDICATOR (SIMPLIFIED)
// ============================================================================

// Peak NDVI as a proxy for potential yield
var peakNDVI = s2WithNDVI.select('NDVI').max();

// Export peak NDVI for yield estimation
Export.image.toDrive({
  image: peakNDVI.clip(aoi),
  description: 'Peak_NDVI_Yield_Indicator',
  folder: 'Crop_Health_Monitoring',
  fileNamePrefix: 'Peak_NDVI_Punjab',
  region: aoi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

print('=== SETUP COMPLETE ===');
print('1. Adjust the AOI to your specific study area');
print('2. Modify date ranges as needed');
print('3. Click "Run" to execute the script');
print('4. Check the "Tasks" tab to start exports');
print('5. Exported files will appear in your Google Drive');
```
