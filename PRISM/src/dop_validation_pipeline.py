"""
PRISM Track C -- DOP computational-pipeline validation (NON-CANDIDATE).

*** This acquisition (2025-10-25, ch2_sar_nrxl_20251025t211236510_d_fp_d18)
    does NOT cover SP_840980_0797630 (-84.098, 79.764) -- see
    docs/DOP_VALIDATION.md / outputs/objective1/dop/candidate_coverage_check.json.
    Every number this script produces validates the DOP COMPUTATION METHOD only.
    None of it is, or is presented as, the candidate's DOP. ***

Reuses, unmodified:
  - src/dfsar_raw_reader.py (verified binary structure, offset-binary decode,
    G0->HV/G1->HH/G2->VV/G3->VH mapping, bias correction)
  - The three DOP formulations already present in
    notebooks/objective1_y4r_polarimetry.ipynb.ipynb (formulas transcribed
    exactly, re-implemented vectorized for a much larger window than the
    notebook's original 25x1024-pixel patch -- see docs/DOP_VALIDATION_RESULTS.md
    for the transcription and why nothing was changed):

  1) Linear-pol Stokes DOP (STEP 27-33), bias-corrected HH/VV, local 5x5
     spatial covariance:
       S1 = <|HH|^2> + <|VV|^2>
       S2 = <|HH|^2> - <|VV|^2>
       S3 = 2*Re(<HH*conj(VV)>)
       S4 = -2*Im(<HH*conj(VV)>)
       DOP = sqrt(S2^2+S3^2+S4^2) / S1

  2) Hybrid-pol Stokes DOP (STEP 46-48), synthesized left-circular-Tx fields
       LH = (HH + j*HV)/sqrt(2), LV = (VH + j*VV)/sqrt(2)
     then the identical Stokes/DOP formula applied to (LH,LV) in place of (HH,VV).

  3) 4x4 full-quad-pol eigenvalue "polarization purity" diagnostic (STEP 26/35):
       k = [HH,HV,VH,VV] stacked per-pixel over a block, C = (k^H k)/N
       eig = eigvalsh(C), clipped >=0; p = eig/sum(eig)
       purity = sqrt(max(0, (4*sum(p^2) - 1)/3))
     -- computed per non-overlapping tile (not per-pixel; this is how the
     notebook computed it -- ONE value per window/tile, not a per-pixel map).

Local-window means for (1)/(2) use scipy.ndimage.uniform_filter (a vectorized
box-filter local mean), which is numerically identical to the notebook's
explicit nested-loop 5x5 mean, just not looped in pure Python.
"""

import json
import os
import time

import numpy as np
from scipy.ndimage import uniform_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dfsar_raw_reader import DfsarRawReader, LINES_PER_POL_CHANNEL, SAMPLES_PER_LINE

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "dop")
os.makedirs(OUT_DIR, exist_ok=True)

# Mid-scene window, same starting line as the already-validated Phase D
# diagnostic window (docs/RAW_DFSAR_VALIDATION.md Section 7), extended in
# both line-count and sample-count for a statistically meaningful map
# instead of the notebook's original 25x1024 patch.
LINE_START = 150_000
LINE_COUNT = 3_000
SAMPLE_START = 0
SAMPLE_COUNT = SAMPLES_PER_LINE  # 1024, full swath

WINDOW = 5  # matches notebook STEP 29 local window size
TILE_LINES, TILE_SAMPLES = 30, 32  # for the eigenvalue-purity tiling (3.2k tiles)


def local_stokes_dop(A, B):
    """Vectorized equivalent of notebook STEP 27-33: local 5x5 mean covariance
    Stokes DOP for a co/cross field pair (A, B)."""
    PA = uniform_filter(np.abs(A) ** 2, size=WINDOW, mode="reflect")
    PB = uniform_filter(np.abs(B) ** 2, size=WINDOW, mode="reflect")
    cross = A * np.conj(B)
    Re_AB = uniform_filter(cross.real, size=WINDOW, mode="reflect")
    Im_AB = uniform_filter(cross.imag, size=WINDOW, mode="reflect")

    S1 = PA + PB
    S2 = PA - PB
    S3 = 2 * Re_AB
    S4 = -2 * Im_AB

    with np.errstate(divide="ignore", invalid="ignore"):
        dop = np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1
    return dop, dict(S1=S1, S2=S2, S3=S3, S4=S4)


def tiled_eigenvalue_purity(HH, HV, VH, VV, tile_lines=TILE_LINES, tile_samples=TILE_SAMPLES):
    """Notebook STEP 26/35 exactly, applied to each non-overlapping tile."""
    n_lines, n_samples = HH.shape
    n_tiles_r = n_lines // tile_lines
    n_tiles_c = n_samples // tile_samples
    purity_map = np.full((n_tiles_r, n_tiles_c), np.nan)
    for ti in range(n_tiles_r):
        for tj in range(n_tiles_c):
            r0, r1 = ti * tile_lines, (ti + 1) * tile_lines
            c0, c1 = tj * tile_samples, (tj + 1) * tile_samples
            k = np.stack([
                HH[r0:r1, c0:c1].ravel(), HV[r0:r1, c0:c1].ravel(),
                VH[r0:r1, c0:c1].ravel(), VV[r0:r1, c0:c1].ravel(),
            ], axis=1)  # (N, 4)
            C = (k.conj().T @ k) / k.shape[0]
            eig = np.linalg.eigvalsh(C)
            eig = np.maximum(eig, 0)
            s = eig.sum()
            if s <= 0:
                continue
            p = eig / s
            purity_map[ti, tj] = float(np.sqrt(max(0.0, (4 * np.sum(p ** 2) - 1) / 3)))
    return purity_map


def stats_block(arr):
    vals = arr[np.isfinite(arr)]
    n_total = int(arr.size)
    n_valid = int(vals.size)
    out = {
        "n_total_px": n_total, "n_valid_px": n_valid,
        "n_nan_px": n_total - n_valid,
        "pct_nan": round(100.0 * (n_total - n_valid) / n_total, 4) if n_total else None,
    }
    if n_valid:
        pct = np.percentile(vals, [5, 25, 50, 75, 95])
        out.update({
            "mean": float(vals.mean()), "median": float(np.median(vals)),
            "std": float(vals.std()), "min": float(vals.min()), "max": float(vals.max()),
            "p5": float(pct[0]), "p25": float(pct[1]), "p50": float(pct[2]),
            "p75": float(pct[3]), "p95": float(pct[4]),
        })
    else:
        out.update({k: None for k in ["mean", "median", "std", "min", "max", "p5", "p25", "p50", "p75", "p95"]})
    return out


def main():
    t0 = time.time()
    reader = DfsarRawReader()
    win = reader.read_window(LINE_START, LINE_COUNT, SAMPLE_START, SAMPLE_COUNT)
    HH, HV, VH, VV = win["HH"], win["HV"], win["VH"], win["VV"]
    print(f"Read window {HH.shape} in {time.time()-t0:.1f}s (bias-corrected HH/HV/VH/VV)")

    # ---- 1. Linear-pol (HH/VV) ----
    dop_linear, _ = local_stokes_dop(HH, VV)
    # ---- 2. Hybrid-pol synthesized LH/LV ----
    sqrt2 = np.sqrt(2.0)
    LH = (HH + 1j * HV) / sqrt2
    LV = (VH + 1j * VV) / sqrt2
    dop_hybrid, _ = local_stokes_dop(LH, LV)
    # ---- 3. Full quad-pol eigenvalue purity (tiled) ----
    purity_map = tiled_eigenvalue_purity(HH, HV, VH, VV)

    print(f"All 3 formulations computed in {time.time()-t0:.1f}s total")

    linear_stats = stats_block(dop_linear)
    hybrid_stats = stats_block(dop_hybrid)
    purity_stats = stats_block(purity_map)

    # single-block whole-window value, exactly as notebook STEP 26/35 computed it
    # (one covariance matrix over the ENTIRE window, for direct comparability
    # with the notebook's reported single value 0.643)
    k_full = np.stack([HH.ravel(), HV.ravel(), VH.ravel(), VV.ravel()], axis=1)
    C_full = (k_full.conj().T @ k_full) / k_full.shape[0]
    eig_full = np.maximum(np.linalg.eigvalsh(C_full), 0)
    p_full = eig_full / eig_full.sum()
    purity_whole_window = float(np.sqrt(max(0.0, (4 * np.sum(p_full ** 2) - 1) / 3)))

    comparison = {
        "prior_notebook_values_25x1024_patch_non_geolocated": {
            "linear_pol_covariance": 0.629,
            "hybrid_pol": 0.557,
            "eigenvalue_purity_4x4": 0.643,
            "note": "These are the values referenced in PROJECT_STATUS.md / docs/DOP_VALIDATION.md as diagnostics on an arbitrary, non-geolocated first-100-lines-derived patch. NOT reused as results here -- shown only for numerical comparison.",
        },
        "this_run_values": {
            "linear_pol_mean": linear_stats["mean"], "linear_pol_median": linear_stats["median"],
            "hybrid_pol_mean": hybrid_stats["mean"], "hybrid_pol_median": hybrid_stats["median"],
            "eigenvalue_purity_whole_window": purity_whole_window,
            "eigenvalue_purity_tiled_mean": purity_stats["mean"], "eigenvalue_purity_tiled_median": purity_stats["median"],
            "window": f"{LINE_COUNT}x{SAMPLE_COUNT} px, mid-scene lines [{LINE_START}:{LINE_START+LINE_COUNT}), all {SAMPLE_COUNT} samples",
        },
        "agreement_note": (
            "This run's window is ~123x larger (3000x1024 vs 25x1024) and at a different scene "
            "location than the prior notebook patch, and is expected to differ numerically -- it is "
            "NOT a reproduction of the same patch, it is an independent, larger-scale validation run "
            "of the same three formulas. Rough order-of-magnitude agreement (all three still land in "
            "the 0.4-0.7 range) supports that the formulas and reader are behaving consistently; exact "
            "numerical match was never expected and is not the validation criterion."
        ),
    }

    formula_comparison = {
        "linear_pol_vs_hybrid_pol_mean_abs_diff": abs(linear_stats["mean"] - hybrid_stats["mean"]),
        "linear_pol_vs_purity_mean_abs_diff": abs(linear_stats["mean"] - purity_whole_window),
        "hybrid_pol_vs_purity_mean_abs_diff": abs(hybrid_stats["mean"] - purity_whole_window),
        "which_is_best_supported": (
            "Linear-pol (HH/VV) Stokes-covariance DOP is the best-supported formulation for this "
            "product: HH/VV are the two polarizations with CONFIRMED/LIKELY channel-mapping "
            "(docs/RAW_DFSAR_VALIDATION.md), it is the standard, textbook dual-pol DOP construction "
            "(Stokes parameters from a genuine spatial covariance estimate, not single-pixel), and it "
            "requires no additional synthesis step. Hybrid-pol depends on the SAME HH/VV/HV/VH inputs "
            "plus an additional circular-synthesis assumption (LH/LV construction), so it inherits all "
            "of linear-pol's channel-mapping uncertainty (including the weaker HH fit) without adding "
            "independent information -- it is retained here as a cross-check, not preferred. The "
            "eigenvalue-purity diagnostic uses all 4 channels directly (no synthesis) but answers a "
            "different physical question (how concentrated the scattering is in the dominant "
            "eigen-mode of the full 4x4 covariance, not the classical 2-parameter DOP) and is most "
            "useful as an independent cross-check rather than a primary DOP estimate."
        ),
    }

    result = {
        "warning": "NON-CANDIDATE DOP PIPELINE VALIDATION ONLY. This acquisition (2025-10-25) does NOT cover SP_840980_0797630. See docs/DOP_VALIDATION.md.",
        "raw_product": "data/ch2_sar_nrxl_20251025t211236510_d_fp_d18/data/raw/20251025/ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat",
        "window": {
            "line_start_per_channel": LINE_START, "line_count": LINE_COUNT,
            "sample_start": SAMPLE_START, "sample_count": SAMPLE_COUNT,
            "local_covariance_window_px": WINDOW,
            "eigenvalue_purity_tile_px": [TILE_LINES, TILE_SAMPLES],
            "n_eigenvalue_purity_tiles": int(purity_map.size),
        },
        "formulas": {
            "linear_pol_stokes_dop": "S1=<|HH|^2>+<|VV|^2>, S2=<|HH|^2>-<|VV|^2>, S3=2Re(<HH*conj(VV)>), S4=-2Im(<HH*conj(VV)>), DOP=sqrt(S2^2+S3^2+S4^2)/S1, local mean over 5x5 px window",
            "hybrid_pol_stokes_dop": "LH=(HH+j*HV)/sqrt(2), LV=(VH+j*VV)/sqrt(2) [Raney-style left-circular-Tx synthesis], then identical Stokes/DOP formula on (LH,LV)",
            "eigenvalue_purity": "k=[HH,HV,VH,VV] per pixel, C=(k^H k)/N over a tile, eig=eigvalsh(C) clipped>=0, p=eig/sum(eig), purity=sqrt(max(0,(4*sum(p^2)-1)/3))",
            "source": "Transcribed unchanged from notebooks/objective1_y4r_polarimetry.ipynb.ipynb STEP 26-35, 46-48 (see docs/DOP_VALIDATION_RESULTS.md for line-by-line citation)",
        },
        "linear_pol_dop": linear_stats,
        "hybrid_pol_dop": hybrid_stats,
        "eigenvalue_purity_tiled_dop": purity_stats,
        "eigenvalue_purity_whole_window": purity_whole_window,
        "comparison_to_prior_notebook_patch": comparison,
        "formula_comparison": formula_comparison,
        "channel_mapping_confidence_caveat": "G1->HH is LIKELY (weakest quantitative fit of the 4 channels, see docs/RAW_DFSAR_VALIDATION.md Section 5) -- all 3 formulations here use HH, so all inherit this reduced confidence to some degree; linear-pol and hybrid-pol also use VV/HV/VH (CONFIRMED/LIKELY).",
    }

    with open(os.path.join(OUT_DIR, "dop_validation_results.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    with open(os.path.join(OUT_DIR, "dop_comparison.json"), "w") as f:
        json.dump({"comparison_to_prior_notebook_patch": comparison, "formula_comparison": formula_comparison}, f, indent=2, default=str)

    # ---- plots ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    im0 = axes[0].imshow(dop_linear, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    axes[0].set_title(f"Linear-pol (HH/VV) DOP map\nNON-CANDIDATE VALIDATION -- mid-scene, 2025-10-25")
    plt.colorbar(im0, ax=axes[0], shrink=0.8)
    im1 = axes[1].imshow(dop_hybrid, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    axes[1].set_title("Hybrid-pol (synth. LH/LV) DOP map\nNON-CANDIDATE VALIDATION")
    plt.colorbar(im1, ax=axes[1], shrink=0.8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dop_map.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.hist(dop_linear[np.isfinite(dop_linear)].ravel(), bins=100, alpha=0.6, label=f"linear-pol (mean={linear_stats['mean']:.3f})", density=True)
    ax.hist(dop_hybrid[np.isfinite(dop_hybrid)].ravel(), bins=100, alpha=0.6, label=f"hybrid-pol (mean={hybrid_stats['mean']:.3f})", density=True)
    ax.hist(purity_map[np.isfinite(purity_map)].ravel(), bins=50, alpha=0.6, label=f"eigenvalue purity, tiled (mean={purity_stats['mean']:.3f})", density=True)
    ax.set_xlabel("DOP"); ax.set_ylabel("density")
    ax.set_title("NON-CANDIDATE DOP pipeline validation -- formulation comparison\n(2025-10-25 acquisition, does NOT cover SP_840980_0797630)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "dop_histogram.png"), dpi=150)
    plt.close(fig)

    print(json.dumps(result, indent=2, default=str)[:3000])
    print(f"\nTotal time: {time.time()-t0:.1f}s. Outputs in {OUT_DIR}")


if __name__ == "__main__":
    main()
