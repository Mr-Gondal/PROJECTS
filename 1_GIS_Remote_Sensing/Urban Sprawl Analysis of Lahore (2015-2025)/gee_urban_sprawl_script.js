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
