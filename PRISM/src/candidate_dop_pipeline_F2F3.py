"""
PRISM -- CANDIDATE-SPECIFIC DOP for the paper's own confirmed-ice craters F2 and F3
(Sinha et al. 2026, Table 1/2), computed on the crater's CIRCULAR INTERIOR MASK
specifically (radius = diameter/2), not a whole-window average -- this is the
key methodological change from the 4 PSR-scale candidates computed earlier this
session, since the paper's own DOP number is an interior-region average.

Single acquisition ch2_sar_ncxl_20200321t082617351_d_fp_d18 (2020-03-21, station
d18) covers BOTH craters, confirmed by point-in-polygon test against the true
image-footprint corners (F2: 23.56 km inside nearest edge; F3: 29.17 km) --
comfortable margins, safely interior. Pixel position for each crater located via
0-residual bilinear inversion of the same 4 corners (same method as all prior
candidates this session).
"""

import json
import os
import time

import numpy as np
from scipy.ndimage import uniform_filter
import rasterio
from rasterio.windows import Window
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "paper_crater_validation")
os.makedirs(OUT_DIR, exist_ok=True)

ZIP_PATH = r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20200321t082617351_d_fp_d18.zip"
INTERNAL_DIR = "data/calibrated/20200321"
BASE = "ch2_sar_ncxl_20200321t082617351_d_sli_xx_fp"
STATION = "d18"
TOTAL_SAMPLES = 512
TOTAL_LINES = 343723
LINE_SPACING_M = 0.488885
PIXEL_SPACING_M = 9.593359

WINDOW_SIZE = 5

BIAS = {
    "HH": (1.383863, -2.668324), "HV": (-5.628389, -0.892712),
    "VH": (6.038121, -8.525171), "VV": (-1.53899, -1.015972),
}

CRATERS = [
    {
        "id": "F2", "lat_lon": [-87.39, 82.31], "diameter_m": 1100,
        "center_line": 47719, "center_sample": 112,
        "context_half_m": 2000,
        "paper_reported": {"cpr_pct_gt1_interior": 47, "cpr_max": 1.95, "dop_range": [0.1, 0.13], "verdict": "Strong evidence"},
        "containment": {"distance_to_nearest_corner_km": 23.56, "note": "Safely interior."},
    },
    {
        "id": "F3", "lat_lon": [-87.31, 86.333], "diameter_m": 700,
        "center_line": 59527, "center_sample": 29,
        "context_half_m": 1300,
        "paper_reported": {"cpr_pct_gt1_interior": 42, "cpr_max": 1.73, "dop_range": [0.1, 0.13], "verdict": "Likely"},
        "containment": {"distance_to_nearest_corner_km": 29.17, "note": "Cross-track position (sample 29 of 512) is close to the swath's near edge -- the circular interior mask (radius 350m = ~36.5 px) may be partially clipped on that side; reported as-is, not padded or faked."},
    },
]


def vsizip_path(pol):
    return f"/vsizip/{ZIP_PATH}/{INTERNAL_DIR}/{BASE}_{pol}_{STATION}.tif"


def read_complex_window(pol, line_start, line_count):
    path = vsizip_path(pol)
    with rasterio.open(path) as src:
        window = Window(0, line_start, TOTAL_SAMPLES, line_count)
        real = src.read(1, window=window).astype(np.float32)
        imag = src.read(2, window=window).astype(np.float32)
    return (real + 1j * imag).astype(np.complex64)


def local_stokes_dop(A, B):
    PA = uniform_filter(np.abs(A) ** 2, size=WINDOW_SIZE, mode="reflect")
    PB = uniform_filter(np.abs(B) ** 2, size=WINDOW_SIZE, mode="reflect")
    cross = A * np.conj(B)
    Re_AB = uniform_filter(cross.real, size=WINDOW_SIZE, mode="reflect")
    Im_AB = uniform_filter(cross.imag, size=WINDOW_SIZE, mode="reflect")
    S1 = PA + PB
    S2 = PA - PB
    S3 = 2 * Re_AB
    S4 = -2 * Im_AB
    with np.errstate(divide="ignore", invalid="ignore"):
        dop = np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1
    return dop


def stats_block(arr, mask=None):
    vals = arr[mask] if mask is not None else arr[np.isfinite(arr)]
    vals = vals[np.isfinite(vals)]
    n_total = int(arr.size) if mask is None else int(mask.sum())
    n_valid = int(vals.size)
    out = {"n_total_px": n_total, "n_valid_px": n_valid}
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


def run_one(crater):
    t0 = time.time()
    cid = crater["id"]
    print(f"\n=== {cid} ===")

    half_lines_ctx = int(crater["context_half_m"] / LINE_SPACING_M)
    line_start = max(0, crater["center_line"] - half_lines_ctx)
    line_count = min(2 * half_lines_ctx, TOTAL_LINES - line_start)

    HH = read_complex_window("hh", line_start, line_count)
    HV = read_complex_window("hv", line_start, line_count)
    VH = read_complex_window("vh", line_start, line_count)
    VV = read_complex_window("vv", line_start, line_count)
    print(f"Read window {HH.shape} in {time.time()-t0:.1f}s")

    HH = HH - complex(*BIAS["HH"])
    HV = HV - complex(*BIAS["HV"])
    VH = VH - complex(*BIAS["VH"])
    VV = VV - complex(*BIAS["VV"])

    dop_linear = local_stokes_dop(HH, VV)
    sqrt2 = np.sqrt(2.0)
    LH = (HH + 1j * HV) / sqrt2
    LV = (VH + 1j * VV) / sqrt2
    dop_hybrid = local_stokes_dop(LH, LV)

    # circular interior mask, radius = diameter/2, in this window's own pixel grid
    n_lines, n_samples = HH.shape
    local_center_line = crater["center_line"] - line_start
    local_center_sample = crater["center_sample"]
    radius_m = crater["diameter_m"] / 2.0
    rows, cols = np.indices((n_lines, n_samples))
    dist_m = np.hypot((rows - local_center_line) * LINE_SPACING_M, (cols - local_center_sample) * PIXEL_SPACING_M)
    interior_mask = dist_m <= radius_m

    linear_interior = stats_block(dop_linear, interior_mask)
    hybrid_interior = stats_block(dop_hybrid, interior_mask)
    linear_whole = stats_block(dop_linear)
    hybrid_whole = stats_block(dop_hybrid)

    result = {
        "category": "CANDIDATE-SPECIFIC DOP (paper-crater validation)",
        "crater_id": cid,
        "lat_lon_deg": crater["lat_lon"],
        "diameter_m": crater["diameter_m"], "interior_radius_m": radius_m,
        "acquisition": "ch2_sar_ncxl_20200321t082617351_d_fp_d18",
        "source_zip_size_bytes": 4817098756,
        "containment_evidence": crater["containment"],
        "paper_reported": crater["paper_reported"],
        "window": {
            "line_start": line_start, "line_count": line_count,
            "center_line": crater["center_line"], "center_sample": crater["center_sample"],
            "local_covariance_window_px": WINDOW_SIZE,
            "n_interior_px": int(interior_mask.sum()),
        },
        "linear_pol_dop_interior": linear_interior,
        "hybrid_pol_dop_interior": hybrid_interior,
        "linear_pol_dop_whole_window": linear_whole,
        "hybrid_pol_dop_whole_window": hybrid_whole,
        "verdict_vs_paper": {
            "prism_interior_dop_lt_0p13": (linear_interior["mean"] is not None) and (linear_interior["mean"] < 0.13),
            "prism_interior_dop_mean": linear_interior["mean"],
            "paper_dop_range": crater["paper_reported"]["dop_range"],
        },
        "calibration_applied": "XML bias_real/bias_imag subtraction only (per-polarization). No gain-imbalance or phase-orthogonality correction applied -- same limitation as all other DOP results this session.",
    }
    with open(os.path.join(OUT_DIR, f"{cid}_candidate_dop.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    fig, ax = plt.subplots(figsize=(9, 6))
    interior_vals = dop_linear[interior_mask]
    interior_vals = interior_vals[np.isfinite(interior_vals)]
    whole_vals = dop_linear[np.isfinite(dop_linear)]
    ax.hist(whole_vals.ravel(), bins=100, alpha=0.4, label=f"whole window (mean={linear_whole['mean']:.3f})", density=True)
    ax.hist(interior_vals.ravel(), bins=60, alpha=0.7, label=f"crater interior only (mean={linear_interior['mean']:.3f})", density=True)
    ax.axvline(0.13, color="red", linestyle="--", label="paper threshold 0.13")
    ax.set_xlabel("Linear-pol DOP"); ax.set_ylabel("density")
    ax.set_title(f"{cid} -- interior vs whole-window DOP\n({result['acquisition']})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{cid}_dop_histogram.png"), dpi=150)
    plt.close(fig)

    print(f"{cid}: interior linear-pol DOP mean={linear_interior['mean']}, median={linear_interior['median']}, n_px={interior_mask.sum()}")
    print(f"{cid}: whole-window linear-pol DOP mean={linear_whole['mean']}")
    print(f"Total time: {time.time()-t0:.1f}s")
    return result


def main():
    all_results = {}
    for crater in CRATERS:
        all_results[crater["id"]] = run_one(crater)
    with open(os.path.join(OUT_DIR, "F2_F3_dop_combined.json"), "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\n=== SUMMARY ===")
    for cid, r in all_results.items():
        v = r["verdict_vs_paper"]
        print(f"{cid}: interior DOP mean={v['prism_interior_dop_mean']}  <0.13? {v['prism_interior_dop_lt_0p13']}  (paper range: {v['paper_dop_range']})")


if __name__ == "__main__":
    main()
