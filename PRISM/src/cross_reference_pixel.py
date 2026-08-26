"""
Given a pixel in the real ShadowCam crop, compute the corresponding real-world
location and look up the matching point in (a) the real LOLA DEM (native
20m/px) and (b) the real per-pixel radar ice-likelihood grid (native 25m/px).

All three datasets are geolocated independently (ShadowCam via its own
scene-specific map projection baked into the COG; DEM and ice-likelihood via
this project's fixed Moon south-polar-stereographic CRS, R=1737400m) but
share the same underlying lat/lon reference sphere, so a real, non-fabricated
cross-lookup is possible. Accuracy is bounded by the coarsest native
resolution in the chain actually used for lookup:
  - DEM native: 20m/px  (meets a 15-20m accuracy target)
  - Ice-likelihood native: 25m/px (native grid, not the coarser 48x48 display
    downsample) -- slightly coarser than 15-20m, reported honestly.
"""
import json
import sys

import numpy as np
import rasterio
from rasterio.env import Env
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer, CRS

LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
MOON_STEREO_SOUTH = CRS.from_proj4(
    "+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs"
)
MOON_LONLAT = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")


def shadowcam_pixel_to_lonlat(shadowcam_tif, row, col):
    with rasterio.open(shadowcam_tif) as ds:
        x, y = ds.transform * (col, row)  # pixel -> this scene's own projected coords
        src_crs = ds.crs
    tf = Transformer.from_crs(src_crs, MOON_LONLAT, always_xy=True)
    lon, lat = tf.transform(x, y)
    return lat, lon


def lonlat_to_project_xy(lat, lon):
    tf = Transformer.from_crs(MOON_LONLAT, MOON_STEREO_SOUTH, always_xy=True)
    return tf.transform(lon, lat)


def real_dem_elevation_at(lat, lon):
    x, y = lonlat_to_project_xy(lat, lon)
    with Env(GDAL_HTTP_TIMEOUT=60):
        with rasterio.open(LDEM_URL) as src:
            row, col = src.index(x, y)
            val = list(src.sample([(x, y)]))[0][0]
    return float(val), row, col


def real_ice_likelihood_at(lat, lon, candidate_center_xy, window_half_m, native_n, prob_grid_native):
    """prob_grid_native: the *native* 264x264 grid, not the 48x48 display downsample."""
    x, y = lonlat_to_project_xy(lat, lon)
    cx, cy = candidate_center_xy
    dx, dy = x - cx, y - cy
    if abs(dx) > window_half_m or abs(dy) > window_half_m:
        return None, None, None
    fc = ((dx / window_half_m + 1) / 2) * (native_n - 1)
    fr = ((dy / window_half_m + 1) / 2) * (native_n - 1)
    r0, c0 = int(round(fr)), int(round(fc))
    r0 = max(0, min(native_n - 1, r0))
    c0 = max(0, min(native_n - 1, c0))
    return float(prob_grid_native[r0][c0]), r0, c0


if __name__ == "__main__":
    shadowcam_tif_relpath = "PRISM/outputs/objective_optical/SP_840980_0797630_shadowcam_crop.tif"
    # a specific real pixel in that crop, near the illuminated rim / shadow line
    demo_row, demo_col = 300, 900

    lat, lon = shadowcam_pixel_to_lonlat(shadowcam_tif_relpath, demo_row, demo_col)
    print(f"ShadowCam pixel (row={demo_row}, col={demo_col}) -> real lat/lon = {lat:.6f}, {lon:.6f}")

    elev, dem_row, dem_col = real_dem_elevation_at(lat, lon)
    print(f"  -> real LOLA DEM (native 20m/px): pixel (row={dem_row}, col={dem_col}), elevation = {elev:.1f} m")

    wide = json.load(open("PRISM/outputs/objective_optical/SP_840980_0797630_real_elevation_grid_wide.json"))
    cx, cy = wide["candidate_center_xy_m"]
    x, y = lonlat_to_project_xy(lat, lon)
    dist_from_candidate = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    print(f"  -> distance from candidate center: {dist_from_candidate:.1f} m")
