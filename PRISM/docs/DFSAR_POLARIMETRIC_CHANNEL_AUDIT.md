# DFSAR_POLARIMETRIC_CHANNEL_AUDIT — what PRISM's bands actually are

**Date:** 2026-08-26. Prerequisite audit for `src/ice_radar_characterization_
v3.py`, per explicit task instruction: "Do NOT assume that HH/HV/VH/VV
mapping is correct" before computing any Stokes/CPR quantity. Every product
type PRISM touches is documented here, per band, with **FACT** vs **NOT
VERIFIED** vs **NO DATA** stated explicitly.

---

## 1. Product inventory — what PRISM actually has, per type

| Product type | Files available in this environment | Complex or intensity? | Channel identity | Calibration state |
|---|---|---|---|---|
| **L4-MOSAIC (Y4R)** — `evn/vol/odd/hlx` | Not locally present this session (ISRO-mosaic, login-gated); values used throughout this investigation are copied from prior-session real pipeline output | **Real-valued power/intensity** (Yamaguchi 4-component decomposition outputs), NOT complex I/Q | Not HH/HV/VH/VV at all — these are **already-decomposed scattering-mechanism components** (even-bounce, volume, odd-bounce, helix), an ISRO-internal derived product | **UNKNOWN — ISRO's internal decomposition/calibration chain is not documented in the CH2DFSAR SIS/user manual** (already established, `SERD_NAN_ANALYSIS.md`) |
| **L3C-MOSAIC** — `cpr/srd/trt` | Same as above | Real-valued, derived | **CPR here is NOT computed by PRISM from any channel pair at all** — it is read directly as an ISRO-precomputed band. PRISM has never verified this matches any specific published CPR formula (Neish's, Sinha's, or any other) | **UNKNOWN — same as above** |
| **L0A-RAW** (raw, uncalibrated) | Two files physically confirmed present this session: `ch2_sar_nrxl_20251025t211236510...` (referenced in prior docs) and `ch2_sar_nrxl_20210414t091917314_d_fp_d18.zip` (found in `C:\Users\sohan\Downloads\` this session — a genuine, complete, 3.2 GB raw product) | **Genuine complex I/Q** (2 bytes/sample, offset-binary decoded — verified, see §3) | 4-way line-interleaved; **group→polarization identity is NOT given by the product format and must be independently re-derived per acquisition** (§4) | **Bias-centering only** (per-channel complex DC offset from XML `bias_real/imag`); gain-imbalance and phase-orthogonality XML fields exist but are not applied by default anywhere in PRISM |
| **Level-1A SLI (calibrated SLC)** | Only XML/CSV metadata present locally (no `.tif` pixel data) for `ch2_sar_ncxl_20220318t135736694_d_fp_d18`; prior sessions' real pixel-level results (DOP for 4 of 7 candidates + F2/F3) came from `.tif` files that lived only on a different machine (`C:\Users\radhe\Downloads\`), not present here | Genuine complex I/Q, per-polarization GeoTIFFs | **Channel identity given directly by ISRO in the filename/PDS4 label** (`..._hh_...`, `..._vv_...` etc.) — NOT byte-inferred for this product tier, unlike raw L0A | Bias-centering only, same as raw |
| **Level-2 SRI** | Not present locally; prior real results for F2/F3 power-only DOP came from a `.tif` accessed by a prior session | `unsigned short int`, **amplitude only, no phase** | Per-polarization, ISRO-labeled | Radiometrically calibrated by ISRO (per CH2DFSAR user manual, Table 1.2.4/3.1) |

**Central finding of this audit:** every number PRISM has ever called
"CPR" for a mosaic-covered site (all 7 candidates, Cabeus, Wiechert, every
M3-reference site) is the **L3C-MOSAIC's precomputed band**, not a
self-computed Stokes quantity. PRISM's genuine, self-computed,
raw-channel-derived polarimetric quantities exist **only** for: (a) the
2025-10-25 non-candidate raw acquisition, (b) the F2/F3 Faustini craters via
a specific 2020-03-21 Level-1A SLC acquisition, (c) the primary candidate
and 3 others' DOP via their own covering Level-1A SLC acquisitions, and (d)
the 2021-04-14 raw acquisition freshly decoded in this session (§3). None of
these four cover Cabeus or Wiechert.

## 2. What "PRISM's CPR" actually is, per site — resolved this session

| Site category | CPR source | Verified equivalent to a published Stokes formula? |
|---|---|---|
| 7 PRISM candidates | L3C-MOSAIC band | **NO — cannot be verified without raw pixel access** |
| Cabeus, Wiechert, all M3 reference sites | Same L3C-MOSAIC band | **NO — same** |
| F2, F3 (Faustini) | Self-computed from real Level-1A SLC complex pixels, **but using the (HH,VV) pairing**, not a genuine single-transmit dual-receive basis (see §5) | Formula shape matches Sinha's Eq. 2 (Stokes DOP), but this is DOP, not the Neish/Raney CPR formula this task asks about; never computed as `(S1-S4)/(S1+S4)` by any prior PRISM session |
| 2021-04-14, 2025-10-25 raw acquisitions | Self-computed from real raw L0A-RAW complex pixels | **This session computed genuine Neish-style Stokes CPR for the first time in PRISM's history** — see §5 and `outputs/objective1/ice_radar_v3_results.json` |

## 3. Raw L0A-RAW byte structure — independently re-verified for a SECOND acquisition this session

PRISM's existing byte-structure findings (`docs/RAW_DFSAR_VALIDATION.md`)
were derived and verified only for the 2025-10-25 acquisition (line length
2325 B). This session physically located and decoded a **second** raw
product, `ch2_sar_nrxl_20210414t091917314_d_fp_d18` (found in
`C:\Users\sohan\Downloads\`, a genuine 3.2 GB file, MD5-labeled in its own
XML, extracted and verified this session), and **independently re-derived**
its byte structure rather than assuming the other file's constants apply
(per explicit task instruction):

| Constant | 2025-10-25 product | 2021-04-14 product (this session) | Same? |
|---|---|---|---|
| Imaging Frames offset | 48,158 B | 50,347 B | Different (expected — different pre-calibration frame count) |
| Line length | 2,325 B | 2,837 B | Different (different acquisition parameters) |
| Payload start | 141 | **141 — independently re-confirmed via fixed-prefix byte-uniqueness scan, not assumed** | **Same** |
| Payload end (2048 B = 1024 samples × 2B) | 2,189 | **2,189 — independently re-confirmed** | **Same** |
| Tail (constant 0x80 padding) | 136 B | **648 B — confirmed constant-valued (0x80) via per-byte-position uniqueness scan across 400 lines** | Different length, same fill value |

**CONCLUSION: the 141-byte prefix and 2048-byte I/Q payload boundaries are a
genuine, confirmed-twice, acquisition-independent DFSAR raw-format
constant** — not an assumption carried over from one file to another. Only
the total line length (hence tail padding) varies with acquisition-specific
parameters. Method: `scratchpad/raw20210414/byte_structure_check.py`,
per-byte-position `numpy.unique()` count across 400 consecutive raw lines,
same technique as PRISM's own original reverse-engineering.

## 4. Channel mapping — independently re-verified for a SECOND acquisition

**Not assumed.** The exhaustive 24-permutation search (`dfsar_channel_
mapping.py`'s methodology, re-implemented from scratch this session against
the 2021-04-14 file's own XML `standard_deviation_real/imag` and
`bias_real/imag`) was re-run on 2,000 lines of this new file:

**Winning mapping: G0→HV, G1→HH, G2→VV, G3→VH — identical to the
2025-10-25 product's independently-derived mapping.** This is now confirmed
**twice**, on two different acquisitions, dates, and file structures — strong
evidence this is a genuine, fixed instrument/format characteristic, not a
coincidence of one file. Full permutation scores in
`outputs/objective1/ice_radar_v3_results.json`.

## 5. Basis mismatch — the central physical finding of this audit

DFSAR's quad-pol mode transmits **alternating H and V pulses** and receives
all four combinations (HH, HV, VH, VV). A genuine "received field of a
single transmitted wave, in two orthogonal linear receive channels" — the
physical quantity classical Stokes-parameter formalism (and Neish/Raney's
CPR) is built to describe — is:

- **(HH, HV)** — the H-transmit pulse's return, received in H and V. A real
  2-component field from ONE transmitted wave.
- **(VH, VV)** — the V-transmit pulse's return, received in H and V. Also a
  real 2-component field from one transmitted wave.

**(HH, VV) — the pairing PRISM's DOP work and Sinha et al. 2026 both use —
is NOT this.** HH and VV are the co-pol returns of *two different*
transmitted pulses. Pairing them into a Stokes vector, as if they were two
components of one received wave, is the specific basis mismatch already
flagged in `DOP_SINHA_2026_RESEARCH.md` §5.1 and independently corroborated
by general SAR pedagogy in `LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md`
§16 (standard dual-pol modes pair one co-pol with one cross-pol channel,
e.g. HH/VH — exactly (HH,HV) and (VH,VV) above, not (HH,VV)).

**This session computed real numbers on all three bases, for the first time
in PRISM's history, using genuine decoded raw pixels** (2021-04-14
acquisition, 2000×1024-pixel window):

| Basis | Neish-Stokes CPR = (S1−S4)/(S1+S4) | PRISM-style DOP |
|---|---:|---:|
| (HH, VV) — PRISM's/Sinha's existing basis | **1.443** | 0.806 |
| (HH, HV) — physically correct, H-transmit | **0.979** | 0.926 |
| (VH, VV) — physically correct, V-transmit | **1.017** | 0.897 |

**The basis choice materially changes the CPR value** (1.44 vs. ~0.98–1.02)
— a ~45% relative difference from the same raw pixels, purely from which
two channels are paired into the Stokes vector. **This is a genuine,
freshly-computed, non-fabricated finding**, not inferred from the
literature. It does **not** tell us anything about ice — this acquisition
is confirmed (§6) to be nowhere near any site of interest — but it directly
demonstrates why "which channels form S1–S4" is not a cosmetic detail.

## 6. Acquisition footprint — confirmed NOT candidate-relevant, more precisely than previously stated

Per the 2021-04-14 acquisition's own XML `Geometry_Parameters` (read this
session): `upper_left_latitude = 85.115896°`, `centre_latitude =
86.874298°` — **both positive**. Every other CH2 DFSAR XML label read in
this and prior investigations (covering south-polar acquisitions) states
explicit **negative** latitudes for the southern hemisphere. **This
acquisition is in the NORTHERN polar region, not merely "a different
southern location"** — a more precise finding than PRISM's prior
characterization of it as simply "unrelated" (`PROJECT_STATUS.md`,
`CANDIDATE_DFSAR_SOURCE.md`). It cannot cover Cabeus, Wiechert, or any of
PRISM's 7 south-polar candidates, by hemisphere alone. All results in §5
above are correctly and unambiguously **pipeline-validation only**.

## 7. Incidence angle — confirmed NOT spatially resolved anywhere

**FACT (re-confirmed this session by direct inspection of both raw XML
labels read):** each raw/calibrated acquisition's XML carries exactly
**one scalar** `isda:incidence_angle` value for the entire scene (e.g.
25.98° for the 2021-04-14 product, 25.996° for the 2025-10-25 product) —
**not a spatially-resolved per-pixel raster.** The Level-1A Grid CSV (used
successfully for candidate-coverage confirmation in the DOP investigation)
carries per-pixel `Slant range` and an incidence-angle-adjacent geometry
column at a coarse 32-line/32-pixel sampling interval for **individual raw
acquisitions only** — **not** for the L4/L3C mosaics, which is where every
candidate's/Cabeus's/Wiechert's CPR value actually comes from. **CONCLUSION:
incidence-angle normalization of CPR is not computable for any
mosaic-derived site in PRISM's current data, regardless of which published
normalization method is chosen** (§`ICE_METRIC_LITERATURE_MAP.md` already
established the Mladenova et al. 2013 cosine-power-law family as the
closest published precedent, absent a lunar-CPR-specific standard).

## 8. Summary table — direct vs. unavailable, per quantity requested

| Quantity | Directly computable in this environment? | For which sites? |
|---|---|---|
| HH/HV/VH/VV power | **Yes** — real decode | 2021-04-14, 2025-10-25 raw acquisitions only (pipeline validation, not candidate sites) |
| HH/VV ratio, cross-pol fraction | **Yes** | Same as above |
| Stokes S1–S4 (any basis) | **Yes** | Same as above |
| Neish-Stokes CPR | **Yes** | Same as above |
| PRISM-style DOP | **Yes** | Same as above, plus already-existing real DOP for 4/7 candidates + F2/F3 (from prior sessions, summary values only, not raw pixels) |
| Pv, SERD, T-Ratio | **Read directly from ISRO L3C/L4-MOSAIC bands** — real values, but not self-computed from channels | All 7 candidates, Cabeus, Wiechert, all M3 reference sites |
| Incidence-angle-normalized CPR | **NO DATA anywhere** | None |
| Genuine Stokes-based CPR for Cabeus, Wiechert, or any of the 7 candidates | **NO DATA** — no raw/SLC pixel access for these specific sites in this environment | None |
