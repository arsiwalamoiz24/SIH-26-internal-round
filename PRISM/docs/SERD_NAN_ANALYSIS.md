# SERD_NAN_ANALYSIS — full-mosaic and shortlist-level investigation

**Date:** 2026-08-22
**Scope:** Track F. Extends the earlier shortlist-only H1/H2 hypothesis test (`src/serd_nan_investigation.py`, `outputs/objective1/serd_nan_hypothesis_test.csv`, `serd_nan_verdict.json`) to the **full L3C-MOSAIC raster** (`src/serd_nan_full_analysis.py`, `outputs/objective1/candidate_physics/serd_nan_analysis.json`, `serd_nan_spatial_map.png`). Read-only characterization of an ISRO-delivered derived product — **no NaN was filled, no SERD formula was assumed or reverse-engineered.**

## 1. Headline numbers (full mosaic, 24,181 × 24,794 px = 599,543,714 px)

| | value |
|---|---:|
| Total pixels | 599,543,714 |
| SERD valid pixels | 340,317,714 |
| SERD NaN pixels | 259,226,000 |
| **SERD NaN %** | **43.24%** |
| CPR NaN % (same raster) | 43.23% |
| T-Ratio NaN % | 43.23% |
| Y4R total-power invalid % | 43.30% |

## 2. The key finding: two very different populations inside that 43.24%

Naively, "43% NaN" sounds alarming. Decomposing it changes the picture entirely:

- **P(CPR also NaN | SERD NaN) = 99.99%**, and likewise for T-Ratio (99.99%) and Y4R total power (99.99%) — all far above the ~0.43% *unconditional* NaN rate of those bands.
- This means **~99.99% of SERD's NaN pixels are NaN in every band simultaneously** — i.e. they lie **outside the actual per-pixel radar coverage** of the 602 contributing acquisitions (the mosaic's delivered raster is a square bounding box; the true multi-pass coverage footprint inside it is not a full square, so all bands are masked identically in the uncovered corners/gaps). This is **expected, shared, outside-coverage masking**, not a SERD-specific defect.
- The remaining **0.011% of SERD-NaN pixels (28,598 of 259,226,000)** have valid CPR *and* valid Y4R power — this is the actual **SERD-specific** NaN behavior worth explaining.

## 3. What explains the SERD-specific residual (the 28,598 px)

For exactly this residual set:

| | at SERD-NaN (residual) | at SERD-valid |
|---|---:|---:|
| Median CPR | 0.971 | 0.222 |
| Mean CPR | 0.981 | 0.253 |
| Fraction with CPR > 1 | 46.9% | 0.2% |

**H2 (CPR-extremity) is well supported for this residual:** SERD tends to be NaN specifically where CPR is high (near or above 1, i.e. strong/anomalous volume-scattering-like returns), consistent with SERD's algorithm having a validity range or singularity tied to CPR.

**H1 (weak Y4R signal) is not well supported:** median Y4R total power at SERD-NaN residual pixels is only ~1.24× the power at SERD-valid pixels (close to 1 — no strong shadow/low-SNR signature).

This full-mosaic result is **consistent with, and explains, the earlier shortlist-level finding**: the 7-candidate shortlist PSR windows (`outputs/objective1/serd_nan_hypothesis_test.csv`) sit *inside* the actual coverage area, so a small window sampled there hits almost exclusively the CPR-correlated residual behavior — which is why those windows show NaN fractions from 0% up to 53.9% (`SP_817950_1586580`), all with a consistent *positive* CPR offset at NaN pixels (mean +0.52 across the 5 PSRs with any NaN) — the same sign and mechanism as the full-mosaic residual, just sampled at PSR scale rather than full-mosaic scale.

## 4. Spatial clustering

Block analysis (200×200 px = 5×5 km blocks, 14,760 blocks, whole mosaic):

- Mean block NaN fraction: 42.4%, std: 44.3% (very high relative to the mean).
- 29.6% of blocks are **entirely NaN**; 37.5% are **entirely valid** — strongly **bimodal**, not scattered.
- **Conclusion:** SERD NaN occurs in large, spatially contiguous regions (consistent with the outside-coverage explanation in §2 — coverage gaps are inherently regional, not per-pixel noise).

See `outputs/objective1/candidate_physics/serd_nan_spatial_map.png` for the block-level NaN-fraction map.

## 5. Is this expected masking, a numerical issue, a processing issue, or a read issue?

**Most consistent with EXPECTED PRODUCT MASKING**, at two levels:

1. The dominant (~99.99% of NaN pixels) outside-coverage masking is expected behavior for any mosaic assembled from irregular-footprint passes into a square raster — every band shows it identically.
2. The much smaller CPR-correlated residual is most consistent with a **CPR-range validity criterion in ISRO's own SERD algorithm** (e.g. an algorithm/ratio undefined or excluded above some CPR threshold) — not a PRISM read/decode error (PRISM never touches SERD's internal computation; it only reads the delivered GeoTIFF pixel values) and not random numerical noise (it is CPR-correlated and spatially non-random within the covered area, though less block-contiguous than the outside-coverage population).

**What was NOT confirmed:** the exact SERD formula/masking rule itself is not documented in the locally available CH2DFSAR SIS (`sarlta/document/ch2_sar_pds_dp_archive_sis.pdf`) and was not independently confirmed against ISRO source code — the CPR-correlation finding is a strong statistical signature, not a verified causal mechanism from ISRO documentation.

## 6. Candidate-specific relevance

**The candidate `SP_840980_0797630` itself has 0% SERD NaN**, both in the earlier PSR-polygon window (`outputs/objective1/serd_nan_investigation.csv`) and in this session's coordinate-based window (`outputs/objective1/candidate_physics/candidate_serd.json`). The NaN behavior characterized here affects *other* regions of the mosaic (up to 53.9% for shortlist candidate `SP_817950_1586580`) — **it does not block or affect the candidate's own SERD value.**

## 7. Explicitly not done

- No NaN values were filled or imputed anywhere.
- No SERD formula was invented, assumed, or reverse-engineered — this is purely a statistical characterization of an ISRO-delivered product's existing NaN pattern.
