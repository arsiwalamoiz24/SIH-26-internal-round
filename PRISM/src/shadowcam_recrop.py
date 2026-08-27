"""
Re-extract ShadowCam crops for the 6 non-primary candidates with a window
sized to each candidate's own real PSR polygon extent, instead of a fixed
1500m half-width that's smaller than several of these craters (up to 4145m
max radius) — the original crop showed a fragment of crater wall/floor with
the PSR mostly or entirely outside the frame, not the crater centered.

Reuses the cached COG URLs from the original search
(outputs/objective_optical/shortlist_shadowcam/summary.json) -- no need to
re-run the MDS search API. Recenters on each PSR polygon's own real vertex
centroid (frontend2/public/assets/prism/psr_boundary/*.json), not the
PSR_ID-encoded (rounded) coordinate, for tighter framing.
"""

import json
import os

import numpy as np
import rasterio
from PIL import Image
from pyproj import CRS, Transformer
from rasterio.env import Env
from rasterio.windows import from_bounds

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUMMARY = os.path.join(REPO, "PRISM", "outputs", "objective_optical", "shortlist_shadowcam", "summary.json")
BOUNDARY_DIR = os.path.join(REPO, "frontend2", "public", "assets", "prism", "psr_boundary")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective_optical", "shortlist_shadowcam_recrop")
os.makedirs(OUT_DIR, exist_ok=True)

MOON_LONLAT = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")

CANDIDATES = {
    "SP_832640_0090770": (-83.264, 9.077),
    "SP_830080_0535120": (-83.008, 53.512),
    "SP_842420_0421060": (-84.242, 42.106),
    "SP_817950_1586580": (-81.795, 158.658),
    "SP_819860_1568660": (-81.986, 156.866),
    "SP_809570_2454450": (-80.957, 245.445),
}

MOON_RADIUS = 1737400
SOUTH_STEREO = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"


def load_boundary_m(cid):
    """Real PSR polygon vertices, in meters, relative to the PSR_ID-encoded (lat,lon)."""
    with open(os.path.join(BOUNDARY_DIR, f"{cid}.json")) as f:
        d = json.load(f)
    return np.array(d["boundary_xy_m"])


def percentile_stretch_to_rgb(data, nodata=-1e30, lo_pct=1, hi_pct=99):
    valid = data[data > nodata]
    if valid.size == 0:
        return None
    lo, hi = np.percentile(valid, [lo_pct, hi_pct])
    stretched = np.clip((data - lo) / (hi - lo + 1e-12), 0, 1)
    stretched[data <= nodata] = 0
    img8 = (stretched * 255).astype(np.uint8)
    return np.stack([img8, img8, img8], axis=-1)


def main():
    with open(SUMMARY) as f:
        summary = json.load(f)

    stereo_tf = Transformer.from_crs(MOON_LONLAT, CRS.from_proj4(SOUTH_STEREO), always_xy=True)
    from_south_stereo = Transformer.from_crs(CRS.from_proj4(SOUTH_STEREO), MOON_LONLAT, always_xy=True)

    for cid, (lat, lon) in CANDIDATES.items():
        entry = summary.get(cid, {})
        extracted = entry.get("extracted", [])
        if not extracted:
            print(f"{cid}: no cached COG url, skipping")
            continue
        cog_url = extracted[0]["cog_url"]

        boundary_m = load_boundary_m(cid)
        base_cx, base_cy = stereo_tf.transform(lon, lat)
        # Real PSR polygon vertices, in absolute south-polar-stereographic meters.
        poly_x = boundary_m[:, 0] + base_cx
        poly_y = boundary_m[:, 1] + base_cy
        # Back to lon/lat per-vertex, so each can be reprojected into the COG's
        # own local CRS below -- this is the actual polygon footprint, not a
        # centered-square guess, so the crop matches the true PSR shape/extent
        # regardless of how far its centroid sits from the PSR_ID coordinate.
        poly_lon, poly_lat = from_south_stereo.transform(poly_x, poly_y)

        print(f"\n=== {cid} ===")

        vsi_url = "/vsicurl/" + cog_url
        with Env(GDAL_HTTP_TIMEOUT=60, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
            with rasterio.open(vsi_url) as ds:
                to_local = Transformer.from_crs(MOON_LONLAT, ds.crs, always_xy=True)
                lx, ly = to_local.transform(poly_lon, poly_lat)
                minx, maxx = float(np.min(lx)), float(np.max(lx))
                miny, maxy = float(np.min(ly)), float(np.max(ly))
                margin = 0.25 * max(maxx - minx, maxy - miny)  # 25% margin for surrounding context
                print(f"  polygon bbox (local CRS): {maxx-minx:.0f} x {maxy-miny:.0f} m, margin={margin:.0f}m")

                win = from_bounds(minx - margin, miny - margin, maxx + margin, maxy + margin, ds.transform)
                data = ds.read(1, window=win)

        if data.size == 0:
            print(f"{cid}: empty window, skipping")
            continue

        rgb = percentile_stretch_to_rgb(data)
        if rgb is None:
            print(f"{cid}: no valid pixels, skipping")
            continue

        out_path = os.path.join(OUT_DIR, f"{cid}_recrop_preview.png")
        Image.fromarray(rgb).save(out_path)
        pct_valid = round(100 * (data > -1e30).sum() / data.size, 1)
        print(f"{cid}: {data.shape} shape, {pct_valid}% valid -> {out_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
