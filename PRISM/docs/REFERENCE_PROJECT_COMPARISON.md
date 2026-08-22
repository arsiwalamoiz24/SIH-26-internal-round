# REFERENCE_PROJECT_COMPARISON — github.com/Brukrish2006/Subsurface-Lunar-Ice-Detection

**Date:** 2026-08-22
**Method:** repository inspected via `WebFetch` (README + file listing summarization, no code execution, no cloning). This is a **reference only** per task instruction — nothing below was copied into PRISM without independent justification, and no threshold from it is treated as validated for PRISM.

Legend: **SOURCE-BACKED** = stated in the reference repo's own README/citations · **PRISM IMPLEMENTATION** = what PRISM actually does today, for comparison · **ASSUMPTION** = the reference repo's own unstated assumption · **INFERENCE** = this document's reasoning about the comparison, not a claim from either repo · **NOT APPLICABLE** = doesn't map onto PRISM's current scope/data.

---

## 1. Target site

- **SOURCE-BACKED:** Reference targets the Sverdrup-Henson Complex (~89.5°S, 152°E), citing Leone et al. (2023, *iScience*) for site selection.
- **PRISM IMPLEMENTATION:** PRISM's candidate is `SP_840980_0797630` at (−84.098°, 79.764°) — a different PSR, ~179 km from the pole rather than ~90°S, selected by PRISM's own Pv/PSR screening pipeline (`notebooks/objective1_dfsar_validation.ipynb.ipynb`), not from this reference's site list.
- **NOT APPLICABLE:** No direct numeric comparison is possible — different targets, different underlying evidence.

## 2. DFSAR product level and CPR/DOP formulas

- **SOURCE-BACKED:** Reference ingests **Level-2 GeoTIFF calibrated products** exported by third-party tool **MIDAS v4.2.4**, with its own radiometric calibration constant (`K = 10^(cal_dB/10)`, `cal = 70.31 dB`), and computes:
  - `CPR = (HH+VV+2HV) / (HH+VV-2HV)` (from full-pol) — a standard Raney-family CPR construction, self-computed from calibrated linear-pol bands.
  - `DOP = |LH-LV| / (LH+LV)` — a **simple amplitude-ratio** DOP definition using synthesized circular fields, NOT a Stokes-parameter DOP.
- **PRISM IMPLEMENTATION:** PRISM's CPR/SERD/T-Ratio for the candidate come directly from ISRO's own **pre-computed L3C-MOSAIC product** (`ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx`) — PRISM does not self-compute CPR from linear-pol bands anywhere. PRISM's DOP (non-candidate validation only, see `docs/DOP_VALIDATION_RESULTS.md`) uses the **Stokes-parameter formulation** `sqrt(S2²+S3²+S4²)/S1` from a genuine local spatial covariance, transcribed from `notebooks/objective1_y4r_polarimetry.ipynb.ipynb`, not the reference's amplitude-ratio formula.
- **INFERENCE:** These are two legitimate but **numerically different** DOP definitions (Stokes-magnitude-ratio vs. simple amplitude-ratio of two circular-basis powers) — they are not guaranteed to produce comparable numeric ranges or thresholds even on identical data. **A DOP threshold calibrated for one definition (e.g. the reference's `<0.13`) cannot be assumed to transfer to the other.** This is exactly why this document does not import the reference's DOP thresholds into PRISM.
- **ASSUMPTION (reference repo's own):** MIDAS-exported "Level-2" products and their `70.31 dB` calibration constant are taken as given inputs by the reference repo; PRISM has not independently verified MIDAS or this calibration constant against the official CH2DFSAR SIS (`sarlta/document/ch2_sar_pds_dp_archive_sis.pdf`), which does not mention MIDAS.

## 3. Ice-detection thresholds (4-tier classification)

- **SOURCE-BACKED:** Reference's tiers: CONFIRMED (CPR + DOP<0.35 + m-chi<−0.10 rad + smooth terrain + T<110K + not-rock), HIGH (CPR + DOP<0.13 + T<110K inside PSR), PROBABLE (CPR + DOP<0.35 inside PSR), CANDIDATE (CPR-only). Thermal gate cites Vasavada et al. (1999); m-chi decomposition cites Raney (2007).
- **PRISM IMPLEMENTATION:** PRISM currently applies **no fixed threshold classification** to CPR/DOP/Pv — Track A (`outputs/objective1/candidate_physics/`) reports raw statistics and mosaic-relative percentiles (e.g. candidate Pv at the 93.9th percentile, CPR at the 97.2nd percentile of the mosaic overview distribution) rather than a hard pass/fail gate. This is a deliberate choice, not an oversight — per this task's explicit instruction not to fabricate or borrow unvalidated thresholds.
- **NOT APPLICABLE / not imported:** None of the reference's CPR/DOP/chi/temperature numeric cutoffs are used anywhere in PRISM. PRISM has no thermal (DIVINER) data integrated, no m-chi decomposition computed, and no rock mask.
- **INFERENCE:** The reference's tiered-gate *structure* (combine multiple independent physical constraints rather than a single metric) is a reasonable design pattern PRISM's `Track I` evidence score (see `outputs/objective1/PHYSICS_RESULTS.json`) follows in spirit — but PRISM's score is explicitly a **normalized, unweighted-or-documented-weight composite**, not a validated multi-tier gate, and is labeled as such.

## 4. Preprocessing

- **SOURCE-BACKED:** Lee speckle filter (7×7, ENL=20 for FP; 5×5, ENL=4 for CP), auto-calibration gate that rescales the CPR threshold if the 90th-percentile CPR exceeds a saturation expectation at high incidence angle.
- **PRISM IMPLEMENTATION:** PRISM applies **no speckle filtering** anywhere — all Pv/CPR/SERD/T-Ratio statistics in `outputs/objective1/candidate_physics/` are computed on the ISRO-delivered mosaic pixels as-is. This is a genuine capability gap, not a hidden equivalence.
- **INFERENCE:** Speckle filtering is a legitimate, standard SAR preprocessing step (reduces multiplicative noise via spatial averaging) that PRISM's window-mean statistics only partially substitute for (PRISM's window means are similar in effect to a very large, uniform box filter, but this was not done for noise-reduction purposes and is not equivalent to Lee filtering, which is adaptive to local statistics).

## 5. Terrain / PSR / rock masking

- **SOURCE-BACKED:** LOLA DEM (5 m, auto-fetched from NASA PDS), slope/aspect/elevation; PSR = union of TMC-2 and OHRC darkest-2% masks; rock mask = roughest 2% of terrain excluded; DSC (doubly-shadowed-crater) geometry via LOLA topographic minimum + d/D ratio > 0.05.
- **PRISM IMPLEMENTATION:** PRISM uses the **LRO/LOLA PSR shapefile catalog** directly (`LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL`, 653 polygons) rather than deriving PSR from TMC-2/OHRC darkness — a different, independently-produced PSR source, not comparable numerically. PRISM's terrain (`outputs/objective2/SP_840980_0797630_terrain_stats.json`) uses **20 m/px LOLA DEM** (`LDSM`/`LDEM_80S_20MPP_ADJ.TIF`, coarser than the reference's 5 m) for slope, elevation, and a Terrain Ruggedness Index (Riley et al. 1999) — no rock mask, no aspect, no DSC geometry.
- **NOT APPLICABLE:** No TMC-2 or OHRC-derived PSR/roughness mask exists anywhere in PRISM. PRISM's own OHRC scene (`ch2_ohr_ncp_20251010T0942085687_d_img_d18`) was independently confirmed **not to cover the candidate** (`PROJECT_STATUS.md` §3.4) — even if PRISM wanted to replicate the reference's TMC/OHRC darkness approach, it does not currently have a covering OHRC scene to do so with.

## 6. ML methodology

- **SOURCE-BACKED:** Soft-voting ensemble (RandomForestClassifier + HistGradientBoostingClassifier + isotonic calibration), **9 explicitly radar-free features** (LOLA slope/elevation/aspect, TMC roughness, PSR score, incidence angle, IIRS band-depth indices, ShadowCam/OHRC brightness), trained on a **synthetic 600-sample anchor dataset built entirely from external, previously-confirmed sites** (LCROSS Cabeus, Chandrayaan-1 M³, Shackleton MiniRF+LPNS, Alaska permafrost analog, sunlit highlands, steep walls) — explicitly **zero training pixels from the target tile itself**, to avoid "label with CPR, train on CPR" circularity.
- **PRISM IMPLEMENTATION:** PRISM has **no trained ML model of any kind** as of this session (`Track J`, `outputs/objective1/ml/` skeleton only — see below). No Isolation Forest, no classifier, no labels.
- **INFERENCE (directly relevant to PRISM's Track J instruction):** The reference's core anti-circularity design — **train only on external, independently-confirmed anchor sites, never on the target tile's own radar-derived labels** — is exactly the principle PRISM's task brief also demands ("do not train an ML model on CPR and then claim it independently validates CPR-derived ice detection"). This is a **legitimate, source-backed best practice worth adopting in principle**. However: **PRISM currently has no equivalent external anchor dataset locally** (no LCROSS, M³, MiniRF, or permafrost-analog data in `PRISM_local_data` or elsewhere in this repo) — replicating the reference's approach would require acquiring that external labeled data first, which is out of scope for this session. PRISM's Track J therefore builds an **unsupervised, feature-only skeleton** (Isolation Forest over independent/complementary features), explicitly not a copy of the reference's supervised ensemble, and does not fabricate a training set.
- **ASSUMPTION (reference repo's own, not independently checked by PRISM):** That the six external anchor-site categories are appropriately analogous to the Sverdrup-Henson target site's physical conditions; that a 600-sample synthetic set (300/300) is sufficient for the 9-feature ensemble to generalize; PRISM did not verify these claims against the reference's own data.

## 7. Volume estimation and rover path planning

- **SOURCE-BACKED:** Two-stage Maxwell-Garnett dielectric-mixing inversion (CPR → permittivity → ice volume fraction, capped at 20% per Feldman et al. 2001) with Monte Carlo uncertainty propagation; A* rover path planning with Bekker-Wong soil-mechanics cost, PSR/communications-blackout/cold-soak penalties, and battery state-of-charge modeling.
- **PRISM IMPLEMENTATION / NOT APPLICABLE:** Neither exists in PRISM. Both are named as **future architecture** in the project's own `PROJECT_STATUS.md` ("A* routing... FastAPI... do not exist anywhere in the repository — 100% future architecture") and are out of scope for this session's tracks (which stop at physics evidence scoring and ML/CNN/YOLO integration skeletons).

## 8. Scientific references worth PRISM independently checking later

These are the reference repo's own citations, listed here for future PRISM use — **PRISM has not yet independently verified any of them against primary sources**, so they are marked ASSUMPTION/unverified pending a dedicated literature check:

- Sinha et al. (2026), *npj Space Exploration* — the CPR/DOP criterion the reference's thresholds derive from.
- Colaprete et al. (2010), *Science* — LCROSS Cabeus 5.6 wt% H₂O confirmation (widely-cited, independently well-established result).
- Spudis et al. (2010), *GRL* — Shackleton MiniRF + LPNS.
- Raney (2007) — m-chi compact-polarimetric decomposition (standard reference in the field; PRISM's own hybrid-pol LH/LV synthesis in `docs/DOP_VALIDATION_RESULTS.md` uses the same Raney-style circular-Tx-field-synthesis convention, independently arrived at from the pre-existing notebook, not copied from this reference).
- Feldman et al. (2001) — Lunar Prospector Neutron Spectrometer 20% ice-fraction upper bound.

## 9. Summary — what PRISM should and should not take from this reference

**Worth adopting (in principle, not yet implemented):**
- The anti-circularity ML training design (external anchor labels only) — flagged as the guiding principle for any future PRISM Isolation Forest / classifier work, contingent on acquiring comparable external labeled data.
- Multi-constraint (radar + terrain + thermal + optical) tiered evidence combination as a *design pattern* — PRISM's Track I evidence score follows this in spirit with normalized, documented weights rather than the reference's specific numeric tiers.

**Explicitly NOT adopted:**
- No CPR/DOP/chi/temperature numeric threshold from the reference is used anywhere in PRISM — different formulas (see §2), different product levels (§2), and different target site (§1) make direct threshold transfer scientifically unjustified.
- No MIDAS-derived calibration constant is used — PRISM's DOP validation uses only the raw product's own XML-stated bias/std calibration fields (`docs/RAW_DFSAR_VALIDATION.md`).
- No rock mask, m-chi decomposition, thermal gate, or volume-fraction inversion is implemented in PRISM as of this session.
