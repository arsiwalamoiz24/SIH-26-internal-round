# DEMO_SCRIPT — PRISM evaluator walkthrough, SP_840980_0797630

**Date:** 2026-08-22
**All files referenced below are real, generated this session, in `outputs/demo/`** (plus source detail in `outputs/objective1/`, `outputs/objective2/`, and `docs/`).

## 1. Candidate coordinate

`SP_840980_0797630` — lat **−84.098°**, lon **79.764°**. A LOLA/LRO-catalog PSR, area 14.234 km², selected by PRISM's own Pv/PSR screening pipeline (`notebooks/objective1_dfsar_validation.ipynb.ipynb`) from real Chandrayaan-2 DFSAR Y4R + CPR/SERD/T-Ratio mosaic products, cross-checked against the LOLA South Pole PSR shapefile.

## 2. Candidate location on the lunar radar mosaic

**File: `outputs/demo/candidate_overview.png`**

Shows the whole Y4R mosaic (Pv, grayscale) with the candidate marked (red star) and the extraction window (cyan box) drawn in true map coordinates (Moon_2000_South_Pole_Stereographic). This is the Track B georeferencing-verification artifact — the candidate's coordinate-to-pixel transform round-trips to 1.4×10⁻¹⁴° error, confirmed PASS.

## 3–6. Pv, CPR, SERD, T-Ratio

**File: `outputs/demo/candidate_radar_metrics.png`** (4-panel composite)

| Metric | Window mean | Percentile in mosaic |
|---|---:|---:|
| Pv | 0.454 | 93.9th |
| CPR | 0.565 | 97.2nd |
| SERD | 0.673 | 4.3rd |
| T-Ratio | 0.571 | 95.8th |

Pv, CPR, and T-Ratio are all elevated (top ~3–6% of the mosaic) and all higher inside the candidate's PSR than in its immediate surroundings — the classic radar ice-favorable signature this project's screening pipeline uses. SERD is the exception: unusually *low* both globally and inside the PSR — flagged, not hidden (see `docs/CANDIDATE_PHYSICS_RESULTS.md` §5, `docs/SERD_NAN_ANALYSIS.md`).

## 7. DOP validation / candidate DOP

**Candidate-specific DOP: BLOCKED.** No acquisition covering the candidate has been confirmed among the 602 manifest entries; PRADAN requires login, not bypassed. See `docs/CANDIDATE_ACQUISITION_SELECTION.md` for the exact manual download list and PRADAN navigation path.

**File: `outputs/demo/dop_validation.png`** — labeled **NON-CANDIDATE DOP PIPELINE VALIDATION**. Shows the DOP formulation comparison (linear-pol, hybrid-pol, eigenvalue-purity) on the one raw product physically present locally (2025-10-25 acquisition), which does **not** cover the candidate (~266–280 km outside its footprint) — this validates the *computation method* (reader, decode, channel mapping, three DOP formulas), not the candidate.

## 8. Terrain

**File: `outputs/demo/candidate_terrain.png`**

Real NASA LOLA 20 m/px DEM (slope, elevation, roughness/TRI), fetched via windowed remote read. **Reported honestly, including the unfavorable part:** 78.6% of the PSR interior exceeds the (unvalidated) 20° hazard threshold, vs. 10.5% of the approach terrain — a strong radar signature does not imply an easy landing site. Thresholds are explicitly author-flagged "crude," not mission-validated.

## 9. Physics evidence

**File: `outputs/demo/candidate_evidence_map.png`** — bar chart, all 7 shortlisted PSRs ranked by Physics Evidence Score, candidate highlighted in red.

**Candidate score: 1.0, rank 1 of 7.** Transparent method: unweighted mean of min-max-normalized Pv/CPR/T-Ratio interior-vs-surroundings deltas, ranked within PRISM's own 7-candidate shortlist. **Not a probability of ice** — no literature-calibrated weighting or absolute threshold exists for this product, so none is claimed. SERD (inconsistent sign) and DOP (unavailable) are explicitly excluded from the sum, not silently dropped.

Also: unsupervised Isolation Forest anomaly ranking (336 real PSRs) — candidate ranks 40th/336, reported with an explicit circularity caveat (features are Pv-derived, same as the selection criterion — not independent validation).

## 10. Final candidate ranking

| Component | Result |
|---|---|
| Radar physics rank (Pv/CPR/T-Ratio composite, 7-candidate shortlist) | **1st of 7** |
| ML anomaly rank (336-PSR Isolation Forest, non-independent features) | 40th of 336 |
| Terrain safety | Unfavorable (78.6% of PSR interior exceeds unvalidated hazard threshold) |
| Candidate-specific DOP | Unavailable (blocked) |

## 11. Remaining limitations (explained, not hidden)

- No candidate-specific DOP exists — the 602-acquisition manifest has been fully mapped to predicted Level-1A Grid filenames (confirmed against the official CH2DFSAR SIS PDF), but PRADAN's login wall blocks automated retrieval. A precise manual download list is ready (`docs/CANDIDATE_ACQUISITION_SELECTION.md`).
- No independent (non-radar-derived) ground-truth ice confirmation exists for this candidate anywhere.
- Terrain hazard thresholds are explicitly unvalidated against any lander/rover specification.
- The physics evidence score's equal weighting is a documented default, not a derived/literature weighting.
- The ML anomaly score's features are not independent of the candidate's own Pv-based selection (stated, not hidden).
- CNN/YOLOv8 boulder/hazard detection is planned architecture only — no labeled imagery dataset or candidate-covering optical scene exists to train on.

## Suggested walkthrough order for the evaluator

1. `outputs/demo/candidate_overview.png` — where is it, and is the georeferencing right?
2. `outputs/demo/candidate_radar_metrics.png` — what does the radar say?
3. `outputs/demo/dop_validation.png` — is the DOP *method* trustworthy, and why isn't there a candidate DOP number?
4. `outputs/demo/candidate_terrain.png` — is it landable?
5. `outputs/demo/candidate_evidence_map.png` — how does it rank against the alternatives?
6. `outputs/demo/physics_summary.json` / `docs/PHYSICS_RESULTS.md` — full machine-readable and narrative detail, with every number's source and confidence level.
