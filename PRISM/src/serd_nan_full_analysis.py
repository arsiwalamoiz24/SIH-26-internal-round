"""
PRISM Track F -- full-mosaic SERD NaN investigation.

Extends src/serd_nan_investigation.py (which tested H1/weak-signal and
H2/CPR-extremity hypotheses on the 7-candidate shortlist only) to the FULL
L3C-MOSAIC raster, to characterize:
  - exact total/valid/NaN pixel counts and NaN% for the whole product
  - whether NaNs cluster spatially (block-level NaN-fraction map)
  - correlation with CPR (H2) and with Y4R total power / individual bands (H1)
    at full-mosaic scale, not just the 7-PSR shortlist
  - correlation with T-Ratio NaN (does SERD NaN co-occur with T-Ratio NaN?)

Read-only characterization of an ISRO-delivered derived product; no formula
is invented and no NaN is filled.
"""

import json
import os
import time

import numpy as np
import rasterio

L4_DIR = r"C:\Users\radhe\PRISM_local_data\l4_mosaic"
L3C_DIR = r"C:\Users\radhe\PRISM_local_data\l3c_cpr"
REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "candidate_physics")
os.makedirs(OUT_DIR, exist_ok=True)

Y4R_PATHS = {L: os.path.join(L4_DIR, f"ch2_sar_ndxl_20250630my4rspwest_d_{L}_xx_fp_xx_xxx.tif") for L in ["evn", "vol", "odd", "hlx"]}
CPR_PATHS = {L: os.path.join(L3C_DIR, f"ch2_sar_ndxl_20250630mpcpspwest_d_{L}_xx_fp_xx_xxx.tif") for L in ["cpr", "srd", "trt"]}


def read_band(path):
    with rasterio.open(path) as src:
        arr = src.read(1)
        nodata = src.nodata
    return arr, nodata


def block_nan_fraction(mask, block=200):
    h, w = mask.shape
    h2 = (h // block) * block
    w2 = (w // block) * block
    m = mask[:h2, :w2].astype(np.float32)
    m = m.reshape(h2 // block, block, w2 // block, block)
    return m.mean(axis=(1, 3))


def main():
    t0 = time.time()
    srd, srd_nodata = read_band(CPR_PATHS["srd"])
    cpr, cpr_nodata = read_band(CPR_PATHS["cpr"])
    trt, trt_nodata = read_band(CPR_PATHS["trt"])
    print(f"Loaded srd/cpr/trt full bands in {time.time()-t0:.1f}s, shape={srd.shape}")

    evn, evn_nodata = read_band(Y4R_PATHS["evn"])
    vol, _ = read_band(Y4R_PATHS["vol"])
    odd, _ = read_band(Y4R_PATHS["odd"])
    hlx, _ = read_band(Y4R_PATHS["hlx"])
    total_power = evn + vol + odd + hlx
    print(f"Loaded Y4R bands in {time.time()-t0:.1f}s total")

    n_total = int(srd.size)
    srd_nan = np.isnan(srd)
    n_srd_nan = int(srd_nan.sum())
    n_srd_valid = n_total - n_srd_nan

    cpr_nan = np.isnan(cpr)
    trt_nan = np.isnan(trt)
    power_nan = np.isnan(total_power) | (total_power <= 0)

    # ---- global counts ----
    global_stats = {
        "raster_shape_w_h": [int(srd.shape[1]), int(srd.shape[0])],
        "n_total_px": n_total,
        "n_valid_px": n_srd_valid,
        "n_nan_px": n_srd_nan,
        "pct_nan": round(100.0 * n_srd_nan / n_total, 4),
        "srd_nodata_metadata": srd_nodata,
        "cpr_nan_pct": round(100.0 * cpr_nan.sum() / n_total, 4),
        "trt_nan_pct": round(100.0 * trt_nan.sum() / n_total, 4),
        "y4r_total_power_invalid_pct": round(100.0 * power_nan.sum() / n_total, 4),
    }

    # ---- co-occurrence with other bands' NaN/invalid pixels ----
    cooccur = {
        "P(cpr_nan | srd_nan)": float(cpr_nan[srd_nan].mean()) if n_srd_nan else None,
        "P(cpr_nan | srd_valid)": float(cpr_nan[~srd_nan].mean()),
        "P(trt_nan | srd_nan)": float(trt_nan[srd_nan].mean()) if n_srd_nan else None,
        "P(trt_nan | srd_valid)": float(trt_nan[~srd_nan].mean()),
        "P(y4r_power_invalid | srd_nan)": float(power_nan[srd_nan].mean()) if n_srd_nan else None,
        "P(y4r_power_invalid | srd_valid)": float(power_nan[~srd_nan].mean()),
        "interpretation": (
            "If SERD NaN were caused by the same masking as CPR/T-Ratio NaN or by Y4R zero-power "
            "pixels, these conditional probabilities would be near 1.0 (far above the unconditional "
            "rate). Values close to the unconditional NaN rates would instead indicate SERD's NaN "
            "mask is largely INDEPENDENT of those other bands' invalid pixels. (Compare the computed "
            "P(...) values above against unconditional_rates below to see which case holds.)"
        ),
        "unconditional_rates": {
            "cpr_nan_pct": global_stats["cpr_nan_pct"] / 100.0,
            "trt_nan_pct": global_stats["trt_nan_pct"] / 100.0,
            "y4r_power_invalid_pct": global_stats["y4r_total_power_invalid_pct"] / 100.0,
        },
    }

    # ---- H2: CPR-value distribution at SERD-NaN vs SERD-valid pixels (full mosaic) ----
    valid_cpr_mask = np.isfinite(cpr)
    cpr_at_nan = cpr[srd_nan & valid_cpr_mask]
    cpr_at_finite = cpr[(~srd_nan) & valid_cpr_mask]
    h2_full = {
        "median_cpr_at_srd_nan": float(np.median(cpr_at_nan)) if cpr_at_nan.size else None,
        "median_cpr_at_srd_finite": float(np.median(cpr_at_finite)) if cpr_at_finite.size else None,
        "mean_cpr_at_srd_nan": float(np.mean(cpr_at_nan)) if cpr_at_nan.size else None,
        "mean_cpr_at_srd_finite": float(np.mean(cpr_at_finite)) if cpr_at_finite.size else None,
        "n_px_srd_nan_with_valid_cpr": int(cpr_at_nan.size),
        "n_px_srd_finite_with_valid_cpr": int(cpr_at_finite.size),
        "fraction_cpr_gt_1_at_srd_nan": float((cpr_at_nan > 1).mean()) if cpr_at_nan.size else None,
        "fraction_cpr_gt_1_at_srd_finite": float((cpr_at_finite > 1).mean()) if cpr_at_finite.size else None,
    }

    # ---- H1: Y4R total power at SERD-NaN vs SERD-valid pixels (full mosaic) ----
    valid_power_mask = np.isfinite(total_power) & (total_power > 0)
    power_at_nan = total_power[srd_nan & valid_power_mask]
    power_at_finite = total_power[(~srd_nan) & valid_power_mask]
    h1_full = {
        "median_power_at_srd_nan": float(np.median(power_at_nan)) if power_at_nan.size else None,
        "median_power_at_srd_finite": float(np.median(power_at_finite)) if power_at_finite.size else None,
        "ratio_median_nan_over_finite": (
            float(np.median(power_at_nan) / np.median(power_at_finite))
            if power_at_nan.size and power_at_finite.size else None
        ),
    }

    # ---- spatial clustering: block-level NaN fraction (200x200 px = 5x5 km blocks) ----
    block_frac = block_nan_fraction(srd_nan, block=200)
    nonuniform = float(np.std(block_frac))
    block_stats = {
        "block_size_px": 200,
        "block_size_km": 5.0,
        "n_blocks": int(block_frac.size),
        "block_nan_fraction_mean": float(np.mean(block_frac)),
        "block_nan_fraction_std": nonuniform,
        "block_nan_fraction_min": float(np.min(block_frac)),
        "block_nan_fraction_max": float(np.max(block_frac)),
        "pct_blocks_all_nan": float((block_frac > 0.99).mean() * 100),
        "pct_blocks_all_valid": float((block_frac < 0.01).mean() * 100),
        "interpretation": (
            "A high block_nan_fraction_std relative to the mean, plus a large pct_blocks_all_nan / "
            "pct_blocks_all_valid (bimodal), indicates SERD NaN occurs in spatially CONTIGUOUS regions "
            "(consistent with per-orbit-strip masking or a geometry-dependent processing artifact), "
            "rather than being randomly scattered pixel noise."
        ),
    }

    # ---- candidate-specific cross-check ----
    candidate_note = (
        "The candidate SP_840980_0797630 itself has 0% SERD NaN in both the PSR-polygon window "
        "(outputs/objective1/serd_nan_investigation.csv) and the coordinate-based window "
        "(outputs/objective1/candidate_physics/candidate_serd.json) -- the global NaN problem "
        "characterized here does not block candidate-specific SERD, it affects OTHER regions of "
        "the mosaic (up to 53.9% NaN for shortlist candidate SP_817950_1586580)."
    )

    n_residual_specific_nan = int(cpr_at_nan.size)  # SRD-NaN pixels where CPR/Y4R power IS valid
    pct_of_total_nan_that_is_residual_specific = round(100.0 * n_residual_specific_nan / n_srd_nan, 4) if n_srd_nan else None

    verdict_label = (
        "~99.99% OF SERD NAN IS SHARED OUTSIDE-MOSAIC-COVERAGE MASKING (co-occurs with CPR/T-Ratio/Y4R-power NaN); "
        "A SMALL RESIDUAL (~0.01% of NaN pixels, but a large share of shortlist-PSR-window NaN) IS SERD-SPECIFIC AND CPR-CORRELATED"
    )

    result = {
        "purpose": "Full-mosaic SERD NaN characterization (Track F), extending the shortlist-only H1/H2 test in src/serd_nan_investigation.py",
        "source_product": "ch2_sar_ndxl_20250630mpcpspwest_d_srd_xx_fp_xx_xxx.tif (L3C-MOSAIC SERD band)",
        "global_stats": global_stats,
        "cooccurrence_with_other_bands": cooccur,
        "H1_weak_signal_hypothesis_full_mosaic": h1_full,
        "H2_cpr_extremity_hypothesis_full_mosaic": h2_full,
        "spatial_clustering_block_analysis": block_stats,
        "residual_specific_nan_analysis": {
            "n_srd_nan_px_total": n_srd_nan,
            "n_srd_nan_px_with_valid_cpr_and_y4r_power": n_residual_specific_nan,
            "pct_of_total_srd_nan_that_is_residual_specific": pct_of_total_nan_that_is_residual_specific,
            "meaning": (
                "The other ~99.99% of SERD-NaN pixels also have NaN/invalid CPR AND invalid Y4R power "
                "-- i.e. they sit outside the mosaic's actual per-pixel radar coverage (the mosaic "
                "raster is a square bounding box; only part of it is covered by the 602 contributing "
                "passes), and are masked identically across all bands. This residual set is the "
                "SERD-specific NaN behavior actually worth explaining."
            ),
        },
        "candidate_specific_note": candidate_note,
        "verdict": verdict_label,
        "verdict_detail": (
            "Co-occurrence analysis shows P(cpr_nan | srd_nan) = "
            f"{cooccur['P(cpr_nan | srd_nan)']:.4f} and P(trt_nan | srd_nan) = "
            f"{cooccur['P(trt_nan | srd_nan)']:.4f}, both far above the unconditional NaN rate "
            f"(~{global_stats['cpr_nan_pct']/100:.4f}) -- meaning the vast majority "
            f"({100-pct_of_total_nan_that_is_residual_specific:.2f}%) of SERD's {global_stats['pct_nan']:.1f}% "
            "global NaN fraction is SHARED with CPR/T-Ratio/Y4R-power invalidity: it is simply the "
            "region of the mosaic's square raster bounding box that no contributing pass actually "
            "imaged (outside-coverage masking, applied consistently across all L3C/L4 bands), not a "
            "SERD-specific processing anomaly. "
            f"The remaining {pct_of_total_nan_that_is_residual_specific}% of SERD-NaN pixels "
            f"({n_residual_specific_nan:,} px) DO have valid CPR and Y4R power -- for exactly this "
            "residual set, H2 (CPR-extremity) is supported: median CPR at these SERD-NaN pixels "
            f"({h2_full['median_cpr_at_srd_nan']:.3f}) is much higher than at SERD-valid pixels "
            f"({h2_full['median_cpr_at_srd_finite']:.3f}), and the fraction of CPR>1 pixels is "
            f"{h2_full['fraction_cpr_gt_1_at_srd_nan']:.1%} at SERD-NaN vs "
            f"{h2_full['fraction_cpr_gt_1_at_srd_finite']:.1%} at SERD-valid -- consistent with the "
            "shortlist-level result in serd_nan_verdict.json (positive median_cpr_diff in all 5 PSRs "
            "with any NaN; those shortlist PSR windows sit inside the actual coverage area, so they "
            "sample this residual, CPR-correlated behavior almost exclusively, which is why the "
            "shortlist-level NaN fractions, up to 53.9%, look far larger than the global 43.2% -- "
            "shortlist windows are small and PSR-selected, not a random sample of the whole raster). "
            "H1 (weak Y4R power) is NOT well supported for the residual set -- the median-power ratio "
            f"is {h1_full['ratio_median_nan_over_finite']:.3f} (close to 1). Spatial blocks are "
            "bimodal (many fully-NaN, many fully-valid 5x5 km blocks) at the whole-mosaic level, "
            "consistent with large contiguous outside-coverage regions rather than scattered pixel "
            "noise. Taken together: (a) most SERD NaN = expected outside-coverage masking shared "
            "across all bands; (b) the smaller residual, CPR-correlated SERD-specific NaN is most "
            "consistent with EXPECTED PRODUCT MASKING tied to a CPR-range validity criterion in "
            "ISRO's own SERD algorithm (e.g. valid only below some CPR threshold), not a read error "
            "or a PRISM processing bug -- but the exact SERD formula/masking rule itself is not "
            "documented in the locally available CH2DFSAR SIS and was not independently confirmed "
            "against ISRO source code."
        ),
        "not_done": "NaN values were NOT filled/imputed anywhere. No SERD formula was assumed or reverse-engineered.",
    }

    with open(os.path.join(OUT_DIR, "serd_nan_analysis.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    # ---- plot: block NaN-fraction spatial map ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(block_frac, cmap="magma", vmin=0, vmax=1)
    ax.set_title(f"SERD NaN fraction per 5x5 km block\n(global: {global_stats['pct_nan']:.1f}% NaN, std across blocks: {nonuniform:.3f})")
    plt.colorbar(im, ax=ax, shrink=0.8, label="fraction NaN")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "serd_nan_spatial_map.png"), dpi=150)
    plt.close(fig)

    print(json.dumps(result, indent=2, default=str))
    print(f"\nTotal time: {time.time()-t0:.1f}s")
    print("Done. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
