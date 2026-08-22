"""
PRISM Objective 2 -- LOLA DEM terrain outputs for candidate SP_840980_0797630.

Phase 1 (2026-08-22). Reproduces and completes the DEM/slope workflow started in
notebooks/obj2 (1).ipynb cells 30-34, which never produced a captured result
(DEM download was at 18% when the notebook was last saved).

Data source: NASA GSFC Planetary Geodynamics (PGDA) 20 m/px South Pole LOLA
products, same URLs as the original notebook:
  - LDSM_80S_20MPP_ADJ.TIF  (pre-computed slope map, degrees)
  - LDEM_80S_20MPP_ADJ.TIF  (elevation, meters, adjusted/leveled product)
Server reports Last-Modified: 2023-06-03 for both files (checked via HTTP HEAD).
Grid: 30400x30400 px, 20 m/px, bounds -304000..304000 m in both x and y,
CRS = Moon (2015) Sphere / Ocentric / South Polar Stereographic, sphere radius
1,737,400 m, latitude_of_origin -90. This is the SAME sphere radius and polar
stereographic parameterization as the Y4R/CPR rasters' CRS (Moon_2000, same
radius) -- since both are perfect-sphere projections with identical pole/scale
parameters, projecting the candidate lat/lon into either CRS produces the same
x/y, so results are directly comparable/overlayable with the radar rasters.

Rather than downloading the full ~3.5 GB / ~2.7 GB files (raw HTTP throughput to
this NASA host measured at ~0.17 MB/s from this network -- a multi-hour
download), this script reads ONLY the ~10x10 km window needed around the
candidate directly from the remote, tiled, Cloud-Optimized-GeoTIFF-like files
via GDAL's /vsicurl/ HTTP range-request virtual filesystem. This is a
data-access optimization, not a change to any scientific formula.

What this script adds beyond the original notebook (clearly labeled, not
silently substituted):
  - Elevation statistics and a Terrain Ruggedness Index (TRI, Riley et al. 1999:
    mean absolute elevation difference between each cell and its 8 neighbors)
    computed from LDEM. The original notebook downloaded LDEM but never used it
    for anything; TRI/roughness was flagged as entirely MISSING in the audit.
    This is a NEW computation, not present in any audited notebook, so it
    carries no reproduction burden against prior displayed numbers.

What this script explicitly does NOT do:
  - It does not treat the safe(<10 deg)/caution(10-20 deg)/hazard(>=20 deg)
    slope thresholds as validated. They are carried over verbatim from the
    original notebook, which labeled them "crude thresholds - refine once you
    overlay actual PSR boundary" -- that caveat is preserved here.
"""

import json
import os

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

PSR_SHP = r"C:\Users\radhe\PRISM_local_data\psr_south\LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp"

OUT_DIR = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM\outputs\objective2"
os.makedirs(OUT_DIR, exist_ok=True)

LDSM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDSM_80S_20MPP_ADJ.TIF"
LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"

CANDIDATE_ID = "SP_840980_0797630"
CANDIDATE_LAT = -84.098
CANDIDATE_LON = 79.764
BUFFER_M = 5000  # matches obj2 (1).ipynb cell 31 -- "5km around the 14.2 km^2 PSR"

MOON_RADIUS = 1737400  # meters, sphere -- same value used for the Y4R/CPR rasters' CRS


def read_window(url, cx, cy, buffer_m):
    with Env(GDAL_HTTP_TIMEOUT=60, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(url) as src:
            bounds = (cx - buffer_m, cy - buffer_m, cx + buffer_m, cy + buffer_m)
            window = window_from_bounds(*bounds, transform=src.transform)
            arr = src.read(1, window=window)
            win_transform = src.window_transform(window)
            profile = {"crs": str(src.crs), "res": src.res, "src_bounds": tuple(src.bounds),
                       "src_dims": (src.width, src.height), "nodata": src.nodata}
    return arr.astype(np.float32), win_transform, profile


def tri_riley(elev):
    # Terrain Ruggedness Index (Riley, Degloria & Elliot 1999): mean absolute
    # elevation difference between a cell and its 8 immediate neighbors.
    # Vectorized via 8 shifted-array comparisons (equivalent to a 3x3 window
    # loop, but avoids a 250k-call Python-level per-pixel callback).
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


def main():
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)
    cx, cy = transformer.transform(CANDIDATE_LON, CANDIDATE_LAT)
    print(f"Candidate {CANDIDATE_ID}: lat={CANDIDATE_LAT}, lon={CANDIDATE_LON} -> x={cx:.2f}, y={cy:.2f} (south-polar stereographic, m)")

    slope, tr, slope_profile = read_window(LDSM_URL, cx, cy, BUFFER_M)
    elev, tr2, elev_profile = read_window(LDEM_URL, cx, cy, BUFFER_M)
    print("Slope window shape:", slope.shape, "Elevation window shape:", elev.shape)
    print("Slope raster profile:", slope_profile)
    print("Elevation raster profile:", elev_profile)

    valid_slope = np.isfinite(slope)
    if slope_profile["nodata"] is not None:
        valid_slope &= (slope != slope_profile["nodata"])
    finite_slope = slope[valid_slope]

    valid_elev = np.isfinite(elev)
    if elev_profile["nodata"] is not None:
        valid_elev &= (elev != elev_profile["nodata"])
    finite_elev = elev[valid_elev]

    # --- PSR interior mask (NEW in Phase 1): distinguish the actual ice-candidate
    # interior from the broader approach terrain -- the crater rim dominates the
    # "hazard" pixel count but a lander needs the INTERIOR floor to be assessed
    # separately from the walls it must fly over to reach it. ---
    psr = gpd.read_file(PSR_SHP).to_crs(slope_profile["crs"])
    cand_row = psr[psr.PSR_ID == CANDIDATE_ID]
    psr_mask = None
    if not cand_row.empty:
        geom = cand_row.iloc[0].geometry
        psr_mask = geometry_mask([geom], out_shape=slope.shape, transform=tr, invert=True)
        print(f"PSR polygon found for {CANDIDATE_ID}: {psr_mask.sum()} px inside, out of {psr_mask.size} in window")
    else:
        print(f"WARNING: {CANDIDATE_ID} not found in PSR shapefile when reprojected to {slope_profile['crs']} -- skipping interior/exterior split")

    # --- Slope statistics (as in the original notebook's intent, cells 31-34) ---
    slope_stats = {
        "n_px": int(finite_slope.size),
        "min_deg": float(finite_slope.min()), "max_deg": float(finite_slope.max()),
        "mean_deg": float(finite_slope.mean()), "median_deg": float(np.median(finite_slope)),
        "std_deg": float(finite_slope.std()),
        "percentiles_5_25_50_75_95": [float(x) for x in np.percentile(finite_slope, [5, 25, 50, 75, 95])],
    }
    safe = finite_slope < 10
    caution = (finite_slope >= 10) & (finite_slope < 20)
    hazard = finite_slope >= 20
    slope_stats["pct_safe_lt10deg"] = float(100 * safe.mean())
    slope_stats["pct_caution_10to20deg"] = float(100 * caution.mean())
    slope_stats["pct_hazard_gte20deg"] = float(100 * hazard.mean())
    slope_stats["threshold_source"] = (
        "Carried over verbatim from obj2 (1).ipynb cell 33. Original author's own inline "
        "comment: 'crude thresholds - refine once you overlay actual PSR boundary'. "
        "NOT independently validated against any lander/rover specification in Phase 1."
    )
    if psr_mask is not None:
        inside_valid = valid_slope & psr_mask
        outside_valid = valid_slope & ~psr_mask
        slope_stats["psr_interior_vs_approach"] = {
            "n_px_inside_psr": int(inside_valid.sum()),
            "mean_deg_inside_psr": float(slope[inside_valid].mean()) if inside_valid.sum() else None,
            "median_deg_inside_psr": float(np.median(slope[inside_valid])) if inside_valid.sum() else None,
            "pct_hazard_gte20deg_inside_psr": float(100 * (slope[inside_valid] >= 20).mean()) if inside_valid.sum() else None,
            "n_px_outside_psr_in_window": int(outside_valid.sum()),
            "mean_deg_outside_psr_in_window": float(slope[outside_valid].mean()) if outside_valid.sum() else None,
            "pct_hazard_gte20deg_outside_psr_in_window": float(100 * (slope[outside_valid] >= 20).mean()) if outside_valid.sum() else None,
            "note": "PSR interior = the actual ice-candidate floor; 'outside psr in window' includes the "
                    "crater rim/walls a lander must cross to reach the interior. These are reported "
                    "separately because they can have very different hazard profiles.",
        }
    print("Slope stats:", json.dumps(slope_stats, indent=2))

    # --- Elevation statistics (NEW in Phase 1 -- LDEM was downloaded but unused in obj2) ---
    elev_range = float(finite_elev.max() - finite_elev.min())
    elev_stats = {
        "n_px": int(finite_elev.size),
        "min_m": float(finite_elev.min()), "max_m": float(finite_elev.max()),
        "mean_m": float(finite_elev.mean()), "std_m": float(finite_elev.std()),
        "elevation_range_m": elev_range,
        "note": "NEW in Phase 1 -- not present in any audited notebook. LDEM was downloaded in "
                "obj2 (1).ipynb cell 30 but never opened/used anywhere in that notebook.",
    }
    print("Elevation stats:", json.dumps(elev_stats, indent=2))

    # --- Roughness / TRI (NEW in Phase 1) ---
    cellsize = abs(tr2.a)  # pixel size in meters (20 m/px expected)
    elev_for_tri = np.where(valid_elev, elev, np.nan)
    tri = tri_riley(elev_for_tri)
    finite_tri = tri[np.isfinite(tri)]
    tri_stats = {
        "method": "Riley, Degloria & Elliot (1999) Terrain Ruggedness Index: mean absolute "
                  "elevation difference between each cell and its 8 immediate neighbors, computed "
                  "on the native 20 m/px LDEM grid.",
        "cellsize_m": float(cellsize),
        "mean_tri_m": float(finite_tri.mean()) if finite_tri.size else None,
        "median_tri_m": float(np.median(finite_tri)) if finite_tri.size else None,
        "max_tri_m": float(finite_tri.max()) if finite_tri.size else None,
        "note": "NEW in Phase 1 -- roughness/TRI was entirely absent from all audited notebooks.",
    }
    if psr_mask is not None:
        inside_tri = tri[psr_mask & np.isfinite(tri)]
        outside_tri = tri[(~psr_mask) & np.isfinite(tri)]
        tri_stats["psr_interior_vs_approach"] = {
            "mean_tri_m_inside_psr": float(inside_tri.mean()) if inside_tri.size else None,
            "mean_tri_m_outside_psr_in_window": float(outside_tri.mean()) if outside_tri.size else None,
        }
    print("TRI stats:", json.dumps(tri_stats, indent=2))

    # --- Save figures ---
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    im0 = axes[0].imshow(np.where(valid_slope, slope, np.nan), cmap="RdYlGn_r", vmin=0, vmax=25)
    axes[0].set_title(f"Slope (deg) -- LDSM, {BUFFER_M*2/1000:.0f}x{BUFFER_M*2/1000:.0f} km window")
    plt.colorbar(im0, ax=axes[0], shrink=0.7)
    im1 = axes[1].imshow(np.where(valid_elev, elev, np.nan), cmap="terrain")
    axes[1].set_title("Elevation (m) -- LDEM")
    plt.colorbar(im1, ax=axes[1], shrink=0.7)
    im2 = axes[2].imshow(tri, cmap="magma")
    axes[2].set_title("Terrain Ruggedness Index (m) -- derived from LDEM")
    plt.colorbar(im2, ax=axes[2], shrink=0.7)
    if psr_mask is not None:
        for ax in axes:
            ax.contour(psr_mask, colors="cyan", linewidths=1.2)
    plt.suptitle(f"{CANDIDATE_ID} -- lat {CANDIDATE_LAT}, lon {CANDIDATE_LON} (Phase 1 terrain reproduction)")
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{CANDIDATE_ID}_terrain_composite.png"), dpi=150)
    plt.close(fig)

    # --- Write outputs ---
    result = {
        "candidate_id": CANDIDATE_ID,
        "candidate_lat": CANDIDATE_LAT,
        "candidate_lon": CANDIDATE_LON,
        "candidate_xy_south_polar_stereographic_m": [cx, cy],
        "window_buffer_m": BUFFER_M,
        "window_size_km": BUFFER_M * 2 / 1000,
        "dem_source": {
            "slope_product": "LDSM_80S_20MPP_ADJ.TIF",
            "elevation_product": "LDEM_80S_20MPP_ADJ.TIF",
            "provider": "NASA GSFC PGDA",
            "url_base": "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/",
            "server_last_modified": "2023-06-03 (per HTTP header, both files)",
            "resolution_m_per_px": 20,
            "crs": slope_profile["crs"],
            "access_method": "GDAL /vsicurl/ windowed remote read (no full download performed)",
        },
        "slope_stats": slope_stats,
        "elevation_stats": elev_stats,
        "roughness_tri_stats": tri_stats,
        "figure": f"{CANDIDATE_ID}_terrain_composite.png",
    }
    with open(os.path.join(OUT_DIR, f"{CANDIDATE_ID}_terrain_stats.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    print("\nDone. Outputs written to", OUT_DIR)


if __name__ == "__main__":
    main()
