# DOP Hypothesis 9: Topographic Orientation Angle Correction

**Date:** 2026-08-27.  
**Status:** IN PROGRESS — see results below.  
**Script:** `src/dop_slope_correction.py`  
**Outputs:** `outputs/objective1/dop_v2/slope_corrected_dop_results.json`, `slope_corrected_dop_comparison.csv`

**Read this alongside:** `docs/DOP_GROUND_TRUTH_INVESTIGATION.md` (Hypotheses 1–8).

---

## What the Other AI Described

A previous AI session suggested a "parallax correction" that would:

> *"rotate S2 and S3 in the polarimetric plane by the local slope angle before computing DOP. Steep Faustini crater walls were artificially inflating DOP (making ice look less likely than it is)."*

This is a real, established correction in SAR polarimetry — the **orientation angle removal** (also called "Faraday rotation analogue for terrain"). Its physical basis:

- When a SAR illuminates a sloped surface, the received polarimetric response is rotated by an orientation angle ψ relative to a flat surface
- For range-direction slope angle θ, the polarimetric orientation angle ψ ≈ θ
- The correction rotates (S2, S3) in the Stokes plane:
  ```
  S2' = S2·cos(2ψ) + S3·sin(2ψ)
  S3' = -S2·sin(2ψ) + S3·cos(2ψ)
  S4' = S4            (unchanged)
  DOP' = sqrt(S2'² + S3'² + S4²) / S1
  ```
- Reference: Lee & Pottier "Polarimetric Radar Imaging" §6.3; Cloude & Pottier 1997

## Sites Evaluated

| Site | Lat | Lon | Known ice |
|---|---:|---:|---|
| Faustini | −87.3° | 77.0° | Yes (M3, Li et al. 2018) |
| SP_840980_0797630 | −84.098° | 79.764° | Candidate |
| Shackleton | −89.54° | 129.20° | Partial (LRO-NIR) |

## Results — Analytic Proxy Mode (NOT data-derived) ✅ COMPLETE

The analytic proxy uses a symmetric bowl-shaped slope model (25° rim, ~0° floor). Results:

| Site | DOP uncorr. | DOP corr. | Pass% uncorr. | Pass% corr. | Δ |
|---|---:|---:|---:|---:|---|
| Faustini | 0.4567 | 0.4567 | 6.32% | 6.32% | **0.0%** |
| SP_840980_0797630 | 0.4220 | 0.4220 | 7.93% | 7.93% | **0.0%** |
| Shackleton | 0.4457 | 0.4457 | 4.51% | 4.51% | **0.0%** |

**Why zero change with analytic proxy:** The symmetric bowl proxy produces a radially-symmetric slope field. The orientation angle rotation is applied **per-pixel** with a unique ψᵢ for each pixel — but since the proxy is radially symmetric, the (cos 2ψ, sin 2ψ) values across the grid sum to zero, leaving `sqrt(S2'² + S3'²)` invariant in aggregate. This is expected and mathematically correct — it does NOT mean the correction itself is wrong, it means the proxy is too smooth to demonstrate it.

## Results — Real LOLA DEM Mode (data-derived slopes) ✅ COMPLETE

Real LOLA DEM slopes were fetched from NASA GSFC PGDA (`LDEM_80S_20MPP_ADJ.TIF`, 20m/px).
Slope statistics confirm these are genuinely steep crater walls:

| Site | LOLA slope mean | LOLA slope max | DOP uncorr. pass% | DOP corr. pass% | Δ |
|---|---:|---:|---:|---:|---|
| Faustini | 23.5° | 31.8° | 6.32% | 6.32% | **0.0%** |
| SP_840980_0797630 | 14.9° | 26.2° | 7.93% | 7.93% | **0.0%** |
| Shackleton | 17.0° | 31.5° | 4.51% | 4.51% | **0.0%** |

**Result: H9b = FAIL. Zero change even with real asymmetric LOLA slopes.**

## Why the Correction Is Mathematically Invariant (the Fundamental Proof)

This is not a numerical quirk — it is a **mathematical identity**:

```
DOP = sqrt(S2² + S3² + S4²) / S1

After rotation by ψ per pixel:
  S2' = S2·cos(2ψ) + S3·sin(2ψ)
  S3' = -S2·sin(2ψ) + S3·cos(2ψ)

Then: S2'² + S3'² = S2²(cos²+sin²) + S3²(sin²+cos²) + cross-terms
                  = S2² + S3²   ← cross-terms cancel exactly

Therefore: DOP' = sqrt(S2'² + S3'² + S4²) / S1
                = sqrt(S2² + S3² + S4²) / S1
                = DOP   ← IDENTICAL, for any ψ, any pixel
```

**The orientation angle correction is rotation in the (S2, S3) plane — and DOP is the
Euclidean norm of the Stokes vector, which is rotation-invariant by definition.** No
matter what slope angle you feed it, DOP cannot change. This is basic vector geometry.

**Conclusion:** The other AI's suggested fix ("rotate S2 and S3 by the local slope angle
before computing DOP") is **mathematically impossible to work** — it is equivalent to
claiming you can change the length of a vector by rotating it. The suggestion was
physically intuitive but algebraically wrong at the most fundamental level.

## Diagnosis: Why the correction is unlikely to be decisive

The deeper reason DOP can't match Sinha et al. 0.10–0.13 was established in Hypotheses 1–8:

> *"Full coherent DOP (as computed): 0.63–0.85. Power-only DOP (|S2|/S1): 0.003–0.063. The paper's 0.10–0.13 sits between these two extremes — suggesting a systematic effect (e.g. a residual geometric/topographic phase trend)."*

The slope correction operates **within** the coherent DOP computation — it rotates the (S2, S3) plane but does NOT collapse the coherent terms to power-only. To actually reach 0.10–0.13 would require the correction to reduce DOP by **>0.35** — much larger than any physically-reasonable orientation angle effect (max ~0.1 reduction for 35° slopes).

## Conclusion (preliminary)

| Hypothesis | Result |
|---|---|
| H9a: Analytic slope proxy | FAIL — zero change (expected, symmetric cancellation) |
| H9b: Real LOLA DEM slopes | Pending |

**Most likely H9b result:** Small reduction (~0.01–0.05), not reaching the 0.10–0.13 target. This would be consistent with the DOP investigation's finding that the mismatch is a processing-level difference (coherent vs. power-only pipeline) rather than a correctable single-factor error.

## What Comes Next

If H9b LOLA result confirms small improvement only:
1. **Accept Hypothesis 9 = FAIL** — honestly documented
2. **Maintain Recommendation from DOP_GROUND_TRUTH_INVESTIGATION.md:** Use CPR as the primary validated metric
3. **Optional:** Contact Sinha et al. authors for Supplementary Table 1

## Shackleton & de Gerlache Results (Completed 2026-08-27)

From `pm4w_shackleton_degerlache.py` (Sohan's extension pattern, same unmodified pm4w_detector_v2.py):

| Site | DOP mean | DOP<0.2 px | CPR>1 px | Final |
|---|---:|---:|---:|---|
| Shackleton | 0.4457 | 168/3721 (4.5%) | 1114/3721 (29.9%) | NON_ICE |
| de Gerlache | 0.5501 | 155/3721 (4.2%) | 270/3721 (7.3%) | NON_ICE |

Both follow the same pattern as all previous sites: high DOP, low CPR overlap. The AND-gate fails on DOP for all pixels simultaneously passing CPR. This is consistent with the full 12-site investigation (all 12 → NON_ICE via PM4W AND-gate).
