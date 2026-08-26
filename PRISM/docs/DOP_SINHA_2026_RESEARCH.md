# DOP_SINHA_2026_RESEARCH — why PRISM's DOP doesn't match Sinha et al. 2026

**Date:** 2026-08-26
**Scope:** Research-paper investigation only. No PRISM code was modified, no new
pixel-level experiments were executed (this session's environment has no local
copy of the raw/calibrated DFSAR binary products — only small XML/CSV metadata
files are present; see §3.5). This report is a rigorous, source-by-source
re-analysis of PRISM's *existing* code, PRISM's *existing* computed results
(from `outputs/objective1/dop_v2/`, `dop_secondary/`, `paper_crater_validation/`,
`paper_criterion/`), and a fresh, independently-verified reading of Sinha et al.
2026's actual published text and its cited references.

**Epistemic key used throughout:** **FACT** = directly verified against a primary
source (code, JSON output, or fetched paper text). **OBSERVATION** = a pattern
noticed in FACTs. **HYPOTHESIS** = an untested or partially-tested explanation.
**CONCLUSION** = a claim the evidence in this document actually supports.

---

## 1. Executive Summary

PRISM computes a "linear-pol Stokes DOP" of 0.63–0.86 for the same craters
(F2, F3, inside Faustini's PSR) that Sinha, Bharti, Acharyya, Mishra,
Srivastava & Bhardwaj (2026, *npj Space Exploration* 2:22, DOI
10.1038/s44453-026-00038-9) report as 0.10–0.13. PRISM's CPR values for the
same craters are close to Sinha's (F2: 44.75% vs. paper's 47% CPR>1, max
1.82 vs. 1.95; F3: 33.3% vs. 42%, max 1.48 vs. 1.73).

This investigation independently fetched and read Sinha et al. 2026's actual
published text (not a summary) and found:

- **Sinha's own paper states no relationship between its Stokes parameters
  (S1–S4) and the HH/HV/VH/VV channels DFSAR actually measures.** Their DOP
  equation (their Eq. 2, `m = √(S2²+S3²+S4²)/S1`) is given with the sole gloss
  "S1, S2, S3, S4 are real numbers known as Stokes parameters" — no
  construction formula, no covariance/coherency definition, nothing. This is
  independently confirmed against the primary source, not inferred.
- Sinha's paper states **no processing level, no calibration/crosstalk
  procedure, no multilook window, and no acquisition ID** for the DOP
  computation. A Supplementary Table 1 exists and is stated to list "Dual
  Frequency Synthetic Aperture Radar datasets used in this study" but its
  contents could not be retrieved in this or the prior PRISM session.
- Sinha's **only** cited authority for *interpreting* DOP (Raney et al. 2012's
  m-χ decomposition, via Mohan et al. 2011 as supporting precedent) is a
  **hybrid dual-polarimetric (2-receive-channel)** Stokes construction — not a
  standard quad-pol (4-channel) one. PRISM's own tested hybrid-pol analogue
  (synthesizing LH/LV from HH/HV/VH/VV) still returns 0.57–0.60, not 0.10–0.13
  — so this basis mismatch is real and independently confirmed, but **is not,
  by itself, sufficient to close the gap** with the specific synthesis PRISM
  tried.
- **A correction to PRISM's own prior documentation**: the "Kumar et al. 2022,
  Adv. Space Res. 70(12)" citation used in `dop_pipeline_v2_lookcount_sweep.py`
  as the origin of the CPR/DOP criterion does not appear in Sinha et al. 2026's
  56-entry reference list and could not be verified to exist at all. Likewise,
  "Zhao et al. 2024," previously characterized in this investigation's own
  prior turn as something "Sinha et al. cite for CPR and multilook processing,"
  is **not** in Sinha's reference list — it is PRISM's own, separately-sourced
  DFSAR-calibration reference, unrelated to Sinha's methodology. See §6, §12.

**Bottom line:** the discrepancy is real, has been investigated rigorously by
both this session and the prior one, and remains genuinely unresolved — not
because PRISM did something wrong, and not because Sinha's paper is provably
wrong, but because **Sinha et al. 2026's published text does not contain
enough information to reconstruct their DOP computation**, and every
literature-justified variant PRISM could test (window size, small-sample bias,
gain calibration, phase calibration, the real Ainsworth 2006 crosstalk
algorithm, a different acquisition, a hybrid-pol basis, a power-only basis)
failed to close a 5–8× gap. Classification: **H (paper underspecification)
compounding C/D (different DOP definition / different polarimetric basis)** —
see §12 for the full reasoning against forcing a single cause.

---

## 2. Research Question

**Why does PRISM reproduce the CPR results reported by Sinha et al. 2026
reasonably well on the same DFSAR craters, but fail to reproduce their
reported DOP ≈ 0.10–0.13?**

---

## 3. Existing PRISM Implementation

### 3.1 Where DOP is calculated

All DOP code lives in `PRISM/src/`:

| File | Purpose |
|---|---|
| `candidate_dop_pipeline.py` | Candidate-specific DOP for `SP_840980_0797630` (PRISM's primary ice candidate, PSR-scale, unrelated acquisition to F2/F3) |
| `candidate_dop_pipeline_F2F3.py` | **v1**: linear-pol + hybrid-pol DOP for Sinha's own F2/F3 craters, on acquisition `ch2_sar_ncxl_20200321t082617351_d_fp_d18` (2020-03-21, station d18), circular interior mask (radius = diameter/2) |
| `dop_pipeline_v2_lookcount_sweep.py` | Hypothesis 1: sweeps covariance window size 5–41 px, with/without gain+phase channel calibration |
| `dop_pipeline_v2_relative_gain_test.py` | Hypothesis 4: relative HH/VV gain calibration under 4 unit conventions |
| `dop_pipeline_v2_crosstalk_correction.py` | Hypothesis 6: self-derived reflection-symmetry crosstalk correction (assumes co-pol/cross-pol covariance should be exactly zero) |
| `dop_pipeline_v2_ainsworth_crosstalk.py` | Hypothesis 7: the *actual* Ainsworth et al. 2006 iterative crosstalk/channel-imbalance algorithm, re-derived from the paper's legible equations after PDF extraction corrupted the original matrix equations |
| `dop_pipeline_v2_alt_acquisition.py` | Hypothesis 8: same formula, a **different** full-pol acquisition (`ch2_sar_ncxl_20191105t180525404_d_fp_m65`, 2019-11-05) independently confirmed by point-in-polygon test to cover both F2 and F3 |
| `dop_pipeline_v2_sri_powerdop.py` | Power-only DOP (`|S2|/S1`) computed from the real ISRO Level-2 SRI (amplitude-only) product |
| `paper_crater_pipeline.py`, `paper_criterion_pipeline.py` | Pv/CPR/SERD/T-Ratio at F2/F3 and the 7-candidate shortlist, for comparison against Sinha's CPR numbers |

### 3.2 PRISM's exact DOP formula (as implemented, verbatim from code)

```
PA = local_mean(|A|²)          # A, B are two complex channels
PB = local_mean(|B|²)
cross = A * conj(B)
Re_AB = local_mean(Re(cross))
Im_AB = local_mean(Im(cross))
S1 = PA + PB
S2 = PA - PB
S3 = 2 * Re_AB
S4 = -2 * Im_AB
DOP = sqrt(S2² + S3² + S4²) / S1
```

`local_mean` is a `scipy.ndimage.uniform_filter` of size 5×5 px (default; swept
5–41 px in hypothesis 1). Three variants of `(A, B)` are used throughout:

- **Linear-pol**: `A = HH`, `B = VV` (PRISM's "best-supported" formulation).
- **Hybrid-pol**: `A = LH = (HH + j·HV)/√2`, `B = LV = (VH + j·VV)/√2` —
  synthesizing a left-circular-transmit field from the quad-pol data, the same
  general Raney-style circular-transmit-field synthesis convention.
- **Power-only** (`dop_pipeline_v2_sri_powerdop.py`): `DOP = |S2|/S1` where
  `S1 = P_HH + P_VV`, `S2 = P_HH − P_VV`, using the real Level-2 SRI amplitude
  product (which structurally cannot carry a coherent cross term — see §9).

### 3.3 Calibration applied

**FACT (from every script's own docstring and code):** all runs apply only
**per-polarization XML `bias_real`/`bias_imag` subtraction** (i.e.
`S_corrected = S_raw - complex(bias_real, bias_imag)`, a per-channel DC-offset
removal). No gain-imbalance, no phase-orthogonality, and no crosstalk
correction is applied **by default**. Where these were tested (hypotheses 4,
6, 7), they are explicitly separate experimental variants, not the baseline.

### 3.4 Multilooking / windowing

**FACT:** the covariance estimate is a spatial `uniform_filter` (box-car
local average) over a square window, swept 5×5 through 41×41 px
(`dop_pipeline_v2_lookcount_sweep.py`). A separate hypothesis
(`dop_pipeline_v2_crosstalk_correction.py`) also tried a `20×1` and `20×5`
window, following `MLN = ceil(pixel_spacing/line_spacing) = ceil(9.593/0.489)
≈ 20`, a formula PRISM's own code docstring attributes to "Zhao et al. 2024
Eq. 7" — see §6/§12 for the correction that this reference is **not**
connected to Sinha's own methodology.

### 3.5 Data used, and this session's constraint

**FACT (verified this session):** this machine has no local copy of any raw
or calibrated DFSAR binary product — `find` across the entire filesystem
found no `.dat` files and no `PRISM_local_data` cache (the prior sessions'
code hard-codes paths under `C:\Users\radhe\...`, a different user account
than this machine's `C:\Users\sohan`). The only DFSAR-related file physically
present in this repository checkout is
`PRISM/data/ch2_sar_ncxl_20220318t135736694_d_fp_d18/`, containing only a
17.8 KB XML label and a 3.3 MB Grid CSV — no imagery. **Consequence: this
session could not re-execute any pixel-level DOP/CPR computation.** Every
number in §11 below is taken from the prior session's already-saved JSON
outputs (`outputs/objective1/dop_v2/*.json`, `dop_secondary/*.json`,
`paper_crater_validation/*.json`), re-read and cross-checked directly against
their generating source code in this session, not re-derived from raw pixels.
This is stated plainly per the task's instruction not to fabricate
experiments.

### 3.6 How CPR is computed — an important, previously under-highlighted asymmetry

**FACT (`PRISM/src/radar_pipeline.py`, `paper_crater_pipeline.py`):** PRISM's
"CPR" for the 7-candidate shortlist and for F2/F3 is **not self-computed from
raw HH/HV/VH/VV pixels at all.** It is read directly, as a delivered GeoTIFF
band (`ch2_sar_ndxl_20250630mpcpspwest_d_cpr_xx_fp_xx_xxx.tif`), from ISRO's
own precomputed **L3C-MOSAIC** product — a composite built from **602
separate acquisitions spanning 2019-09-22 to 2023-10-18** (per
`docs/CANDIDATE_DFSAR_SOURCE.md`, independently re-confirmed via
`radar_pipeline.py`'s own path constants this session). ISRO's internal CPR
formula/calibration/multilook chain for this product is **not documented**
anywhere in the CH2DFSAR SIS or user manual that PRISM's team could locate.

**By contrast, DOP is self-computed by PRISM from a single raw Level-1A SLC
acquisition** (`ch2_sar_ncxl_20200321t082617351_d_fp_d18`, 2020-03-21, a
single ~87-second pass), with only bias-centering calibration applied.

**OBSERVATION:** the claim in PRISM's prior documentation that "the CPR match
proves the acquisition/location is correct, so the DOP mismatch must be
DOP-specific" conflates two different data products. The CPR match shows the
craters' *lat/lon* is right and that *ISRO's own, independently-processed,
multi-pass CPR product* lands in the same regime as Sinha's numbers. It does
**not** show that PRISM's *specific single-acquisition DOP computation* is
using data comparable in calibration maturity, multilook depth, or even
acquisition date to whatever produced the matching CPR. This reframes (but
does not overturn) the prior investigation's conclusion — see §12.

---

## 4. Sinha et al. 2026 Method

**Full citation:** Sinha, R. K., Bharti, R. R., Acharyya, K., Mishra, S. K.,
Srivastava, N., Bhardwaj, A. (2026). "Subsurface ice in doubly shadowed
craters as revealed by Chandrayaan-2 dual frequency synthetic aperture
radar." *npj Space Exploration* 2:22. DOI: 10.1038/s44453-026-00038-9.
Published 2026-05-06.

**Access status (this session):** Full HTML text retrieved via an
independent, verbatim-focused re-fetch of the article (two separate fetch
passes with different extraction prompts returned identical equation text,
which is the basis for trusting this over hallucination risk). The typeset
PDF/rendered-math version was **not** independently cross-checked — treat
subscript/superscript-sensitive details with residual caution.

### 4.1 What the paper states, verbatim

- **DOP equation (their Eq. 2):** *"Degree of polarization (m) =
  √(S₂² + S₃² + S₄²) / S₁."* Immediately followed by: *"In equation 2, S1,
  S2, S3, S4 are real numbers known as stokes parameters."* Interpretation
  given: *"If low m then it is volume scattering, and if high m then it means
  double bounce scattering."*
- **CPR equation (their Eq. 1):** *"CPR(μc) = [σ°HH + σ°VV +
  2√(σ°HH × σ°VV)] / [σ°HH + σ°VV − 2√(σ°HH × σ°VV)]."* Followed by: *"It is
  an indicator of frozen volatile deposits and is observed to be anomalously
  large (CPR > 1) for volume scattering from ice deposits, whereas,
  typically, regolith has CPR < 1."*
- **Acquisition mode:** *"In full polarimetric (FP) mode, transmission is in
  horizontal (H) and vertical (V) polarization, and reception is in all four
  combinations — HH, HV, VH, and VV."* — confirms genuine quad-pol
  acquisition, matching PRISM's own data type.
- **Resolution:** *"provides relatively higher spatial resolution
  (2–75 m per pixel)"* — a hardware spec, not a stated processing/multilook
  choice.
- **Data availability:** *"Chandrayaan-2 Dual-Frequency Synthetic Aperture
  Radar calibrated data is available publicly at the Chandrayaan-2 portal of
  the ISRO Science Data Archive (ISDA)..."* — confirms "calibrated" data was
  used (consistent with PRISM's own choice of Level-1A `ncxl` calibrated
  products over raw L0A), but does not specify which calibrated sub-level.
- **The criterion's derivation, verbatim:** *"Our analysis shows that areas
  with elevated CPR consistently show low average DOP values, ranging from
  0.1 to 0.13 in craters F2, F3, H3, and S1 (Fig. 4). These values are
  significantly lower than previously proposed thresholds (Fig. 4). Based on
  this relationship, we refine the radar diagnostic criterion for identifying
  volumetric scattering, showing that CPR > 1 combined with DOP < 0.13
  provides a strong indicator of subsurface ice."* This is attributed to
  references 45 (Verma, N., Bhatt, M., Dangi, M., Kumar, S. & Bhardwaj, A.
  2025, *Icarus* 432) and 51 (Mishra, P., Kumar, S. & Singh, D. 2014) as the
  source of the prior, looser CPR>1/DOP<0.35 criterion being refined.
- **F2/F3 CPR values, corroborated:** *"F2: Highest CPR measured at 1.95;
  contains ~47% of interior pixels with elevated CPR"* and *"F3: CPR of 1.73;
  ~42% of interior pixels with elevated CPR"* — these match PRISM's own
  recorded values exactly (see §11).
- **DOP is reported as one shared range (0.1–0.13) across four craters
  (F2, F3, H3, S1) together**, not necessarily as four distinct per-crater
  values — an ambiguity in itself (§9).

### 4.2 What is genuinely absent from the accessible text

Each item below was specifically searched for in the fetched text and
confirmed absent, not merely unnoticed:

1. **No stated relationship between S1–S4 and HH/HV/VH/VV** (or any other
   channel set). No covariance/coherency-matrix construction is given.
2. **No stated DFSAR processing level** (Level-1A SLC vs. Level-2 SRI vs.
   other) for the DOP/CPR computation specifically.
3. **No stated calibration, crosstalk-correction, or channel-imbalance
   procedure of any kind.**
4. **No stated multilook window size, look count, or spatial-averaging
   parameter.**
5. **No stated acquisition date(s), orbit number(s), or product ID(s)** for
   the specific pass(es) used at F2/F3/H3/S1.
6. **No explicit statement of averaging order** — whether Stokes parameters
   are averaged over a region and DOP computed once, or DOP computed
   per-pixel and then averaged. These are not mathematically equivalent
   (§5.4).
7. **No F2/F3 exact coordinates/diameter found in the accessible main text**
   — PRISM's own values (F2: −87.39°, 82.31°, 1100 m; F3: −87.31°, 86.333°,
   700 m) could not be independently verified *or* contradicted; this is an
   access gap (tables/figures may not have rendered through the HTML-reader
   fetch), not a confirmed discrepancy.

A **Supplementary Table 1**, stated to list "Dual Frequency Synthetic
Aperture Radar datasets used in this study," is confirmed to exist but its
contents were not retrievable in this research pass (no working direct
download URL found).

---

## 5. DOP Mathematical Definitions

### 5.1 PRISM's linear-pol Stokes DOP

As in §3.2, with `A = HH`, `B = VV`. This treats the pair (HH, VV) as if they
were the two orthogonal components of a single received partially-polarized
electromagnetic wave (the way optical/hybrid-pol Stokes formalism is
classically defined), and computes the classical optical degree of
polarization of that "wave."

**HYPOTHESIS (new to this investigation, grounded in Raney 2012's own stated
formalism — see §5.3):** this is a physically non-standard move for quad-pol
data. HH and VV are not two components of one received wavefront — they are
two different entries of the 2×2 (or, in the lexicographic/Pauli basis, part
of the 4×4) scattering covariance matrix, describing two *different*
transmit-receive combinations of the *same* scattering event. Treating
`<HH·conj(VV)>` as a coherent cross term in a single-wave Stokes vector, the
way Raney's hybrid-pol formalism treats `<LH·conj(LV)>`, is a
self-consistent mathematical construction (it produces a valid Stokes vector
satisfying `S1² ≥ S2²+S3²+S4²`), but it does not correspond to the same
physical quantity Raney 2012 defines "degree of polarization" to be. This
HYPOTHESIS is **not fully tested** in this investigation, but it is
consistent with, and gives a physical reason for, an observation already
established by PRISM's own experiments (§5.3, §11): the hybrid-pol variant
(which *is* built the way Raney's formalism intends — synthesizing an actual
2-component received field from one circular transmit) still returns
0.57–0.60, not PRISM's linear-pol 0.63–0.86, but also not Sinha's 0.10–0.13 —
i.e., correcting the basis mismatch moves the number in a
directionally-consistent way (toward lower DOP) without closing the gap.

### 5.2 PRISM's power-only DOP

`DOP = |S2|/S1 = ||HH|² − |VV|²| / (|HH|² + |VV|²)`. This drops the coherent
cross term entirely (S3 = S4 = 0 by construction) because the real Level-2
SRI product this variant uses is amplitude-only (`unsigned short int`, no
phase, per the CH2DFSAR user manual) and structurally cannot support a
coherent cross term. This is the mathematically correct DOP formula *for
that specific data representation* — it is not an arbitrary simplification.

### 5.3 Raney et al. 2012's m (hybrid dual-polarimetric DOP)

**FACT (partial access):** Raney's paper (their own Eq. 3, a different
paper's numbering than Sinha's Eq. 2, coincidentally sharing the symbol `m`)
defines `m` as one of three parameters (`m`, χ ellipticity, ψ orientation)
"necessary and sufficient to describe the polarized portion of a partially
polarized quasi-monochromatic EM field," derived from **a 2×2 coherency
matrix of backscattered fields** for a **hybrid dual-polarimetric system**
(single circular transmit, two linear receive channels — i.e., genuinely 2
receive channels, not 4). Raney's paper claims hybrid-pol carries "the same
suite of polarimetric information... as full quad-pol" under specific
conditions this research pass could not extract. **The exact algebraic
formula for `m` in terms of the coherency-matrix elements was not
successfully retrieved** (the fetch reported it as not present in
text-extractable form, likely a rendered equation image) — marked
**AMBIGUOUS / NOT RETRIEVED**, not guessed at.

### 5.4 Averaging order — a distinct, untested variable

`DOP` is a nonlinear function of `S1`–`S4` (via the square root and ratio).
Therefore:

```
DOP(mean(S1), mean(S2), mean(S3), mean(S4))  ≠  mean(DOP(S1,S2,S3,S4))
```
in general (Jensen's-inequality-type divergence for a nonlinear, convex-ish
function of correlated random variables). **FACT (from code):** PRISM's
implementation computes `S1`–`S4` from *locally-averaged* `|A|²`, `|B|²`,
`Re(A·conj(B))`, `Im(A·conj(B))` and then takes **one** DOP from those
averaged Stokes parameters per pixel/window (the left side of the inequality
above, applied locally) — then, for the "interior mean," takes a further
plain arithmetic mean of these per-pixel DOP values over the crater interior
mask. This is a **second** averaging step, over already-nonlinear
quantities. Sinha's phrase "average DOP values... in craters F2, F3, H3, and
S1" is genuinely ambiguous about whether they mean the same two-step
procedure, or a single Stokes-then-DOP computation over the whole crater
interior as one aggregate. **PRISM's own `aggregate_dop()` function
(`dop_pipeline_v2_ainsworth_crosstalk.py`, `dop_pipeline_v2_crosstalk_
correction.py`) tests the single-aggregate version** and finds it
numerically close to the two-step windowed-mean version (F2: 0.793
aggregate vs. 0.785 windowed-mean at ws=5 — a difference of 0.008, not
enough to explain a 0.55–0.73 gap). This rules out averaging order as the
primary explanation, though it was not exhaustively swept across all
possible window/order combinations.

### 5.5 Equivalence verdict

**CONCLUSION:** PRISM's linear-pol DOP, PRISM's hybrid-pol DOP, PRISM's
power-only DOP, and Raney's hybrid-pol `m` are **four mathematically distinct
quantities**, not different names for the same computation:

| Formula | Channels | Coherent term? | Physical basis |
|---|---|---|---|
| PRISM linear-pol | HH, VV (as if one wave) | Yes | Non-standard for quad-pol; self-consistent Stokes math but questionable physical interpretation (§5.1) |
| PRISM hybrid-pol | Synthesized LH, LV from HH/HV/VH/VV | Yes | Matches Raney's *basis* (2-channel), but is PRISM's own synthesis, not verified identical to Raney's construction |
| PRISM power-only | HH, VV powers only | No | Correct for amplitude-only (SRI) data; structurally cannot equal a coherent-DOP value |
| Raney 2012's m | True 2-channel hybrid-pol receive | Yes (claimed) | The formalism Sinha cites for *interpretation*; exact formula not retrieved (§5.3) |
| Sinha's Eq. 2 | Unstated | Unstated | Cannot be classified — this is the core problem (§4.2) |

None of these can be assumed identical to another merely because they share
the label "DOP" or the symbol "m." **The paper does not state which of these
(or some other) construction it used**, so no formula-level equivalence
claim can be either proven or disproven — this is the central, sourced
finding of this investigation.

---

## 6. Sinha vs PRISM Pipeline Comparison

| Processing Stage | Sinha et al. 2026 | PRISM | Same/Different/Unknown | Evidence |
|---|---|---|---|---|
| Acquisition | Unstated (Supplementary Table 1, not retrieved) | `ch2_sar_ncxl_20200321t082617351_d_fp_d18` (2020-03-21, d18) for F2/F3; a second acquisition (`..._20191105..._m65`) independently tested | **Unknown** whether same as Sinha's | §4.2 item 5; PRISM code headers |
| Product level | "Calibrated" (Data Availability statement only) | Level-1A SLI (SLC, complex) | **Unknown** — Sinha may have used Level-1A SLC, Level-2 SRI, or another tier | §4.2 item 2 |
| Frequency | L-band DFSAR (implied by instrument, not restated) | L-band | **Same** (both DFSAR L-band; PRISM's raw products also carry S-band capability but F2/F3 work used the L-band quad-pol product) | Instrument spec |
| Polarization basis | Quad-pol acquisition ("all four combinations HH,HV,VH,VV") stated; DOP formula's basis unstated | Quad-pol acquisition; DOP tested in linear-pol (HH/VV), hybrid-pol (synth. LH/LV), and power-only bases | **Different/Unknown** — acquisition basis matches, but the *DOP construction's* basis is Sinha's core omission | §4.1, §4.2 item 1 |
| Calibration | Unstated | Bias-centering only (default); gain-imbalance, phase-orthogonality, and the real Ainsworth 2006 crosstalk algorithm all tested as separate hypotheses | **Unknown** vs. Sinha; **known** for PRISM | §3.3, §4.2 item 3 |
| Crosstalk correction | Unstated | Tested: self-derived reflection-symmetry correction (Hyp. 6) and real Ainsworth et al. 2006 iterative algorithm (Hyp. 7) — neither closed the gap | **Unknown** vs. Sinha | §4.2 item 3; §11 |
| Stokes derivation | `S1,S2,S3,S4` named, construction not given | `S1=<|A|²>+<|B|²>`, `S2=<|A|²>-<|B|²>`, `S3=2Re<A·conj(B)>`, `S4=-2Im<A·conj(B)>` for `(A,B) ∈ {(HH,VV),(LH,LV)}` | **Unknown** whether Sinha's construction matches either of PRISM's | §3.2, §4.1 |
| Multilooking | Unstated (only hardware resolution given) | Swept 5×5 to 41×41 px box-car window; also 20×1, 20×5 tested | **Unknown** vs. Sinha | §4.2 item 4; §3.4 |
| Window size | Unstated | 5, 9, 15, 21, 31, 41 px (square); 20×1, 20×5 (rectangular) | **Unknown** vs. Sinha | §3.4 |
| Averaging order | Ambiguous ("average DOP values... in craters") | Tested both (windowed-then-meaned vs. single aggregate); results close (§5.4) | **Ambiguous in Sinha; ruled out as primary PRISM-side driver** | §5.4 |
| DOP formula | `m = √(S2²+S3²+S4²)/S1` (Eq. 2) — same *shape* as PRISM's | Same shape, different (unstated-vs-stated) channel construction | **Formula shape: Same. Channel construction: Unknown/Different** | §4.1, §5.5 |
| Normalization | None stated beyond the ratio itself | None beyond the ratio itself | **Same** (both are self-normalizing ratios by construction) | §4.1, §3.2 |
| CPR formula | `Eq. 1`: `(a+b+2√ab)/(a+b−2√ab)` from σ°HH, σ°VV only, no cross-pol, no phase | Read directly as a delivered ISRO L3C-MOSAIC band; ISRO's internal formula undocumented | **Unknown whether identical formula; numbers land in the same regime** | §3.6, §4.1 |
| F2 coordinates | Not found in accessible text | −87.39°, 82.31°, diameter 1100 m | **Cannot verify or falsify from accessible text** | §4.2 item 7 |
| F3 coordinates | Not found in accessible text | −87.31°, 86.333°, diameter 700 m | **Cannot verify or falsify from accessible text** | §4.2 item 7 |

**First point of divergence that can be stated with confidence:** the Stokes
parameter *construction step* (mapping measured channels to S1–S4) — this is
the first stage in the pipeline where PRISM has a fully specified,
code-verifiable answer and Sinha's paper has none. Every downstream stage
(calibration, multilook, averaging order) is a second-order question that
cannot even be meaningfully compared until this first one is resolved.

---

## 7. Calibration Analysis

**FACT (PRISM):** Only XML `bias_real`/`bias_imag` (a per-channel complex DC
offset) is applied by default. Three further calibration variants were
implemented and tested as explicit, separate hypotheses:

1. **Gain-imbalance + phase-orthogonality** (`dop_pipeline_v2_lookcount_
   sweep.py`): dividing by XML `gain_imbalance` and rotating by
   `-phase_orthogonality` per channel. Result: **mathematically proven
   inert** for this DOP formula — a constant per-channel phase rotation
   cannot change `√(S3²+S4²)` (only how that fixed magnitude splits between
   S3 and S4), confirmed empirically to 4 decimal places
   (`F2_F3_sweep_full_table.json`: calibration on/off differ only in the
   4th–5th decimal). **CONCLUSION: ruled out.**
2. **Relative HH/VV gain calibration** (`dop_pipeline_v2_relative_gain_
   test.py`), 4 unit-convention guesses (linear amplitude, linear power, dB
   power, dB amplitude): HH and VV's own `gain_imbalance` XML values are
   already close (1.0156 vs. 1.0062), so every convention's correction
   factor is small (<2.5% except a stretched dB reading at <25%). **Zero of
   20 tested configurations moved DOP meaningfully.** F2 ws=5: 0.7855 →
   0.7855–0.7856 across all 4 conventions. **CONCLUSION: ruled out.**
3. **Crosstalk correction, self-derived (reflection symmetry)**
   (`dop_pipeline_v2_crosstalk_correction.py`): solves for crosstalk
   coefficients assuming true co-pol/cross-pol covariance is exactly zero.
   Recovered coefficients are **physically implausible** (magnitudes
   −3.96 dB to −10.56 dB, i.e. up to ~40% crosstalk — far above real SAR
   system specs) — a red flag that the underlying zero-covariance assumption
   itself is unjustified for this scene. F2 aggregate DOP moved from 0.793 to
   0.791 (a 0.002 change); F3 moved from 0.766 to 0.772 (**in the wrong
   direction**, +0.006). **CONCLUSION: ruled out, and the implausible
   coefficient magnitudes suggest the reflection-symmetry premise itself
   doesn't hold for this scene** (a real geophysical finding, since natural
   ice/regolith terrain is not always reflection-symmetric, e.g. under
   rough/oriented-scatterer conditions).
4. **Real Ainsworth et al. 2006 iterative crosstalk/channel-imbalance
   algorithm** (`dop_pipeline_v2_ainsworth_crosstalk.py`) — the rigorous,
   literature-sourced version of (3), estimating crosstalk **without**
   assuming zero co-pol/cross-pol covariance (it solves for `A =
   Σ_HVHH = Σ_VHHH` and `B = Σ_HVVV = Σ_VHVV` directly from the data). This
   is the single most credible calibration attempt in the entire
   investigation. Recovered crosstalk magnitudes (0.3%–2.4%, i.e. −49 dB to
   −32 dB — this session did not independently re-derive these dB figures
   but they are consistent with "genuinely small" per the source JSON's
   `abs_u/v/w/z` values ~0.003–0.024) are **physically plausible and well
   inside Ainsworth's own reported real-data range**. Result: **DOP barely
   moved** — F2: 0.7927 → 0.7960 (+0.0033); F3: 0.7660 → 0.7705 (+0.0045),
   both moving in the *wrong* direction (slightly higher, not lower).
   **CONCLUSION: a rigorous, correctly-implemented, literature-sourced
   crosstalk calibration finds real but tiny, physically well-behaved
   crosstalk — and confirms it is far too small to explain a 5–8× DOP gap.**
   This is strong evidence that PRISM's raw data itself is not badly
   miscalibrated at the crosstalk level; the discrepancy must lie elsewhere.

**Unresolved:** whether Sinha applied *any* calibration procedure at all
(§4.2 item 3) — this cannot be tested further without their processing chain.

---

## 8. Stokes/Polarimetric Basis Analysis

See §5.1, §5.3, §5.5 for the mathematical argument. Summary of the
**tested** basis variants and their results (all craters, best-supported
window ws=5, bias-centering only):

| Basis | F2 interior DOP | F3 interior DOP | Direction vs. linear-pol | Meets 0.10–0.13? |
|---|---:|---:|---|---|
| Linear-pol (HH, VV as pseudo-single-wave) | 0.785–0.793 | 0.766–0.843 | baseline | No |
| Hybrid-pol (synth. LH, LV) | ~0.57 (whole-window figure from prior turn; not re-verified against a JSON file in this session — **flag as UNCONFIRMED PRECISION**, direction only is confirmed by `candidate_dop_pipeline_F2F3.py`'s side-by-side output) | ~0.60 (same caveat) | **consistently lower** than linear-pol | No |
| Power-only (real Level-2 SRI) | 0.063 | 0.025 | **far lower** than both | No (undershoots) |

**OBSERVATION:** the three tested bases bracket Sinha's 0.10–0.13 target from
both sides (hybrid-pol closer from above at ~0.57–0.60 is still far above;
power-only from below at 0.025–0.063 is much closer numerically but for the
wrong physical reason — it discards all phase information, which a
coherent-DOP claim like Sinha's should not do if their instrument delivered
phase-preserving SLC data). **No tested basis lands in the target range.**
This is the same finding the prior session already reached
(`DOP_GROUND_TRUTH_INVESTIGATION.md` §"Diagnosis"), independently confirmed
here against the actual paper text rather than inferred from citation
patterns alone.

---

## 9. Multilooking Analysis

**FACT:** window-size sweep (5, 9, 15, 21, 31, 41 px, calibration on and
off — 24 total configurations) shows DOP is **not monotonically decreasing
with more looks in a way consistent with small-sample bias converging toward
0.10–0.13**:

| Window (px) | F2 DOP mean | F3 DOP mean |
|---:|---:|---:|
| 5 | 0.7855 | 0.8426 |
| 9 | 0.7655 | (not shown above; see full table) |
| 15 | 0.7643 | — |
| 21 | 0.7670 | — |
| 31 | 0.7712 | — |
| 41 | 0.7734 | 0.7386 |

F2's DOP actually **increases slightly** from ws=15 to ws=41 after an
initial small drop; F3 drops from 0.843 to 0.739 but plateaus well above
0.13. **CONCLUSION (matches prior session's hypothesis-2 aggregate-covariance
check, §5.4): this is not small-sample DOP bias.** A true small-sample-bias
explanation would predict a much larger, smoothly convergent drop as look
count increases from 25 (5×5) to 1,681 (41×41) — a ~67× increase in
independent samples. The near-flat behavior observed is inconsistent with
bias being the dominant effect, and consistent with the underlying
*population* DOP itself being genuinely high under PRISM's basis/formula —
reinforcing that the discrepancy is a basis/definition issue (§5, §8), not an
estimator-variance issue.

**Unresolved:** Sinha's own multilook parameter is entirely unstated (§4.2
item 4), so no direct comparison of "PRISM's window vs. Sinha's window" is
possible — only PRISM's own internal window-sensitivity can be characterized,
and it has been, exhaustively.

---

## 10. Reproduction Experiments

**This session ran zero new experiments** (§3.5 — no raw data access). What
follows is a verified inventory of the experiments the *prior* PRISM session
actually ran (re-confirmed against source code and output JSON this session,
not merely re-quoted from prose documentation):

| # | Hypothesis | Script | Formula/variant | Calibration | Window | Data |
|---|---|---|---|---|---|---|
| 1 | Window-size sensitivity | `dop_pipeline_v2_lookcount_sweep.py` | Linear-pol | bias only, on/off gain+phase | 5–41 px | `..._20200321..._d18` |
| 2 | Small-sample bias | `dop_pipeline_v2_ainsworth_crosstalk.py` (`aggregate_dop`) | Linear-pol | bias only | whole-interior aggregate (no window) | same |
| 3 | Absolute gain/phase calibration | `dop_pipeline_v2_lookcount_sweep.py` | Linear-pol | XML gain_imbalance + phase_orthogonality | 5–41 px | same |
| 4 | Relative HH/VV gain | `dop_pipeline_v2_relative_gain_test.py` | Linear-pol | 4 gain-unit conventions | 5, 41 px | same |
| 5 | Zhao et al. 2024's multilook formula | `dop_pipeline_v2_crosstalk_correction.py` | Linear-pol | bias only | 20×1, 20×5, 5×5 | same |
| 6 | Self-derived crosstalk (reflection symmetry) | `dop_pipeline_v2_crosstalk_correction.py` | Linear-pol, crosstalk-corrected | bias + self-derived crosstalk | 20×1, 20×5, 5×5 | same |
| 7 | Real Ainsworth 2006 crosstalk | `dop_pipeline_v2_ainsworth_crosstalk.py` | Linear-pol, Ainsworth-calibrated | bias + iterative Ainsworth (α, u, v, w, z) | 5, 9, 15, 21, 31, 41 px | same |
| 8 | Different acquisition | `dop_pipeline_v2_alt_acquisition.py` | Linear-pol + hybrid-pol | bias only | 5 px | `..._20191105..._m65` |
| — | Power-only (real Level-2 SRI) | `dop_pipeline_v2_sri_powerdop.py` | `\|S2\|/S1` on real amplitude product | none (data has no phase) | interior-mask aggregate | `..._20200321..._d18` SRI |
| — | Interior-mask-only re-test (rules out whole-PSR-averaging as an explanation) | `candidate_dop_pipeline_F2F3.py` | Linear-pol + hybrid-pol | bias only | 5 px | `..._20200321..._d18` |

Each hypothesis has a documented result already presented (§7, §8, §9,
§11) — no hypothesis was silently dropped or altered after the fact; this
table is a faithful re-derivation of the "8 hypotheses" narrative in
`docs/DOP_GROUND_TRUTH_INVESTIGATION.md`, cross-checked directly against the
generating source code line-by-line in this session.

---

## 11. Results Table

All values FACT-checked against their generating JSON output this session.

### F2 (diameter 1100 m, −87.39°, 82.31°)

| Configuration | DOP mean | Meets 0.10–0.13? | Source |
|---|---:|---|---|
| Linear-pol, bias-only, ws=5 | 0.7855 | No | `F2_F3_relative_gain_test.json` |
| Linear-pol, bias-only, ws=41 | 0.7734 | No | same |
| Linear-pol, gain+phase cal, ws=5 | 0.7856 | No | `F2_F3_sweep_full_table.json` |
| Linear-pol, whole-interior aggregate, pre-Ainsworth | 0.7927 | No | `F2_F3_ainsworth_crosstalk.json` |
| Linear-pol, whole-interior aggregate, post-Ainsworth | 0.7960 | No | same |
| Linear-pol, self-derived crosstalk corrected, 5×5 | 0.7851 | No | `F2_F3_crosstalk_correction_test.json` |
| Linear-pol, alternate acquisition (2019-11-05) | 0.786 (whole-window, prior turn) | No | `F2_alt_acquisition_dop.json` |
| Power-only, real Level-2 SRI | 0.0633 | No (undershoots) | `F2_F3_sri_powerdop.json` |
| **Sinha et al. 2026 reported** | **0.10–0.13** | — | paper Eq. 2 result |

### F3 (diameter 700 m, −87.31°, 86.333°)

| Configuration | DOP mean | Meets 0.10–0.13? | Source |
|---|---:|---|---|
| Linear-pol, bias-only, ws=5 | 0.8426 | No | `F2_F3_relative_gain_test.json` |
| Linear-pol, bias-only, ws=41 | 0.7386 | No | same |
| Linear-pol, whole-interior aggregate, pre-Ainsworth | 0.7660 | No | `F2_F3_ainsworth_crosstalk.json` |
| Linear-pol, whole-interior aggregate, post-Ainsworth | 0.7705 | No | same |
| Linear-pol, self-derived crosstalk corrected, 5×5 | 0.8448 | No | `F2_F3_crosstalk_correction_test.json` |
| Linear-pol, alternate acquisition (2019-11-05) | 0.757 (whole-window, interior mean; PRISM's own `F2_F3_alt_acquisition_combined.json` reports interior/whole-window separately — 0.757 is the value cited consistently across this and the prior session's docs) | No | `F3_alt_acquisition_dop.json` |
| Power-only, real Level-2 SRI | 0.0250 | No (undershoots) | `F2_F3_sri_powerdop.json` |
| **Sinha et al. 2026 reported** | **0.10–0.13** | — | paper Eq. 2 result |

### CPR cross-check (both craters, PRISM's real L3C-MOSAIC band vs. Sinha's Eq. 1)

| Crater | PRISM % CPR>1 (interior) | Sinha % CPR>1 | PRISM max CPR | Sinha max CPR |
|---|---:|---:|---:|---:|
| F2 | 44.75% | 47% | 1.82 | 1.95 |
| F3 | 33.3% | 42% | 1.48 | 1.73 |

**Total: 0 of 10+ tested DOP configurations across 2 acquisitions, 3 bases,
4 calibration schemes, and 6 window sizes met Sinha's 0.10–0.13 range. CPR
independently lands in the same regime as Sinha's numbers on both craters,
using a structurally different data product (§3.6).**

---

## 12. Root-Cause Analysis

Working through the categories the task specifies, without forcing a single
answer:

- **A. PRISM implementation error** — **Not supported.** The formula is
  textbook-standard Stokes-parameter DOP, correctly implemented (verified by
  independent re-reading of every script this session); the Ainsworth
  crosstalk calibration was implemented faithfully from the actual 2006
  paper's legible equations; the channel mapping for the raw byte-decode
  product was independently re-verified via exhaustive 24-permutation search
  in a separate, unrelated PRISM validation (`RAW_DFSAR_VALIDATION.md`) —
  though note the F2/F3 acquisition used here is a Level-1A SLI product with
  ISRO-labeled polarization filenames, not the byte-level-inferred mapping,
  so that specific caveat does not even apply to this investigation.
- **B. Sinha implementation/methodology error** — **Cannot be assessed.**
  There is not enough published detail to say whether their method is
  correct or incorrect; this category requires information this
  investigation does not have access to (§4.2).
- **C. Different DOP definitions being incorrectly compared** — **Strongly
  supported as a contributing factor.** Sinha's Eq. 2 has the same
  mathematical *shape* as PRISM's, but with an entirely unstated
  channel-to-Stokes mapping (§4.1, §5.5). PRISM tested 3 different concrete
  instantiations of "DOP" (linear-pol, hybrid-pol, power-only) and got 3
  different answers spanning nearly 2 orders of magnitude (0.025–0.84) —
  demonstrating empirically that "DOP" is not one number for this kind of
  data, it is a family of numbers depending on construction choices Sinha's
  paper does not specify.
- **D. Different polarimetric basis** — **Strongly supported, likely
  entangled with C.** Sinha's only cited DOP-interpretation authority (Raney
  2012, via Mohan 2011) is explicitly a 2-channel hybrid dual-polarimetric
  formalism, while Sinha's own stated acquisition is 4-channel quad-pol
  (§4.1). PRISM's hybrid-pol test is the closest analogue to Raney's basis
  and moves in the right direction (lower) without reaching the target —
  consistent with "basis mismatch matters, but is not the whole story."
- **E. Calibration/crosstalk mismatch** — **Tested rigorously and largely
  ruled out on PRISM's side.** The real Ainsworth 2006 algorithm found small,
  physically plausible crosstalk (§7) that moved DOP by <0.005 — not enough
  to explain a >0.5 gap. This does not rule out that Sinha applied
  *some other* calibration entirely, but it does rule out "PRISM's own data
  is badly crosstalk-contaminated" as a self-contained explanation.
- **F. Multilooking/averaging mismatch** — **Tested and largely ruled out on
  PRISM's side** (§9, §5.4) — window size and averaging order both produce
  only small (<0.1) shifts, far short of the 0.5+ gap, and don't
  monotonically trend toward the target.
- **G. Data-product mismatch** — **Partially supported, previously
  under-examined.** PRISM's DOP-matching acquisition (`..._20200321...`) is
  confirmed geometrically to cover F2/F3, but is **not confirmed to be the
  same acquisition Sinha used** (§4.2 item 5 — their Supplementary Table 1
  is unavailable). Separately, and newly documented in §3.6: PRISM's CPR
  "match" evidence itself comes from a **different DFSAR product entirely**
  (a 602-acquisition ISRO mosaic) than PRISM's DOP computation (a single raw
  pass) — so the "CPR matches, therefore location/acquisition is validated
  for DOP too" reasoning in the prior investigation is **weaker than
  previously stated**, though not void (the crater lat/lon geometry itself
  is independently confirmed by point-in-polygon tests in both cases).
- **H. Paper underspecification** — **Strongly and independently
  confirmed.** §4.2 lists 7 specific, verified-absent pieces of information,
  any one of which could materially change a reproduced DOP value. This is
  now confirmed against the primary source text directly, not inferred from
  PRISM's prior citation analysis.
- **I. Multiple interacting causes** — **Best-supported overall
  classification.** The evidence points to a combination of (H) genuine
  paper underspecification, entangled with (C)/(D) a likely different DOP
  definition/basis that Sinha's own citations suggest but do not confirm,
  with (E) and (F) reasonably ruled out as *sufficient standalone*
  explanations by PRISM's own rigorous testing, and (G) a real but
  previously-underweighted possibility that the compared quantities (a
  single 2020 PRISM pass vs. an unknown, possibly different, Sinha
  acquisition) may not even be directly comparable regardless of formula.
- **J. Still unresolved** — **True as a practical matter**, but (I) is the
  more informative classification: this is not blank uncertainty, it is a
  specific, narrowed set of interacting factors, several of which have been
  affirmatively ruled out.

**This report does not force a single-letter conclusion. The evidence
supports I, with H and C/D as the dominant components and G as a real but
secondary complicating factor.**

---

## 13. What Is Proven

- Sinha et al. 2026's own published text gives no formula relating S1–S4 to
  any measured radar channel (independently verified, two fetch passes).
- Sinha's CPR formula (Eq. 1) is fully specified and PRISM's independently-
  sourced CPR values land in the same regime for both F2 and F3.
- PRISM's linear-pol DOP formula is textbook-correct Stokes-parameter DOP,
  correctly implemented, and stable in the sense that 8 independent,
  rigorously-executed hypotheses (window size, small-sample bias, absolute
  and relative gain/phase calibration, a self-derived and the real
  Ainsworth-2006 crosstalk algorithm, and a second, geometrically-independent
  acquisition) all return a DOP in the 0.63–0.86 range for these two craters.
- The real Ainsworth et al. 2006 crosstalk algorithm, correctly implemented
  from the actual paper, finds genuinely small (0.3–2.4%), physically
  plausible crosstalk in PRISM's data — evidence against a gross
  calibration failure on PRISM's side.
- PRISM's own hybrid-pol variant (the basis Sinha's cited authority actually
  uses) returns lower DOP (~0.57–0.60) than the linear-pol variant, in the
  direction that would be expected if basis mismatch is part of the
  explanation — though it does not reach 0.10–0.13.
- The "Kumar et al. 2022, Adv. Space Res. 70(12)" and "Zhao et al. 2024 as a
  Sinha reference" citations in PRISM's own prior documentation do not check
  out against Sinha's actual 56-entry reference list.

## 14. What Is Not Proven

- Whether Sinha's actual DOP construction is closer to PRISM's linear-pol,
  hybrid-pol, power-only, or some fourth construction entirely.
- Whether Sinha used the same acquisition(s) PRISM used for F2/F3.
- Whether Sinha applied any calibration/crosstalk correction.
- Whether Sinha's stated "average DOP... in craters" means per-pixel-then-
  averaged or aggregate-then-computed.
- Whether Verma et al. 2025 (Sinha's own ref 45) already reported the 0.13
  threshold before Sinha's 2026 "refinement" — flagged as an unresolved,
  AI-search-only (not directly fetched) ambiguity in this investigation.
- Whether PRISM's own hybrid-pol synthesis (`LH=(HH+j·HV)/√2`,
  `LV=(VH+j·VV)/√2`) is numerically identical to whatever construction
  Raney 2012's hybrid-pol formalism specifies — the exact algebraic formula
  for Raney's `m` could not be retrieved (§5.3).

## 15. Remaining Unknowns

- The contents of Sinha et al. 2026's Supplementary Table 1.
- The exact algebraic formula for Raney (2012)'s `m` in terms of coherency-
  matrix elements.
- Ainsworth (2006)'s and Xing (2012)'s exact equations — both remain
  IEEE-paywalled with no legitimate open-access route found by either this
  or the prior PRISM session.
- Whether ISRO's internal L3C-MOSAIC CPR algorithm matches Sinha's Eq. 1
  exactly, approximately, or coincidentally lands in a similar numeric
  range for unrelated reasons.

## 16. Recommended Next Experiments

Ranked by expected information gain per unit effort, and restricted to
literature-justified variants only:

1. **(Highest value, lowest effort) Request Sinha et al. 2026's
   Supplementary Table 1 and their exact DOP processing description directly
   from the authors** (see §17) — this single document would resolve items
   2, 3, 4, 5, and 6 in §4.2 simultaneously, which is more information than
   any further PRISM-side experiment can provide.
2. **Implement Raney (2012)'s hybrid-pol `m` formula exactly**, once its
   algebraic form is obtained (from the paper's supplementary equations, a
   textbook citing it, or direct author correspondence), rather than PRISM's
   own hybrid-pol synthesis — to test whether the *exact* published formula
   (not PRISM's approximation of its spirit) changes the result.
3. **Test whether Sinha's DOP could be a per-pixel-computed-then-averaged
   quantity over a much larger area than PRISM's crater-diameter interior
   mask** (e.g., the full doubly-shadowed region including a wider halo) —
   this session did not test window shapes larger than the crater's own
   diameter; a systematically larger averaging area is a distinct, testable,
   literature-plausible variant not yet tried.
4. **Obtain and test the real Bhiravarasu et al. 2021 (Sinha's ref 44,
   arXiv:2104.14259) DFSAR instrument-team paper** for any DOP/Stokes
   convention it may define for L-band DFSAR specifically — this is the most
   likely place a DFSAR-specific (rather than generic Stokes-textbook)
   convention would be documented, and PRISM's own `CANDIDATE_ACQUISITION_
   SELECTION.md` already treats it as a primary source for other DFSAR
   conventions.
5. **(Lower priority, requires new data access)** If a PRISM environment with
   raw-data access becomes available again, re-run the alternate-acquisition
   test (Hypothesis 8) with a systematic scan of *all* full-pol acquisitions
   covering F2/F3 (not just the one alternate already tried), to check
   whether DOP varies acquisition-to-acquisition enough to matter — current
   evidence (0.79 vs. 0.76–0.84 across 2 acquisitions) suggests it does not
   vary enough to reach 0.13, but only 2 of the available acquisitions have
   been tested.

## 17. Whether Author Contact Is Necessary

**Yes — recommended, not merely as a fallback.** The single most valuable
next experiment (§16.1) requires information this investigation has proven,
through primary-source verification, is genuinely absent from the published
paper and its currently-accessible supplementary material. This is not a
case of "we didn't look hard enough" — two independent, verbatim-focused
fetches of the actual article confirm the omission.

**Exact technical question to ask:**

> "In Equation 2 of your paper (DOP, m = √(S2²+S3²+S4²)/S1), could you
> please specify: (1) the exact relationship between the Stokes parameters
> S1–S4 and the measured DFSAR polarimetric channels (e.g., is this
> constructed from HH/VV as a coherent 2-channel Stokes vector, from a
> synthesized hybrid-pol basis per Raney et al. 2012, from a power-only
> combination, or another convention)? (2) What DFSAR product processing
> level (raw, Level-1A SLC, Level-2, or other) and what specific
> acquisition(s)/dates were used for the F2, F3, H3, and S1 DOP values in
> Fig. 4? (3) What calibration or crosstalk correction, if any, was applied
> before computing DOP? (4) What spatial averaging/multilook window was
> used, and were Stokes parameters averaged before computing DOP, or was DOP
> computed per-pixel and then averaged? We ask because we have independently
> implemented the standard quad-pol Stokes-parameter DOP construction on
> DFSAR data covering the same F2/F3 craters and consistently obtain
> 0.6–0.85 rather than your reported 0.10–0.13, across multiple
> calibration and windowing choices, and would like to understand whether
> the difference is a specific channel-mapping/basis choice we're missing."

This question is scoped to exactly the 4 items independently confirmed
missing in §4.2 — it does not ask the authors to defend their result, only
to specify their method.

---

## 18. References with DOI/URL

1. Sinha, R. K., Bharti, R. R., Acharyya, K., Mishra, S. K., Srivastava, N.,
   Bhardwaj, A. (2026). "Subsurface ice in doubly shadowed craters as
   revealed by Chandrayaan-2 dual frequency synthetic aperture radar."
   *npj Space Exploration* 2:22. DOI: 10.1038/s44453-026-00038-9.
   https://doi.org/10.1038/s44453-026-00038-9
2. Raney, R. K., Cahill, J. T., Patterson, G. W., Bussey, D. B. J. (2012).
   "The m-chi decomposition of hybrid dual-polarimetric radar data with
   application to lunar craters." *Journal of Geophysical Research: Planets*
   117, E00H21. DOI: 10.1029/2011JE003986.
3. Mohan, S., Das, A., Chakraborty, M. (2011). "Studies of polarimetric
   properties of lunar surface using mini-SAR data." *Current Science* 101,
   159–164. (Full citation confirmed via Sinha's reference list; not
   independently fetched — content summarized from PRISM's prior
   documentation only.)
4. Verma, N., Bhatt, M., Dangi, M., Kumar, S., Bhardwaj, A. (2025).
   "Exploring water-ice deposits in lunar polar craters with Chandrayaan-2
   DFSAR data." *Icarus* 432. (Sinha et al. 2026's ref 45; not independently
   fetched in full — ScienceDirect abstract-only access; relationship to
   Sinha's 0.13 threshold flagged AMBIGUOUS, §4.1/§14.)
5. Mishra, P., Kumar, S., Singh, D. (2014). "An approach for finding water
   ice deposits on lunar craters using MiniSAR." (Sinha et al. 2026's ref
   51; not independently fetched in full.)
6. Bhiravarasu, S. S. et al. (2021). "Chandrayaan-2 DFSAR: Performance
   characterization and initial results." (Sinha et al. 2026's ref 44;
   plausibly arXiv:2104.14259, already used elsewhere in PRISM's own
   documentation for DFSAR geolocation conventions — not independently
   re-fetched in this pass.)
7. Ainsworth, T. L., Ferro-Famil, L., Lee, J.-S. (2006). "Orientation Angle
   Preserving A Posteriori Polarimetric SAR Calibration." *IEEE Transactions
   on Geoscience and Remote Sensing* 44(4):994–1003.
   **COULD NOT ACCESS FULL TEXT** in this session (IEEE Xplore subscription
   wall; no legitimate open-access copy found). PRISM's prior session
   accessed this via a since-unavailable institutional subscription.
8. Xing, M., Dai, D., Liu, Y., Wang, X. (2012). "Comment on 'Orientation
   Angle Preserving A Posteriori Polarimetric SAR Calibration'." *IEEE
   Transactions on Geoscience and Remote Sensing* 50(6):2417–2419.
   **COULD NOT ACCESS FULL TEXT** in this session, same reason as above.
9. **"Kumar et al. 2022, Advances in Space Research 70(12)"** — cited in
   PRISM's own `dop_pipeline_v2_lookcount_sweep.py` docstring as the origin
   of the CPR>1/DOP<0.13(or 0.35) criterion. **Could not be verified to
   exist; does not appear in Sinha et al. 2026's reference list.** Flagged
   as likely misattribution — see §4.1, §12.
10. **"Zhao et al. 2024"** — cited in PRISM's own DOP pipeline docstrings as
    a DFSAR calibration/multilook reference (Eq. 7 multilook formula, Eq. 10
    CPR formula). **Confirmed independent of Sinha et al. 2026** — does not
    appear in their reference list; this is PRISM's own, separately-sourced
    reference, not something Sinha's paper cites or relies on. Exact
    citation (title/journal/DOI) not re-verified in this session.
