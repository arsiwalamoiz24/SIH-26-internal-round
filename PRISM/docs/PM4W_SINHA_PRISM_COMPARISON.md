# PM4W_SINHA_PRISM_COMPARISON — three-way method audit and implementation plan

**Date:** 2026-08-26. **Objective unchanged: physics-based lunar water-ice
detection.** No new score, no new weights, no threshold tuning, no ranking
change anywhere in this document — per explicit task instruction.

---

## 1. Sinha et al. 2026 — re-audited against PM4W's completeness standard

Full detail: `docs/DOP_SINHA_2026_RESEARCH.md` (unchanged, not re-litigated
here). Summary, structured to match PM4W's audit format:

| Item | Sinha et al. 2026 |
|---|---|
| Exact Stokes construction | `m = √(S2²+S3²+S4²)/S1` (their Eq. 2) — formula shape confirmed, **channel-to-Stokes construction NEVER stated** ("S1,S2,S3,S4 are real numbers known as stokes parameters" — no further definition) |
| Channel mapping | **Never stated.** Their own data is confirmed quad-pol (HH/HV/VH/VV) acquisition, but which two channels (or which combination) form S1–S4 is not specified anywhere in the accessible text |
| CPR equation | `CPR(μc) = (a+b+2√ab)/(a−b... )` from **σ°HH, σ°VV power only** (their Eq. 1) — a **power-only, no-cross-term, no-phase** construction, mathematically **different from PM4W's/Neish's `(S1−S4)/(S1+S4)`** despite both being called "CPR" |
| DOP equation | Same shape as PM4W's `m`, channel construction unstated (see above) |
| Covariance/coherency construction | Not stated |
| Multilooking | Not stated |
| Calibration | Not stated |
| Acquisition/product | "Calibrated" DFSAR data (Data Availability statement) — processing level (raw/Level-1A/Level-2) not specified; acquisition date/ID not given in main text; Supplementary Table 1 exists but was not retrievable |
| Thresholds | CPR>1 & DOP<0.13 (refined from a prior 0.35, attributed to Verma et al. 2025 and Mishra et al. 2014) |
| Spatial resolution | Not stated (only a generic 2–75 m/px hardware spec) |

## 2. Three-way comparison: PM4W vs. Sinha vs. PRISM

| Dimension | PM4W (Wang et al. 2025) | Sinha et al. 2026 | PRISM (current) |
|---|---|---|---|
| Instrument | LRO Mini-RF, hybrid-pol hardware | Chandrayaan-2 DFSAR, quad-pol hardware | Chandrayaan-2 DFSAR (same as Sinha) |
| Stokes basis | **Genuinely correct** — single circular transmit, dual linear receive (hardware-enforced) | **Unstated** — quad-pol data, channel pairing never specified | HH/VV pairing (self-acknowledged non-standard, `DOP_SINHA_2026_RESEARCH.md` §5.1), or (for the 2 non-candidate acquisitions with raw access) HH/HV or VH/VV — a **linear**-transmit hybrid basis, not equivalent to Mini-RF's **circular**-transmit hybrid basis |
| CPR formula | `(S1−S4)/(S1+S4)` — Stokes-based, from a genuine hybrid-pol receive pair | `(σHH+σVV+2√(σHHσVV))/(σHH+σVV−2√(σHHσVV))` — power-only, HH/VV based, **no cross term, no phase** | ISRO L3C-MOSAIC precomputed band — formula never verified against either of the above |
| DOP threshold | m<0.2, tied to an explicit sensitivity analysis showing the inflection point | DOP<0.13, attributed to prior work, no stated derivation of the 0.13 figure itself in the accessible text | PRISM's own DOP consistently 0.63–0.86, meets neither threshold under any tested basis |
| CPR threshold | C>1, same sensitivity-analysis justification | CPR>1 (per Sinha's ref. to the prior 0.35/1.0-family criterion) | PRISM's real interior-mean CPR across 18 tested sites never exceeds ~0.48 (Shackleton, the highest); **per-pixel** fractions exceeding CPR>1 do exist (up to ~11% of interior pixels for some candidates) — mean-based and pixel-based comparisons are not the same test |
| Roughness handling | **Explicit dedicated tier** — 9×9 fractal-dimension filter on radar backscatter intensity | **Not addressed at all** in the accessible text | V2's `roughness_context` — an explicitly-labeled **provisional** cross-site heuristic on DEM-derived hazard, not a validated model, not radar-intensity-domain |
| Thermal/illumination handling | Explicit tier: T<110K, illumination<0.2, both used as hard filters | Not addressed | **Real, already-computed illumination fraction for every site tested — already passing PM4W's own 0.2 threshold everywhere** (§ PM4W doc §4); no temperature data ingested |
| Decision rule | Hard multi-tier AND-gate, per-pixel | Two-condition AND (CPR>1 & DOP<0.13), per their own stated refined criterion | Continuous percentile composite (v1, now known unvalidated) or ordinal evidence tier (V2) — **neither is an AND-gate on physical thresholds** |
| Own validation vs. independent evidence | Real, quantified, honestly reported (60% pixel / 11% area vs. M3) | Not found in the accessible text | Real, quantified, honestly reported (`INDEPENDENT_ICE_VALIDATION.md`, `POSITIVE_NEGATIVE_CONTROL_VALIDATION.md`) — PRISM's own validation culture is, if anything, more rigorous and more transparent than either published paper's accessible text |

**The single most important three-way finding:** **"CPR" is not one
quantity across these three sources.** PM4W's CPR is a genuine Stokes
`(S1−S4)/(S1+S4)` construction from a hardware-correct hybrid-pol receive
pair. Sinha's CPR is a power-only `σHH,σVV` ratio with no cross-term or
phase information at all. PRISM's CPR (for every candidate, Cabeus, and
Wiechert) is an ISRO-internal precomputed quantity of unverified formula.
**Comparing "PRISM's CPR is 0.166 at Cabeus" against "Neish's CPR is
0.25±0.12 at Cabeus" against "PM4W's CPR>1 threshold" is comparing three
quantities that share a name, not a formula** — already correctly caveated
qualitatively in `POSITIVE_NEGATIVE_CONTROL_VALIDATION.md` and
`ICE_RADAR_V3_REDESIGN.md` Q1/Q3, and now confirmed as a genuine three-way
divergence, not a two-way one.

## 3. Verma et al. 2025 — what it challenges, and what remains unverified

Full detail: `ice_validation_icarus2025_cpr_dop_literature.md` (prior
session's research notes) and `DOP_SINHA_2026_RESEARCH.md` §6.2. Access
remains **fully blocked** (ScienceDirect, two independent investigation
attempts) — every claim below is search-summary confidence, explicitly not
elevated to fact:

- **Challenges to PM4W/Sinha assumptions:** Verma 2025 reportedly attributes
  some CPR>1 occurrences "primarily to surface roughness," directly
  supporting PM4W's own design decision to add a dedicated roughness filter
  (§ PM4W doc §1.7) rather than relying on CPR/DOP thresholds alone — a
  genuine point of *agreement* between Verma's critique and PM4W's own
  architecture, not a contradiction.
- **CPR limitations:** consistent with Neish (2011), Carter (2012), Eke
  (2014), Fa (2018) — all independently confirmed, full text, in this
  investigation.
- **DOP behavior:** Verma reportedly finds DOP<0.13 for 4 specific craters
  and reports an inverse CPR-DOP relationship — **the specific quantitative
  figure (R²~0.99) remains explicitly UNVERIFIED** and is not used as fact
  anywhere in this document.
- **Mixed ice/regolith interpretation:** consistent with Neish 2011's own
  interpretation (low CPR does not rule out fine-grained ice mixed into
  regolith) — this is now a convergent theme across Neish 2011 (confirmed),
  PM4W's own stated limitations (§ PM4W doc §3), and Verma 2025's reported
  (unverified) findings.
- **Known false positives:** roughness/double-bounce geometry (Carter 2012,
  confirmed), consistent with PM4W's own explicit design rationale for its
  fractal-roughness tier.

**No disagreement was found between Verma 2025 and PM4W** on the general
roughness-caution theme — they are directionally consistent, for whatever
that is worth given Verma's access limitation. **The disagreement that
matters is between Sinha 2026 and PRISM's own reproduction attempt**
(`DOP_SINHA_2026_RESEARCH.md`, unchanged), not between Verma and PM4W.

---

## 4. LIST A — Can implement now

Published methodology clear, required PRISM data already available:

1. **Illumination filter (<0.2)** — PRISM already computes this correctly
   for every site tested; simply apply the PM4W threshold to already-real
   numbers. (Every site already passes.)
2. **Per-pixel CPR>1 fraction as a PM4W-tier-1-style proxy** — PRISM
   already records `cpr_pct_gt1_inside` for all 7 candidates (real,
   already-computed, from the L3C-MOSAIC band). This is not a verified
   equivalent of PM4W's Stokes CPR (§2 above), but it is a real, available,
   already-computed pixel-fraction statistic that could be reported
   alongside PM4W's own threshold for qualitative (not formula-verified)
   comparison.
3. **Y4R total power → dB backscatter, as a rough σ°_LH analogue** —
   theoretically computable from data PRISM already has (evn+vol+odd+hlx,
   linear scale), though not verified equivalent to Mini-RF's specific LH
   channel/calibration convention.

## 5. LIST B — Can implement after obtaining data

Published methodology is clear; PRISM lacks the required data:

1. **Genuine Stokes CPR/DOP/phase/decomposition for Cabeus, Wiechert, and
   all 7 candidates** — requires an authenticated PRADAN session to find
   and download covering raw/Level-1A SLC acquisitions (3 of 7 candidates
   have never even had this search performed).
2. **Fractal-dimension roughness on DFSAR backscatter intensity** — a
   straightforward equation (Eq. 4) once real S1 imagery exists per
   candidate; not yet computed anywhere in PRISM.
3. **Diviner per-candidate temperature (<110K test)** — no ingestion
   pipeline exists yet; would need a direct PDS/Diviner archive query per
   candidate coordinate.
4. **A genuine Mini-RF ingestion pipeline** — PM4W's own method, run on its
   own native instrument, would sidestep DFSAR's basis-mismatch problem
   entirely (§2's central finding) — this is arguably the single highest-
   leverage new data source, not previously considered anywhere in this
   investigation.
5. **The `w` metric and Eq. 7's both-decompositions-vs-either ambiguity** —
   need a cleaner primary-source read (or direct author contact) before
   this can move from "unresolved" to "implementable."

## 6. LIST C — Scientifically unresolved

Papers disagree, or the equation/interpretation cannot be established:

1. **What PRISM's own "CPR" (L3C-MOSAIC band) formula actually is** —
   ISRO's internal algorithm is undocumented; cannot be reconciled with
   either PM4W's or Sinha's CPR without ISRO providing it.
2. **Whether Sinha et al. 2026's DOP construction resembles PM4W's Mini-RF
   hybrid-pol basis, PRISM's HH/VV quad-pol basis, or neither** — Sinha's
   own paper does not say.
3. **PM4W's own `w` metric definition** (α/γ terms unresolved).
4. **Whether PM4W's Eq. 7 requires both decomposition variants to agree or
   either to pass.**
5. **The exact quantitative CPR-DOP relationship Verma 2025 reportedly
   proposes** — access remains fully blocked; qualitative direction only.
6. **Whether DFSAR (quad-pol, linear-transmit) can ever produce a Stokes
   construction physically equivalent to Mini-RF's (hybrid-pol, circular-
   transmit) one** — this is not merely a missing-data problem (List B); it
   may be a fundamental instrument-architecture limitation. Flagged
   explicitly as *possibly* List C rather than List B, pending expert
   radar-polarimetry input beyond what literature review alone can resolve.

---

## 7. Final answer: minimum changes required

**"What is the minimum set of changes/data required to turn PRISM into a
physics-based ice detector that can be validated against PM4W + Sinha +
independent M3/LCROSS evidence?"**

### 1. Code changes (design only — none implemented in this task, per instruction)
- A new, clearly-separate module (not V2, not V3 — a genuine PM4W-style
  reproduction would be its own file) implementing the exact PM4W AND-gate
  logic on whatever real channels are ultimately available, reusing
  `ice_radar_characterization_v3.py`'s already-correct `stokes_parameters()`
  and `neish_stokes_cpr()` functions unchanged (same Stokes-CPR formula
  PM4W uses).
- A fractal-dimension roughness function (Eq. 4), applied to real DFSAR/
  Mini-RF backscatter intensity, not DEM elevation — a genuinely new
  metric, not a re-labeling of `compute_roughness_rms`.
- A Diviner ingestion function, per-candidate-coordinate temperature query.
- (Highest leverage, largest new effort) A Mini-RF ingestion pipeline,
  parallel to PRISM's existing DFSAR pipeline.

### 2. Data we need
- Authenticated PRADAN access, specifically targeted at Cabeus, Wiechert,
  and the 3 never-searched candidates.
- Mini-RF Level-2 data for PRISM's candidate coordinates (public, PDS
  Geosciences Node — noted as accessible without login in
  `LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md` §26).
- Diviner per-candidate temperature (same public PDS access).
- PM4W's supplementary material or direct author contact, to resolve the
  `w` metric and Eq. 7 ambiguity.
- Verma et al. 2025's full text (still blocked) or direct author contact.

### 3. Equations
All already extracted verbatim (§ PM4W doc §1, §7) — no new derivation
needed except the unresolved `w` metric. Sinha's equations remain
under-specified at the source (not something PRISM can independently
resolve without the paper providing more detail or Supplementary Table 1).

### 4. Validation sites
Cabeus (positive, Level-1 LCROSS), Wiechert (negative, Level-1 M3),
Shackleton (PM4W's own best-agreement site with M3 — a natural third
anchor point spanning two independent methodologies), Faustini and de
Gerlache (PM4W's other flagged priority sites), then PRISM's own 7
candidates as the genuinely unknown test set.

### 5. Validation metrics
- Pixel-level and area-level consistency against M3, computed the same way
  PM4W itself reports it (60%/11% is PM4W's own bar — PRISM should report
  its own numbers on the same two-part scale for direct comparability).
- Positive-control tier assignment (Cabeus should pass more AND-gate tiers
  than Wiechert, at minimum on illumination and, if computable, temperature
  — CPR/DOP tiers may legitimately fail per Neish 2011, and that is not a
  pipeline failure, per `ICE_RADAR_V3_REDESIGN.md`'s already-established
  framing).
- Cross-instrument agreement rate (DFSAR-derived vs. Mini-RF-derived,
  where both exist for the same site) — not yet possible without Mini-RF
  ingestion.

### 6. Expected outputs
A per-pixel (or per-candidate-window, given PRISM's likely resolution
constraints) PASS/FAIL AND-gate result, structurally distinct from both
V1's continuous score and V2's evidence tier — a third, complementary
output type, not a replacement for either.

### 7. What remains impossible to validate
- **Formula-level equivalence between PRISM's ISRO-precomputed CPR and any
  published Stokes CPR formula** — impossible without ISRO documenting its
  internal algorithm, regardless of what other data PRISM acquires.
- **Sinha et al. 2026's exact method** — impossible without their
  Supplementary Table 1 or direct author response (unchanged from
  `DOP_SINHA_2026_RESEARCH.md` §17).
- **Whether DFSAR can ever be made physically equivalent to Mini-RF's
  hybrid-pol basis** — genuinely open (List C item 6), possibly requiring
  expert input beyond a literature-review methodology.
- **PM4W's own `w` metric**, until its equation is fully resolved from a
  primary source.
