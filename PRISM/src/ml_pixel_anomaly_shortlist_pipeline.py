"""
PRISM Objective 1 -- Track J-v2 shortlist: extend the real per-pixel Isolation
Forest (independent Pv/CPR/SERD/T-Ratio bands, see ml_pixel_anomaly_pipeline.py
for the primary candidate) to the other 6 PSRs in the 7-candidate shortlist.

Same data-access technique as scripts/legacy/extract_candidate_window_remote.py:
GDAL /vsicurl/ windowed remote reads against the team's shared-Drive-hosted Y4R
(evn/vol/odd/hlx) and L3C (cpr/srd/trt) GeoTIFFs -- reuses the already-resolved
direct-download URLs cached in data/raw/candidate_window_urls.json (verified
still valid: a fresh range request against them returned HTTP 206).

Scope note (see DECISIONS.md / PRISM/docs/ML_METHODS.md for the full reasoning):
this stays at the per-candidate window scale, same as the primary candidate.
A regional *pixel*-level pass is not attempted -- Objective 1's own radar
screening already covers the full region at PSR-aggregate scale (that's what
the existing 336-PSR Isolation Forest v1 uses); a regional pixel-level pass
would require the full Y4R/L3C mosaics at native resolution, i.e. the
multi-GB-download problem this windowed-read technique exists to avoid.

Output: one JSON per candidate under PRISM/outputs/objective1/ml/shortlist/,
plus a summary CSV comparing all 7 (primary + 6) ice-likelihood PSR-interior
vs. approach-terrain separations.
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URLS = json.load(open(os.path.join(REPO, "data", "raw", "candidate_window_urls.json")))
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
CANDIDATE_TABLE = os.path.join(REPO, "PRISM", "outputs", "objective1", "candidate_table_overview.csv")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective1", "ml", "shortlist")
os.makedirs(OUT_DIR, exist_ok=True)

HALF_WINDOW_M = 3300.0  # same window definition as the primary candidate's extraction
MOON_RADIUS = 1737400
RANDOM_STATE = 42

SHORTLIST_IDS = [
    "SP_832640_0090770", "SP_830080_0535120", "SP_842420_0421060",
    "SP_817950_1586580", "SP_819860_1568660", "SP_809570_2454450",
]

GEOG_MOON_WKT = (
    'GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",'
    'SPHEROID["Moon_2000_IAU_IAG",1737400,0]],'
    'PRIMEM["Reference_Meridian",0],UNIT["Degree",0.0174532925199433]]'
)


def read_window(band, bounds, transform_ref):
    vsi = "/vsicurl/" + URLS[band]
    with rasterio.open(vsi) as src:
        if transform_ref["crs"] is None:
            transform_ref["crs"] = src.crs
        window = window_from_bounds(*bounds, transform=src.transform)
        arr = src.read(1, window=window)
    return arr.astype(np.float32)


def run_for_candidate(psr_id, lat, lon, psr_gdf):
    print(f"\n=== {psr_id} ({lat}, {lon}) ===")
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)
    cx, cy = transformer.transform(lon, lat)
    bounds = (cx - HALF_WINDOW_M, cy - HALF_WINDOW_M, cx + HALF_WINDOW_M, cy + HALF_WINDOW_M)

    transform_ref = {"crs": None}
    bands = {b: read_window(b, bounds, transform_ref) for b in ["evn", "vol", "odd", "hlx", "cpr", "srd", "trt"]}
    h, w = bands["evn"].shape
    win_transform = from_bounds(*bounds, w, h)

    total = bands["evn"] + bands["vol"] + bands["odd"] + bands["hlx"]
    valid_pv = np.isfinite(total) & (total > 0)
    pv = np.where(valid_pv, bands["vol"] / np.where(valid_pv, total, np.nan), np.nan).astype(np.float32)

    valid = np.isfinite(pv) & np.isfinite(bands["cpr"]) & np.isfinite(bands["srd"]) & np.isfinite(bands["trt"]) \
        & (bands["cpr"] != 0) & (bands["trt"] != 0)
    n_valid = int(valid.sum())
    print(f"Window {h}x{w} = {h*w} px, {n_valid} valid ({100*n_valid/(h*w):.2f}%)")

    X = np.column_stack([pv[valid], bands["cpr"][valid], bands["srd"][valid], bands["trt"][valid]])
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    iso = IsolationForest(n_estimators=200, contamination="auto", random_state=RANDOM_STATE)
    iso.fit(Xs)
    raw_score = -iso.decision_function(Xs)

    score_grid = np.full((h, w), np.nan, dtype=np.float32)
    score_grid[valid] = raw_score
    smin, smax = np.nanmin(score_grid), np.nanmax(score_grid)
    ice_likelihood = (score_grid - smin) / (smax - smin)

    psr_mask = None
    cand_row = psr_gdf[psr_gdf.PSR_ID == psr_id]
    if not cand_row.empty:
        geom = cand_row.iloc[0].geometry
        psr_mask = geometry_mask([geom], out_shape=(h, w), transform=win_transform, invert=True)

    result = {
        "purpose": "Track J-v2 shortlist -- per-pixel Isolation Forest, real independent Pv/CPR/SERD/T-Ratio bands.",
        "candidate_id": psr_id, "candidate_lat": lat, "candidate_lon": lon,
        "model": "sklearn.ensemble.IsolationForest", "features": ["Pv", "CPR", "SERD", "T-Ratio"],
        "n_pixels_valid": n_valid, "window_shape_px": [h, w], "pixel_size_m": 25.0,
        "source": "Real Y4R+L3C mosaic bands via /vsicurl/ windowed remote read (shared team Drive)",
    }
    if psr_mask is not None:
        inside_scores = ice_likelihood[psr_mask & valid]
        outside_scores = ice_likelihood[(~psr_mask) & valid]
        result["psr_interior_vs_surroundings"] = {
            "n_px_inside_psr": int((psr_mask & valid).sum()),
            "n_px_outside_psr_in_window": int((~psr_mask & valid).sum()),
            "mean_ice_likelihood_inside_psr": float(np.mean(inside_scores)) if inside_scores.size else None,
            "mean_ice_likelihood_outside_psr": float(np.mean(outside_scores)) if outside_scores.size else None,
        }
        print("PSR interior vs surroundings:", json.dumps(result["psr_interior_vs_surroundings"], indent=2))

    with open(os.path.join(OUT_DIR, f"{psr_id}_pixel_anomaly.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    return result


def main():
    candidates = pd.read_csv(CANDIDATE_TABLE)
    psr_gdf = gpd.read_file(PSR_SHP)
    # Reproject to the Y4R raster CRS once we know it (same for all bands/candidates)
    with rasterio.open("/vsicurl/" + URLS["evn"]) as src:
        psr_gdf = psr_gdf.to_crs(src.crs)

    summary = []
    # Include the primary candidate's already-computed result for a complete 7-row comparison table.
    primary_path = os.path.join(REPO, "PRISM", "outputs", "objective1", "ml", "pixel_anomaly_map.json")
    if os.path.exists(primary_path):
        p = json.load(open(primary_path))
        psr = p.get("psr_interior_vs_surroundings", {})
        summary.append({
            "PSR_ID": p["candidate_id"], "mean_ice_likelihood_inside_psr": psr.get("mean_ice_likelihood_inside_psr"),
            "mean_ice_likelihood_outside_psr": psr.get("mean_ice_likelihood_outside_psr"), "n_pixels_valid": p["n_pixels_valid"],
        })

    for psr_id in SHORTLIST_IDS:
        row = candidates[candidates.PSR_ID == psr_id]
        if row.empty:
            print(f"WARNING: {psr_id} not in candidate table, skipping")
            continue
        result = run_for_candidate(psr_id, float(row.lat.iloc[0]), float(row.lon.iloc[0]), psr_gdf)
        psr = result.get("psr_interior_vs_surroundings", {})
        summary.append({
            "PSR_ID": psr_id, "mean_ice_likelihood_inside_psr": psr.get("mean_ice_likelihood_inside_psr"),
            "mean_ice_likelihood_outside_psr": psr.get("mean_ice_likelihood_outside_psr"), "n_pixels_valid": result["n_pixels_valid"],
        })

    summary_df = pd.DataFrame(summary)
    summary_df["separation"] = summary_df.mean_ice_likelihood_inside_psr - summary_df.mean_ice_likelihood_outside_psr
    summary_df = summary_df.sort_values("separation", ascending=False)
    summary_df.to_csv(os.path.join(OUT_DIR, "shortlist_pixel_anomaly_summary.csv"), index=False)
    print("\n", summary_df.to_string(index=False))
    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
