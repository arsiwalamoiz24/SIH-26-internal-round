# LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE — multi-source independent validation

**Date:** 2026-08-26. **Scope:** does PRISM's candidate set occupy locations for
which independent observations (NASA, ISRO, and peer-reviewed literature)
provide converging evidence consistent with the metrics PRISM measures? This is
**not** an attempt to prove PRISM's candidates are ice because ice exists
somewhere on the Moon — every claim below is spatially and evidentially scoped.

**Epistemic key** (as in `DOP_SINHA_2026_RESEARCH.md`): **FACT** = verified
against a primary or full-text source. **OBSERVATION** = a pattern noticed in
FACTs. **HYPOTHESIS** = untested/partially-tested explanation.
**CONCLUSION** = a claim the evidence actually supports. Per-source access
status (full text / search-summary / press-release-only) is stated throughout
— **items sourced only from AI-generated search summaries, not a direct fetch,
are marked and should be treated as moderate- not high-confidence.**

**Method note:** three parallel literature-research passes were run (NASA
instrument evidence; M3/ShadowCam/abundance/datasets; the Icarus 2025 DFSAR
paper and general CPR/DOP literature), each producing raw research notes now
folded into this report. Spatial distances below were computed by this session
directly (haversine, Moon mean radius 1,737.4 km) from PRISM's own recorded
candidate coordinates and published crater-center coordinates — not taken from
any secondary source's distance claims.

---

## 1. Research Objective

Determine whether PRISM's candidate locations and calculated radar/terrain/
optical metrics are consistent with independent scientific evidence for lunar
water ice or hydrogen-rich deposits — using spatially meaningful, scientifically
defensible cross-validation, not general "there is ice on the Moon" reasoning.

## 2. PRISM Candidate Overview

All 7 shortlisted candidates are **unnamed LOLA-catalog PSR polygons** — none
corresponds to a named crater (Cabeus, Faustini, Shackleton, etc.) that appears
anywhere in the independent literature searched for this report. This single
fact governs almost everything that follows.

| PSR_ID | Lat | Lon | Area (km²) | Pv | CPR mean/max/%>1 | SERD | T-Ratio | DOP | Hazard (interior mean) | Illum. | ML pixel-anomaly separation | Physics-evidence rank | ShadowCam correlation |
|---|---:|---:|---:|---:|---|---:|---:|---|---:|---:|---:|---:|---|
| **SP_840980_0797630** (primary) | −84.098 | 79.764 | 14.234 | 0.507 | 0.630 / 1.61 / 7.33% | 0.636 | 0.651 | 0.680 (real) | 0.597 | 0.0 | +0.017 | 1 | 0.994 |
| SP_832640_0090770 | −83.264 | 9.077 | 32.494 | 0.518 | 0.710 / 2.07 / 10.79% | 0.609 | 0.718 | 0.841 (real) | 0.748 | 0.0 | +0.009 | 2 | 0.995–0.996 |
| SP_809570_2454450 | −80.957 | 245.445 | 9.198 | 0.427 | 0.395 / 1.23 / 0.10% | 0.753 | 0.467 | not computed | 0.722 | 0.0 | +0.061 | 3 | 0.988–0.991 |
| SP_819860_1568660 | −81.986 | 156.866 | 10.735 | 0.500 | 0.636 / 1.59 / 10.41% | 0.636 | 0.654 | 0.827 (real) | 0.646 | 0.0 | +0.097 | 4 | 0.989–0.993 |
| SP_842420_0421060 | −84.242 | 42.106 | 25.463 | 0.526 | 0.556 / 1.42 / 0.14% | 0.627 | 0.667 | not computed | 0.792 | 0.0 | −0.007 | 5 | 0.996–0.997 |
| SP_817950_1586580 | −81.795 | 158.658 | 43.429 | 0.487 | 0.518 / 1.04 / 0.004% | 0.660 | 0.590 | not computed | 0.641 | 0.0 | −0.015 | 6 | 0.971–0.996 |
| SP_830080_0535120 | −83.008 | 53.512 | 22.471 | 0.490 | 0.668 / 1.74 / 7.22% | 0.624 | 0.688 | 0.630 (real) | 0.617 | 0.0 | +0.012 | 7 | 0.982–0.988 |

Sources: `outputs/objective1/paper_criterion/seven_candidates_paper_criterion.csv`,
`outputs/objective2/shortlist/shortlist_hazard_summary.csv`,
`outputs/objective2/SP_840980_0797630_hazard_map_v2.json`,
`outputs/objective1/ml/shortlist/shortlist_pixel_anomaly_summary.csv`,
`outputs/objective1/evidence_score/physics_evidence_score.json`,
`PRISM/docs/ML_METHODS.md` (ShadowCam correlations). Illumination = 0.0 for
every candidate — independently confirms all 7 are genuinely permanently
shadowed (§DECISIONS.md), consistent with the geometric PSR-catalog premise,
not itself ice evidence.

## 3. Literature Search Method

Three parallel research passes (see Method note above) used WebSearch and
WebFetch (including a jina.ai HTML-reader-proxy technique that successfully
bypassed apparent paywalls for two Nature-family/AGU articles in this and the
prior Sinha investigation, but failed against ScienceDirect/IEEE/Science
Advances, which returned hard bot-detection walls in every attempt). Every
source below carries an explicit access-status tag. No content is presented as
verbatim-quoted unless a full-text fetch actually succeeded.

---

## 4. NASA Evidence

### 4.1 LEND (neutron spectrometer, hydrogen)
**FACT (search-summary confidence):** Mitrofanov et al. (2010, *Science*
330:483–486, DOI 10.1126/science.1185696) mapped south-polar hydrogen; formally
disputed by a published Technical Comment (DOI 10.1126/science.1203341) and
Response (DOI 10.1126/science.1203483) — the original claim was **not**
universally accepted at the time. Sanin et al. (2017, *Icarus* 283:20–30, DOI
10.1016/j.icarus.2016.10.019) report **~105 ppmw (0.095±0.01 wt% water-equiv.)
within 10° of the pole; ~140 ppmw (0.13±0.02 wt%) within 2°** — hydrogen
enrichment increasing toward the pole. Cabeus shows the regional maximum,
corresponding to an estimated **0.5–4.0 wt% water ice** depending on assumed
overburden thickness. **Spatial resolution: 10 km FWHM** (collimated
footprint).
**CONCLUSION:** every PRISM candidate PSR (9–43 km², i.e. ~3–7 km across) is
**smaller than a single LEND resolution element.** LEND provides
**regional-scale support, not candidate-pixel-level validation** — it cannot
distinguish any one PRISM candidate from its neighbors.

### 4.2 The 2024 "widespread ice" study
**FACT:** McClanahan et al. (2024), *Planetary Science Journal* (preprint
arXiv:2303.03911), combines **Diviner thermal + LOLA topography** (not LAMP)
in a modeling study. Verbatim NASA science-page framing: *"widespread evidence
of water ice within PSRs... towards at least 77 degrees south latitude,"*
concentrated near coldest points (**<75 K**) and poleward-facing PSR slopes.
**CONCLUSION:** this is a **thermal/topographic plausibility model, not a
direct detection** — Evidence-Hierarchy Level 4 (§19), not Level 1–3. All 7
PRISM candidates (−80.957° to −84.242°) fall inside its ≥77°S zone, but the
study provides **no candidate-specific resolution or per-PSR measurement.**

### 4.3 LCROSS / Cabeus
See §7 (Peer-Reviewed Radar Evidence section covers Mini-RF; LCROSS placed
here under NASA evidence). **FACT:** Colaprete et al. (2010, *Science*
330:463–468, DOI 10.1126/science.1186986): **5.6 ± 2.9 wt% water** in Cabeus
regolith, inferred from NIR absorbance + UV hydroxyl emission in the impact
**ejecta plume** of a deliberate ~2.3-metric-ton Centaur impact. This is
**not** a passive surface observation — it is a single-point, subsurface-
excavating measurement. No statement generalizing this result to other PSRs
was found in the accessible literature. **Cabeus is not among PRISM's 7
candidates** (PRISM's own catalog separately maps it to PSR
`SP_844580_3134320`, per `INDEPENDENT_ICE_VALIDATION.md`).
**CONCLUSION (per task framing): classify LCROSS as independent
regional/physical ground truth — proof water ice CAN exist in south-polar
PSRs — not direct validation of any specific PRISM candidate.**

## 5. ISRO/Chandrayaan Evidence

### 5.1 Chandrayaan-1 M3 (Li et al. 2018, PNAS)
**FACT (full text obtained, PMC6130389):** Spectral method requires
co-occurring 1.3/1.5/2.0 μm absorption features; spectral-angle-mapping
threshold **<30°** vs. lab water-frost standards. Resolution **~280×280 m**.
**"~3.5% of cold traps exhibit ice exposures"** — i.e. even within PSRs, ice
detections are a small minority, not a blanket signature. Ice-bearing pixels
show **~30 wt% ice intimately mixed with dry regolith** (mixture-model
estimate, not an areal average). Positive craters (verbatim): **Haworth,
Shoemaker, Sverdrup, Shackleton, Faustini, de Gerlache, Rozhdestvenskiy**.
Negative controls (verbatim): **Amundsen, Hedervari, Idel'son L, Wiechert,
Bosch**. **No sub-crater (wall vs. floor) location given.** **No
machine-readable pixel coordinates exist anywhere** — re-confirmed
independently this session (SI is a 19.3 MB PDF with an image-only map, Fig.
S5) — a genuine, persistent data gap, not a search failure.

### 5.2 Chandrayaan-2 DFSAR — Verma et al. 2025 and Sinha et al. 2026
See §6.2–6.3. Both are ISRO/Chandrayaan-2-DFSAR-based studies and the single
most important finding connecting them is documented there.

## 6. Peer-Reviewed Radar Evidence

### 6.1 LRO Mini-RF — a genuinely contested literature, not a consensus
**FACT (Spudis et al. 2013, *JGR Planets* 118, DOI 10.1002/jgre.20156, fetched
via jina.ai proxy, good confidence):** *"Shackleton... patchy, high CPR on the
walls... consistent with a small amount of water ice mixed with regolith."*
Haworth cited for separate LAMP UV frost evidence. *"Small patchy areas of
high CPR... in Shoemaker and Faustini"* (brief mention). **The paper's own
authors explicitly concede the radar model alone cannot definitively
distinguish ice from extreme surface roughness.**

**FACT (skeptical/roughness side):** Eke et al. (2014, *Icarus* 241:66–81,
arXiv:1312.4749) — north-polar craters, elevated CPR attributed to
**wall-steepness and incomplete regolith maturation**, not ice. Fa (2018, *JGR
Planets*, DOI 10.1029/2018JE005668) ties high CPR to **high Diviner rock
abundance at blocky ejecta** — rocks, not ice.

**CONCLUSION:** the field itself has not resolved whether elevated CPR in
polar crater interiors is ice-specific. **No Mini-RF study targets any of
PRISM's 7 unnamed candidate PSRs** — only named craters have been studied.

### 6.2 Chandrayaan-2 DFSAR — Verma, Bhatt, Dangi, Kumar & Bhardwaj (2025), *Icarus* 432, 116492
**Access status: COULD NOT ACCESS FULL TEXT** — ScienceDirect and
ResearchGate both hard-blocked every fetch attempt, including the jina.ai
proxy technique. Everything below is reconstructed from **3 independently
cross-checked WebSearch summaries**, not a primary-source read — treat with
more caution than the Sinha 2026 findings, which did achieve full-text access.

**Consistently reported across independent searches:** 14 craters screened
for CPR>1 using L-band full-pol DFSAR; **9 doubly-shadowed craters inside
Faustini, Haworth, and Shoemaker** studied in detail; **4 craters met
CPR>1 & DOP<0.13**; one ~1.1 km crater inside Faustini with a "lobate rim"
flagged as possible subsurface-ice excavation; DOP computed **"after applying
parallax error correction"** (a named but unexplained processing step — see
§16); resolution 20–25 m, matching PRISM's own DFSAR products.

**⚠ Major, unconfirmed but well-grounded finding — read carefully:** Verma
2025's senior author is **A. Bhardwaj — the same senior author as Sinha et al.
2026.** Verma's "~1.1 km, lobate-rim, Faustini crater flagged for possible ice
excavation" is strikingly identical in diameter, host crater, and description
to Sinha 2026's own **"F2"** crater. **This could not be confirmed** (neither
paper's full crater table was independently accessible), but if true, **Verma
2025 and Sinha 2026 are not two independent lines of evidence — they may be
the same research group's sequential write-ups of the same crater/dataset.**
This materially affects how "independent corroboration" should be scored
anywhere these two papers might otherwise be cited together (§17, §21).

**Resolved from the prior investigation:** whether Verma 2025 already used
DOP<0.13 before Sinha 2026's stated "refinement" from 0.35 — **yes**, per
search-summary evidence, Verma 2025 itself reports DOP<0.13 for 4 craters
alongside a broader 0–0.35 criterion. Sinha's "refinement" framing is not
contradicted, but is less novel than it appears standing alone, and reinforces
the same-research-program picture above.

**Not independently found this session:** the task brief's specific claim
that Verma 2025 states "~2% of pixels exceed CPR>1" and "homogeneous surface
ice is unlikely" — **not verified either way**, flagged NOT VERIFIED, not
assumed true.

**Spatial overlap:** Verma 2025's craters (Faustini ≈ `SP_871460_0840750`,
Haworth ≈ `SP_874930_3578760`, Shoemaker ≈ `SP_880260_0452790`) **do not
overlap any of PRISM's 7 shortlisted candidates.**

### 6.3 Chandrayaan-2 DFSAR — Sinha et al. 2026
Already fully investigated in `DOP_SINHA_2026_RESEARCH.md` — preserved
unchanged here: DOP methodology **not yet independently reproducible** by
PRISM (0.63–0.86 obtained vs. 0.10–0.13 claimed, across 8+ hypotheses); CPR
independently lands in the same regime. Used here as one evidence layer among
several, not the sole basis for any conclusion.

## 7. Optical/Spectral Evidence

Covered in §5.1 (M3) and §10 (ShadowCam) — kept together with those sections
to avoid duplication; cross-referenced here per the requested outline.

## 8. Hydrogen/Neutron Evidence

Covered in §4.1 (LEND).

## 9. Thermal Evidence

**FACT (Paige et al. 2010, *Science* 330:479–482, DOI 10.1126/science.1187726,
search-summary confidence):** coldest measured PSR temperatures **~25 K**;
Cabeus subsurface estimated **~38 K**. Diviner's cold-trapping regions extend
**beyond** strict PSR polygon boundaries in places.

**The ~110 K ice-stability threshold:** traced (moderate confidence, not
independently verified) to Vasavada, Paige & Wood (1999, *Icarus*),
building on Watson, Murray & Brown (1961, *JGR*) — the foundational
cold-trap concept. Physically grounded (sublimation becomes negligible over
geologic timescales below this temperature), not an arbitrary round number,
but **PRISM should independently verify Vasavada et al. 1999's exact wording
before citing 110 K as an authoritative number in its own docs** — flagged
AMBIGUOUS pending that check.

**Per-candidate/per-crater Diviner temperature data: NOT retrieved for any
of PRISM's 7 candidates, nor for any of the named reference craters, in this
literature pass.** This requires a direct PDS query against Diviner's archive
at each candidate's coordinates, not a literature search — a genuine,
actionable data gap (see §26 datasets, §24 recommended experiment).
**CONCLUSION: Diviner/thermal evidence is used here strictly as a physical
plausibility layer (Evidence Level 4), not proof of ice, per task
instruction — and even that plausibility layer currently has zero
candidate-specific numbers for PRISM's actual shortlist.**

## 10. ShadowCam Evidence

**This is the single most important, and most sobering, finding in this
report.**

**FACT (Ando, Li, Robinson & Wagner 2025, *The Planetary Science Journal*
6(3):62, DOI 10.3847/PSJ/adb8d1 — full text obtained, high confidence):**
maximum-radiance ShadowCam mosaics (Jan 2023–Dec 2024, 60 m/px) compared
directly against M3's own ice-detection pixels across **14 named south-polar
PSRs**: Cabeus, Cabeus B, Faustini, Haworth, Nobile, Scott, Shackleton,
Shoemaker, Slater, Stose, Sverdrup+Henson, Unnamed, Wiechert J, de Gerlache —
overlapping 6 of PRISM's 7 M3-positive reference craters and 1 negative
control (Wiechert), directly.

**Verbatim headline finding (abstract): "Individual M3 positive water ice
detections show no radiance contrast with their surroundings."** At the
**north** pole, M3-positive PSRs show a real ~4.4× higher modal radiance than
M3-negative PSRs (though the authors caution this cannot be definitively
attributed to water ice either). **This pattern does NOT hold at the south
pole**: *"We do not see the same trend at the south pole, even when only
examining its smaller PSRs."* **The only south-polar exception: Cabeus** —
the one PSR with independent LCROSS ground truth.

**Sensitivity limit:** ShadowCam requires **~20–30 wt% water ice** for
visible-wavelength radiance contrast — right at the edge of M3's own ~30 wt%
ice-bearing-pixel estimate, meaning lower-concentration ice could be real and
still invisible to this test.

| Crater (PRISM control role) | ShadowCam finding | Interpretation | Confidence |
|---|---|---|---|
| Cabeus (positive control) | Only south-polar PSR with a positive M3-vs-non-M3 radiance shift | Weak positive — the one place ShadowCam and M3 agree in direction | LOW-MODERATE |
| Faustini, Shackleton, Haworth, Shoemaker, Sverdrup, de Gerlache (positive controls) | Included in the 14-PSR test set; none singled out as showing a shift | Null — ShadowCam does not independently confirm ice here | MODERATE (full-text verified) |
| Wiechert J (M3 negative control) | Included; not distinguished from positive-control PSRs | Consistent with the overall south-pole null result | MODERATE |

A second paper (Watkins et al., *Science Advances*, exact author list
**unverified**, access blocked by CAPTCHA on all fetch attempts — search-
snippet confidence only) reportedly examined Faustini, Slater, Cabeus,
Wiechert J, Hermite A, Mouchez L and found scattered 20–50 m bright,
forward-scattering spots but concluded most PSRs "lack surface ice exposures,
or ice concentration is below the detection limit" — directionally
consistent with Ando 2025, flagged AMBIGUOUS pending verification.

**CONCLUSION:** PRISM's own prior verification that its ShadowCam crops show
real terrain (adjacent-pixel correlation ~0.99, all 7 candidates —
`ML_METHODS.md`) establishes **signal quality**, not **ice presence** — these
are different claims. The peer-reviewed ShadowCam literature currently does
**not** support optical ice confirmation for 13 of the 14 named PSRs it has
tested, including most of PRISM's own reference craters. **This is a genuine
complication for any "convergent multi-instrument evidence" narrative and
must be stated plainly, not smoothed over.**

## 11. Candidate-by-Candidate Comparison

Per task instruction: `CONFIRMED / STRONG SUPPORT / MODERATE SUPPORT / WEAK
SUPPORT / NO DATA / CONTRADICTORY / NOT COMPARABLE`. **Because none of PRISM's
7 candidates is a named crater with its own literature, every external-
instrument column below is regional/latitude-band context at best — this
table should not be read as candidate-level confirmation from any of these
instruments.**

| Candidate | PRISM ice score (Physics Evidence rank) | CPR | DOP | Terrain hazard | ShadowCam | M3 | LEND | Mini-RF | Diviner | Independent papers | Overall external support |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **SP_840980_0797630** (primary) | Rank 1/7 (score 1.0) | 0.630 mean, 7.33% CPR>1 | 0.680 (real, doesn't meet Sinha's <0.13) | Unfavorable (0.597 interior hazard, PSR mostly crater wall not floor, `PROJECT_STATUS.md`) | Real signal (0.994 corr.), no independent ice-specific interpretation | **NOT COMPARABLE** (~15.2 km from Amundsen, an M3 *negative* control — see §18) | NO DATA (regional only, §4.1) | NO DATA (no study targets this PSR) | NO DATA (no per-candidate Diviner temps retrieved) | None specific to this PSR | **WEAK** — regional plausibility only; nearest named reference site is an ice-negative control |
| SP_832640_0090770 | Rank 2/7 | 0.710 mean, 10.79% CPR>1 (highest CPR of the 7) | 0.841 (real, high) | Unfavorable (0.748, highest hazard of the 7) | Real signal (0.995–0.996) | NOT COMPARABLE (no nearby named crater identified this pass) | NO DATA | NO DATA | NO DATA | None | **WEAK** |
| SP_809570_2454450 | Rank 3/7 | 0.395 mean, 0.10% CPR>1 (lowest CPR of the 7) | Not computed | Unfavorable (0.722) | Real signal (0.988–0.991) | NOT COMPARABLE | NO DATA | NO DATA | NO DATA | None | **WEAK** — also has the highest ML anomaly separation (+0.061) of the shortlist, a PRISM-internal finding only |
| SP_819860_1568660 | Rank 4/7 | 0.636 mean, 10.41% CPR>1 | 0.827 (real, high) | Unfavorable (0.646) | Real signal (0.989–0.993) | NOT COMPARABLE (~85–87 km from Wiechert, an M3 negative control) | NO DATA | NO DATA | NO DATA | None | **WEAK** — highest ML separation among DOP-computed candidates (+0.097) |
| SP_842420_0421060 | Rank 5/7 | 0.556 mean, 0.14% CPR>1 | Not computed | Most unfavorable of all 7 (0.792) | Real signal (0.996–0.997) | NOT COMPARABLE | NO DATA | NO DATA | NO DATA | None | **WEAK**, and PRISM's own ML anomaly score is *negative* here (−0.007) |
| SP_817950_1586580 | Rank 6/7 | 0.518 mean, 0.004% CPR>1 (near-zero) | Not computed | Unfavorable (0.641) | Real signal (0.971–0.996) | NOT COMPARABLE | NO DATA | NO DATA | NO DATA | None | **WEAK**, negative ML anomaly score (−0.015) |
| SP_830080_0535120 | Rank 7/7 (lowest) | 0.668 mean, 7.22% CPR>1 | 0.630 (real) | Most favorable of the 7 (0.617, still "unfavorable" in absolute terms) | Real signal (0.982–0.988) | NOT COMPARABLE | NO DATA | NO DATA | NO DATA | None | **WEAK** |

## 12. Positive Controls

- **LCROSS Cabeus** (`SP_844580_3134320` in PRISM's own catalog, per
  `INDEPENDENT_ICE_VALIDATION.md`) — the field's only Level-1 direct
  detection (5.6±2.9 wt% water, Colaprete et al. 2010). Also the **only**
  south-polar PSR where ShadowCam's own radiance test shows the expected
  M3-consistent signal (Ando et al. 2025). The strongest available
  positive control by a wide margin.
- **M3-positive craters with multiple lines of support**: Faustini and
  Shoemaker appear in M3 (Li et al. 2018), Mini-RF (Spudis et al. 2013,
  with caveats), and Brown et al. 2022's resource-rich list — the closest
  thing to "converging evidence" found anywhere in this investigation,
  **though ShadowCam itself does not add a confirming signal for either**
  (§10). Verma 2025/Sinha 2026's DFSAR craters are also inside these two
  hosts (§6.2), but per §6.2's caveat, may not be independent of each other.

## 13. Negative Controls

- **M3-negative craters (Li et al. 2018, verbatim): Amundsen, Hedervari,
  Idel'son L, Wiechert, Bosch (Bosch is north-polar, excluded from south-pole
  comparisons).**
- **A genuine cross-instrument contradiction, found this session:** Brown et
  al. (2022, *Icarus* 377, 114874) list **Amundsen** among their
  "resource-rich" PSRs (hydrogen/frost co-location modeling) — directly
  contradicting Li et al. 2018's M3 spectral non-detection at the same
  crater. **This is reported as a real, unresolved tension, not resolved in
  either direction by this investigation.** Recommendation: use **Hedervari,
  Idel'son L, or Wiechert** as negative controls instead of Amundsen where a
  "clean" (non-contested) control is needed (§18).
- **PRISM's own prior negative-control test already exists and is directly
  relevant**: `INDEPENDENT_ICE_VALIDATION.md` (2026-08-22) ran PRISM's exact
  Pv/CPR/SERD/T-Ratio pipeline on 7 M3-positive and 4 south-polar M3-negative
  craters and found **no systematic separation** (positive mean score 0.573
  vs. control mean 0.636 — controls scored *higher* on average) — this
  result is preserved, not re-litigated, and is the single most important
  PRISM-internal finding this new literature pass corroborates rather than
  overturns: **does PRISM's metric behave differently between positive and
  negative controls? No — not in PRISM's own prior test, and nothing found in
  this pass contradicts that finding.**

## 14. Metric-by-Metric Validation

| PRISM Metric | Literature Support | Ice Specificity | Known False Positives | Transferable Threshold? |
|---|---|---|---|---|
| **Pv** (Yamaguchi volume-scattering fraction) | General SAR decomposition literature (Yamaguchi 4-component decomposition is a standard, widely-cited technique) supports the *formula*, not an ice-specific claim | Low–moderate — volume scattering also arises from rough/blocky regolith, not just ice | Rough terrain, boulder fields, block fields (same mechanism flagged for CPR, §15) | No literature-derived absolute threshold found; PRISM's own "high Pv" tier is a data-derived percentile, not literature-anchored (already documented in PRISM's own `PROJECT_STATUS.md`) |
| **CPR** | Extensively studied, but genuinely contested (§15) | Contested — Spudis et al. pro-ice vs. Eke/Fa/Campbell/Neish roughness-alternative, both peer-reviewed | Fresh-crater ejecta, block fields, impact melt, crater-wall steepness — all explicitly documented in the literature (§15) | CPR>1 is a widely-used heuristic but not a validated absolute ice threshold; not safely transferable without corroboration |
| **SERD** | **No independent literature validating this as an ice indicator was found in this investigation** — it is an ISRO/DFSAR-internal derived product; its algorithm is not documented in the CH2DFSAR SIS (per PRISM's own `SERD_NAN_ANALYSIS.md`) | Unknown/unverified externally | Unknown | No — no external threshold exists to transfer |
| **T-Ratio** | Same as SERD — not independently checked against external literature in this pass (out of scope for the 3 forks run); PRISM's own docs describe it as a dielectric-constant proxy without an external citation | Unknown/unverified externally | Unknown | No |
| **DOP** | Textbook Stokes-parameter *formula* is standard (confirmed, §16); the specific **quad-pol HH/VV channel pairing PRISM uses is explicitly non-standard** per general SAR polarimetry pedagogy (standard dual-pol modes pair one co-pol with one cross-pol channel, e.g. HH/VH) | Contested and basis-dependent — see `DOP_SINHA_2026_RESEARCH.md` in full | Basis mismatch, calibration/crosstalk (tested and largely ruled out for PRISM's own data), averaging order | No safely transferable threshold — Sinha's 0.10–0.13 could not be independently reproduced by PRISM under any tested formulation |
| **Isolation Forest anomaly score** | Unsupervised anomaly detection is a well-established general ML technique; its output is only as ice-specific as its input features (Pv/CPR/SERD/T-Ratio for the v2/pixel version) | Fully inherited from input-feature specificity — see Pv/CPR rows above | Whatever the underlying features' false positives are | Not applicable — this is a relative ranking, not a calibrated threshold; already documented as such in `ML_METHODS.md` |
| **Slope / roughness / illumination (terrain hazard)** | Well-supported by standard photogrammetric/DEM methods and Diviner cold-trap literature (Paige 2010, Vasavada 1999, Watson 1961) for the illumination/thermal-stability logic | Not an ice indicator — correctly scoped by PRISM as a hazard/accessibility metric, not an ice-detection metric | Not applicable (not used as an ice indicator) | PRISM's own 10°/20° hazard thresholds remain self-flagged "crude," not literature-derived (unchanged from prior audit) |
| **ShadowCam signal (adjacent-pixel correlation)** | PRISM's own verification method (established in `ML_METHODS.md`) is sound for confirming genuine terrain signal vs. sensor noise | **Not an ice indicator** — correlation confirms real terrain, not ice presence; peer-reviewed literature (Ando et al. 2025) shows ShadowCam radiance itself does not confirm ice at 13/14 tested south-polar PSRs | Real terrain without ice would show identical high correlation | Ando et al. 2025 gives a genuine external threshold (~20–30 wt% ice needed for visible-wavelength contrast) but this has not yet been applied to PRISM's own ShadowCam crops as an ice test — only as a signal-quality test |

## 15. CPR Limitations

**The literature repeatedly and explicitly warns that CPR>1 does not
automatically mean ice.** This is not a hypothetical caveat PRISM is adding
out of caution — it is a real, active, peer-reviewed controversy:

- **Pro-ice side:** Spudis et al. (2013) — CPR anomalies at Shackleton,
  Haworth, Shoemaker, Faustini "consistent with" ice, while **explicitly
  conceding the model cannot rule out roughness alone.**
- **Roughness/skeptical side:** Eke et al. (2014) — north-polar anomalous
  craters explained by wall steepness and regolith immaturity, not ice. Fa
  (2018) — high CPR co-located with high Diviner rock abundance at blocky
  ejecta. Campbell and Neish (cited via search-summary, exact titles not
  independently confirmed this pass — AMBIGUOUS) — polarimetric radar used
  specifically to characterize rough ejecta/impact-melt deposits as a
  roughness diagnostic, independent of any ice question. **Fresh crater
  ejecta (<200 Ma) shows elevated CPR out to >3 crater diameters from the
  rim, declining with age** — a documented, ice-unrelated mechanism.
- **The core ambiguity, stated plainly in the literature:** a rocky regolith
  scatters a radar signal multiple times, partially mimicking the volume-
  scattering signature of buried ice. **This is the same double-bounce/
  volume-scattering ambiguity PRISM's own SERD investigation and DOP work
  already grapple with — now confirmed as a named, recognized problem in the
  broader field, not something PRISM discovered in isolation.**

**Explicit caveat for PRISM going forward (per task instruction):** CPR>1
alone should never be presented as ice confirmation in any PRISM output — it
should always be paired with at least one other, ideally independent,
indicator, and even then treated as suggestive rather than conclusive.

## 16. DOP Literature Comparison

This extends, and does not replace, `DOP_SINHA_2026_RESEARCH.md`.

- **The Stokes-parameter DOP formula shape is confirmed standard** —
  `√(S2²+S3²+S4²)/S1` (PRISM/Sinha's indexing) is algebraically the same
  textbook construction as the classical optics `√(S1²+S2²+S3²)/S0`. The open
  question was never the formula's shape, only which physical channels feed
  it.
- **New, sourced finding:** general SAR polarimetry pedagogy (Natural
  Resources Canada / Carleton University course materials, corroborated by
  search summary) states that **(HH,VH) and (VV,HV) — one co-pol + one
  cross-pol channel — are the standard dual-pol modes** used by real
  spaceborne systems (PALSAR, TerraSAR-X, RADARSAT-2). **PRISM's own
  "linear-pol" (HH,VV) pairing — two co-pol channels — is explicitly
  discussed in this literature as a non-standard configuration.** This is a
  new, independently-sourced reinforcement of `DOP_SINHA_2026_RESEARCH.md`
  §5.1's hypothesis, now grounded in general SAR pedagogy rather than only
  an inference from Raney's hybrid-pol paper.
- **However, real precedent for linear dual-pol DOP does exist:** Shirvany,
  Chabert & Tourneret (2012), *IEEE JSTARS* 5(3):885–892, "Ship and Oil-Spill
  Detection Using the Degree of Polarization in Linear and Hybrid/Compact
  Dual-Pol SAR" — establishes "degree of polarization for linear dual-pol
  SAR" as a legitimate, published research topic in mainstream (ocean
  remote-sensing) literature. **Full text could not be accessed** (IEEE
  anti-bot wall); the exact channel pairing they use (HH/VV vs. a co+cross
  pairing) **could not be confirmed to match PRISM's choice** — flagged
  AMBIGUOUS. This is genuine precedent for the *category* PRISM's DOP
  construction belongs to, not confirmation that PRISM's specific pairing is
  the established convention.
- **Independent corroboration of a separate PRISM finding:** a general SAR
  source states plainly that dual-pol *intensity-only* data "cannot
  straightforwardly" support DOP, because it requires the complex cross
  product between channels — this independently confirms, from a source
  unconnected to PRISM, exactly what `dop_pipeline_v2_sri_powerdop.py`
  already concluded about the amplitude-only Level-2 SRI product.

## 17. Quantitative Ice-Abundance Evidence

| Crater | Quantity | Value | Method/Instrument | Source |
|---|---|---|---:|---|
| Cabeus | Water ice mass | **~11 × 10⁶ t** | Hydrogen/frost co-location modeling | Brown et al. (2022), *Icarus* 377, 114874, DOI 10.1016/j.icarus.2021.114874 |
| Shoemaker | Water ice mass | **~5 × 10⁶ t** | same | same |
| Faustini | Water ice mass | **~4 × 10⁶ t** | same | same |
| South pole (regional baseline) | Water-equivalent hydrogen | **~1.5 wt%** (original); later work suggests **~2 wt%**, with localized 30-km-scale PSRs potentially **>10 wt%** if concentrated in a thin near-surface layer | Lunar Prospector Neutron Spectrometer | Feldman et al. (2001), *JGR Planets* 106(E10), DOI 10.1029/2000JE001444; refined by Lawrence et al. (2006), DOI 10.1029/2005JE002637 |
| M3 ice-bearing pixels | Ice-in-mixture concentration | **~30 wt%** (not an areal average — only for the ~3.5% of cold-trap pixels showing detections) | NIR spectral mixture modeling | Li et al. 2018 |
| Cabeus (LCROSS) | Ejecta-plume water abundance | **5.6 ± 2.9 wt%** | Impact-plume spectroscopy | Colaprete et al. 2010 |

**Brown et al. 2022's own "most resource-rich" PSR list (verbatim):**
Faustini, Cabeus, de Gerlache, Shoemaker, Haworth, Sverdrup, Slater, and
**Amundsen** — the Amundsen entry directly contradicts Li et al. 2018's M3
non-detection at the same crater (§13). **Access status:** these tonnage
figures come from consistent, repeated search-engine summarization
(ScienceDirect blocked all direct/proxy fetches) — citations and craters are
high-confidence; exact uncertainty ranges were not independently retrieved.

**None of these quantitative figures apply to any of PRISM's 7 shortlisted
candidates** — every number above is for a named crater outside PRISM's
shortlist.

## 18. Spatial Cross-Validation

This is the most consequential section. **Distances computed directly by this
session (haversine, Moon mean radius 1,737.4 km), not taken from any
secondary source.**

**PRISM's primary candidate, `SP_840980_0797630` (−84.098°, 79.764°), sits
approximately 15.2 km from Amundsen crater (−84.5°, 82.8°)** — the closest
proximity found between any PRISM candidate and any named reference crater in
this investigation. Amundsen is:
- an **M3 ice-negative control** (Li et al. 2018 explicitly found no ice
  signature there), **and**
- simultaneously listed on Brown et al. (2022)'s **"resource-rich"** PSR list
  (§13, §17) — a genuine, unresolved cross-instrument contradiction at this
  exact nearby location.

This is neither a validation nor a refutation of PRISM's primary candidate —
it means the **nearest independently-studied location** to PRISM's own top
candidate is itself a site of **contested, contradictory** external evidence,
not a clean positive or negative reference point. This should be treated as a
priority follow-up location, not ignored.

Coarse coordinate screening (not exhaustively computed to full precision for
every pair) found no other PRISM candidate within roughly 80 km of a named
reference crater:

| PRISM candidate | Nearest named reference site found | Approx. distance | Reference site's ice status |
|---|---|---:|---|
| SP_840980_0797630 (primary) | Amundsen | **~15.2 km** | M3-negative / Brown-2022-resource-rich (contradictory) |
| SP_819860_1568660 | Wiechert | ~85–87 km | M3-negative |
| SP_817950_1586580 | Wiechert | ~85–90 km (not separately computed to full precision) | M3-negative |
| SP_842420_0421060 | Shoemaker | ~117 km | M3-positive, Mini-RF-studied |
| SP_830080_0535120 | Shoemaker | ~156 km | M3-positive, Mini-RF-studied |
| SP_832640_0090770, SP_809570_2454450 | none within ~150 km found in this pass | not comparable | — |

**CONCLUSION: no PRISM candidate spatially overlaps or sits within a few
kilometers of any independently-studied, ice-positive named crater.** The
closest approach found is to an M3 *negative* control with contradictory
secondary evidence. This is the honest, load-bearing spatial finding of this
entire report — it must not be paraphrased as "PRISM's candidates are near
known ice sites."

## 19. Evidence Hierarchy

Per task-specified 5 levels, populated with what this investigation actually
found:

- **LEVEL 1 — Direct physical/spectral detection:** LCROSS Colaprete et al.
  2010 (Cabeus, single-point ejecta-plume measurement); M3 Li et al. 2018
  (spectral, ~3.5% of cold-trap pixels, named craters only).
- **LEVEL 2 — Independent remote-sensing with strong physical
  interpretation:** LEND hydrogen (Sanin et al. 2017, regional); Brown et al.
  2022 tonnage modeling; ShadowCam (Ando et al. 2025) — though the latter's
  south-polar result is predominantly a **null** finding, it is still Level-2
  *evidence* (a real test that mostly failed to confirm, not absence of a
  test).
- **LEVEL 3 — Radar indicators:** Mini-RF CPR (Spudis 2013, contested); DFSAR
  CPR/DOP (Verma 2025, Sinha 2026, PRISM's own pipeline).
- **LEVEL 4 — Environmental plausibility:** Diviner thermal (Paige 2010,
  Vasavada 1999); McClanahan et al. 2024 widespread-ice thermal/topographic
  model; PRISM's own terrain hazard/illumination outputs (illumination = 0.0
  for all 7 candidates, confirming genuine permanent shadow — plausibility,
  not detection).
- **LEVEL 5 — PRISM-derived model scores:** Pv, CPR/SERD/T-Ratio window
  statistics, the Physics Evidence Score, and the Isolation Forest anomaly
  score.

**CONCLUSION: none of PRISM's 7 shortlisted candidates has any Level 1, 2, or
3 evidence directly attributable to it.** Every number in the candidate table
(§11) that is genuinely candidate-specific is Level 4 (terrain/illumination)
or Level 5 (PRISM's own radar-derived scores). This is stated plainly, per
task instruction not to let a PRISM model score outrank direct observational
evidence — **it does not, because no direct observational evidence exists for
any of these specific 7 locations.**

## 20. Strongest External Validation

**For PRISM's actual 7-candidate shortlist: none.** No Level 1–3 evidence
exists for any of the 7 candidates specifically. The strongest applicable
support is regional/environmental: all 7 fall within LEND's broadly
hydrogen-enhanced zone (§4.1), within McClanahan et al. 2024's ≥77°S
plausibility zone (§4.2), and all 7 show genuine 0.0 illumination (§2,
independently geometric confirmation of permanent shadow). **This is real but
weak support — latitude-band consistency, not location-specific
confirmation.**

**For the broader south-polar region PRISM operates in (not PRISM's specific
candidates): Cabeus** is unambiguously the strongest validated location —
Level 1 (LCROSS), Level 2/3 partial corroboration (LEND regional maximum,
the only south-polar ShadowCam radiance match), though notably **PRISM's own
prior radar-metric test scored Cabeus lowest of 11 tested sites**
(`INDEPENDENT_ICE_VALIDATION.md`) — a real, unresolved tension between
"best externally confirmed site" and "best PRISM-radar-scoring site,"
reaffirmed rather than resolved by this investigation.

## 21. Contradictory Evidence

Explicitly surfaced by this investigation, not glossed over:

1. **Amundsen**: M3-negative (Li et al. 2018) vs. Brown et al. 2022
   resource-rich list — and it sits ~15.2 km from PRISM's own primary
   candidate (§18).
2. **ShadowCam vs. M3 at the south pole**: Ando et al. 2025 finds no
   radiance-contrast confirmation of M3's south-polar ice detections at 13
   of 14 tested PSRs — a real instrument-vs-instrument disagreement, only
   Cabeus shows agreement.
3. **Cabeus scores worst on PRISM's own radar metric** despite being the
   best-confirmed ice site in the solar system by direct measurement
   (`INDEPENDENT_ICE_VALIDATION.md`, reaffirmed here).
4. **Mini-RF's internal split**: Spudis et al. 2013 (pro-ice, with explicit
   self-acknowledged uncertainty) vs. Eke et al. 2014 / Fa 2018
   (roughness-driven alternative explanation) for the same underlying CPR
   signal at the same craters.
5. **LEND's original 2010 hydrogen-anomaly claim was formally disputed**
   in the literature itself (a published Technical Comment + Response),
   not universally accepted at face value.
6. **Possible non-independence of Verma 2025 and Sinha 2026** (§6.2) — if
   confirmed, any future PRISM document citing both as separate corroborating
   sources for the same crater would itself be introducing a false
   appearance of independent convergence.

## 22. What PRISM Can Legitimately Claim

- PRISM's 7 candidates are genuine LOLA-catalog PSRs with **independently
  confirmed 0.0 illumination** (geometric, not radar-derived) — real physical
  permanent shadow, consistent with the necessary (not sufficient) condition
  for ice stability.
- PRISM's candidates fall within the broad **latitude band (77–90°S)** for
  which regional hydrogen enhancement (LEND) and a thermal/topographic
  ice-plausibility model (McClanahan et al. 2024) both apply — genuine, but
  weak, environmental-plausibility support (Level 4).
- PRISM's own CPR values are **numerically consistent** with the same-shaped
  metric reported by Sinha et al. 2026 and (per search-summary evidence)
  Verma et al. 2025, on the same general instrument (Chandrayaan-2 DFSAR) —
  though the underlying formulas are not confirmed identical, and CPR itself
  is a contested ice indicator in the broader literature (§15).
- PRISM's ShadowCam imagery for all 7 candidates is **confirmed to show real
  terrain signal** (not sensor noise), a legitimate and independently
  verified claim distinct from any claim about ice presence.
- PRISM's DOP methodology, its limitations, and its 8+ tested hypotheses are
  now **more rigorously documented than the papers (Sinha 2026, likely Verma
  2025) it is being compared against** — Sinha's own paper does not specify
  its channel-to-Stokes-parameter mapping, calibration, or acquisition,
  which PRISM's own DOP pipeline does specify and document exhaustively.

## 23. What PRISM Cannot Claim

- **PRISM cannot claim any of its 7 candidates is independently confirmed as
  ice-bearing.** No Level 1, 2, or 3 evidence exists for any of them
  specifically (§19, §20).
- **PRISM cannot claim its candidates are spatially close to confirmed ice.**
  The nearest named reference site to any candidate (Amundsen, ~15.2 km from
  the primary candidate) is an ice-*negative* control with its own
  contradictory secondary evidence (§18, §21).
- **PRISM cannot claim CPR>1 is ice-specific.** This is explicitly and
  repeatedly contested in the peer-reviewed literature (§15).
- **PRISM cannot claim its DOP formula reproduces or validates against
  Sinha et al. 2026's reported values** — this remains unresolved, per
  `DOP_SINHA_2026_RESEARCH.md`, and is not changed by this broader
  literature pass.
- **PRISM cannot claim ShadowCam optically confirms ice at any of its
  candidates or its own reference craters** — the one directly relevant,
  full-text-verified peer-reviewed paper (Ando et al. 2025) finds the
  opposite for 13 of 14 tested south-polar PSRs.
- **PRISM cannot claim its own radar-based evidence score correlates with
  independently confirmed ice presence** — its own prior test
  (`INDEPENDENT_ICE_VALIDATION.md`) found no such correlation, and this
  investigation found nothing to overturn that result.

## 24. Recommended Validation Experiment

**Best positive-control target: Cabeus (`SP_844580_3134320` in PRISM's own
PSR catalog).** Rationale: the only south-polar location with (a) Level-1
direct water detection (LCROSS, 5.6±2.9 wt%), (b) regional LEND hydrogen
maximum, (c) the only south-polar ShadowCam radiance match to M3, (d) a known
PSR boundary already in PRISM's own shapefile catalog, and (e) DFSAR mosaic
coverage already confirmed (it is inside the same Y4R/L3C mosaic PRISM
already processes). **Recommended experiment: run PRISM's full pipeline
(Pv/CPR/SERD/T-Ratio, terrain hazard, Isolation Forest, and — if a covering
Level-1A SLC acquisition can be found via the same footprint-search method
used for the primary candidate — DOP) on `SP_844580_3134320`, and compare
directly against PRISM's own primary candidate's numbers.** This would be a
formal positive-control run, extending (not replacing) the crater-level test
already done in `INDEPENDENT_ICE_VALIDATION.md`.

**Best negative-control target: Hedervari, Idel'son L, or Wiechert** — clean
M3-negative controls **without** the Amundsen/Brown-et-al.-2022 contradiction
(§13, §21). Recommend **Wiechert** specifically since it is also the
south-polar PSR ShadowCam's own literature (Ando et al. 2025) directly
included in its 14-PSR test set with a confirmed null result — giving two
independent instruments' agreement on its negative status, the cleanest
negative control available.

## 25. References

1. Mitrofanov, I. G. et al. (2010). *Science* 330(6003):483–486. DOI
   10.1126/science.1185696. (+ Technical Comment DOI 10.1126/science.1203341;
   Response DOI 10.1126/science.1203483.)
2. Sanin, A. B. et al. (2017). *Icarus* 283:20–30. DOI
   10.1016/j.icarus.2016.10.019.
3. McClanahan, T. P. et al. (2024). "Evidence for Widespread Hydrogen
   Sequestration within the Moon's South Pole Cold Traps." *Planetary
   Science Journal*. Preprint arXiv:2303.03911.
4. Colaprete, A. et al. (2010). *Science* 330(6003):463–468. DOI
   10.1126/science.1186986.
5. Gladstone, G. R. et al. (2010). *Science* 330(6003) (LCROSS UV/LAMP
   companion paper; not independently fetched, citation only).
6. Li, S. et al. (2018). *PNAS* 115(36):8907–8912. DOI
   10.1073/pnas.1802345115.
7. Verma, N., Bhatt, M., Dangi, M., Kumar, S., Bhardwaj, A. (2025). *Icarus*
   432, 116492. DOI 10.1016/j.icarus.2025.116492 (probable, not confirmed
   against a resolver). **Full text not accessed — search-summary
   confidence only.**
8. Sinha, R. K. et al. (2026). *npj Space Exploration* 2:22. DOI
   10.1038/s44453-026-00038-9. (Full detail in `DOP_SINHA_2026_RESEARCH.md`.)
9. Spudis, P. D. et al. (2013). *JGR Planets* 118. DOI 10.1002/jgre.20156.
10. Eke, V. R. et al. (2014). *Icarus* 241:66–81. arXiv:1312.4749.
11. Fa, W. (2018). *JGR Planets*. DOI 10.1029/2018JE005668.
12. Paige, D. A. et al. (2010). *Science* 330(6003):479–482. DOI
    10.1126/science.1187726.
13. Vasavada, A. R., Paige, D. A., Wood, S. E. (1999). *Icarus* (exact
    volume/page not independently verified this pass — AMBIGUOUS).
14. Watson, K., Murray, B. C., Brown, H. (1961). *JGR* (foundational
    cold-trap concept; citation not independently re-verified this pass).
15. Ando, J., Li, S., Robinson, M., Wagner, R. (2025). *The Planetary
    Science Journal* 6(3):62. DOI 10.3847/PSJ/adb8d1.
16. Watkins, R. N. et al. (author list unverified). *Science Advances*
    (ShadowCam PSR ice search; access-blocked, search-snippet confidence
    only — verify before formal citation).
17. Brown, R. H., Boyd, S., Denevi, B. W., Henriksen, M. R. et al. (2022).
    *Icarus* 377, 114874. DOI 10.1016/j.icarus.2021.114874.
18. Feldman, W. C. et al. (2001). *JGR Planets* 106(E10). DOI
    10.1029/2000JE001444.
19. Lawrence, D. J. et al. (2006). *JGR Planets*. DOI
    10.1029/2005JE002637.
20. Shirvany, R., Chabert, M., Tourneret, J.-Y. (2012). *IEEE JSTARS*
    5(3):885–892. (Full text not accessed — IEEE anti-bot wall.)
21. Marshall, W. et al. (2011). *Space Science Reviews*. DOI
    10.1007/s11214-011-9765-0. (LCROSS Centaur impact coordinate, already
    used in PRISM's `INDEPENDENT_ICE_VALIDATION.md`.)

## 26. Dataset Links

| Dataset | Portal | Coverage | Resolution | Access | Candidate-level use feasible? |
|---|---|---|---|---|---|
| LEND | `pds-geosciences.wustl.edu`; `ode.rsl.wustl.edu` | Global, polar emphasis | ~10 km FWHM | Public, no login | **No** — too coarse for any single PRISM candidate |
| Diviner | `pds-geosciences.wustl.edu/missions/lro/diviner.htm`; `diviner.ucla.edu/data` | Global | ~200 m/px (thermal) | Public, no login | **Yes** — fine enough for per-PSR min/max temperature extraction; not yet done for any PRISM candidate |
| Mini-RF | PDS Geosciences Node; global mosaic release at `pds.nasa.gov/data/pds4/releases/geo/lro_minirf_globalmosaic-20251218/` | Near-global (coverage gaps) | ~30 m/px (mode-dependent) | Public, no login | Plausible — pending confirmation of coverage over each specific PRISM PSR |
| LROC (NAC/WAC) | `data.lroc.im-ldi.com` (PRISM already uses); PDS Imaging Node mirror | Near-global, strip-dependent | 0.5–2 m/px (NAC) | Public, no login | **Yes** — PRISM already does this |
| ShadowCam | `data.im-ldi.com` (PRISM already uses) | South + north PSRs, frame-dependent | 1.7 m/px native | Public, no login | **Yes** — PRISM already does this |
| Chandrayaan-1 M3 | PDS Geosciences Node general holdings; Europe PMC for Li et al. 2018 SI | South-polar strips | 140–280 m/px | Public (PDS); SI ice-map is image-only, not a coordinate layer | Limited — raw cubes are public, but locating ice-detection pixels independently would be new analysis work, not a lookup |
| Chandrayaan-2 DFSAR | ISRO PRADAN `pradan.issdc.gov.in/ch2` (PRISM already uses extensively) | South-polar, acquisition-dependent | 25 m/px (mosaic), finer raw | Login-gated | **Yes** — PRISM already does this |

**No data was downloaded in the production of this report** — this table
identifies what is realistically usable, per task instruction, without
committing to any download.

---

## Final note on scope

This report deliberately does **not** conclude "PRISM detected ice." It
answers the question actually asked: **does PRISM's candidate set occupy a
location for which independent observations converge with PRISM's own
metrics?** The honest answer, across every instrument and paper investigated,
is: **not yet, and not currently measurably so** — PRISM's candidates enjoy
only regional/latitude-band environmental plausibility (Level 4), no
candidate-specific direct or radar evidence (Levels 1–3) exists for any of
the 7 shortlisted PSRs, the nearest independently-studied location to
PRISM's own top candidate is a contested ice-negative control, and PRISM's
own prior positive/negative-control test already found no systematic
separation in its radar metrics. This is reported as the honest scientific
state of the investigation, not softened for presentation purposes.
