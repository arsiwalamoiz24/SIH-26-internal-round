# PHYSICS_RESULTS — SP_840980_0797630, consolidated

**Date:** 2026-08-22
**Full machine-readable version:** `outputs/objective1/PHYSICS_RESULTS.json` (also copied to `outputs/demo/physics_summary.json`)

Every number below carries a **CANDIDATE-SPECIFIC** or **NON-CANDIDATE VALIDATION** label and a source file, per task instruction. Nothing here is fabricated; every "BLOCKED" is a real, investigated blocker, not a placeholder.

## Candidate

`SP_840980_0797630`, lat **−84.098°**, lon **79.764°**, PSR area 14.234 km² (LOLA/LRO PSR catalog).

## 1. Georeferencing verification — CANDIDATE-SPECIFIC

**PASS.** Round-trip coordinate-transform error: 1.4×10⁻¹⁴°. Source: `outputs/objective1/candidate_physics/georeferencing_check.json` (Track B).

## 2. Radar physics (Pv / CPR / SERD / T-Ratio) — CANDIDATE-SPECIFIC

From the Y4R L4-MOSAIC + CPR/SERD/T-Ratio L3C-MOSAIC (2025-06-30, compiled from 602 acquisitions 2019-09-22 to 2023-10-18), coordinate-window extraction (±3,300 m, verified georeferencing):

| Metric | Window mean | Relative percentile in mosaic |
|---|---:|---:|
| Pv | 0.454 | 93.9th |
| CPR | 0.565 | 97.2nd |
| SERD | 0.673 | 4.3rd (anomalously low) |
| T-Ratio | 0.571 | 95.8th |

Full detail: `docs/CANDIDATE_PHYSICS_RESULTS.md`.

## 3. SERD NaN investigation — CANDIDATE-SPECIFIC finding + full-mosaic characterization

Candidate has **0% SERD NaN**. Full mosaic: 43.24% NaN, of which ~99.99% is shared outside-coverage masking (co-occurs with CPR/T-Ratio/Y4R-power NaN); the small residual (~0.01%) is CPR-correlated, consistent with expected SERD-algorithm masking. Full detail: `docs/SERD_NAN_ANALYSIS.md`.

## 4. DOP computational pipeline validation — NON-CANDIDATE VALIDATION

**The 2025-10-25 acquisition used here does NOT cover SP_840980_0797630** (~266–280 km outside its footprint). This validates the DOP computation method only.

| Formulation | Mean | Prior notebook (25×1024 patch) |
|---|---:|---:|
| Linear-pol (HH/VV) Stokes | 0.667 | 0.629 |
| Hybrid-pol (synth. LH/LV) Stokes | 0.574 | 0.557 |
| Eigenvalue purity (whole window) | 0.630 | 0.643 |

Best-supported: linear-pol Stokes DOP (standard construction, strongest channel mapping). Full detail: `docs/DOP_VALIDATION_RESULTS.md`.

## 5. Candidate-specific DOP — RESOLVED (this session, follow-up)

**No longer blocked.** With user-authenticated PRADAN access, the covering acquisition `ch2_sar_ncxl_20220318t135736694_d_fp_d18` (2022-03-18, station d18, quad-pol Level-1A SLI) was identified, confirmed via two independent real-data checks (true rotated image-footprint corners, 20 km margin; actual per-pixel Grid CSV, 91 m from nearest sample), downloaded (1.92 GB), and processed.

| Formulation | Mean | Median | n px | NaN % |
|---|---:|---:|---:|---:|
| Linear-pol (HH/VV) Stokes | **0.680** | **0.708** | 488,000 | 0.0 |
| Hybrid-pol (synth. LH/LV) Stokes | 0.594 | 0.607 | 488,000 | 0.0 |
| Eigenvalue purity (whole window) | 0.909 | — | — | — |

Best-supported: linear-pol Stokes DOP (mean 0.680, median 0.708) — same formula/rationale as the non-candidate validation run in §4, now genuinely centered on the candidate. Full detail, including the false-positive lesson from an earlier (corrected) screening pass: `docs/DOP_VALIDATION_RESULTS.md`, `docs/CANDIDATE_ACQUISITION_SELECTION.md`, `outputs/objective1/dop/candidate_dop.json`, `candidate_acquisition.json`.

**Note:** the Physics Evidence Score (§7) and ML anomaly score (§8) below were **not recomputed** with this new DOP value — they retain their original values (per explicit instruction not to redo those calculations this session). Incorporating candidate DOP into those scores is a natural next step, not yet done.

## 6. Terrain — CANDIDATE-SPECIFIC

Real NASA LOLA 20 m/px DEM (`LDSM`/`LDEM_80S_20MPP_ADJ.TIF`), fetched via GDAL `/vsicurl/` windowed remote read (no full multi-GB download):

| | Whole window (10×10 km) | PSR interior | Approach terrain |
|---|---:|---:|---:|
| Mean slope | 10.7° | 22.1° | 8.8° |
| % ≥20° (hazard, unvalidated threshold) | 20.2% | **78.6%** | 10.5% |
| Mean TRI (roughness) | — | 6.3 m | 2.5 m |
| Elevation range | 1,742 m | — | — |

**This is a genuinely unfavorable finding, reported honestly:** the PSR interior itself is quite steep by the (author-flagged-as-crude) 20° threshold. A strong radar ice signature does not imply an easy landing site. Full detail: `outputs/objective2/SP_840980_0797630_terrain_stats.json`.

## 7. Physics Evidence Score — CANDIDATE-SPECIFIC (ranking within PRISM's own shortlist)

**Score: 1.0 (rank 1 of 7)** shortlisted PSRs, from an unweighted mean of min-max-normalized Pv/CPR/T-Ratio interior-vs-surroundings deltas. **Not a probability of ice** — SERD and DOP are explicitly excluded (inconsistent directionality; unavailable, respectively). Full method and all 7 candidates' scores: `outputs/objective1/evidence_score/physics_evidence_score.json`.

## 8. ML (Isolation Forest) — CANDIDATE-SPECIFIC ranking, non-independent features

Unsupervised Isolation Forest over 336 PSRs (real sample, no fabricated data): candidate ranks **40th of 336** by anomaly score. **Circularity caveat, stated explicitly:** all 4 features are Pv-derived, the same metric that produced the candidate's shortlist selection — this is NOT independent validation. No supervised classifier was built (no ground-truth ice labels exist anywhere in this project). Full detail: `outputs/objective1/ml/isolation_forest_results.json`.

## 9. CNN / YOLOv8 — PLANNED / NOT TRAINED

No labeled imagery dataset exists; the one local OHRC scene does not cover the candidate. Integration interface only: `src/cnn_yolo_interface.py`.

## 10. Data confidence summary

| Component | Confidence |
|---|---|
| Radar physics (Pv/CPR/SERD/T-Ratio) | HIGH — real ISRO products, verified georeferencing, reproduces prior run to ~0.01–0.02 |
| Candidate-specific DOP | MODERATE-HIGH — real covering acquisition, confirmed via true footprint + Grid CSV (91 m), but only bias-centering calibration applied (no gain/phase correction), single acquisition/window |
| DOP pipeline method | MODERATE-HIGH — formulas transcribed verbatim; this product's HH/HV/VH/VV identity is ISRO-labeled directly (not byte-level-inferred), no phase/gain calibration |
| Terrain | HIGH data / hazard thresholds explicitly UNVALIDATED |
| Physics evidence score | MODERATE — real inputs, transparent method, equal-weighting is a documented default |
| ML anomaly score | LOW-MODERATE — real Isolation Forest, but features are circular relative to candidate selection |

## 11. Limitations (full list)

See `outputs/objective1/PHYSICS_RESULTS.json` → `limitations`, reproduced here:

- No independent ground-truth ice confirmation exists for this candidate.
- Candidate-specific DOP is now available (§5) but the evidence score and ML score have not yet been recomputed to include it — they still reflect the pre-DOP state.
- Candidate DOP calibration is bias-centering only (no gain-imbalance/phase-orthogonality correction) — same limitation as the non-candidate validation run.
- SERD is excluded from the evidence-score sum due to inconsistent (negative) directionality, unresolved by any source in this project.
- Terrain hazard thresholds are explicitly unvalidated (author-flagged "crude").
- Physics evidence score equal-weighting is a documented default, not a literature-justified scheme.
- ML anomaly score uses features not independent of the Pv-based candidate selection (circularity, explicitly not claimed as validation).
