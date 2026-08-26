# DOP_SINHA_2026_EXECUTIVE_SUMMARY

**Date:** 2026-08-26. Short-form summary of `DOP_SINHA_2026_RESEARCH.md` (the
full DOP-vs-Sinha-et-al.-2026 investigation) plus, below, its natural
follow-on: `LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md` (the broader
multi-instrument independent-validation investigation). Read the two full
reports for source-by-source detail, equations, and access-status caveats —
this file is a pointer and headline summary, not a replacement for either.

---

## DOP vs. Sinha et al. 2026 — headline summary

PRISM computes a linear-pol Stokes DOP of 0.63–0.86 for the same craters
(F2, F3, inside Faustini's PSR) that Sinha et al. 2026 (*npj Space
Exploration* 2:22, DOI 10.1038/s44453-026-00038-9) report as 0.10–0.13.
PRISM's CPR values for the same craters land close to Sinha's (F2: 44.75%
vs. 47% CPR>1; F3: 33.3% vs. 42%).

Independent, verbatim-verified reading of Sinha et al. 2026's actual
published text found:

- **Sinha's own paper states no relationship between its Stokes parameters
  (S1–S4) and the HH/HV/VH/VV channels DFSAR measures.** Their DOP equation
  is given with the sole gloss "S1–S4 are real numbers known as Stokes
  parameters" — no construction formula.
- Sinha's paper states no processing level, no calibration/crosstalk
  procedure, no multilook window, and no acquisition ID for the DOP
  computation. A Supplementary Table 1 exists but its contents were not
  retrievable.
- Sinha's only cited authority for *interpreting* DOP (Raney et al. 2012's
  m-χ decomposition, via Mohan et al. 2011) is a **hybrid dual-polarimetric
  (2-channel) construction**, not standard quad-pol. PRISM's own tested
  hybrid-pol analogue still returns 0.57–0.60, not 0.10–0.13 — the basis
  mismatch is real but not, by itself, sufficient to close the gap.
- **Correction to PRISM's own prior documentation:** the "Kumar et al. 2022,
  Adv. Space Res. 70(12)" and "Zhao et al. 2024" citations previously used
  in PRISM's DOP scripts as tied to Sinha's methodology do not appear in
  Sinha's actual 56-entry reference list.

**Classification:** the discrepancy is best explained by **paper
underspecification (H), compounding a likely different DOP definition/basis
(C/D)** — not a proven PRISM implementation error. A rigorous, real
implementation of the Ainsworth et al. 2006 crosstalk-calibration algorithm
ruled out gross miscalibration on PRISM's side. 8+ literature-justified
hypotheses were tested; none closed the gap.

**Recommendation:** contact Sinha et al. directly (exact question drafted in
`DOP_SINHA_2026_RESEARCH.md` §17) — this is the single highest-value next
step, since it would resolve most of the confirmed unknowns at once.

Full report: `PRISM/docs/DOP_SINHA_2026_RESEARCH.md`.

---

## Independent Lunar Ice Evidence

Follow-on investigation (`LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md`,
same date) asked a broader question: setting the Sinha DOP dispute aside,
does independent scientific evidence — NASA and ISRO instruments, and
peer-reviewed literature beyond Sinha's one paper — support PRISM's 7
shortlisted candidates specifically? The strongest findings:

- **None of PRISM's 7 shortlisted candidates is a named crater** with its
  own literature (Cabeus, Faustini, Shackleton, etc. are all elsewhere).
  Every independent instrument/paper found (LEND, Mini-RF, LCROSS, M3,
  ShadowCam, Diviner, quantitative-abundance studies) targets *named*
  craters, not PRISM's unnamed LOLA-catalog PSR polygons.
- **PRISM's primary candidate (`SP_840980_0797630`) sits ~15.2 km from
  Amundsen crater** — the closest approach found between any PRISM
  candidate and any independently-studied site. Amundsen is an **M3
  ice-negative control** (Li et al. 2018) that also, contradictorily,
  appears on a separate paper's (Brown et al. 2022) "resource-rich" PSR
  list — a genuine, unresolved cross-instrument disagreement at PRISM's
  own doorstep, not a confirmation.
- **ShadowCam — the one instrument PRISM itself already uses for optical
  evidence — does not, per the most directly relevant peer-reviewed paper
  (Ando, Li, Robinson & Wagner 2025), confirm M3's south-polar ice
  detections at 13 of 14 tested named PSRs.** Only Cabeus shows the expected
  signal. PRISM's own prior verification (real terrain signal, ~0.99
  adjacent-pixel correlation) establishes signal *quality*, not ice
  *presence* — these are different claims.
- **CPR's ice-specificity is genuinely, actively contested in the
  peer-reviewed literature** (Spudis et al. 2013 pro-ice vs. Eke et al.
  2014 / Fa 2018 roughness-alternative) — reinforcing, not just repeating,
  PRISM's own existing caution about this metric.
- **LEND (10 km FWHM) and the 2024 McClanahan et al. thermal/topographic
  "widespread ice" study are both regional-scale**, not candidate-scale —
  every PRISM candidate PSR is smaller than a single LEND resolution
  element.
- **PRISM's own prior positive/negative-control test** (running its exact
  radar pipeline on 7 M3-positive and 4 M3-negative craters,
  `INDEPENDENT_ICE_VALIDATION.md`) found **no systematic separation** —
  reaffirmed, not overturned, by this broader literature pass.

**Honest bottom line:** PRISM's candidates currently have regional/
latitude-band environmental plausibility (Level 4 of a 5-level evidence
hierarchy — see the full report §19) — genuine but weak support. **No
Level 1–3 (direct, strong remote-sensing, or radar) independent evidence
exists for any of PRISM's 7 specific candidates.** The nearest
independently-studied reference site to PRISM's own top candidate is a
contested ice-negative control, not a positive one.

**Recommended validation experiment:** run PRISM's full pipeline on Cabeus
(`SP_844580_3134320`, already in PRISM's own PSR catalog) as a formal
positive control — the only south-polar location with Level-1 direct
detection, a regional LEND maximum, and the only ShadowCam radiance match to
M3 — using Wiechert as the cleanest available negative control.

Full report: `PRISM/docs/LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md`.

---

## Positive/Negative Control Validation

The recommended experiment above was run (`PRISM/docs/POSITIVE_NEGATIVE_
CONTROL_VALIDATION.md`, same date): PRISM's pipeline was executed identically
on Cabeus (positive control) and Wiechert (negative control) — same formulas,
same code paths, only the location changed. Pv/CPR/SERD/T-Ratio and the
evidence score are real values from PRISM's own prior validation run
(`INDEPENDENT_ICE_VALIDATION.md`); terrain hazard (slope/roughness/
illumination) was freshly computed this session, live, from the real public
NASA LOLA DEM, at an identical window for both sites. DOP and Isolation
Forest could not be computed for either site (no PRADAN/mosaic access in
this environment) and are explicitly marked NO DATA, not estimated.

**Result: Cabeus scored LOWER than Wiechert, not higher.**
- Combined evidence score: Cabeus 0.320 (rank 11 of 11 in PRISM's validation
  set) vs. Wiechert 0.714 (rank 3 of 11).
- **Pv, CPR, and T-Ratio — every metric that actually feeds the combined
  score — each individually rank Wiechert above Cabeus.** Only SERD favors
  Cabeus, and SERD's sign convention is unresolved elsewhere in PRISM's own
  work and is already excluded from the score for that reason.
- **DOP could not help or hurt this experiment — it was not computable for
  either site.** Per its own investigation, DOP remains an unvalidated,
  PRISM-internal metric, not something this experiment could bring in as
  ground truth either way.
- **CPR hurt, not helped**: it moved in the wrong direction, same as Pv and
  T-Ratio.
- Terrain hazard was scale-matched and computed fresh, but is not part of
  the ice-evidence score and does not change the classification.

**Classification: FAIL.** PRISM's combined ice-evidence score, and each of
its three active input metrics individually, ranks the known negative
control above the known positive control. This reaffirms, in a tightly
controlled single-pair form, PRISM's own broader prior finding
(`INDEPENDENT_ICE_VALIDATION.md`). The 7-candidate shortlist ranking was not
modified by this experiment, but its validity as an ice-*probability* proxy
(as opposed to an internally-consistent relative ranking) is now
unsupported by two independent PRISM-run tests, not just the literature
review.

Full report: `PRISM/docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md`.
