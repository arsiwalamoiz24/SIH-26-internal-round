"""
One-off extraction: read the real per-pixel CPR/SERD/T-Ratio/Pv(evn,vol,odd,hlx)
arrays for the candidate window (SP_840980_0797630, -84.098, 79.764) directly
from the team's shared Google Drive-hosted Y4R/L3C GeoTIFFs, via GDAL /vsicurl/
windowed remote reads (no full 2.2GB-per-band download).

Same window definition as PRISM/src/candidate_physics_pipeline.py:
  half_window_m = 3300.0, centered on the candidate lon/lat, reprojected into
  the raster's own Moon_2000_South_Pole_Stereographic CRS.

Output: data/raw/candidate_window/candidate_window_arrays.npz (gitignored),
containing evn, vol, odd, hlx, cpr, srd, trt, pv (all float32, real values).
"""
import json
import os

import numpy as np
import pyproj
import rasterio
from rasterio.windows import from_bounds as window_from_bounds

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URLS = json.load(open(os.path.join(REPO, "data", "raw", "candidate_window_urls.json")))

CAND_LAT = -84.098
CAND_LON = 79.764
HALF_WINDOW_M = 3300.0

GEOG_MOON_WKT = (
    'GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",'
    'SPHEROID["Moon_2000_IAU_IAG",1737400,0]],'
    'PRIMEM["Reference_Meridian",0],UNIT["Degree",0.0174532925199433]]'
)


def read_window(band):
    vsi = "/vsicurl/" + URLS[band]
    with rasterio.open(vsi) as src:
        if band == "evn":
            target_crs = src.crs
            geog_moon = pyproj.CRS.from_wkt(GEOG_MOON_WKT)
            fwd = pyproj.Transformer.from_crs(geog_moon, target_crs, always_xy=True)
            cand_x, cand_y = fwd.transform(CAND_LON, CAND_LAT)
            bounds = (
                cand_x - HALF_WINDOW_M, cand_y - HALF_WINDOW_M,
                cand_x + HALF_WINDOW_M, cand_y + HALF_WINDOW_M,
            )
            read_window.bounds = bounds
            read_window.cand_xy = (cand_x, cand_y)
        window = window_from_bounds(*read_window.bounds, transform=src.transform)
        arr = src.read(1, window=window)
        nodata = src.nodata
    print(f"{band}: shape={arr.shape} min={np.nanmin(arr):.6g} max={np.nanmax(arr):.6g} nodata={nodata}")
    return arr.astype(np.float32)


def main():
    bands = {}
    for b in ["evn", "vol", "odd", "hlx", "cpr", "srd", "trt"]:
        bands[b] = read_window(b)

    total = bands["evn"] + bands["vol"] + bands["odd"] + bands["hlx"]
    valid_pv = np.isfinite(total) & (total > 0)
    pv = np.where(valid_pv, bands["vol"] / np.where(valid_pv, total, np.nan), np.nan).astype(np.float32)

    out_dir = os.path.join(REPO, "data", "raw", "candidate_window")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "candidate_window_arrays.npz")
    np.savez_compressed(
        out_path,
        evn=bands["evn"], vol=bands["vol"], odd=bands["odd"], hlx=bands["hlx"],
        cpr=bands["cpr"], srd=bands["srd"], trt=bands["trt"], pv=pv,
        candidate_xy_m=np.array(read_window.cand_xy),
        window_bounds_m=np.array(read_window.bounds),
        half_window_m=HALF_WINDOW_M,
    )
    print("\nSaved:", out_path)
    print("pv stats: mean", np.nanmean(pv), "median", np.nanmedian(pv))


if __name__ == "__main__":
    main()
