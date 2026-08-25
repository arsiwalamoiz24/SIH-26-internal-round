"""
PRISM -- DOP pipeline v2, real Level-2 SRI power-ratio DOP test.

Follow-up to a direct question: "why aren't we using the Level-2 SRI
product?" The official ch2_dfsar_user_manual_v1.0.pdf (Table 1.2.4/3.1,
downloaded and read this session) confirms SRI is `unsigned short int`,
amplitude-only, no phase, one band per polarization -- it structurally
cannot carry the Re/Im(HH*VV*) cross term needed for the standard S3/S4
Stokes terms. So the only DOP formula the data supports is the power-only
ratio:

    DOP_SRI = |S2|/S1 = ||HH|^2 - |VV|^2| / (|HH|^2 + |VV|^2)

This was already estimated via a proxy computed from the raw Level-1A SLC
amplitude data (dop_pipeline_v2_ainsworth_crosstalk.py's F2/F3 windows,
reported in the plan file: F2=0.0032, F3=0.0331). This script instead reads
the REAL ISRO-calibrated Level-2 SRI product (already present in the
already-downloaded acquisition zip -- no new download needed) to check
whether ISRO's own Level-2 processing (radiometric calibration,
azimuth_looks=20 multilooking, incidence-angle/map-projection geocoding --
all confirmed via the SRI XML label, isda:Product_Parameters) shifts the
HH/VV power ratio meaningfully relative to the naive SLC-derived proxy.

The SRI GeoTIFFs turn out to be properly georeferenced, axis-aligned
Polar-Stereographic-Moon rasters (confirmed via rasterio: real CRS + affine
transform), unlike the rotated slant-range SLI grid -- so crater locations
are found by a direct pyproj forward-transform of lat/lon into this CRS,
then rasterio's own inverse transform to pixel row/col. No bilinear corner
inversion needed here (that was only necessary for the rotated SLI grid
used in the other v2/v1 scripts).

0 DN is confirmed no-data (89% of the raster, consistent with a rotated SAR
swath padded into an axis-aligned bounding raster) and is masked out.
"""

import json
import os

import numpy as np
import pyproj
import rasterio
from rasterio.windows import Window

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "dop_v2")
os.makedirs(OUT_DIR, exist_ok=True)

ZIP_PATH = r"C:\Users\radhe\Downloads\ch2_sar_ncxl_20200321t082617351_d_fp_d18.zip"
INTERNAL_DIR = "data/calibrated/20200321"
BASE = "ch2_sar_ncxl_20200321t082617351_d_sri_xx_fp"
STATION = "d18"

GEOG_MOON_WKT = (
    'GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",'
    'SPHEROID["Moon_2000_IAU_IAG",1737400,0]],'
    'PRIMEM["Reference_Meridian",0],UNIT["Degree",0.0174532925199433]]'
)

CRATERS = [
    {"id": "F2", "lat": -87.39, "lon": 82.31, "diameter_m": 1100, "context_half_m": 2000,
     "sli_proxy_dop": 0.0032},
    {"id": "F3", "lat": -87.31, "lon": 86.333, "diameter_m": 700, "context_half_m": 1300,
     "sli_proxy_dop": 0.0331},
]
PAPER_RANGE = [0.10, 0.13]


def vsizip_path(pol):
    return f"/vsizip/{ZIP_PATH}/{INTERNAL_DIR}/{BASE}_{pol}_{STATION}.tif"


def read_window_at_latlon(pol, lat, lon, half_m, geog_crs):
    path = vsizip_path(pol)
    with rasterio.open(path) as src:
        fwd = pyproj.Transformer.from_crs(geog_crs, src.crs, always_xy=True)
        x, y = fwd.transform(lon, lat)
        col_c, row_c = ~src.transform * (x, y)
        half_px = int(half_m / abs(src.transform.a))
        col0 = int(col_c) - half_px
        row0 = int(row_c) - half_px
        size = 2 * half_px
        window = Window(col0, row0, size, size)
        arr = src.read(1, window=window, boundless=True, fill_value=0).astype(np.float64)
        win_transform = src.window_transform(window)
    return arr, win_transform, (x, y), (col_c - col0, row_c - row0)


def main():
    geog_crs = pyproj.CRS.from_wkt(GEOG_MOON_WKT)
    results = {}

    for crater in CRATERS:
        cid = crater["id"]
        print(f"\n=== {cid} ===")
        HH, win_tr, xy, local_center = read_window_at_latlon(
            "hh", crater["lat"], crater["lon"], crater["context_half_m"], geog_crs)
        VV, _, _, _ = read_window_at_latlon(
            "vv", crater["lat"], crater["lon"], crater["context_half_m"], geog_crs)

        px_size = abs(win_tr.a)
        h, w = HH.shape
        rows, cols = np.indices((h, w))
        local_col, local_row = local_center
        dist_m = np.hypot((cols - local_col) * px_size, (rows - local_row) * px_size)
        radius_m = crater["diameter_m"] / 2.0
        interior_mask = dist_m <= radius_m

        valid = (HH > 0) & (VV > 0)  # 0 DN = no-data
        inside_valid = interior_mask & valid
        n_valid = int(inside_valid.sum())
        n_total = int(interior_mask.sum())

        if n_valid == 0:
            print(f"  WARNING: no valid (nonzero) SRI pixels inside {cid} interior "
                  f"({n_total} total interior px, mapped center px=({local_col:.1f},{local_row:.1f})). "
                  f"Acquisition/footprint may not actually cover this crater at SRI resolution, "
                  f"or crater is smaller than the SRI 25m pixel spacing allows to resolve reliably.")
            results[cid] = {
                "crater_id": cid, "n_interior_px": n_total, "n_valid_interior_px": 0,
                "error": "no valid SRI pixels in interior mask",
                "mapped_xy": list(xy), "local_center_px": list(local_center),
            }
            continue

        hh_i = HH[inside_valid]
        vv_i = VV[inside_valid]
        PHH = np.mean(hh_i ** 2)
        PVV = np.mean(vv_i ** 2)
        S1 = PHH + PVV
        S2 = PHH - PVV
        dop_sri = abs(S2) / S1

        result = {
            "crater_id": cid,
            "pixel_spacing_m": px_size,
            "n_interior_px": n_total,
            "n_valid_interior_px": n_valid,
            "mapped_xy_m": list(xy),
            "local_center_px_in_window": list(local_center),
            "mean_HH_DN": float(hh_i.mean()), "mean_VV_DN": float(vv_i.mean()),
            "power_HH": float(PHH), "power_VV": float(PVV),
            "dop_sri_power_only": float(dop_sri),
            "sli_proxy_dop_power_only": crater["sli_proxy_dop"],
            "paper_range": PAPER_RANGE,
            "meets_paper_range": bool(PAPER_RANGE[0] <= dop_sri <= PAPER_RANGE[1]),
        }
        results[cid] = result
        print(f"  n_valid_interior={n_valid}/{n_total}  mean_HH_DN={hh_i.mean():.1f}  mean_VV_DN={vv_i.mean():.1f}")
        print(f"  DOP_SRI (real Level-2 product) = {dop_sri:.4f}   "
              f"(SLC-derived proxy was {crater['sli_proxy_dop']:.4f})   paper range: {PAPER_RANGE}")

    with open(os.path.join(OUT_DIR, "F2_F3_sri_powerdop.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n=== SUMMARY ===")
    for cid, r in results.items():
        if "error" in r:
            print(f"{cid}: ERROR -- {r['error']}")
        else:
            print(f"{cid}: DOP_SRI={r['dop_sri_power_only']:.4f}  "
                  f"(proxy was {r['sli_proxy_dop_power_only']:.4f})  "
                  f"meets_range={r['meets_paper_range']}")
    print("\nDone. Output in", OUT_DIR)


if __name__ == "__main__":
    main()
