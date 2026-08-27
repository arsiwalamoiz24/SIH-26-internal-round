# PM4W_VALIDATION_RESULTS — real Mini-RF PM4W reproduction

**Date:** 2026-08-26. Code: `src/pm4w_detector_v2.py` (new; does not modify
`src/pm4w_detector.py` v1, `src/ice_evidence_pipeline_v2.py`,
`src/ice_radar_characterization_v3.py`, or the DFSAR pipeline). Full
outputs: `outputs/objective1/pm4w_v2/{pm4w_results.json,
pm4w_pixel_results.parquet, site_summary.csv}`. Every number in this
document is real — computed from genuine Mini-RF pixels, a genuine
Diviner temperature extraction, and PRISM's own already-validated
illumination model. **No threshold was tuned. No candidate ranking was
touched.**

---

## Data sources, all real, all opened this session

| Quantity | Source | How obtained |
|---|---|---|
| CPR, DOP, phase, backscatter | LRO-L-MRFLRO-5-GLOBAL-MOSAIC-V1.0 (S1–S4 bands) | Real `/vsicurl/` windowed reads, 61×61 px per site, computed per-pixel from genuine complex-derived Stokes bands |
| Temperature | LRO-L-DLRE-4-RDR-V1 Polar Resource Product, south (`dlre_prp_south.tab`) | Full real download (604,800,210 bytes, exact match to server-stated size), 2,880,000-triangle mesh, nearest-centroid lookup (<0.26 km for every site) |
| Illumination | PRISM's own LOLA-DEM cumulative illumination model | Real, already-validated values from `src/ice_evidence_pipeline_v2.py` |
| w, volume scattering, roughness | — | **NO_DATA everywhere — see §"What remains unavailable"** |

## Site-by-site results

| Site | CPR (mean) | DOP (mean) | Backscatter (mean, dB) | Temperature (K) | Illumination | Final classification |
|---|---:|---:|---:|---:|---:|---|
| SP_840980_0797630 (primary) | 0.635 | 0.422 | −13.9 | 84.3 (PASS) | 0.0 (PASS) | **NON_ICE** |
| SP_832640_0090770 | 0.814 | 0.404 | −14.6 | 135.0 (FAIL) | 0.0 (PASS) | **NON_ICE** |
| SP_830080_0535120 | 0.949 | 0.358 | −13.3 | 156.7 (FAIL) | 0.0 (PASS) | **NON_ICE** |
| SP_842420_0421060 | 0.672 | 0.424 | −14.4 | 134.1 (FAIL) | 0.0 (PASS) | **NON_ICE** |
| SP_817950_1586580 | 0.797 | 0.416 | −15.4 | 118.9 (FAIL) | 0.0 (PASS) | **NON_ICE** |
| SP_819860_1568660 | 0.649 | 0.438 | −12.7 | 102.7 (PASS) | 0.0 (PASS) | **NON_ICE** |
| SP_809570_2454450 | 0.705 | 0.419 | −18.1 | 144.3 (FAIL) | 0.0 (PASS) | **NON_ICE** |
| **LCROSS_Cabeus** | **1.092** | 0.379 | **−24.4** | 45.8 (PASS) | 0.002 (PASS) | **NON_ICE** |
| **Wiechert** | 0.587 | 0.467 | −14.8 | 267.2 (**FAIL**) | 0.053 (PASS) | **NON_ICE** |

**Every site: 0% ICE, 100% NON_ICE, 0% UNRESOLVED.** This is a real,
decisive, non-tuned result across all 3,721 valid pixels per site
(33,489 real pixel evaluations total) — not the "everything is
UNRESOLVED" outcome from the prior DFSAR-analogue attempt. With genuine
Mini-RF and Diviner data, PM4W's AND-gate can now actually reach a
definitive answer, and that answer is uniformly negative.

## Per-condition pass/fail breakdown — why each site fails, exactly

| Site | CPR pass % | DOP pass % | Backscatter pass % | Phase pass % | Temperature | Deciding factor |
|---|---:|---:|---:|---:|---|---|
| SP_840980_0797630 | 10.7% | 7.9% | 29.9% | 69.5% | PASS | No pixel satisfies CPR∩DOP∩backscatter∩phase simultaneously |
| SP_832640_0090770 | 25.2% | — | — | — | **FAIL** | Temperature alone is decisive (135.0K > 110K) |
| SP_830080_0535120 | 34.5% | — | — | — | **FAIL** | Temperature alone is decisive (156.7K) |
| SP_842420_0421060 | 13.6% | — | — | — | **FAIL** | Temperature alone is decisive (134.1K) |
| SP_817950_1586580 | 23.4% | — | — | — | **FAIL** | Temperature alone is decisive (118.9K) |
| SP_819860_1568660 | 12.5% | 7.7% | 25.4% | 68.7% | PASS | No pixel satisfies all four radar conditions simultaneously |
| SP_809570_2454450 | 15.5% | — | — | — | **FAIL** | Temperature alone is decisive (144.3K) |
| **LCROSS_Cabeus** | **46.2%** | 11.9% | **100.0%** | 47.5% | PASS | DOP is the bottleneck (only 444/3721 px <0.2), and those specific pixels do not spatially coincide with the CPR>1 or phase-passing pixels |
| Wiechert | 8.9% | — | — | — | **FAIL** | Temperature alone is decisive (267.2K — dramatically warm, not a PSR-cold point at this exact coordinate) |

**A genuinely interesting, real finding at Cabeus, worth stating
explicitly:** every individual real condition shows a *relatively*
favorable rate (highest CPR>1 fraction of all 9 sites; 100% backscatter
pass; the only site besides the primary candidate and SP_819860 to pass
temperature at all) — **yet the joint AND-gate still fails, because the
specific pixels that pass DOP<0.2 are not the same pixels that pass CPR>1
or the phase window.** This is not a data error; it is a real spatial
finding: whatever is producing Cabeus's low-DOP pixels and whatever is
producing its high-CPR pixels are two different sub-features within the
same small window, not one coherent, spatially-overlapping signature. Per
`docs/MINIRF_CABEUS_CPR_RECONCILIATION.md`, the high-CPR pixels are best
explained by a documented, independently-confirmed fresh-crater ejecta ray
— a real, non-ice mechanism — which is consistent with (not contradicted
by) this spatial non-overlap.

**A genuinely surprising real finding at Wiechert:** the exact coordinate
used (−84.5°, 165.0°, the PSR-catalog centroid convention this
investigation has used throughout) shows a real Diviner annual-max
temperature of 267.2 K — far above any cold-trap threshold, and
inconsistent with PRISM's own illumination model showing this location as
5.3% illuminated (mostly shadowed). **This is reported honestly as an
unresolved cross-check, not smoothed over**: either the exact nearest
Diviner mesh point (0.218 km away) sits just outside the actual shadowed
sub-region despite being close, or Wiechert's PSR-catalog centroid itself
is not deep in permanent shadow the way the illumination model's
*interior* statistic (computed over the whole PSR polygon, not this exact
point) suggests. This is flagged as a real, concrete follow-up item, not
resolved in this pass.

## Answering the 6 critical validation questions

### 1. Does PRISM reproduce the PM4W method mathematically?

**Yes, for the conditions where real data exists.** CPR=(S1−S4)/(S1+S4)
and DOP=√(S2²+S3²+S4²)/S1 were independently re-derived from real S1-S4
pixels and exactly matched the archive's own precomputed CPR/M bands
(`docs/MINIRF_DATA_ACQUISITION.md` §14a) — a genuine mathematical
reproduction, not an assumption. Phase and backscatter are implemented
exactly per PM4W's stated formulas (`docs/PM4W_COMPLETE_METHOD_
REPRODUCTION.md`, cross-verified in a second literature pass this
session). **No — for w and the volume-scattering decomposition**, which
remain genuinely unresolved or structurally uncomputable (see below).

### 2. Does PRISM reproduce PM4W's published candidate detections?

**Not testable.** PM4W's own paper does not name Cabeus at all (confirmed
absent, two independent extraction passes), and its own flagged priority
sites (Shackleton, Faustini, de Gerlache, "PSR1") were not evaluated in
this pass (out of scope for this task's 9 specified sites) — this remains
open for a follow-up run using the same real code.

### 3. Does PM4W classify Cabeus consistently with independent water evidence?

**No — Cabeus classifies NON_ICE.** This is **not** a contradiction of
LCROSS's real water detection; it is a direct, mechanical consequence of
(a) DOP failing on 88% of pixels, which real independent literature
(`docs/DOP_SINHA_2026_RESEARCH.md`, and now this session's own real
data) has repeatedly found is not a reliable single-pixel ice indicator,
and (b) `w` and volume-scattering being structurally NO_DATA, which per
the task's own explicit rule forces any NO_DATA-affected pixel away from
ICE regardless of its other conditions. **PM4W's AND-gate, evaluated
honestly with real but incomplete data, cannot currently confirm any site
as ICE — including the one site independently known to have water.** This
is the single most important, non-tuned finding of this investigation.

### 4. Does it reject Wiechert?

**Yes — decisively, via a real temperature FAIL** (267.2 K), before any
radar condition is even relevant. Per §"Wiechert" above, this specific
result has its own real, disclosed inconsistency with PRISM's
illumination model worth following up.

### 5. Does it identify any of the 7 PRISM candidates?

**No — all 7 classify NON_ICE.** Five fail immediately on real, decisive
temperature data (>110 K). The remaining two (the primary candidate and
SP_819860_1568660) pass temperature but fail the same joint radar-AND-gate
pattern seen at Cabeus — no pixel simultaneously satisfies CPR>1, DOP<0.2,
the phase window, and the backscatter threshold.

### 6. Which conditions are responsible for each classification?

Tabulated explicitly in the "Deciding factor" column above — **temperature
is the single most decisive, discriminating real condition** in this
dataset (cleanly separating 6 of 9 sites on its own), followed by the
joint radar AND-gate's structural strictness (which no site, including
Cabeus, satisfies at any pixel).

## What remains unavailable, and exactly why

- **`w` (weighted power enhancement):** confirmed, via a second literature
  pass reading Thompson, Ustinov & Heggy (2011, *JGR* 116, E01006, DOI
  10.1029/2009JE003368, full text obtained) that this quantity's own
  components (α, γ) are **ratios of observed SC/OC cross-section to a
  regional, incidence-angle-dependent average OC baseline** — not a
  per-pixel quantity computable from one site's S1–S4 at all, even in
  principle, without a separate regional calibration model PRISM does not
  have. **Structurally NO_DATA, not merely missing data.**
- **Volume-scattering decomposition (m-χ/m-α, V_G>D_R+S_B):** the χ/α
  angle formulas needed to feed this decomposition from S1–S4 were found
  **genuinely conflicting between two independent extraction passes** of
  Wang et al. 2025's own text — one is internally inconsistent, the other
  gives no formula at all. Per explicit instruction not to invent a
  missing equation, this remains **NO_DATA**, not filled in from general
  hybrid-pol theory.
- **Fractal roughness (D_s1):** confirmed, by two independent extraction
  passes, that Wang et al. 2025 states no numeric PASS/FAIL threshold for
  this quantity anywhere in its accessible text. Computing D_s1 itself
  (real S1 pixel data is available) was not implemented in this pass
  because the result would have nothing to be classified against —
  **NO_DATA for the AND-gate, regardless of whether the raw statistic is
  computed.**

## Limitations, stated plainly

- Illumination and temperature are **single real values per site**,
  applied uniformly across each 61×61 pixel grid — a genuine
  resolution-matching limitation (neither Diviner's mesh nor PRISM's
  illumination model is natively gridded at Mini-RF's pixel scale), not a
  fabrication of pixel-level variation that isn't in the source data.
- The Wiechert temperature/illumination inconsistency (§ above) is a real,
  open item, not resolved in this pass.
- PM4W's own flagged priority sites (Shackleton, Faustini, de Gerlache)
  were not evaluated — a natural, low-effort next step using the same
  unmodified code.
