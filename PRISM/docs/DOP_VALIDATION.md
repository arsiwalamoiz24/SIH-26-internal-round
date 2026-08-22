# DOP_VALIDATION — full story: blocked → pipeline validated → resolved

**Date:** 2026-08-22. This file merges what were originally two separate documents (`DOP_VALIDATION.md` and `DOP_VALIDATION_RESULTS.md`) into one chronological account, since the second was a same-day sequel to the first and reading them separately made it easy to miss that the blocker documented in Part 1 was fully resolved by Part 3.

**Bottom line if you only read one line:** candidate-specific DOP for `SP_840980_0797630` is **RESOLVED** — see Part 3. Parts 1–2 are kept because they document real, useful work (a genuine coverage blocker, and a pipeline-validation run) that the final result depends on.

---

## Part 1 — Initial attempt: BLOCKED at candidate coverage

Candidate-level DOP could not be calculated from the raw DFSAR product then held in the repo (`ch2_sar_nrxl_20251025t211236510_d_fp_d18`, product_id `2575411`, 2025-10-25 acquisition), because that product's acquisition does not cover the candidate's location. This was a genuine, quantified geolocation blocker, not a formulation or calibration blocker. No DOP value was reported for the candidate at this stage. The prior 0.64 / 0.57 / 0.64 numbers from `notebooks/objective1_y4r_polarimetry.ipynb.ipynb` were **not** used, extended, or reinterpreted as the candidate's DOP.

### Coverage determination

Compared the candidate's lat/lon against the raw product's own `isda:Geometry_Parameters` block (4 corner lat/lons + scene center), taken directly from the `.dat` XML label. Distances computed via haversine great-circle distance on the sphere the product itself defines. Independently corroborated using the geometry CSV's satellite ephemeris. Full numeric evidence: `outputs/objective1/dop/candidate_coverage_check.json`.

| Reference point | Lat | Lon | Distance to candidate |
|---|---|---|---|
| Scene UL corner | −84.502295° | −23.217621° | 270.4 km |
| Scene UR corner | −84.556978° | −22.521599° | 267.9 km |
| Scene LR corner | −86.567711° | −77.521892° | 277.9 km |
| Scene LL corner | −86.482727° | −77.422285° | 280.3 km |
| **Scene center** | **−85.998683°** | **−43.600595°** | **265.7 km** |

Scene extent: ~135 km along-track × ~2.6 km cross-track. The candidate sits ~266–280 km outside this footprint — roughly 2x the entire scene length, and >100x the scene's cross-track width. No plausible geolocation error in a delivered PDS4 label (typically 10s of meters to a few km) could close a 265+ km gap.

### What was still established and reused later
- Binary structure of the raw product (offsets, line length, I/Q payload bounds) — confirmed.
- Offset-binary sample decoding convention — confirmed, re-verified at a second file location.
- Polarization channel mapping G0→HV, G1→HH, G2→VV, G3→VH — HV/VH/VV confirmed, HH likely (correct group, weaker quantitative fit). See `RAW_DFSAR_VALIDATION.md`.
- A memory-safe, reusable `read_window()` reader (`src/dfsar_raw_reader.py`), ready to point at a covering product without re-deriving the byte structure.
- The DOP formulation itself (windowed 2×2 H/V covariance → linear-pol Stokes DOP) — a legitimate, textbook-standard construction, unchanged from `notebooks/objective1_y4r_polarimetry.ipynb.ipynb` STEP 27-33.

Explicitly **not** done at this stage, per the task's critical rules: no DOP fabricated/estimated/assumed for the candidate, no candidate window invented, no geolocation invented, no calibration constants invented.

---

## Part 2 — Pipeline validation (non-candidate)

**The 2025-10-25 acquisition was used to validate the DOP computational pipeline only — it never covered the candidate.** This step ran the same three formulas (transcribed unchanged from the notebook) at a much larger, vectorized scale, purely to prove the pipeline itself was sound. Code: `src/dop_validation_pipeline.py`. Outputs: `outputs/objective1/dop/dop_validation_results.json`, `dop_comparison.json`, `dop_map.png`, `dop_histogram.png`.

### Formulas (transcribed, not invented)

**1) Linear-pol Stokes DOP** (bias-corrected HH/VV, local 5×5-pixel spatial covariance):
```
S1 = <|HH|^2> + <|VV|^2>
S2 = <|HH|^2> - <|VV|^2>
S3 = 2*Re(<HH*conj(VV)>)
S4 = -2*Im(<HH*conj(VV)>)
DOP = sqrt(S2^2 + S3^2 + S4^2) / S1
```
**2) Hybrid-pol Stokes DOP** (synthesized left-circular-transmit fields): `LH = (HH + j*HV)/sqrt(2)`, `LV = (VH + j*VV)/sqrt(2)`, same Stokes/DOP formula applied to `(LH, LV)`.
**3) 4×4 full-quad-pol eigenvalue "polarization purity"**: sample covariance of stacked `[HH,HV,VH,VV]`, purity from normalized eigenvalues.

### Window and results
Mid-scene lines 150,000–152,999 × 1,024 range samples — 3,072,000 pixels, ~123x larger than the notebook's original 25×1024 patch.

| Formulation | n px | mean | median | std | min | max |
|---|---:|---:|---:|---:|---:|---:|
| Linear-pol (HH/VV) | 3,072,000 | 0.667 | 0.682 | 0.114 | 0.022 | 1.000 |
| Hybrid-pol (synth. LH/LV) | 3,072,000 | 0.574 | 0.589 | 0.138 | 0.010 | 1.000 |
| Eigenvalue purity (whole window) | — | **0.630** | — | — | — | — |

All three land within ~0.02–0.04 of their Part-1-notebook counterparts despite a 123x larger, differently-located window — evidence the pipeline behaves consistently and isn't an artifact of one tiny patch. **Best-supported formulation: linear-pol (HH/VV) Stokes-covariance DOP** — standard construction, no synthesis assumption, and HH/VV channel mapping is confirmed/likely.

### Known limitations carried forward
- G1→HH channel mapping is *likely*, not *confirmed* — weakest quantitative fit of the four channels.
- No gain-imbalance or phase-orthogonality calibration applied — only XML bias-centering.
- This validates the *method*, not anything about DOP near the candidate.

---

## Part 3 — Candidate-specific DOP: RESOLVED

A covering acquisition was identified, confirmed, downloaded, and processed.

### Acquisition
`ch2_sar_ncxl_20220318t135736694_d_fp_d18` — 2022-03-18, station d18, quad-pol Level-1A SLANT-RANGE (HH/HV/VH/VV, `ComplexLSB8`). Product ID 2238611. Downloaded via PRADAN (authenticated), 1,920,035,453 bytes. Full selection detail: `CANDIDATE_ACQUISITION_SELECTION.md`.

### Containment evidence (two independent checks)
1. **True rotated image-footprint corners** (PDS4 `image_upper_left/upper_right/lower_right/lower_left_mapX/mapY`, not the loose bounding-box corners — see the false-positive lesson below): candidate ~20 km inside the nearest edge.
2. **Actual Level-1A Grid CSV** (real per-pixel lat/lon/slant-range/incidence, 8,059×9 samples at 32-line/32-pixel spacing): nearest sampled grid point is **91 meters** from the candidate coordinate.

### A false-positive lesson, documented not hidden
An initial screening pass tested candidate containment against the PDS4 label's *loose axis-aligned bounding-box corners*, which flagged `ch2_sar_ncxl_20191106t114537878_d_fp_d18` as containing — that 4.88 GB product was downloaded before the actual Grid CSV revealed it misses the candidate by **~75 km**. The bounding box is inflated well beyond the true rotated swath for near-polar passes. Fix: use the label's `image_*` corners (the true rotated footprint), then confirm with the Grid CSV. The wrong download was deleted and is not used anywhere in this project's results. All 602 manifest acquisitions were then re-screened with the corrected method; 6 genuine hits were found, and the one with the largest edge margin was selected.

### Candidate-specific DOP results
Window: full range width (244 samples) × 2,000 lines centered on the Grid-confirmed candidate line (219,616) — 488,000 pixels, genuinely centered on the candidate.

| Formulation | n px | mean | median | std | min | max |
|---|---:|---:|---:|---:|---:|---:|
| Linear-pol (HH/VV) | 488,000 | **0.680** | **0.708** | 0.183 | 0.012 | 0.999 |
| Hybrid-pol (synth. LH/LV) | 488,000 | 0.594 | 0.607 | 0.188 | 0.008 | 0.999 |
| Eigenvalue purity (whole window) | — | **0.909** | — | — | — | — |

Full percentile tables: `outputs/objective1/dop/candidate_dop.json`. Maps: `outputs/objective1/dop/candidate_dop.png`, `candidate_dop_histogram.png`.

**Best-supported value: linear-pol (HH/VV) Stokes DOP, mean 0.680 / median 0.708** — this product's channel identity is given directly by PDS4 label filenames (not byte-level-inferred), so the Part-1/2 HH-weak-fit caveat does not apply here.

**Calibration:** XML bias-centering only (per-polarization `bias_real`/`bias_imag`) — no gain-imbalance or phase-orthogonality correction applied, same limitation as Part 2.

**This is genuinely candidate-specific.** Do not conflate it with Part 2's non-candidate pipeline-validation numbers.
