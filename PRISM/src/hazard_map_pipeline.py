"""
PRISM Objective 2 -- Track G-v2: combined hazard map (slope + roughness +
illumination) for candidate SP_840980_0797630.

Ports the algorithms from notebooks/obj2_probably.ipynb (Sobel-gradient slope,
RMS local roughness, multi-azimuth/elevation horizon-shadow illumination
fraction, weighted hazard combination) -- but fixes a real bug in that
notebook: its DEM-loading cell's own comment says "we need raw elevation",
but the URL it actually reads is LDSM_80S_20MPP_ADJ.TIF, which is NASA's
PRE-COMPUTED SLOPE raster, not the elevation raster (LDEM_80S_20MPP_ADJ.TIF).
Confirmed by exact match: the notebook's printed "elevation range"
(0.00700597558170557 to 59.308616638183594) is identical to this project's
own previously-computed slope_stats min/max in
outputs/objective2/SP_840980_0797630_terrain_stats.json (Track G-v1, which
correctly read LDSM for slope). So every downstream quantity in that notebook
(slope-of-slope, roughness of slope values, illumination ray-cast against
slope-as-height) was computed on the wrong physical quantity. This script
reruns the same algorithms against the CORRECT elevation raster.

Data access: same GDAL /vsicurl/ windowed-remote-read technique as
terrain_pipeline.py (Track G-v1) -- no full multi-GB file download.

Cross-check: this script's Sobel-derived slope is compared against Track G-v1's
NASA-precomputed LDSM slope for the same window/pixels as a sanity check.
"""

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
from rasterio.env import Env
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terrain_algorithms import (
    compute_slope, compute_roughness_rms, compute_cumulative_illumination,
    compute_hazard_map, stats_block,
)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective2")
os.makedirs(OUT_DIR, exist_ok=True)

LDSM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDSM_80S_20MPP_ADJ.TIF"
LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"

CANDIDATE_ID = "SP_840980_0797630"
CANDIDATE_LAT = -84.098
CANDIDATE_LON = 79.764
BUFFER_M = 5000  # same window as Track G-v1, for direct comparability

MOON_RADIUS = 1737400

TRACK_G_V1_PATH = os.path.join(OUT_DIR, f"{CANDIDATE_ID}_terrain_stats.json")


def read_window(url, cx, cy, buffer_m):
    with Env(GDAL_HTTP_TIMEOUT=60, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(url) as src:
            bounds = (cx - buffer_m, cy - buffer_m, cx + buffer_m, cy + buffer_m)
            window = window_from_bounds(*bounds, transform=src.transform)
            arr = src.read(1, window=window)
            win_transform = src.window_transform(window)
            profile = {"crs": str(src.crs), "res": src.res, "nodata": src.nodata}
    return arr.astype(np.float64), win_transform, profile


def main():
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)
    cx, cy = transformer.transform(CANDIDATE_LON, CANDIDATE_LAT)
    print(f"Candidate {CANDIDATE_ID}: x={cx:.2f}, y={cy:.2f}")

    print("Reading LDEM (elevation, correct source)...")
    elev, tr, elev_profile = read_window(LDEM_URL, cx, cy, BUFFER_M)
    pixel_size = 20.0  # native LDEM/LDSM resolution
    print("Elevation window shape:", elev.shape, "range:", np.nanmin(elev), "to", np.nanmax(elev))

    valid = np.isfinite(elev)
    if elev_profile["nodata"] is not None:
        valid &= (elev != elev_profile["nodata"])
    elev_valid = np.where(valid, elev, np.nan)

    print("Computing slope (Sobel, on correct elevation)...")
    slope = compute_slope(elev_valid, pixel_size)
    print("Computing RMS roughness...")
    roughness = compute_roughness_rms(elev_valid)
    print("Computing cumulative illumination (24 ray-cast passes)...")
    illum_frac = compute_cumulative_illumination(elev_valid, pixel_size, n_azimuths=8, sun_elevations=[5, 10, 15])
    print("Computing combined hazard map...")
    hazard = compute_hazard_map(slope, roughness, illum_frac)

    safe_mask = hazard < 0.33
    caution_mask = (hazard >= 0.33) & (hazard < 0.66)
    hazard_mask = hazard >= 0.66
    print(f"Safe: {100*safe_mask.mean():.1f}%  Caution: {100*caution_mask.mean():.1f}%  Hazard: {100*hazard_mask.mean():.1f}%")

    # ---- Cross-check against Track G-v1 (NASA-precomputed LDSM slope) ----
    cross_check = None
    if os.path.exists(TRACK_G_V1_PATH):
        v1 = json.load(open(TRACK_G_V1_PATH))
        v1_slope = v1["slope_stats"]
        finite_slope = slope[valid]
        cross_check = {
            "track_g_v1_ldsm_mean_deg": v1_slope["mean_deg"],
            "track_g_v2_sobel_mean_deg": float(finite_slope.mean()),
            "abs_diff_deg": abs(v1_slope["mean_deg"] - float(finite_slope.mean())),
            "track_g_v1_ldsm_median_deg": v1_slope["median_deg"],
            "track_g_v2_sobel_median_deg": float(np.median(finite_slope)),
            "note": "Two independent slope methods (NASA-precomputed LDSM vs. this script's own Sobel-gradient "
                    "computation from LDEM elevation) on the same window -- agreement supports both being correct; "
                    "large disagreement would flag a bug in one of them.",
        }
        print("Cross-check vs Track G-v1:", json.dumps(cross_check, indent=2))

    # ---- PSR interior mask ----
    psr_mask = None
    try:
        psr = gpd.read_file(PSR_SHP).to_crs(elev_profile["crs"])
        cand_row = psr[psr.PSR_ID == CANDIDATE_ID]
        if not cand_row.empty:
            geom = cand_row.iloc[0].geometry
            psr_mask = geometry_mask([geom], out_shape=elev.shape, transform=tr, invert=True)
            print(f"PSR interior mask: {int(psr_mask.sum())} px")
    except Exception as e:
        print("PSR mask unavailable:", e)

    result = {
        "candidate_id": CANDIDATE_ID,
        "candidate_lat": CANDIDATE_LAT,
        "candidate_lon": CANDIDATE_LON,
        "window_buffer_m": BUFFER_M,
        "pixel_size_m": pixel_size,
        "bug_fix_note": (
            "The source notebook (obj2_probably.ipynb) intended to load elevation but actually read "
            "LDSM_80S_20MPP_ADJ.TIF (NASA's precomputed SLOPE raster), confirmed by its printed value range "
            "(0.007-59.3) exactly matching this project's own prior slope stats. This script fixes that by "
            "reading LDEM_80S_20MPP_ADJ.TIF (elevation, meters) instead. All formulas below are otherwise "
            "unchanged from the source notebook."
        ),
        "dem_source": {
            "elevation_product": "LDEM_80S_20MPP_ADJ.TIF",
            "provider": "NASA GSFC PGDA", "resolution_m_per_px": 20,
            "access_method": "GDAL /vsicurl/ windowed remote read (no full download performed)",
        },
        "slope_deg": stats_block(slope[valid], "Sobel-gradient slope from LDEM"),
        "roughness_rms_m": stats_block(roughness[valid], "5x5 local RMS elevation roughness"),
        "illumination_fraction": stats_block(illum_frac[valid], "Fraction of 24 (8 azimuth x 3 elevation) sun positions illuminated"),
        "hazard_score": {
            **stats_block(hazard[valid], "Weighted hazard = (slope_norm + roughness_norm + (1-illum))/3, equal weights"),
            "pct_safe_lt0.33": float(100 * safe_mask[valid].mean()),
            "pct_caution_0.33to0.66": float(100 * caution_mask[valid].mean()),
            "pct_hazard_gte0.66": float(100 * hazard_mask[valid].mean()),
            "weighting_note": "Equal 1/3 weighting is a documented default (same convention as the Physics Evidence "
                               "Score elsewhere in this project), not literature-calibrated.",
        },
        "cross_check_vs_track_g_v1_ldsm_slope": cross_check,
    }

    if psr_mask is not None:
        inside = valid & psr_mask
        outside = valid & (~psr_mask)
        result["psr_interior_vs_approach"] = {
            "n_px_inside_psr": int(inside.sum()),
            "mean_hazard_inside_psr": float(hazard[inside].mean()) if inside.sum() else None,
            "pct_hazard_gte0.66_inside_psr": float(100 * (hazard[inside] >= 0.66).mean()) if inside.sum() else None,
            "mean_illum_frac_inside_psr": float(illum_frac[inside].mean()) if inside.sum() else None,
            "n_px_outside_psr_in_window": int(outside.sum()),
            "mean_hazard_outside_psr_in_window": float(hazard[outside].mean()) if outside.sum() else None,
            "pct_hazard_gte0.66_outside_psr_in_window": float(100 * (hazard[outside] >= 0.66).mean()) if outside.sum() else None,
            "mean_illum_frac_outside_psr_in_window": float(illum_frac[outside].mean()) if outside.sum() else None,
            "note": "PSR interior = the actual ice-candidate floor (should be near-zero illumination by definition -- "
                    "that's what makes it a PSR); 'outside' is the surrounding approach terrain a lander must cross.",
        }
        print("PSR interior vs approach:", json.dumps(result["psr_interior_vs_approach"], indent=2))

    with open(os.path.join(OUT_DIR, f"{CANDIDATE_ID}_hazard_map_v2.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    # ---- Figure ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    im0 = axes[0, 0].imshow(np.where(valid, slope, np.nan), cmap="RdYlGn_r", vmin=0, vmax=30)
    axes[0, 0].set_title("Slope (deg, Sobel from LDEM)"); plt.colorbar(im0, ax=axes[0, 0])
    im1 = axes[0, 1].imshow(np.where(valid, roughness, np.nan), cmap="inferno")
    axes[0, 1].set_title("RMS Roughness (m)"); plt.colorbar(im1, ax=axes[0, 1])
    im2 = axes[1, 0].imshow(np.where(valid, illum_frac, np.nan), cmap="gray", vmin=0, vmax=1)
    axes[1, 0].set_title("Illumination Fraction (24 sun positions)"); plt.colorbar(im2, ax=axes[1, 0])
    im3 = axes[1, 1].imshow(np.where(valid, hazard, np.nan), cmap="RdYlGn_r", vmin=0, vmax=1)
    axes[1, 1].set_title("Combined Hazard Score"); plt.colorbar(im3, ax=axes[1, 1])
    if psr_mask is not None:
        for ax in axes.flat:
            ax.contour(psr_mask, colors="cyan", linewidths=1.2)
    plt.suptitle(f"{CANDIDATE_ID} -- Track G-v2 (bug-fixed: real LDEM elevation)")
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{CANDIDATE_ID}_hazard_map_v2.png"), dpi=150)
    plt.close(fig)

    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
