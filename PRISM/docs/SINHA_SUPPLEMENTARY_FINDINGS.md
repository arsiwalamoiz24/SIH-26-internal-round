# Sinha et al. 2026 Supplementary Material — what it settles, and what it reopens

**Date:** 2026-08-26. **Source:** the paper's own Supplementary Information
(`44453_2026_38_MOESM1_ESM.pdf`, 9 pages), read directly this session, together with
the Chandrayaan-2 DFSAR User Manual (SAC/SIPG/MDPD/CH2/SAR/2020/12/23 v1.0) and the
full text of Zhao et al. 2024 (IEEE TGRS 62:5208317). None of these documents are
committed to this repo — they are third-party copyrighted PDFs supplied by the team.
Cite them by the identifiers above.

**Why this document exists:** `DOP_GROUND_TRUTH_INVESTIGATION.md` closed with
"the only remaining productive step is obtaining Sinha et al.'s Supplementary
Table 1." That table is now in hand. It does not resolve the DOP discrepancy, but it
**invalidates the way one of the eight hypotheses was closed**, and the supplement's
Figure 6 **contradicts the recommendation that investigation ended on**. Both are
corrected here and in the files that carried the old wording.

---

## 1. Supplementary Table 1 — their actual acquisitions

The table lists exactly six DFSAR datasets used in the study:

| # | DFSAR Data ID | Mode |
|---|---|---|
| 1 | `ch2_sar_ncls_20200808t201154198_d_cp_d18` | **compact-pol** (`_cp_`) |
| 2 | `ch2_sar_ncxl_20191009t103018034_d_fp_d18` | full-pol |
| 3 | `ch2_sar_ncxl_20191113t183130223_d_fp_d18` | full-pol |
| 4 | `ch2_sar_ncxl_20201019t092257302_d_fp_d18` | full-pol |
| 5 | `ch2_sar_ncxl_20201022t140200748_d_fp_d18` | full-pol |
| 6 | `ch2_sar_ncxl_20220909t150312532_d_fp_d32` | full-pol |

**PRISM has never run its DOP pipeline on any of these.** Hypotheses 1–7 all used
`ch2_sar_ncxl_20200321t082617351_d_fp_d18`; hypothesis 8 used
`ch2_sar_ncxl_20191105t180525404_d_fp_m65`. Neither appears above.

Entry #4 *was* seen by PRISM: the hypothesis-8 footprint search checked
`20201019t092257302` and rejected it because its footprint misses F2 by ~2.8 km
(it does cover F3). That rejection was correct for a single-acquisition test, but it
means PRISM discarded one of the paper's own datasets rather than following it up —
for example by testing F3 alone against it, or by combining acquisitions the way a
study using six of them presumably does.

### Consequence: hypothesis 8 is reopened

Hypothesis 8 was recorded as "closes off 'wrong acquisition' as an explanation."
That conclusion does not survive this table. It was reached using an acquisition
(`20191105t180525404_d_fp_m65`) that is **not one the authors used**. Showing that a
seventh, unrelated acquisition also yields high DOP says nothing about whether *their*
six do. The honest status is: **untested**, not "ruled out."

### Entry #1 is compact-pol, which matches the investigation's own leading hypothesis

`DOP_GROUND_TRUTH_INVESTIGATION.md` diagnosed the mismatch as most likely
"a different polarimetric basis," noting that the paper's only two DOP-interpretation
citations (Raney et al. 2012 m-χ; Mohan et al. 2011 Mini-SAR) are **hybrid/compact-pol**
references rather than quad-pol ones. Supplementary Table 1 confirms a real compact-pol
DFSAR dataset was in the study. That elevates the hypothesis from inference to something
directly testable: compute DOP the compact-pol way (Stokes vector from a transmitted
circular / received orthogonal-linear basis) on acquisition #1, rather than the linear
quad-pol Stokes construction PRISM currently uses.

This is a genuinely new avenue and it is **not** one of the eight already closed. The
existing stop rule ("do not re-try hypotheses 1–8") stands as written and does not
cover it.

---

## 2. Supplementary Figure 6 — CPR alone is explicitly insufficient

Quoting the caption directly (F2's exterior region, ROI shown in their Fig. 6b):

> "Note that <2% pixels within the ROI show elevated CPR pixels, having an average CPR
> and DOP values as 1.1 and 0.17, respectively. It is important to note here that while
> regions outside the crater characterized by rough surfaces show localized elevated CPR
> values (1.1), they are associated with higher DOP (0.17), exceeding the proposed
> threshold of 0.13. Moreover, **this also demonstrates that high CPR alone is
> insufficient and that the combined CPR-DOP criterion is required to distinguish
> roughness driven scattering from subsurface volumetric scattering.**"

This is the authors pre-empting exactly the roughness confound that makes elevated CPR
ambiguous — and answering it with DOP. In their framework **DOP is the discriminator**;
CPR is a necessary but not sufficient screen.

### Consequence: the "use CPR as the validated criterion" recommendation is wrong as stated

`DOP_GROUND_TRUTH_INVESTIGATION.md` recommended: "Use PRISM's CPR-based criterion as
the validated ground-truth metric, and de-emphasize DOP matching." On 2026-08-26 that
wording was propagated into the frontend, `DECISIONS.md`, `TODO.md` and
`F2_F3_final_comparison_summary.json` (commit `d3ce772`).

The reasoning behind it was sound on the evidence then available — CPR reproduces the
paper's numbers, DOP does not, so lean on the one that validates. The supplement shows
why that is not safe: **the metric PRISM validated is the one the authors say cannot
separate ice from rough rock on its own, and the metric PRISM dropped is the one that
does the separating.** Ranking candidates on CPR alone will rank rough terrain and
subsurface ice identically, which is precisely the failure mode the paper warns about.

**Corrected position, now carried in all those files:**

- CPR agreement remains real, and remains PRISM's strongest external validation — it
  confirms the radar processing, the crater geolocation, and the acquisition handling.
- CPR is **not** sufficient evidence of ice on its own, by the source paper's own
  explicit statement.
- DOP remains unreconciled *and* necessary. It is not de-emphasised; it is an open
  problem blocking a complete criterion.
- Any PRISM candidate ranking built on CPR alone must say that it cannot distinguish
  volumetric scattering from surface roughness.

---

## 3. The nine craters and their built-in controls

Supplementary Figures 4 and 5 name every ROI in the study:

**Nine doubly-shadowed craters** — F1, F2, F3 (in Faustini), H1, H2, H3 (Haworth),
S1, S2, S3 (Shoemaker).

Supplementary Figure 5 gives per-crater histograms of interior CPR and annotates in red
"the craters ... having relatively higher number of CPR elevated pixels":

| Elevated CPR (their red annotation) | Not elevated |
|---|---|
| **F2, F3, H3, S1** | F1, H1, H2, S2, S3 |

**Three control ROIs** — Tooley crater floor, Tooley crater wall, and the exterior
region surrounding H3 (Supplementary Figure 3 describes that exterior as dominated by
impact melt flow deposits extending 3–5 crater radii from the rim). F2's exterior
(§2 above) is a fourth, with published values.

**Why this matters more than any control set PRISM could assemble.** All nine craters
are small, doubly-shadowed, inside PSRs, in the same thermal environment, of the same
morphological class. The 4-vs-5 split therefore controls for sampling scale, shadowing
and crater morphology *by construction* — the confounds that a whole-crater or
random-disk control set cannot separate. If PRISM's pipeline reproduces that ordering,
it is evidence the pipeline responds to whatever distinguishes those four; if it does
not, the CPR agreement at F2/F3 was coincidental.

`src/nine_crater_validation_pipeline.py` implements this test. It needs the coordinates
and diameters of the seven craters other than F2/F3, which are in the main paper, not
the supplement.

**A limit to state plainly:** that pipeline tests **CPR ordering only**. PRISM's DOP
requires Level-1A SLC (phase-preserving) data, while the L4/L3C mosaics the pipeline
reads are amplitude-derived products. So it cannot evaluate the combined CPR-DOP
criterion the paper says is required — it tests the necessary half, not the sufficient
one.

---

## 4. The DFSAR User Manual does not define DOP or CPR

`TODO.md` carried an open question: is there a vendor/documented Chandrayaan-2-specific
DOP formula? The manual was read in full this session. It is a 7-page PDS4 archive
document covering bundle structure, product levels and file formats. It contains **no
DOP formula, no CPR formula and no Stokes-parameter definitions** — searched for
"degree of polarization", "DOP", "Stokes", "m-chi": zero hits.

So PRISM's use of the general Stokes construction is not contradicted by vendor
documentation, because no vendor definition exists to contradict it. The question is
answered, negatively, and can be closed.

Two incidental confirmations from the manual, both consistent with existing PRISM notes:

- Level-1A SLI is single-look complex (`ComplexLSB8`, I/Q interleaved, 4 bytes each) —
  phase-preserving, which is what DOP needs.
- Level-2A SRI is `Unsigned short int` — amplitude only. This independently confirms the
  investigation's note that real Level-2 SRI data can only support a power-only DOP.

---

## 5. Zhao et al. 2024, in full — one new untested hypothesis

PRISM already cites Zhao et al. 2024 for its CPR formula (their Eq. 10) and the
azimuth multilook number (their Eq. 7, `MLN = ⌈output_pixel_spacing/output_line_spacing⌉`,
used in hypothesis 5). The full text is now available and contains a step PRISM has
never applied:

**Low-quality range-area removal.** Zhao et al.'s framework identifies and removes
portions of a DFSAR image where the estimated crosstalk exceeds the instrument's own
−30 dB antenna-isolation specification, on the argument that such areas are
noise-affected. They evaluate >900 DFSAR scenes this way.

PRISM's DOP work has never checked whether the F2/F3 windows fall inside such a
low-quality range region. If they do, the covariance terms driving DOP could be
noise-dominated regardless of how well the calibration is solved — which would be
consistent with hypothesis 7's finding that a correctly-implemented Ainsworth solve
returns small, plausible crosstalk yet barely moves DOP.

Call this **hypothesis 9**. Like the compact-pol avenue in §1, it is outside the closed
set of eight and is a legitimate thing to test.

---

## Where this leaves the DOP question

Three live avenues, replacing the previous "nothing left but contacting the authors":

1. **Run the DOP pipeline on the paper's own acquisitions** (Supplementary Table 1,
   entries 2–6 for full-pol), rather than on the two unrelated acquisitions used so far.
2. **Compute compact-pol / hybrid-basis DOP** on entry #1, matching the m-χ formalism the
   paper's own citations point to, instead of the linear quad-pol Stokes construction.
3. **Apply Zhao et al. 2024's low-quality-area removal** before computing DOP, and check
   whether the F2/F3 windows survive it.

The stop rule on hypotheses 1–8 is unchanged — none of these three repeats any of them.
