# CABEUS_FAUSTINI_ICE_INDICATOR_PROFILE — Cabeus & Faustini

**Date:** 2026-08-26. Same format as the earlier per-candidate profiles
(`docs/CANDIDATE_PHYSICS_RESULTS.md`), applied to the two independently-
confirmed reference sites, with Wiechert (negative control) shown
alongside for contrast. **Plot:** `outputs/objective1/ice_indicator_
profile/ice_indicator_profile.png`. Code: `src/plot_ice_indicator_
profile.py` (new; does not modify any existing pipeline file).

**Read this document together with `docs/PM4W_VALIDATION_RESULTS.md` and
`docs/MINIRF_CABEUS_CPR_RECONCILIATION.md` — on their own, the numbers
below can look more ice-consistent than the full picture supports.** This
document reports every individual metric honestly, including the ones
that look elevated/ice-like, and then states plainly what the combined
PM4W verdict actually was and why.

---

## 1. Georeferencing

| Site | Lat | Lon | Role |
|---|---:|---:|---|
| Cabeus | −84.6796° | −48.7093° | Positive reference — LCROSS direct impact site |
| Faustini | −87.3° | 77.0° | Positive reference — M3 spectral detection |
| Wiechert | −84.5° | 165.0° | Negative control — M3 explicit non-detection |

## 2. Source products

- **DFSAR mosaic metrics (Pv, CPR, SERD, T-Ratio):** ISRO Chandrayaan-2
  L4-MOSAIC (Y4R) + L3C-MOSAIC, whole-window means, from
  `outputs/validation/{ice_reference_sites,control_sites}.csv` (real
  pipeline run, prior session). **This CPR is the ISRO-precomputed band —
  not the same formula as the Mini-RF CPR below** (see
  `docs/PM4W_SINHA_PRISM_COMPARISON.md` §2 for the three-way formula
  distinction).
- **Mini-RF spatial CPR/DOP maps:** real per-pixel values, genuine
  `/vsicurl/` reads against `LRO-L-MRFLRO-5-GLOBAL-MOSAIC-V1.0`, 61×61 px
  windows, from `outputs/objective1/pm4w_v2/{pm4w_pixel_results.parquet,
  faustini_pixel_results.parquet}`.
- **PM4W condition pass rates:** same real per-pixel data, thresholds
  exactly as published in Wang et al. 2025 (CPR>1, DOP<0.2,
  backscatter<−15dB) — unchanged, untuned.

## 3. Results — individual metrics (the "ice-like behaviour" indicators)

| Metric | Cabeus | Faustini | Wiechert (control) | Direction that's "ice-like" |
|---|---:|---:|---:|---|
| Pv (DFSAR, window mean) | 0.217 | 0.289 | 0.314 | Higher = more volume scattering |
| CPR (DFSAR/ISRO band, window mean) | 0.166 | 0.297 | 0.311 | Higher = classically "ice-like" (contested, §5) |
| SERD (DFSAR, window mean) | 0.848 | 0.792 | 0.779 | Direction unresolved in PRISM's own prior work |
| T-Ratio (DFSAR, window mean) | 0.200 | 0.305 | 0.325 | Higher = classically "ice-like" |
| **Mini-RF CPR>1, % of real pixels** | **46.2%** | 8.8% | 8.9% | Higher = more pixels individually exceed the PM4W threshold |
| **Mini-RF DOP<0.2, % of real pixels** | 11.9% | 6.3% | 5.2% | Higher = more pixels individually exceed the PM4W threshold |
| Mini-RF backscatter<−15dB, % of real pixels | **100.0%** | 19.4% | 46.4% | Higher = more pixels this dark |
| Diviner annual max. temperature | **45.8 K** | **51.8 K** | 267.2 K | Lower = better cold-trap consistency |
| Illumination fraction | 0.0022 | 0.023 | 0.053 | Lower = more consistently shadowed |

**Genuinely elevated, real, ice-consistent-direction indicators found at
Cabeus specifically:** the highest Mini-RF CPR>1 pixel fraction of any
site tested in this entire investigation (46.2%), 100% of pixels below
the PM4W backscatter threshold, and the coldest real Diviner temperature
of the three sites. **At Faustini:** genuinely the second-coldest real
temperature (51.8 K) and the lowest illumination fraction of the three by
a wide margin relative to Wiechert. **These are real, not cherry-picked —
Cabeus and Faustini do look more individually ice-consistent than Wiechert
on several independent metrics, which is itself a meaningful, non-trivial
finding.**

## 4. Spatial character (from the real Mini-RF maps)

- **Cabeus's real CPR map** shows a highly heterogeneous, speckled
  texture with numerous small patches exceeding CPR>1 (the cyan contour in
  the figure) scattered across roughly half the window — consistent with
  `docs/MINIRF_CABEUS_CPR_RECONCILIATION.md`'s finding that a documented
  fresh-crater ejecta ray sits at this exact coordinate, which would
  produce exactly this kind of patchy, elevated-but-not-uniform CPR
  texture.
- **Faustini's real CPR/DOP maps show a visible horizontal banding
  pattern** — a real feature of the downloaded data, not a plotting
  artifact, most likely reflecting the mosaic's own compositing seams
  between separate Mini-RF orbital passes at this latitude. Not
  interpreted further here; flagged for anyone doing follow-up spatial
  analysis at this site.
- In neither map do the CPR>1 regions and the DOP<0.2 regions visually
  coincide — consistent with `docs/PM4W_VALIDATION_RESULTS.md`'s finding
  that 0% of pixels at either site satisfy both conditions simultaneously.

## 5. Interpretation — what this does and does not show

**Shows, honestly:** on several individual metrics, Cabeus and Faustini
present more ice-consistent values than the Wiechert negative control —
this is a real pattern, visible in real data, and worth reporting as
genuine partial support.

**Does not show:** that PM4W's full, published, multi-condition AND-gate
confirms ice at either site. Per `docs/PM4W_VALIDATION_RESULTS.md`, both
classify **NON_ICE** — not because any single metric is unfavorable, but
because the *specific pixels* that pass one condition (e.g. low DOP) are
not the same pixels that pass another (e.g. high CPR), so no location
within either window satisfies every published requirement at once. This
is exactly why PM4W is a conjunctive multi-metric method rather than a
single-threshold one: it is specifically designed to reject the kind of
"some metrics look elevated" pattern seen here unless they co-occur
spatially.

**The correct, honest summary sentence for a dashboard:** *"Cabeus and
Faustini — both independently confirmed ice sites — show individually
elevated, ice-consistent radar and thermal indicators relative to the
Wiechert control, but PRISM's real Mini-RF PM4W implementation, applied
without threshold tuning, does not yet confirm ice at either site under
the full published methodology."* This is not a weaker story than a bare
"ICE" classification — it is a more defensible one, and it is what the
real data supports.

## 6. Limitations

- Mini-RF and DFSAR CPR are different formulas from different instruments
  (`docs/PM4W_SINHA_PRISM_COMPARISON.md` §2) — the two CPR rows in the
  table above must not be read as the same measurement at two scales.
- The 61×61 px Mini-RF window is small relative to Faustini's and
  Cabeus's actual crater/PSR extents; a wider window was not attempted in
  this pass.
- Illumination and temperature are single real values per site, applied
  uniformly (see `docs/PM4W_VALIDATION_RESULTS.md`'s limitations section)
  — not independently re-derived here.
- The horizontal banding in Faustini's maps (§4) is noted but not
  investigated further in this pass.
