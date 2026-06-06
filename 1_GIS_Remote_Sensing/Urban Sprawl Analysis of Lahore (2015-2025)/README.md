# Urban Sprawl Analysis of Lahore (2015–2025)

**Author:** Haris Hussain  
**Institution:** Space Science, University of the Punjab, Lahore  
**Date:** 2025  
**Type:** GIS & Remote Sensing Portfolio Project

---

## Overview

Lahore, the second-largest city in Pakistan, has experienced rapid and often unplanned urban expansion over the past decade. Driven by population growth, rural-to-urban migration, and economic development, the city's built-up area has expanded significantly into surrounding agricultural and peri-urban zones. This project quantifies that expansion by applying machine learning classification to multi-temporal Landsat 8 imagery (2015 and 2025) within Google Earth Engine, producing Land Use / Land Cover (LULC) maps and a change-detection layer that highlights newly built-up areas.

Pakistan's urban population is growing at over 3% annually, and Lahore — as a major economic and cultural hub — is at the forefront of this transformation. Understanding the spatial pattern of sprawl is critical for urban planners, environmental managers, and infrastructure developers. This analysis provides a replicable, data-driven method for monitoring urban growth using freely available satellite imagery and cloud-based processing.

---

## Data Sources

| Dataset | Source | Resolution | Bands Used |
|---------|--------|------------|------------|
| Landsat 8 Collection 2 Level-2 Surface Reflectance | [USGS EarthExplorer](https://earthexplorer.usgs.gov/) via Google Earth Engine (`LANDSAT/LC08/C02/T1_L2`) | 30 m | SR_B2 (Blue), SR_B3 (Green), SR_B4 (Red), SR_B5 (NIR), SR_B6 (SWIR1), SR_B7 (SWIR2) |
| Administrative Boundaries | FAO GAUL 2015 Level 2 (`FAO/GAUL/2015/level2`) | Vector | — |

Imagery was filtered for cloud cover < 15% and composited per epoch (2015 and 2024–2025).

---

## Methodology

### 1. Pre-processing (GEE)

- **Cloud masking:** The `QA_PIXEL` band is used to mask clouds, cirrus, and cloud shadows via bitmask operations.
- **Scaling:** Surface reflectance values are scaled using the Collection 2 formula: `pixel × 0.0000275 − 0.2`, converting raw DN to reflectance.
- **Composite:** A median reducer is applied over each epoch to produce cloud-free image composites.
- **Clip:** Both composites are clipped to the Lahore district boundary.

### 2. Classification — Random Forest

A Random Forest classifier (50 trees) is trained on two land-cover classes:

- **Urban (Class 1):** Built-up areas, roads, concrete surfaces
- **Non-Urban (Class 0):** Vegetation, water, bare soil, agriculture

Training samples are extracted from the 6 spectral bands listed above. The classifier is trained independently for 2015 and 2025 to account for spectral shifts across time.

### 3. Change Detection

New urban areas are identified by subtracting the 2015 classification from the 2025 classification:

```
New Urban = Classification_2025 − Classification_2015
```

A pixel value of **+1** indicates a transition from Non-Urban (0) in 2015 to Urban (1) in 2025 — i.e., urban sprawl. A `pixelArea()` reducer then calculates the total area (in m²) of new built-up land.

---

## Results

The output consists of three raster layers exported as GeoTIFFs:

1. **Lahore_LULC_2015.tif** — Classified land cover for 2015 (red = urban, green = non-urban).
2. **Lahore_LULC_2025.tif** — Classified land cover for 2025.
3. **New Built-up Regions** — A yellow overlay (in the GEE Map) highlighting pixels that changed from non-urban to urban between the two epochs.

The GEE console prints the total new urban area in square meters, which can be converted to km² for reporting.

> **Note:** These results are for *demonstration purposes* only. Training data is minimal (4 point samples), so the classification accuracy is not yet suitable for scientific publication.

---

## How to Reproduce

1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com).
2. Create a new script and paste the full code from `GEE_Urban_Sprawl_Analysis.js`.
3. **(Critical)** Use the GEE geometry tools to draw **training polygons**:
   - Create a geometry named `urbanTrain` with property `class = 1` — draw over buildings, roads, and concrete surfaces.
   - Create a geometry named `nonUrbanTrain` with property `class = 0` — draw over vegetation, water, and bare land.
   - Replace the placeholder `sampleUrban` and `sampleNonUrban` variables with your new geometry imports.
4. Click **Run**. Inspect the classified layers on the map.
5. Open the **Tasks** tab to export `Lahore_LULC_2015` and `Lahore_LULC_2025` to your Google Drive as GeoTIFFs (30 m resolution).
6. *(Optional)* Import the exported rasters into QGIS or ArcGIS Pro for further analysis (directional ellipses, future prediction via the MOLUSCE plugin).

---

## Accuracy Assessment

**Not yet performed.** The current script includes only *4 point samples* (2 urban, 2 non-urban) as placeholders. **A minimum of 20–30 polygons per class is recommended** to train a robust Random Forest model. For a proper accuracy assessment:

- Reserve 30% of training polygons for validation.
- Compute a confusion matrix, overall accuracy, and Kappa coefficient.
- Consider temporally independent validation points for change detection.

---

## Limitations

- **Training data:** The single largest limitation. With only 4 points, the classifier is essentially untrained and results are unreliable.
- **Temporal resolution:** Only two epochs (2015 and 2025) are compared. Annual or biennial analysis would provide a more nuanced picture.
- **Single sensor:** Landsat 8 alone is used; incorporating Sentinel-2 (10 m) could improve spatial detail.
- **No accuracy metrics:** Without a confusion matrix, map uncertainty is unknown.
- **Binary classification:** Only two classes (urban / non-urban) are mapped. A multi-class scheme (e.g., water, vegetation, bare soil, high/low density urban) would be more informative.
- **Seasonal effects:** Image composites from different seasons may introduce spectral variability unrelated to land cover change.

---

## Learning Outcomes

Through this project, the following skills were developed:

- **Google Earth Engine JavaScript API:** Filtering, cloud masking, scaling, and compositing Landsat 8 imagery.
- **Supervised classification:** Training a Random Forest classifier with spectral bands.
- **Change detection:** Raster algebra to identify land-cover transitions.
- **Area calculation:** Using `pixelArea()` and reducers to quantify change.
- **Export workflows:** Transferring GEE results to desktop GIS software (QGIS, ArcGIS Pro).
- **Spatial modeling workflow:** Understanding the full pipeline from satellite imagery to predictive mapping (including potential use of MOLUSCE for future scenario simulation).

---

## Files in This Folder

| File | Description |
|------|-------------|
| `README.md` | This document |
| `GEE_Urban_Sprawl_Analysis.js` | Google Earth Engine JavaScript code for LULC classification and change detection |
| `step_by_step_guide.txt` | Extended guide covering Phases 2–4 (ArcGIS directional analysis and QGIS MOLUSCE prediction for 2035) |
| *(Output rasters are exported to Google Drive, not stored locally)* | — |

---

## Google Earth Engine Code

The full JavaScript code is reproduced below and also available in `GEE_Urban_Sprawl_Analysis.js`.

```javascript
// Google Earth Engine Script for Urban Sprawl Analysis
// Description: Multi-temporal Land Use Land Cover (LULC) Classification 
// using Landsat 8 (2015 and 2025) to map urban expansion in Lahore.
// Output: Exports Classified LULC Rasters for 2015 and 2025

// 1. DEFINE STUDY AREA (Lahore, Pakistan)
var admin2 = ee.FeatureCollection("FAO/GAUL/2015/level2");
var roi = admin2.filter(ee.Filter.eq('ADM2_NAME', 'Lahore')).first().geometry();

Map.centerObject(roi, 10);
Map.addLayer(roi, {color: 'red'}, 'Lahore Boundary', false);

// -------------------------------------------------------------
// 2. IMAGE PREPARATION (Landsat 8 Surface Reflectance)
// -------------------------------------------------------------
// Mask clouds and scale pixel values
function maskL8sr(image) {
  var qa = image.select('QA_PIXEL');
  var cloudBitMask = 1 << 3;
  var cirrusBitMask = 1 << 2;
  var cloudExtBitMask = 1 << 4;
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    .and(qa.bitwiseAnd(cirrusBitMask).eq(0))
    .and(qa.bitwiseAnd(cloudExtBitMask).eq(0));
  return image.updateMask(mask).multiply(0.0000275).add(-0.2); // Scaling factors for Collection 2
}

// 2015 Image Composite 
var image2015 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                  .filterBounds(roi)
                  .filterDate('2015-01-01', '2015-12-31')
                  .filter(ee.Filter.lt('CLOUD_COVER', 15))
                  .map(maskL8sr)
                  .median()
                  .clip(roi);

// 2025 Image Composite
var image2025 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                  .filterBounds(roi)
                  .filterDate('2024-01-01', '2025-12-31')
                  .filter(ee.Filter.lt('CLOUD_COVER', 15))
                  .map(maskL8sr)
                  .median()
                  .clip(roi);

var visParams = {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 0, max: 0.3};
Map.addLayer(image2015, visParams, 'Landsat 8 RGB 2015', false);
Map.addLayer(image2025, visParams, 'Landsat 8 RGB 2025', false);

// -------------------------------------------------------------
// 3. LULC CLASSIFICATION (Random Forest)
// -------------------------------------------------------------
// IMPORTANT: The samples below are just placeholders to let the script run.
// For accurate results, use the GEE geometry tools to draw polygons 
// over built-up areas (class: 1) and rural areas (class: 0) to replace these points!

var sampleUrban = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([74.3587, 31.5204]), {'class': 1}), 
  ee.Feature(ee.Geometry.Point([74.3200, 31.5500]), {'class': 1})  
]);
var sampleNonUrban = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([74.4500, 31.4000]), {'class': 0}), 
  ee.Feature(ee.Geometry.Point([74.2000, 31.6000]), {'class': 0})
]);
var trainingPoints = sampleUrban.merge(sampleNonUrban);

var bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'];

// Train RF for 2015
var training2015 = image2015.select(bands).sampleRegions({
  collection: trainingPoints, properties: ['class'], scale: 30
});
var classifier2015 = ee.Classifier.smileRandomForest(50).train({
  features: training2015, classProperty: 'class', inputProperties: bands
});
var classified2015 = image2015.select(bands).classify(classifier2015);

// Train RF for 2025
var training2025 = image2025.select(bands).sampleRegions({
  collection: trainingPoints, properties: ['class'], scale: 30
});
var classifier2025 = ee.Classifier.smileRandomForest(50).train({
  features: training2025, classProperty: 'class', inputProperties: bands
});
var classified2025 = image2025.select(bands).classify(classifier2025);

Map.addLayer(classified2015, {min: 0, max: 1, palette: ['green', 'red']}, 'Classified 2015', false);
Map.addLayer(classified2025, {min: 0, max: 1, palette: ['green', 'red']}, 'Classified 2025');

// -------------------------------------------------------------
// 4. CHANGE DETECTION (Urban Expansion)
// -------------------------------------------------------------
// Calculate new urban areas
var expansion = classified2025.subtract(classified2015);
var newUrban = expansion.eq(1); // Areas that went from 0 (Non-Urban) to 1 (Urban)

Map.addLayer(newUrban.selfMask(), {palette: 'yellow'}, 'New Built-up Regions (Sprawl)');

// Calculate expansion area automatically in GEE
var areaImage = ee.Image.pixelArea().updateMask(newUrban);
var newUrbanArea = areaImage.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: roi,
  scale: 30,
  maxPixels: 1e13
}).get('area');

print('New Urban Area (Sprawl) in Square Meters:', newUrbanArea);

// -------------------------------------------------------------
// 5. EXPORT TASKS FOR QGIS/ARCGIS PRO
// -------------------------------------------------------------
// Export 2015 Classification
Export.image.toDrive({
  image: classified2015, 
  description: 'Lahore_LULC_2015',
  folder: 'GEE_Urban_Sprawl', scale: 30, region: roi, maxPixels: 1e13
});
// Export 2025 Classification
Export.image.toDrive({
  image: classified2025, 
  description: 'Lahore_LULC_2025',
  folder: 'GEE_Urban_Sprawl', scale: 30, region: roi, maxPixels: 1e13
});
```
