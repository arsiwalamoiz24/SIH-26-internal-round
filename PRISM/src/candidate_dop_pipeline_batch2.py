"""
PRISM -- CANDIDATE-SPECIFIC DOP for SP_819860_1568660 and SP_830080_0535120.

Same method as src/candidate_dop_pipeline.py (primary candidate) and
src/candidate_dop_pipeline_SP_832640.py: covering acquisitions found via a
full 602-manifest scan (point-in-polygon against true PDS4 image-footprint
corners), pixel position located via 0-residual bilinear inversion of those
same 4 corners.

SP_819860_1568660: acquisition ch2_sar_ncxl_20220408t112037436_d_fp_d18,
  polygon margin only 1.47 km (thinnest of all candidates found so far) --
  bilinear inversion places it at line 142148 of 142172 total lines
  (99.98% along-track, ~24 lines from the true strip end). Flagged as a
  thin-margin case, not a false positive (contains=True, verified).

SP_830080_0535120: acquisition ch2_sar_ncxl_20230917t031302812_d_fp_d32,
  polygon margin 41.05 km, bilinear inversion places it at line 154387 of
  225875 (68% along-track), sample 98 of 244 (40% across) -- safely interior.
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
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "dop_secondary")
os.makedirs(OUT_DIR, exist_ok=True)

WINDOW_SIZE = 5

CONFIGS = [
    {
        "candidate_id": "SP_819860_1568660",
        "cand_lat_lon": [-81.986, 156.866],
        "acquisition": "ch2_sar_ncxl_20220408t112037436_d_fp_d18",
        "zip_path": r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20220408t112037436_d_fp_d18.zip",
        "internal_dir": "data/calibrated/20220408",
        "base": "ch2_sar_ncxl_20220408t112037436_d_sli_xx_fp",
        "station": "d18",
        "total_samples": 244,
        "total_lines": 142172,
        "center_line": 142148,
        "center_sample": 57,
        "half_lines": 500,  # candidate is only 24 lines from the true strip end -- smaller window
        "tile_lines_samples": [25, 61],  # for eigenvalue purity tiling
        "bias": {
            "HH": (-1.261469, 1.423355), "HV": (-0.04723, 3.013441),
            "VH": (-2.221001, 0.772133), "VV": (2.399571, 4.363719),
        },
        "containment": {
            "distance_to_nearest_corner_km": 1.47,
            "bilinear_line_frac": 0.9998, "bilinear_sample_frac": 0.2354,
            "note": "THIN MARGIN -- candidate sits ~24 lines (of 142172) from the true end of this acquisition's strip. Real, verified containment (not a false positive), but the thinnest margin of any candidate confirmed this session.",
        },
        "source_zip_size_bytes": 1052930056,
    },
    {
        "candidate_id": "SP_830080_0535120",
        "cand_lat_lon": [-83.008, 53.512],
        "acquisition": "ch2_sar_ncxl_20230917t031302812_d_fp_d32",
        "zip_path": r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20230917t031302812_d_fp_d32.zip",
        "internal_dir": "data/calibrated/20230917",
        "base": "ch2_sar_ncxl_20230917t031302812_d_sli_xx_fp",
        "station": "d32",
        "total_samples": 244,
        "total_lines": 225875,
        "center_line": 154387,
        "center_sample": 98,
        "half_lines": 1000,
        "tile_lines_samples": [40, 61],
        "bias": {
            "HH": (-0.011092, 2.51078), "HV": (0.725632, 2.880709),
            "VH": (-1.714616, 0.97623), "VV": (3.514545, 4.764772),
        },
        "containment": {
            "distance_to_nearest_corner_km": 41.05,
            "bilinear_line_frac": 0.6835, "bilinear_sample_frac": 0.4026,
            "note": "Safely interior on both axes -- comfortable margin.",
        },
        "source_zip_size_bytes": 1678925641,
    },
]


def vsizip_path(cfg, pol):
    return f"/vsizip/{cfg['zip_path']}/{cfg['internal_dir']}/{cfg['base']}_{pol}_{cfg['station']}.tif"


def read_complex_window(cfg, pol, line_start, line_count):
    path = vsizip_path(cfg, pol)
    with rasterio.open(path) as src:
        window = Window(0, line_start, cfg["total_samples"], line_count)
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


def tiled_eigenvalue_purity(HH, HV, VH, VV, tile_lines, tile_samples):
    n_lines, n_samples = HH.shape
    n_r = max(1, n_lines // tile_lines)
    n_c = max(1, n_samples // tile_samples)
    purity_map = np.full((n_r, n_c), np.nan)
    for ti in range(n_r):
        for tj in range(n_c):
            r0, r1 = ti * tile_lines, min((ti + 1) * tile_lines, n_lines)
            c0, c1 = tj * tile_samples, min((tj + 1) * tile_samples, n_samples)
            k = np.stack([
                HH[r0:r1, c0:c1].ravel(), HV[r0:r1, c0:c1].ravel(),
                VH[r0:r1, c0:c1].ravel(), VV[r0:r1, c0:c1].ravel(),
            ], axis=1)
            if k.shape[0] < 4:
                continue
            C = (k.conj().T @ k) / k.shape[0]
            eig = np.maximum(np.linalg.eigvalsh(C), 0)
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


def run_one(cfg):
    t0 = time.time()
    CAND = cfg["candidate_id"]
    print(f"\n=== {CAND} ({cfg['acquisition']}) ===")

    line_start = max(0, cfg["center_line"] - cfg["half_lines"])
    line_count = min(2 * cfg["half_lines"], cfg["total_lines"] - line_start)

    HH = read_complex_window(cfg, "hh", line_start, line_count)
    HV = read_complex_window(cfg, "hv", line_start, line_count)
    VH = read_complex_window(cfg, "vh", line_start, line_count)
    VV = read_complex_window(cfg, "vv", line_start, line_count)
    print(f"Read window {HH.shape} in {time.time()-t0:.1f}s")

    HH = HH - complex(*cfg["bias"]["HH"])
    HV = HV - complex(*cfg["bias"]["HV"])
    VH = VH - complex(*cfg["bias"]["VH"])
    VV = VV - complex(*cfg["bias"]["VV"])

    dop_linear = local_stokes_dop(HH, VV)
    sqrt2 = np.sqrt(2.0)
    LH = (HH + 1j * HV) / sqrt2
    LV = (VH + 1j * VV) / sqrt2
    dop_hybrid = local_stokes_dop(LH, LV)
    tl, ts = cfg["tile_lines_samples"]
    purity_map = tiled_eigenvalue_purity(HH, HV, VH, VV, tl, ts)

    k_full = np.stack([HH.ravel(), HV.ravel(), VH.ravel(), VV.ravel()], axis=1)
    C_full = (k_full.conj().T @ k_full) / k_full.shape[0]
    eig_full = np.maximum(np.linalg.eigvalsh(C_full), 0)
    p_full = eig_full / eig_full.sum()
    purity_whole_window = float(np.sqrt(max(0.0, (4 * np.sum(p_full ** 2) - 1) / 3)))

    linear_stats = stats_block(dop_linear)
    hybrid_stats = stats_block(dop_hybrid)
    purity_stats = stats_block(purity_map)

    result = {
        "category": "CANDIDATE-SPECIFIC DOP",
        "candidate_id": CAND,
        "candidate_lat_lon_deg": cfg["cand_lat_lon"],
        "acquisition": cfg["acquisition"],
        "source_zip_size_bytes": cfg["source_zip_size_bytes"],
        "containment_evidence": {
            "method": "point-in-polygon ray-casting against true rotated image-footprint corners (isda:image_upper_left/upper_right/lower_right/lower_left_mapX/mapY), same method as all other candidates this session",
            **cfg["containment"],
        },
        "window": {
            "line_start": line_start, "line_count": line_count,
            "sample_start": 0, "sample_count": cfg["total_samples"],
            "center_line": cfg["center_line"], "center_sample": cfg["center_sample"],
            "half_lines": cfg["half_lines"], "local_covariance_window_px": WINDOW_SIZE,
            "eigenvalue_purity_tile_px": cfg["tile_lines_samples"],
        },
        "linear_pol_dop": linear_stats,
        "hybrid_pol_dop": hybrid_stats,
        "eigenvalue_purity_tiled_dop": purity_stats,
        "eigenvalue_purity_whole_window": purity_whole_window,
        "best_supported_formulation": "linear-pol (HH/VV) Stokes-covariance DOP -- same rationale as all other candidates' DOP results this session.",
        "calibration_applied": "XML bias_real/bias_imag subtraction only (per-polarization, from this product's own PDS4 label). No gain-imbalance or phase-orthogonality correction applied.",
        "limitations": [
            f"Single acquisition, single ~{line_count}x{cfg['total_samples']} px window centered on the candidate -- not the full scene, not multi-temporal.",
            "No gain-imbalance/phase-orthogonality calibration applied (bias-centering only).",
            "No independent ground-truth ice confirmation exists for this candidate anywhere in this project.",
        ],
    }
    out_path = os.path.join(OUT_DIR, f"{CAND}_candidate_dop.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.hist(dop_linear[np.isfinite(dop_linear)].ravel(), bins=100, alpha=0.6, label=f"linear-pol (mean={linear_stats['mean']:.3f})", density=True)
    ax.hist(dop_hybrid[np.isfinite(dop_hybrid)].ravel(), bins=100, alpha=0.6, label=f"hybrid-pol (mean={hybrid_stats['mean']:.3f})", density=True)
    ax.set_xlabel("DOP"); ax.set_ylabel("density")
    ax.set_title(f"{CAND} -- CANDIDATE-SPECIFIC DOP\n({cfg['acquisition']})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{CAND}_dop_histogram.png"), dpi=150)
    plt.close(fig)

    print(f"linear-pol DOP: mean={linear_stats['mean']:.3f} median={linear_stats['median']:.3f}")
    print(f"Total time: {time.time()-t0:.1f}s")
    return result


def main():
    all_results = {}
    for cfg in CONFIGS:
        all_results[cfg["candidate_id"]] = run_one(cfg)
    print("\n=== SUMMARY ===")
    for cid, r in all_results.items():
        print(cid, "linear-pol DOP mean =", r["linear_pol_dop"]["mean"], " <0.13?", r["linear_pol_dop"]["mean"] < 0.13)


if __name__ == "__main__":
    main()
