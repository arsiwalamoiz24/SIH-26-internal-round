# ICE_PIPELINE_V2_REDESIGN — rebuilding the ice-evidence layer

**Date:** 2026-08-26. Companion code: `src/ice_evidence_pipeline_v2.py` (new,
real, runnable). Companion literature doc: `docs/ICE_METRIC_LITERATURE_MAP.md`.
PRISM v1 (`src/physics_evidence_score.py`) is **preserved unmodified** — this
document explains why it needed a companion, not a replacement, and what the
companion actually does differently.

**The one-sentence reframe this document argues for:** PRISM v1 asked *"how
high is the radar anomaly?"*; V2 asks *"what is the best available evidence,
and does PRISM's radar data add anything once that evidence is accounted
for?"* — these produce different, non-interchangeable outputs, and V2 is
explicitly not a replacement score, it is a different question.

---

## 1. Why PRISM v1 Failed Validation

`docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md` ran PRISM's exact,
unmodified v1 pipeline on Cabeus (LCROSS-confirmed positive) and Wiechert
(M3-confirmed negative). Result: Cabeus scored 0.3204 (rank 11 of 11
validation sites); Wiechert scored 0.7138 (rank 3 of 11). Every metric
feeding the score — Pv, CPR, T-Ratio — individually ranked the negative
control above the positive control. This was **not** a bug in the scoring
arithmetic; `physics_evidence_score.py` executed exactly as designed. The
failure is architectural: **v1 has no mechanism for recognizing that
independent, direct evidence (when it exists) should outrank a contested
radar proxy** — it only knows how to compute a relative percentile of
Pv/CPR/T-Ratio, and it treats that percentile as the entire answer.

## 2. Evidence from Cabeus vs. Wiechert

Real numbers (§7 of the control-validation report, reproduced here for
context): Cabeus Pv 0.217 / CPR 0.166 / T-Ratio 0.200 — all **lower** than
Wiechert's Pv 0.314 / CPR 0.311 / T-Ratio 0.325. This is not noise; the gaps
are large (CPR nearly 2×) and consistent in direction across three
independent metrics. **The correct scientific conclusion is not "PRISM's
radar processing is broken"** — Neish et al. 2011 (§3) independently
confirms Cabeus genuinely has low CPR by real, external measurement. The
correct conclusion is **"CPR/Pv/T-Ratio, as PRISM computes them, do not
track ice presence at this confirmed site — so a score built only from them
cannot be trusted to track ice presence anywhere else either."**

## 3. CPR Literature Conflict

Three independent findings, now confirmed (`ICE_METRIC_LITERATURE_MAP.md`),
jointly establish that CPR is neither necessary nor sufficient for ice:

- **Neish et al. (2011, *JGR Planets* 116, E01005, DOI
  10.1029/2010JE003647, full text obtained):** at Cabeus — the strongest
  confirmed-ice site available — only **2% of Mini-RF pixels** and **0.01%
  of Chandrayaan-1 Mini-SAR pixels** have CPR>1; mean CPR (0.25±0.12) is
  *below* the 0.31±0.17 south-polar regional average. Their own
  interpretation: low CPR rules out a thick, near-surface ice sheet, **not**
  ice mixed as fine grains into regolith. **High CPR is not necessary for
  ice.**
- **Eke et al. (2014) and Fa (2018):** elevated CPR at various craters is
  attributable to crater-wall steepness and blocky ejecta roughness, not
  ice. **High CPR is not sufficient for ice.**
- **Verma et al. (2025):** reportedly attributes some CPR>1 cases to
  surface roughness and reports an inverse CPR-DOP relationship —
  **qualitatively used here; the specific R²~0.99 figure attributed to it
  in web search results is UNVERIFIED (ScienceDirect fully inaccessible in
  two independent investigation passes) and is not cited as fact anywhere
  in V2's code or this document.**

**Consequence for V2:** CPR (and Pv, the same physical family) can only be
used as a *contextual*, roughness-checked, relative signal — never as a
threshold, and never alone.

## 4. DOP Reproducibility Problem

Unchanged from `docs/DOP_SINHA_2026_RESEARCH.md`: 8 independent hypotheses
(window size, small-sample bias, absolute and relative gain/phase
calibration, self-derived and the real Ainsworth et al. 2006 crosstalk
algorithm, an alternate acquisition) all return PRISM's DOP at 0.63–0.86 for
the same craters Sinha et al. 2026 report as 0.10–0.13. **V2 does not use
DOP as ground truth or as a score input.** It is computed and reported, when
available, purely as `dop_diagnostic_not_scored` — visible, not hidden, but
structurally incapable of moving a site's tier.

## 5. Pv Analysis

1. **Exact equation:** `Pv = vol / (evn + vol + odd + hlx)` — Yamaguchi
   four-component volume-scattering fraction (`src/radar_pipeline.py`).
2. **Original source:** Yamaguchi decomposition, a standard, general SAR
   polarimetric-decomposition technique — not lunar- or ice-specific in
   origin.
3. **Scattering mechanism:** fraction of backscattered power attributed to
   randomly-oriented/volume scattering (as opposed to surface, double-bounce,
   or helix scattering).
4. **Ice-specific? No.** Confirmed by `ice_v2_literature_verification.md`
   §E: the literature lists coherent-backscatter enhancement (a genuine,
   ice-related, low-loss-dielectric phenomenon) *alongside* wavelength-scale
   depolarization and dihedral double-bounce (both generic roughness
   effects) as equally valid causes of the same general signal category.
5. **Known alternatives:** rough/blocky regolith, buried rock fields,
   subsurface structural heterogeneity of any kind.
6. **Is PRISM's current sign correct?** PRISM treats high Pv as
   ice-favorable. This is directionally consistent with the (contested)
   literature's ice-related mechanism, but the same direction is equally
   produced by roughness — **the sign is not "wrong," it is
   under-determined.**
7. **Tested against Cabeus/Wiechert:** Cabeus 0.217 < Wiechert 0.314 —
   negative control higher, same failure pattern as CPR.
   **The sign was NOT changed to fix this** (task Sec 6 explicit
   instruction) — Pv is instead demoted to a contextual `radar_evidence`
   component, never a standalone score input.

## 6. SERD Analysis

1. **Exact equation:** unknown — SERD is delivered as a precomputed ISRO
   L3C-MOSAIC band; PRISM reads it directly and has never had access to
   ISRO's internal derivation formula (`docs/SERD_NAN_ANALYSIS.md`, already
   established, re-confirmed this session).
2. **Original source:** ISRO/Chandrayaan-2 DFSAR product documentation
   (CH2DFSAR SIS) — does **not** document the SERD algorithm.
3. **Scattering mechanism:** described by PRISM's own docs as a roughness
   indicator, but this is inherited terminology, not an independently
   verified physical derivation.
4. **Ice-specific? No independent literature validating SERD as an ice
   indicator was found in this or the prior investigation — not
   "contested," genuinely absent.**
5. **Known alternatives:** unknown (algorithm undocumented).
6. **Sign:** PRISM's own prior work already found SERD's directionality
   inconsistent — *lower* inside PRISM's primary candidate's PSR interior
   than its surroundings, the opposite of "rougher/higher = icier" intuition
   some other metrics imply (`CANDIDATE_PHYSICS_RESULTS.md`). At Cabeus vs.
   Wiechert, SERD is the *one* metric favoring Cabeus (0.848 vs. 0.779) —
   but given the unresolved general sign problem, **this single favorable
   result is not treated as validating SERD**, per explicit task instruction
   not to change or trust a sign merely because it helps the control result.
7. **Tested against Cabeus/Wiechert:** see above.

**Verdict: moved to `EXPERIMENTAL_METRICS`, removed from the primary V2
score**, per task Sec 6's explicit rule ("if a metric has no defensible
literature basis for ice detection, move it").

## 7. T-Ratio Analysis

Identical audit outcome to SERD: undocumented ISRO-internal formula, no
independent external literature found validating it as an ice indicator,
directionality untested/unestablished beyond PRISM's own internal
observations. **Moved to `EXPERIMENTAL_METRICS`.**

## 8. Proposed V2 Architecture

A **strict, lexicographic evidence-tier classifier**, not an additive
weighted score:

```
Tier 4 (HIGH)                    <- Level A positive (M3 detection OR LCROSS)
Tier 3 (MODERATE-HIGH)           <- Level B positive, no Level A available
                                     (e.g. a validated ShadowCam radiance shift)
Tier 1 (LOW)                     <- Level A negative (M3 explicit non-detection)
Tier 0 (PLAUSIBLE-UNCONFIRMED)   <- no Level A/B evidence exists at all
                                     (radar/thermal/optical still computed
                                     and reported, but cannot set the tier)
```

The tier is decided **only** by the highest-quality available evidence.
Once Level A has spoken (positive or negative), nothing at Level B–E can
change the tier — this is the literal, code-level implementation of task
Sec 7's "do not allow a lower evidence class to override a higher one," and
it requires no numeric weight to be tuned. See `classify_evidence_tier()`
in `src/ice_evidence_pipeline_v2.py`.

**Output is an "Evidence Index" (an ordinal tier + fully transparent
component breakdown), never an "Ice Probability."** No numeric probability
is computed or claimed anywhere in V2, per explicit task instruction —
there is currently insufficient calibrated data to justify one.

## 9. Mathematical Definitions

- **Tier classification:** a deterministic decision rule (§8), not a
  fitted statistical model — see the exact `if/elif` structure in
  `classify_evidence_tier()`.
- **CPR/Pv relative anomaly:** `interior_mean − exterior_mean`, within the
  same acquisition/window/calibration PRISM's own `radar_pipeline.py`
  already uses — **not** a raw `CPR>1` threshold. `None` where the
  interior/exterior split isn't available (Cabeus, Wiechert — whole-window
  only in the source data), never estimated.
- **Roughness-context flag:** `roughness_percentile_among_tested_sites` — a
  cross-site percentile rank of each site's combined hazard score
  (slope+roughness+illumination, `terrain_algorithms.compute_hazard_map`,
  unmodified) among all sites tested in this session. Explicitly labeled
  **PROVISIONAL** — this is a heuristic comparison, not a fitted or
  published roughness-vs-CPR statistical model (no such model was found or
  independently verifiable in the literature — see §3/`ICE_METRIC_
  LITERATURE_MAP.md`).

## 10. Literature Basis for Each Component

| V2 component | Literature basis |
|---|---|
| Level A (M3) | Li et al. 2018, PNAS, full text |
| Level A (LCROSS) | Colaprete et al. 2010, Science, full text of the finding (search-summary confidence on exact figure) |
| Level B (ShadowCam) | Ando, Li, Robinson & Wagner 2025, PSJ, full text |
| Level C (illumination/PSR) | Watson, Murray & Brown 1961 (foundational cold-trap concept); geometric fact, independently computed by PRISM |
| Level D (CPR/Pv relative anomaly) | Same underlying formula as PRISM v1, reframed per Neish 2011 / Eke 2014 / Fa 2018's collective finding that raw thresholds are unreliable |
| Roughness context | Provisional, explicitly not claimed to be literature-derived (no such published model was found) |
| DOP exclusion | `DOP_SINHA_2026_RESEARCH.md` |
| SERD/T-Ratio exclusion | `ICE_METRIC_LITERATURE_MAP.md` — absence of any external validating literature |

## 11. Positive/Negative Controls

**Train (used to design/motivate the architecture):** Cabeus (positive),
Wiechert (negative) — the two sites the entire redesign was triggered by.

**Held-out (added to `SITES` only after `classify_evidence_tier()` was
already written and had not been touched since):**
- Positive: Faustini, de Gerlache, Haworth, Shoemaker, Sverdrup, Shackleton
  (all M3-confirmed, Li et al. 2018).
- Negative: Hedervari, Idel'son L (clean M3-confirmed negatives), Amundsen
  (M3-negative but **contested** — also appears on Brown et al. 2022's
  "resource-rich" list; kept in as an explicit stress-test of how the
  hierarchy handles conflicting evidence, not swapped for a cleaner site).

## 12. Validation Protocol

Run `src/ice_evidence_pipeline_v2.py` (unmodified after the held-out sites
were added) and record tier assignments. Result: **9 of 9 held-out sites
tiered correctly** (6/6 positives → tier 4, 3/3 negatives → tier 1,
including the contested Amundsen, which the hierarchy correctly resolves in
M3's favor while explicitly reporting the Brown et al. 2022 contradiction
rather than hiding it).

**Important, honest caveat on what this result does and does not mean:**
this is **not** a meaningful test of predictive skill in the machine-
learning sense. Tier 4/1 for a named crater is set by *directly reading its
own M3 classification* — the same information that defines the "positive"/
"negative" label in the first place. **9/9 is close to tautological, not
evidence of a validated detection model.** The genuinely meaningful
validation claim is narrower and more honest: **the architecture correctly
lets Level A evidence set the tier and correctly prevents PRISM's own
contested radar metrics from overriding it** — which is precisely the
mechanism that was missing in v1 (§1). The real open question V2 cannot yet
answer is whether its **Level D radar evidence has any discriminative value
of its own** — that can only be tested on sites with *no* Level A evidence,
which is every one of PRISM's actual 7 candidates, and for which no ground
truth exists to check against (§17).

## 13. Data Leakage Controls

Per task Sec 10: **no numeric weight or threshold in V2 was fit
statistically from Cabeus/Wiechert (or any other site).** `classify_
evidence_tier()` is a fixed logical rule, not a learned model — there is
nothing to "leak" in the conventional sense. The one place a genuine
methodological caution applies: **the decision to build a lexicographic
evidence hierarchy at all was motivated by observing Cabeus's low-CPR/
direct-LCROSS-evidence pattern.** This means Cabeus and Wiechert cannot be
presented as a blind test of *whether such an architecture is a good idea*
— only the 9 held-out sites (§11–12) can support that claim, and even they,
per §12's caveat, mostly validate the mechanism rather than any predictive
content. **No metric weight was ever fit, so no formal train/test split of
numeric parameters was needed** — the task's fallback instruction ("if
sample size is too small to fit a statistical model, use a transparent
rule-based evidence index instead") is exactly the path taken here, not a
compromise forced by insufficient data.

## 14. Limitations

- **The CPR/Pv relative anomaly is not computable for Cabeus, Wiechert, or
  any of the 9 held-out sites** — only the 7 PRISM candidates have a real
  interior/exterior split in this environment's available data
  (`docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md` §5/9, unresolved). Level D
  therefore cannot be cross-checked against the very sites used to validate
  Levels A/B.
- **Roughness-context is a provisional cross-site heuristic**, not a fitted
  or published model — explicitly labeled as such in every output record.
- **No per-pixel incidence-angle raster exists anywhere in PRISM's data** —
  incidence-angle-normalized CPR (task Sec 3) remains structurally
  NOT COMPUTABLE, regardless of which published normalization method is
  chosen.
- **DOP remains entirely a diagnostic field** — genuinely useful information
  (PRISM's own real, candidate-specific DOP values) is computed and stored
  but contributes nothing to any score, by design, until the Sinha
  discrepancy is resolved.
- **All 7 of PRISM's actual candidates land in Tier 0** — V2 does not (and,
  honestly, cannot with currently available data) produce a differentiated
  ice-confidence ranking among them at the same rigor as it does for the
  named, independently-studied craters. This is stated as the correct,
  honest output — not a shortcoming to paper over.

## 15. Expected Outputs

Per candidate (see `src/ice_evidence_pipeline_v2.py`'s `build_evidence_
index()` and the exact tree structure requested in the task):

```
Ice Evidence V2
├── Evidence Index (tier code + label, NOT a probability)
├── Independent Evidence (Level A/B: M3, LCROSS, LEND, ShadowCam)
├── Thermal Plausibility (Level C: illumination fraction)
├── Radar Evidence (Level D: CPR/Pv relative anomaly, roughness context)
├── DOP Diagnostic (not scored)
├── Experimental Metrics (SERD, T-Ratio — not scored)
└── Hazard & Traversability (kept fully separate, per Sec 16)
```

## 16. How V2 Connects to Hazard Mapping

**It doesn't, by design** (task Sec 12). `hazard_and_traversability` is
reported alongside the evidence index in the same JSON record for
convenience, but is explicitly excluded from `evidence_index` computation.
PRISM's existing `terrain_algorithms.py` (slope/roughness/illumination/
hazard) is reused **unmodified** as the source of this field — V2 adds no
new hazard logic, it only stops mixing hazard into the ice score.

## 17. How V2 Connects to Rover Traversal / Landing-Site Scoring

Per task Sec 12's proposed framework, Objective 3 should combine
`Landing Site Score = Ice Evidence + Safety + Traversability + Mission
Constraints` as an **explicit, documented decision framework** — not
implemented in this pass (out of scope; this pass is the ice-evidence layer
only), but V2's output shape is designed for exactly this future
consumption: `evidence_index.tier_code` (an ordinal 0/1/3/4, not a
continuous probability) is a deliberately conservative input a future
landing-site scorer can combine with hazard/traversability without
implying false numerical precision. **A tier-0 candidate (all 7 of PRISM's
current shortlist) should not be scored as if it had any ice-confidence
advantage over another tier-0 candidate on the basis of Level A/B evidence
— only their Level D radar-anomaly-minus-roughness-context differs, and
that should be weighted accordingly modestly by whatever Objective-3 logic
is eventually built.**

## 18. What Can and Cannot Be Claimed

**Can claim:**
- V2's evidence hierarchy, applied identically and without any site-specific
  tuning, correctly tiers Cabeus (positive) above Wiechert (negative), and
  correctly tiers all 9 held-out M3-classified sites — because it reads
  independent evidence directly rather than relying on PRISM's own
  contested radar metrics.
- Every metric now carries an explicit, sourced ice-specificity rating
  (`ICE_METRIC_LITERATURE_MAP.md`), and SERD/T-Ratio/DOP no longer silently
  contribute to any headline score.
- The architecture is fully reproducible, uses no fitted numeric weights,
  and is documented well enough that a future session could extend it
  without re-deriving any of this reasoning.

**Cannot claim:**
- That V2 "solves" ice detection for PRISM's actual 7 candidates — it
  correctly and honestly reports that **none of them has any Level A/B
  evidence**, and therefore all 7 remain at the same, low-confidence
  evidence tier V2 assigns by design when no independent evidence exists.
- That the 9/9 held-out result is a validated predictive model — per §12,
  it is close to tautological (the tier for a named crater is read directly
  from the same M3 classification that defines its label), and the one
  genuinely novel, non-trivial claim it supports is architectural (Level A
  correctly overrides Level D), not predictive.
- That CPR/Pv relative anomalies, even reframed, are validated ice
  indicators — they remain Level D, explicitly weaker than Level A/B, per
  the unresolved literature conflict documented in §3.
- **ICE DETECTION PIPELINE REMAINS UNVALIDATED for PRISM's own candidate
  set specifically** — stated directly, per task Sec 17's explicit
  instruction not to claim success prematurely. What V2 delivers instead is
  a more honest instrument: it stops PRISM from reporting a confident-
  looking single number for the 7 candidates when no confident-looking
  number is actually justified by the evidence available, and it correctly
  separates the layers (independent evidence, radar context, roughness
  context, hazard) that PRISM's own future work (a genuine same-scale radar
  re-run, a targeted search for any independent evidence actually covering
  one of the 7 candidates) would need to improve on, one at a time, instead
  of all blended into one opaque score.
