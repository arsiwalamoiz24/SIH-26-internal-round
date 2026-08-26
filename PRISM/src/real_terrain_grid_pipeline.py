"""
Real LOLA DEM elevation grids for 3D terrain visualization.

Two windows are extracted for the primary candidate:
  - "wide": a large-context real elevation grid (real DEM, no photo/ML data),
    used as the base terrain mesh so the frontend can show real geography
    well beyond what the radar/ML pipelines cover.
  - "narrow" (unchanged from before): matches the existing 48x48 real
    Pv/CPR/probIce evidence grid's exact 6.6km window, for direct alignment.

Same /vsicurl/ windowed-remote-read technique and CRS as
hazard_map_pipeline.py (Moon south-polar stereographic, R=1737400m),
LDEM_80S_20MPP_ADJ.TIF (NASA GSFC PGDA), no full download.
"""
import json
import os

import numpy as np
import rasterio
from rasterio.env import Env
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer

LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
MOON_RADIUS = 1737400
OUT_DIR = "PRISM/outputs/objective_optical"


def read_dem_window(cx, cy, half_m):
    with Env(GDAL_HTTP_TIMEOUT=90, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(LDEM_URL) as src:
            bounds = (cx - half_m, cy - half_m, cx + half_m, cy + half_m)
            window = window_from_bounds(*bounds, transform=src.transform)
            arr = src.read(1, window=window).astype(np.float64)
    return arr


def downsample_to_grid(arr, n):
    h, w = arr.shape
    row_idx = np.linspace(0, h - 1, n).astype(int)
    col_idx = np.linspace(0, w - 1, n).astype(int)
    return arr[np.ix_(row_idx, col_idx)]


def process_candidate(cid, lat, lon, half_m, grid_size, tag):
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    tf = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)
    cx, cy = tf.transform(lon, lat)

    dem_native = read_dem_window(cx, cy, half_m)
    dem_grid = downsample_to_grid(dem_native, grid_size)

    elev_mean = float(dem_native.mean())
    relative_grid = (dem_grid - elev_mean).round(3)

    out = {
        "candidate_id": cid,
        "candidate_lat": lat,
        "candidate_lon": lon,
        "candidate_center_xy_m": [cx, cy],
        "grid_size": grid_size,
        "window_half_m": half_m,
        "native_shape": list(dem_native.shape),
        "native_pixel_size_m": 20.0,
        "elevation_source": {
            "product": "LDEM_80S_20MPP_ADJ.TIF",
            "provider": "NASA GSFC PGDA",
            "access_method": "GDAL /vsicurl/ windowed remote read (no full download)",
        },
        "elevation_stats_native_window_m": {
            "min": float(dem_native.min()),
            "max": float(dem_native.max()),
            "mean": elev_mean,
            "std": float(dem_native.std()),
        },
        "elevationGridRelativeM": relative_grid.tolist(),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/{cid}_real_elevation_grid{tag}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"{cid}{tag}: native {dem_native.shape}, half_m={half_m}, grid={grid_size}x{grid_size}, "
          f"elev range {out['elevation_stats_native_window_m']['min']:.1f} to "
          f"{out['elevation_stats_native_window_m']['max']:.1f} m, saved {out_path}")


# Same 7-candidate shortlist as src/radar_pipeline.py / src/psr_boundary_export.py
CANDIDATES = [
    {"id": "SP_840980_0797630", "lat": -84.098, "lon": 79.764},
    {"id": "SP_832640_0090770", "lat": -83.264, "lon": 9.077},
    {"id": "SP_809570_2454450", "lat": -80.957, "lon": 245.445},
    {"id": "SP_819860_1568660", "lat": -81.986, "lon": 156.866},
    {"id": "SP_842420_0421060", "lat": -84.242, "lon": 42.106},
    {"id": "SP_817950_1586580", "lat": -81.795, "lon": 158.658},
    {"id": "SP_830080_0535120", "lat": -83.008, "lon": 53.512},
]

if __name__ == "__main__":
    for cand in CANDIDATES:
        # narrow: matches the 48x48 evidence grid window used elsewhere
        process_candidate(cand["id"], cand["lat"], cand["lon"], half_m=3300, grid_size=48, tag="")
        # wide: bigger-context real terrain for the frontend 3D view
        process_candidate(cand["id"], cand["lat"], cand["lon"], half_m=9000, grid_size=120, tag="_wide")
