# DOP_VALIDATION_RESULTS — computational pipeline validation (NON-CANDIDATE)

**Date:** 2026-08-22

**The 2025-10-25 acquisition is used to validate the DOP computational pipeline only. It does not cover SP_840980_0797630.** Its footprint is ~265-280 km from the candidate (`docs/DOP_VALIDATION.md`, `outputs/objective1/dop/candidate_coverage_check.json`). Nothing in this document is, or should ever be cited as, the candidate's DOP.

## 1. What changed since `docs/DOP_VALIDATION.md`

That earlier document established the formulas were legitimate but stopped before running them (blocked on candidate coverage, correctly did not fabricate a candidate window). This session runs the same three formulas — transcribed unchanged from `notebooks/objective1_y4r_polarimetry.ipynb.ipynb` — at a much larger, vectorized scale, purely as a **pipeline validation exercise** on the one raw product physically present locally. Code: `src/dop_validation_pipeline.py`. Outputs: `outputs/objective1/dop/dop_validation_results.json`, `dop_comparison.json`, `dop_map.png`, `dop_histogram.png`.

## 2. Formulas (transcribed, not invented)

**1) Linear-pol Stokes DOP** (notebook STEP 27-33, bias-corrected HH/VV, local 5×5-pixel spatial covariance):

```
S1 = <|HH|^2> + <|VV|^2>
S2 = <|HH|^2> - <|VV|^2>
S3 = 2*Re(<HH*conj(VV)>)
S4 = -2*Im(<HH*conj(VV)>)
DOP = sqrt(S2^2 + S3^2 + S4^2) / S1
```

**2) Hybrid-pol Stokes DOP** (notebook STEP 46-48, synthesized left-circular-transmit fields):

```
LH = (HH + j*HV) / sqrt(2)
LV = (VH + j*VV) / sqrt(2)
```
then the identical Stokes/DOP formula applied to `(LH, LV)` in place of `(HH, VV)`.

**3) 4×4 full-quad-pol eigenvalue "polarization purity"** (notebook STEP 26/35):

```
k = [HH, HV, VH, VV]  (per pixel, stacked over a window/tile as rows)
C = (k^H k) / N        (4x4 sample covariance)
eig = eigvalsh(C), clipped >= 0
p = eig / sum(eig)
purity = sqrt(max(0, (4*sum(p^2) - 1) / 3))
```

All three formulas are quoted verbatim from the notebook cells (line-by-line grep-verified this session), not re-derived or altered. Local-window means for (1)/(2) are computed with `scipy.ndimage.uniform_filter` — a vectorized box-filter local mean, numerically identical to the notebook's explicit nested-loop 5×5 mean.

## 3. Window used

Mid-scene, same starting line as the already-validated Phase D diagnostic window (`docs/RAW_DFSAR_VALIDATION.md` §7): per-channel lines **150,000–152,999** (3,000 lines), all 1,024 range samples — **3,072,000 pixels**, ~123× larger than the notebook's original 25×1024 (25,600 px) patch. Chosen deliberately far from the start of the file, per the same "don't assume the first bytes are representative" reasoning as the prior Phase D check.

## 4. Results

| Formulation | n px | mean | median | std | min | max | NaN % |
|---|---:|---:|---:|---:|---:|---:|---:|
| Linear-pol (HH/VV) | 3,072,000 | 0.667 | 0.682 | 0.114 | 0.022 | 1.000 | 0.0 |
| Hybrid-pol (synth. LH/LV) | 3,072,000 | 0.574 | 0.589 | 0.138 | 0.010 | 1.000 | 0.0 |
| Eigenvalue purity (tiled, 30×32 px, 3,200 tiles) | 3,200 | 0.611 | 0.638 | 0.076 | 0.359 | 0.723 | 0.0 |
| Eigenvalue purity (whole 3.07M-px window, single value) | — | **0.630** | — | — | — | — | — |

Full percentile tables and metadata in `outputs/objective1/dop/dop_validation_results.json`.

## 5. Comparison with the prior notebook's 25×1024 patch

| Formulation | Prior notebook (25×1024, non-geolocated, first ~100 raw lines) | This run (3000×1024, mid-scene) |
|---|---:|---:|
| Linear-pol covariance | 0.629 | 0.667 (mean) / 0.682 (median) |
| Hybrid-pol | 0.557 | 0.574 (mean) / 0.589 (median) |
| Eigenvalue purity (single window value) | 0.643 | 0.630 |

**These are independent runs at different scene locations and different window sizes — exact numerical agreement was never the criterion, and none of the prior 0.629/0.557/0.643 values are reused as this run's result.** The finding is that all three land within ~0.02–0.04 of their prior counterparts despite a 123× larger, differently-located window — this is evidence the pipeline (reader, decode, channel mapping, formula implementation) behaves **consistently and is not an artifact of the specific tiny patch** the original notebook happened to use, which is exactly what a pipeline-validation exercise is meant to show.

## 6. Which formulation is best supported

**Linear-pol (HH/VV) Stokes-covariance DOP** is the best-supported formulation for this product:

- It is the standard, textbook dual-pol DOP construction (Stokes parameters from a genuine local spatial covariance/coherency estimate, not single uncorrelated pixels — the notebook's own STEP 24 "naive" single-pixel version was correctly self-flagged invalid, since it degenerates to DOP≡1 everywhere).
- HH/VV channel mapping is CONFIRMED/LIKELY (`docs/RAW_DFSAR_VALIDATION.md` §5), and it requires no additional synthesis assumption.

Hybrid-pol depends on the *same* HH/VV/HV/VH inputs plus an additional circular-polarization-synthesis assumption (the LH/LV construction) — it inherits all of linear-pol's channel-mapping uncertainty (including the weaker HH fit) without adding independent information, so it is retained here as a **cross-check**, not the primary formulation.

The eigenvalue-purity diagnostic uses all 4 channels directly (no synthesis step) but answers a **different physical question** — how concentrated the scattering is in the dominant eigenmode of the full 4×4 covariance matrix, a generalized N-level "purity" (Barakat-type), not the classical 2-parameter Stokes DOP. It is a useful independent cross-check (and its whole-window value of 0.630 sits almost exactly between the other two), but is not a drop-in replacement for either Stokes-based DOP.

## 7. Known limitations, carried forward unchanged

- **G1→HH channel mapping is LIKELY, not CONFIRMED** — weakest quantitative fit of the four channels (`docs/RAW_DFSAR_VALIDATION.md` §5). All three formulations here use HH (directly or via LH), so all inherit reduced confidence to some degree.
- **No gain-imbalance or phase-orthogonality calibration is applied** — only XML bias-centering (`src/dfsar_raw_reader.py`, `apply_bias_correction=True` default). The phase-orthogonality discrepancy noted in `PROJECT_STATUS.md`/`docs/RAW_DFSAR_VALIDATION.md` §5 remains **UNRESOLVED**; these DOP values are uncalibrated for phase/gain beyond bias-centering.
- **This is a single mid-scene window of one non-candidate acquisition** — it validates that the *method* produces stable, plausible (0 ≤ DOP ≤ 1, no NaN, no infinities), formula-consistent results at scale. It says nothing about DOP anywhere near the candidate.
- **`DOP = 1.0000001192092896` (linear-pol max)** is a floating-point rounding artifact at the physical DOP=1 ceiling (fully polarized pixel edge case), not a formula error — values are otherwise correctly bounded in `[0, 1]`.

## Explicit statement (per task instruction)

> **The 2025-10-25 acquisition is used to validate the DOP computational pipeline only. It does not cover SP_840980_0797630.**

## Candidate-specific DOP status — RESOLVED this session

**COMPLETE.** A covering acquisition was identified, confirmed, downloaded, and processed. Full detail: `docs/CANDIDATE_ACQUISITION_SELECTION.md` §Update, `outputs/objective1/dop/candidate_acquisition.json`, `outputs/objective1/dop/candidate_dop.json`.

### Acquisition

`ch2_sar_ncxl_20220318t135736694_d_fp_d18` — 2022-03-18, station d18, quad-pol Level-1A SLANT-RANGE (HH/HV/VH/VV, `ComplexLSB8`). Product ID 2238611. Downloaded via PRADAN (authenticated), 1,920,035,453 bytes.

### Containment evidence (two independent checks, both real data, no guessing)

1. **True rotated image-footprint corners** (PDS4 `image_upper_left/upper_right/lower_right/lower_left_mapX/mapY`, not the loose bounding-box corners — see the false-positive lesson below): candidate ~20 km inside the nearest edge.
2. **Actual Level-1A Grid CSV** (`geometry/calibrated/20220318/ch2_sar_ncxl_20220318t135736694_g_sli_xx_fp_xx_d18.csv`, real per-pixel lat/lon/slant-range/incidence, 8,059×9 samples at 32-line/32-pixel spacing): nearest sampled grid point is **91 meters** from the candidate coordinate, at sample index 5 of 9 (comfortably inside the swath width, not at the range edge).

### A false-positive lesson from this session, documented not hidden

An initial screening pass tested candidate containment against the PDS4 label's **loose axis-aligned bounding-box corners** (`upper_left`/`upper_right`/`lower_right`/`lower_left`, without the `image_` prefix). This flagged `ch2_sar_ncxl_20191106t114537878_d_fp_d18` as containing — that 4.88 GB product was downloaded before the actual Grid CSV revealed it misses the candidate by **~75 km**. The bounding box is inflated well beyond the true rotated swath for near-polar passes (the axis-aligned box must enclose an elongated, rotated strip, leaving large empty triangular margins). The fix: use the label's **`image_*` corners**, which are the true rotated data-footprint quadrilateral, not the padded scene envelope — then confirm with the Grid CSV. That wrong download was deleted and is not used anywhere in this project's results. All 602 manifest acquisitions were then re-screened with the corrected method; 6 genuine hits were found, and the one with the largest edge margin was selected.

### Candidate-specific DOP results

Window: full range width (244 samples) × 2,000 lines centered on the Grid-confirmed candidate line (219,616) — **488,000 pixels**, genuinely centered on the candidate (unlike the non-candidate validation window above, which is centered on an arbitrary mid-scene location of a non-covering acquisition).

| Formulation | n px | mean | median | std | min | max | NaN % |
|---|---:|---:|---:|---:|---:|---:|---:|
| Linear-pol (HH/VV) | 488,000 | **0.680** | **0.708** | 0.183 | 0.012 | 0.999 | 0.0 |
| Hybrid-pol (synth. LH/LV) | 488,000 | 0.594 | 0.607 | 0.188 | 0.008 | 0.999 | 0.0 |
| Eigenvalue purity (tiled, 40×61 px, 200 tiles) | 200 | 0.594 | 0.509 | 0.203 | 0.356 | 0.981 | 0.0 |
| Eigenvalue purity (whole 488k-px window, single value) | — | **0.909** | — | — | — | — | — |

Full percentile tables: `outputs/objective1/dop/candidate_dop.json`. Maps/histograms: `outputs/objective1/dop/candidate_dop.png`, `candidate_dop_histogram.png`.

**Best-supported value: linear-pol (HH/VV) Stokes DOP, mean 0.680 / median 0.708** — same rationale as §6 above (standard construction, no synthesis assumption; this product's HH/HV/VH/VV channel identity is given directly by the PDS4 label filenames, not inferred via byte-level reverse engineering, so the `docs/RAW_DFSAR_VALIDATION.md` HH-weak-fit caveat does not apply here).

**Calibration:** XML bias-centering only (per-polarization `bias_real`/`bias_imag` from this product's own label), same as the non-candidate validation — no gain-imbalance or phase-orthogonality correction applied.

**This is genuinely candidate-specific** — clearly separate from the non-candidate 2025-10-25 pipeline-validation numbers above. Do not conflate the two.
