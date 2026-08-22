"""
PRISM Objective 1 -- SERD NaN investigation (Phase 1 task 13).

The original notebooks reported a large, PSR-dependent NaN fraction in the SERD
(L3C) raster (0% to ~54% across the 7-candidate shortlist, per
outputs/objective1/serd_nan_investigation.csv) without explaining the cause.
SERD is an ISRO-delivered derived product (not computed by us), so its exact
algorithm is not available to inspect directly. This script tests two testable,
physically plausible hypotheses against the pixel data itself:

  H1 (weak-signal / radar-shadow hypothesis): SERD is NaN preferentially where
     total Y4R backscatter power (evn+vol+odd+hlx) is very low -- i.e. SERD is
     an indeterminate ratio in low-SNR / shadowed pixels.
  H2 (CPR-extremity hypothesis): SERD is NaN preferentially where CPR is near
     a mathematically singular value (e.g. CPR near 0), consistent with SERD
     being derived from a formula that has a singularity there.

This does not change any formula -- it is read-only statistical characterization
of an existing ISRO product to explain a phenomenon already flagged in the audit.
"""

import json
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds as window_from_bounds

L4_DIR = r"C:\Users\radhe\PRISM_local_data\l4_mosaic"
L3C_DIR = r"C:\Users\radhe\PRISM_local_data\l3c_cpr"
PSR_SHP = r"C:\Users\radhe\PRISM_local_data\psr_south\LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp"
OUT_DIR = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM\outputs\objective1"

SHORTLIST_IDS = [
    "SP_832640_0090770", "SP_830080_0535120", "SP_842420_0421060",
    "SP_817950_1586580", "SP_840980_0797630", "SP_819860_1568660",
    "SP_809570_2454450",
]

Y4R_PATHS = {L: os.path.join(L4_DIR, f"ch2_sar_ndxl_20250630my4rspwest_d_{L}_xx_fp_xx_xxx.tif") for L in ["evn", "vol", "odd", "hlx"]}
CPR_PATHS = {L: os.path.join(L3C_DIR, f"ch2_sar_ndxl_20250630mpcpspwest_d_{L}_xx_fp_xx_xxx.tif") for L in ["cpr", "srd", "trt"]}


def read_full_res_window(path, bounds):
    with rasterio.open(path) as src:
        window = window_from_bounds(*bounds, transform=src.transform)
        arr = src.read(1, window=window)
        win_transform = src.window_transform(window)
    return arr.astype(np.float32), win_transform


def main():
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        full_crs = src.crs
    psr = gpd.read_file(PSR_SHP).to_crs(full_crs)

    rows = []
    for psr_id in SHORTLIST_IDS:
        row = psr[psr.PSR_ID == psr_id].iloc[0]
        minx, miny, maxx, maxy = row.geometry.bounds
        buffer = 1000
        bounds = (minx - buffer, miny - buffer, maxx + buffer, maxy + buffer)

        evn_fr, tr = read_full_res_window(Y4R_PATHS["evn"], bounds)
        vol_fr, _ = read_full_res_window(Y4R_PATHS["vol"], bounds)
        odd_fr, _ = read_full_res_window(Y4R_PATHS["odd"], bounds)
        hlx_fr, _ = read_full_res_window(Y4R_PATHS["hlx"], bounds)
        cpr_fr, _ = read_full_res_window(CPR_PATHS["cpr"], bounds)
        srd_fr, _ = read_full_res_window(CPR_PATHS["srd"], bounds)

        total_power = evn_fr + vol_fr + odd_fr + hlx_fr
        valid_total = np.isfinite(total_power) & (total_power > 0)

        psr_mask = geometry_mask([row.geometry], out_shape=evn_fr.shape, transform=tr, invert=True)

        nan_mask = np.isnan(srd_fr)
        finite_mask = np.isfinite(srd_fr)

        # H1: total-power decile comparison between NaN and finite SERD pixels
        common = valid_total  # only compare where Y4R power itself is valid
        power_at_nan = total_power[nan_mask & common]
        power_at_finite = total_power[finite_mask & common]

        # H2: CPR value comparison between NaN and finite SERD pixels
        valid_cpr = np.isfinite(cpr_fr)
        cpr_at_nan = cpr_fr[nan_mask & valid_cpr]
        cpr_at_finite = cpr_fr[finite_mask & valid_cpr]

        # Spatial: NaN fraction inside vs outside the PSR polygon
        nan_inside = float(nan_mask[psr_mask].mean()) if psr_mask.sum() else np.nan
        nan_outside = float(nan_mask[~psr_mask].mean()) if (~psr_mask).sum() else np.nan

        rec = {
            "PSR_ID": psr_id,
            "pct_nan_overall": round(100 * nan_mask.mean(), 2),
            "pct_nan_inside_psr": round(100 * nan_inside, 2),
            "pct_nan_outside_psr": round(100 * nan_outside, 2),
            "median_total_power_at_nan": float(np.median(power_at_nan)) if power_at_nan.size else None,
            "median_total_power_at_finite": float(np.median(power_at_finite)) if power_at_finite.size else None,
            "median_cpr_at_nan": float(np.median(cpr_at_nan)) if cpr_at_nan.size else None,
            "median_cpr_at_finite": float(np.median(cpr_at_finite)) if cpr_at_finite.size else None,
        }
        rows.append(rec)
        print(psr_id, rec)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT_DIR, "serd_nan_hypothesis_test.csv"), index=False)

    # Aggregate verdict
    power_ratio = (df["median_total_power_at_nan"] / df["median_total_power_at_finite"]).dropna()
    cpr_diff = (df["median_cpr_at_nan"] - df["median_cpr_at_finite"]).dropna()

    verdict = {
        "H1_weak_signal_hypothesis": {
            "median_power_ratio_nan_over_finite_across_shortlist": power_ratio.tolist(),
            "mean_ratio": float(power_ratio.mean()) if len(power_ratio) else None,
            "interpretation": (
                "ratio << 1 across the shortlist would support H1 (SERD NaN occurs in low-power/shadow pixels); "
                "ratio ~= 1 would refute it"
            ),
        },
        "H2_cpr_extremity_hypothesis": {
            "median_cpr_diff_nan_minus_finite_across_shortlist": cpr_diff.tolist(),
            "mean_diff": float(cpr_diff.mean()) if len(cpr_diff) else None,
            "interpretation": (
                "a large, consistent negative or positive offset would support H2; near-zero would refute it"
            ),
        },
        "spatial_pattern": "see pct_nan_inside_psr vs pct_nan_outside_psr per PSR in serd_nan_hypothesis_test.csv",
    }

    with open(os.path.join(OUT_DIR, "serd_nan_verdict.json"), "w") as f:
        json.dump(verdict, f, indent=2, default=str)

    print("\n=== VERDICT ===")
    print(json.dumps(verdict, indent=2, default=str))


if __name__ == "__main__":
    main()
