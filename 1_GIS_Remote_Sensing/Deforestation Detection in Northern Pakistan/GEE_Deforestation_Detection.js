// ============================================================================
// PROJECT 1.4: Deforestation Detection in Northern Pakistan
// Region: Northern Pakistan (KPK, Gilgit-Baltistan, Azad Kashmir)
// Data: Hansen Global Forest Change v1.12 (2000-2024)
// Purpose: Detect and quantify forest cover changes, create change maps,
//          and calculate carbon loss estimates
// ============================================================================

// ============================================================================
// SECTION 1: DEFINE AREA OF INTEREST (AOI)
// ============================================================================

// Option 1: Draw your AOI manually in GEE Code Editor
// Then use the drawn geometry

// Option 2: Define Northern Pakistan region (adjust coordinates as needed)
var aoi = ee.Geometry.Rectangle([71.5, 34.0, 74.5, 37.0]); 
// Covers parts of KPK, Gilgit-Baltistan, and Azad Kashmir

// Option 3: Upload a shapefile of your specific study area
// Go to Assets -> Upload -> Shapefile, then import it here
// var aoi = ee.FeatureCollection('users/your_username/northern_pakistan_forests');

// ============================================================================
// SECTION 2: LOAD HANSEN GLOBAL FOREST CHANGE DATASET
// ============================================================================

// Load the Hansen Global Forest Change dataset (v1.12, 2000-2024)
var hansen = ee.Image('UMD/hansen/global_forest_change_2024_v1_12');

// Extract relevant bands
var treeCover2000 = hansen.select('treecover2000');        // Tree cover percentage in 2000 (0-100)
var lossMask = hansen.select('loss');                      // Binary: 1 = loss, 0 = no loss
var gainMask = hansen.select('gain');                      // Binary: 1 = gain, 0 = no gain
var lossYear = hansen.select('lossyear');                  // Year of loss (0-24, where 0=2001, 24=2024)
var dataMask = hansen.select('datamask');                  // Valid data mask

print('Hansen dataset loaded successfully');

// ============================================================================
// SECTION 3: DEFINE FOREST THRESHOLD AND MASK FOREST AREAS
// ============================================================================

// Define minimum tree cover threshold to classify as "forest" (FAO standard: 10%)
var forestThreshold = 10;

// Create forest mask for year 2000
var forest2000 = treeCover2000.gte(forestThreshold);

// Calculate actual forest area in 2000
var forestArea2000 = forest2000.multiply(ee.Image.pixelArea()).divide(1000000); // Convert to km²

// Clip to AOI
var forest2000Clipped = forest2000.clip(aoi);
var forestArea2000Clipped = forestArea2000.clip(aoi);

print('Forest definition: Tree cover >= ' + forestThreshold + '% in year 2000');

// ============================================================================
// SECTION 4: CALCULATE DEFORESTATION STATISTICS
// ============================================================================

// Total forest area in 2000
var totalForest2000 = forestArea2000Clipped.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 30,
  maxPixels: 1e13
});

print('=== FOREST COVER STATISTICS ===');
print('Total Forest Area in 2000 (km²):', totalForest2000);

// Areas that experienced deforestation
var deforestedArea = lossMask.multiply(forest2000).multiply(ee.Image.pixelArea()).divide(1000000);
var totalDeforested = deforestedArea.clip(aoi).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 30,
  maxPixels: 1e13
});

print('Total Deforested Area (2000-2024) (km²):', totalDeforested);

// Calculate deforestation percentage
var deforestationPercent = ee.Number(totalDeforested.get('loss'))
  .divide(ee.Number(totalForest2000.get('treecover2000')))
  .multiply(100);

print('Deforestation Rate (%):', deforestationPercent);

// Areas with forest gain (reforestation)
var reforestedArea = gainMask.multiply(ee.Image.pixelArea()).divide(1000000);
var totalReforested = reforestedArea.clip(aoi).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 30,
  maxPixels: 1e13
});

print('Total Reforested Area (2000-2012) (km²):', totalReforested);

// Net forest change
var netChange = ee.Number(totalReforested.get('gain'))
  .subtract(ee.Number(totalDeforested.get('loss')));

print('Net Forest Change (km²):', netChange);

// ============================================================================
// SECTION 5: TEMPORAL ANALYSIS - DEFORESTATION BY YEAR
// ============================================================================

// Create a list of years (2001-2024)
var years = ee.List.sequence(1, 24);

// Calculate deforested area for each year
var yearlyDeforestation = years.map(function(year) {
  var lossInYear = lossYear.eq(year);
  var area = lossInYear.multiply(ee.Image.pixelArea()).divide(1000000);
  
  var stats = area.clip(aoi).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: aoi,
    scale: 30,
    maxPixels: 1e13
  });
  
  return ee.Feature(null, {
    'year': ee.Number(2000).add(year),
    'deforested_km2': stats.get('lossyear'),
    'cumulative_deforested_km2': null // Will calculate below
  });
});

// Create feature collection
var yearlyStats = ee.FeatureCollection(yearlyDeforestation);

// Calculate cumulative deforestation
var cumulativeDeforestation = yearlyStats.map(function(feature) {
  var year = feature.get('year');
  var cumulative = yearlyStats
    .filter(ee.Filter.lte('year', year))
    .aggregate_sum('deforested_km2');
  
  return feature.set('cumulative_deforested_km2', cumulative);
});

print('Yearly Deforestation Statistics:', cumulativeDeforestation);

// Create chart of yearly deforestation
var deforestationChart = ui.Chart.feature.byFeature({
  features: cumulativeDeforestation,
  xProperty: 'year',
  yProperties: ['deforested_km2', 'cumulative_deforested_km2']
}).setOptions({
  title: 'Annual and Cumulative Deforestation in Northern Pakistan',
  hAxis: {title: 'Year'},
  vAxis: {title: 'Area (km²)'},
  series: {
    0: {type: 'columns', labelInLegend: 'Annual Deforestation (km²)'},
    1: {type: 'line', labelInLegend: 'Cumulative Deforestation (km²)'}
  },
  colors: ['d95f02', '7570b3']
});

print('Deforestation Time Series Chart:', deforestationChart);

// ============================================================================
// SECTION 6: SPATIAL ANALYSIS - DEFORESTATION HOTSPOTS
// ============================================================================

// Create deforestation hotspot map (loss year visualization)
var lossYearVis = lossYear.updateMask(lossMask).clip(aoi);

// Identify recent deforestation (last 5 years: 2020-2024)
var recentLoss = lossYear.gte(20).and(lossYear.lte(24));
var recentDeforestedArea = recentLoss.multiply(ee.Image.pixelArea()).divide(1000000);
var totalRecentLoss = recentDeforestedArea.clip(aoi).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 30,
  maxPixels: 1e13
});

print('Recent Deforestation (2020-2024) (km²):', totalRecentLoss);

// Identify old deforestation (2001-2010)
var oldLoss = lossYear.gte(1).and(lossYear.lte(10));

// Create deforestation severity layer
var deforestationSeverity = lossYear.updateMask(lossMask);

// ============================================================================
// SECTION 7: CARBON LOSS ESTIMATION
// ============================================================================

// Average carbon density for tropical/subtropical forests (Mg C/ha)
// Northern Pakistan forests: approximately 100-150 Mg C/ha (adjust based on literature)
var carbonDensity = 120; // Mg C per hectare

// Calculate carbon loss
var carbonLoss = lossMask.multiply(forest2000)
  .multiply(ee.Image.pixelArea())
  .divide(10000) // Convert m² to hectares
  .multiply(carbonDensity)
  .clip(aoi);

var totalCarbonLoss = carbonLoss.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 30,
  maxPixels: 1e13
});

print('=== CARBON LOSS ESTIMATION ===');
print('Total Carbon Loss (Mg C):', totalCarbonLoss);
print('Total Carbon Loss (tonnes CO2 equivalent):', 
  ee.Number(totalCarbonLoss.get('loss')).multiply(3.67)); // Convert C to CO2

// ============================================================================
// SECTION 8: ELEVATION-BASED DEFORESTATION ANALYSIS (OPTIONAL)
// ============================================================================

// Load SRTM elevation data
var elevation = ee.Image('USGS/SRTMGL1_003').clip(aoi);

// Create elevation zones
var elevationZones = elevation.expression(
  'b(0) < 1000 ? 1 : ' +    // Low elevation
  'b(0) < 2000 ? 2 : ' +    // Mid elevation
  'b(0) < 3000 ? 3 : 4',    // High elevation
  {'b(0)': elevation}
).rename('elevation_zone');

// Analyze deforestation by elevation zone
var deforestationByElevation = elevationZones.updateMask(lossMask);

print('Elevation-based deforestation analysis created');
print('Zone 1: <1000m, Zone 2: 1000-2000m, Zone 3: 2000-3000m, Zone 4: >3000m');

// ============================================================================
// SECTION 9: CREATE DEFORESTATION ALERT MAP
// ============================================================================

// Combine tree cover, loss, and gain into single alert layer
var alertMap = ee.Image(0)
  .where(forest2000.eq(1).and(lossMask.eq(0)), 1)  // Intact forest
  .where(forest2000.eq(1).and(lossMask.eq(1)), 2)  // Deforested
  .where(gainMask.eq(1), 3)                         // Reforested
  .where(forest2000.eq(0).and(lossMask.eq(0)).and(gainMask.eq(0)), 4); // Non-forest

var alertMapClipped = alertMap.clip(aoi);

print('Alert map created with classes:');
print('1 = Intact Forest, 2 = Deforested, 3 = Reforested, 4 = Non-Forest');

// ============================================================================
// SECTION 10: VISUALIZATION
// ============================================================================

// Tree cover 2000 visualization
var treeCoverVis = {
  min: 0,
  max: 100,
  palette: ['FFFFFF', '00FF00', '006600']
};

// Loss year visualization
var lossYearVisParams = {
  min: 0,
  max: 24,
  palette: ['FFFF00', 'FFA500', 'FF0000', '8B0000']
};

// Alert map visualization
var alertVis = {
  min: 1,
  max: 4,
  palette: ['006600', 'FF0000', '00FF00', 'CCCCCC']
  // Green (intact), Red (deforested), Light green (reforested), Gray (non-forest)
};

// Carbon loss visualization
var carbonLossVis = {
  min: 0,
  max: 500,
  palette: ['FFFFFF', 'FFFF00', 'FF8C00', 'FF0000', '8B0000']
};

// Add layers to map
Map.centerObject(aoi, 7);
Map.addLayer(aoi, {color: 'red'}, 'Area of Interest');

// Tree cover 2000
Map.addLayer(treeCover2000.clip(aoi), treeCoverVis, 'Tree Cover 2000 (%)');

// Forest mask
Map.addLayer(forest2000Clipped.updateMask(forest2000Clipped), 
  {palette: ['006600']}, 'Forest Areas (2000)');

// Deforestation alert map
Map.addLayer(alertMapClipped, alertVis, 'Deforestation Alert Map');

// Loss year
Map.addLayer(lossYearVis, lossYearVisParams, 'Deforestation Year');

// Recent deforestation
Map.addLayer(recentLoss.updateMask(recentLoss).clip(aoi), 
  {palette: ['FF0000']}, 'Recent Deforestation (2020-2024)');

// Carbon loss
Map.addLayer(carbonLoss, carbonLossVis, 'Carbon Loss (Mg C/ha)');

// Add legend
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }
});

var legendTitle = ui.Label({
  value: 'Deforestation Alert Map',
  style: {
    fontWeight: 'bold',
    fontSize: '16px',
    margin: '0 0 4px 0'
  }
});
legend.add(legendTitle);

var labels = ['Intact Forest', 'Deforested Area', 'Reforested Area', 'Non-Forest'];
var colors = ['006600', 'FF0000', '00FF00', 'CCCCCC'];

for (var i = 0; i < 4; i++) {
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

// Add loss year legend
var lossLegend = ui.Panel({
  style: {
    position: 'bottom-right',
    padding: '8px 15px'
  }
});

var lossLegendTitle = ui.Label({
  value: 'Deforestation Year',
  style: {
    fontWeight: 'bold',
    fontSize: '14px',
    margin: '0 0 4px 0'
  }
});
lossLegend.add(lossLegendTitle);

var yearLabels = ['2001-2005', '2006-2010', '2011-2015', '2016-2020', '2021-2024'];
var yearColors = ['FFFF00', 'FFA500', 'FF8C00', 'FF0000', '8B0000'];

for (var i = 0; i < 5; i++) {
  var row = ui.Panel({
    widgets: [
      ui.Label({
        style: {
          backgroundColor: yearColors[i],
          padding: '10px',
          marginRight: '8px'
        }
      }),
      ui.Label({
        value: yearLabels[i],
        style: {margin: '0 0 4px 0'}
      })
    ],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
  lossLegend.add(row);
}

Map.add(lossLegend);

// ============================================================================
// SECTION 11: DISTRICT-LEVEL ANALYSIS (OPTIONAL)
// ============================================================================

// Load administrative boundaries (GADM level 2)
var gadm = ee.FeatureCollection('WCMC/WDPA/current/polygons');

// If you have specific district boundaries, upload them as shapefile
// var districts = ee.FeatureCollection('users/your_username/pakistan_districts');

// Example: Zonal statistics by district (uncomment when you have district boundaries)
/*
var districtDeforestation = districts.map(function(district) {
  var area = lossMask.clip(district.geometry())
    .multiply(ee.Image.pixelArea())
    .divide(1000000)
    .reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: district.geometry(),
      scale: 30,
      maxPixels: 1e13
    });
  
  return district.set({
    'deforested_km2': area.get('loss'),
    'analysis_year': '2000-2024'
  });
});

print('District-level Deforestation:', districtDeforestation);
*/

// ============================================================================
// SECTION 12: SENTINEL-2 VALIDATION (OPTIONAL)
// ============================================================================

// Load recent Sentinel-2 imagery for visual validation
var s2Recent = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi)
  .filterDate('2024-01-01', '2024-12-31')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .median()
  .clip(aoi);

// True color composite for visual reference
var s2TrueColor = {
  bands: ['B4', 'B3', 'B2'],
  min: 0,
  max: 3000
};

// Uncomment to add Sentinel-2 base layer
// Map.addLayer(s2Recent, s2TrueColor, 'Sentinel-2 True Color (2024)');

// ============================================================================
// SECTION 13: SUMMARY STATISTICS
// ============================================================================

print('========================================');
print('DEFORESTATION ANALYSIS SUMMARY');
print('========================================');
print('Study Area: Northern Pakistan');
print('Analysis Period: 2000-2024');
print('Data Source: Hansen Global Forest Change v1.12');
print('----------------------------------------');
print('Forest Cover in 2000 (km²):', totalForest2000.get('treecover2000'));
print('Total Deforested (km²):', totalDeforested.get('loss'));
print('Deforestation Rate (%):', deforestationPercent.round(2));
print('Total Reforested (km²):', totalReforested.get('gain'));
print('Net Forest Change (km²):', netChange.round(2));
print('Recent Deforestation 2020-2024 (km²):', totalRecentLoss.get('lossyear'));
print('Total Carbon Loss (Mg C):', totalCarbonLoss.get('loss'));
print('CO2 Equivalent (tonnes):', ee.Number(totalCarbonLoss.get('loss')).multiply(3.67).round(0));
print('========================================');

// ============================================================================
// SECTION 14: EXPORT RESULTS TO GOOGLE DRIVE
// ============================================================================

// Export tree cover 2000
Export.image.toDrive({
  image: treeCover2000.clip(aoi),
  description: 'Tree_Cover_2000',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'TreeCover2000_NorthernPakistan',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export deforestation mask
Export.image.toDrive({
  image: lossMask.clip(aoi),
  description: 'Deforestation_Mask',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'DeforestationMask_2000_2024',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export loss year map
Export.image.toDrive({
  image: lossYearVis.clip(aoi),
  description: 'Deforestation_Year_Map',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'LossYear_2000_2024',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export forest gain mask
Export.image.toDrive({
  image: gainMask.clip(aoi),
  description: 'Reforestation_Map',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'ForestGain_2000_2012',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export deforestation alert map
Export.image.toDrive({
  image: alertMapClipped,
  description: 'Deforestation_Alert_Map',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'AlertMap_NorthernPakistan',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export carbon loss map
Export.image.toDrive({
  image: carbonLoss.clip(aoi),
  description: 'Carbon_Loss_Map',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'CarbonLoss_NorthernPakistan',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export recent deforestation (2020-2024)
Export.image.toDrive({
  image: recentLoss.clip(aoi),
  description: 'Recent_Deforestation',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'RecentDeforestation_2020_2024',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

// Export yearly statistics as CSV
Export.table.toDrive({
  collection: cumulativeDeforestation,
  description: 'Yearly_Deforestation_Stats',
  folder: 'Deforestation_Northern_Pakistan',
  fileNamePrefix: 'YearlyDeforestationStats',
  fileFormat: 'CSV'
});

// ============================================================================
// SECTION 15: TIME SERIES OF SENTINEL-2 FOR SPECIFIC LOCATIONS (OPTIONAL)
// ============================================================================

// Function to create NDVI time series for deforested areas
function createDeforestationTimeSeries() {
  // Get Sentinel-2 images before and after major deforestation
  var s2Before = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate('2015-01-01', '2015-12-31')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .median();
  
  var s2After = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate('2024-01-01', '2024-12-31')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .median();
  
  // Calculate NDVI
  var ndviBefore = s2Before.normalizedDifference(['B8', 'B4']).rename('NDVI');
  var ndviAfter = s2After.normalizedDifference(['B8', 'B4']).rename('NDVI');
  
  // NDVI change
  var ndviChange = ndviAfter.subtract(ndviBefore).rename('NDVI_Change');
  
  return {
    ndviBefore: ndviBefore,
    ndviAfter: ndviAfter,
    ndviChange: ndviChange
  };
}

// Uncomment to run time series analysis
// var timeSeries = createDeforestationTimeSeries();
// Map.addLayer(timeSeries.ndviChange.clip(aoi), 
//   {min: -0.5, max: 0.5, palette: ['red', 'white', 'green']}, 
//   'NDVI Change (2015-2024)');

print('=== SETUP COMPLETE ===');
print('1. Adjust the AOI to your specific study area');
print('2. Modify forest threshold if needed (line 40)');
print('3. Click "Run" to execute the script');
print('4. Check the "Tasks" tab to start exports');
print('5. Exported files will appear in your Google Drive');
