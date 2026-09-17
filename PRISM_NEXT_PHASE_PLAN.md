# PRISM — Next Phase Plan: From Radar Screening to Physics-Informed Multi-Evidence Ice Site Screening

**Status:** Planning document only. Nothing in `PRISM/`, `frontend2/`, `scripts/`, or any pipeline output has been modified to produce this file.
**Date written:** 2026-09-15.
**Supersedes nothing** — this is additive to `README.md`, `PROJECT_GUIDE.md`, `DECISIONS.md`, `PRISM_PRD.md`, and `EVALUATION_SCRIPT.md`, all of which remain the authoritative record of what has actually been built and decided so far. Where this document disagrees with the PRD's original aspirational architecture (Bayesian fusion, Cloude-Pottier decomposition, a single composite "Science Confidence Budget"), that is called out explicitly — the PRD describes what PRISM *set out* to build; this document describes what PRISM's own evidence says it should build *next*, based on results the team already produced.

---

## 1. EXECUTIVE SUMMARY

**What we originally tried.** PRISM screened Chandrayaan-2 DFSAR radar data for four indicators — Pv (volume-scattering fraction), CPR (circular polarization ratio), SERD (roughness proxy), T-Ratio (dielectric proxy) — computed a fifth, separately-troubled indicator (DOP, degree of polarization, from raw Level-1A data), combined the first three into an unweighted "physics evidence score," and used that score to rank seven candidate permanently-shadowed regions (PSRs) by how ice-like their radar signature looks.

**Why radar-only analysis is insufficient — and this isn't a hypothesis, it's already measured.** PRISM's own team ran two independent control experiments against real, published ice ground truth, and both failed:

1. `INDEPENDENT_ICE_VALIDATION.md` (2026-08-22) ran the exact same Pv/CPR/T-Ratio evidence score against 7 craters with independent M3 spectral ice evidence and 4 craters explicitly checked and found *not* to show ice. The score did not separate them (positive mean 0.573 vs. control mean 0.636 — controls scored *higher*). LCROSS Cabeus — the one site on the Moon with a direct, in-situ physical water measurement — ranked **lowest of all 11 tested sites**.
2. `POSITIVE_NEGATIVE_CONTROL_VALIDATION.md` (2026-08-26) ran a focused head-to-head: Cabeus (positive control) vs. Wiechert (negative control). Every individual metric that feeds PRISM's combined score — Pv, CPR, T-Ratio — ranked Wiechert *above* Cabeus. Final classification: **FAIL**.

Separately, PRISM's own DOP computation cannot be reconciled with a directly comparable published value: at the exact craters (F2/F3 inside Faustini) that Sinha et al. 2026 report DOP = 0.10–0.13 for, PRISM computes DOP = 0.63–0.86 — after 8+ rigorously tested hypotheses (calibration, crosstalk, window size, an independently-verified alternate acquisition) failed to close the gap. This is documented in `PRISM/docs/DOP_SINHA_2026_RESEARCH.md` and is not something this plan proposes to re-investigate from scratch.

None of this means PRISM's radar work was done badly — the opposite is true. The team built the pipeline, then *tested it against ground truth it didn't control*, and reported the failure instead of hiding it or re-tuning until it passed. That discipline is the foundation this plan builds on.

**What we are changing.** PRISM stops asking *"does the radar prove ice?"* — a question its own evidence says radar alone cannot answer for unnamed, uncharacterized PSRs — and starts asking: *"is the ice hypothesis physically plausible at this specific site, what independent physical evidence channels support or contradict it, what else could explain what we're seeing, and how much can we actually conclude given real uncertainty?"* Radar (Pv/CPR/SERD/T-Ratio/DOP) becomes **one evidence channel among several**, explicitly weighted by how independent it is from the others and how well it has (or hasn't) survived a control test — not silently trusted because it's the channel we have the most code for.

**What PRISM is becoming.** A **physics-informed multi-evidence ice-site screening and prioritization system** that:
- Defines, per site, the *exact* ice hypothesis being tested (not a vague "is there ice" — see §8).
- Applies hard physical gates before considering a site plausible at all (thermal stability, PSR/illumination status).
- Weighs strong, genuinely independent evidence (direct/regional measurements like LCROSS, LEND, or literature at *named* craters) separately from weaker, radar-internal supporting evidence.
- Explicitly checks alternative explanations (surface roughness, fresh-crater ejecta, coincidental geometry) before treating a radar anomaly as ice-supportive.
- Is allowed to say **INCONCLUSIVE** — and, per its own evidence to date, that will be the honest answer for most or all of the 7 candidates until stronger evidence channels are added.

This is a narrower, more defensible claim than "we detect ice." It is also a much stronger hackathon/SIH submission, because it is the one thing almost no competing team will have: a system that ran its own falsification tests, reported the failures, and built its next phase around fixing the actual epistemic problem instead of adding a sixth radar ratio.

---

## 2. CURRENT BASELINE

Everything in this section describes code and output that exists in the repository today, verified by direct inspection. Nothing here is aspirational.

### 2.1 What PRISM currently does

PRISM is a lunar south-polar water-ice screening, hazard-mapping, and landing/rover-traverse-planning system built on real Chandrayaan-2 DFSAR radar data and NASA LOLA terrain data (`README.md`). Team OUTLIERs, SIH26_76 (ISRO-affiliated hackathon, `PRISM_PRD.md`). It runs four linked stages (`DECISIONS.md`):
1. **Module 1 — Ice screening** (radar ratios → shortlist ranking)
2. **Module 2 — Hazard mapping** (LOLA terrain → slope/roughness/illumination)
3. **Objective 3 — Landing-site selection**
4. **Objective 4 — Rover traverse planning** (real A* engine, most recently and actively worked on — see recent git log)

The **PRD's original vision** (`PRISM_PRD.md`) was more ambitious than what's built: a Bayesian sensor-fusion model producing `P(ice | radar, morphology, thermal)`, a Cloude-Pottier physics decomposition, Maxwell-Garnett volume estimation with credible intervals, and a single composite "Science Confidence Budget" gauge. **None of this Bayesian-fusion machinery is implemented.** What's implemented instead — an unweighted percentile-normalized evidence score, explicitly *not* labeled a probability (`src/physics_evidence_score.py`'s own docstring says so) — is scientifically more honest than the PRD's original framing, even though it's a simpler system. This plan treats the *actually-built* evidence-score approach as the real baseline, not the PRD's aspirational Bayesian model.

### 2.2 Candidate sites (exact, verified)

**7 screened candidates**, selected via the radar-ratio pipeline (`src/radar_pipeline.py`, `SHORTLIST_IDS`):

| ID | Notes |
|---|---|
| `SP_840980_0797630` | **Primary candidate.** −84.098°, 79.764°E, 14.234 km² |
| `SP_832640_0090770` | |
| `SP_830080_0535120` | |
| `SP_842420_0421060` | |
| `SP_817950_1586580` | |
| `SP_819860_1568660` | |
| `SP_809570_2454450` | |

**+ 2 featured external-validation sites**, treated as full peers in the frontend/PM4W/terrain pipelines but explicitly *not* part of the screened shortlist:
- **Faustini** (`SP_871460_0840750`) — cited for Sinha et al. 2026's M3 spectral detection at its F2/F3 sub-craters.
- **Cabeus** (`SP_844580_3134320`) — cited for Colaprete et al. 2010's LCROSS direct in-situ water detection.

**= 9 sites total** with real pipeline output today. None of PRISM's own 7 candidates is a named, independently-studied crater — Faustini and Cabeus are shown for comparison, not because they're PRISM candidates (`DOP_SINHA_2026_EXECUTIVE_SUMMARY.md`).

A separate **13-site independent reference table** (`src/validation_sites.py`) exists purely for validation: LCROSS Cabeus + 7 M3-positive craters (Faustini, de Gerlache, Haworth, Shoemaker, Sverdrup, Shackleton, Rozhdestvenskiy) + 5 M3-negative controls (Amundsen, Hedervari, Idel'son L, Wiechert, Bosch). 2 of the 13 (Rozhdestvenskiy, Bosch) are north-pole — no PRISM data coverage exists for them, reported honestly as `NO_COVERAGE`, not silently dropped.

### 2.3 Existing radar indicators (implemented, working code)

| Indicator | Formula / source | Status |
|---|---|---|
| **Pv** | `vol/(evn+vol+odd+hlx)` — Yamaguchi 4-component volume-scattering fraction, from Y4R L4 mosaic | Working, feeds the composite score |
| **CPR** | `(S1−S4)/(S1+S4)`, from Mini-RF/DFSAR S1–S4 | Working, feeds the composite score |
| **SERD** | Single-bounce Eigenvalue Relative Difference (roughness proxy), from L3C mosaic | Working, but large unexplained NaN fraction and inconsistent sign/direction — **explicitly excluded** from the composite score |
| **T-Ratio** | Dielectric proxy, from L3C mosaic | Working, feeds the composite score |
| **DOP** | `sqrt(S2²+S3²+S4²)/S1` (linear-pol Stokes), self-computed from raw Level-1A SLC | Working code, but **cannot be reconciled with the one published comparable value** (see §6) |

`src/physics_evidence_score.py` combines Pv, CPR, T-Ratio (SERD and DOP excluded, both for documented reasons) via min-max normalization and an unweighted mean. Its own docstring states this is **not a probability of ice** — a relative ranking only. This is the score currently shown on the frontend evidence page.

### 2.4 Existing DOP implementation

Separate from the four ratios above. Computed from raw Level-1A SLC complex data at specific craters (mainly F2/F3 inside Faustini's PSR, plus a secondary/alternate-acquisition test). See §6 for the full discrepancy against Sinha et al. 2026.

### 2.5 Other implemented evidence/hazard components

- **Terrain** (`src/terrain_algorithms.py`): real Sobel-gradient slope, uniform-filter RMS roughness, horizon-ray-cast illumination model, all from the raw LOLA `LDEM` elevation raster (a real bug — accidentally loading NASA's *precomputed slope* raster instead of elevation — was caught and fixed, `DECISIONS.md`). All 7 shortlisted PSRs show exactly 0.0 mean illumination across 24 simulated sun positions — an independent **geometric** confirmation that they are genuinely permanently shadowed, not just a catalog label.
- **ML — Isolation Forest v2** (`src/ml_pixel_anomaly_pipeline.py` / `_shortlist_pipeline.py`): per-pixel anomaly scoring on Pv/CPR/SERD/T-Ratio, genuinely independent of the screening metric (an earlier v1, PSR-level, is explicitly flagged in its own docstring as circular — reuses the same Pv ranking as its input feature — and is *not* independent evidence). Run for all 7 candidates; **not yet run for Faustini/Cabeus** (shown honestly on the frontend as "not run for this site").
- **ML — YOLOv8n-seg boulder detector** (`models/boulder_detector_yolov8n_seg.pt`, trained on BoulderNet/Prieur et al. 2023): real detections on real ShadowCam crops, all 9 sites. This is a **hazard/terrain-alternative-explanation** tool (boulders as landing/traverse obstacles), not an ice-evidence channel. Box mAP50 = 0.551, mask mAP50 = 0.179 — a domain gap between BoulderNet's training imagery and ShadowCam crops is acknowledged, not hidden.
- **No CNN ice classifier exists — by design.** No ground-truth ice labels exist for training one; the team decided not to fabricate this, correctly.
- **Optical imagery**: OHRC (Chandrayaan-2) was tried and **confirmed a dead end** — zero south-polar OHRC coverage near any candidate. Replaced by NASA LROC NAC (public) — then that too failed for the primary candidate's PSR interior (adjacent-pixel correlation −0.077, a noise signature — the interior gets zero direct sunlight, so an ordinary pushbroom camera has no signal there). Finally replaced by **NASA ShadowCam** (built specifically for PSR interiors, ~200× more sensitive than NAC) — verified with 0.994 adjacent-pixel correlation, real signal, used for all 9 sites. A real, stated limitation: a single ShadowCam frame is small relative to Faustini/Cabeus's much larger craters and cannot be arbitrarily widened.
- **PM4W** (`src/pm4w_detector_v2.py` etc.) — an independent, *published* multi-condition ice detector (Wang et al.) using real Mini-RF CPR + DOP + phase + backscatter **and real Diviner temperature**. Classifies **all 9–12 tested sites as NON_ICE, including Cabeus** (LCROSS-confirmed). This is PRISM's single strongest existing piece of evidence that radar-only/CPR-DOP screening does not reliably separate ice from terrain — already run, already logged, not something this plan proposes as new work. One structural gap: the `w` parameter and volume-scattering decomposition PM4W depends on are flagged as **structurally NO_DATA** — the literature's own formulas for deriving them are contradictory/unrecoverable, not just unavailable to PRISM specifically.
- **Diviner thermal**: listed in the PRD as "optional, degrades gracefully" — but a real Diviner `.tab` read is already embedded inline inside `pm4w_detector_v2.py`. **No standalone, first-class thermal-suitability module exists yet** — this is a gap, not a from-scratch build (see §9).

### 2.6 What is NOT implemented (do not assume otherwise)

- **M3 (Moon Mineralogy Mapper) spectral data** — not reprocessed anywhere in PRISM. Every M3 reference in the repo (Faustini, the 13-site reference table) is a **citation of someone else's published result** (Li et al. 2018; Sinha et al. 2026), not independent PRISM analysis. A prior investigation (`INDEPENDENT_ICE_VALIDATION.md` Task 1) searched specifically for a machine-readable, pixel-level M3 ice-detection dataset and **confirmed none exists publicly** — Li et al. 2018's own supplementary material presents detections only as a figure/map, not a coordinate table.
- **LAMP (Lyman-Alpha Mapping Project)** — never investigated in PRISM at all. Zero prior work to build on.
- **LEND (hydrogen/neutron)** — never implemented. Mentioned only in a literature-review doc as regional-scale (~10 km FWHM), which is already known to be coarser than any of PRISM's candidate PSRs (§5).
- **Bayesian sensor fusion, Cloude-Pottier decomposition, Maxwell-Garnett volume estimation with credible intervals, "Science Confidence Budget"** — all PRD v2 aspirations, none implemented.
- **Automated tests** — `PRISM/tests/` is an empty directory. No test suite exists anywhere in the pipeline.
- **`frontend/`** — superseded/dead as of 2026-08-24. `frontend2/` is the live dashboard (`candidates/`, `evidence/`, `terrain/`, `traverse/` routes). Any MVP work in §9 extends `frontend2/`, not `frontend/`.

---

## 3. THE NEW PRISM PIPELINE

```
Candidate Site (one of PRISM's 7, or a new one added later)
   │
   ▼
Data Acquisition            — pull each evidence channel's raw product for this site's coordinates
   │
   ▼
Data Preprocessing          — reproject/crop/window-read each product to the site's footprint
   │
   ▼
Physical Feasibility Checks (HARD GATES)
   — is the *specific* ice hypothesis being tested even physically possible here?
   — e.g. permanently shadowed? thermally stable (Diviner Tmax below a sublimation-relevant threshold)?
   — if a gate fails → site is reclassified ICE-UNLIKELY for *that* hypothesis, pipeline still
     records why (a gate failure is itself informative, not a dead end)
   │
   ▼
Terrain / Alternative-Explanation Analysis
   — slope, roughness, crater freshness/ejecta status
   — could terrain alone explain any radar anomaly we're about to look at?
   │
   ▼
Radar Evidence (existing Pv/CPR/SERD/T-Ratio)
   — supporting evidence only; explicitly NOT trusted alone (§1, §6 explain why)
   │
   ▼
Polarimetric Evidence (DOP/Stokes)
   — supporting evidence only, currently flagged UNRELIABLE pending §6's validation path
   │
   ▼
Spectral / Hydrogen Evidence (M3 / LAMP / LEND)
   — only if verified available for this site (§5) — otherwise explicitly marked NOT AVAILABLE,
     not silently skipped
   │
   ▼
Independent Corroboration
   — named-crater literature, LCROSS/LEND regional context, cross-instrument agreement
   — clearly separated from "another analysis of the same radar/optical data we already have"
   │
   ▼
Evidence / Uncertainty Engine (§8)
   — combines gates + strong evidence + supporting evidence + alternative-explanation flags
   — outputs a tiered classification, never a bare probability number
   │
   ▼
Final Site Classification
   — ICE-SUPPORTED / HIGH-CONFIDENCE
   — ICE-SUPPORTED / MODERATE-CONFIDENCE
   — INCONCLUSIVE
   — ICE-UNLIKELY
   │
   ▼
Visualization / Report
   — frontend2 evidence page, per-site rationale, explicit "what would change this classification"
```

**Plain-English walkthrough:** for each site, PRISM first asks "is this physically the kind of place ice could survive at all?" (gates). If yes, it gathers every evidence channel it can actually get real data for, explicitly notes what else (besides ice) could produce what it's seeing, and only then produces a classification — one that's allowed to say "we don't know yet" instead of forcing a yes/no.

---

## 4. INDICATOR/EVIDENCE MATRIX

**Table A — physical meaning and independence**

| Evidence channel | Physical quantity | Why it matters for ice | Potential alternative explanation | Independent from radar? |
|---|---|---|---|---|
| Diviner temperature | Max/min/mean bolometric surface & near-subsurface temperature | Ice is only thermodynamically stable below a temperature threshold (~110 K region, per Li et al. 2018's own Diviner-based cold-trap criterion) | None really — this is a physical gate, not a detector; a cold site can still be ice-free | **Yes** |
| PSR / illumination status | Fraction of time in direct sunlight; PRISM already computes this geometrically from LOLA + horizon ray-casting | Permanent shadow is necessary (not sufficient) for near-surface ice stability at most latitudes | A site can be a PSR and still have zero ice (no delivery mechanism, or ice has sublimated away over geologic time) — **do not equate PSR with ice** | **Yes** (already independent of radar) |
| LOLA terrain / slope | Elevation gradient | Confirms PSR interior morphology; needed to interpret radar geometry effects and to keep landing/traverse feasible | Steep slopes independently elevate CPR (rough-terrain artifact), which is exactly the ice/roughness ambiguity this whole plan exists to address | **Yes** |
| Surface roughness (RMS, from LOLA; SERD, from radar) | Small-scale height variance | Rough surfaces scatter radar similarly to volume-scattering ice in some regimes — roughness is the #1 documented *alternative explanation* for elevated CPR | This *is* the alternative explanation, not independent support | LOLA-roughness: yes. SERD: no (radar-derived) |
| Mini-RF/DFSAR radar ratios (Pv, CPR, T-Ratio) | Volume-scattering fraction, circular polarization ratio, dielectric proxy | Volume scattering and elevated CPR are classically associated with buried dielectric heterogeneity (ice) | Surface/near-surface roughness, fresh-crater ejecta blocks (documented for Cabeus, see `MINIRF_CABEUS_CPR_RECONCILIATION.md`), coherent-backscatter effects | No (this is the existing radar channel) |
| DOP / Stokes parameters | Degree of polarization of returned signal | Low DOP has been proposed (Sinha et al. 2026) as an ice-consistent depolarization signature | Basis/definition ambiguity itself (see §6) means a "low DOP" claim currently cannot be trusted without first resolving what's being measured | No, and currently **unreliable** (see §6) |
| M3 spectral (3 µm ice absorption) | Diagnostic near-IR absorption feature of H2O/OH at the surface | Direct(er) compositional evidence, physically different mechanism from radar volume scattering | Adsorbed OH from solar wind (not crystalline ice), spectral contamination, thermal-emission artifacts at these temperatures | **Yes — different phenomenon, different instrument, different depth sensitivity** |
| LAMP (UV) | Surface frost/ice UV albedo signature inside PSRs | Independent optical-band evidence, does not require sunlight (UV airglow illumination) | Regolith UV-albedo variation unrelated to ice; low native SNR in some published analyses | **Yes** |
| LEND hydrogen | Epithermal neutron suppression → inferred hydrogen enrichment | Hydrogen enrichment is a necessary correlate of water ice (though not exclusively water) | Hydrated minerals, other H-bearing volatiles, regional/orbital averaging artifacts at ~10 km scale | **Yes** |
| Independent observations / literature | LCROSS in-situ, named-crater M3/Mini-RF/LEND studies, peer-reviewed critiques | The only channels not derived from PRISM's own processing of its own data | N/A — but must be checked for genuine spatial/target overlap with our candidates, not just topical relevance | **Yes, when genuinely independent** (see caveat below) |

**Independence caveat, stated explicitly:** Mini-RF's *own* precomputed CPR/DOP mosaic (used inside PM4W) and PRISM's *self-computed* DFSAR CPR/DOP are **not fully independent of each other** — same underlying physical phenomenon, different processing chains. Treat agreement between them as weak corroboration (same instrument family, cross-processing check), not as two independent lines of evidence. True independence requires a different physical phenomenon (thermal, spectral, neutron) or a different mission/instrument measuring something radar cannot (LCROSS, LEND, M3, LAMP).

**Table B — availability, processing, and status**

| Evidence channel | Data source | Exact product/dataset to investigate | Spatial resolution | Temporal resolution | Expected availability for our sites | Processing required | Scientific strength | Current status | Priority |
|---|---|---|---|---|---|---|---|---|---|
| Diviner temperature | NASA LRO Diviner (PDS Geosciences Node) | `LRO-L-DLRE-4-RDR-V1` Polar Resource Product south, `dlre_prp_south.tab` (`docs/DIVINER_DATA_ACQUISITION.md`) | 2.88M-element triangular mesh, nearest-centroid distances <0.26 km at all 9 sites | Multi-year composite (annual max already time-integrated) | **AVAILABLE — CONFIRMED 2026-09-17** for all 9 sites + Wiechert | Done — `src/thermal_gate_pipeline.py` | Strong (a real physical gate, not a detector) | **Implemented** (Phase 2 complete: gate + cross-validation) | Maintain |
| PSR / illumination | LOLA-derived, already computed in-house | `src/terrain_algorithms.py` horizon-ray-cast model + LOLA/ASU PSR shapefile (653 polygons) | 20 m/px (native LOLA DEM) | Static geometry (multi-epoch sun-angle simulation already done, 24 positions) | **AVAILABLE NOW** | None — already built and run for all 7 candidates | Strong (geometric, independently confirms catalog PSR status) | **Implemented** | Maintain |
| LOLA terrain/slope | NASA LOLA DEM (public) | `LDEM_80S_20MPP_ADJ.TIF`, 20 m/px | 20 m/px | Static | **AVAILABLE NOW** | None — already built | Moderate (context, not ice proof) | **Implemented** | Maintain |
| Surface roughness (LOLA RMS) | Same LOLA DEM | `terrain_algorithms.py` uniform-filter RMS roughness | 20 m/px | Static | **AVAILABLE NOW** | None | Moderate (alternative-explanation channel) | **Implemented** | Maintain |
| Mini-RF/DFSAR radar ratios | ISRO PRADAN (Chandrayaan-2 DFSAR), NASA Mini-RF Global Mosaic | Y4R L4 mosaic, L3C mosaic | Sub-100 m class (mosaic-dependent) | Single-epoch mosaic | **AVAILABLE NOW** for the 7 candidates; NOT TESTED for the 13-site reference set (confirmed gap, `ice_reference_sites.csv`) | Already built | **Weak, per PRISM's own 2 control-test failures** — supporting only | **Implemented, validated as insufficient alone** | Maintain, re-weight down |
| DOP/Stokes | ISRO PRADAN raw Level-1A SLC | Various acquisitions, per-site coverage confirmed via footprint-polygon search (not bounding box) | Native SAR resolution (sub-100 m) | Single-epoch | AVAILABLE for Faustini F2/F3 and one alternate acquisition; **NOT TESTED** for the 7 candidates or the 13-site reference set | High — acquisition-hunt + full-pol Stokes processing per site (this is the expensive step) | **Currently unreliable — see §6** | Implemented, **discrepancy unresolved** | **HIGH (validation), LOW (as a gate) until resolved** |
| M3 spectral | Chandrayaan-1 M3 (PDS Geosciences Node / Li et al. 2018 SI) | No machine-readable pixel-level ice-detection product exists (confirmed by direct search, `INDEPENDENT_ICE_VALIDATION.md` Task 1); only named-crater-level citations usable | ~280 m/px native M3, but detections only published as a figure, not coordinates | Single mission epoch (2008-2009) | **NOT REALISTIC to reprocess**; crater-level citation only, and only for *named* craters — none of PRISM's 7 is named | High if attempting raw reprocessing (likely prohibitive); low if citation-only | Strong where it exists, but doesn't exist for our candidates | Not implemented (citation-only) | **LOW** (reprocessing); MEDIUM (as literature context) |
| LAMP (UV) | LRO LAMP (PDS Geosciences Node) | UV albedo/frost maps — **TO VERIFY**: does a public, gridded product exist at usable resolution for our 7 candidates? | TO VERIFY | TO VERIFY | **NEEDS VERIFICATION** — first-pass investigation not yet done | Unknown until verified | Potentially strong (independent phenomenon) if usable | Not investigated at all | **MEDIUM** (verify first, cheaply) |
| LEND hydrogen | LRO LEND (PDS Geosciences Node) | Epithermal neutron suppression / hydrogen-abundance maps | ~10 km FWHM footprint | Multi-year composite | **NOT REALISTIC at candidate scale** — every PRISM candidate PSR is smaller than one LEND resolution element (confirmed in `LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md`) | Low to pull the product; **high** to interpret meaningfully at sub-resolution scale | Weak at candidate scale, moderate at regional scale | Not implemented | **LOW** for per-candidate gating; **MEDIUM** for regional plausibility framing |
| Independent observations/literature | Peer-reviewed papers, USGS Gazetteer, NASA/ISRO mission pages | LCROSS (Colaprete 2010, Marshall 2011), M3 (Li 2018), Sinha et al. 2026, Ando et al. 2025 (ShadowCam), PM4W (Wang et al.) | N/A | N/A | **AVAILABLE NOW** for named reference craters; **NOT AVAILABLE** for PRISM's own 7 unnamed candidates specifically | Low (literature review, already substantially done) | Strong where target overlap is genuine; near-zero where it isn't | **Implemented as a validation harness** (13-site table); not yet a per-candidate live evidence input | **HIGH** — cheapest, already-proven-valuable channel |

---

## 5. DATA AVAILABILITY AUDIT

Data availability is the single biggest constraint on this plan — more than modeling sophistication, more than frontend polish. Below, every proposed channel is bucketed honestly.

### AVAILABLE NOW
- **Diviner temperature at all 9 sites (7 candidates + Faustini + Cabeus) + Wiechert — CONFIRMED 2026-09-17.** Re-acquired from NASA PDS (`docs/DIVINER_DATA_ACQUISITION.md`), re-extracted via `src/thermal_gate_pipeline.py` (Phase 2 deliverable, now built), cross-validated against the existing hardcoded values in `pm4w_detector_v2.py`/`pm4w_faustini_extension.py` — all 9 within 0.05K, distances all <0.26 km. Moved here from "LIKELY AVAILABLE" below.
- LOLA DEM terrain (slope, roughness, illumination/PSR geometry) — already built, already run for all 7 candidates + Faustini/Cabeus.
- Mini-RF/DFSAR radar ratios (Pv, CPR, T-Ratio, SERD) — already built, already run, already validated (and found insufficient alone).
- ShadowCam optical imagery — already verified real signal, already run for all 9 sites.
- YOLOv8n-seg boulder detection — already trained, already run for all 9 sites (hazard channel, not ice evidence).
- The 13-site independent reference table (LCROSS + M3-positive + M3-negative) — already built, already used for two control experiments.

### LIKELY AVAILABLE (needs a focused pull, not a research project)
- ~~Diviner temperature at the 7 candidate coordinates~~ — **moved to AVAILABLE NOW above, confirmed 2026-09-17.**
- **Mini-RF Global Mosaic CPR/DOP/Stokes**, independent of the DFSAR-derived version, as a cross-processing sanity check (not full independence, per the caveat in §4) — the team already has code paths that touch Mini-RF data (PM4W); confirm coverage at the 7 candidates specifically, not just at named craters.

### NEEDS VERIFICATION (first-pass investigation required before committing engineering time)
- **LAMP (UV frost detection).** Never investigated in PRISM. First task: does a public, gridded PDS product exist, and does it cover the 7 candidate coordinates at a resolution finer than the PSRs themselves? If yes, is it downloadable without a login gate? Until this is checked, do not assume it's usable.
- **DOP/Stokes coverage at the 7 candidates and the 13 reference sites** (currently `NOT TESTED` per `ice_reference_sites.csv`'s own header — this is not a guess, it's a column that's literally marked not-tested for every row). Requires the same true-footprint-polygon acquisition search already used successfully once for Faustini (`CANDIDATE_ACQUISITION_SELECTION.md`).
- **Additional Mini-RF Global Mosaic products** (Stokes-derived m-chi decomposition) as a possible resolution to the DOP basis ambiguity in §6 — worth a scoping pass before assuming it closes the gap.

### NOT REALISTIC FOR MVP
- **M3 pixel-level reprocessing at PRISM's own 7 candidates.** Already confirmed: no public, machine-readable pixel-coordinate product exists even for the *named* craters PRISM already cites — reprocessing raw M3 data from scratch, for unnamed candidates the original paper never examined, is a multi-week radiometric/spectral-calibration project, not a hackathon task.
- **LEND at candidate (sub-PSR) resolution.** The instrument's own 10 km footprint is larger than every PRISM candidate. Useful only as regional context ("is this general area hydrogen-enriched at all"), never as a per-candidate gate.
- **Full Bayesian sensor fusion / Cloude-Pottier decomposition** (the PRD's original architecture). No team bandwidth evidence this is coming, and — more importantly — it would not fix the actual problem identified in §1: the issue isn't that the current fusion is too simple, it's that most of the inputs to *any* fusion are currently either weak (radar) or absent (spectral/hydrogen) for these specific sites.
- **A CNN ice classifier.** No ground-truth labels exist for the 7 candidates or anywhere spatially matched to them. Correctly not attempted so far; nothing in this plan changes that.

---

## 6. THE DOP PROBLEM

**What we currently calculate.** Linear-polarization Stokes DOP, `sqrt(S2² + S3² + S4²) / S1`, computed from raw Level-1A SLC (phase-preserving, complex) DFSAR data at Faustini's F2 and F3 sub-craters. Result: **0.63–0.86** (varies slightly by acquisition/window; a fully independent alternate acquisition reproduced the same high range, 0.665/0.757).

**What the paper reports.** Sinha et al. 2026 (*npj Space Exploration* 2:22) report DOP = **0.10–0.13** for the same F2/F3 craters, and interpret low DOP as an ice-consistent depolarization signature.

**Why the numbers cannot automatically be compared.**
1. Sinha et al. 2026's own paper never specifies how its Stokes parameters (S1–S4) map onto the HH/HV/VH/VV channels DFSAR actually measures — the equation is given with only "S1–S4 are real numbers known as Stokes parameters," no construction formula.
2. The paper states no processing level, no calibration/crosstalk procedure, no multilook window, and no acquisition ID for its own DOP computation. A Supplementary Table 1 that likely resolves this was never retrievable in this investigation.
3. The paper's only cited authority for *interpreting* DOP (Raney et al. 2012's m-chi decomposition, via Mohan et al. 2011) is a **hybrid/compact dual-polarimetric** construction (2-channel, e.g. Mini-RF's actual CTLR architecture) — not the standard quad-pol construction DFSAR's raw data naturally supports. PRISM's own tested hybrid-pol analogue still returned 0.57–0.60, not 0.10–0.13 — real, but not sufficient by itself to close the gap.
4. PRISM's CPR values (an independently cross-checkable quantity) land close to the paper's: F2 44.75% vs. the paper's 47% elevated-CPR pixels; F3 33.3% vs. 42%. This makes "PRISM's radar pipeline/geolocation is simply wrong" an unlikely explanation — the discrepancy is specific to DOP, not the whole pipeline.

**Possible causes, ranked by current evidence:**
1. **Most likely: a different DOP *definition/basis*** than the standard full-coherent quad-pol Stokes DOP PRISM computes — most consistent with the hybrid-pol citation trail, though PRISM's own hybrid-pol test didn't fully confirm it.
2. **Also likely: a non-coherent/detected data product** rather than phase-preserving raw SLC (e.g., something closer to the Level-2 SRI product, or an undocumented noise/topographic-phase correction) — supported by the empirical observation that `|HH| ≈ |VV|` almost exactly in both crater interiors (S2≈0, itself a real, strong depolarization signature, physically consistent with ice), while the *coherent cross term* (S3, S4 — which requires preserved phase) is what inflates DOP toward 1, and this persists even at huge-N aggregation (ruling out small-sample noise as the cause).
3. **Ruled out:** covariance window size, small-sample statistical bias, absolute per-channel gain/phase calibration, relative HH/VV gain calibration, the paper's own documented azimuth-only multilook formula, a self-derived crosstalk correction, and — critically — the real, faithfully-implemented Ainsworth et al. 2006 crosstalk-calibration algorithm (converged to small, physically plausible crosstalk, but barely moved DOP). Also ruled out: wrong acquisition — a fully independent, independently-geolocated alternate acquisition reproduced the same high-DOP pattern.

**What information from the paper needs to be reproduced.** The paper's Supplementary Table 1 (acquisition IDs, presumably processing parameters) — this is the single piece of information most likely to resolve the ambiguity, and it is not publicly available.

**What exact investigation should happen before touching DOP code:**
1. **Contact Sinha et al. directly.** A specific question is already drafted (`DOP_SINHA_2026_RESEARCH.md` §17): ask exactly how S1–S4 map to measured channels, what processing level/calibration was used, and request Supplementary Table 1. This is the highest-value, lowest-engineering-cost next step and should happen in parallel with everything else in this plan, not block it.
2. **Scope (don't yet build) a power-only/detected-product DOP reproduction** using a non-coherent Mini-RF/DFSAR product, to test hypothesis 2 above, once/if a suitable product is located.
3. **Scope a rigorous hybrid/compact-pol m-chi reproduction** directly against Raney et al. 2012's actual equations (not an approximation), to more conclusively test hypothesis 1.
4. **Do not treat DOP as a hard gate or a trusted supporting-evidence input until one of the above closes the gap.** In the evidence engine (§8), DOP should be shown, transparently, as "measured but not currently interpretable against the one available published comparison" — not silently included in a score, and not silently dropped either.

**Step-by-step DOP validation experiment (proposed, not yet run):**
1. Draft and send the author-contact email (near-zero cost, blocked only on someone doing it).
2. While waiting: identify whether a non-coherent Mini-RF/DFSAR product (equivalent to "detected," phase-discarded) is accessible; if yes, recompute F2/F3 DOP from it and compare.
3. While waiting: implement the Raney et al. 2012 m-chi hybrid-pol DOP formula exactly as published (not PRISM's earlier approximate hybrid-pol test) and recompute F2/F3.
4. If either (2) or (3) lands within a defensible margin of 0.10–0.13, document the match, and only then consider re-deriving DOP for the 7 candidates using the matching method.
5. If the author responds with Supplementary Table 1 details, re-run whichever of (2)/(3) it points to as the correct method, and only *then* consider DOP for inclusion as supporting evidence in the engine.
6. Until 4 or 5 happens, DOP stays labeled **UNRESOLVED / NOT COMPARABLE** everywhere in the product, not silently reported as a confidence-boosting number.

---

## 7. VALIDATION WITHOUT A LARGE LABELLED DATASET

PRISM has no way to get thousands of labeled "this pixel is ice / this pixel is not" examples — nobody does, for the lunar poles. The team already discovered the right substitute in practice (`INDEPENDENT_ICE_VALIDATION.md`, `POSITIVE_NEGATIVE_CONTROL_VALIDATION.md`): **small-N, independently-sourced positive and negative reference sites, tested with the exact same pipeline used on real candidates, with results reported honestly even when they fail.** This section formalizes that as the standing validation methodology going forward, for every new evidence channel, not just radar.

**Known positive reference sites (already built, `src/validation_sites.py`):** LCROSS Cabeus (HIGH confidence — direct in-situ measurement); 7 M3-positive named craters (MODERATE confidence — remote spectral inference, itself disputed in places).

**Known negative/reference sites (already built):** 5 M3-checked-negative craters. "Negative" here precisely means "checked at M3's spectral/spatial sensitivity and no absorption feature found" — **not** "genuinely ice-free." This distinction must be preserved every time these sites are used, per the existing documentation's own careful phrasing.

**Independent instrument observations already available:** LCROSS (Cabeus), M3 (7 named craters), Mini-RF/ShadowCam literature (Ando et al. 2025 — does *not* confirm M3 detections at 13 of 14 tested PSRs), PM4W (Wang et al., independently classifies all tested sites NON_ICE).

**Published observations already reviewed:** `LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md` — the single most load-bearing prior-work doc for this whole plan; anyone starting on evidence-engine work should read it before writing code.

**Thermal/physical constraints:** Diviner-based cold-trap criterion (Tmax ≤ ~110 K) already used by Li et al. 2018 to define their own negative controls — this is exactly the kind of hard gate §8 formalizes.

**Cross-source consistency:** the DOP-vs-CPR agreement check in §6 (CPR matched the paper reasonably; DOP didn't) is itself a validation technique — when two indicators from the same underlying paper are compared, agreement on one and disagreement on another localizes the problem instead of casting doubt on everything.

**Uncertainty and spatial/temporal consistency:** every reference site's coordinate provenance, window size, and coverage status is already tracked per-site in `ice_reference_sites.csv` — this pattern (explicit provenance columns, explicit `NOT TESTED`/`NO_COVERAGE` values instead of blanks) should be the template for every new evidence channel's output table.

**The proof/support/evidence ladder this plan commits to using, consistently, everywhere:**

| Tier | Definition | Example from PRISM's own data |
|---|---|---|
| **PROOF** | Direct, in-situ physical measurement at the exact site | LCROSS at Cabeus. **PRISM has zero sites at this tier among its own 7 candidates.** |
| **STRONG SUPPORT** | Independent remote-sensing detection, different physical mechanism from what's being tested, genuinely targeting the exact site | M3 3 µm detection at a *named* crater. **None of PRISM's 7 candidates has this — they are unnamed, unstudied PSRs.** |
| **WEAK/SUGGESTIVE EVIDENCE** | Regional-scale independent data (LEND), or a radar/terrain indicator with documented alternative explanations, or proximity to (not identity with) an independently-studied site | PRISM's current Pv/CPR/T-Ratio evidence score, post-validation-failure — this is exactly where it now belongs |
| **INCONCLUSIVE** | Evidence is absent, contradictory, or the relevant hard gate cannot be evaluated | DOP at any of the 7 candidates, until §6 resolves |

**Honest conclusion for this section:** given the evidence available today, none of PRISM's 7 candidates can honestly be placed above WEAK/SUGGESTIVE. That is not a failure of this plan — it is the actual, current state of the evidence, and saying so clearly is the whole point of moving away from a system that implied more confidence than it had.

---

## 8. PROPOSED EVIDENCE ENGINE

**Explicitly not this:**
```
Pv match           = 20 points
CPR match          = 20 points
T-Ratio match       = 20 points
SERD match          = 20 points
DOP match           = 20 points
─────────────────────────────
total               = "ice probability"
```
This is exactly the naive scheme PRISM's own PRD (§2) already criticized in competing teams' work, and it's precisely what PRISM's own two control experiments showed doesn't work even when applied to PRISM's own metrics.

**Instead — a tiered structure:**

**A. HARD PHYSICAL GATES.** Binary/near-binary conditions that define whether the *specific* ice hypothesis under test is even plausible. Example gates for "stable near-surface water ice in permanent shadow": (1) site is genuinely a PSR — already geometrically confirmed for all 7 candidates; (2) Diviner Tmax is below the temperature at which water ice sublimates on relevant timescales (~110 K region, following Li et al. 2018's own criterion) — **currently not evaluated per-candidate**, this is the highest-priority new gate to add (§9). A gate failure doesn't kill the pipeline — it reclassifies the site as ICE-UNLIKELY *for this specific hypothesis* and records exactly which gate failed, which is itself useful information (e.g., "warm PSR, ice hypothesis excluded, but site may still be scientifically interesting for other reasons").

**B. STRONG EVIDENCE.** Independent observations at PROOF or STRONG SUPPORT tier (§7) for the *exact* site. **Currently zero for all 7 PRISM candidates** — this is the honest, load-bearing fact this whole plan is built around. If a new channel (LAMP, a verified Diviner product, a genuinely site-matched LEND read) reaches this tier for a candidate, it should dominate the final classification.

**C. SUPPORTING EVIDENCE.** Radar/polarimetric/terrain indicators — currently Pv, CPR, T-Ratio, (DOP once §6 resolves it). Can *raise or lower* confidence but, per §7, can never alone justify anything above WEAK/SUGGESTIVE. This tier is exactly where PRISM's evidence score already sits — the fix here is re-labeling and re-scoping its claimed strength, not rebuilding it.

**D. CONFLICT / ALTERNATIVE-EXPLANATION ANALYSIS.** For every piece of supporting evidence, explicitly check whether a non-ice mechanism plausibly explains it before counting it as support. PRISM already has real examples of this working: `MINIRF_CABEUS_CPR_RECONCILIATION.md` explains Cabeus's elevated CPR as a documented fresh-crater-ejecta effect (Fassett et al. 2024), *not* ice — this is exactly the kind of check that should run automatically, not just appear in a one-off doc.

**E. UNCERTAINTY.** The engine must be able to output **INCONCLUSIVE**, and — given §7's honest ladder — that should be the *default* answer for any of the 7 candidates until B-tier evidence exists for at least one of them.

**Worked example — primary candidate `SP_840980_0797630` through the engine:**

| Step | Result |
|---|---|
| Gate: PSR status | **PASS** — 0.0 illumination across 24 sun positions, geometrically confirmed |
| Gate: thermal stability (Diviner) | **NOT YET EVALUATED** — highest-priority next task |
| Strong evidence (B) | **NONE** — not a named crater, no LCROSS/M3/LAMP/LEND site-specific data |
| Supporting evidence (C) | Pv/CPR/T-Ratio evidence score = highest-ranked of the 7 shortlisted candidates, *but this metric has failed 2 independent control tests* — down-weighted accordingly |
| Alternative-explanation check (D) | Not yet run systematically for this candidate — planned in §9/§10 |
| Uncertainty (E) | High — no strong evidence, supporting evidence of known-weak reliability |
| **Classification today, honestly** | **INCONCLUSIVE** — best-ranked among PRISM's own candidates, but that ranking is internally-consistent within a method PRISM's own team has shown does not reliably separate ice from non-ice sites |

**Future weighting/likelihood approach (explicitly deferred, not built now):** once real independence and reliability numbers exist for more than one channel (e.g., once §6 resolves DOP, once a thermal gate exists, once LAMP availability is verified), a genuine likelihood-ratio or Bayesian-network structure over the gates/tiers above becomes possible. Building that machinery now, on top of channels that are themselves unvalidated, would just add a second layer of false confidence on top of the first — exactly the mistake this plan exists to avoid.

---

## 9. MINIMUM VIABLE PRODUCT (MVP)

**Design principle:** the MVP is not "build every evidence channel." It is "make the evidence-tier structure real and visible, using channels PRISM can actually get data for in the time available, and be honest on the frontend about what's missing." Given how much is already implemented (§2), most of the MVP is *re-organizing and extending* existing code, not writing a new pipeline from scratch.

**Exact inputs:**
- Existing Pv/CPR/T-Ratio evidence score (already computed, all 9 sites).
- Existing LOLA terrain/slope/roughness/illumination (already computed, all 9 sites).
- Existing PSR-geometry confirmation (already computed).
- **New:** Diviner temperature per candidate (extend the existing one-off PM4W read into a first-class per-site extraction — this is the single highest-leverage new input, since it's the one hard gate not yet evaluated).
- Existing 13-site independent reference table, used as the validation harness for every new channel added (not as a live per-candidate input).
- Existing alternative-explanation write-ups (e.g., `MINIRF_CABEUS_CPR_RECONCILIATION.md`) formalized into a small, explicit per-candidate checklist rather than left as prose docs.

**Exact processing:**
1. Add a thermal gate module: pull Diviner Tmax (or the best available proxy) for each of the 9 sites; apply the ~110 K-region threshold; record PASS/FAIL/NO_DATA explicitly per site.
2. Re-label `physics_evidence_score.py`'s output from a numeric score implying precision to a qualitative supporting-evidence tier, and surface the fact that it has failed 2 control tests directly next to the number, not buried in a doc.
3. Add a small alternative-explanation checklist per site (roughness flag from LOLA RMS + SERD sign; ejecta/fresh-crater flag where literature exists e.g. Cabeus).
4. Combine gates + supporting-tier + alternative-explanation flags into the 4-way classification (§8) per site — a simple decision table, not a trained model.

**Exact indicators used in the MVP:** PSR geometry (gate), Diviner thermal (gate), Pv/CPR/T-Ratio (supporting), LOLA roughness + SERD sign (alternative-explanation flag). That's it — no M3/LAMP/LEND reprocessing in the MVP.

**Exact output:** per site — one of ICE-SUPPORTED/HIGH, ICE-SUPPORTED/MODERATE, INCONCLUSIVE, ICE-UNLIKELY, plus a short rationale string listing which gates passed, what evidence exists, and what alternative explanation (if any) was checked. Given §7's honest ladder, **expect most or all of the 7 candidates to classify as INCONCLUSIVE** in this MVP — that is a correct, not a disappointing, outcome, and the demo narrative should say so directly rather than avoid it.

**Minimal frontend/dashboard requirements:** extend `frontend2/src/data/prism.ts` and `frontend2/evidence/page.tsx` (already the right home for this — it already shows a unified per-site evidence view across all 9 sites with honest provenance comments) to add: (1) the classification badge, (2) a gate-by-gate breakdown, (3) the alternative-explanation flags, (4) a visible "what would upgrade this classification" note. Do not build a new page or a new app.

**What we deliberately leave out of the MVP:** M3/LAMP/LEND data pulls (§5 — not realistic in the timeframe); DOP as a scored input (§6 — unresolved); any Bayesian/likelihood weighting (§8 — premature); a CNN classifier (no labels); full-resolution regional-scale processing beyond the existing 9 sites.

**What can be added later, in order of leverage:** (1) DOP, once §6 resolves it; (2) a verified LAMP channel, if §5's verification pass finds one; (3) genuine LEND regional-context framing (clearly labeled as regional, not per-candidate); (4) extending the whole engine to more than 7 candidates if a broader screening pass is ever wanted.

---

## 10. PHASED EXECUTION PLAN

> Adjusted from the template in the brief to reflect what's actually already done — several "phases" below are mostly complete, and are marked as such rather than re-planned from zero.

**PHASE 0 — Freeze current baseline.** *Objective:* lock down what "current implementation" means so nothing in this plan is built against a moving target. *Tasks:* tag/commit the current state of `PRISM/src`, `PRISM/outputs`, `frontend2`; treat this document itself as the frozen baseline description. *Deliverable:* this document + a git tag. *Dependency:* none. *Done when:* the team agrees this document's §2 is accurate. *Status:* **effectively done by writing this document** — no new work required beyond review.

**PHASE 1 — Data availability audit.** *Objective:* resolve every "TO VERIFY"/"NEEDS VERIFICATION" row in §4/§5. *Tasks:* confirm Diviner product/resolution for all 9 sites; confirm Mini-RF Global Mosaic coverage at the 7 candidates specifically; do a first-pass LAMP availability check; confirm DOP coverage status (already partially known — `NOT TESTED` everywhere). *Deliverable:* an updated version of §4/§5's tables with every row resolved to AVAILABLE/NOT AVAILABLE. *Dependency:* none — can start immediately. *Done when:* zero "TO VERIFY" rows remain. *Parallel with:* Phase 6 (DOP author contact).

**PHASE 2 — Thermal gate (Diviner).** *Objective:* build the one new hard gate the MVP needs. *Tasks:* extract per-site Diviner Tmax for all 9 sites; apply the cold-trap threshold; record PASS/FAIL/NO_DATA. *Deliverable:* `src/thermal_gate_pipeline.py` (or similar) + a per-site JSON/CSV output, same provenance discipline as `ice_reference_sites.csv`. *Dependency:* Phase 1's Diviner-availability confirmation. *Done when:* all 9 sites have a recorded gate result.

**PHASE 3 — Alternative-explanation flags.** *Objective:* formalize the roughness/ejecta checks that already exist as prose (`MINIRF_CABEUS_CPR_RECONCILIATION.md`, SERD-sign notes) into a per-site checklist. *Deliverable:* small module producing a flag list per site. *Dependency:* none (existing data only). *Can run in parallel with Phase 2.*

**PHASE 4 — Evidence engine (MVP version).** *Objective:* combine gates + existing evidence score + alternative-explanation flags into the 4-way classification (§8/§9). *Deliverable:* one script producing a classification + rationale per site, tested against the existing 13-site validation harness before being trusted on the 7 candidates. *Dependency:* Phases 2 and 3. *Done when:* it runs end-to-end on all 9 sites and the team has reviewed the (likely mostly-INCONCLUSIVE) output honestly.

**PHASE 5 — DOP validation experiment.** *Objective:* execute §6's step-by-step plan. *Tasks:* send the author-contact email; scope/attempt the power-only and hybrid-pol reproductions. *Deliverable:* either a resolved DOP method or a documented "still unresolved" status with DOP excluded from the engine. *Dependency:* none — can start immediately, in parallel with everything else. *Done when:* DOP is either included (with a justified method) or formally excluded from the MVP engine.

**PHASE 6 — Frontend integration.** *Objective:* surface the classification, gates, and rationale on `frontend2/evidence`. *Deliverable:* updated `prism.ts` + `evidence/page.tsx` (extend, don't rebuild). *Dependency:* Phase 4's output shape. *Can start on mock data before Phase 4 finishes, to de-risk the UI work in parallel.*

**PHASE 7 — Validation pass on the new engine.** *Objective:* re-run the same style of control experiment §7 describes (13-site reference table) against the *new* gates/flags, not just the old radar score, to check whether the thermal gate and alternative-explanation flags actually improve separation. *Deliverable:* an `INDEPENDENT_ICE_VALIDATION_V2.md`-style honest report. *Dependency:* Phases 2–4. *Done when:* the report exists, whatever it finds.

**PHASE 8 — Additional evidence channels (post-MVP, only if time remains).** *Objective:* pursue whichever of LAMP/LEND-regional/DOP-if-resolved passed Phase 1's availability check. *Dependency:* Phase 1 + Phase 5.

**PHASE 9 — Final evaluation/demo.** *Objective:* prepare the honest narrative (§1's executive summary is the seed) for judges — leading with the control-test failures as evidence of rigor, not hiding them. *Dependency:* Phase 4 minimum, Phase 7 ideally.

---

## 11. NEXT 5 EXACT ACTIONS

1. **Verify Diviner coverage and resolution for all 9 sites (7 candidates + Faustini + Cabeus).** Confirm whether the existing `.tab`-read code path inside `pm4w_detector_v2.py` can be generalized, or whether a different Diviner PDS product (annual max/min/mean map) is needed, and pull real Tmax values for each site's coordinates.
2. **Send the Sinha et al. 2026 author-contact email** (question already drafted in `PRISM/docs/DOP_SINHA_2026_RESEARCH.md` §17) requesting their Supplementary Table 1 and exact Stokes-to-channel construction.
3. **Do a first-pass LAMP availability check**: search the PDS Geosciences Node for a public, gridded LAMP UV-frost product; determine resolution and whether it covers the 7 candidate coordinates; record the result as AVAILABLE/NOT AVAILABLE in an updated §4/§5 table — do not build anything yet, just verify.
4. **Confirm DOP/Stokes acquisition coverage for the 7 candidates and the 13-site reference table** using the same true-footprint-polygon search method already proven for Faustini (`CANDIDATE_ACQUISITION_SELECTION.md`) — the `ice_reference_sites.csv` column currently reads `NOT TESTED` for every row; resolve it to yes/no per site.
5. **Formalize the Cabeus CPR-ejecta alternative-explanation writeup (`MINIRF_CABEUS_CPR_RECONCILIATION.md`) into a reusable code check** (roughness/ejecta flag), as the first concrete piece of §8's "D — conflict/alternative-explanation analysis" tier, and apply it to all 9 sites, not just Cabeus.

---

## 12. TEAM DIVISION

Suggested for 4–6 students, aligned to the existing module ownership pattern in `DECISIONS.md` rather than inventing a new structure:

| Track | Owns | Depends on |
|---|---|---|
| **Data acquisition & availability audit** | Phase 1 (§10): Diviner, Mini-RF cross-check, LAMP first-pass, DOP coverage search | Nothing — start immediately |
| **Radar/DOP** | Phase 5 (§10): DOP validation experiment, author contact, power-only/hybrid-pol reproduction attempts | Data-acquisition track's DOP-coverage findings |
| **Terrain/environment** | Phase 2 + 3 (§10): Diviner thermal gate, alternative-explanation flags (roughness/ejecta) | Data-acquisition track's Diviner findings |
| **Independent evidence** | Maintain/extend the 13-site reference table; run Phase 7's validation pass against the new engine; own the honest-reporting discipline (§7) | Terrain/environment and radar/DOP tracks' outputs, to validate against |
| **Evidence engine** | Phase 4 (§10): combine gates + supporting evidence + flags into the classification, own §8's decision logic | Terrain/environment and data-acquisition tracks |
| **Frontend/integration** | Phase 6 (§10): extend `frontend2/evidence/page.tsx` and `prism.ts` | Evidence-engine track's output shape (can start on mocked shapes in parallel) |

**Sequencing note:** data acquisition and DOP validation can both start on day one with zero dependencies. Everything else waits on data acquisition's findings for at least one input (Diviner or DOP coverage). Frontend can de-risk itself early by building against a mocked classification shape before the evidence engine is finished.

---

## 13. FAILURE CONDITIONS / KILL CRITERIA

Concrete signals that should cause the team to **drop** a specific piece of work rather than keep pushing on it:

- **Diviner does not resolve individual candidate PSRs** (i.e., native product resolution is coarser than the PSR itself, like LEND already is) → drop the per-candidate thermal *gate*, keep Diviner only as regional context, and say so explicitly rather than quietly using a resolution-mismatched number as if it were site-specific.
- **LAMP has no public, downloadable product covering the candidates**, or requires processing tooling the team cannot realistically stand up in the time available → drop it from the MVP, keep it as a documented "future work" item, do not attempt a partial/approximate implementation that would misrepresent confidence.
- **DOP's Supplementary Table 1 is never obtained, and neither the power-only nor hybrid-pol reproduction lands within a defensible margin of 0.10–0.13** → DOP stays permanently excluded from the scored engine (labeled UNRESOLVED), not quietly re-included once time pressure mounts.
- **A proposed new indicator turns out not to be physically independent of radar** (e.g., it's just another Mini-RF product reprocessed a different way) → do not count it as independent corroboration in the evidence engine; at most, treat it as a cross-processing sanity check on the existing radar channel, per §4's independence caveat.
- **Processing requirements for any channel exceed the realistic remaining timeline** (e.g., raw M3 spectral reprocessing, full SPICE/ISIS photogrammetry for any imagery source) → do not attempt; cite the literature instead, clearly labeled as citation not PRISM-computed.
- **The re-validation pass in Phase 7 shows the new gates/flags don't improve separation either** → this is not itself a reason to hide the result. Report it exactly as `INDEPENDENT_ICE_VALIDATION.md` reported the original failure. The project's credibility rests on this pattern continuing, not on eventually forcing a pass.
- **A candidate fails its PSR-geometry gate on closer inspection** (it shouldn't, given the existing 24-sun-position confirmation, but if new data ever contradicts it) → immediately reclassify that candidate ICE-UNLIKELY for the primary hypothesis, don't quietly keep using old geometry.

---

## 14. FINAL RECOMMENDATION

**Is PRISM still viable?** Yes — but only if "viable" is understood correctly. PRISM cannot currently claim, and should not claim, that any of its 7 candidates contains ice with meaningful confidence. What it *can* claim, and what is genuinely valuable, is that it has built a working, real-data pipeline that correctly identified its own method's limitations through honest control testing — most hackathon teams never run this kind of test on themselves at all, let alone report a failure.

**What is the strongest version we can realistically build?** A screening-and-prioritization tool that is explicit about evidence tiers, runs a real thermal gate, flags known alternative explanations, and is willing to say INCONCLUSIVE for most sites — paired with a resolved (or honestly-still-open) DOP story and a verified picture of what additional public data genuinely covers these candidates. That is achievable in a hackathon timeframe because most of the hard engineering (radar pipeline, terrain pipeline, ML anomaly detection, optical imagery, a real A* traverse planner) is already built and working.

**What is the biggest scientific risk?** That the team (or the pitch) slides back into implying more certainty than the evidence supports — e.g., presenting the evidence-score ranking as if higher rank meant "more likely ice" after §1's two control experiments already showed that specific claim is unsupported. The single most important discipline to carry forward is the one already demonstrated in `DECISIONS.md`: report what's found, not what would look best.

**What is the biggest engineering risk?** Time spent chasing data that turns out unavailable (M3 pixel coordinates, LEND at candidate resolution) instead of front-loading the availability audit (§5, §10 Phase 1) before committing to build anything on top of it. The second-biggest risk is scope creep into full Bayesian fusion machinery that adds complexity without adding real evidence underneath it.

**What should we NOT waste time on?** A sixth radar ratio. A CNN classifier without labels. Raw M3/LEND reprocessing from scratch. A numeric "ice probability" that implies more precision than any current evidence channel supports. Rebuilding the frontend from scratch instead of extending `frontend2/evidence`.

**What would make this compelling for an SIH/student-innovation submission?** Precisely the thing most teams won't have: a documented, falsifiable methodology that tested itself against real ground truth, found real problems, and responded by re-architecting around honesty about uncertainty instead of hiding it. "We built a system rigorous enough to catch its own mistakes, and here's exactly what we're doing about them" is a stronger, more memorable pitch than "we found ice" — and it has the decisive advantage of being true.
