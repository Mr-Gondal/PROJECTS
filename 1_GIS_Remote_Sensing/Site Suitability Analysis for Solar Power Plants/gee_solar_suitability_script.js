// Google Earth Engine Script for Solar Power Plant Site Suitability
// Description: Multi-Criteria Decision Analysis (MCDA) for Solar Suitability
// considering Solar Radiation, Slope, Aspect, Land Cover, and Protected Areas.
// Output: Exports a Solar Site Suitability Raster for further refinement in ArcGIS Pro.

// 1. DEFINE STUDY AREA (Punjab)
// Using FAO GAUL boundaries. The default is 'Punjab' in India. 
// You can change 'India' to 'Pakistan' or 'ADM1_NAME' if you are looking at the Pakistani province.
var admin = ee.FeatureCollection("FAO/GAUL/2015/level1");
var roi = admin.filter(ee.Filter.and(
  ee.Filter.eq('ADM1_NAME', 'Punjab'),
  ee.Filter.eq('ADM0_NAME', 'India') // Change 'India' to 'Pakistan' if needed
)).first().geometry();

Map.centerObject(roi, 7);
Map.addLayer(roi, {color: 'blue'}, 'Study Area (Punjab)', false);

// -------------------------------------------------------------
// 2. DATA ACQUISITION & NORMALIZATION (MCDA FACTORS)
// -------------------------------------------------------------

// A. Solar Radiation (Dataset: TerraClimate - Downward surface shortwave radiation)
var climate = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE")
                .filterDate('2018-01-01', '2022-12-31')
                .select('srad');
// Calculate mean over the period
var meanSrad = climate.mean().clip(roi); // W/m^2

// Normalize Solar Radiation (Higher = more suitable, scaled 0 to 1)
var maxSrad = ee.Number(meanSrad.reduceRegion(ee.Reducer.max(), roi, 5000).get('srad'));
var minSrad = ee.Number(meanSrad.reduceRegion(ee.Reducer.min(), roi, 5000).get('srad'));
var normSrad = meanSrad.subtract(ee.Image(minSrad))
                   .divide(ee.Image(maxSrad).subtract(ee.Image(minSrad)));

// B. Topography: Elevation, Slope & Aspect (Dataset: SRTM DEM 30m)
var dem = ee.Image('USGS/SRTMGL1_003').clip(roi);
var slope = ee.Terrain.slope(dem);
var aspect = ee.Terrain.aspect(dem);

// Normalize Slope (Lower slope is better: < 5 degrees ideal, > 15 is generally excluded)
// We use a linear decay for suitability where 0 degrees = 1.0, and 15 degrees = 0.0
var slopeSuitability = ee.Image(1).subtract(slope.divide(15)).clamp(0, 1);

// Normalize Aspect (South-facing is best in Northern Hemisphere, ~135 to 225 degrees)
// South receives the most direct sunlight throughout the year
var aspectSuitability = aspect.expression(
  '(a >= 135 && a <= 225) ? 1.0 : (a >= 90 && a < 135) || (a > 225 && a <= 270) ? 0.7 : 0.3',
  { 'a': aspect }
);

// C. Land Cover (Dataset: ESA WorldCover 10m)
var lc = ee.ImageCollection("ESA/WorldCover/v200").first().clip(roi);

// Assign suitability based on class (0 to 1 scale)
// ESA Classes: 10 Trees(0.1), 20 Shrubland(0.8), 30 Grassland(0.7), 40 Cropland(0.4), 
// 50 Built-up(0.1 - excluded due to land cost/availability), 60 Bare(1.0 - ideal), 
// 70 Snow/Ice(0), 80 Water(0), 90 Wetland(0), 95 Mangroves(0), 100 Moss(0)
var lcSuitability = lc.remap(
  [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100],
  [0.1, 0.8, 0.7, 0.4, 0.1, 1.0, 0, 0, 0, 0, 0]
);

// -------------------------------------------------------------
// 3. CONSTRAINTS (Areas to Exclude Completely)
// -------------------------------------------------------------

// Constraint 1: Protected Areas (Dataset: WDPA)
// We cannot build power plants in national parks or nature reserves.
var protectedAreas = ee.FeatureCollection("WCMC/WDPA/current/polygons").filterBounds(roi);
var paMask = ee.Image(1).paint(protectedAreas, 0).clip(roi); // 0 inside PA, 1 outside

// Constraint 2: Unsuitable Land/Water (Classes 70, 80, 90)
var waterMask = lc.neq(80).and(lc.neq(70)).and(lc.neq(90));

// Constraint 3: Steep slopes (> 15 degrees are typically excluded for utility-scale solar)
var slopeMask = slope.lt(15);

// Combine all exclusionary masks
var totalMask = paMask.and(waterMask).and(slopeMask);

// -------------------------------------------------------------
// 4. SUITABILITY MAPPING (MCDA Weighted Overlay)
// -------------------------------------------------------------
// Weights: Solar Rad 40%, Land Cover 30%, Slope 20%, Aspect 10%
var initialSuitability = normSrad.multiply(0.40)
  .add(lcSuitability.multiply(0.30))
  .add(slopeSuitability.multiply(0.20))
  .add(aspectSuitability.multiply(0.10))
  .multiply(totalMask) // Apply constraints (excluded areas become 0)
  .rename('Solar_Suitability_Base');

// Visualize the results
Map.addLayer(initialSuitability.updateMask(totalMask), 
  {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'green', 'darkgreen']}, 
  'Initial Solar Suitability (GEE)');

// -------------------------------------------------------------
// 5. EXPORT FOR ARCGIS PRO
// -------------------------------------------------------------
// We export this base suitability layer. 
// "Proximity to grid" is best modeled inside ArcGIS using Euclidean Distance on local grid vectors!

Export.image.toDrive({
  image: initialSuitability,
  description: 'Solar_Site_Suitability_Base',
  folder: 'GEE_Solar_Project',
  scale: 30, 
  region: roi.bounds(),
  maxPixels: 1e13
});
