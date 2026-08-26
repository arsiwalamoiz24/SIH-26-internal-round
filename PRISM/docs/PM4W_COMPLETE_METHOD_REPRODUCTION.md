# PM4W_COMPLETE_METHOD_REPRODUCTION — Wang et al. 2025 full method audit

**Date:** 2026-08-26. **Objective preserved: physics-based lunar water-ice
detection.** This document does not implement anything — it extracts PM4W's
complete published method and audits PRISM's current data/code against it,
component by component, per explicit task instruction.

**Source:** Wang, R., Feng, Y., Tong, X., Zhou, Y., Tang, P., Li, P., Dong,
Y., Xi, H., Xu, X., Wang, C., Jin, Y., Liu, S. (2025). "Shallow subsurface
water-ice distribution in the lunar south polar region: analysis based on
Mini-RF and multi-metrics." *Geo-spatial Information Science*. DOI:
10.1080/10095020.2025.2526678. **Access: full text obtained** (jina.ai
reader-proxy on tandfonline.com after a direct-fetch 403; treat as
PARAPHRASED-with-VERBATIM-quotes confidence — one notch below the cleaner
direct/PMC access achieved for Sinha 2026, Neish 2011, and Li 2018 earlier
in this investigation). No supplementary material was located.

**PM4W = "Polarimetric Method for Water-ice Detection."** A **hard AND-gate
classifier** (every tier must pass — not a weighted score), applied to LRO
Mini-RF Level-2 data (30 m/px) to identify shallow (1–3 m) subsurface
water-ice across 87°S–90°S.

---

## 1. Every PM4W component, full detail

### 1.1 Stokes parameters (Eq. 1)

1. **Variable names:** S1, S2, S3, S4.
2. **Equation:** standard Stokes construction from two receive channels.
3. **Physical meaning:** S1 = total intensity; S2 = H-minus-V power
   difference; S3 = real part of the H·V* cross term; S4 = imaginary part.
4. **Input data source:** Mini-RF Level 2 (radiometrically and
   polarization-corrected).
5. **Required polarization channels:** Mini-RF's own hybrid/compact-pol
   hardware — **verbatim**: "Emits left-hand circular polarization and
   receives orthogonal linear information in both horizontal and vertical
   polarization." This is a genuine **single-transmit (circular), dual-
   linear-receive** system — structurally the correct 2-component basis for
   a Stokes vector, by construction, not by a modeling choice.
6. **Spatial resolution:** 30 m/px.
7. **Window size:** not stated for the base Stokes construction itself
   (per-pixel).
8. **Calibration:** "radiometrically and polarization-corrected" (Level 2
   product-level calibration, not independently detailed further in the
   accessible text).
9–11. Not applicable to the raw Stokes construction itself.
12. Validation is reported at the combined-decision-rule level (§ below),
    not per intermediate Stokes parameter.

### 1.2 CPR — C (§3.2 of the extraction)

1. **Variable:** C.
2. **Equation:** `C = (S1 − S4)/(S1 + S4)`.
3. **Physical meaning:** circular polarization ratio, from a genuine
   circular-transmit hybrid-pol Stokes vector.
4–7. Same as §1.1 (derived from the same Stokes parameters).
8. Same as §1.1.
9. **Threshold: C > 1.**
10. **Decision rule:** one AND-term among five in the radar-metric tier.
11. **Empirical or theoretical?** The paper runs an explicit sensitivity
    analysis (their Fig. 13): CPR=1 is shown as a genuine inflection point
    where PSR-concentration and M3-consistency both peak and then decline
    for higher thresholds. **This reads as empirically justified** (chosen
    because it demonstrably produces the best PSR-concentrated,
    M3-consistent result), presented by the paper with physical framing but
    not derived from first principles independent of the data.
12. **Published validation:** 90%+ of C≥1 pixels fall inside PSRs (after
    the full multi-tier filter); M3 pixel-consistency peaks near CPR≈1
    (~70%) and declines toward CPR=1.2 (~30%).

### 1.3 Degree of polarization — m (§3.3)

1–8. Same Stokes basis as §1.1–1.2.
9. **Threshold: m < 0.2** (associated with volume scattering).
10. AND-term in the radar-metric tier.
11. Not explicitly separated from the CPR sensitivity analysis in the
    extracted text — likely the same empirical-with-physical-framing basis.
12. Same combined validation as §1.2.

### 1.4 Backscatter coefficient — σ°_LH (§3.4)

1. **Variable:** σ°_LH.
2. **Equation:** `σ°_LH = (S1 + S2)/2`.
3. **Physical meaning:** the LH (left-circular transmit, horizontal
   receive) backscatter power, in dB.
9. **Threshold: < −15 dB.**
10. AND-term.

### 1.5 Relative phase — δ (§3.5)

1. **Variable:** δ.
2. **Equation:** `δ = arctan(S4/S3)`.
9. **Threshold: 0°<δ<80° OR 100°<δ<180°.**
10. AND-term.

### 1.6 Weighted power enhancement — w (§3.6)

1. **Variable:** w.
2. **Equation:** `w = 0.12α + 0.88γ` — **α and γ are NOT fully resolved
   from the accessible text** (α is likely the m-α decomposition's own
   angle; γ is undefined in what was retrieved). **Marked UNRESOLVED, not
   guessed at.**
9. **Threshold: 0.5–1.0.**
10. AND-term.
11–12. Cannot be assessed until the equation itself is resolved.

### 1.7 Fractal-dimension terrain roughness — D_s1 (Eq. 4)

1. **Variable:** D_s1.
2. **Equation:** `D_s1 = log(N_r)/log(1/r)` (box-counting-style fractal
   dimension), via the "Triangular Prism Surface Area Method."
3. **Physical meaning, verbatim:** "includes both surface or subsurface
   electromagnetic scattering roughness" — explicitly designed as PM4W's
   direct mitigation for the CPR-vs-roughness ambiguity (Neish, Carter, Eke,
   Fa — all already established in this investigation).
4. **Input data source:** computed directly from the Mini-RF **S1
   (backscatter intensity) image itself**, not a separate DEM.
6. **Spatial resolution:** 30 m/px (matching Mini-RF).
7. **Window size: 9×9 pixels.**
9. No hard pass/fail threshold stated for D_s1 itself in the extracted
   text (used as a filter/mask, exact cutoff not resolved — needs
   re-verification if reproduced).
10. Filters out topographically/electromagnetically rough false positives.
11. Not resolved from this extraction pass.
12. Cited as the mechanism that raised PSR-concentration from ~20% (radar
    metrics alone) to ~90% (full multi-tier filter) — a real, quantified,
    reported improvement.

### 1.8 Environmental metrics — temperature and illumination

1. **Variables:** annual maximum temperature; annual average illumination.
4. **Input data source:** temperature from Diviner; illumination source
   not explicitly stated in the extracted text (presumably a
   LOLA-illumination model, consistent with the general literature already
   surveyed in this investigation).
6. Rescaled to 30 m to match Mini-RF.
9. **Thresholds: temperature < 110 K; illumination < 0.2.**
10. AND-terms in the environmental tier.
11. **Temperature threshold: physically derived** — matches the
    Vasavada/Watson-Murray-Brown ice-stability threshold already
    established elsewhere in this investigation (`LUNAR_SOUTH_POLE_ICE_
    VALIDATION_LITERATURE.md` §9), not something PM4W invented.

### 1.9 Polarimetric decomposition validation (Eqs. 5–7)

1. **Variables:** D_R (double-bounce), V_G (volume), S_B (single-bounce),
   computed via two alternative decompositions.
2. **m-χ decomposition (Eq. 5):**
   `D_R = √[m·S1·(1+sin2χ)/2]`, `V_G = √[S1·(1−m)]`,
   `S_B = √[m·S1·(1−sin2χ)/2]`.
   **m-α decomposition (Eq. 6):**
   `D_R = √[m·S1·(1−cos2α)/2]`, `V_G = √[S1·(1−m)]`,
   `S_B = √[m·S1·(1+cos2α)/2]`.
3. **Physical meaning:** standard hybrid-pol scattering-mechanism
   decomposition — separates the same total power into double-bounce,
   volume, and single-bounce contributions.
9. **Decision rule (Eq. 7): `V_G > D_R + S_B`** — volume scattering must
   strictly dominate the sum of the other two mechanisms, a falsifiable
   ordering condition, not a magnitude threshold on one term alone.
10. **AMBIGUOUS whether both decomposition variants must independently
    satisfy Eq. 7, or either suffices** — not resolved in this extraction,
    flagged for a targeted follow-up read if this specific detail matters.
11. Physically derived (standard decomposition theory), the ordering
    condition itself is a theoretical volume-scattering signature, not an
    empirical fit.
12. **Verbatim-flagged quote:** "The intensity of the V_G component at the
    water-ice point (>0.2) is significantly larger than those of the D_R
    and S_B components (<0.1)" — presented as confirming the
    theoretically-predicted signature at their detected pixels.

## 2. Full decision rule

**Sequential AND-gate across three tiers — ALL must pass:**
1. Radar: `C>1 AND m<0.2 AND σ°_LH<−15dB AND (0°<δ<80° OR 100°<δ<180°) AND 0.5≤w≤1.0`
2. Decomposition: `V_G > D_R + S_B`
3. Topographic/environmental: fractal-roughness filter AND `T<110K` AND `illumination<0.2`

**This is categorically different in kind from every PRISM scoring
mechanism to date** — v1's continuous percentile composite, V2's tiered
evidence hierarchy, and V3's characterization vector are all either
continuous scores or ordinal classifications; none is a hard multi-term
AND-gate on a single pixel.

## 3. PM4W's own validation and stated limitations

- 1,578 pixels (30m each) classified ice; 91% inside 29 catalogued PSRs.
- Radar tier alone: only ~20% inside PSRs; full multi-tier filter: ~90% —
  the paper's own central evidence that multi-metric fusion is necessary.
- Vs. M3 (1500m fuzzy buffer): 60% pixel consistency, only **11% area
  consistency** — a large, honestly-reported gap, attributed to M3's
  coarser resolution, positional accuracy, and shallower (surface-only,
  not 1–3m subsurface) sensitivity.
- **Shackleton PSR: best M3 agreement (62% pixel / 29% area)** — flagged by
  the paper as "a promising site for future on-site water-ice detection."
  Faustini, de Gerlache, and an internal "PSR1" also flagged for follow-up.
- Cabeus is **not singled out by name** in the extracted results — this
  extraction pass could not confirm a Cabeus-specific PM4W number either
  way; flagged as an open item, not assumed absent or present.
- Own limitations, verbatim-flagged: spatial filtering trades resolution
  for noise reduction; elevated CPR/low-m on crater walls "could be
  attributed not only to water-ice but also to Double-bounce Scattering
  effects, and wavelength-scale rock effects" (the same roughness ambiguity
  this whole investigation has tracked); available terrain products (≥20m)
  are "insufficient to accurately calculate the terrain slope at the
  Mini-RF wavelength scale (12.6 cm)" — an explicit, quantified
  scale-mismatch admission; local incidence angle on crater walls
  "very directly" influences CPR, without a described correction method.

## 4. PRISM comparison table

| PM4W component | Exact method | PRISM equivalent | Available? | Missing requirement |
|---|---|---|---|---|
| Stokes S1–S4 | Single-transmit (LH circular), dual-linear-receive Mini-RF hardware | DOP work uses quad-pol HH/VV (wrong basis) or, per `ice_radar_characterization_v3.py`, HH/HV or VH/VV (linear-transmit dual-receive — structurally analogous but from a **linear**, not circular, transmit — a physically different hybrid basis, not a drop-in equivalent) | **Partial** — real raw-channel access exists for exactly 2 non-candidate DFSAR acquisitions only | No Mini-RF data ingested by PRISM at all; DFSAR quad-pol is architecturally a different instrument than Mini-RF hybrid-pol |
| CPR `(S1−S4)/(S1+S4)` | Per-pixel, threshold C>1 | PRISM's "CPR" for every candidate/Cabeus/Wiechert is the **ISRO L3C-MOSAIC precomputed band** — formula never verified against this or any published construction | **E** (ISRO precomputed, not raw pixels) for all mosaic sites; PRISM DOES already record **per-pixel `cpr_pct_gt1_inside`** (fraction of interior pixels with CPR>1) for all 7 candidates — a genuinely reusable, already-computed proxy for PM4W's tier-1 CPR test | Formula-level verification against Neish/PM4W's Stokes construction — impossible without raw DFSAR pixels at candidate sites |
| DOP `√(S2²+S3²+S4²)/S1` | Per-pixel, threshold m<0.2 | PRISM's DOP (quad-pol HH/VV basis) never approaches <0.2 (consistently 0.63–0.86, `DOP_SINHA_2026_RESEARCH.md`); even the physically-correct (HH,HV)/(VH,VV) bases tested in V3 gave **0.90–0.93 — HIGHER, not lower** | **B** — different equation basis, and fixing the basis does not resolve the gap | A genuinely different instrument architecture (circular-transmit hybrid-pol) may be required, not just a basis fix within DFSAR |
| Backscatter σ°_LH < −15dB | Per-pixel dB threshold | PRISM has real Y4R total-power bands (evn+vol+odd+hlx, linear scale) that could in principle be converted to dB (`10·log10`, per `PROJECT_GUIDE.md`'s own documented convention) | **C/D border** — theoretically computable from data PRISM already has, but never done, and Mini-RF's LH-specific dB convention isn't directly reproducible from DFSAR's different channel set | Needs an explicit calibration/conversion step never implemented; not equivalent to Mini-RF's own radiometric scale without independent verification |
| Relative phase δ = arctan(S4/S3) | Per-pixel | Requires the same raw complex S3,S4 as CPR/DOP | **D** for candidates (no raw pixel access); computable in principle for the 2 non-candidate raw acquisitions PRISM can already decode | Raw pixel access at candidate sites |
| Weighted power w | Per-pixel, 0.5–1.0 | Not implemented, and the equation itself is unresolved from this extraction | **C** — scientifically unresolved (both the paper's own definition and PRISM's ability to reproduce it) | A cleaner primary-source read of PM4W's α/γ definitions |
| Fractal roughness D_s1 (9×9, on S1) | Radar-intensity-domain roughness | PRISM's roughness is **DEM-derived RMS elevation variance** (`terrain_algorithms.compute_roughness_rms`) — a genuinely different metric, different domain (topography, not radar backscatter texture) | **B** — PRISM has *a* roughness concept, but a categorically different equation | Would require computing fractal dimension directly on DFSAR backscatter imagery, never done |
| Temperature < 110 K | Diviner, per-pixel | **No per-candidate/per-Cabeus/per-Wiechert Diviner temperature data has been ingested anywhere in PRISM**, confirmed repeatedly (`LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md` §9) | **D** | A direct PDS/Diviner archive query per candidate coordinate — never attempted |
| Illumination < 0.2 | LOLA-illumination-model-derived, per-pixel | **PRISM already computes this, for real, for all 7 candidates + Cabeus + Wiechert + 9 held-out sites** (`terrain_algorithms.compute_cumulative_illumination`) — and **every site tested already falls well under 0.2** (illumination fractions ranged 0.0–0.126 across the full 18-site set in `ice_evidence_pipeline_v2.py`'s real output) | **A — already available and already passing** | None — this is a genuine, ready-to-use PRISM capability that directly matches a PM4W tier |
| m-χ / m-α decomposition, V_G>D_R+S_B | Per-pixel, from the same Stokes basis | Not implemented anywhere in PRISM | **D** for candidates (needs raw pixels); theoretically extendable to the 2 non-candidate raw acquisitions PRISM can already decode, using code very similar to `ice_radar_characterization_v3.py`'s existing `stokes_parameters()` function | Raw pixel access at candidate sites; the decomposition math itself is straightforward to add once real S1–S4 exist |
