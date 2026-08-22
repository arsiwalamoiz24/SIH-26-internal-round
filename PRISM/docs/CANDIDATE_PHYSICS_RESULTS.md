# CANDIDATE_PHYSICS_RESULTS — SP_840980_0797630 (Tracks A + B)

**Date:** 2026-08-22
**Category: CANDIDATE-SPECIFIC.** Every number below is extracted from a window centered on the candidate's actual coordinate, using verified georeferencing (Track B, §1). Code: `src/candidate_physics_pipeline.py`. Outputs: `outputs/objective1/candidate_physics/candidate_{pv,cpr,serd,tratio}.json`, `candidate_physics_summary.json`, `candidate_{pv,cpr,serd,tratio}.png`, `candidate_locator.png`, `georeferencing_check.json`.

## 1. Georeferencing verification (Track B) — PASSED

- Raster CRS (read directly from the GeoTIFF header, not assumed): `Moon_2000_South_Pole_Stereographic`, sphere radius 1,737,400 m, `latitude_of_origin=-90`, `central_meridian=0`.
- Candidate (−84.098°, 79.764°) → projected (176275.878, 31831.393) m via `pyproj.Transformer` (geographic-Moon-sphere → raster CRS).
- **Round-trip check:** inverse-transforming the projected point back to lon/lat reproduces the input to **1.4×10⁻¹⁴° absolute error** (floating-point noise, effectively exact).
- Candidate pixel position: column 19,273.3 / row 11,343.6 of a 24,181×24,794 px raster — **well inside** the raster bounds and pixel grid (not an edge/extrapolation case).
- Y4R and CPR/SERD/T-Ratio rasters confirmed to share **identical CRS and bounds** (`y4r_cpr_crs_match: true`, `y4r_cpr_bounds_match: true`) — a single coordinate transform is valid for all four metrics.
- **Longitude wrapping:** not an issue here — the mosaic is a projected (not geographic-grid) CRS spanning the full 360° south-polar cap continuously around the pole, so there is no antimeridian/0–360-vs-±180 seam to cross for a single point placement. Verified by the round-trip error above, not merely assumed.
- **Verdict: PASS.** Full detail in `outputs/objective1/candidate_physics/georeferencing_check.json`. See also `candidate_locator.png` for a visual check (candidate marker + extraction window drawn on the whole-mosaic Pv overview).

## 2. Source products

| Product | ID | Level | Date |
|---|---|---|---|
| Y4R L4-MOSAIC (evn/vol/odd/hlx) | `ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx` | L4-MOSAIC (Derived) | 2025-06-30 |
| CPR/SERD/T-Ratio L3C-MOSAIC | `ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx` | L3C-MOSAIC (Derived) | 2025-06-30 |
| PSR shapefile (secondary interior/surroundings split only) | `LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL` | LRO/LOLA catalog | — |

Both mosaics are compiled from 602 contributing acquisitions spanning 2019-09-22 to 2023-10-18 (`outputs/objective1/dop/manifest_602_parsed.json`) — **this is a multi-year compiled product, not a single dated pass.**

## 3. Window definition

- Fixed **±3,300 m square** (6.6×6.6 km, 264×264 px @ 25 m/px) centered on the candidate's *projected coordinate* — not the PSR polygon, and not an arbitrary pixel offset.
- Chosen to be comparable in scale to the earlier PSR+1km-buffer window used in `src/radar_pipeline.py`'s Phase-1 run (~6.6×6.3 km).
- The candidate's own PSR polygon (area 14.234 km², from the LOLA shapefile) is used as a **secondary interior/surroundings split within this window**, for continuity with the earlier PSR-based results — not as the primary window definition.

## 4. Results

| Metric | Window mean | median | std | min | max | n valid / total | Relative percentile in mosaic overview |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Pv** | 0.454 | 0.469 | 0.182 | 0.002 | 0.875 | 69,696 / 69,696 (0% NaN) | **93.9th** |
| **CPR** | 0.565 | 0.542 | 0.284 | 0.030 | 1.852 | 69,696 / 69,696 (0% NaN) | **97.2nd** |
| **SERD** | 0.673 | 0.669 | 0.144 | 0.134 | 0.997 | 69,696 / 69,696 (0% NaN) | **4.3rd** |
| **T-Ratio** | 0.571 | 0.530 | 0.312 | 0.014 | 2.189 | 69,696 / 69,696 (0% NaN) | **95.8th** |

"Relative percentile in mosaic overview" = the window-mean value's percentile rank against a 1500-row-overview (resampled) distribution of the same metric across the whole mosaic — an approximate global-context number, not an exact full-resolution percentile (see limitations).

**Secondary split — PSR interior vs. surroundings within the same window:**

| Metric | PSR interior mean (n=22,772 px) | Surroundings mean (n=46,924 px) | Difference |
|---|---:|---:|---:|
| Pv | 0.509 | 0.428 | +0.081 |
| CPR | 0.633 | 0.532 | +0.102 |
| SERD | 0.635 | 0.692 | **−0.057** |
| T-Ratio | 0.655 | 0.530 | +0.125 |

These reproduce the prior Phase-1 audit numbers (Pv interior 0.507/0.549 mean/median, CPR 0.630, SERD 0.636, T-Ratio 0.651 — `PROJECT_STATUS.md` §1) to within ~0.01–0.02 despite a differently-defined window (coordinate-centered here vs. PSR-polygon+1km-buffer previously) — a useful independent cross-check that the two window-definition methods agree.

## 5. Interpretation

- **Pv, CPR, and T-Ratio are all in the top ~3–6% of the whole mosaic's overview distribution**, and all are elevated inside the PSR relative to its immediate surroundings — the qualitative signature the original screening pipeline treats as ice-favorable (elevated volume scattering, elevated circular polarization ratio with some CPR>1 pixels, elevated T-Ratio).
- **SERD is anomalous relative to that narrative**: it sits at only the **4th percentile** of the mosaic overview (i.e., unusually *low* SERD globally) and is *lower* inside the PSR than in its surroundings — the same counter-intuitive pattern already flagged in `PROJECT_STATUS.md` §1 ("not obviously consistent with a simple 'rougher = icier' narrative"). See `docs/SERD_NAN_ANALYSIS.md` for a related (but distinct) SERD data-quality investigation — the candidate itself has 0% SERD NaN, so this is a genuine low-value finding, not a masking artifact.

## 6. Limitations

- Mosaic-derived (multi-year compiled), not a single dated acquisition — see §2.
- Fixed ±3,300 m coordinate window, not the PSR polygon itself; PSR split is secondary.
- "Relative percentile in mosaic overview" compares against a 1500-row-resampled distribution (not full-resolution) — an approximate, not exact, global context.
- No independent ground truth for ice exists anywhere in this project; all four metrics are radar-derived scattering statistics, not direct ice measurements.
- No statistical significance testing (no p-values, no multiple-comparison correction) is performed on the interior-vs-surroundings differences.
