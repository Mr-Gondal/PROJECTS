# REDO INSTRUCTIONS — GIS & Remote Sensing Portfolio

Use this file as a prompt for any AI to generate proper project files from scratch.
This tells you (the user) and the AI exactly what to do.

---

## 1. Alternative Ways to Represent GIS Data (Instead of Interactive Dashboards)

You don't need an interactive HTML dashboard. Here are better, more honest options:

| Method | What You Do | Tools Needed | Portfolio Impact |
|--------|------------|-------------|-----------------|
| **Static Map Layout** | Export a proper map with legend, scale bar, north arrow, title | ArcGIS Pro / QGIS | Professional, standard |
| **PDF Report** | Full write-up: intro, data, methodology, results, discussion | Word/LaTeX + maps | Shows writing + analysis |
| **Google Earth Engine App** | Deploy your GEE script as a web app directly on GEE | GEE Code Editor > Apps | Shows GEE mastery |
| **Story Map** | Scrollable narrative with embedded maps, text, images | ESRI Story Maps / Mapbox | Excellent for portfolio |
| **Jupyter Notebook** | Python-based analysis with code + maps inline | Jupyter + folium/geopandas | Shows coding + GIS |
| **Leaflet Web Map** | Lightweight interactive map loading actual GeoTIFF tiles | Leaflet.js + QGIS (tiles) | Real data, not fake |
| **Static Infographic** | Single-page visual summary combining charts + maps | Illustrator / Canva | Portfolio-friendly |
| **Video Screen Recording** | Walk through your GEE script + ArcGIS maps on video | OBS / Screen recorder | Shows you did the work |

### Recommended: Mix & Match

```
Project = GEE Script (real code) + Static Maps (from QGIS) + 1-page Report (PDF)
```

This is honest (the maps come from real data), professional (proper cartography), and defensible (you can explain every step).

---

## 2. Prompt for AI: "Write a Proper README for Each Project"

Copy and paste this prompt for each of the 5 folders:

---

### PROMPT START (copy this)

You are a GIS professional helping build a portfolio project. Write a detailed `README.md` file for the folder `[FOLDER NAME]`.

**Context:**
- Author: Haris Hussain, Space Science, University of the Punjab, Lahore
- The project involves satellite remote sensing and GIS analysis
- The Google Earth Engine (GEE) JavaScript code is provided in a `.js` file in the same folder
- The analysis uses real satellite data (Sentinel-2 / Landsat / Hansen / SRTM)
- Output maps are exported from GEE and styled in ArcGIS Pro or QGIS
- All maps in the README should be described as static exports (GeoTIFFs styled in GIS software)
- NO fake interactive dashboards — only real GEE analysis + static maps

**Requirements for the README:**

1. **Title and Author** — Project name, author name, institution, date
2. **Overview** — 2-3 paragraphs explaining what the project does and why it matters (Pakistan-specific context)
3. **Data Sources** — Table listing satellite data used, resolution, source URL, purpose
4. **Methodology** — Step-by-step workflow:
   - Data acquisition (GEE code explanation)
   - Pre-processing (cloud masking, mosaicking, etc.)
   - Analysis (index calculation, classification, change detection)
   - Post-processing (export, styling in GIS)
5. **Key Formulas** — Any indices or equations used (NDVI, NDWI, NDBI, etc.) in LaTeX or code blocks
6. **Results** — Describe what the exported maps show. Use placeholder text like:
   > *"Figure 1: NDVI map of Punjab agricultural zones. Green areas show healthy vegetation (NDVI > 0.6), red areas show stressed or bare land."*
7. **How to Reproduce** — Step-by-step instructions:
   - Open GEE Code Editor
   - Copy-paste the `.js` file
   - Adjust the AOI if needed
   - Click Run
   - Go to Tasks tab → Run exports
   - Download GeoTIFFs from Google Drive
   - Open in ArcGIS Pro / QGIS
   - Apply symbology (specify color ramps and classification)
   - Create layout with legend, scale bar, north arrow
   - Export as PDF or PNG
8. **Accuracy Assessment** (if applicable) — Overall accuracy, kappa coefficient, confusion matrix
9. **Limitations** — Honest discussion of what the analysis doesn't capture
10. **Learning Outcomes** — What skills this project demonstrates
11. **Files in this folder** — List of files and what each does

**Tone:** Professional, technical, honest. Do NOT overclaim. Use phrases like "this analysis demonstrates" rather than "this project delivers."

**Output format:** Pure Markdown (`.md`). Use tables, code blocks, headings, and bullet points.

### PROMPT END

---

## 3. GEE Code to Include in Each README

Paste the contents of each `.js` file into the README under a section called "## Google Earth Engine Code" using a JavaScript code block. This way the README is self-contained and the user doesn't need to open separate files.

```markdown
## Google Earth Engine Code

```javascript
// paste the entire .js file content here
```
```

---

## 4. How to Redo Each Project from Scratch (For the User)

### Step 1: Clean up

```powershell
# Remove old trace files (already done for NDVI folder)
# Check others:
Get-ChildItem -Recurse -Filter "prompt.txt" -Path "."
Get-ChildItem -Recurse -Filter ".qwen" -Path "." -Directory
# Delete any found
```

### Step 2: Fix the GEE Scripts

| Project | Fix Needed |
|---------|-----------|
| 1. NDVI | ✅ Already solid — just run it as-is |
| 2. Deforestation | ✅ Already solid — just run it as-is |
| 3. Flood Hazard | Rewrite — use Pakistan study area, not US sample coordinates |
| 4. Solar Suitability | Fix ADM0_NAME from 'India' to 'Pakistan', expand analysis |
| 5. Urban Sprawl | Add real training polygons (minimum 20 per class), not 4 points |

### Step 3: Run Each GEE Script

1. Go to https://code.earthengine.google.com/
2. Create new script, paste the `.js` content
3. Adjust AOI to your study area
4. Click Run
5. Check Console tab for output
6. Go to Tasks tab → click Run for each export
7. Wait for exports to complete
8. Download GeoTIFFs from Google Drive

### Step 4: Style Maps in QGIS (Free) or ArcGIS Pro

For each GeoTIFF:
1. Open GIS software
2. Add raster layer
3. Right-click → Properties → Symbology
4. Choose appropriate color ramp:
   - NDVI: Red-Yellow-Green (red = low, green = high)
   - Land cover: Categorical colors
   - Change detection: Red for loss, Green for gain
   - Suitability: Red-Yellow-Green (red = poor, green = good)
5. Create Layout:
   - Add map frame
   - Add legend
   - Add scale bar
   - Add north arrow
   - Add title
   - Add your name and date
6. Export as PNG/PDF (300 DPI)

### Step 5: Write the README

Use the AI prompt from Section 2 above. Then manually review and edit — make sure you understand every sentence.

### Step 6: Test Your Knowledge

Before putting anything in your portfolio, be able to answer:

- ❓ "What does this band combination show?"
- ❓ "Why did you use a 20% cloud filter?"
- ❓ "What's the difference between NDVI and EVI?"
- ❓ "How many training samples did you use?"
- ❓ "What's the spatial resolution of your output?"

If you stumble on any of these, study that topic before presenting the project.

---

## 5. Folder Structure After Redo

Each project folder should contain:

```
Project Name/
├── README.md             ← Self-contained (includes GEE code + instructions)
├── gee_script.js         ← The GEE JavaScript code (also inside README)
├── step_by_step_guide.txt ← How to reproduce in QGIS/ArcGIS
└── outputs/              ← Folder for exported maps (optional)
    ├── ndvi_map_2024.png
    ├── classification_2024.png
    └── ...
```

No `.qwen/` folders, no `prompt.txt`, no AI trace files.

---

## 6. Interview Defense Script

For each project, memorize this 30-second pitch:

> *"For this project, I used [satellite data] over [region] from [year] to [year]. I processed it in Google Earth Engine using [technique: NDVI / Random Forest / change detection]. The output rasters were exported and styled in [QGIS / ArcGIS Pro] to produce the final classification maps. The main finding was [key result]. One limitation is [honest limitation], and with more time I would [improvement]."*

Practice this until it sounds natural, not memorized.
