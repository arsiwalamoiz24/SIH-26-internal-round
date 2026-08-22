"""
PRISM Objective 2 -- Track G-v2 shortlist: full-resolution hazard maps
(slope + roughness + illumination + combined score) for the other 6 PSRs in
Objective 1's 7-candidate shortlist (src/radar_pipeline.py's SHORTLIST_IDS),
not just the primary candidate SP_840980_0797630 (already done in
hazard_map_pipeline.py). Same window definition (+/-5000m, native 20m/px),
same algorithms (terrain_algorithms.py), so results are directly comparable
across the shortlist and against the primary candidate's own full-res result.
"""

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.env import Env
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terrain_algorithms import compute_slope, compute_roughness_rms, compute_cumulative_illumination, compute_hazard_map, stats_block

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
CANDIDATE_TABLE = os.path.join(REPO, "PRISM", "outputs", "objective1", "candidate_table_overview.csv")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective2", "shortlist")
os.makedirs(OUT_DIR, exist_ok=True)

LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
BUFFER_M = 5000
NATIVE_PX_SIZE = 20.0
MOON_RADIUS = 1737400

# Same 7-candidate shortlist as src/radar_pipeline.py -- primary candidate excluded
# (already done, full-res, with Track G-v1 cross-check, in hazard_map_pipeline.py).
SHORTLIST_IDS = [
    "SP_832640_0090770", "SP_830080_0535120", "SP_842420_0421060",
    "SP_817950_1586580", "SP_819860_1568660", "SP_809570_2454450",
]


def read_window(url, cx, cy, buffer_m):
    with Env(GDAL_HTTP_TIMEOUT=60, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(url) as src:
            bounds = (cx - buffer_m, cy - buffer_m, cx + buffer_m, cy + buffer_m)
            window = window_from_bounds(*bounds, transform=src.transform)
            arr = src.read(1, window=window)
            win_transform = src.window_transform(window)
            profile = {"crs": str(src.crs), "res": src.res, "nodata": src.nodata}
    return arr.astype(np.float64), win_transform, profile


def run_for_candidate(psr_id, lat, lon, psr_gdf):
    print(f"\n=== {psr_id} ({lat}, {lon}) ===")
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)
    cx, cy = transformer.transform(lon, lat)

    elev, tr, elev_profile = read_window(LDEM_URL, cx, cy, BUFFER_M)
    valid = np.isfinite(elev)
    if elev_profile["nodata"] is not None:
        valid &= (elev != elev_profile["nodata"])
    elev_valid = np.where(valid, elev, np.nan)

    slope = compute_slope(elev_valid, NATIVE_PX_SIZE)
    roughness = compute_roughness_rms(elev_valid)
    illum_frac = compute_cumulative_illumination(elev_valid, NATIVE_PX_SIZE, n_azimuths=8, sun_elevations=[5, 10, 15])
    hazard = compute_hazard_map(slope, roughness, illum_frac)

    safe_mask, caution_mask, hazard_mask = hazard < 0.33, (hazard >= 0.33) & (hazard < 0.66), hazard >= 0.66
    print(f"Safe: {100*safe_mask.mean():.1f}%  Caution: {100*caution_mask.mean():.1f}%  Hazard: {100*hazard_mask.mean():.1f}%")

    psr_mask = None
    cand_row = psr_gdf[psr_gdf.PSR_ID == psr_id]
    if not cand_row.empty:
        geom = cand_row.iloc[0].geometry
        psr_mask = geometry_mask([geom], out_shape=elev.shape, transform=tr, invert=True)

    result = {
        "candidate_id": psr_id, "candidate_lat": lat, "candidate_lon": lon,
        "window_buffer_m": BUFFER_M, "pixel_size_m": NATIVE_PX_SIZE,
        "dem_source": {"elevation_product": "LDEM_80S_20MPP_ADJ.TIF", "provider": "NASA GSFC PGDA",
                       "resolution_m_per_px": 20, "access_method": "GDAL /vsicurl/ windowed remote read"},
        "slope_deg": stats_block(slope[valid], "Sobel-gradient slope from LDEM"),
        "roughness_rms_m": stats_block(roughness[valid], "5x5 local RMS elevation roughness"),
        "illumination_fraction": stats_block(illum_frac[valid], "Fraction of 24 sun positions illuminated"),
        "hazard_score": {
            **stats_block(hazard[valid], "Weighted hazard = (slope_norm + roughness_norm + (1-illum))/3"),
            "pct_safe_lt0.33": float(100 * safe_mask[valid].mean()),
            "pct_caution_0.33to0.66": float(100 * caution_mask[valid].mean()),
            "pct_hazard_gte0.66": float(100 * hazard_mask[valid].mean()),
        },
    }
    if psr_mask is not None:
        inside, outside = valid & psr_mask, valid & (~psr_mask)
        result["psr_interior_vs_approach"] = {
            "n_px_inside_psr": int(inside.sum()),
            "mean_hazard_inside_psr": float(hazard[inside].mean()) if inside.sum() else None,
            "mean_illum_frac_inside_psr": float(illum_frac[inside].mean()) if inside.sum() else None,
            "n_px_outside_psr_in_window": int(outside.sum()),
            "mean_hazard_outside_psr_in_window": float(hazard[outside].mean()) if outside.sum() else None,
            "mean_illum_frac_outside_psr_in_window": float(illum_frac[outside].mean()) if outside.sum() else None,
        }

    with open(os.path.join(OUT_DIR, f"{psr_id}_hazard_map.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    fig, axes = plt.subplots(1, 4, figsize=(24, 6))
    im0 = axes[0].imshow(np.where(valid, slope, np.nan), cmap="RdYlGn_r", vmin=0, vmax=30)
    axes[0].set_title("Slope (deg)"); plt.colorbar(im0, ax=axes[0], shrink=0.7)
    im1 = axes[1].imshow(np.where(valid, roughness, np.nan), cmap="inferno")
    axes[1].set_title("RMS Roughness (m)"); plt.colorbar(im1, ax=axes[1], shrink=0.7)
    im2 = axes[2].imshow(np.where(valid, illum_frac, np.nan), cmap="gray", vmin=0, vmax=1)
    axes[2].set_title("Illumination Fraction"); plt.colorbar(im2, ax=axes[2], shrink=0.7)
    im3 = axes[3].imshow(np.where(valid, hazard, np.nan), cmap="RdYlGn_r", vmin=0, vmax=1)
    axes[3].set_title("Combined Hazard"); plt.colorbar(im3, ax=axes[3], shrink=0.7)
    if psr_mask is not None:
        for ax in axes:
            ax.contour(psr_mask, colors="cyan", linewidths=1.0)
    plt.suptitle(f"{psr_id} -- Track G-v2 shortlist")
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{psr_id}_hazard_map.png"), dpi=130)
    plt.close(fig)

    return result


def main():
    candidates = pd.read_csv(CANDIDATE_TABLE)
    psr_gdf = None
    summary = []
    for psr_id in SHORTLIST_IDS:
        row = candidates[candidates.PSR_ID == psr_id]
        if row.empty:
            print(f"WARNING: {psr_id} not found in candidate table, skipping")
            continue
        lat, lon = float(row.lat.iloc[0]), float(row.lon.iloc[0])
        if psr_gdf is None:
            # Reproject PSR polygons once, using this window's CRS (same CRS regardless of window)
            with Env(GDAL_HTTP_TIMEOUT=60, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
                with rasterio.open(LDEM_URL) as src:
                    crs = src.crs
            psr_gdf = gpd.read_file(PSR_SHP).to_crs(crs)
        result = run_for_candidate(psr_id, lat, lon, psr_gdf)
        summary.append({
            "PSR_ID": psr_id, "lat": lat, "lon": lon,
            "mean_hazard": result["hazard_score"]["mean"],
            "mean_hazard_inside_psr": result.get("psr_interior_vs_approach", {}).get("mean_hazard_inside_psr"),
            "mean_illum_frac_inside_psr": result.get("psr_interior_vs_approach", {}).get("mean_illum_frac_inside_psr"),
        })

    summary_df = pd.DataFrame(summary).sort_values("mean_hazard")
    summary_df.to_csv(os.path.join(OUT_DIR, "shortlist_hazard_summary.csv"), index=False)
    print("\n", summary_df.to_string(index=False))
    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
