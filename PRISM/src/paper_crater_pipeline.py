"""
PRISM -- Pv/CPR/SERD/T-Ratio at the paper's own confirmed-ice craters F2 and F3
(Sinha et al. 2026, npj Space Exploration 2:22, Table 1/2), inside Faustini's PSR.

Both F2 (diameter 1100 m) and F3 (diameter 700 m) are small doubly-shadowed
sub-features with NO polygon in the LOLA PSR shapefile PRISM otherwise uses
(that catalog is PSR-scale, these are crater-scale features inside a PSR) --
so "interior" here is approximated as a circular mask of radius = diameter/2
around each crater's own coordinate, the closest available analogue to the
paper's own interior-vs-exterior methodology.

Formulas and data sources are unchanged from src/paper_criterion_pipeline.py /
src/candidate_physics_pipeline.py -- same local L4/L3C mosaics, same Pv/CPR
definitions, only the window size and interior-mask shape change to match
these much smaller features.
"""

import json
import os

import numpy as np
import pyproj
import rasterio
from rasterio.windows import from_bounds as window_from_bounds

L4_DIR = r"C:\Users\radhe\PRISM_local_data\l4_mosaic"
L3C_DIR = r"C:\Users\radhe\PRISM_local_data\l3c_cpr"

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "paper_crater_validation")
os.makedirs(OUT_DIR, exist_ok=True)

Y4R_PATHS = {
    L: os.path.join(L4_DIR, f"ch2_sar_ndxl_20250630my4rspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["evn", "vol", "odd", "hlx"]
}
CPR_PATHS = {
    L: os.path.join(L3C_DIR, f"ch2_sar_ndxl_20250630mpcpspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["cpr", "srd", "trt"]
}

GEOG_MOON_WKT = (
    'GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",'
    'SPHEROID["Moon_2000_IAU_IAG",1737400,0]],'
    'PRIMEM["Reference_Meridian",0],UNIT["Degree",0.0174532925199433]]'
)

CRATERS = [
    {
        "id": "F2", "host": "Faustini", "lat": -87.39, "lon": 82.31,
        "diameter_m": 1100, "half_window_m": 2000,
        "paper_reported": {"cpr_pct_gt1_interior": 47, "cpr_max": 1.95, "dop_range": [0.1, 0.13], "verdict": "Strong evidence"},
    },
    {
        "id": "F3", "host": "Faustini", "lat": -87.31, "lon": 86.333,
        "diameter_m": 700, "half_window_m": 1300,
        "paper_reported": {"cpr_pct_gt1_interior": 42, "cpr_max": 1.73, "dop_range": [0.1, 0.13], "verdict": "Likely"},
    },
]


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
    block = {"n_total_px": n_total, "n_valid_px": n_valid}
    if n_valid > 0:
        block.update({"mean": float(np.mean(vals)), "median": float(np.median(vals)),
                       "std": float(np.std(vals)), "min": float(np.min(vals)), "max": float(np.max(vals))})
    else:
        block.update({k: None for k in ["mean", "median", "std", "min", "max"]})
    return block


def main():
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        target_crs = src.crs
    geog_moon = pyproj.CRS.from_wkt(GEOG_MOON_WKT)
    fwd = pyproj.Transformer.from_crs(geog_moon, target_crs, always_xy=True)

    all_results = {}
    for crater in CRATERS:
        cid = crater["id"]
        cand_x, cand_y = fwd.transform(crater["lon"], crater["lat"])
        hw = crater["half_window_m"]
        bounds = (cand_x - hw, cand_y - hw, cand_x + hw, cand_y + hw)
        radius_m = crater["diameter_m"] / 2.0

        evn_w, win_tr, _ = read_window(Y4R_PATHS["evn"], bounds)
        vol_w, _, _ = read_window(Y4R_PATHS["vol"], bounds)
        odd_w, _, _ = read_window(Y4R_PATHS["odd"], bounds)
        hlx_w, _, _ = read_window(Y4R_PATHS["hlx"], bounds)
        cpr_w, _, cpr_nodata = read_window(CPR_PATHS["cpr"], bounds)
        srd_w, _, srd_nodata = read_window(CPR_PATHS["srd"], bounds)
        trt_w, _, trt_nodata = read_window(CPR_PATHS["trt"], bounds)

        total_w = evn_w + vol_w + odd_w + hlx_w
        valid_pv_w = np.isfinite(total_w) & (total_w > 0)
        pv_w = np.where(valid_pv_w, vol_w / np.where(valid_pv_w, total_w, np.nan), np.nan)

        valid_cpr_w = np.isfinite(cpr_w) & (cpr_w != 0) & (cpr_w != (cpr_nodata if cpr_nodata is not None else np.nan))
        valid_srd_w = np.isfinite(srd_w) & (srd_w != (srd_nodata if srd_nodata is not None else np.nan))
        valid_trt_w = np.isfinite(trt_w) & (trt_w != 0) & (trt_w != (trt_nodata if trt_nodata is not None else np.nan))

        # circular interior mask (radius = diameter/2), in the window's own pixel grid
        h, w = pv_w.shape
        rows, cols = np.indices((h, w))
        # window_transform maps (col,row) -> (x,y); build px coords of window center via inverse transform
        col_c, row_c = ~win_tr * (cand_x, cand_y)
        # pixel size (assume square pixels, take from transform)
        px_size = abs(win_tr.a)
        dist_px = np.hypot(cols - col_c, rows - row_c)
        interior_mask = dist_px * px_size <= radius_m
        exterior_mask = ~interior_mask

        def block_for(name, arr, valid_mask, nodata):
            inside = valid_mask & interior_mask
            outside = valid_mask & exterior_mask
            n_cpr_inside = int(inside.sum())
            rec = {
                "interior": stats_block(arr, inside),
                "surroundings": stats_block(arr, outside),
            }
            if name == "cpr" and n_cpr_inside:
                elevated = inside & (arr > 1)
                n_elev = int(elevated.sum())
                rec["interior"]["pct_gt1"] = round(100.0 * n_elev / n_cpr_inside, 3)
                rec["interior"]["max"] = float(arr[inside].max())
            return rec

        pv_block = block_for("pv", pv_w, valid_pv_w, None)
        cpr_block = block_for("cpr", cpr_w, valid_cpr_w, cpr_nodata)
        srd_block = block_for("srd", srd_w, valid_srd_w, srd_nodata)
        trt_block = block_for("trt", trt_w, valid_trt_w, trt_nodata)

        result = {
            "crater_id": cid, "host_psr": crater["host"],
            "lat_lon_deg": [crater["lat"], crater["lon"]],
            "projected_xy_m": [float(cand_x), float(cand_y)],
            "diameter_m": crater["diameter_m"], "interior_radius_m": radius_m,
            "window_half_m": hw, "window_shape_px": list(pv_w.shape),
            "paper_reported": crater["paper_reported"],
            "prism_pv": pv_block, "prism_cpr": cpr_block, "prism_srd": srd_block, "prism_tratio": trt_block,
        }
        all_results[cid] = result
        print(json.dumps({k: v for k, v in result.items() if k not in ("prism_pv","prism_srd","prism_tratio")}, indent=2, default=str))

        with open(os.path.join(OUT_DIR, f"{cid}_faustini_pv_cpr_srd_trt.json"), "w") as f:
            json.dump(result, f, indent=2, default=str)

    with open(os.path.join(OUT_DIR, "F2_F3_combined_pv_cpr_srd_trt.json"), "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
