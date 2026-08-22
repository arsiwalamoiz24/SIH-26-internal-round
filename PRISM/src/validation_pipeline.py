"""
PRISM independent validation -- run the EXISTING Pv/CPR/SERD/T-Ratio/terrain/
evidence-score pipeline (unchanged formulas, src/radar_pipeline.py /
candidate_physics_pipeline.py / terrain_pipeline.py / physics_evidence_score.py)
over independently-sourced ice-reference and control sites.

Does NOT modify the candidate pipeline, DOP thresholds, the 0.13 criterion,
or any existing PRISM output. Read-only reuse of the same formulas/CRS.

South-pole sites only (Y4R/CPR mosaic + LOLA PSR shapefile are south-polar
products) -- north-pole sites (Rozhdestvenskiy, Bosch) are explicitly marked
NO_COVERAGE, not silently skipped or fabricated.
"""

import json
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import pyproj
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds as window_from_bounds

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validation_sites import SITES

L4_DIR = r"C:\Users\radhe\PRISM_local_data\l4_mosaic"
L3C_DIR = r"C:\Users\radhe\PRISM_local_data\l3c_cpr"
PSR_SHP = r"C:\Users\radhe\PRISM_local_data\psr_south\LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp"

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "validation")
os.makedirs(OUT_DIR, exist_ok=True)

Y4R_PATHS = {L: os.path.join(L4_DIR, f"ch2_sar_ndxl_20250630my4rspwest_d_{L}_xx_fp_xx_xxx.tif") for L in ["evn", "vol", "odd", "hlx"]}
CPR_PATHS = {L: os.path.join(L3C_DIR, f"ch2_sar_ndxl_20250630mpcpspwest_d_{L}_xx_fp_xx_xxx.tif") for L in ["cpr", "srd", "trt"]}

GEOG_MOON_WKT = (
    'GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",'
    'SPHEROID["Moon_2000_IAU_IAG",1737400,0]],'
    'PRIMEM["Reference_Meridian",0],UNIT["Degree",0.0174532925199433]]'
)

LDSM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDSM_80S_20MPP_ADJ.TIF"


def read_window(path, bounds):
    with rasterio.open(path) as src:
        window = window_from_bounds(*bounds, transform=src.transform)
        arr = src.read(1, window=window)
        win_transform = src.window_transform(window)
        nodata = src.nodata
    return arr.astype(np.float32), win_transform, nodata


def stats_block(arr, valid_mask):
    vals = arr[valid_mask]
    n_total = int(arr.size)
    n_valid = int(vals.size)
    out = {"n_total_px": n_total, "n_valid_px": n_valid,
           "n_nan_px": n_total - n_valid,
           "pct_nan": round(100.0 * (n_total - n_valid) / n_total, 3) if n_total else None}
    if n_valid:
        pct = np.percentile(vals, [5, 25, 50, 75, 95])
        out.update({"mean": float(vals.mean()), "median": float(np.median(vals)),
                     "std": float(vals.std()), "min": float(vals.min()), "max": float(vals.max()),
                     "p5": float(pct[0]), "p25": float(pct[1]), "p50": float(pct[2]),
                     "p75": float(pct[3]), "p95": float(pct[4])})
    else:
        out.update({k: None for k in ["mean", "median", "std", "min", "max", "p5", "p25", "p50", "p75", "p95"]})
    return out


def main():
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        target_crs = src.crs
        full_bounds = src.bounds
        full_w, full_h = src.width, src.height

    geog_moon = pyproj.CRS.from_wkt(GEOG_MOON_WKT)
    fwd = pyproj.Transformer.from_crs(geog_moon, target_crs, always_xy=True)

    psr = gpd.read_file(PSR_SHP).to_crs(target_crs)

    # overview distribution for relative-percentile scoring (same method as candidate_physics_pipeline.py)
    out_h = 1500
    out_w = int(out_h * full_w / full_h)

    def read_overview(path):
        with rasterio.open(path) as src:
            arr = src.read(1, out_shape=(1, out_h, out_w), resampling=Resampling.average)
            return arr.squeeze().astype(np.float32)

    evn_ov = read_overview(Y4R_PATHS["evn"]); vol_ov = read_overview(Y4R_PATHS["vol"])
    odd_ov = read_overview(Y4R_PATHS["odd"]); hlx_ov = read_overview(Y4R_PATHS["hlx"])
    cpr_ov = read_overview(CPR_PATHS["cpr"]); srd_ov = read_overview(CPR_PATHS["srd"]); trt_ov = read_overview(CPR_PATHS["trt"])
    total_ov = evn_ov + vol_ov + odd_ov + hlx_ov
    total_ov_safe = np.where((total_ov <= 0) | ~np.isfinite(total_ov), np.nan, total_ov)
    pv_ov = vol_ov / total_ov_safe

    def valid_ov(arr):
        return arr[np.isfinite(arr)]

    overview_dist = {"pv": valid_ov(pv_ov), "cpr": valid_ov(cpr_ov), "serd": valid_ov(srd_ov), "tratio": valid_ov(trt_ov)}

    results = []
    for site in SITES:
        rec = {**site}
        if site["region"] != "south":
            rec.update({"status": "NO_COVERAGE", "reason": "north pole -- outside PRISM's south-polar Y4R/CPR mosaic and LOLA PSR catalog"})
            results.append(rec)
            print(site["site_id"], "SKIPPED (north pole, no coverage)")
            continue

        lat, lon = site["lat"], site["lon"]
        x, y = fwd.transform(lon, lat)
        inside_bounds = (full_bounds.left <= x <= full_bounds.right) and (full_bounds.bottom <= y <= full_bounds.top)
        if not inside_bounds:
            rec.update({"status": "OUTSIDE_MOSAIC_BOUNDS", "projected_xy_m": [x, y]})
            results.append(rec)
            print(site["site_id"], "OUTSIDE MOSAIC BOUNDS")
            continue

        half_m = site["window_half_km"] * 1000.0
        bounds = (x - half_m, y - half_m, x + half_m, y + half_m)

        evn_w, tr, _ = read_window(Y4R_PATHS["evn"], bounds)
        vol_w, _, _ = read_window(Y4R_PATHS["vol"], bounds)
        odd_w, _, _ = read_window(Y4R_PATHS["odd"], bounds)
        hlx_w, _, _ = read_window(Y4R_PATHS["hlx"], bounds)
        cpr_w, _, cpr_nodata = read_window(CPR_PATHS["cpr"], bounds)
        srd_w, _, srd_nodata = read_window(CPR_PATHS["srd"], bounds)
        trt_w, _, trt_nodata = read_window(CPR_PATHS["trt"], bounds)

        total_w = evn_w + vol_w + odd_w + hlx_w
        valid_pv = np.isfinite(total_w) & (total_w > 0)
        pv_w = np.where(valid_pv, vol_w / np.where(valid_pv, total_w, np.nan), np.nan)
        valid_cpr = np.isfinite(cpr_w) & (cpr_w != 0) & (cpr_w != (cpr_nodata if cpr_nodata is not None else np.nan))
        valid_srd = np.isfinite(srd_w) & (srd_w != (srd_nodata if srd_nodata is not None else np.nan))
        valid_trt = np.isfinite(trt_w) & (trt_w != 0) & (trt_w != (trt_nodata if trt_nodata is not None else np.nan))

        pv_stats = stats_block(pv_w, valid_pv)
        cpr_stats = stats_block(cpr_w, valid_cpr)
        srd_stats = stats_block(srd_w, valid_srd)
        trt_stats = stats_block(trt_w, valid_trt)

        def rel_pct(metric_key, window_vals):
            dist = overview_dist[metric_key]
            if window_vals.size == 0 or dist.size == 0:
                return None
            return float((dist < np.mean(window_vals)).mean() * 100.0)

        pv_relpct = rel_pct("pv", pv_w[valid_pv])
        cpr_relpct = rel_pct("cpr", cpr_w[valid_cpr])
        trt_relpct = rel_pct("tratio", trt_w[valid_trt])
        srd_relpct = rel_pct("serd", srd_w[valid_srd])

        # PSR membership
        from shapely.geometry import Point
        pt = Point(x, y)
        in_psr = bool(psr.contains(pt).any())
        psr_id_hit = None
        if in_psr:
            hit = psr[psr.contains(pt)]
            if len(hit):
                psr_id_hit = str(hit.iloc[0].PSR_ID)

        # Physics Evidence Score analog: mean of normalized (percentile/100) for Pv/CPR/T-Ratio, SERD excluded
        components = [v for v in [pv_relpct, cpr_relpct, trt_relpct] if v is not None]
        evidence_score = float(np.mean([c / 100.0 for c in components])) if components else None

        # terrain (best-effort; LOLA DEM windowed remote read)
        terrain_stats = None
        try:
            slope_w, _, slope_nodata = read_window(LDSM_URL, bounds)
            valid_slope = np.isfinite(slope_w)
            if slope_nodata is not None:
                valid_slope &= (slope_w != slope_nodata)
            terrain_stats = stats_block(slope_w, valid_slope)
        except Exception as e:
            terrain_stats = {"error": str(e)}

        rec.update({
            "status": "OK",
            "projected_xy_m": [x, y],
            "window_bounds_m": list(bounds),
            "window_shape_px": list(pv_w.shape),
            "in_psr_catalog": in_psr,
            "psr_id": psr_id_hit,
            "pv": pv_stats, "cpr": cpr_stats, "serd": srd_stats, "tratio": trt_stats,
            "pv_relative_percentile": pv_relpct, "cpr_relative_percentile": cpr_relpct,
            "tratio_relative_percentile": trt_relpct, "serd_relative_percentile": srd_relpct,
            "slope_deg": terrain_stats,
            "dop_status": "NOT TESTED -- would require the same per-site acquisition-hunt-and-download workflow used for the original candidate (docs/CANDIDATE_ACQUISITION_SELECTION.md); not attempted for these 13 reference sites in this task",
            "physics_evidence_score_analog": evidence_score,
        })
        results.append(rec)
        print(site["site_id"], "OK", f"Pv={pv_stats['mean']:.3f} CPR={cpr_stats['mean']:.3f} score={evidence_score}")

    with open(os.path.join(OUT_DIR, "validation_raw_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\nDone. Raw results in", OUT_DIR)
    return results


if __name__ == "__main__":
    main()
