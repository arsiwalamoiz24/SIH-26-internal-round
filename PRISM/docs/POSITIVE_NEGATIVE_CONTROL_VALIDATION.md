# POSITIVE_NEGATIVE_CONTROL_VALIDATION — Cabeus vs. Wiechert

**Date:** 2026-08-26. **Scope:** a formal positive/negative-control
experiment running PRISM's ice-detection pipeline on LCROSS Cabeus (known
positive) and Wiechert (known negative), to directly test whether PRISM's
metrics — individually and combined — can distinguish a confirmed-ice site
from a confirmed-checked-negative site. **The 7-candidate shortlist ranking
is NOT modified by this document.**

**Epistemic key** (as in the two prior reports): **FACT** = verified against
a primary/full-text source or a real computation run in this session.
**OBSERVATION** = a pattern noticed in FACTs. **HYPOTHESIS** = untested/
partially-tested explanation. **CONCLUSION** = a claim the evidence actually
supports.

**Data-provenance note, stated up front:** this session's environment has no
local copy of the Chandrayaan-2 DFSAR Y4R/L3C mosaics or raw Level-1A SLC
products (ISRO PRADAN is login-gated; no cached team-Drive URLs were
available in this environment). **Pv/CPR/SERD/T-Ratio and the combined
evidence score below are real values, computed by PRISM's own pipeline in a
prior session** (`INDEPENDENT_ICE_VALIDATION.md`, 2026-08-22,
`src/validation_pipeline.py`) and re-extracted here from
`outputs/validation/ice_reference_sites.csv` and `control_sites.csv` — not
recomputed in this session, and not fabricated. **Terrain hazard (slope,
roughness, illumination) IS freshly computed in this session**, live, from
the real public NASA PGDA LOLA DEM, using PRISM's own
`src/terrain_algorithms.py` formulas and the identical window convention
`src/hazard_map_shortlist_pipeline.py` uses for PRISM's own 7-candidate
shortlist (±5,000 m buffer, native 20 m/px). **DOP and Isolation Forest could
not be computed for either site in this session** — see §5, §13.

---

## 1. Objective

Test PRISM's ice-detection pipeline against a known positive control
(Cabeus, direct LCROSS water detection) and a known negative control
(Wiechert, M3-checked non-detection): does the known positive score above
the known negative, on each individual metric and on the combined evidence
score?

## 2. Why Cabeus

Cabeus hosts the LCROSS impact site — the only place on the Moon with a
**direct, in-situ physical measurement** of water (not a remote inference).
Colaprete et al. (2010, *Science* 330:463–468, DOI 10.1126/science.1186986)
report **5.6 ± 2.9 wt% water** in the impact ejecta plume. PRISM's own PSR
catalog already maps this site to `SP_844580_3134320`
(`INDEPENDENT_ICE_VALIDATION.md`).

## 3. Why Wiechert

Li et al. (2018, *PNAS* 115(36):8907–8912) explicitly list Wiechert among
craters where a Diviner-identified cold trap (Tmax ≤110 K) **was
specifically checked for the M3 3-μm ice-absorption feature and the feature
was not found.** `LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md` separately
identifies Wiechert as the **cleanest** available negative control (unlike
Amundsen, it has no contradicting secondary evidence from Brown et al. 2022)
and as a site independently included in Ando et al. (2025)'s ShadowCam
radiance study, where it showed **no** positive shift — a second instrument
agreeing with its negative status.

## 4. Independent Ground Truth

**Precise terminology used throughout, per task instruction: "M3-negative"
means "explicitly checked at M3's ~280 m spectral resolution and no
ice-absorption feature was detected" — not "genuinely ice-free." M3 cannot
rule out ice below its detection sensitivity, ice at depth, or ice outside
the specific pixels examined.**

### Cabeus

| Evidence source | Finding | Access status |
|---|---|---|
| LCROSS (Colaprete et al. 2010) | 5.6±2.9 wt% water in ejecta plume — a single-point, subsurface-excavating measurement | Search-summary, high-confidence headline number |
| LEND (Sanin et al. 2017) | Regional hydrogen maximum in the south polar region is at the Cabeus impact site; 0.5–4.0 wt% water-ice equivalent depending on assumed overburden | Search-summary |
| Chandrayaan-1 M3 (Li et al. 2018) | **Cabeus does not appear in either Li et al. 2018's M3-positive or M3-negative crater list** — it was not one of the cold traps M3 specifically classified in that paper's SI Fig. S5 | Full text obtained (prior session) — this is a genuine, confirmed absence, not an access gap |
| ShadowCam (Ando et al. 2025) | The **only** south-polar PSR (of 14 tested) showing a positive M3-vs-non-M3 radiance shift | Full text obtained |
| Diviner (Paige et al. 2010) | Subsurface temperature estimated ~38 K | Search-summary |
| Spatial scale of LCROSS measurement | Single impact point (±115 m lat / ±44 m lon, 1σ, per Marshall et al. 2011); **not** a PSR-wide map | Confirmed via PRISM's own prior validation work |

### Wiechert

| Evidence source | Finding | Access status |
|---|---|---|
| Chandrayaan-1 M3 (Li et al. 2018) | Cold trap explicitly checked; **"no ice exposure detected"** at M3's spectral/spatial sensitivity — precise terminology, not "ice-free" | Full text obtained |
| ShadowCam (Ando et al. 2025) | Included in the 14-PSR south-pole test set; **not** singled out as showing a radiance shift (i.e., consistent with the M3 non-detection) | Full text obtained |
| LEND | No site-specific data found — regional coverage only (§`LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md` §4.1) | No data |
| Diviner | No site-specific temperature data found in this or the prior literature pass | No data |
| Mini-RF | No study targeting Wiechert specifically was found | No data |

## 5. Data Availability

| Requirement | Cabeus | Wiechert | Same for both? |
|---|---|---|---|
| Y4R/L3C mosaic coverage (Pv/CPR/SERD/T-Ratio) | Yes — used in prior session | Yes — used in prior session | Yes, product-wise |
| **Window size used for Pv/CPR/SERD/T-Ratio** | **±1.0 km half-window** (LCROSS point-measurement scale) | **±20.5 km half-window** (crater-radius scale, diameter 41 km / 2) | **No — genuine mismatch, not controlled in the source data** (see §9) |
| PSR-catalog polygon | Yes, `SP_844580_3134320` | **No** — Wiechert's centroid does not fall inside a LOLA PSR sub-polygon (confirmed, `in_psr_catalog: False` in the source CSV) | **No** |
| LOLA DEM (terrain) | Yes, public `/vsicurl/` | Yes, public `/vsicurl/` | **Yes — freshly computed this session at an identical ±5,000 m window for both** |
| Raw Level-1A SLC DFSAR (for DOP) | Not available in this environment (PRADAN login-gated; no acquisition-coverage search was performed for either site) | Same | Same (neither) |
| ShadowCam raw frame (for a fresh pixel correlation check) | Not re-fetched this session (relies on Ando et al. 2025's published finding instead, §4) | Same | Same (neither re-fetched; both use the same published paper) |
| DFSAR pixel grids for Isolation Forest v2 | Not available in this environment | Same | Same (neither) |

## 6. Experimental Protocol

- **Pv/CPR/SERD/T-Ratio, evidence score:** extracted verbatim from
  `outputs/validation/ice_reference_sites.csv` /`control_sites.csv`
  (`src/validation_pipeline.py`, same code path/formulas as PRISM's own
  `src/candidate_physics_pipeline.py`, per that script's own docstring — no
  formula changes). **Not recomputed this session** — see §5 for the window
  caveat.
- **Terrain (slope/roughness/illumination/hazard):** freshly computed this
  session, live, via `src/terrain_algorithms.py`'s exact functions
  (`compute_slope`, `compute_roughness_rms`, `compute_cumulative_illumination`,
  `compute_hazard_map`, unmodified), reading the real NASA PGDA LOLA DEM
  (`LDEM_80S_20MPP_ADJ.TIF`) via GDAL `/vsicurl/`, at the **identical**
  ±5,000 m buffer / native 20 m/px window `src/hazard_map_shortlist_
  pipeline.py` uses for PRISM's own 7 shortlisted candidates. **This is the
  one part of this experiment that is fully scale-matched between the two
  sites**, per the task's core rule.
- **DOP:** not computed for either site — no raw Level-1A SLC acquisition
  covering either site was searched for or downloaded in this session (would
  require an authenticated PRADAN session, unavailable here). Per the task's
  own explicit instruction, DOP is **not** used as ground truth in this
  experiment regardless.
- **Isolation Forest:** not computed for either site — requires either the
  336-PSR overview table (v1, needs ISRO-gated mosaic access) or per-pixel
  Y4R/L3C windowed reads (v2, needs cached remote URLs not present in this
  environment).
- **ShadowCam:** not independently re-run as a pixel-correlation check this
  session (would require re-deriving a reverse-engineered coordinate-search
  API against `data.im-ldi.com` from scratch, out of scope for this pass
  given time budget); instead, the directly-relevant, full-text-verified
  peer-reviewed finding for both exact sites (Ando et al. 2025, §4) is used.

## 7. Metric Results

| Metric | Cabeus | Wiechert | Difference (Cabeus − Wiechert) | Interpretation |
|---|---:|---:|---:|---|
| **Pv** | 0.2172 | 0.3139 | **−0.0967** | Negative control higher |
| **CPR** | 0.1663 | 0.3109 | **−0.1446** | Negative control higher |
| **SERD** | 0.8484 | 0.7790 | +0.0694 | Positive control higher — but SERD's directionality is explicitly unresolved/excluded from PRISM's own evidence score (see §12) |
| **T-Ratio** | 0.1998 | 0.3252 | **−0.1254** | Negative control higher |
| **DOP** | NO DATA | NO DATA | — | Not computable in this environment; not used as ground truth per task instruction |
| **Isolation Forest** | NO DATA | NO DATA | — | Not computable in this environment (requires ISRO-gated mosaic access) |
| **Slope (deg, ±5km window)** | 6.64 | 11.77 | −5.13 | Cabeus flatter (hazard-relevant, not an ice indicator) |
| **Roughness RMS (m)** | 3.31 | 5.99 | −2.68 | Cabeus smoother (hazard-relevant, not an ice indicator) |
| **Illumination fraction** | 0.0022 | 0.0531 | −0.0509 | Cabeus more consistently shadowed (environmental plausibility, not a direct ice indicator) |
| **Hazard score (0–1)** | 0.4527 | 0.4644 | −0.0117 | Cabeus marginally lower/safer, both solidly in "caution" tier |
| **Final evidence score** (Pv/CPR/T-Ratio composite, SERD excluded, PRISM's own formula) | **0.3204** (rank 11 of 11 validation sites) | **0.7138** (rank 3 of 11) | **−0.3934** | **Negative control scores decisively higher** |

## 8. Combined PRISM Results

**Does the known positive control rank above the known negative control? No.**
Cabeus's evidence score (0.320) is the **lowest of all 11 sites** in PRISM's
own validation set (7 M3-positive + 4 M3-negative craters,
`INDEPENDENT_ICE_VALIDATION.md`); Wiechert's (0.714) ranks 3rd-highest.
**This is a decisive inversion of the expected relationship, not a marginal
or ambiguous result.**

## 9. Spatial-Scale Analysis

Per task instruction, the exact LCROSS footprint was **not invented**. The
existing radar-metric windows used were:
- **Cabeus: ±1.0 km half-window** (2 km across) — chosen in the prior
  session to reflect LCROSS's point-measurement scale, the best defensible
  proxy available since no exact plume footprint is published as a
  coordinate/polygon.
- **Wiechert: ±20.5 km half-window** (41 km across) — derived from the
  crater's own diameter/2, matching the "crater-disk" convention used for
  every other reference site in that validation run.

**This is a genuine, uncontrolled variable — the two sites were NOT evaluated
at matched radar-metric window sizes**, and this session's environment
cannot recompute either site at additional scales (280 m, 500 m, 1 km, whole
PSR) without Y4R/L3C mosaic access it does not have. **This must be stated
as a real limitation, not glossed over.**

**However, the direction of this confound does not obviously favor the
observed result being an artifact.** Cabeus's window is *small and tightly
centered* on the actual LCROSS impact point — if anything, a smaller,
more-precisely-targeted window should concentrate any real ice signal more
strongly than a larger, more heterogeneous window would dilute it.
Wiechert's much larger window averages over 41 km of crater interior,
which would be expected to *dilute* any localized anomaly toward a
background/control-like value. **If window size alone explained the
result, the expected bias direction would be for Cabeus (small, targeted
window) to score relatively higher, not lower, than a fair same-scale
comparison would show — the opposite of what was observed.** This is a
reasoned argument, not a proof, and does not eliminate the need for a
genuine same-scale re-run as a follow-up (§18) — but it means the window
mismatch is unlikely, by itself, to be manufacturing the observed inversion.

**Terrain metrics (§7) ARE scale-matched (identical ±5 km window for both)**
— this is the one part of the experiment fully free of this confound, and
it shows a much smaller, directionally different pattern (Cabeus
marginally *safer*/flatter, not an ice signal either way).

## 10. Positive-Control Performance

Cabeus **underperforms** on every metric feeding PRISM's combined evidence
score (Pv, CPR, T-Ratio all lower than Wiechert's) and on the combined score
itself (lowest of 11 validation sites). It only scores higher on SERD, a
metric PRISM's own team has never established a consistent ice-vs-not
directionality for, and which is explicitly excluded from the combined score
for exactly that reason. Terrain-wise, Cabeus is marginally more favorable
(flatter, more consistently shadowed) — genuine, real, but not part of
PRISM's ice-evidence scoring.

## 11. Negative-Control Performance

Wiechert **outperforms** the known positive control on Pv, CPR, T-Ratio,
and the combined evidence score. This is the mirror image of §10 — a
negative control scoring like a strong candidate, which is precisely the
failure mode a control experiment exists to catch.

## 12. Metric-Level Interpretation

- **Does CPR distinguish Cabeus from Wiechert? Yes — but in the wrong
  direction.** Wiechert's CPR (0.311) is nearly double Cabeus's (0.166).
- **Does Pv distinguish them? Yes, wrong direction** — same pattern.
- **Does T-Ratio distinguish them? Yes, wrong direction** — same pattern,
  the largest absolute gap of the three (0.125).
- **Does SERD distinguish them? Yes, correct direction (Cabeus higher)** —
  but SERD's sign convention is unresolved in PRISM's own prior work
  (`CANDIDATE_PHYSICS_RESULTS.md` already flags SERD as *lower* inside
  PRISM's own primary candidate's PSR interior than its surroundings — the
  opposite of the "rougher/higher SERD = icier" intuition some other metrics
  imply) — this single-metric "win" should not be read as validating SERD as
  an ice indicator without further work.
- **Does DOP distinguish them?** Not testable — no data for either site in
  this environment.
- **Does Isolation Forest distinguish them?** Not testable — no data.
- **Does terrain information help?** It provides real, useful hazard
  context (Cabeus is flatter and more consistently shadowed than Wiechert
  within a matched window) but is **not an ice indicator** and was never
  claimed to be one by PRISM's own design — it correctly stays out of the
  ice-evidence score.

**Bottom line: of the four metrics that actually feed PRISM's combined
ice-evidence score, three (Pv, CPR, T-Ratio) rank the negative control
above the positive control, and the fourth (SERD) is excluded from the
score precisely because its sign is unresolved.**

## 13. Failure Modes

- **DOP and Isolation Forest could not be evaluated at all** — a real gap
  in this experiment's completeness, driven by data/tooling access in this
  specific environment, not a finding about DOP's or Isolation Forest's own
  validity.
- **Window-size mismatch between the two sites' radar metrics** (§9) is a
  genuine, documented limitation, argued (not proven) to be unlikely to
  fully explain the observed inversion.
- **Cabeus is absent from Li et al. 2018's own M3 crater lists** — meaning
  Cabeus's "positive control" status rests entirely on LCROSS (direct) and
  LEND (regional) evidence, not on M3, unlike every other positive-control
  site in PRISM's validation set. This is a real asymmetry in what "positive
  control" means across sites and should be kept in mind when generalizing
  this result.
- **ShadowCam was not independently re-run** for either site this session —
  the Ando et al. 2025 finding is used as-is, not re-verified against fresh
  pixel data.

## 14. What Passed

- The **terrain/hazard pipeline** ran identically, successfully, and
  reproducibly for both sites using real public data, with no site-specific
  tuning — a clean methodological success, independent of the ice-evidence
  question.
- **PRISM's own evidence-score formula executed exactly as designed**,
  without modification, on both sites — the pipeline itself is functioning
  correctly; the *result* it produces is the problem, not a bug in the
  scoring code.

## 15. What Failed

- **The combined PRISM ice-evidence score ranks the known negative control
  above the known positive control** — decisively (rank 3 vs. rank 11 of
  11).
- **Every individual metric that feeds that score (Pv, CPR, T-Ratio) does
  the same**, independently.
- This is not a new finding manufactured by this experiment — it
  **reaffirms** PRISM's own prior, broader test
  (`INDEPENDENT_ICE_VALIDATION.md`: positive mean score 0.573 vs. control
  mean 0.636 across 7 positive/4 control sites) in a tightly-scoped,
  single-pair form, exactly as the task requested.

## 16. Implications for the 7 Candidates

**The 7-candidate ranking is not modified by this document, per explicit
instruction.** But the result here directly reinforces
`LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md`'s conclusion: PRISM's
Pv/CPR/T-Ratio-based evidence score — the same score used to rank the 7
shortlisted candidates — has now failed a dedicated, focused control
experiment as well as the earlier broader one. **This means the physics
evidence score ranking among the 7 candidates should be read as an
internally-consistent relative ordering within PRISM's own methodology, not
as evidence that higher-ranked candidates are more likely to be ice.** The
ranking's validity as an ice-probability proxy is now doubly (broad test +
this focused test) unsupported by independent evidence.

## 17. Limitations

- Pv/CPR/SERD/T-Ratio were not recomputed in this session and carry forward
  the window-size mismatch documented in §5/§9.
- DOP and Isolation Forest are simply absent from this experiment, not
  tested-and-passed or tested-and-failed.
- Only two sites were tested in this focused experiment (a third/fourth
  site, e.g. Faustini or Shoemaker, would strengthen statistical confidence,
  and PRISM's own broader 11-site test already exists and points the same
  direction).
- ShadowCam evidence for both sites comes from one external paper (Ando et
  al. 2025), not a fresh PRISM-side pixel computation.
- Terrain hazard, while freshly and identically computed, is not an ice
  indicator and does not bear on the pass/fail determination in §18 below.

## 18. Recommended Next Experiment

1. **Same-scale radar re-run** (highest priority): once an environment with
   Y4R/L3C mosaic access (either ISRO PRADAN credentials or the team's
   cached Google-Drive `/vsicurl/` URLs) is available, recompute Pv/CPR/
   SERD/T-Ratio for both Cabeus and Wiechert at **matched** window sizes
   (e.g., both at the crater-disk convention, and both at a small
   LCROSS-point-scale window) to fully close the §9 gap.
2. **Extend to a third control pair** (e.g., Faustini as a second positive,
   Hedervari or Idel'son L as a second negative) using the same matched-scale
   protocol, to check whether the Cabeus/Wiechert result generalizes or is
   specific to this pair.
3. Per the parent literature investigation's own recommendation: **pixel-
   level M3 validation** remains blocked by the same access gap identified
   there (no machine-readable M3 ice-detection coordinates exist anywhere
   found in either investigation) — this is a data-discovery problem, not a
   PRISM engineering problem, and is lower priority than #1 above given #1
   directly addresses this experiment's own most material limitation.

---

## Final classification: **FAIL**

Per the task's own classification rules: this is not INCONCLUSIVE, because
a real, matched-window comparison (terrain) was possible and executed, and
the ice-evidence-relevant metrics (Pv, CPR, T-Ratio, combined score), despite
the window-size caveat, show a large, directionally consistent, and
independently-reaffirmed (via `INDEPENDENT_ICE_VALIDATION.md`'s broader
prior test) inversion — not a marginal or ambiguous result that residual
data limitations could plausibly flip. It is not PARTIAL PASS, because no
ice-evidence metric (excluding the excluded, sign-ambiguous SERD) discriminates
correctly. **PRISM's current combined ice-evidence score, and each of its
three active input metrics individually, ranks the known negative control
(Wiechert) above the known positive control (Cabeus) — the pipeline fails
this basic control experiment, as designed and executed identically for
both sites.**
