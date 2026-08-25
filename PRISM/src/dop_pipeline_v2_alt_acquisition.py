"""
PRISM DOP -- hypothesis 8: does a genuinely DIFFERENT full-pol DFSAR acquisition
(not just different processing) change the F2/F3 DOP result?

Plan B of the DOP ground-truth investigation (see
outputs/objective1/dop_v2/ and the plan file graceful-wandering-wand.md):
after 7 ruled-out calibration/processing hypotheses on the single acquisition
ch2_sar_ncxl_20200321t082617351_d_fp_d18 used all session, this searches PRADAN
for an alternate full-pol acquisition whose FOOTPRINT genuinely covers both F2
and F3, confirmed by point-in-polygon test in the Moon polar-stereographic
projection (not a loose bounding-box check) -- of 18 full-pol candidates found
near Faustini, only ch2_sar_ncxl_20191105t180525404_d_fp_m65 (2019-11-05,
station m65) covers BOTH craters (F2: 2.08 km inside nearest image-footprint
edge; F3: 3.58 km inside).

Pixel positions located via 0-residual bilinear inversion of the acquisition's
own 4 true corner control points (isda:Geometry_Parameters, in projected
map meters) -- same method as candidate_dop_pipeline_F2F3.py and
candidate_dop_pipeline_SP_832640.py, independently re-derived here for this
acquisition's own geometry (different swath, different corner coordinates,
different line/sample spacing -- this is NOT the d18 acquisition's grid).

Same DOP formula, same bias-only calibration, same circular-interior-mask
methodology as the rest of this session -- only the source acquisition
changes, to isolate whether the high-DOP result is acquisition-specific or a
persistent artifact of DFSAR full-pol data / this processing chain in general.
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
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "dop_v2")
os.makedirs(OUT_DIR, exist_ok=True)

ZIP_PATH = r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20191105t180525404_d_fp_m65.zip"
INTERNAL_DIR = "data/calibrated/20191105"
BASE = "ch2_sar_ncxl_20191105t180525404_d_sli_xx_fp"
STATION = "m65"
TOTAL_SAMPLES = 512
TOTAL_LINES = 57880
LINE_SPACING_M = 0.601246
PIXEL_SPACING_M = 9.593359

WINDOW_SIZE = 5

# isda:polarization_info bias_real/bias_imag from this acquisition's own SLI XML label
# (data/calibrated/20191105/ch2_sar_ncxl_20191105t180525404_d_sli_xx_fp_xx_m65.xml)
BIAS = {
    "HH": (2.403838, -0.413572), "HV": (-4.057937, 4.116325),
    "VH": (8.758044, -4.767118), "VV": (-2.019781, -0.586494),
}

# center_line/center_sample from 0-residual bilinear inversion of this
# acquisition's own 4 true corners (isda:Geometry_Parameters lat/lon,
# forward-projected to Moon polar-stereographic meters, solved with fsolve);
# see investigation notes for the corner values and solve script.
CRATERS = [
    {
        "id": "F2", "lat_lon": [-87.39, 82.31], "diameter_m": 1100,
        "center_line": 36585, "center_sample": 408,
        "context_half_m": 2000,
        "paper_reported": {"cpr_pct_gt1_interior": 47, "cpr_max": 1.95, "dop_range": [0.1, 0.13], "verdict": "Strong evidence"},
        "containment": {"distance_to_nearest_corner_km": 2.08, "note": "Confirmed inside true image-footprint polygon (point-in-polygon, Moon polar-stereographic projection), but margin is much tighter than the baseline d18 acquisition (23.56 km) -- flag if window reads hit no-data."},
    },
    {
        "id": "F3", "lat_lon": [-87.31, 86.333], "diameter_m": 700,
        "center_line": 46264, "center_sample": 332,
        "context_half_m": 1300,
        "paper_reported": {"cpr_pct_gt1_interior": 42, "cpr_max": 1.73, "dop_range": [0.1, 0.13], "verdict": "Likely"},
        "containment": {"distance_to_nearest_corner_km": 3.58, "note": "Confirmed inside true image-footprint polygon; tighter margin than baseline d18 acquisition (29.17 km)."},
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
        "category": "HYPOTHESIS 8 -- alternate acquisition DOP (Plan B of DOP investigation)",
        "crater_id": cid,
        "lat_lon_deg": crater["lat_lon"],
        "diameter_m": crater["diameter_m"], "interior_radius_m": radius_m,
        "acquisition": "ch2_sar_ncxl_20191105t180525404_d_fp_m65",
        "acquisition_date": "2019-11-05",
        "baseline_acquisition_for_comparison": "ch2_sar_ncxl_20200321t082617351_d_fp_d18",
        "source_zip_size_bytes": 813145924,
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
    with open(os.path.join(OUT_DIR, f"{cid}_alt_acquisition_dop.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    fig, ax = plt.subplots(figsize=(9, 6))
    interior_vals = dop_linear[interior_mask]
    interior_vals = interior_vals[np.isfinite(interior_vals)]
    whole_vals = dop_linear[np.isfinite(dop_linear)]
    ax.hist(whole_vals.ravel(), bins=100, alpha=0.4, label=f"whole window (mean={linear_whole['mean']:.3f})", density=True)
    ax.hist(interior_vals.ravel(), bins=60, alpha=0.7, label=f"crater interior only (mean={linear_interior['mean']:.3f})", density=True)
    ax.axvline(0.13, color="red", linestyle="--", label="paper threshold 0.13")
    ax.set_xlabel("Linear-pol DOP"); ax.set_ylabel("density")
    ax.set_title(f"{cid} -- alternate acquisition (2019-11-05, m65)\ninterior vs whole-window DOP")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{cid}_alt_acquisition_histogram.png"), dpi=150)
    plt.close(fig)

    print(f"{cid}: interior linear-pol DOP mean={linear_interior['mean']}, median={linear_interior['median']}, n_px={interior_mask.sum()}")
    print(f"{cid}: whole-window linear-pol DOP mean={linear_whole['mean']}")
    print(f"Total time: {time.time()-t0:.1f}s")
    return result


def main():
    all_results = {}
    for crater in CRATERS:
        all_results[crater["id"]] = run_one(crater)
    with open(os.path.join(OUT_DIR, "F2_F3_alt_acquisition_combined.json"), "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\n=== SUMMARY (alternate acquisition, 2019-11-05 m65) ===")
    for cid, r in all_results.items():
        v = r["verdict_vs_paper"]
        print(f"{cid}: interior DOP mean={v['prism_interior_dop_mean']}  <0.13? {v['prism_interior_dop_lt_0p13']}  (paper range: {v['paper_dop_range']})")


if __name__ == "__main__":
    main()
