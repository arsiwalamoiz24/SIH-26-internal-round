"""
PRISM -- DOP pipeline v2, first-order crosstalk correction test.

Ainsworth et al. 2006 (the "Ans" algorithm Zhao et al. 2024 uses for DFSAR) was
not accessible this session (paywalled at IEEE/ScienceDirect/MDPI). Rather than
reconstruct a multi-parameter iterative algorithm from imprecise memory, this
script implements a SIMPLER, self-derived first-order crosstalk correction
grounded in the same standard physical assumption these algorithms all use:
for natural distributed terrain with reflection symmetry, the TRUE covariance
between a co-pol channel (HH or VV) and either cross-pol channel (HV, VH)
should be zero. Any measured non-zero <HH,HV*>, <HH,VH*>, <VV,HV*>, <VV,VH*>
is attributed to linear crosstalk leakage from HV/VH into HH/VV, and removed
by solving:

    HH_corrected = HH - v*HV - w*VH   [v,w solve <HH_corrected,HV*>=0, <HH_corrected,VH*>=0]
    VV_corrected = VV - u*HV - z*VH   [u,z solve <VV_corrected,HV*>=0, <VV_corrected,VH*>=0]

each a straightforward 2x2 complex linear system, solved once per crater using
the real aggregate covariance over the full interior mask (same real
already-downloaded acquisition, same real pixel positions as the rest of the
v2 pipeline). This is NOT a verbatim reproduction of Ainsworth 2006 or the
Zhao et al. Ans/Quegan implementation -- it is an independently-derived,
verifiable first-order correction based on the same reflection-symmetry
premise, reported as such.
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
MLN = int(np.ceil(PIXEL_SPACING_M / LINE_SPACING_M))  # 20, per Zhao et al. 2024 Eq. 7

BIAS = {
    "HH": (1.383863, -2.668324), "HV": (-5.628389, -0.892712),
    "VH": (6.038121, -8.525171), "VV": (-1.53899, -1.015972),
}

CRATERS = [
    {"id": "F2", "diameter_m": 1100, "center_line": 47719, "center_sample": 112, "context_half_m": 2000},
    {"id": "F3", "diameter_m": 700, "center_line": 59527, "center_sample": 29, "context_half_m": 1300},
]
PAPER_RANGE = [0.10, 0.13]


def vsizip_path(pol):
    return f"/vsizip/{ZIP_PATH}/{INTERNAL_DIR}/{BASE}_{pol}_{STATION}.tif"


def read_complex_window(pol, line_start, line_count):
    path = vsizip_path(pol)
    with rasterio.open(path) as src:
        window = Window(0, line_start, TOTAL_SAMPLES, line_count)
        real = src.read(1, window=window).astype(np.float32)
        imag = src.read(2, window=window).astype(np.float32)
    return (real + 1j * imag).astype(np.complex64)


def solve_crosstalk(co_pol, hv, vh):
    """Solve co_pol_corrected = co_pol - a*hv - b*vh such that the corrected
    channel is decorrelated from both hv and vh (reflection-symmetry assumption)."""
    A = np.array([
        [np.mean(hv * np.conj(hv)), np.mean(vh * np.conj(hv))],
        [np.mean(hv * np.conj(vh)), np.mean(vh * np.conj(vh))],
    ], dtype=complex)
    b = np.array([np.mean(co_pol * np.conj(hv)), np.mean(co_pol * np.conj(vh))], dtype=complex)
    a, w = np.linalg.solve(A, b)
    return a, w


def stokes_dop(A, B, win_shape):
    PA = uniform_filter(np.abs(A) ** 2, size=win_shape, mode="reflect")
    PB = uniform_filter(np.abs(B) ** 2, size=win_shape, mode="reflect")
    cross = A * np.conj(B)
    Re_AB = uniform_filter(cross.real, size=win_shape, mode="reflect")
    Im_AB = uniform_filter(cross.imag, size=win_shape, mode="reflect")
    S1 = PA + PB
    S2 = PA - PB
    S3 = 2 * Re_AB
    S4 = -2 * Im_AB
    with np.errstate(divide="ignore", invalid="ignore"):
        dop = np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1
    return dop


def aggregate_dop(A, B, mask):
    a = A[mask]; b = B[mask]
    PA = np.mean(np.abs(a) ** 2); PB = np.mean(np.abs(b) ** 2)
    cross = np.mean(a * np.conj(b))
    S1 = PA + PB; S2 = PA - PB; S3 = 2 * cross.real; S4 = -2 * cross.imag
    return np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1


def main():
    results = {}
    for crater in CRATERS:
        cid = crater["id"]
        print(f"\n=== {cid} ===")
        half_lines_ctx = int(crater["context_half_m"] / LINE_SPACING_M)
        line_start = max(0, crater["center_line"] - half_lines_ctx)
        line_count = min(2 * half_lines_ctx, TOTAL_LINES - line_start)

        HH = read_complex_window("hh", line_start, line_count) - complex(*BIAS["HH"])
        HV = read_complex_window("hv", line_start, line_count) - complex(*BIAS["HV"])
        VH = read_complex_window("vh", line_start, line_count) - complex(*BIAS["VH"])
        VV = read_complex_window("vv", line_start, line_count) - complex(*BIAS["VV"])

        local_center_line = crater["center_line"] - line_start
        local_center_sample = crater["center_sample"]
        radius_m = crater["diameter_m"] / 2.0
        rows_idx, cols_idx = np.indices(HH.shape)
        dist_m = np.hypot((rows_idx - local_center_line) * LINE_SPACING_M,
                           (cols_idx - local_center_sample) * PIXEL_SPACING_M)
        mask = dist_m <= radius_m

        hh_i, hv_i, vh_i, vv_i = HH[mask], HV[mask], VH[mask], VV[mask]
        v, w = solve_crosstalk(hh_i, hv_i, vh_i)
        u, z = solve_crosstalk(vv_i, hv_i, vh_i)
        print(f"  crosstalk solved: v={v:.4f} w={w:.4f} (HH<-HV,VH)  u={u:.4f} z={z:.4f} (VV<-HV,VH)")
        print(f"  |v|={abs(v):.4f} |w|={abs(w):.4f} |u|={abs(u):.4f} |z|={abs(z):.4f}  (crosstalk should be << 1 if plausible)")

        HH_corr = HH - v * HV - w * VH
        VV_corr = VV - u * HV - z * VH

        # verify: corrected co-pol should now be decorrelated from HV/VH
        hhc_i, vvc_i = HH_corr[mask], VV_corr[mask]
        resid_hh_hv = np.mean(hhc_i * np.conj(hv_i)) / np.sqrt(np.mean(np.abs(hhc_i)**2)*np.mean(np.abs(hv_i)**2))
        resid_vv_hv = np.mean(vvc_i * np.conj(hv_i)) / np.sqrt(np.mean(np.abs(vvc_i)**2)*np.mean(np.abs(hv_i)**2))
        print(f"  residual normalized <HHcorr,HV*>={resid_hh_hv:.5f} <VVcorr,HV*>={resid_vv_hv:.5f} (should be ~0)")

        dop_agg_before = aggregate_dop(HH, VV, mask)
        dop_agg_after = aggregate_dop(HH_corr, VV_corr, mask)

        table = []
        for win_shape, label in [((MLN, 1), "20x1"), ((MLN, 5), "20x5"), ((5, 5), "5x5")]:
            dop_before = stokes_dop(HH, VV, win_shape)
            dop_after = stokes_dop(HH_corr, VV_corr, win_shape)
            vb = dop_before[mask]; vb = vb[np.isfinite(vb)]
            va = dop_after[mask]; va = va[np.isfinite(va)]
            table.append({
                "window": label,
                "dop_mean_before_crosstalk_correction": float(vb.mean()),
                "dop_mean_after_crosstalk_correction": float(va.mean()),
            })
            print(f"  win={label:6s} before={vb.mean():.4f}  after={va.mean():.4f}")

        result = {
            "crater_id": cid,
            "crosstalk_coefficients": {"v": [v.real, v.imag], "w": [w.real, w.imag], "u": [u.real, u.imag], "z": [z.real, z.imag]},
            "crosstalk_magnitudes_dB": {k: float(20*np.log10(abs(val))) for k, val in [("v",v),("w",w),("u",u),("z",z)]},
            "residual_check_after_correction": {"HHcorr_HV_normcorr": [resid_hh_hv.real, resid_hh_hv.imag], "VVcorr_HV_normcorr": [resid_vv_hv.real, resid_vv_hv.imag]},
            "aggregate_whole_interior_dop": {"before": float(dop_agg_before), "after": float(dop_agg_after)},
            "windowed_table": table,
            "paper_range": PAPER_RANGE,
            "meets_paper_range_after_correction": bool(PAPER_RANGE[0] <= dop_agg_after <= PAPER_RANGE[1]),
        }
        results[cid] = result
        print(f"  AGGREGATE DOP: before={dop_agg_before:.4f}  after={dop_agg_after:.4f}  (paper: {PAPER_RANGE})")

    with open(os.path.join(OUT_DIR, "F2_F3_crosstalk_correction_test.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n=== SUMMARY ===")
    for cid, r in results.items():
        print(f"{cid}: aggregate DOP {r['aggregate_whole_interior_dop']['before']:.3f} -> {r['aggregate_whole_interior_dop']['after']:.3f}  meets paper range: {r['meets_paper_range_after_correction']}")
    print("\nDone. Output in", OUT_DIR)


if __name__ == "__main__":
    main()
