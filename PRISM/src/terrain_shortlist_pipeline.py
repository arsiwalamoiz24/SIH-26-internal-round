"""
PRISM Objective 2 -- real terrain composites (slope + elevation + TRI) for the
other 6 PSRs in the 7-candidate shortlist, not just the primary candidate
SP_840980_0797630 (already done in terrain_pipeline.py). Same window
definition (+/-5000m, native 20m/px), same DEM source and CRS, so results are
directly comparable across the shortlist and against the primary candidate's
own terrain_composite.png. Modeled directly on the proven
hazard_map_shortlist_pipeline.py (same lat/lon source, same /vsicurl/ windowed
remote-read pattern, same PSR-contour overlay).
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
from terrain_algorithms import compute_slope, stats_block

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
CANDIDATE_TABLE = os.path.join(REPO, "PRISM", "outputs", "objective1", "candidate_table_overview.csv")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective2", "shortlist")
os.makedirs(OUT_DIR, exist_ok=True)

LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
BUFFER_M = 5000
NATIVE_PX_SIZE = 20.0
MOON_RADIUS = 1737400

SHORTLIST_IDS = [
    "SP_832640_0090770", "SP_830080_0535120", "SP_842420_0421060",
    "SP_817950_1586580", "SP_819860_1568660", "SP_809570_2454450",
]


def read_window(url, cx, cy, buffer_m):
    with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(url) as src:
            bounds = (cx - buffer_m, cy - buffer_m, cx + buffer_m, cy + buffer_m)
            window = window_from_bounds(*bounds, transform=src.transform)
            arr = src.read(1, window=window)
            win_transform = src.window_transform(window)
            profile = {"crs": str(src.crs), "res": src.res, "nodata": src.nodata}
    return arr.astype(np.float64), win_transform, profile


def tri_riley(elev):
    padded = np.pad(elev, 1, mode="constant", constant_values=np.nan)
    h, w = elev.shape
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    diffs = np.full((8, h, w), np.nan, dtype=np.float64)
    for k, (dy, dx) in enumerate(offsets):
        neighbor = padded[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
        diffs[k] = np.abs(neighbor - elev)
    with np.errstate(invalid="ignore"):
        tri = np.nanmean(diffs, axis=0)
    tri[~np.isfinite(elev)] = np.nan
    return tri


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
    tri = tri_riley(elev_valid)

    psr_mask = None
    cand_row = psr_gdf[psr_gdf.PSR_ID == psr_id]
    if not cand_row.empty:
        geom = cand_row.iloc[0].geometry
        psr_mask = geometry_mask([geom], out_shape=elev.shape, transform=tr, invert=True)

    finite_slope = slope[valid]
    finite_elev = elev[valid]
    finite_tri = tri[np.isfinite(tri)]

    result = {
        "candidate_id": psr_id, "candidate_lat": lat, "candidate_lon": lon,
        "window_buffer_m": BUFFER_M, "pixel_size_m": NATIVE_PX_SIZE,
        "dem_source": {"elevation_product": "LDEM_80S_20MPP_ADJ.TIF", "provider": "NASA GSFC PGDA",
                       "resolution_m_per_px": 20, "access_method": "GDAL /vsicurl/ windowed remote read"},
        "slope_stats": stats_block(finite_slope, "Sobel-gradient slope from LDEM"),
        "elevation_stats": {
            "n_px": int(finite_elev.size),
            "min_m": float(finite_elev.min()), "max_m": float(finite_elev.max()),
            "mean_m": float(finite_elev.mean()), "std_m": float(finite_elev.std()),
            "elevation_range_m": float(finite_elev.max() - finite_elev.min()),
        },
        "roughness_tri_stats": stats_block(finite_tri, "Riley et al. 1999 TRI, native 20 m/px LDEM"),
    }
    if psr_mask is not None:
        inside, outside = valid & psr_mask, valid & (~psr_mask)
        result["psr_interior_vs_approach"] = {
            "n_px_inside_psr": int(inside.sum()),
            "mean_slope_deg_inside_psr": float(slope[inside].mean()) if inside.sum() else None,
            "mean_tri_m_inside_psr": float(tri[inside & np.isfinite(tri)].mean()) if (inside & np.isfinite(tri)).sum() else None,
            "n_px_outside_psr_in_window": int(outside.sum()),
            "mean_slope_deg_outside_psr_in_window": float(slope[outside].mean()) if outside.sum() else None,
        }

    with open(os.path.join(OUT_DIR, f"{psr_id}_terrain_stats.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    im0 = axes[0].imshow(np.where(valid, slope, np.nan), cmap="RdYlGn_r", vmin=0, vmax=25)
    axes[0].set_title(f"Slope (deg) -- LDSM, {BUFFER_M*2/1000:.0f}x{BUFFER_M*2/1000:.0f} km window")
    plt.colorbar(im0, ax=axes[0], shrink=0.7)
    im1 = axes[1].imshow(np.where(valid, elev, np.nan), cmap="terrain")
    axes[1].set_title("Elevation (m) -- LDEM")
    plt.colorbar(im1, ax=axes[1], shrink=0.7)
    im2 = axes[2].imshow(tri, cmap="magma")
    axes[2].set_title("Terrain Ruggedness Index (m) -- derived from LDEM")
    plt.colorbar(im2, ax=axes[2], shrink=0.7)
    if psr_mask is not None:
        for ax in axes:
            ax.contour(psr_mask, colors="cyan", linewidths=1.2)
    plt.suptitle(f"{psr_id} -- lat {lat}, lon {lon} (shortlist terrain reproduction)")
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{psr_id}_terrain_composite.png"), dpi=150)
    plt.close(fig)

    # ---- Single-panel crop (no title/colorbar) -- for use as a 3D mesh texture ----
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.imshow(np.where(valid, elev, np.nan), cmap="terrain")
    if psr_mask is not None:
        ax2.contour(psr_mask, colors="cyan", linewidths=1.0)
    ax2.axis("off")
    fig2.savefig(os.path.join(OUT_DIR, f"{psr_id}_elevation_only.png"), dpi=150,
                 bbox_inches="tight", pad_inches=0)
    plt.close(fig2)

    print(f"{psr_id}: done -- elev range {result['elevation_stats']['elevation_range_m']:.1f} m")
    return result


def main():
    candidates = pd.read_csv(CANDIDATE_TABLE)
    psr_gdf = None
    for psr_id in SHORTLIST_IDS:
        row = candidates[candidates.PSR_ID == psr_id]
        if row.empty:
            print(f"WARNING: {psr_id} not found in candidate table, skipping")
            continue
        lat, lon = float(row.lat.iloc[0]), float(row.lon.iloc[0])
        if psr_gdf is None:
            with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
                with rasterio.open(LDEM_URL) as src:
                    crs = src.crs
            psr_gdf = gpd.read_file(PSR_SHP).to_crs(crs)
        try:
            run_for_candidate(psr_id, lat, lon, psr_gdf)
        except Exception as e:
            print(f"FAILED {psr_id}: {e}")

    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
