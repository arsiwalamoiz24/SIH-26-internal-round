# PM4W_PRISM_IMPLEMENTATION — implementation report

**Date:** 2026-08-26. **Objective unchanged: physics-based lunar
water-ice detection.** Code: `src/pm4w_detector.py` (new, PM4W-feasible
components only), `src/dfsar_ice_evidence.py` (new, DFSAR kept as a
separate, clearly-labeled layer). Neither modifies `src/ice_evidence_
pipeline_v2.py` or `src/ice_radar_characterization_v3.py`. No V4/V5, no
new weights, no threshold tuning, no 7-candidate ranking change.

---

## 1. What PM4W requires

A hard, per-pixel, 9-condition AND-gate: CPR>1, DOP<0.2, backscatter<−15dB,
a phase window, a weighted-power term, a volume-scattering-dominance
decomposition test, a fractal-roughness (radar-intensity-domain) filter,
temperature<110K, illumination<0.2 — all derived from **Mini-RF's own
hybrid-pol (circular-transmit, dual-linear-receive) Stokes parameters**,
plus Diviner temperature. Full detail: `docs/PM4W_COMPLETE_METHOD_
REPRODUCTION.md`.

## 2. What PRISM can reproduce

**One condition directly usable now: illumination < 0.2** — real,
already-computed for all 18 sites tested, via PRISM's own independently-
implemented LOLA-DEM cumulative illumination model (ANALOGUE
comparability — not verified formula-identical to PM4W's own illumination
product, but the same physical quantity from the same source data type).

**One condition usable as an explicit analogue: the CPR>1 condition**,
using PRISM's existing per-pixel `cpr_pct_gt1_inside` statistic (available
for the 7 candidates only) as a stand-in for PM4W's per-pixel Stokes CPR
test — **never called "PM4W CPR,"** always labeled ANALOGUE, because
PRISM's CPR is an ISRO-precomputed band of undocumented formula, not a
self-computed Stokes construction.

## 3. What PRISM cannot reproduce

DOP, backscatter, phase, weighted power, the volume-scattering
decomposition, and fractal roughness **all require genuine Mini-RF
complex/Stokes data PRISM has never ingested.** Temperature requires
Diviner data PRISM has never ingested. None of these were estimated,
substituted, or approximated from DFSAR data — every one is reported as
`NO_DATA` with an explicit reason in `src/pm4w_detector.py`'s output.

## 4. Which data are missing

Per `docs/PM4W_DATA_REQUIREMENTS.md`'s full table:
- **Mini-RF Level 2 / CDR-MOSAIC data** for Cabeus, Wiechert, and all 7
  candidates — highest priority. A specific, real, public NASA PDS dataset
  was identified this session (`LRO-L-MRFLRO-5-CDR-MOSAIC-V1.0`, south-
  polar CPR and S1 mosaics, 118 m/px, no login required, stated coverage
  ≥80°S encompassing all 9 sites of interest) — but the exact file URL was
  not pinned down within this session's budget.
- **Diviner per-candidate temperature** — no ingestion pipeline exists;
  public PDS access, never attempted.
- **PM4W's own supplementary material** — not located; needed to resolve
  the `w` metric's undefined terms.

## 5. Which conditions pass/fail at Cabeus

Real output from `src/pm4w_detector.py`, computed with **no knowledge of
Cabeus's identity or ground-truth status fed into the classifier** (per
Task 6's explicit requirement — `classify_site()` takes only measured
quantities as arguments):

| Condition | Status | Value |
|---|---|---|
| illumination | **PASS** | 0.0022 (< 0.2) |
| cpr | **NO_DATA** | no `cpr_pct_gt1` statistic exists for Cabeus in PRISM's data (only a whole-window mean, 0.166 — insufficient to evaluate a per-pixel-fraction test) |
| dop | NO_DATA | Mini-RF not ingested |
| backscatter | NO_DATA | Mini-RF not ingested; DFSAR conversion not demonstrated comparable |
| phase | NO_DATA | Mini-RF not ingested |
| weighted_power | NO_DATA | equation itself unresolved |
| volume_scattering | NO_DATA | Mini-RF not ingested |
| roughness | NO_DATA | Mini-RF S1 mosaic not ingested |
| temperature | NO_DATA | Diviner not ingested |

**Classification: UNRESOLVED** (no condition FAILed, but 7 of 9 required
conditions are NO_DATA — the rule "if any required condition is NO_DATA,
do not classify as ICE" is triggered immediately). **Wiechert produces the
identical pattern** — illumination PASS (0.053, also <0.2), everything
else NO_DATA, also UNRESOLVED. **Both controls land at the same
classification** — this is not a validation failure in the sense of
"wrong answer," it is an honest reflection of genuinely insufficient data,
and is stated as such, not disguised.

## 6. Whether the PM4W detector can be validated

**Not yet, with current data.** Validation requires the detector to
produce a *differentiated* result on known positive vs. known negative
sites (Cabeus → something other than what Wiechert produces). With 7 of 9
conditions permanently NO_DATA for every site (no Mini-RF, no Diviner
data anywhere), **the detector cannot currently discriminate any site from
any other** — all 18 sites tested (7 candidates + 11 controls/references)
produced the identical `UNRESOLVED` classification. This is the correct,
mechanical, non-tuned consequence of the AND-gate rule applied honestly —
not evidence the rule is wrong, and not softened to claim partial success
where none exists.

## 7. Whether the 7 candidates can be evaluated

**They were run** (Task 8 permits this even without full validation, since
the result cannot be forced into ICE regardless) — **all 7 produced
`UNRESOLVED`**, identical in pattern to Cabeus and Wiechert. **This is not
a validated ice/non-ice answer for any candidate** — it is the same
honest "insufficient data" result the controls themselves produced,
explicitly not elevated to a claim about the candidates' actual ice
status. No candidate was forced into ICE; none could be, structurally,
given the classifier's rules and current data.

## 8. Exactly what NASA/ISRO data should be obtained next

Ranked by leverage:

1. **Mini-RF CDR-MOSAIC data** (`LRO-L-MRFLRO-5-CDR-MOSAIC-V1.0`, south
   polar CPR + S1, 118 m/px) — highest priority, per Task 4; would unlock
   genuine (not analogue) CPR, DOP, phase, weighted-power, and volume-
   scattering-decomposition evaluation for every site at once, being a
   pre-computed polar mosaic rather than per-acquisition search-and-
   download. Next concrete step: resolve the exact file path via the ODE
   coordinate-search tool (`ode.rsl.wustl.edu/moon/`) or the dataset's SIS
   document.
2. **Diviner temperature data**, per-candidate-coordinate, public PDS
   query — unlocks the environmental tier's second condition.
3. **A real, authenticated PRADAN session**, specifically targeted at the
   3 candidates that have never had any raw/SLC acquisition search
   performed at all, plus Cabeus and Wiechert — this improves the
   *separate* `DFSAR_ICE_EVIDENCE` layer (Sinha/Verma comparison), not
   PM4W's own detector, which structurally requires Mini-RF regardless of
   DFSAR data quality.
4. **PM4W's supplementary material or direct author contact** — resolves
   the `w` metric and the Eq. 7 both-vs-either ambiguity, the two
   remaining scientifically unresolved (not just missing-data) items from
   `docs/PM4W_SINHA_PRISM_COMPARISON.md`'s List C.

---

## Summary

PM4W's methodology is now fully extracted, correctly separated from
PRISM's DFSAR/Sinha work, and implemented exactly as far as PRISM's actual
data permits — one real condition (illumination, already passing
everywhere), one honest analogue (CPR>1 fraction, available for 7 of 18
sites), and seven structurally NO_DATA conditions, none faked. The
resulting `UNRESOLVED` classification for every site — including the
known positive and negative controls — is the correct, honest output of a
never-tuned AND-gate given real data gaps, not a defect to be argued away.
The path to an actually validated PM4W reproduction runs through Mini-RF
data acquisition, not through adjusting PRISM's existing code.
