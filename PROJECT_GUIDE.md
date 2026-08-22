# 🌙 NIDHI Project: Complete Guide (Start to Finish)
**Navigation, Ice Detection, and Hazard Integration**
*Team OUTLIERs | SIH26_76*

---

> **How to read this document:** Think of this as your personal Wikipedia for the whole project.
> Every section explains the "what", the "why", and the "how" in plain English.
> Technical terms are explained the moment they are introduced.

---

## Part 1: What is the Big Problem We Are Solving?

### 1.1 The Moon's South Pole — Why Does Everyone Care?

The Moon's South Pole has craters so deep that sunlight **never reaches their floors**. These are called **Permanently Shadowed Regions (PSRs)**. Because they are permanently dark, they are extremely cold (around -200°C). At these temperatures, water ice can survive for **billions of years** without evaporating.

This matters enormously because:
- Water = Drinking water for astronauts on a future Moon base.
- Water (H₂O) can be split into **Hydrogen (fuel)** and **Oxygen (air to breathe)**.
- Mining ice on the Moon is **vastly cheaper** than launching water from Earth.

ISRO (India), NASA (USA), China, and others are all targeting the South Pole for this exact reason. India's Chandrayaan-3 already landed near the south pole in 2023.

### 1.2 The Problem Isn't Just "Find Ice" — It's Much Harder

Scientists use **radar satellites** to look for ice. The radar sends a signal down to the Moon and listens to how the signal bounces back. Ice and rough rocks can bounce the signal back in similar ways. This causes **false positives** — the radar says "there's ice here!" but it's actually just a bumpy rock.

So the problem has **four layers**:
1. ❓ **Where is the ice?** (and how do we avoid false positives from rocks?)
2. ❓ **Where is it safe to land nearby?** (the PSRs themselves are too dark and steep to land inside)
3. ❓ **Where are the boulders and craters** that could destroy a rover?
4. ❓ **What is the safest driving route** for the rover from the landing site into the crater?

Existing research papers solve each of these **one at a time**, separately. Nobody has ever built a single, automated system that answers all four questions together. **That is exactly what NIDHI does.**

---

## Part 2: Our Data — What Raw Material Are We Working With?

Think of our data like raw ingredients before cooking. We have three major data sources.

### 2.1 Chandrayaan-2 DFSAR — The Radar Sensor

**What it is:** DFSAR stands for **Dual Frequency Synthetic Aperture Radar**. It is the radar instrument on board India's Chandrayaan-2 spacecraft, which is still orbiting the Moon right now.

**What it does:** It beams radar pulses (radio waves) at the Moon's surface and measures how they bounce back. It does this in two different frequencies (**L-band and S-band**). L-band waves are longer and can penetrate deeper into the surface (about 2-3 meters), which is what makes them useful for detecting **subsurface ice**.

**What we actually downloaded:** We downloaded real DFSAR data from ISRO's PRADAN portal. The files are huge:
- The raw radar file (`ch2_sar_nrxl...d18.dat`) is **2,785 MB** (nearly 3 GB).
- The L4-MOSAIC product (processed radar maps) is **4.5 GB** as a ZIP file.

**The specific data layers we use from DFSAR:**

| Layer Name | Technical Name | What it represents in plain English |
|---|---|---|
| **CPR** | Circular Polarization Ratio | A number that goes high when the radar signal bounces around many times (scatters "volumetrically"). High CPR in a PSR = possible ice. |
| **Volume Scattering (VOL)** | Yamaguchi VOL component | The amount of the radar signal that scattered inside the surface, not on top. High VOL = likely subsurface structure (possibly ice). |
| **SERD** | Single-bounce Eigenvalue Relative Difference | A roughness indicator. It tells us if a surface is smooth or rough. Crucial for filtering out false positives from rocks. |
| **T-Ratio** | T-Ratio | Related to the dielectric constant (how the material interacts with radar). Ice and rock have different dielectric properties. |
| **EVN, ODD, HLX** | Even-bounce, Odd-bounce, Helix | Other scattering components. Used together to understand the surface type. |

**Our actual data coverage:** The downloaded L4-MOSAIC covers the region from **75.6°S to 89.7°S** (basically the entire lunar south polar cap) at **25 meters per pixel**. Each image is **24,181 × 24,794 pixels** — enormous.

### 2.2 NASA LOLA DEM — The Elevation Map

**What it is:** LOLA stands for **Lunar Orbiter Laser Altimeter**, a NASA instrument that precisely measured the height of the entire lunar surface by bouncing laser pulses off it.

**What a DEM is:** DEM stands for **Digital Elevation Model**. Think of it as a highly detailed topographic map — essentially a grid where every pixel stores the exact height of the surface at that location.

**Why we need it:** Without knowing the terrain's shape (slopes, cliff edges, crater rims), we can't:
- Calculate if a slope is safe enough to land on.
- Find the permanent shadow zones (which require knowing where the sun can't shine based on terrain shape).
- Route the rover around steep drops.

### 2.3 PSR Catalogue — The Shadow Map

**What it is:** A pre-made shapefile (a vector map) published by the LROC team at Arizona State University. It contains **653 polygon shapes** — each polygon is the outline of a single Permanently Shadowed Region crater floor.

**Why we need it:** We use this as a "gate." We only look for ice **inside PSRs** because that's the only place it's thermally stable. This drastically reduces the number of pixels we need to analyze, from millions to thousands.

---

## Part 3: What Has Been Done So Far (The Notebook Work)

This is the work done in the Jupyter Notebook (`Untitled3.ipynb`) running on Google Colab with Google Drive.

### 3.1 Step 1: Getting and Unpacking the Data

**What was done:**
- Connected Google Colab to Google Drive where the data files were stored.
- Found the massive ZIP files (DFSAR data, PSR catalogue).
- Wrote Python code to inspect and extract only the specific TIF layers needed (`evn`, `vol`, `odd`, `hlx`, `cpr`, `serd`, `trt`), avoiding wasting hours extracting files we don't need.

**Tools used:** Python's built-in `zipfile` library, `os` library.

**Key finding:** The L4-MOSAIC ZIP was 4.5 GB and contained four massive GeoTIFF files (~2.2 GB each). Extraction took about 7-8 minutes.

---

### 3.2 Step 2: Understanding the Data Structure

**What was done:**
- Opened each TIF file using `rasterio` (a Python library for reading satellite map files).
- Checked the dimensions, coordinate system, and data ranges of each layer.

**Key findings from the notebook:**
- All four layers (`evn`, `vol`, `odd`, `hlx`) are perfectly co-registered (same size, same coordinates). This means they are already aligned perfectly on top of each other — no extra alignment work needed for these layers.
- The coordinate system is **Moon 2000 South Pole Stereographic** — a projection designed specifically for looking at the south pole from directly above.
- Initial stats showed `min=0.0000` and `max=0.0000`, which seemed alarming (all zeros?). On closer inspection with 10 decimal places, the actual values are extremely small numbers (like `8.7e-12` to `2e-08`). This is normal for radar power values in linear scale.

**Key insight:** The data was **not in dB scale** (decibels). Raw radar power is always in linear scale (tiny numbers). To visualize it meaningfully, you convert to dB using the formula `10 * log10(value)`. The notebook added this conversion.

---

### 3.3 Step 3: First Visualization

**What was done:**
- Downsampled each 24,000×24,000 pixel image to 1,500×1,500 pixels (for speed).
- Converted all four layers to dB scale.
- Plotted them as four side-by-side images (called a 2×2 subplot grid).

**What the visualization showed:** A visual map of the entire lunar south polar region color-coded by each scattering type. Bright spots (in VOL map) inside dark areas (PSRs) are the first hint of ice candidates.

---

### 3.4 Step 4: The Screening Pipeline (The Main Work — from the Objective 1 Report)

This is the core scientific analysis. Here is what the pipeline did, step by step:

#### Step 4a: Computing Volume Scattering Fraction
**Formula:** `Pv = VOL / (EVN + VOL + ODD + HLX)`

This creates a single number per pixel between 0 and 1 that says: "Of all the radar energy that bounced back, what fraction bounced around *inside* the surface?" A high number (close to 1) means most energy scattered volumetrically — which is the signature of ice or a porous subsurface structure.

#### Step 4b: PSR Gating
The PSR catalogue was "rasterized" — meaning the vector polygon shapes were converted into a pixel mask on the same grid as the radar data. Only pixels that fall **inside a PSR polygon** are analyzed. This reduced the millions of pixels to only those in permanently dark zones.

#### Step 4c: Shortlisting Candidate Craters
The entire south pole area was scanned at overview resolution. Any PSR region with an unusually high volume scattering fraction was flagged. **Seven candidate PSRs** were initially shortlisted.

#### Step 4d: Multi-indicator Testing (The Filter)
Each of the 7 candidates was then tested against **four independent physical indicators**:
1. **Volume Scattering (VOL):** Is it genuinely high inside the PSR compared to outside?
2. **CPR (Circular Polarization Ratio):** Is it elevated? (CPR > 1 is the classic ice indicator.)
3. **SERD (Roughness):** Is the surface smooth? If CPR is high but SERD is also high (very rough surface), it's probably just a rough rock, not ice. This is the anti-false-positive filter.
4. **T-Ratio (Dielectric proxy):** Does it behave like a low-dielectric material (ice has a very low dielectric constant ~3.15, dry rock is much higher)?

#### Step 4e: Visual Inspection at Full Resolution
Each shortlisted candidate was zoomed into at the full 25 m/pixel resolution to visually check if the anomaly is spatially coherent (a real, floor-filling signal) or just random noise pixels.

#### The Result:
- **1 candidate PASSED all 4 checks:** PSR ID `SP_840980_0797630` at coordinates **84.098°S, 79.764°E**. It showed a spatially coherent, floor-concentrated anomaly.
- **2 candidates showed positive stats but failed visual inspection** → downgraded.
- **4 candidates were ruled out** by convergent negative evidence.

> ⚠️ **Important disclaimer (directly from the report):** "This is a screened radar candidate, not a confirmed ice detection." Radar alone cannot 100% confirm ice — that requires a rover physically drilling into the surface. But it IS the scientifically sound, state-of-the-art method for narrowing down the search.

---

## Part 4: What Is Planned Next (The Remaining 3 Objectives)

The Objective 1 report explicitly states that Objectives 2-4 are separate, downstream work. Here is what they involve:

### 4.1 Objective 2: Hazard Mapping (OHRC Imagery)

**What:** Use Chandrayaan-2 OHRC (Optical High Resolution Camera) images of the area around the candidate PSR to map surface hazards.

**How:**
- Ingest high-resolution optical images of the crater rim area (outside the dark PSR).
- Run image processing to detect boulders, small craters, and steep rock faces.
- Overlay this with DEM slope calculations (from LOLA) to find areas where the slope exceeds safe landing angles.
- Output: A **Hazard Mask** — a map where every unsafe pixel is marked red.

**Tech used:** `Rasterio`, `OpenCV` (for image processing), `NumPy`.

### 4.2 Objective 3: Landing Site Selection

**What:** Find the best spot to actually put the lander down, just outside the dark PSR.

**How:** For the area around the candidate PSR, score every potential landing ellipse (a 100m × 100m zone) based on:
- **Slope Safety:** Is the ground flat enough? (Requirement: slope < ~5°)
- **Solar Power:** How many hours per lunar day does this spot receive sunlight? (Landers need solar power.)
- **Proximity to Ice:** How close is this spot to the `SP_840980_0797630` ice candidate?

**Output:** A ranked list of the **top 3 candidate landing sites** with their scores.

### 4.3 Objective 4: Rover Traverse Planning

**What:** Plot the rover's driving path from the landing site into the crater to reach the ice.

**How:** Using the A* (A-Star) pathfinding algorithm on a grid built from the DEM:
- Every pixel in the grid has a "movement cost."
- Cost = `(Slope Penalty) + (Hazard Penalty) − (Ice Proximity Reward)`
- A* explores the grid and finds the path with the lowest total cost.
- Also estimates total accessible ice volume using the area of the anomaly and the L-band radar penetration depth (~2-3 meters).

**Tools used:** `NetworkX` (for the graph/pathfinding math), `NumPy` (for the cost grid).

---

## Part 5: The Software Stack — How It All Connects

```
┌─────────────────────────────────────────────────┐
│          DATA SOURCES (The Raw Ingredients)     │
│  ISRO PRADAN (DFSAR) + NASA PDS (LOLA DEM)      │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         PROCESSING LAYER (The Kitchen)          │
│  Python + Rasterio + GDAL                       │
│  - Unzip, read, align, normalize satellite data  │
│  - Store in PostgreSQL + PostGIS database        │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         AI & COMPUTE ENGINE (The Brain)         │
│                                                 │
│  🧠 ICE DETECTION:                              │
│  Scikit-learn Isolation Forest (Anomaly Detect) │
│  Features: CPR + SERD + VOL + T-Ratio           │
│  Output: Ice Probability Map (0.0 → 1.0)        │
│                                                 │
│  🗺️ HAZARD MAPPING:                            │
│  YOLOv8 / CNN on OHRC imagery                   │
│  Output: Boulder + Slope Hazard Mask            │
│                                                 │
│  🚀 LANDING SITE SCORER:                        │
│  Weighted scoring matrix on DEM + proximity     │
│  Output: Top 3 Landing Sites                    │
│                                                 │
│  🛣️ PATHFINDING:                               │
│  NetworkX A* on weighted terrain graph          │
│  Output: Optimal rover waypoints                │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         BACKEND API (The Waiter)                │
│  FastAPI (Python)                               │
│  - Serves maps, paths, scores as JSON/GeoJSON   │
│  - The bridge between the compute engine        │
│    and the visual dashboard                     │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         MISSION CONTROL DASHBOARD (The Display) │
│  Next.js + React + Tailwind CSS                 │
│  - Deck.gl for interactive 2D/3D map layers     │
│  - Three.js for 3D crater terrain model         │
│  - User toggles between: CPR heatmap,           │
│    Ice probability map, Hazard mask, Rover path │
└─────────────────────────────────────────────────┘
```

---

## Part 6: Key Scientific Terms Glossary

| Term | Plain English Explanation |
|---|---|
| **PSR** | Permanently Shadowed Region. A crater floor that never sees sunlight. The only place ice can survive on the Moon. |
| **DFSAR** | Chandrayaan-2's radar instrument. Sends radio waves at the Moon and listens for echoes. |
| **CPR** | Circular Polarization Ratio. A number that gets high when radar signals bounce around many times inside a material (ice does this). |
| **SERD** | A roughness measure. Helps us tell the difference between a rough rock (which also has high CPR) and actual ice. |
| **L-band** | A long-wavelength radar signal (~24 cm). Long wavelengths penetrate deeper into the surface (~2-3 m), useful for subsurface ice. |
| **Isolation Forest** | An unsupervised ML algorithm that detects anomalies. We use it to find pixels that are statistically completely different from normal lunar terrain (ice candidates). |
| **A\*** | A-Star algorithm. A classic AI pathfinding algorithm. Finds the cheapest/safest path through a grid. Like GPS, but for a Moon rover. |
| **DEM** | Digital Elevation Model. A map where each pixel stores the height of the terrain at that spot. |
| **GeoTIFF** | A standard image file format for satellite data that includes embedded coordinate information (so the image can be placed on a map). |
| **PostGIS** | An extension to PostgreSQL that lets you store and query map/spatial data (like "find all pixels within this crater outline"). |
| **FastAPI** | A Python library for building fast web APIs. Your compute results are served through FastAPI to the frontend. |
| **Deck.gl** | A JavaScript library (from Uber) for rendering large-scale geospatial maps in the browser, including 3D terrain. |

---

## Part 7: Current Status Summary

| Objective | Status | Key Output |
|---|---|---|
| **Obj 1: Ice Detection** | ✅ DONE | 1 confirmed ice candidate: PSR `SP_840980_0797630` at 84.098°S, 79.764°E |
| **Obj 2: Hazard Mapping** | 🔄 PLANNED | Hazard mask from OHRC imagery + DEM slopes |
| **Obj 3: Landing Site** | 🔄 PLANNED | Top 3 ranked landing sites near the candidate PSR |
| **Obj 4: Rover Traverse** | 🔄 PLANNED | Optimal waypoints from landing site to ice + volume estimate |
| **Backend API** | 🔄 PLANNED | FastAPI serving all outputs to dashboard |
| **Frontend Dashboard** | 🔄 PLANNED | Next.js 3D mission control UI |

The scientific backbone (Objective 1) is DONE with real ISRO data. The hackathon work is now about turning that into a functional software demo with the dashboard.# 🌙 NIDHI Project: Complete Guide (Start to Finish)
**Navigation, Ice Detection, and Hazard Integration**
*Team OUTLIERs | SIH26_76*

---

> **How to read this document:** Think of this as your personal Wikipedia for the whole project.
> Every section explains the "what", the "why", and the "how" in plain English.
> Technical terms are explained the moment they are introduced.

---

## Part 1: What is the Big Problem We Are Solving?

### 1.1 The Moon's South Pole — Why Does Everyone Care?

The Moon's South Pole has craters so deep that sunlight **never reaches their floors**. These are called **Permanently Shadowed Regions (PSRs)**. Because they are permanently dark, they are extremely cold (around -200°C). At these temperatures, water ice can survive for **billions of years** without evaporating.

This matters enormously because:
- Water = Drinking water for astronauts on a future Moon base.
- Water (H₂O) can be split into **Hydrogen (fuel)** and **Oxygen (air to breathe)**.
- Mining ice on the Moon is **vastly cheaper** than launching water from Earth.

ISRO (India), NASA (USA), China, and others are all targeting the South Pole for this exact reason. India's Chandrayaan-3 already landed near the south pole in 2023.

### 1.2 The Problem Isn't Just "Find Ice" — It's Much Harder

Scientists use **radar satellites** to look for ice. The radar sends a signal down to the Moon and listens to how the signal bounces back. Ice and rough rocks can bounce the signal back in similar ways. This causes **false positives** — the radar says "there's ice here!" but it's actually just a bumpy rock.

So the problem has **four layers**:
1. ❓ **Where is the ice?** (and how do we avoid false positives from rocks?)
2. ❓ **Where is it safe to land nearby?** (the PSRs themselves are too dark and steep to land inside)
3. ❓ **Where are the boulders and craters** that could destroy a rover?
4. ❓ **What is the safest driving route** for the rover from the landing site into the crater?

Existing research papers solve each of these **one at a time**, separately. Nobody has ever built a single, automated system that answers all four questions together. **That is exactly what NIDHI does.**

---

## Part 2: Our Data — What Raw Material Are We Working With?

Think of our data like raw ingredients before cooking. We have three major data sources.

### 2.1 Chandrayaan-2 DFSAR — The Radar Sensor

**What it is:** DFSAR stands for **Dual Frequency Synthetic Aperture Radar**. It is the radar instrument on board India's Chandrayaan-2 spacecraft, which is still orbiting the Moon right now.

**What it does:** It beams radar pulses (radio waves) at the Moon's surface and measures how they bounce back. It does this in two different frequencies (**L-band and S-band**). L-band waves are longer and can penetrate deeper into the surface (about 2-3 meters), which is what makes them useful for detecting **subsurface ice**.

**What we actually downloaded:** We downloaded real DFSAR data from ISRO's PRADAN portal. The files are huge:
- The raw radar file (`ch2_sar_nrxl...d18.dat`) is **2,785 MB** (nearly 3 GB).
- The L4-MOSAIC product (processed radar maps) is **4.5 GB** as a ZIP file.

**The specific data layers we use from DFSAR:**

| Layer Name | Technical Name | What it represents in plain English |
|---|---|---|
| **CPR** | Circular Polarization Ratio | A number that goes high when the radar signal bounces around many times (scatters "volumetrically"). High CPR in a PSR = possible ice. |
| **Volume Scattering (VOL)** | Yamaguchi VOL component | The amount of the radar signal that scattered inside the surface, not on top. High VOL = likely subsurface structure (possibly ice). |
| **SERD** | Single-bounce Eigenvalue Relative Difference | A roughness indicator. It tells us if a surface is smooth or rough. Crucial for filtering out false positives from rocks. |
| **T-Ratio** | T-Ratio | Related to the dielectric constant (how the material interacts with radar). Ice and rock have different dielectric properties. |
| **EVN, ODD, HLX** | Even-bounce, Odd-bounce, Helix | Other scattering components. Used together to understand the surface type. |

**Our actual data coverage:** The downloaded L4-MOSAIC covers the region from **75.6°S to 89.7°S** (basically the entire lunar south polar cap) at **25 meters per pixel**. Each image is **24,181 × 24,794 pixels** — enormous.

### 2.2 NASA LOLA DEM — The Elevation Map

**What it is:** LOLA stands for **Lunar Orbiter Laser Altimeter**, a NASA instrument that precisely measured the height of the entire lunar surface by bouncing laser pulses off it.

**What a DEM is:** DEM stands for **Digital Elevation Model**. Think of it as a highly detailed topographic map — essentially a grid where every pixel stores the exact height of the surface at that location.

**Why we need it:** Without knowing the terrain's shape (slopes, cliff edges, crater rims), we can't:
- Calculate if a slope is safe enough to land on.
- Find the permanent shadow zones (which require knowing where the sun can't shine based on terrain shape).
- Route the rover around steep drops.

### 2.3 PSR Catalogue — The Shadow Map

**What it is:** A pre-made shapefile (a vector map) published by the LROC team at Arizona State University. It contains **653 polygon shapes** — each polygon is the outline of a single Permanently Shadowed Region crater floor.

**Why we need it:** We use this as a "gate." We only look for ice **inside PSRs** because that's the only place it's thermally stable. This drastically reduces the number of pixels we need to analyze, from millions to thousands.

---

## Part 3: What Has Been Done So Far (The Notebook Work)

This is the work done in the Jupyter Notebook (`Untitled3.ipynb`) running on Google Colab with Google Drive.

### 3.1 Step 1: Getting and Unpacking the Data

**What was done:**
- Connected Google Colab to Google Drive where the data files were stored.
- Found the massive ZIP files (DFSAR data, PSR catalogue).
- Wrote Python code to inspect and extract only the specific TIF layers needed (`evn`, `vol`, `odd`, `hlx`, `cpr`, `serd`, `trt`), avoiding wasting hours extracting files we don't need.

**Tools used:** Python's built-in `zipfile` library, `os` library.

**Key finding:** The L4-MOSAIC ZIP was 4.5 GB and contained four massive GeoTIFF files (~2.2 GB each). Extraction took about 7-8 minutes.

---

### 3.2 Step 2: Understanding the Data Structure

**What was done:**
- Opened each TIF file using `rasterio` (a Python library for reading satellite map files).
- Checked the dimensions, coordinate system, and data ranges of each layer.

**Key findings from the notebook:**
- All four layers (`evn`, `vol`, `odd`, `hlx`) are perfectly co-registered (same size, same coordinates). This means they are already aligned perfectly on top of each other — no extra alignment work needed for these layers.
- The coordinate system is **Moon 2000 South Pole Stereographic** — a projection designed specifically for looking at the south pole from directly above.
- Initial stats showed `min=0.0000` and `max=0.0000`, which seemed alarming (all zeros?). On closer inspection with 10 decimal places, the actual values are extremely small numbers (like `8.7e-12` to `2e-08`). This is normal for radar power values in linear scale.

**Key insight:** The data was **not in dB scale** (decibels). Raw radar power is always in linear scale (tiny numbers). To visualize it meaningfully, you convert to dB using the formula `10 * log10(value)`. The notebook added this conversion.

---

### 3.3 Step 3: First Visualization

**What was done:**
- Downsampled each 24,000×24,000 pixel image to 1,500×1,500 pixels (for speed).
- Converted all four layers to dB scale.
- Plotted them as four side-by-side images (called a 2×2 subplot grid).

**What the visualization showed:** A visual map of the entire lunar south polar region color-coded by each scattering type. Bright spots (in VOL map) inside dark areas (PSRs) are the first hint of ice candidates.

---

### 3.4 Step 4: The Screening Pipeline (The Main Work — from the Objective 1 Report)

This is the core scientific analysis. Here is what the pipeline did, step by step:

#### Step 4a: Computing Volume Scattering Fraction
**Formula:** `Pv = VOL / (EVN + VOL + ODD + HLX)`

This creates a single number per pixel between 0 and 1 that says: "Of all the radar energy that bounced back, what fraction bounced around *inside* the surface?" A high number (close to 1) means most energy scattered volumetrically — which is the signature of ice or a porous subsurface structure.

#### Step 4b: PSR Gating
The PSR catalogue was "rasterized" — meaning the vector polygon shapes were converted into a pixel mask on the same grid as the radar data. Only pixels that fall **inside a PSR polygon** are analyzed. This reduced the millions of pixels to only those in permanently dark zones.

#### Step 4c: Shortlisting Candidate Craters
The entire south pole area was scanned at overview resolution. Any PSR region with an unusually high volume scattering fraction was flagged. **Seven candidate PSRs** were initially shortlisted.

#### Step 4d: Multi-indicator Testing (The Filter)
Each of the 7 candidates was then tested against **four independent physical indicators**:
1. **Volume Scattering (VOL):** Is it genuinely high inside the PSR compared to outside?
2. **CPR (Circular Polarization Ratio):** Is it elevated? (CPR > 1 is the classic ice indicator.)
3. **SERD (Roughness):** Is the surface smooth? If CPR is high but SERD is also high (very rough surface), it's probably just a rough rock, not ice. This is the anti-false-positive filter.
4. **T-Ratio (Dielectric proxy):** Does it behave like a low-dielectric material (ice has a very low dielectric constant ~3.15, dry rock is much higher)?

#### Step 4e: Visual Inspection at Full Resolution
Each shortlisted candidate was zoomed into at the full 25 m/pixel resolution to visually check if the anomaly is spatially coherent (a real, floor-filling signal) or just random noise pixels.

#### The Result:
- **1 candidate PASSED all 4 checks:** PSR ID `SP_840980_0797630` at coordinates **84.098°S, 79.764°E**. It showed a spatially coherent, floor-concentrated anomaly.
- **2 candidates showed positive stats but failed visual inspection** → downgraded.
- **4 candidates were ruled out** by convergent negative evidence.

> ⚠️ **Important disclaimer (directly from the report):** "This is a screened radar candidate, not a confirmed ice detection." Radar alone cannot 100% confirm ice — that requires a rover physically drilling into the surface. But it IS the scientifically sound, state-of-the-art method for narrowing down the search.

---

## Part 4: What Is Planned Next (The Remaining 3 Objectives)

The Objective 1 report explicitly states that Objectives 2-4 are separate, downstream work. Here is what they involve:

### 4.1 Objective 2: Hazard Mapping (OHRC Imagery)

**What:** Use Chandrayaan-2 OHRC (Optical High Resolution Camera) images of the area around the candidate PSR to map surface hazards.

**How:**
- Ingest high-resolution optical images of the crater rim area (outside the dark PSR).
- Run image processing to detect boulders, small craters, and steep rock faces.
- Overlay this with DEM slope calculations (from LOLA) to find areas where the slope exceeds safe landing angles.
- Output: A **Hazard Mask** — a map where every unsafe pixel is marked red.

**Tech used:** `Rasterio`, `OpenCV` (for image processing), `NumPy`.

### 4.2 Objective 3: Landing Site Selection

**What:** Find the best spot to actually put the lander down, just outside the dark PSR.

**How:** For the area around the candidate PSR, score every potential landing ellipse (a 100m × 100m zone) based on:
- **Slope Safety:** Is the ground flat enough? (Requirement: slope < ~5°)
- **Solar Power:** How many hours per lunar day does this spot receive sunlight? (Landers need solar power.)
- **Proximity to Ice:** How close is this spot to the `SP_840980_0797630` ice candidate?

**Output:** A ranked list of the **top 3 candidate landing sites** with their scores.

### 4.3 Objective 4: Rover Traverse Planning

**What:** Plot the rover's driving path from the landing site into the crater to reach the ice.

**How:** Using the A* (A-Star) pathfinding algorithm on a grid built from the DEM:
- Every pixel in the grid has a "movement cost."
- Cost = `(Slope Penalty) + (Hazard Penalty) − (Ice Proximity Reward)`
- A* explores the grid and finds the path with the lowest total cost.
- Also estimates total accessible ice volume using the area of the anomaly and the L-band radar penetration depth (~2-3 meters).

**Tools used:** `NetworkX` (for the graph/pathfinding math), `NumPy` (for the cost grid).

---

## Part 5: The Software Stack — How It All Connects

```
┌─────────────────────────────────────────────────┐
│          DATA SOURCES (The Raw Ingredients)     │
│  ISRO PRADAN (DFSAR) + NASA PDS (LOLA DEM)      │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         PROCESSING LAYER (The Kitchen)          │
│  Python + Rasterio + GDAL                       │
│  - Unzip, read, align, normalize satellite data  │
│  - Store in PostgreSQL + PostGIS database        │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         AI & COMPUTE ENGINE (The Brain)         │
│                                                 │
│  🧠 ICE DETECTION:                              │
│  Scikit-learn Isolation Forest (Anomaly Detect) │
│  Features: CPR + SERD + VOL + T-Ratio           │
│  Output: Ice Probability Map (0.0 → 1.0)        │
│                                                 │
│  🗺️ HAZARD MAPPING:                            │
│  YOLOv8 / CNN on OHRC imagery                   │
│  Output: Boulder + Slope Hazard Mask            │
│                                                 │
│  🚀 LANDING SITE SCORER:                        │
│  Weighted scoring matrix on DEM + proximity     │
│  Output: Top 3 Landing Sites                    │
│                                                 │
│  🛣️ PATHFINDING:                               │
│  NetworkX A* on weighted terrain graph          │
│  Output: Optimal rover waypoints                │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         BACKEND API (The Waiter)                │
│  FastAPI (Python)                               │
│  - Serves maps, paths, scores as JSON/GeoJSON   │
│  - The bridge between the compute engine        │
│    and the visual dashboard                     │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         MISSION CONTROL DASHBOARD (The Display) │
│  Next.js + React + Tailwind CSS                 │
│  - Deck.gl for interactive 2D/3D map layers     │
│  - Three.js for 3D crater terrain model         │
│  - User toggles between: CPR heatmap,           │
│    Ice probability map, Hazard mask, Rover path │
└─────────────────────────────────────────────────┘
```

---

## Part 6: Key Scientific Terms Glossary

| Term | Plain English Explanation |
|---|---|
| **PSR** | Permanently Shadowed Region. A crater floor that never sees sunlight. The only place ice can survive on the Moon. |
| **DFSAR** | Chandrayaan-2's radar instrument. Sends radio waves at the Moon and listens for echoes. |
| **CPR** | Circular Polarization Ratio. A number that gets high when radar signals bounce around many times inside a material (ice does this). |
| **SERD** | A roughness measure. Helps us tell the difference between a rough rock (which also has high CPR) and actual ice. |
| **L-band** | A long-wavelength radar signal (~24 cm). Long wavelengths penetrate deeper into the surface (~2-3 m), useful for subsurface ice. |
| **Isolation Forest** | An unsupervised ML algorithm that detects anomalies. We use it to find pixels that are statistically completely different from normal lunar terrain (ice candidates). |
| **A\*** | A-Star algorithm. A classic AI pathfinding algorithm. Finds the cheapest/safest path through a grid. Like GPS, but for a Moon rover. |
| **DEM** | Digital Elevation Model. A map where each pixel stores the height of the terrain at that spot. |
| **GeoTIFF** | A standard image file format for satellite data that includes embedded coordinate information (so the image can be placed on a map). |
| **PostGIS** | An extension to PostgreSQL that lets you store and query map/spatial data (like "find all pixels within this crater outline"). |
| **FastAPI** | A Python library for building fast web APIs. Your compute results are served through FastAPI to the frontend. |
| **Deck.gl** | A JavaScript library (from Uber) for rendering large-scale geospatial maps in the browser, including 3D terrain. |

---

## Part 7: Current Status Summary

| Objective | Status | Key Output |
|---|---|---|
| **Obj 1: Ice Detection** | ✅ DONE | 1 confirmed ice candidate: PSR `SP_840980_0797630` at 84.098°S, 79.764°E |
| **Obj 2: Hazard Mapping** | 🔄 PLANNED | Hazard mask from OHRC imagery + DEM slopes |
| **Obj 3: Landing Site** | 🔄 PLANNED | Top 3 ranked landing sites near the candidate PSR |
| **Obj 4: Rover Traverse** | 🔄 PLANNED | Optimal waypoints from landing site to ice + volume estimate |
| **Backend API** | 🔄 PLANNED | FastAPI serving all outputs to dashboard |
| **Frontend Dashboard** | 🔄 PLANNED | Next.js 3D mission control UI |

The scientific backbone (Objective 1) is DONE with real ISRO data. The hackathon work is now about turning that into a functional software demo with the dashboard.

---

## Part 8: Team Roles and Work Allocation (6-Member Breakdown)

For a balanced, multidisciplinary execution of Project NIDHI, the work is structured into 6 specialized roles. This allocation ensures clear boundaries between frontend, backend, data science, and AI while keeping all objectives aligned.

### 📋 Member 1: Project Lead & Lead AI Integration Engineer (Member 1)
* **Core Responsibilities:**
  * System architecture definition, workflow orchestration, and cross-module integration.
  * Development and implementation of the **Ice Detection Engine** using unsupervised ML (Isolation Forest) to isolate polar ice candidate anomalies.
  * Building the **FastAPI Backend Web API** to serve calculated outputs, GeoJSON vectors, and heatmaps to the dashboard.
* **Deliverables:** API routes, ML model endpoints, system integration pipeline.

### 🛰️ Member 2: Space Data & GIS Specialist (Member 2)
* **Core Responsibilities:**
  * Ingestion, extraction, and preprocessing of raw ISRO Chandrayaan-2 DFSAR (L-band/S-band) and NASA LOLA DEM data.
  * Core spatial alignment, co-registration, and conversion of radar power to Decibel (dB) scale.
  * Designing the geospatial schema in **PostgreSQL + PostGIS** database to execute spatial queries (e.g., rasterizing ASU's PSR catalogue vectors onto the radar grids).
* **Deliverables:** PostGIS spatial database, aligned datasets (GeoTIFFs), automated geospatial preprocessing scripts.

### 👁️ Member 3: Computer Vision & Hazard Mapping Engineer (Member 3)
* **Core Responsibilities:**
  * Developing the **Hazard Mapping Engine** to process high-resolution optical images (Chandrayaan-2 OHRC).
  * Training and deploying a lightweight object detection model (**YOLOv8 / CNN**) to automatically segment boulders, small craters, and steep rocky outcrops.
  * Fusing the optical hazard mask with DEM slope thresholds using **OpenCV** to produce the final binary Hazard Mask.
* **Deliverables:** YOLOv8/CNN model, hazard detection scripts, OpenCV image post-processing pipeline.

### 🛣️ Member 4: Navigation & Path Planning Engineer (Member 4)
* **Core Responsibilities:**
  * Designing the **Rover Traverse Planning Engine** to plot optimal trajectories from landing zones to ice targets.
  * Implementing the **A\* (A-Star) Pathfinding Algorithm** over a custom terrain cost graph (calculating movement costs based on slope safety and hazard proximity).
  * Creating the landing site weighted scoring matrix (assessing candidate landing ellipses for flat terrain, solar exposure, and proximity to ice).
* **Deliverables:** Cost-grid generator, A* path planning script (using NetworkX/NumPy), landing site scorer.

### 🗺️ Member 5: Frontend UI/UX Developer — 2D Interactive Maps (Member 5)
* **Core Responsibilities:**
  * Building the **Mission Control Dashboard** structure using **Next.js, React, and Tailwind CSS**.
  * Implementing **Deck.gl** and Mapbox overlays to render large-scale spatial datasets interactively in 2D.
  * Creating interface controls for toggling layers (CPR heatmap, ML Ice Probability, Hazard Mask, and Rover Path vectors).
* **Deliverables:** Next.js dashboard UI, Deck.gl map integration, interactive map controls.

### 🧊 Member 6: 3D Visualization & Graphics Developer (Member 6)
* **Core Responsibilities:**
  * Creating the interactive **3D Terrain Visualizer** to reconstruct crater topography inside the browser.
  * Developing the **Three.js / WebGL viewport** to render the lunar DEM mesh with custom shaders (highlighting permanently shadowed regions in real-time).
  * animating the rover's trajectory path over the 3D terrain surface.
* **Deliverables:** Three.js component, 3D terrain shader, rover waypoint animator.