# 02 â€” Tropical-Cyclone Rainfall and Track Analysis

## Case study and question
**Cyclone Biparjoy, Arabian Sea, June 2023.** How did satellite-observed rainfall vary with storm intensity, translation speed, distance from the storm centre and landfall?

## Minimum viable study
Use IBTrACS best-track points and GPM IMERG from 7â€“18 June 2023. Analyse the northern Arabian Sea and Sindhâ€“Gujarat landfall region. Make time windows pre-landfall, landfall day and 48 hours post-landfall.

## Methods
1. Download IBTrACS v4 and filter the selected storm/basin; keep time, latitude, longitude, maximum sustained wind, pressure and status fields.
2. Harmonise timestamps to UTC; never infer intensity where the track has missing values.
3. Sum IMERG rainfall in fixed 24-hour windows and plot the track over each map.
4. Calculate storm translation speed from consecutive positions, clearly noting temporal spacing.
5. Optional: reproject rainfall to a storm-centred coordinate system and composite annular mean rainfall by intensity category.
6. Annotate landfall time/location from a cited authoritative source.

## Outputs
- Track + intensity time-series graphic
- Three GPM rainfall maps (before / near / after landfall)
- Rainfall versus intensity and translation-speed chart
- Brief interpretation and limitations

## Data / caveats
Use IBTrACS (NOAA/NCEI), GPM IMERG Final and ERA5 only if weather context is added. Do not infer wind, surge, damage or causality from precipitation maps. IMERG sampling, overpass/retrieval uncertainty, coastal pixels and storm-centre positional error are limitations.

## Individual contribution
> I integrated best-track and satellite rainfall data, produced track-aware rainfall analyses, and interpreted results within product uncertainty.
---

## Environment Setup

Using pip:

```bash
pip install -r requirements.txt
```

Using conda:

```bash
conda env create -f environment.yml
conda activate biparjoy-rainfall-analysis
```

## Project Structure

```text
biparjoy-rainfall-analysis/
|-- README.md
|-- requirements.txt
|-- environment.yml
|-- data/
|   |-- raw/
|   |   |-- ibtracs/
|   |   `-- boundary/
|   `-- processed/
|-- notebooks/
|   |-- 01_data_acquisition.ipynb
|   |-- 02_track_kinematics.ipynb
|   |-- 03_precipitation_stats.ipynb
|   `-- 04_figure_generation.ipynb
|-- src/
|   |-- __init__.py
|   |-- gee_utils.py
|   |-- track_utils.py
|   `-- visualization.py
`-- outputs/
    |-- figures/
    `-- tables/
```
