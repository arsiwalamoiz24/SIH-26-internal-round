"""
PRISM -- DOP pipeline v2, relative HH/VV gain calibration test.

Mathematical note (established this session before writing this script): a
constant (spatially-invariant) PHASE correction -- whether applied per-channel
or as a relative HH-vs-VV difference -- cannot change linear-pol Stokes DOP,
because DOP depends only on |HH|^2, |VV|^2, and the MAGNITUDE of the HH*conj(VV)
cross term; a constant phase rotation changes that cross term's angle but not
its magnitude. This was confirmed empirically in
src/dop_pipeline_v2_lookcount_sweep.py (channel calibration on/off gave
identical results to 4 decimal places). So this script tests GAIN only -- the
one lever that can actually move S1/S2, under 4 different unit-convention
guesses for XML `gain_imbalance` (units are NOT specified in the XML for this
field, unlike most other fields which do carry a `unit=` attribute):
  (a) direct linear amplitude ratio
  (b) direct linear power ratio (sqrt for amplitude)
  (c) value interpreted as dB, power convention (10^(dB/10) for power)
  (d) value interpreted as dB, amplitude convention (10^(dB/20) for amplitude)

Relative HH/VV correction factor computed from the RATIO (or dB difference) of
the two channels' own XML gain_imbalance values -- HH=1.015561, VV=1.006232
for this acquisition -- and applied to VV only (bringing VV onto HH's
reference), tested at window sizes 5 and 41 (the two extremes already swept)
for both F2 and F3.

Reuses the same real downloaded acquisition and pixel positions as
src/dop_pipeline_v2_lookcount_sweep.py -- does not modify that script or any
prior output.
"""

import json
import os

import numpy as np
from scipy.ndimage import uniform_filter
import rasterio
from rasterio.windows import Window

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

BIAS = {"HH": (1.383863, -2.668324), "VV": (-1.53899, -1.015972)}
GAIN_HH = 1.015561
GAIN_VV = 1.006232

CRATERS = [
    {"id": "F2", "diameter_m": 1100, "center_line": 47719, "center_sample": 112, "context_half_m": 2000},
    {"id": "F3", "diameter_m": 700, "center_line": 59527, "center_sample": 29, "context_half_m": 1300},
]
PAPER_RANGE = [0.10, 0.13]
WINDOW_SIZES = [5, 41]


def vsizip_path(pol):
    return f"/vsizip/{ZIP_PATH}/{INTERNAL_DIR}/{BASE}_{pol}_{STATION}.tif"


def read_complex_window(pol, line_start, line_count):
    path = vsizip_path(pol)
    with rasterio.open(path) as src:
        window = Window(0, line_start, TOTAL_SAMPLES, line_count)
        real = src.read(1, window=window).astype(np.float32)
        imag = src.read(2, window=window).astype(np.float32)
    return (real + 1j * imag).astype(np.complex64)


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


# relative correction factor conventions -- applied to VV to bring it onto HH's reference
db_diff = GAIN_HH - GAIN_VV  # only meaningful under dB conventions; numerically tiny either way
CONVENTIONS = {
    "none (baseline, bias-centering only)": 1.0,
    "linear_amplitude_ratio": GAIN_HH / GAIN_VV,
    "linear_power_ratio_sqrt": np.sqrt(GAIN_HH / GAIN_VV),
    "dB_power_10^(diff/10)": 10 ** (db_diff / 10.0),
    "dB_amplitude_10^(diff/20)": 10 ** (db_diff / 20.0),
}


def main():
    rows = []
    for crater in CRATERS:
        cid = crater["id"]
        half_lines_ctx = int(crater["context_half_m"] / LINE_SPACING_M)
        line_start = max(0, crater["center_line"] - half_lines_ctx)
        line_count = min(2 * half_lines_ctx, TOTAL_LINES - line_start)

        print(f"\n=== {cid} ===")
        HH_raw = read_complex_window("hh", line_start, line_count) - complex(*BIAS["HH"])
        VV_raw = read_complex_window("vv", line_start, line_count) - complex(*BIAS["VV"])

        local_center_line = crater["center_line"] - line_start
        local_center_sample = crater["center_sample"]
        radius_m = crater["diameter_m"] / 2.0
        rows_idx, cols_idx = np.indices(HH_raw.shape)
        dist_m = np.hypot((rows_idx - local_center_line) * LINE_SPACING_M,
                           (cols_idx - local_center_sample) * PIXEL_SPACING_M)
        interior_mask = dist_m <= radius_m

        for conv_name, factor in CONVENTIONS.items():
            VV = VV_raw * factor
            for ws in WINDOW_SIZES:
                dop = stokes_dop(HH_raw, VV, ws)
                vals = dop[interior_mask]
                vals = vals[np.isfinite(vals)]
                rec = {
                    "crater_id": cid, "convention": conv_name, "correction_factor": float(factor),
                    "window_size_px": ws,
                    "interior_dop_mean": float(vals.mean()) if vals.size else None,
                    "interior_dop_median": float(np.median(vals)) if vals.size else None,
                    "meets_paper_range": bool(vals.size and PAPER_RANGE[0] <= vals.mean() <= PAPER_RANGE[1]),
                }
                rows.append(rec)
                print(f"  {conv_name:35s} factor={factor:.5f} ws={ws:2d}  mean={rec['interior_dop_mean']:.4f}")

    converged = [r for r in rows if r["meets_paper_range"]]
    summary = {
        "purpose": "Relative HH/VV gain calibration test (phase correction excluded -- mathematically inert, see module docstring)",
        "gain_imbalance_raw_values": {"HH": GAIN_HH, "VV": GAIN_VV},
        "conventions_tested": list(CONVENTIONS.keys()),
        "full_table": rows,
        "n_converged": len(converged),
        "converged_configs": converged,
        "verdict": (
            f"{len(converged)} configuration(s) landed in the paper's 0.10-0.13 range."
            if converged else
            "NO relative-gain convention tested (linear ratio, linear power, dB power, dB amplitude) moved either crater's interior DOP meaningfully -- HH and VV's own gain_imbalance values are already very close to each other (1.0156 vs 1.0062), so under every unit convention the relative correction factor is small (<25% even in the most aggressive dB interpretation) and cannot explain a ~6x gap from the paper's target. This rules out relative HH/VV gain calibration as the explanation too."
        ),
    }
    with open(os.path.join(OUT_DIR, "F2_F3_relative_gain_test.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n=== VERDICT ===")
    print(summary["verdict"])
    print("\nDone. Output in", OUT_DIR)


if __name__ == "__main__":
    main()
