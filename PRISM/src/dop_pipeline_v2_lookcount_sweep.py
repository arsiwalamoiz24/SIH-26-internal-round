"""
PRISM -- DOP pipeline v2: window-size (look-count) + channel-calibration sweep,
validated against the paper's own ground truth at F2 and F3 (Sinha et al. 2026,
DOP 0.10-0.13 for both craters).

Does NOT modify or reuse output from src/candidate_dop_pipeline_F2F3.py (v1) --
this is an independent, from-scratch computation, reading the same real
already-downloaded acquisition (ch2_sar_ncxl_20200321t082617351_d_fp_d18.zip)
and the same real bilinear-inversion pixel positions (re-derived here, not
imported, to keep this script self-contained and independently auditable).

Literature check (this session, before writing this script): Kumar et al. 2022
(Adv. Space Res. 70/12, the actual origin of the "CPR>1 & DOP<0.13" criterion
the npj 2026 paper refines) explicitly describes "multilook processing
(averaging several independent estimates of reflectivity) on [T] and [C]
matrices" as standard methodology for this exact DOP computation -- consistent
with treating covariance-window size as a legitimate multilooking parameter to
sweep, not an arbitrary fudge factor. Exact look count/window size and the
precise gain_imbalance/phase_orthogonality application formula were NOT
recoverable from public abstracts (ScienceDirect/IEEE/ResearchGate/LPSC PDFs
all returned 403/405/418 to automated fetch this session) -- so this script
empirically sweeps both, reporting the FULL table, and does not silently pick
a flattering point.

Two independent variables swept:
  1. Covariance window size (5,9,15,21,31,41 px) -- more looks = less small-
     sample DOP bias (standard PolSAR theory).
  2. Channel calibration: OFF (bias-centering only, same as all v1 runs) vs ON
     (additionally divides each channel's complex value by its own XML
     gain_imbalance and rotates by -phase_orthogonality radians before forming
     Stokes parameters -- a standard channel-equalization convention, applied
     per-channel since the XML provides one gain/phase value per polarization,
     not one value per channel-pair).
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

ZIP_PATH = r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20200321t082617351_d_fp_d18.zip"
INTERNAL_DIR = "data/calibrated/20200321"
BASE = "ch2_sar_ncxl_20200321t082617351_d_sli_xx_fp"
STATION = "d18"
TOTAL_SAMPLES = 512
TOTAL_LINES = 343723
LINE_SPACING_M = 0.488885
PIXEL_SPACING_M = 9.593359

BIAS = {
    "HH": (1.383863, -2.668324), "HV": (-5.628389, -0.892712),
    "VH": (6.038121, -8.525171), "VV": (-1.53899, -1.015972),
}
GAIN_IMBALANCE = {"HH": 1.015561, "HV": 0.915277, "VH": 0.940057, "VV": 1.006232}
PHASE_ORTHOGONALITY_RAD = {"HH": 1.569032, "HV": -2.123233, "VH": 1.616139, "VV": -0.686576}

CRATERS = [
    {
        "id": "F2", "diameter_m": 1100,
        "center_line": 47719, "center_sample": 112, "context_half_m": 2000,
        "paper_dop_range": [0.10, 0.13],
    },
    {
        "id": "F3", "diameter_m": 700,
        "center_line": 59527, "center_sample": 29, "context_half_m": 1300,
        "paper_dop_range": [0.10, 0.13],
    },
]

WINDOW_SIZES = [5, 9, 15, 21, 31, 41]
CALIBRATION_MODES = ["off", "on"]


def vsizip_path(pol):
    return f"/vsizip/{ZIP_PATH}/{INTERNAL_DIR}/{BASE}_{pol}_{STATION}.tif"


def read_complex_window(pol, line_start, line_count):
    path = vsizip_path(pol)
    with rasterio.open(path) as src:
        window = Window(0, line_start, TOTAL_SAMPLES, line_count)
        real = src.read(1, window=window).astype(np.float32)
        imag = src.read(2, window=window).astype(np.float32)
    return (real + 1j * imag).astype(np.complex64)


def calibrate_channel(S, pol, apply_gain_phase):
    S = S - complex(*BIAS[pol])
    if apply_gain_phase:
        S = S / GAIN_IMBALANCE[pol] * np.exp(-1j * PHASE_ORTHOGONALITY_RAD[pol])
    return S


def stokes_dop(A, B, window_size):
    PA = uniform_filter(np.abs(A) ** 2, size=window_size, mode="reflect")
    PB = uniform_filter(np.abs(B) ** 2, size=window_size, mode="reflect")
    cross = A * np.conj(B)
    Re_AB = uniform_filter(cross.real, size=window_size, mode="reflect")
    Im_AB = uniform_filter(cross.imag, size=window_size, mode="reflect")
    S1 = PA + PB
    S2 = PA - PB
    S3 = 2 * Re_AB
    S4 = -2 * Im_AB
    with np.errstate(divide="ignore", invalid="ignore"):
        dop = np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1
    return dop


def main():
    t0 = time.time()
    rows = []

    for crater in CRATERS:
        cid = crater["id"]
        half_lines_ctx = int(crater["context_half_m"] / LINE_SPACING_M)
        line_start = max(0, crater["center_line"] - half_lines_ctx)
        line_count = min(2 * half_lines_ctx, TOTAL_LINES - line_start)

        print(f"\n=== {cid}: reading window {line_count}x{TOTAL_SAMPLES} ===")
        HH_raw = read_complex_window("hh", line_start, line_count)
        VV_raw = read_complex_window("vv", line_start, line_count)

        local_center_line = crater["center_line"] - line_start
        local_center_sample = crater["center_sample"]
        radius_m = crater["diameter_m"] / 2.0
        rows_idx, cols_idx = np.indices(HH_raw.shape)
        dist_m = np.hypot((rows_idx - local_center_line) * LINE_SPACING_M,
                           (cols_idx - local_center_sample) * PIXEL_SPACING_M)
        interior_mask = dist_m <= radius_m
        n_interior = int(interior_mask.sum())
        print(f"{cid}: {n_interior} interior px")

        for cal_mode in CALIBRATION_MODES:
            apply_gp = (cal_mode == "on")
            HH = calibrate_channel(HH_raw.copy(), "HH", apply_gp)
            VV = calibrate_channel(VV_raw.copy(), "VV", apply_gp)

            for ws in WINDOW_SIZES:
                dop = stokes_dop(HH, VV, ws)
                vals = dop[interior_mask]
                vals = vals[np.isfinite(vals)]
                rec = {
                    "crater_id": cid,
                    "calibration": cal_mode,
                    "window_size_px": ws,
                    "n_interior_valid_px": int(vals.size),
                    "interior_dop_mean": float(vals.mean()) if vals.size else None,
                    "interior_dop_median": float(np.median(vals)) if vals.size else None,
                    "interior_dop_std": float(vals.std()) if vals.size else None,
                    "paper_dop_range": crater["paper_dop_range"],
                    "meets_paper_range": bool(vals.size and crater["paper_dop_range"][0] <= vals.mean() <= crater["paper_dop_range"][1]),
                }
                rows.append(rec)
                print(f"  cal={cal_mode:3s} ws={ws:2d}  mean={rec['interior_dop_mean']:.4f}  median={rec['interior_dop_median']:.4f}")

    with open(os.path.join(OUT_DIR, "F2_F3_sweep_full_table.json"), "w") as f:
        json.dump(rows, f, indent=2, default=str)

    # plot: DOP mean vs window size, one line per (crater, calibration)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, cid in zip(axes, ["F2", "F3"]):
        for cal_mode in CALIBRATION_MODES:
            sub = [r for r in rows if r["crater_id"] == cid and r["calibration"] == cal_mode]
            sub = sorted(sub, key=lambda r: r["window_size_px"])
            ax.plot([r["window_size_px"] for r in sub], [r["interior_dop_mean"] for r in sub],
                     marker="o", label=f"calibration={cal_mode}")
        pr = [r for r in rows if r["crater_id"] == cid][0]["paper_dop_range"]
        ax.axhspan(pr[0], pr[1], color="green", alpha=0.15, label="paper range")
        ax.set_title(f"{cid} interior DOP vs window size")
        ax.set_xlabel("covariance window size (px)")
        ax.set_ylabel("linear-pol DOP (interior mean)")
        ax.legend()
        ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "F2_F3_sweep_plot.png"), dpi=150)
    plt.close(fig)

    # convergence check
    converged = [r for r in rows if r["meets_paper_range"]]
    summary = {
        "purpose": "Window-size + channel-calibration sweep for F2/F3 DOP, validated against paper ground truth (0.10-0.13)",
        "n_configs_tested": len(rows),
        "n_configs_meeting_paper_range": len(converged),
        "converged_configs": converged,
        "full_table": rows,
        "verdict": (
            f"{len(converged)} of {len(rows)} tested configurations landed within the paper's 0.10-0.13 range."
            if converged else
            "NO tested configuration (window size 5-41px, with or without gain/phase channel calibration) brought either crater's interior DOP into the paper's 0.10-0.13 range. This is reported as the honest outcome, not adjusted."
        ),
    }
    with open(os.path.join(OUT_DIR, "F2_F3_sweep_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n=== VERDICT ===")
    print(summary["verdict"])
    print(f"\nTotal time: {time.time()-t0:.1f}s. Outputs in {OUT_DIR}")


if __name__ == "__main__":
    main()
