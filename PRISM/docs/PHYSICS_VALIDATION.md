# PRISM Phase 1 — Physics Pipeline Validation

**Date:** 2026-08-22
**Scope:** Reproduce and fix the existing DFSAR/Y4R/PSR/CPR/SERD/T-Ratio radar pipeline,
and produce real, candidate-specific LOLA terrain outputs, for candidate `SP_840980_0797630`
(lat -84.098°, lon 79.764°). No ML, no YOLO, no DOP work was performed in this phase.
The current OHRC scene (confirmed non-overlapping in the prior audit) was not used.

All numbers in this document come from actually re-running code against real,
locally-held Chandrayaan-2 DFSAR products and real NASA LOLA DEM products — nothing
here is copied from the notebooks without independent re-execution.

---

## 1. Data provenance

| Product | Local source | Acquisition / mosaic date | Provider | Access method |
|---|---|---|---|---|
| DFSAR raw L0A-RAW (quad-pol HH/HV/VH/VV) | `ch2_sar_nrxl_20251025t211236510_d_fp_d18.zip` (manually placed in `Downloads` by the project owner; not re-downloaded) | 2025-10-25 (product_id 2575411, orbit 27527) | ISRO ISDA/Pradan | Local ZIP, extracted in full (2.72 GB `.dat`) |
| DFSAR Y4R L4 mosaic (evn/vol/odd/hlx) | `ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx.zip` | mosaic date 2025-06-30 | ISRO ISDA/Pradan | Local ZIP, extracted in full (4×2.234 GB GeoTIFF) |
| DFSAR L3C mosaic (CPR/SERD/T-Ratio) | `ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx.zip` | mosaic date 2025-06-30 | ISRO ISDA/Pradan | Local ZIP, extracted in full (3×2.234 GB GeoTIFF) |
| LOLA South Pole PSR shapefile | `NAC_POLE_PSR_SOUTH.ZIP` (local copy, byte-for-byte the same public PDS product) | product finalized 2022-02-09 (file timestamps) | NASA PDS / LROC | Local ZIP, extracted (653 polygons) |
| LOLA 20 m/px slope map (LDSM) | remote, not downloaded in full | server reports Last-Modified 2023-06-03 | NASA GSFC PGDA | `/vsicurl/` windowed remote read (GDAL HTTP range requests) — only the ~10×10 km window around the candidate was ever fetched |
| LOLA 20 m/px elevation (LDEM) | remote, not downloaded in full | server reports Last-Modified 2023-06-03 | NASA GSFC PGDA | `/vsicurl/` windowed remote read, same as above |

**Why `/vsicurl/` instead of downloading the full DEM files:** raw HTTP throughput
from this network to `pgda.gsfc.nasa.gov` was measured at ≈0.17 MB/s (a 2 MB range
request took 12 s). A full download of the two ~3.5 GB / ~2.7 GB files at that rate
would take several hours. Since only a 10×10 km window around one candidate was
needed, GDAL's `/vsicurl/` virtual filesystem was used to issue HTTP range requests
against the remote, internally-tiled (512×512 block) GeoTIFFs, fetching only the
handful of tiles that intersect the window. This is a data-access optimization,
**not** a substitution of a different dataset — the URLs, product files, and pixel
values are identical to what a full download would have produced; this was spot
checked by comparing the returned CRS/bounds/resolution against the values the
original notebook printed for the same files.

**Why local ZIPs for the radar products instead of re-downloading:** the DFSAR raw/Y4R/CPR
products are ISRO ISDA (Pradan) products gated behind a login-required portal
(`pradan.issdc.gov.in/ch2/protected/...`) with no public/anonymous download path
found. These exact product files (confirmed by filename and byte size matching what
the audited notebooks printed) were found already present locally, apparently
downloaded previously by the project owner. No substitute or synthetic data was used.

---

## 2. Objective 1 — Radar pipeline

### 2.1 Notebook fix

**File modified:** `notebooks/obj2 (1).ipynb`, cells 23 and 24.

**Bug (confirmed by direct inspection of the saved notebook JSON):**
- Cell 23 set `zip_path` to the **Y4R mosaic** zip (`..._my4rspwest_..._fp_xxx.zip`)
  when extracting the CPR/SERD/T-Ratio layers, instead of the **L3C CPR** zip
  (`..._mpcpspwest_..._fp_xxx.zip`). This meant zero `.tif` files matching the wanted
  CPR/SERD/T-Ratio suffixes were ever extracted.
- Cell 24 additionally built its file-search pattern using the Y4R filename fragment
  (`my4rspwest`) instead of the CPR one (`mpcpspwest`), a second, compounding
  instance of the same copy-paste error — even a correctly-fixed Cell 23 would not
  have been found by the original Cell 24.

**Fix applied:** both strings corrected to reference the actual CPR/SERD/T-Ratio
product. A comment was added at each fix site explaining what was wrong and why,
per the instruction not to change code silently. Stale cell outputs (which showed
the `RasterioIOError` and the mis-extracted file listing) were cleared since they no
longer correspond to the corrected code. No other cells, and no scientific formula,
were changed. This fix was applied directly to the notebook's JSON (not via a
Jupyter re-execution) because the notebook is too large (≈30k tokens once rendered)
for this environment's notebook-editing tool to load; the two target cells were
located and replaced by exact string match with a verification step that aborted
the write if either exact match failed.

### 2.2 Reproduction result: can the previously-displayed CPR/SERD/T-Ratio numbers be reproduced?

**Yes — reproduced from the correct data with `src/radar_pipeline.py`, agreeing with
the audit-reported figures to within floating-point rounding.**

| Metric (SP_840980_0797630) | PROJECT_STATUS.md (audit) | Reproduced (Phase 1, this run) | \|difference\| |
|---|---|---|---|
| Pv, PSR interior mean | 0.507 | 0.507053 | 0.00005 |
| Pv, surroundings mean | 0.426 | 0.426375 | 0.00038 |
| CPR, PSR interior mean | 0.630 | 0.630387 | 0.00039 |
| CPR, surroundings mean | 0.532 | 0.531717 | 0.00028 |
| CPR>1 fraction inside PSR | 7.33% | 7.326% | 0.004 |
| SERD, PSR interior mean | 0.636 | 0.636214 | 0.00021 |
| SERD, surroundings mean | 0.692 | 0.692403 | 0.00040 |
| T-Ratio, PSR interior mean | 0.651 | 0.651342 | 0.00034 |
| T-Ratio, surroundings mean | 0.531 | 0.530581 | 0.00042 |
| valid px, PSR interior | 22,810 | 22,810 | 0 |
| PSR area (km²) | 14.234 | 14.234 | 0 |

Full per-candidate table (all 7 shortlisted PSRs, not just the target candidate) is
in `outputs/objective1/shortlist_full_res_comparison.csv`, and the overview-level
336-PSR candidate table is in `outputs/objective1/candidate_table_overview.csv`
(candidate ranked 6th of 7 shortlisted by overview high-tier Pv fraction, exactly
matching the audit).

**Interpretation:** the notebook-displayed numbers were genuine, reproducible
results computed from real data — the audit's original "these numbers cannot be
regenerated from a clean run" finding was correct **as a statement about the saved
notebook's code**, not as a statement about whether the underlying science was
real. With the path bug fixed and run against the correct files, everything
reproduces.

### 2.3 DFSAR polarization channel-mapping verification

**File:** `src/dfsar_channel_mapping.py`. Output: `outputs/objective1/dfsar_channel_mapping_verification.json`.

The original notebook (`objective1_y4r_polarimetry.ipynb.ipynb`, STEP 8–19) decoded
the raw L0A `.dat` byte layout (46-byte fixed prefix, 2048-byte I/Q payload at byte
offset 141–2189 per 2325-byte imaging line, 4-way line interleave into groups
G0–G3) and assigned G0→HV, G1→HH, G2→VV, G3→VH by inspection, cross-checked against
the XML's per-polarization `standard_deviation_real/imag` and `bias_real/imag`
values. The audit flagged this as "not fully verified" since no alternative
grouping was tested and HH's fit was visibly the weakest of the four.

This script reproduces the exact same byte-decode (same offsets, same 100-line
sample) and then **exhaustively tests all 24 possible permutations** of assigning
{HH, HV, VH, VV} to {G0, G1, G2, G3}, scored against the XML reference statistics.

**A first version of the fit metric was itself wrong** — it used relative squared
error for the bias terms, and HH's XML `bias_real` (0.086681) is so close to zero
that a modest absolute mismatch produced a relative error over 20, which dominated
the whole score and made the original notebook's mapping look 2nd-best (rank 2/24)
purely as a numerical artifact of that near-zero denominator, not a real fit
problem. This was caught, and the metric was corrected to score bias terms against
a fixed cross-channel scale (the standard deviation of the 4 XML bias values)
instead of each channel's own value — documented in the script itself.

**Corrected result:**
- The original notebook's mapping (G0→HV, G1→HH, G2→VV, G3→VH) is the **exhaustively verified best fit — rank 1 of 24** — at both the original 100-line sample and an extended 4000-line sample (40× more data).
- The best-fit mapping is stable across both sample sizes (identical winner).
- HH (assigned to G1) remains the weakest-fitting individual channel of the four (fit error ≈0.22–0.29 vs <0.09 for the other three) — consistent with the audit's original observation — but no alternative assignment does better for HH; it is simply the noisiest channel in this raw product, not a sign of a wrong mapping.

**Conclusion: the channel mapping used throughout the Y4R notebook's raw-DFSAR DOP
work is verified correct**, to the extent 4-channel std/bias fitting against XML
metadata can establish it. This does not itself validate the downstream DOP values
(still EXPERIMENTAL per the audit) — it only confirms which raw byte-stream
corresponds to which polarization.

### 2.4 SERD NaN investigation

**File:** `src/serd_nan_investigation.py`. Outputs: `outputs/objective1/serd_nan_hypothesis_test.csv`, `outputs/objective1/serd_nan_verdict.json`.

The audit found SERD NaN fractions ranging from 0% to ~54% across the 7-candidate
shortlist with no explanation. Two hypotheses were tested against the actual pixel
data (SERD's algorithm is an ISRO-internal derivation, not available to inspect
directly, so this is statistical characterization, not formula-level proof):

- **H1 (weak-signal/shadow):** is SERD NaN where total Y4R backscatter power is
  very low? **Not supported** — median total power at NaN vs. finite pixels has a
  mean ratio of 0.89 (close to 1) and is inconsistent in direction across PSRs
  (ranges from 0.25× to 1.33×).
- **H2 (CPR-extremity):** is SERD NaN where CPR is anomalously high? **Strongly
  supported** — median CPR at SERD-NaN pixels is consistently 0.36–0.68 *higher*
  than at SERD-finite pixels, in **every one of the 5 PSRs** that had any SERD NaN
  at all (the candidate itself and one other PSR had 0% NaN, so were excluded from
  this comparison by construction).

**Conclusion:** SERD's missing values are best explained as a mathematical
artifact of ISRO's derivation becoming undefined (or being masked as invalid) at
high/anomalous CPR — not a coverage, shadow, or SNR issue. This is a statistical
inference from pixel co-occurrence, not a proof from the algorithm itself (which
was not available). The candidate `SP_840980_0797630` has 0% SERD NaN both inside
and outside its PSR, so this issue does not affect the candidate's own SERD numbers.

### 2.5 Files produced

| File | Contents | Source rasters | CRS | Processing |
|---|---|---|---|---|
| `outputs/objective1/candidate_table_overview.csv` | All 336 PSRs with radar coverage, ranked by high-Pv-tier fraction | Y4R evn/vol/odd/hlx (1500-px overview), LOLA PSR shapefile | Moon_2000 South Pole Stereographic (R=1,737,400 m) | `Pv = vol/(evn+vol+odd+hlx)`, percentile tiering (p50/p90 of this scene), polygon rasterization |
| `outputs/objective1/shortlist_full_res_comparison.csv` | Full-res Pv/CPR/SERD/T-Ratio, PSR-interior vs. surroundings, for the 7-candidate shortlist | Y4R + CPR full-resolution windows, 1 km buffer around each PSR | same | same formulas, full sensor resolution |
| `outputs/objective1/serd_nan_investigation.csv` | Per-PSR SERD NaN/zero/negative counts and finite range | CPR mosaic SERD band | same | pixel counting only |
| `outputs/objective1/serd_nan_hypothesis_test.csv`, `serd_nan_verdict.json` | H1/H2 test statistics per PSR | Y4R + CPR full-res windows | same | median comparison between NaN and finite pixel subsets |
| `outputs/objective1/dfsar_channel_mapping_verification.json` | 24-permutation fit-error ranking at N=100 and N=4000 raw lines | raw L0A `.dat` (`ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat`) + its XML label | N/A (raw sensor domain, no CRS) | byte decode per STEP 8-19 of the original notebook; exhaustive permutation scoring |
| `outputs/objective1/reproduction_log.json` | Run metadata + audit-vs-reproduced comparison table | — | — | — |
| `outputs/objective1/SP_840980_0797630_radar_composite.png` | Y4R RGB, Pv, CPR, SERD maps with PSR boundary overlay for the candidate | Y4R + CPR full-res window, 1 km buffer | same | as above; RGB uses 2-98th percentile dB-normalized evn/vol/odd |

**Assumptions carried over unchanged from the original notebooks:** the "high Pv"
tier is a data-derived percentile of *this scene*, not a literature-derived ice
threshold; no statistical significance testing is applied to any PSR-vs-surroundings
comparison; a 1 km buffer around each PSR polygon defines "surroundings."

**Limitations:** this reproduction still only covers the same shortlist of 7 PSRs
the original notebooks chose; the DOP work (raw byte-level polarimetry) was
intentionally **not** touched in Phase 1 per instruction, beyond the channel-mapping
verification above, which is upstream of and separate from any DOP computation.

---

## 3. Objective 2 — Terrain

### 3.1 Pipeline

**File:** `src/terrain_pipeline.py`. This completes the workflow `notebooks/obj2 (1).ipynb`
cells 30–34 set up but never finished (the notebook's own DEM download was captured
at 18% and produced no output).

**Processing steps:**
1. Project the candidate lat/lon (-84.098, 79.764) to the DEM's south-polar
   stereographic CRS using the same formula as the original notebook
   (`+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R=1737400`) →
   x=176275.88 m, y=31831.39 m.
2. Read a 5000 m buffer (10×10 km window, 500×500 px at 20 m/px) from the remote
   LDSM (slope) and LDEM (elevation) rasters via `/vsicurl/`, matching the buffer
   size the original notebook set up.
3. Compute slope statistics and the safe(<10°)/caution(10–20°)/hazard(≥20°)
   breakdown, using thresholds copied verbatim from the original notebook.
4. **New in Phase 1** (not present in any audited notebook): elevation statistics,
   a Terrain Ruggedness Index (Riley, Degloria & Elliot 1999 — mean absolute
   elevation difference between each cell and its 8 neighbors, vectorized, native
   20 m/px grid), and a split of both slope and TRI into "PSR interior" vs.
   "surrounding approach terrain in the 10×10 km window," using the same LOLA PSR
   polygon used in the radar pipeline, reprojected into the DEM's CRS.

The PSR-interior pixel count (35,586 px × 400 m²/px = 14.2344 km²) matches the
candidate's catalog area (14.234 km²) to 4 significant figures, which is an internal
consistency check that the polygon-to-DEM-grid alignment is correct.

### 3.2 Results

**Whole 10×10 km window (approach terrain):**
- Slope: min 0.007°, max 59.3°, mean 10.72°, median 8.01° (n=250,000 px)
- 59.9% safe (<10°), 19.9% caution (10–20°), **20.2% hazard (≥20°)**
- Elevation: -4410.7 m to -2668.6 m, 1742.1 m of relief across the window
- TRI: mean 3.02 m, median 2.18 m, max 38.77 m

**PSR interior only (the actual ice-candidate area, 35,586 px):**
- Mean slope **22.08°**, median **23.12°**
- **78.6% of the PSR interior is "hazard" (≥20°) under the notebook's own thresholds**
- Mean TRI 6.29 m — more than double the window-wide average (2.5 m outside the PSR)

**Key finding, flagged prominently because it is not obvious and matters for
downstream landing-site work:** the PSR polygon for this candidate is **not** a
flat crater floor. Visually (see the composite figure) and statistically, it
corresponds mostly to the crater's steep inner wall, with only a small flat basin
at its center. This is physically consistent with how PSRs form near the lunar
poles (grazing illumination casts long shadows across crater walls, not just
floors), but it means the same terrain that hosts the ice-favorable radar signature
(§2) is, by the project's own preliminary slope thresholds, mostly too steep for
direct landing or roving. This does not invalidate the radar evidence — it is a
terrain-accessibility finding, separate from the ice-likelihood question — but it
is a first-order input to any future landing-site-suitability or rover-routing work
and should not be overlooked.

### 3.3 Files produced

| File | Contents | Source | CRS | Processing |
|---|---|---|---|---|
| `outputs/objective2/SP_840980_0797630_terrain_stats.json` | All slope/elevation/TRI statistics, whole-window and PSR-interior-split | LDSM + LDEM, 10×10 km window | Moon (2015) Sphere / Ocentric / South Polar Stereographic (R=1,737,400 m — same sphere radius as the radar CRS, so results are directly co-locatable) | see §3.1 |
| `outputs/objective2/SP_840980_0797630_terrain_composite.png` | Slope, elevation, and TRI maps with PSR boundary overlay | same | same | RdYlGn_r (0–25°), terrain, magma colormaps |

**Assumptions:** the safe/caution/hazard slope thresholds are copied verbatim from
the original notebook's own author, who labeled them "crude ... refine once you
overlay actual PSR boundary" — that caveat is preserved and repeated here. They are
**not** validated against any specific lander or rover engineering specification in
this phase.

**Limitations:** TRI is a simple, standard, general-purpose roughness index; it is
not a lander-specific hazard model (e.g. it does not account for footpad size,
rock-abundance-specific hazard, or slope-direction relative to an approach
trajectory). Only one candidate was processed in Phase 1 (per the phased-work
instruction); the shortlist's other 6 PSRs have not yet received the same terrain
treatment.

---

## 4. What remains uncertain after Phase 1

- DOP (from raw DFSAR) was intentionally not touched — still EXPERIMENTAL, per the prior audit.
- SERD's NaN behavior is explained statistically (correlates with high CPR) but not confirmed against ISRO's actual SERD formula, which was not available.
- The slope safe/caution/hazard thresholds are still not validated against a real mission engineering constraint.
- Only the target candidate's terrain was processed; the other 6 shortlisted PSRs were not.
- OHRC was not touched in this phase (per instruction) — the project still has no OHRC scene covering this candidate.
- Isolation Forest / YOLOv8 / CNN: still 100% absent (per instruction, not attempted in Phase 1).
