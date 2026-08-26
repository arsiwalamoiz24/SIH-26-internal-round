# PM4W_DATA_REQUIREMENTS — data availability map

**Date:** 2026-08-26. Companion to `docs/PM4W_COMPLETE_METHOD_
REPRODUCTION.md`'s equation-level audit; this document is the condition-
by-condition data-availability map underlying `src/pm4w_detector.py`.

| Condition | PM4W required quantity | Required instrument | Required product | PRISM equivalent | Spatial resolution | Available? | Scientifically comparable? | Missing data |
|---|---|---|---|---|---|---|---|---|
| Illumination | Annual average illumination < 0.2 | LOLA (illumination model) | Not stated by PM4W's own paper | `terrain_algorithms.compute_cumulative_illumination` — real, independently implemented cumulative ray-cast model | 20 m/px (PRISM's DEM) vs. PM4W's 30 m | **Yes — already computed for all 18 sites tested** | **ANALOGUE** — same physical concept (LOLA-DEM cumulative sun-position model), not verified formula-identical to PM4W's own illumination product | None — usable now |
| CPR (Stokes) | Per-pixel `(S1−S4)/(S1+S4) > 1` from Mini-RF hybrid-pol Stokes | Mini-RF | Level 2 (radiometrically/polarization-corrected) | **None ingested** — PRISM's "CPR" is the ISRO L3C-MOSAIC DFSAR band (undocumented formula) | Mini-RF: 30 m/px native, mosaics at 118 m or ~950 m (256/32 PPD) | **No genuine Stokes CPR anywhere in PRISM** | **NOT_COMPARABLE** as a formula match; PRISM's existing CPR>1-pixel-fraction is reported as an explicit **ANALOGUE** only | Real Mini-RF Level 2 or CDR-MOSAIC data (§ Mini-RF section below) |
| DOP | `m=√(S2²+S3²+S4²)/S1 < 0.2`, same Mini-RF Stokes basis | Mini-RF | Level 2 | DFSAR-derived DOP exists for 4/7 candidates, but on a **different instrument, different (linear-transmit) basis** | — | **No** — DFSAR DOP is not a substitute | **NOT_COMPARABLE** | Real Mini-RF data |
| Backscatter σ°_LH | `(S1+S2)/2 < −15 dB` | Mini-RF | Level 2 | PRISM's Y4R total power (linear scale) is theoretically dB-convertible | 25 m/px (DFSAR mosaic) | **Not implemented** — conversion never demonstrated physically comparable to Mini-RF's own LH radiometric scale | **NOT_COMPARABLE until demonstrated** | A calibration/comparability study, not yet attempted |
| Relative phase δ | `arctan(S4/S3)`, Mini-RF Stokes basis | Mini-RF | Level 2 (complex, phase-preserving) | None | — | **No** | **NOT_COMPARABLE** | Real Mini-RF complex data |
| Weighted power w | `0.12α+0.88γ`, 0.5–1.0 | Mini-RF | Level 2 (decomposition-derived) | None | — | **No — and the equation itself is unresolved from the source paper** | N/A | PM4W's supplementary material or author contact |
| Volume-scattering decomposition (V_G>D_R+S_B) | m-χ / m-α decomposition, Mini-RF Stokes | Mini-RF | Level 2 | None | — | **No** | **NOT_COMPARABLE** | Real Mini-RF complex data |
| Fractal roughness D_s1 | 9×9-window fractal dimension on **radar backscatter intensity** (not DEM) | Mini-RF S1 mosaic | Level 3 mosaic (S1) | PRISM's roughness is DEM-elevation RMS — a **different metric, different domain** | Mini-RF S1 mosaic: 118 m (256 PPD) | **No** | **NOT_COMPARABLE** (different physical domain entirely) | Real Mini-RF S1 mosaic + new fractal-dimension code |
| Temperature < 110K | Diviner annual maximum temperature | Diviner | Not stated (product-level) | **None ingested anywhere in PRISM**, confirmed repeatedly | ~200 m/px (Diviner, public) | **No** | N/A | A Diviner ingestion pipeline, per-candidate-coordinate query — never attempted |

## Mini-RF — the highest-priority data source (Task 4)

**A specific, real, public NASA PDS dataset was identified and verified
this session:** `LRO-L-MRFLRO-5-CDR-MOSAIC-V1.0` — the Level-3 Mini-RF
polar mosaic dataset, hosted at `pds-geosciences.wustl.edu`. Confirmed via
two independent search passes:

- **Two mosaic products exist per pole** (north ≥80°, south ≤−80°): one
  from **CPR** data, one from **Stokes S1** data.
- **Two resolutions available: 32 PPD (~950 m/px) and 256 PPD (~118 m/px)**
  — the 118 m figure independently corroborates the same number found via
  a separate search earlier in this investigation
  (`LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md` §26).
- Stored under a `DATA/SAR/MOSAICS` directory structure, each file
  accompanied by a detached PDS label and a JPEG browse image (per the
  dataset's own SIS documentation, confirmed by search).
- **Public NASA PDS Geosciences Node — no login requirement found anywhere**
  in this investigation, unlike ISRO's login-gated PRADAN portal.
- A **coordinate-based search tool exists**: the Lunar Orbital Data
  Explorer (`ode.rsl.wustl.edu/moon/`), explicitly designed for this
  purpose.

**Coverage relative to PRISM's sites of interest:** the south-polar mosaic
is stated to cover **all latitudes south of −80°**. PRISM's 7 candidates
span −80.957° to −84.242°; LCROSS Cabeus is at −84.68°; Wiechert is at
−84.5°. **All 9 sites of interest fall within this stated coverage zone**
— a genuinely positive, verified finding (unlike DFSAR, where 3 of the 7
candidates have never even had a covering raw acquisition searched for,
and Cabeus/Wiechert have none identified at all).

**What was NOT achieved this session, stated honestly:** the exact
downloadable file URL/path for the south-polar CPR and S1 mosaic files was
**not** pinned down within this session's time budget — two direct-fetch
attempts at plausible directory paths returned 404 or an incomplete
listing. **This is a concrete, bounded next step** (navigate the ODE
coordinate-search tool or the dataset's own SIS document to the exact
filename), not a fundamental blocker — the dataset's existence, coverage,
resolution, and public accessibility are all independently confirmed.

**A directly relevant, Cabeus-specific finding surfaced during this
search, not previously known to this investigation:** a 2023 DPS
(Division for Planetary Sciences) conference abstract, "LRO Mini-RF
Bistatic Observations of Cabeus Crater Revisited" (ADS:
2023DPS....5510108P — **conference abstract, not a peer-reviewed journal
article; lower confidence than the Neish 2011 journal paper**), reports
that Mini-RF S-band bistatic radar shows a real "opposition response" at
Cabeus's floor distinct from nearby craters, but **not** in X/C-band —
interpreted as consistent with water ice buried below ~0.5 m of regolith
that does not itself produce a normal CPR radar-detectable signature. This
is directionally consistent with, and adds specific mechanistic detail to,
Neish et al. 2011's already-confirmed low-CPR-at-Cabeus finding.

**Data still needed at Wiechert and the 7 candidates specifically:** even
with the mosaic dataset identified, actual per-pixel coverage, quality
flags, and real values for these exact coordinates have **not** been
extracted in this session — the mosaic's existence and stated coverage
zone is confirmed, but individual-site pixel values are not yet in hand.
