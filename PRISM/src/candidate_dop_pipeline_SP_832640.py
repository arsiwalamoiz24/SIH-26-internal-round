"""
PRISM -- CANDIDATE-SPECIFIC DOP for SP_832640_0090770 (-83.264, 9.077).

Acquisition: ch2_sar_ncxl_20191114t002451477_d_fp_mad (2019-11-14, station mad,
quad-pol L1A-SLANT-RANGE HH/HV/VH/VV). Confirmed to cover the candidate by TWO
independent methods (same standard as the primary candidate SP_840980_0797630):
  1. Point-in-polygon ray-casting against the PDS4 label's TRUE rotated
     image-footprint corners (isda:image_upper_left/upper_right/lower_right/
     lower_left_mapX/mapY, Moon_2000_South_Pole_Stereographic projected
     meters). Candidate is ~5.18 km inside the nearest corner (not the loose
     axis-aligned envelope box -- same lesson already documented for the
     primary candidate).
  2. The acquisition's actual Level-1A Grid CSV (per-pixel lat/lon,
     geometry/calibrated/20191114/..._g_sli_xx_fp_xx_mad.csv, 159,570
     records): nearest sampled grid point is 121 METERS from the candidate
     coordinate.
  3. Independent geometric cross-check: bilinear inversion of the image's 4
     true corner control points (0 residual fit) places the candidate at
     line~6758 of 283,623 (2.4% along-track) and sample~153 of 512 (30% cross
     -track) -- safely interior on both axes, consistent with methods 1-2.

DOP formulas: identical to src/candidate_dop_pipeline.py (linear-pol HH/VV
Stokes, hybrid-pol synthesized LH/LV Stokes, 4x4 eigenvalue purity) --
transcribed unchanged, not re-derived.
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

ZIP_PATH = r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20191114t002451477_d_fp_mad.zip"
INTERNAL_DIR = "data/calibrated/20191114"
BASE = "ch2_sar_ncxl_20191114t002451477_d_sli_xx_fp"

CANDIDATE_ID = "SP_832640_0090770"
CAND_LAT, CAND_LON = -83.264, 9.077

# From bilinear inversion of the 4 true image-footprint corners (0-residual fit)
CENTER_LINE = 6758
CENTER_SAMPLE = 153
HALF_LINES = 1000
TOTAL_LINES = 283623
TOTAL_SAMPLES = 512

WINDOW_SIZE = 5
TILE_LINES, TILE_SAMPLES = 40, 64  # 2000/40=50, 512/64=8 -> 400 tiles


def vsizip_path(pol):
    return f"/vsizip/{ZIP_PATH}/{INTERNAL_DIR}/{BASE}_{pol}_mad.tif"


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


def tiled_eigenvalue_purity(HH, HV, VH, VV, tile_lines, tile_samples):
    n_lines, n_samples = HH.shape
    n_r = n_lines // tile_lines
    n_c = max(1, n_samples // tile_samples)
    purity_map = np.full((n_r, n_c), np.nan)
    for ti in range(n_r):
        for tj in range(n_c):
            r0, r1 = ti * tile_lines, (ti + 1) * tile_lines
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


def main():
    t0 = time.time()
    line_start = max(0, CENTER_LINE - HALF_LINES)
    line_count = min(2 * HALF_LINES, TOTAL_LINES - line_start)

    HH = read_complex_window("hh", line_start, line_count)
    HV = read_complex_window("hv", line_start, line_count)
    VH = read_complex_window("vh", line_start, line_count)
    VV = read_complex_window("vv", line_start, line_count)
    print(f"Read window {HH.shape} in {time.time()-t0:.1f}s")

    # bias-correction from this product's own XML calibration constants
    BIAS = {
        "HH": (2.241162, -0.061271), "HV": (-4.565737, 4.820437),
        "VH": (8.699006, -4.560964), "VV": (-2.199722, -0.508930),
    }
    HH = HH - complex(*BIAS["HH"])
    HV = HV - complex(*BIAS["HV"])
    VH = VH - complex(*BIAS["VH"])
    VV = VV - complex(*BIAS["VV"])

    dop_linear = local_stokes_dop(HH, VV)
    sqrt2 = np.sqrt(2.0)
    LH = (HH + 1j * HV) / sqrt2
    LV = (VH + 1j * VV) / sqrt2
    dop_hybrid = local_stokes_dop(LH, LV)
    purity_map = tiled_eigenvalue_purity(HH, HV, VH, VV, TILE_LINES, TILE_SAMPLES)

    k_full = np.stack([HH.ravel(), HV.ravel(), VH.ravel(), VV.ravel()], axis=1)
    C_full = (k_full.conj().T @ k_full) / k_full.shape[0]
    eig_full = np.maximum(np.linalg.eigvalsh(C_full), 0)
    p_full = eig_full / eig_full.sum()
    purity_whole_window = float(np.sqrt(max(0.0, (4 * np.sum(p_full ** 2) - 1) / 3)))

    linear_stats = stats_block(dop_linear)
    hybrid_stats = stats_block(dop_hybrid)
    purity_stats = stats_block(purity_map)

    acquisition_info = {
        "category": "CANDIDATE-SPECIFIC",
        "candidate_id": CANDIDATE_ID,
        "candidate_lat_lon_deg": [CAND_LAT, CAND_LON],
        "acquisition": "ch2_sar_ncxl_20191114t002451477_d_fp_mad",
        "product_id": "2068911",
        "date_of_pass": "2019-11-14",
        "station": "mad",
        "product_type": "L1A-SLANT-RANGE",
        "num_polarizations": 4,
        "polarizations": ["HH", "HV", "VH", "VV"],
        "source_zip": ZIP_PATH,
        "source_zip_size_bytes": 3993323822,
        "downloaded_via": "PRADAN authenticated session (pradan.issdc.gov.in/ch2/protected/browse.xhtml), Browse and Download > SAR",
        "containment_evidence": {
            "method_1_true_image_footprint_corners": {
                "description": "Point-in-polygon ray-casting test against the PDS4 label's TRUE rotated image-footprint corners.",
                "candidate_projected_xy_m": [32261.266575399244, 201932.84867428246],
                "image_corners_mapXY_m": {
                    "UL": [30872.117115, 206919.299244], "UR": [40737.423604, 202745.043525],
                    "LR": [-25506.094809, 46159.442494], "LL": [-34726.590376, 50075.099771],
                },
                "contains": True,
                "distance_to_nearest_corner_km": 5.18,
            },
            "method_2_actual_grid_csv": {
                "description": "Direct search of the Level-1A Grid CSV for the nearest actual per-pixel lat/lon sample to the candidate.",
                "nearest_grid_point_lat_lon": [-83.264680, 9.110562],
                "nearest_grid_point_distance_m": 121.13,
                "nearest_grid_record_idx": 155787,
                "total_grid_records": 159570,
            },
            "method_3_bilinear_corner_inversion": {
                "description": "Bilinear inversion of the 4 true image-footprint corners as control points -- 0 m residual fit, independent cross-check of pixel position.",
                "line": 6757.99, "sample": 153.16,
                "total_lines": TOTAL_LINES, "total_samples": TOTAL_SAMPLES,
                "along_track_fraction": 0.0238, "cross_track_fraction": 0.2997,
            },
        },
    }

    with open(os.path.join(OUT_DIR, "candidate_acquisition.json"), "w") as f:
        json.dump(acquisition_info, f, indent=2, default=str)

    window_meta = {
        "line_start": line_start, "line_count": line_count,
        "sample_start": 0, "sample_count": TOTAL_SAMPLES,
        "center_line": CENTER_LINE, "center_sample": CENTER_SAMPLE, "half_lines": HALF_LINES,
        "local_covariance_window_px": WINDOW_SIZE,
        "eigenvalue_purity_tile_px": [TILE_LINES, TILE_SAMPLES],
    }

    formulas = {
        "linear_pol_stokes_dop": "S1=<|HH|^2>+<|VV|^2>, S2=<|HH|^2>-<|VV|^2>, S3=2Re(<HH*conj(VV)>), S4=-2Im(<HH*conj(VV)>), DOP=sqrt(S2^2+S3^2+S4^2)/S1, local mean over 5x5 px window",
        "hybrid_pol_stokes_dop": "LH=(HH+j*HV)/sqrt(2), LV=(VH+j*VV)/sqrt(2), then identical Stokes/DOP formula on (LH,LV)",
        "eigenvalue_purity": "k=[HH,HV,VH,VV] per pixel, C=(k^H k)/N over a tile, eig=eigvalsh(C) clipped>=0, p=eig/sum(eig), purity=sqrt(max(0,(4*sum(p^2)-1)/3))",
        "source": "Identical to src/candidate_dop_pipeline.py (primary candidate) -- not re-derived, only re-pointed at this candidate's covering acquisition.",
    }

    result = {
        "category": "CANDIDATE-SPECIFIC DOP",
        "candidate_id": CANDIDATE_ID,
        "acquisition": "ch2_sar_ncxl_20191114t002451477_d_fp_mad",
        "window": window_meta,
        "formulas": formulas,
        "linear_pol_dop": linear_stats,
        "hybrid_pol_dop": hybrid_stats,
        "eigenvalue_purity_tiled_dop": purity_stats,
        "eigenvalue_purity_whole_window": purity_whole_window,
        "best_supported_formulation": "linear-pol (HH/VV) Stokes-covariance DOP -- same rationale as the primary candidate's DOP result.",
        "calibration_applied": "XML bias_real/bias_imag subtraction only (per-polarization, from this product's own PDS4 label). No gain-imbalance or phase-orthogonality correction applied -- same limitation as the primary candidate's DOP result.",
        "channel_mapping_note": "Level-1A SLI product with per-polarization TIF files explicitly named _hh_/_hv_/_vh_/_vv_ in the PDS4 label and filename -- ISRO-labeled directly, not byte-level-inferred.",
        "limitations": [
            "Single acquisition, single ~2000x512 px window centered on the candidate -- not the full scene, not multi-temporal.",
            "No gain-imbalance/phase-orthogonality calibration applied (bias-centering only).",
            "No independent ground-truth ice confirmation exists for this candidate anywhere in this project.",
        ],
    }

    with open(os.path.join(OUT_DIR, "candidate_dop.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    fig, axes = plt.subplots(1, 2, figsize=(10, 10))
    im0 = axes[0].imshow(dop_linear, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    axes[0].set_title(f"{CANDIDATE_ID}\nLinear-pol (HH/VV) DOP -- CANDIDATE-SPECIFIC")
    plt.colorbar(im0, ax=axes[0], shrink=0.6)
    im1 = axes[1].imshow(dop_hybrid, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    axes[1].set_title("Hybrid-pol (synth. LH/LV) DOP -- CANDIDATE-SPECIFIC")
    plt.colorbar(im1, ax=axes[1], shrink=0.6)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "candidate_dop.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.hist(dop_linear[np.isfinite(dop_linear)].ravel(), bins=100, alpha=0.6, label=f"linear-pol (mean={linear_stats['mean']:.3f})", density=True)
    ax.hist(dop_hybrid[np.isfinite(dop_hybrid)].ravel(), bins=100, alpha=0.6, label=f"hybrid-pol (mean={hybrid_stats['mean']:.3f})", density=True)
    ax.hist(purity_map[np.isfinite(purity_map)].ravel(), bins=30, alpha=0.6, label=f"eigenvalue purity, tiled (mean={purity_stats['mean']:.3f})", density=True)
    ax.set_xlabel("DOP"); ax.set_ylabel("density")
    ax.set_title(f"{CANDIDATE_ID} -- CANDIDATE-SPECIFIC DOP\n(ch2_sar_ncxl_20191114t002451477_d_fp_mad)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "candidate_dop_histogram.png"), dpi=150)
    plt.close(fig)

    print(json.dumps(result, indent=2, default=str))
    print(f"\nTotal time: {time.time()-t0:.1f}s. Outputs in {OUT_DIR}")


if __name__ == "__main__":
    main()
