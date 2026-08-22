"""
PRISM Objective 1 -- DFSAR / Y4R / PSR-screening / CPR-SERD-T-Ratio reproduction.

Phase 1 (2026-08-22): reproduces, from real locally-held Chandrayaan-2 DFSAR
products, the candidate-screening pipeline originally developed in
notebooks/objective1_dfsar_validation.ipynb.ipynb and copy-pasted into
notebooks/objective1_y4r_polarimetry.ipynb.ipynb and notebooks/obj2 (1).ipynb.

This script does NOT change any scientific formula from the original notebooks.
Pv = vol / (evn+vol+odd+hlx) (Yamaguchi four-component volume-scattering fraction),
PSR-vs-surroundings differencing, and percentile-tier ranking are computed exactly
as in the audited notebooks. Where this script's results differ numerically from the
figures quoted in PROJECT_STATUS.md, that is called out explicitly, not silently
absorbed.

Data sources used (all confirmed present locally in
C:\\Users\\radhe\\PRISM_local_data, extracted from ZIPs manually placed in
C:\\Users\\radhe\\Downloads -- these are the same ISRO PDS4 products the original
notebooks reference via Google Drive, and were NOT re-downloaded or substituted):
  - Y4R L4 mosaic (evn/vol/odd/hlx), product ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx,
    acquisition/mosaic date 2025-06-30.
  - CPR/SERD/T-Ratio L3C mosaic, product ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx,
    same mosaic date 2025-06-30 (same grid as Y4R -- confirmed by CRS/bounds match
    in the original notebooks and re-verified here).
  - LOLA South Pole PSR shapefile, NAC_POLE_PSR_SOUTH.ZIP -> LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL,
    653 polygons (source: PDS via pds.lroc.im-ldi.com, local copy used).

CRS: Moon_2000_South_Pole_Stereographic (ESRI:103878-equivalent PROJCS baked into
the Y4R/CPR GeoTIFFs), radius 1,737,400 m sphere, latitude_of_origin -90.
"""

import json
import os
import time

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from rasterio.windows import from_bounds as window_from_bounds

L4_DIR = r"C:\Users\radhe\PRISM_local_data\l4_mosaic"
L3C_DIR = r"C:\Users\radhe\PRISM_local_data\l3c_cpr"
PSR_SHP = r"C:\Users\radhe\PRISM_local_data\psr_south\LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp"

OUT_DIR = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM\outputs\objective1"
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_ID = "SP_840980_0797630"
SHORTLIST_IDS = [
    "SP_832640_0090770", "SP_830080_0535120", "SP_842420_0421060",
    "SP_817950_1586580", "SP_840980_0797630", "SP_819860_1568660",
    "SP_809570_2454450",
]

Y4R_PATHS = {
    L: os.path.join(L4_DIR, f"ch2_sar_ndxl_20250630my4rspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["evn", "vol", "odd", "hlx"]
}
CPR_PATHS = {
    L: os.path.join(L3C_DIR, f"ch2_sar_ndxl_20250630mpcpspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["cpr", "srd", "trt"]
}


def read_overview(path, out_shape):
    with rasterio.open(path) as src:
        arr = src.read(1, out_shape=(1, out_shape[0], out_shape[1]), resampling=Resampling.average)
        return arr.squeeze().astype(np.float32)


def read_full_res_window(path, bounds):
    with rasterio.open(path) as src:
        window = window_from_bounds(*bounds, transform=src.transform)
        arr = src.read(1, window=window)
        win_transform = src.window_transform(window)
    return arr.astype(np.float32), win_transform


def main():
    log = {"started": time.strftime("%Y-%m-%d %H:%M:%S")}

    # ---- 1. Overview Pv + PSR screening (reproduces dfsar_validation.ipynb cells 1-22) ----
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        full_bounds = src.bounds
        full_crs = src.crs
        full_w, full_h = src.width, src.height

    print(f"Y4R raster: {full_w}x{full_h}, crs={full_crs}, bounds={full_bounds}")

    out_h = 1500
    out_w = int(out_h * full_w / full_h)

    evn = read_overview(Y4R_PATHS["evn"], (out_h, out_w))
    vol = read_overview(Y4R_PATHS["vol"], (out_h, out_w))
    odd = read_overview(Y4R_PATHS["odd"], (out_h, out_w))
    hlx = read_overview(Y4R_PATHS["hlx"], (out_h, out_w))

    total = evn + vol + odd + hlx
    total_safe = np.where((total <= 0) | ~np.isfinite(total), np.nan, total)
    pv_fraction = vol / total_safe
    finite_pv = pv_fraction[np.isfinite(pv_fraction)]
    p50, p90 = np.percentile(finite_pv, [50, 90])
    print(f"Overview Pv: mean={finite_pv.mean():.3f} median={np.median(finite_pv):.3f} p50={p50:.3f} p90={p90:.3f}")

    score = np.full(pv_fraction.shape, np.nan)
    low = np.isfinite(pv_fraction) & (pv_fraction < p50)
    mod = np.isfinite(pv_fraction) & (pv_fraction >= p50) & (pv_fraction < p90)
    high = np.isfinite(pv_fraction) & (pv_fraction >= p90)
    score[low] = 0
    score[mod] = 1
    score[high] = 2

    psr = gpd.read_file(PSR_SHP)
    print(f"Loaded {len(psr)} PSR polygons, source CRS={psr.crs}")
    psr_aligned = psr.to_crs(full_crs)

    overview_transform = from_bounds(*full_bounds, out_w, out_h)

    results = []
    for idx, row in psr_aligned.iterrows():
        poly_mask = geometry_mask([row.geometry], out_shape=(out_h, out_w), transform=overview_transform, invert=True)
        n_total = poly_mask.sum()
        if n_total == 0:
            continue
        n_high = (poly_mask & (score == 2)).sum()
        n_mod = (poly_mask & (score == 1)).sum()
        n_valid = (poly_mask & np.isfinite(pv_fraction)).sum()
        if n_valid == 0:
            continue
        results.append({
            "PSR_ID": row.PSR_ID, "lat": row.latitude, "lon": row.longitude,
            "area_km2": row.area, "px_with_radar_data": int(n_valid),
            "high_tier_fraction": n_high / n_valid,
            "moderate_plus_fraction": (n_high + n_mod) / n_valid,
        })

    candidate_table = pd.DataFrame(results).sort_values("high_tier_fraction", ascending=False)
    candidate_table.to_csv(os.path.join(OUT_DIR, "candidate_table_overview.csv"), index=False)
    print(f"PSRs with radar coverage: {len(candidate_table)} / {len(psr_aligned)}")

    cand_row = candidate_table[candidate_table.PSR_ID == CANDIDATE_ID]
    if cand_row.empty:
        raise RuntimeError(f"{CANDIDATE_ID} not found in reproduced candidate table -- investigate before proceeding")
    cand_overview = cand_row.iloc[0].to_dict()
    print("Reproduced overview stats for candidate:", cand_overview)
    log["candidate_overview_reproduced"] = cand_overview

    rank = int((candidate_table.PSR_ID.values == CANDIDATE_ID).nonzero()[0][0]) + 1
    log["candidate_overall_rank_by_high_tier_fraction"] = rank
    log["n_psrs_with_radar_coverage"] = int(len(candidate_table))

    # ---- 2. Full-resolution Pv/CPR/SERD/T-Ratio comparison for the shortlist ----
    with rasterio.open(CPR_PATHS["cpr"]) as src:
        cpr_crs, cpr_bounds = src.crs, src.bounds
    crs_match = (cpr_crs == full_crs)
    bounds_match = (cpr_bounds == full_bounds)
    print(f"CPR raster CRS match Y4R: {crs_match}; bounds match: {bounds_match}")
    log["cpr_raster_crs_matches_y4r"] = bool(crs_match)
    log["cpr_raster_bounds_match_y4r"] = bool(bounds_match)

    full_res_rows = []
    serd_nan_report = []
    for psr_id in SHORTLIST_IDS:
        row = psr_aligned[psr_aligned.PSR_ID == psr_id].iloc[0]
        minx, miny, maxx, maxy = row.geometry.bounds
        buffer = 1000
        bounds = (minx - buffer, miny - buffer, maxx + buffer, maxy + buffer)

        evn_fr, tr = read_full_res_window(Y4R_PATHS["evn"], bounds)
        vol_fr, _ = read_full_res_window(Y4R_PATHS["vol"], bounds)
        odd_fr, _ = read_full_res_window(Y4R_PATHS["odd"], bounds)
        hlx_fr, _ = read_full_res_window(Y4R_PATHS["hlx"], bounds)
        cpr_fr, cpr_tr = read_full_res_window(CPR_PATHS["cpr"], bounds)
        srd_fr, srd_tr = read_full_res_window(CPR_PATHS["srd"], bounds)
        trt_fr, trt_tr = read_full_res_window(CPR_PATHS["trt"], bounds)

        total_fr = evn_fr + vol_fr + odd_fr + hlx_fr
        valid_fr = np.isfinite(total_fr) & (total_fr > 0)
        total_safe_fr = np.where(valid_fr, total_fr, np.nan)
        pv_fr = vol_fr / total_safe_fr

        psr_mask_fr = geometry_mask([row.geometry], out_shape=evn_fr.shape, transform=tr, invert=True)
        inside_pv = psr_mask_fr & valid_fr
        outside_pv = (~psr_mask_fr) & valid_fr

        valid_cpr = np.isfinite(cpr_fr) & (cpr_fr != 0)
        inside_cpr = psr_mask_fr & valid_cpr
        outside_cpr = (~psr_mask_fr) & valid_cpr

        valid_srd = np.isfinite(srd_fr)
        inside_srd = psr_mask_fr & valid_srd
        outside_srd = (~psr_mask_fr) & valid_srd

        valid_trt = np.isfinite(trt_fr) & (trt_fr != 0)
        inside_trt = psr_mask_fr & valid_trt
        outside_trt = (~psr_mask_fr) & valid_trt

        rec = {
            "PSR_ID": psr_id, "lat": row.latitude, "lon": row.longitude, "area_km2": row.area,
            "window_shape": str(evn_fr.shape),
            "n_valid_pv_inside": int(inside_pv.sum()), "n_valid_pv_outside": int(outside_pv.sum()),
            "pv_mean_inside": float(pv_fr[inside_pv].mean()) if inside_pv.sum() else np.nan,
            "pv_mean_outside": float(pv_fr[outside_pv].mean()) if outside_pv.sum() else np.nan,
            "n_valid_cpr_inside": int(inside_cpr.sum()),
            "cpr_mean_inside": float(cpr_fr[inside_cpr].mean()) if inside_cpr.sum() else np.nan,
            "cpr_mean_outside": float(cpr_fr[outside_cpr].mean()) if outside_cpr.sum() else np.nan,
            "cpr_pct_gt1_inside": float((cpr_fr[inside_cpr] > 1).mean() * 100) if inside_cpr.sum() else np.nan,
            "n_valid_srd_inside": int(inside_srd.sum()), "n_valid_srd_outside": int(outside_srd.sum()),
            "srd_mean_inside": float(srd_fr[inside_srd].mean()) if inside_srd.sum() else np.nan,
            "srd_mean_outside": float(srd_fr[outside_srd].mean()) if outside_srd.sum() else np.nan,
            "n_valid_trt_inside": int(inside_trt.sum()),
            "trt_mean_inside": float(trt_fr[inside_trt].mean()) if inside_trt.sum() else np.nan,
            "trt_mean_outside": float(trt_fr[outside_trt].mean()) if outside_trt.sum() else np.nan,
        }
        full_res_rows.append(rec)
        print(psr_id, rec)

        # SERD NaN investigation (task 13)
        n_total_win = srd_fr.size
        n_nan = int(np.isnan(srd_fr).sum())
        n_zero = int((srd_fr == 0).sum())
        n_neg = int((srd_fr < 0).sum())
        finite_srd = srd_fr[np.isfinite(srd_fr)]
        with rasterio.open(CPR_PATHS["srd"]) as srd_src:
            srd_nodata = srd_src.nodata
        serd_nan_report.append({
            "PSR_ID": psr_id, "window_size": n_total_win, "n_nan": n_nan,
            "pct_nan": round(100 * n_nan / n_total_win, 2),
            "n_zero": n_zero, "n_negative": n_neg,
            "finite_min": float(finite_srd.min()) if finite_srd.size else None,
            "finite_max": float(finite_srd.max()) if finite_srd.size else None,
            "raster_nodata_metadata": srd_nodata,
        })

        if psr_id == CANDIDATE_ID:
            # Save RGB + Pv/CPR/SERD figure for the candidate specifically
            def norm_db(arr):
                with np.errstate(divide="ignore", invalid="ignore"):
                    db = 10 * np.log10(arr)
                finite = db[np.isfinite(db)]
                if finite.size == 0:
                    return np.zeros_like(arr)
                vmin, vmax = np.percentile(finite, [2, 98])
                return np.clip((db - vmin) / (vmax - vmin), 0, 1)

            rgb = np.dstack([norm_db(evn_fr), norm_db(vol_fr), norm_db(odd_fr)])
            fig, axes = plt.subplots(1, 4, figsize=(24, 6))
            axes[0].imshow(rgb)
            axes[0].contour(psr_mask_fr, colors="cyan", linewidths=1.2)
            axes[0].set_title("Y4R RGB (R=even,G=vol,B=odd)")
            im1 = axes[1].imshow(np.where(valid_fr, pv_fr, np.nan), cmap="viridis", vmin=0, vmax=1)
            axes[1].contour(psr_mask_fr, colors="red", linewidths=1.2)
            axes[1].set_title("Pv"); plt.colorbar(im1, ax=axes[1], shrink=0.7)
            im2 = axes[2].imshow(np.where(valid_cpr, cpr_fr, np.nan), cmap="inferno", vmin=0, vmax=1)
            axes[2].contour(psr_mask_fr, colors="cyan", linewidths=1.2)
            axes[2].set_title("CPR"); plt.colorbar(im2, ax=axes[2], shrink=0.7)
            im3 = axes[3].imshow(np.where(valid_srd, srd_fr, np.nan), cmap="viridis", vmin=0, vmax=1)
            axes[3].contour(psr_mask_fr, colors="cyan", linewidths=1.2)
            axes[3].set_title("SERD"); plt.colorbar(im3, ax=axes[3], shrink=0.7)
            plt.suptitle(f"{CANDIDATE_ID} -- lat {row.latitude}, lon {row.longitude}, area {row.area:.1f} km^2 (Phase 1 reproduction)")
            plt.tight_layout()
            fig.savefig(os.path.join(OUT_DIR, f"{CANDIDATE_ID}_radar_composite.png"), dpi=150)
            plt.close(fig)

    full_res_df = pd.DataFrame(full_res_rows)
    full_res_df.to_csv(os.path.join(OUT_DIR, "shortlist_full_res_comparison.csv"), index=False)

    serd_df = pd.DataFrame(serd_nan_report)
    serd_df.to_csv(os.path.join(OUT_DIR, "serd_nan_investigation.csv"), index=False)

    # ---- 3. Compare against the numbers recorded in PROJECT_STATUS.md ----
    audit_reported = {
        "pv_mean_inside": 0.507, "pv_mean_outside": 0.426,
        "cpr_mean_inside": 0.630, "cpr_mean_outside": 0.532, "cpr_pct_gt1_inside": 7.33,
        "srd_mean_inside": 0.636, "srd_mean_outside": 0.692,
        "trt_mean_inside": 0.651, "trt_mean_outside": 0.531,
        "n_valid_pv_inside": 22810, "area_km2": 14.234,
    }
    cand_repro = full_res_df[full_res_df.PSR_ID == CANDIDATE_ID].iloc[0].to_dict()
    comparison = {}
    for k, audit_v in audit_reported.items():
        repro_v = cand_repro.get(k)
        comparison[k] = {"audit_reported": audit_v, "reproduced": repro_v,
                          "abs_diff": None if repro_v is None else round(abs(repro_v - audit_v), 6)}
    log["candidate_full_res_vs_audit_comparison"] = comparison

    log["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(OUT_DIR, "reproduction_log.json"), "w") as f:
        json.dump(log, f, indent=2, default=str)

    print("\n=== COMPARISON: reproduced vs. audit-reported (SP_840980_0797630) ===")
    for k, v in comparison.items():
        print(f"  {k}: audit={v['audit_reported']}  reproduced={v['reproduced']}  |diff|={v['abs_diff']}")

    print("\nDone. Outputs written to", OUT_DIR)


if __name__ == "__main__":
    main()
