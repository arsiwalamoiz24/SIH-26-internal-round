# DOP Ground-Truth Investigation — 8 hypotheses, F2/F3, Faustini PSR

**Date:** 2026-08-25. **Bottom line if you only read one paragraph:** PRISM's DOP
computation cannot reproduce Sinha et al. 2026's own reported ground-truth DOP
(0.10–0.13) at their confirmed-ice craters F2 and F3 inside Faustini's PSR,
despite testing 8 independent, rigorously-executed hypotheses covering every
calibration, processing, and data-source avenue reachable from public and
institutional sources. PRISM's own CPR pipeline, by contrast, matches the
paper well on the same data. **Recommendation: use PRISM's CPR-based
criterion as the validated ground-truth metric, and de-emphasize DOP
matching, unless the paper's Supplementary Table 1 becomes available.**

> ⚠️ **That recommendation is SUPERSEDED, and hypothesis 8 is REOPENED.** The
> Supplementary Table 1 named above arrived on 2026-08-26. It shows PRISM ran on
> none of the authors' six acquisitions, and Supplementary Figure 6 states that
> high CPR alone is insufficient to separate roughness from volumetric
> scattering — the combined CPR-DOP criterion is required. The 8-hypothesis work
> below is unchanged and still correct as measurement; only its closing
> recommendation and hypothesis 8's "ruled out" status are withdrawn. See the
> [Addendum, 2026-08-26](#addendum-2026-08-26--the-supplementary-material-arrived-and-it-changes-two-conclusions-above)
> at the end of this file, and `SINHA_SUPPLEMENTARY_FINDINGS.md`.

---

## The problem

Sinha et al. 2026 (*npj Space Exploration* 2:22) report degree-of-polarization
(DOP) values of **0.10–0.13** for F2 (1100 m diameter) and F3 (700 m diameter),
two small doubly-shadowed features inside Faustini crater's permanently
shadowed region, as part of their evidence for water ice. Their DOP equation
is given generically as:

```
m = sqrt(S2² + S3² + S4²) / S1
```

with **no stated relationship** between S1–S4 and the HH/HV/VH/VV channels a
quad-pol SAR instrument actually measures. Their only two citations for
*interpreting* DOP (low m → volume scattering, high m → double bounce) are
Raney et al. 2012 (the m-χ decomposition, a **hybrid/compact-polarimetric**
formalism) and Mohan et al. 2011 (hybrid-pol Mini-SAR lunar studies) — neither
is a standard quad-pol reference.

PRISM computes DOP from Chandrayaan-2 DFSAR full-pol (quad-pol) data using the
standard linear-pol Stokes construction (bias-corrected HH/VV, local spatial
covariance):

```
S1 = <|HH|²> + <|VV|²>
S2 = <|HH|²> - <|VV|²>
S3 = 2·Re(<HH·conj(VV)>)
S4 = -2·Im(<HH·conj(VV)>)
DOP = sqrt(S2² + S3² + S4²) / S1
```

Applied to the real, downloaded, footprint-confirmed DFSAR acquisition
covering F2 and F3, this consistently returns **DOP ≈ 0.63–0.85** — 5 to 8
times higher than the paper's range. Meanwhile PRISM's CPR pipeline, on the
*same* acquisition, matches the paper's own numbers reasonably closely (see
[Independent evidence](#independent-evidence-cpr-matches) below) — so the
acquisition/location is very likely correct, and the discrepancy is specific
to DOP.

---

## The 8 hypotheses, in order

Each was tested to completion, with honest reporting of the result even when
it didn't move the number — no hypothesis was adjusted post hoc to force a
match.

| # | Hypothesis | Method | Result |
|---|---|---|---|
| 1 | Covariance window / look-count size | Swept 5–41 px local covariance windows | Plateaus at 0.74–0.85 — window size is not the driver |
| 2 | Small-sample statistical bias | Whole-crater-interior huge-N aggregate covariance (bias-free limit) | Same result as windowed — rules out few-look bias entirely |
| 3 | Absolute per-channel gain/phase calibration | Applied XML `gain_imbalance` / `phase_orthogonality` corrections | Mathematically inert for a magnitude-ratio metric like DOP |
| 4 | Relative HH/VV gain calibration | Tested 4 different unit conventions for the relative gain term | Negligible — HH/VV channels are already very similar in amplitude |
| 5 | Zhao et al. 2024's own documented multilook formula | Applied their exact azimuth-only multilook (`MLN = ceil(range_spacing/azimuth_spacing) = 20`) per their Eq. 7 | Same plateau as hypothesis 1 |
| 6 | Self-derived crosstalk correction (reflection symmetry) | 2×2 linear solve assuming HV≈VH cross-terms are zero | Produced implausible 34–63% crosstalk coefficients (physically impossible); negligible DOP change |
| 7 | The real Ainsworth et al. 2006 crosstalk/channel-imbalance algorithm | Implemented faithfully from the actual IEEE TGRS paper (the algorithm Zhao et al. 2024 themselves cite as "Ans") — full 6-step iterative solve, converged in 2–3 iterations | Found genuinely small, physically plausible crosstalk (0.3–2.4%, *cleaner* than Ainsworth's own real PiSAR example) — but DOP barely moved (F2: 0.793→0.796, F3: 0.766→0.771) |
| 8 | A genuinely different source acquisition | Searched PRADAN, footprint-verified 18 full-pol candidates near Faustini via point-in-polygon test in the correct Moon polar-stereographic projection; found and downloaded the one that covers both craters (2019-11-05, different date and swath mode from the acquisition used in hypotheses 1–7); independently re-geolocated F2/F3 from scratch in its own pixel grid | F2 = 0.665, F3 = 0.757 — lower than the original acquisition (0.786/0.843) but still 5–7× the paper's target |

Hypotheses 1–6 and the paper Methods re-read are documented in detail in the
session's working plan file (kept outside this repo, in the assistant's local
plan history); hypotheses 7–8 are summarized in full below since they're the
most diagnostic.

### Hypothesis 7 in detail — the real Ainsworth 2006 algorithm

Ainsworth, Ferro-Famil & Lee, *"Orientation Angle Preserving A Posteriori
Polarimetric SAR Calibration,"* IEEE TGRS 44(4):994–1003, 2006, solves for 2
channel-imbalance parameters (`k` fixed to 1, `α` solved) and 4 complex
crosstalk parameters (`u,v,w,z`) from the data's own aggregate covariance
matrix, *without* assuming reflection symmetry (unlike the cruder method in
hypothesis 6) — it estimates the off-diagonal terms `A = Σ_HVHH = Σ_VHHH` and
`B = Σ_HVVV = Σ_VHVV` directly from the data instead of assuming they're zero.

Implemented the paper's full iterative procedure (Section IV, Eq. 10–21) on
the real F2/F3 aggregate covariance. Converged cleanly by iteration 2–3 of 8:

| Crater | \|u\| | \|v\| | \|w\| | \|z\| | α | η/β | DOP before → after |
|---|---|---|---|---|---|---|---|
| F2 | 0.0041 | 0.0031 | 0.0031 | 0.0041 | 1.061 | 0.103 | 0.7927 → 0.7960 |
| F3 | 0.0235 | 0.0146 | 0.0146 | 0.0235 | 1.050 | 0.166 | 0.7660 → 0.7705 |

Both crosstalk magnitudes are well inside Ainsworth's own reported real-data
range (5–20%, their PiSAR example) — in fact cleaner — and `η/β < 1` for both,
meaning the calibration doesn't even flag a data-quality problem. This is the
opposite failure mode from hypothesis 6: here the *correct* algorithm finds
real, small, well-bounded crosstalk, and confirms it's simply too small to
explain a 6× DOP discrepancy. (A known bug in the original 2006 paper,
identified by Xing et al. 2012, was noted but not silently patched — see the
script's docstring for detail.)

**Outputs:** `outputs/objective1/dop_v2/F2_F3_ainsworth_crosstalk.json`,
`F2_F3_ainsworth_summary.json`, `F2_F3_ainsworth_plot.png`. Script:
`src/dop_pipeline_v2_ainsworth_crosstalk.py`.

### Hypothesis 8 in detail — a genuinely different acquisition

All of hypotheses 1–7 used the single acquisition
`ch2_sar_ncxl_20200321t082617351_d_fp_d18` (2020-03-21, station d18). To rule
out "wrong acquisition" as an explanation, searched PRADAN's SAR data browser
for other full-polarimetric acquisitions whose **true footprint** — not just
a nearby center coordinate — actually covers F2 (82.31°E, −87.39°) and F3
(86.333°E, −87.31°).

**Method:** filtered PRADAN's browse table (`Filename` contains `d_fp`,
`CentreLongitude` 78–90°, `CentreLatitude` −89° to −85°) down to 18
full-polarimetric candidates near Faustini. For each promising candidate,
read its PDS4 label's true image-footprint corners
(`isda:image_upper_left/upper_right/lower_right/lower_left`, given directly
in projected map meters) and ran a real point-in-polygon test against F2/F3's
coordinates forward-projected into the same Moon polar-stereographic CRS
(`pyproj`, the exact CRS read from the product's own GeoTIFF) — not a loose
bounding-box approximation.

Of the candidates checked, only one covers **both** craters:

| Acquisition | Date | Mode | F2 coverage | F3 coverage |
|---|---|---|---|---|
| `ch2_sar_ncxl_20191105t180525404_d_fp_m65` | 2019-11-05 | m65 | ✅ 2.08 km inside nearest edge | ✅ 3.58 km inside |
| `ch2_sar_ncxl_20201019t092257302_d_fp_d18` | 2020-10-19 | d18 | ❌ ~2.8 km outside | ✅ inside |
| 4 others checked | 2019–2022 | d18/d32 | ❌ | ❌ |

Downloaded the covering acquisition (813,145,924 bytes, confirmed to contain
the same SLI complex HH/HV/VH/VV product structure as the baseline). Located
F2/F3 in its own pixel grid via 0-residual bilinear inversion of the
acquisition's own 4 true corner control points (`isda:Geometry_Parameters`,
solved with `scipy.optimize.fsolve` in the projected CRS) — F2 at line
36585/sample 408, F3 at line 46264/sample 332, both comfortably inside the
512-sample swath with no interior-mask clipping. Ran the identical DOP
pipeline (same bias-only calibration, same 5 px covariance window, same
circular-interior-mask methodology):

| Crater | This acquisition (2019-11-05) | Baseline acquisition (2020-03-21) | Paper target |
|---|---|---|---|
| F2 | **0.665** | 0.786 | 0.10–0.13 |
| F3 | **0.757** | 0.843 | 0.10–0.13 |

Lower than the baseline, but still 5–7× too high. **This closes off "wrong
acquisition" as an explanation** — a completely independent acquisition
(different date, different swath mode, independently geolocated from
scratch) reproduces the same high-DOP pattern seen across every acquisition
and candidate tested this investigation (8 acquisitions total, including 3
other PSR candidates unrelated to F2/F3 — see
`outputs/objective1/dop_secondary/`).

**Outputs:** `outputs/objective1/dop_v2/F2_alt_acquisition_dop.json`,
`F3_alt_acquisition_dop.json`, `F2_F3_alt_acquisition_combined.json`, plus
histogram PNGs. Script: `src/dop_pipeline_v2_alt_acquisition.py`.

---

## Independent evidence: CPR matches {#independent-evidence-cpr-matches}

The paper's CPR formula (their Eq. 1, the classic μc construction —
HH/VV power ratio only, no cross-pol terms) is *different* from the formula
PRISM's own CPR pipeline normally uses (Zhao et al. 2024's Eq. 10, which
includes HV/VH cross terms) — yet PRISM's CPR still matches the paper's own
reported numbers reasonably well on the same acquisition/location:

| Crater | PRISM elevated-CPR % (interior) | Paper's reported % | PRISM max CPR | Paper's max CPR |
|---|---|---|---|---|
| F2 | 44.75% | 47% | 1.82 | 1.95 |
| F3 | 33.3% | 42% | — | 1.73 |

This is independent evidence the crater location and acquisition used
throughout this investigation are correct — the mismatch is specific to DOP,
not a wrong-location or wrong-acquisition problem in general.

---

## Diagnosis: why DOP, specifically, doesn't match

Re-reading the paper's own Methods section (page 7, "CPR and DOP
calculations") closely: `|HH| ≈ |VV|` almost exactly in both crater
interiors (S2 ≈ 0 — a real, strong depolarization signature consistent with
volume scattering / ice). The full coherent DOP is inflated toward 1 by the
**S3/S4 cross term** (`Re/Im(HH·VV*)`), which requires preserved phase. Two
diagnostic tests bracket the paper's target from opposite sides:

- **Full coherent DOP** (as computed throughout this investigation): 0.63–0.85 — far **above** target.
- **Power-only DOP** (`|S2|/S1`, dropping the coherent cross-term entirely — the only formula real Level-2 SRI amplitude-only data can support): 0.003–0.033 (SLC-derived proxy) or 0.025–0.063 (verified against the real Level-2 SRI GeoTIFFs) — far **below** target.

The paper's 0.10–0.13 sits *between* these two extremes, and this behavior
persists even at whole-crater-interior aggregation (not small-sample noise —
hypothesis 2 already ruled that out), suggesting a systematic effect (e.g. a
residual geometric/topographic phase trend) rather than random noise in the
coherent cross-term.

**Most likely explanation:** the paper's DOP product is not derived from raw
Level-1A SLI complex (phase-preserving) data the way PRISM computes it — it's
more consistent with a different processing level, an undocumented
noise/topography correction, or a different polarimetric basis (their only
DOP-interpretation citations are hybrid/compact-pol references, not standard
quad-pol ones). This cannot be resolved further without the paper's
**Supplementary Table 1** (lists their exact acquisitions/processing, not
publicly available) or direct correspondence with the authors.

---

## Recommendation

1. **Do not re-try hypotheses 1–8** — every calibration, processing, and
   acquisition-level avenue reachable from public/institutional sources has
   been exhausted and honestly reported.
2. **Use PRISM's CPR-based criterion as the validated ground-truth metric**
   going forward — it already matches the paper's own numbers well, on the
   same real data.
3. If pursuing DOP further becomes worthwhile, the only remaining productive
   step is obtaining Sinha et al.'s Supplementary Table 1, or direct
   correspondence with the authors about their exact DOP processing chain.

## Where the work lives

- Scripts: `src/dop_pipeline_v2_*.py` (8 independent hypothesis scripts, none
  modifying each other or the original `src/candidate_dop_pipeline*.py`
  pipeline), `src/paper_crater_pipeline.py`, `src/paper_criterion_pipeline.py`.
- Outputs: `outputs/objective1/dop_v2/`, `outputs/objective1/dop_secondary/`,
  `outputs/objective1/paper_crater_validation/`, `outputs/objective1/paper_criterion/`.
- This document supersedes the informal working notes; it is the
  single source of truth for the DOP ground-truth investigation.

---

## Addendum, 2026-08-26 — the Supplementary Material arrived, and it changes two conclusions above

This document's own closing recommendation was: obtain Sinha et al.'s Supplementary
Table 1. That has now happened. It does **not** resolve the DOP discrepancy, but it
invalidates how one hypothesis was closed and contradicts the recommendation this
document ends on. Full analysis: `SINHA_SUPPLEMENTARY_FINDINGS.md`. In brief:

**1. Hypothesis 8 is reopened — "wrong acquisition" is untested, not ruled out.**
Supplementary Table 1 lists the six acquisitions the authors actually used:
`ch2_sar_ncls_20200808t201154198_d_cp_d18` (**compact-pol**), and full-pol
`20191009t103018034`, `20191113t183130223`, `20201019t092257302`,
`20201022t140200748`, `20220909t150312532_d_fp_d32`. PRISM used
`20200321t082617351` for hypotheses 1–7 and `20191105t180525404_d_fp_m65` for
hypothesis 8. **Neither is on that list.** Demonstrating that a seventh, unrelated
acquisition also yields high DOP says nothing about whether theirs do. (Entry #4 was
seen and rejected during the hypothesis-8 footprint search because it misses F2 by
~2.8 km — correct for a single-acquisition test, but it means one of their own
datasets was discarded rather than followed up, e.g. on F3 alone, which it does cover.)

**2. The recommendation to lean on CPR instead of DOP is wrong as stated.**
Supplementary Figure 6 reports the exterior of F2 — rough terrain — at mean CPR 1.1
and mean DOP 0.17, and concludes that "high CPR alone is insufficient and that the
combined CPR-DOP criterion is required to distinguish roughness driven scattering from
subsurface volumetric scattering." So the metric this document validated is the one the
authors say cannot separate ice from rough rock unaided, and the metric it recommended
de-emphasising is the discriminator. CPR agreement remains real and remains PRISM's
strongest external validation — of the *radar processing and geolocation*, not of ice.
DOP is an open problem blocking a complete criterion, not a metric to set aside.

**3. The stop rule stands, and does not cover what is now available.** Hypotheses 1–8
should still not be re-run as they were. Three genuinely new avenues exist: the authors'
own full-pol acquisitions; a compact-pol / hybrid-basis DOP on their compact-pol dataset
(the m-χ formalism this document already identified as the leading explanation, now
confirmed present in their data); and Zhao et al. 2024's low-quality range-area removal
(−30 dB antenna isolation), which PRISM has never applied and which could leave the
F2/F3 covariance terms noise-dominated regardless of calibration quality.

**4. One open question elsewhere is now closed.** The Chandrayaan-2 DFSAR User Manual
(SAC/SIPG/MDPD/CH2/SAR/2020/12/23 v1.0) was read in full: it is a 7-page PDS4 archive
document and defines **no** DOP formula, CPR formula, or Stokes parameters. PRISM's use
of the general Stokes construction is not contradicted by vendor documentation because
no vendor definition exists. It also confirms Level-1A SLI is single-look complex
(phase-preserving) while Level-2A SRI is `Unsigned short int` (amplitude only) —
independently supporting this document's power-only-DOP note.
