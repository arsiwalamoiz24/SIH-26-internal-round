# CANDIDATE_DFSAR_SOURCE — tracing SP_840980_0797630 to its source acquisition(s)

**Date:** 2026-08-22
**Scope:** Task 1-4 per this session's instructions. No DOP calculation, no ML, no OHRC processing, no candidate change, no downloads were performed. All files inspected below were already present locally (either in this repo's `PRISM/data`, in `C:\Users\radhe\PRISM_local_data`, or as previously-downloaded zip archives in `C:\Users\radhe\Downloads`); two small manifest files (`*_fp_xxx.txt`, 25 KB / 25 KB) were extracted from already-downloaded zips using Python's `zipfile` (no network access), because they existed in the zip but had not been extracted by the earlier `extract_all.py` run.

---

## Candidate coordinates

`SP_840980_0797630`, lat **−84.098°**, lon **79.764°**, PSR area 14.234 km² (LOLA/LRO PSR shapefile polygon).

---

## TASK 1 — Trace the candidate

**Chain, as implemented in `notebooks/objective1_dfsar_validation.ipynb.ipynb`** (the origin notebook — copy-pasted unchanged as a shared preamble into `objective1_y4r_polarimetry.ipynb.ipynb` and `obj2 (1).ipynb`; reproduced numerically today in `outputs/objective1/reproduction_log.json` and implemented in this repo's `src/radar_pipeline.py`):

1. **PSR polygon** — `SP_840980_0797630` comes from the LRO/LOLA South Pole PSR shapefile (`NAC_POLE_PSR_SOUTH.ZIP` → `LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL`, 653 polygons), **independent of DFSAR** — this is a permanently-shadowed-region catalog derived from LOLA altimetry/illumination modeling, not radar.
2. **Pv** (Yamaguchi volume-scattering fraction) = `vol / (evn+vol+odd+hlx)`, computed from the **Y4R L4-MOSAIC** product `ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx` (4 GeoTIFF bands: evn/vol/odd/hlx).
3. **CPR, SERD, T-Ratio** computed from the **L3C-MOSAIC** product `ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx` (3 GeoTIFF bands: cpr/srd/trt), same grid/CRS as the Y4R mosaic (confirmed by CRS/bounds match, both in the original notebook and re-verified in `src/radar_pipeline.py`).
4. PSR mask rasterized onto the same grid; candidate ranked by top-decile Pv fraction inside its PSR polygon; PSR-interior vs. local-surroundings statistics computed for Pv/CPR/SERD/T-Ratio (see `PROJECT_STATUS.md` §1 for the full reproduced numbers).

**Generating notebook:** `objective1_dfsar_validation.ipynb.ipynb`.

**Exact source data for the candidate's radar evidence:** the **Y4R L4-MOSAIC** and **CPR/SERD/T-Ratio L3C-MOSAIC** products — **not** any single raw acquisition. This is the central finding of this task.

---

## TASK 2 — Local file search results

Searched the entire `PRISM` repo (`Grep` for `SP_840980_0797630`, `840980`, `0797630`, `-84.098`, `79.764`, `CPR`, `SERD`, `T-Ratio`, `Pv`) and the external local cache `C:\Users\radhe\PRISM_local_data` (referenced by `src/radar_pipeline.py` / `src/serd_nan_investigation.py`) and `C:\Users\radhe\Downloads` (original zip archives).

**What is present locally:**

| Product | Location | Processing level | Covers candidate? |
|---|---|---|---|
| Y4R L4-MOSAIC (`ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx`) | `C:\Users\radhe\PRISM_local_data\l4_mosaic\` (extracted) + `Downloads\ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx.zip` (4.93 GB, original) | L4-MOSAIC (Derived) | Yes — whole-hemisphere mosaic, trivially contains the candidate lat/lon, but see Task 3 caveat |
| CPR/SERD/T-Ratio L3C-MOSAIC (`ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx`) | `C:\Users\radhe\PRISM_local_data\l3c_cpr\` (extracted) + `Downloads\ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx.zip` (3.59 GB, original) | L3C-MOSAIC (Derived) | Same as above |
| Raw L0A-RAW quad-pol, 2025-10-25 (`ch2_sar_nrxl_20251025t211236510_d_fp_d18`) | `PRISM/data/...` (repo) + `PRISM_local_data\raw\` + `Downloads\...zip` | L0A-RAW, quad-pol (HH/HV/VH/VV) | **NO** — established in the prior session (~266-280 km outside footprint; see `docs/DOP_VALIDATION.md`). Also postdates the mosaic's 2023-10-18 cutoff, so it could never have contributed to the candidate's Pv/CPR/SERD/T-Ratio regardless. |
| Raw L0B-RAW compact/hybrid-pol, 2025-11-06 (`ch2_sar_nrxl_20251106t221014810_d_cp_d18`) | `Downloads\ch2_sar_nrxl_20251106t221014810_d_cp_d18.zip` (752 MB, **not yet extracted** — an empty `cp_raw\` directory exists in the local cache as a placeholder) | L0B-RAW, **2-pol only** (LH/LV, hybrid-pol) | **NO** — footprint centered at (−88.78°, −149.77°), nearest corner ≈152 km from the candidate (computed this session, haversine, same method as `docs/DOP_VALIDATION.md`). Also not quad-pol, so it could not support HH/HV/VH/VV DOP even if it did overlap. Also postdates the mosaic cutoff. |

**No other DFSAR raw acquisition is present locally.** No file anywhere in the repo or the local cache contains a per-pixel or per-orbit footprint table that directly names which single raw acquisition covers (−84.098°, 79.764°).

**New finding this session:** each mosaic's `Readme.txt` (already extracted) states: *"The source L-band full-pol DFSAR datasets used to develop the mosaic are listed in `ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx.txt`"* (and the analogous CPR file). These manifest `.txt` files exist inside the original zip archives in `Downloads\` but were **not extracted** by the earlier `extract_all.py` run (its file-suffix filter only kept `.tif`/`.xml`/`Readme.txt`). This session extracted them (no download, no network access — read directly from the already-local zip via Python's `zipfile`):

- `PRISM_local_data\l4_mosaic\source_acquisitions_manifest.txt`
- `PRISM_local_data\l3c_cpr\source_acquisitions_manifest.txt`

Both list **602 identical source acquisitions** (byte-identical set), naming convention `ch2_sar_ncxl_YYYYMMDDtHHMMSSFFF_d_fp_<station>` — note the processing-level code `ncxl` (Chandrayaan SAR **calibrated** level), not `nrxl` (the **raw L0A-RAW** level our two locally-held raw products use. Whether an `nrxl` raw product with the identical date/time/station exists for each `ncxl` entry is plausible by naming convention but **not confirmed** locally — no `nrxl`-level counterpart file for any of these 602 entries was found in `PRISM_local_data`, `Downloads`, or the repo.

Date range of the 602 contributing acquisitions: **2019-09-22 to 2023-10-18** (matches the mosaic XML's own `Time_Coordinates` block exactly). Station-code breakdown: `d18`=367, `d32`=163, `n18`=47, `gds`=11, `g26`=9, `m65`=3, `mad`=2.

(Incidental cross-check: the unrelated 2021-04-14 raw acquisition used for byte-structure inspection in `obj2 (1).ipynb` — flagged in `PROJECT_STATUS.md` as "an unrelated raw DFSAR acquisition" — does appear in this manifest, twice (`20210414t062336471_d_fp_d18`, `20210414t121626178_d_fp_d18`), confirming it genuinely was one of the mosaic's 602 contributors even though it was not used for Pv extraction in that notebook. This is informational only; it does not change the coverage question below.)

---

## TASK 3 — Does the source footprint contain the candidate?

**Mosaic-level footprint** (from `ch2_sar_ndxl_20250630my4rspwest_d_xxx_xx_fp_xx_xxx.xml` / the CPR mosaic's identical-structure XML, `isda:Geometry_Parameters`, UPS/polar-stereographic projection):

| Corner | Lat | Lon |
|---|---|---|
| UL | −75.594018° | −177.546273° |
| UR | −75.594018° | 178.785211° |
| LR | −89.720403° | 178.785211° |
| LL | −89.720403° | −177.546273° |

This spans the **entire south-polar cap** (all 360° of longitude, −75.6° to −89.7° latitude) — a compiled multi-year mosaic, not a single pass. The candidate (−84.098°, 79.764°) falls trivially inside this whole-hemisphere box. **This confirms the mosaic product covers the candidate, but it does not identify which of the 602 individual contributing acquisitions imaged that specific pixel** — mosaics of this kind are typically built by taking the best/most-recent/highest-quality pass per output pixel across all contributing orbits, and this product's PDS4 label does not carry a per-pixel source-orbit index. **No per-pixel or per-tile provenance grid was found in the extracted mosaic package** (only the flat list of 602 contributing acquisition names, with no accompanying footprint or spatial index for each one).

**Individual raw-acquisition footprints checked this session** (the only two raw acquisitions physically present locally): both confirmed **NOT** covering the candidate (Task 2 table above). Neither is in the 602-item manifest anyway (both postdate the 2023-10-18 mosaic cutoff).

**Conclusion:** the mosaic (whole-hemisphere, derived) covers the candidate; **no single raw acquisition's footprint covering the candidate has been identified or confirmed from data available locally.**

---

## TASK 4 — Identifying the required raw product

1. **Exact acquisition date:** **UNDETERMINED.** The candidate's radar evidence comes from a 602-acquisition mosaic (2019-09-22 to 2023-10-18); no per-acquisition footprint data is available locally to isolate which of the 602 dates specifically images (−84.098°, 79.764°).
2. **Exact DFSAR product ID:** **UNDETERMINED**, for the same reason. (The mosaic's own `isda:job_id` is `ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx` / `...mpcpspwest...` — these are mosaic job IDs, not raw per-orbit product IDs like the `2575411` we have for the 2025-10-25 raw file.)
3. **Exact product type:** Would be **L0A-RAW, quad full-polarimetric** (`num_polarizations=4`, HH/HV/VH/VV) to support the same DOP construction validated in `docs/RAW_DFSAR_VALIDATION.md` — inferred from the fact that the mosaic's contributors are named `..._d_fp_...` (full-pol) and from the two raw products we do have, one of which (`_fp_`) is quad-pol and the other (`_cp_`) is 2-pol hybrid. The manifest's `_fp_` tag on all 602 entries indicates they were acquired in full-polarimetric mode, consistent with quad-pol raw products existing for each.
4. **Exact raw product filename that would be required:** **UNDETERMINED.** If the `ncxl`→`nrxl` naming correspondence holds (unconfirmed), the required file would be named `ch2_sar_nrxl_<one of the 602 timestamps>_d_r0a_xx_fp_xx_<station>.dat`, for whichever one of the 602 timestamp/station combinations in `source_acquisitions_manifest.txt` has a footprint containing (−84.098°, 79.764°). That specific timestamp cannot be identified without either (a) each candidate acquisition's own XML footprint, or (b) an ISRO/ISDA per-orbit footprint index — neither is present locally.
5. **Whether the raw full-polarimetric product is available/expected for that acquisition:** **UNKNOWN/NOT PRESENT.** None of the 602 manifest-listed acquisitions (at any processing level, raw or calibrated) are present in this repo or the local cache. Only their aggregate mosaic output is present.
6. **What files would be required to calculate candidate-level DOP:** the raw L0A-RAW quad-pol product (`.dat` + `.xml`, and ideally its geometry `.csv`/`.xml`) for whichever of the 602 (or possibly additional, post-2023-10-18, not-yet-mosaicked) acquisitions actually images the candidate — confirmed by footprint before use, exactly as done for the 2025-10-25 product in the prior session. None of these files currently exist locally for a confirmed-covering acquisition.

---

## Confidence level

| Finding | Confidence |
|---|---|
| Candidate's Pv/CPR/SERD/T-Ratio come from the Y4R L4-MOSAIC + CPR/SERD/T-Ratio L3C-MOSAIC (both `20250630` products), not any single raw acquisition | **CONFIRMED** — direct code/notebook trace + exact numeric reproduction (`outputs/objective1/reproduction_log.json`) |
| These two mosaics are built from 602 identical contributing acquisitions spanning 2019-09-22 to 2023-10-18 | **CONFIRMED** — read directly from each product's own manifest file, extracted from the already-local zip archives this session |
| The mosaic's whole-hemisphere footprint contains the candidate | **CONFIRMED** — direct corner-coordinate check |
| Which single one (or more) of the 602 contributing acquisitions specifically images the candidate pixel | **UNDETERMINED — not knowable from data currently available locally** |
| The two raw acquisitions physically present locally (2025-10-25 quad-pol, 2025-11-06 hybrid-pol) do not cover the candidate | **CONFIRMED** (haversine geolocation check, both) |
| A raw `nrxl`-level product exists for each `ncxl` manifest entry with matching date/time/station | **UNCONFIRMED / PLAUSIBLE BY NAMING CONVENTION ONLY** |
