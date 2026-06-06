# Site Suitability Analysis for Solar Power Plants — Punjab, Pakistan

**Author:** Haris Hussain  
**Institution:** Space Science, University of the Punjab, Lahore  
**Date:** 2026  
**Satellite Data:** TerraClimate, SRTM DEM, ESA WorldCover  
**Analysis Type:** Multi-Criteria Decision Analysis (MCDA)

---

## Overview

Pakistan faces a persistent energy deficit, with demand regularly outstripping supply during peak summer months. Punjab province, the country's agricultural and industrial heartland, receives some of the highest solar irradiance levels in the world, making it a prime candidate for utility-scale solar photovoltaic (PV) installations. However, not all land is suitable: factors such as slope, aspect, land cover, and proximity to protected areas must be systematically evaluated before siting decisions can be made.

This project implements a Multi-Criteria Decision Analysis (MCDA) framework in Google Earth Engine to identify and map suitable locations for solar power plants across Punjab, Pakistan. The analysis integrates five key factors — solar radiation, slope, aspect, land cover type, and protected area boundaries — into a single suitability index ranging from 0 (unsuitable) to 1 (highly suitable). Exclusionary constraints remove water bodies, steep slopes, snow/ice, wetlands, and legally protected areas from consideration.

The output is a base suitability raster that can be further refined in a GIS environment by adding proximity-to-transmission-grid and distance-to-road analyses. This workflow demonstrates a reproducible, data-driven approach to renewable energy planning that can be adapted to any region with available satellite and ancillary data.

## Data Sources

| Dataset | Source | Resolution | Purpose |
|---------|--------|-----------|---------|
| Solar Radiation | TerraClimate (IDAHO_EPSCOR/TERRACLIMATE) | ~4 km | Mean downward surface shortwave radiation (2018–2022) |
| Digital Elevation Model | SRTM GL1 (USGS/SRTMGL1_003) | 30 m | Elevation, slope, and aspect calculation |
| Land Cover | ESA WorldCover v200 | 10 m | Land surface classification for suitability weighting |
| Protected Areas | WDPA (WCMC/WDPA/current/polygons) | Vector | Exclusion of national parks and nature reserves |

## Methodology

### Factor Selection and Normalization

1. **Solar Radiation (Weight: 40%)** — Mean annual downward shortwave radiation from TerraClimate (2018–2022) is normalized to a 0–1 scale using min-max rescaling. Higher radiation values receive higher suitability scores.

2. **Slope (Weight: 20%)** — Derived from SRTM DEM. Slope suitability follows a linear decay function where 0° = 1.0 and 15° = 0.0. Slopes exceeding 15° are excluded entirely via the constraint mask.

3. **Aspect (Weight: 10%)** — South-facing slopes (135°–225°) are optimal for solar PV in the northern hemisphere and receive a score of 1.0. Southeast and southwest aspects score 0.7, and all other aspects score 0.3.

4. **Land Cover (Weight: 30%)** — ESA WorldCover classes are remapped to suitability values:
   - Bare/sparse land: 1.0 (ideal)
   - Shrubland: 0.8
   - Grassland: 0.7
   - Cropland: 0.4
   - Built-up: 0.1
   - Tree cover, water, snow/ice, wetlands: 0.0 (excluded)

### Constraints

Three binary constraint layers are applied multiplicatively:
- **Protected Areas:** All WDPA polygons within the study area are masked out.
- **Unsuitable Land Cover:** Water bodies, snow/ice, and wetlands are excluded.
- **Steep Slopes:** Terrain exceeding 15° gradient is removed.

### Suitability Index

The final suitability score is computed as a weighted linear combination:

```
Suitability = (SolarRad × 0.40 + LandCover × 0.30 + Slope × 0.20 + Aspect × 0.10) × ConstraintMask
```

All constraint-masked pixels receive a score of 0 regardless of their factor values.

## Key Formulas

**Min-Max Normalization:**

```
X_norm = (X - X_min) / (X_max - X_min)
```

**Slope Suitability (linear decay):**

```
Slope_Suit = clamp(1 - slope / 15, 0, 1)
```

## Results

The analysis produces a continuous suitability raster (0–1) for Punjab province.

> *Figure 1: Solar site suitability map of Punjab. Dark green areas indicate highly suitable sites (score > 0.7), typically corresponding to bare or shrubland with low slope and high solar radiation. Red areas represent unsuitable or constrained zones.*

> *Figure 2: Exclusion mask showing protected areas, water bodies, and steep slopes removed from consideration.*

The base suitability layer is intended for further refinement in ArcGIS Pro or QGIS, where proximity to existing transmission infrastructure and road networks can be incorporated as additional weighted criteria.

## How to Reproduce

1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Create a new script and paste the contents of `GEE_Solar_Site_Suitability.js`.
3. **Important:** Change `ADM0_NAME` from `'India'` to `'Pakistan'` on line 12 of the script to target Punjab, Pakistan.
4. Adjust the study area by modifying the `ADM1_NAME` filter if needed.
5. Click **Run** and inspect the Console output and Map layers.
6. Go to the **Tasks** tab and click **Run** for the export.
7. Download the GeoTIFF from your Google Drive.
8. Open in ArcGIS Pro or QGIS.
9. Apply a red-yellow-green color ramp (red = poor, green = good).
10. Create a layout with legend, scale bar, north arrow, and title.
11. Export as PDF or PNG at 300 DPI.

## Accuracy Assessment

A formal accuracy assessment was not performed for this MCDA model. Sensitivity analysis of the factor weights is recommended to understand how changes in weighting affect the final suitability classification. Ground-truth validation through field visits to top-ranked sites would provide the strongest validation.

## Limitations

- **Coarse climate data:** TerraClimate solar radiation data has a ~4 km spatial resolution, which may miss local-scale variability.
- **Subjective weighting:** The analytical weights (40/30/20/10) are based on literature review and expert judgment rather than empirical optimization.
- **No grid proximity analysis:** Distance to transmission infrastructure is a critical siting factor but must be modeled separately in a desktop GIS.
- **Static analysis:** This assessment does not account for future climate scenarios or land-use change.
- **Administrative boundary artifact:** The GAUL 2015 level-1 boundary for Punjab may not match current administrative divisions.

## Learning Outcomes

This project demonstrates the following skills:

- Multi-Criteria Decision Analysis (MCDA) in Google Earth Engine
- Satellite-derived solar radiation assessment using TerraClimate
- Terrain analysis (slope, aspect) from SRTM DEM
- Land cover reclassification and suitability mapping
- Constraint-based exclusion modeling
- Export and visualization of suitability rasters for GIS refinement

## Files in This Folder

| File | Description |
|------|-------------|
| `GEE_Solar_Site_Suitability.js` | Google Earth Engine JavaScript code for MCDA analysis |
| `README.md` | This document — project documentation and reproduction guide |
| `step_by_step_guide.txt` | Step-by-step instructions for reproduction in QGIS/ArcGIS Pro |
| `outputs/` | Folder for exported GeoTIFFs and final map layouts (populated after running the analysis) |

## Google Earth Engine Code

```javascript
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
```
