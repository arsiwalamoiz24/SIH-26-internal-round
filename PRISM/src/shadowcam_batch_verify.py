"""
Batch ShadowCam search + windowed-read crop extraction + real-vs-noise
verification for the 7-candidate shortlist. Reuses the same true-polygon
containment method (WKB footprint decode, not axis-aligned bbox) validated
this session, plus the adjacent-pixel-correlation sanity check that caught
the earlier NAC false-positive.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

import numpy as np
import rasterio
from pyproj import CRS, Transformer
from rasterio.windows import from_bounds
from shapely import wkb
from shapely.geometry import Point, Polygon

os.environ["GDAL_HTTP_MULTIRANGE"] = "YES"

MOON_LONLAT = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")
MOON_STEREO_SOUTH = CRS.from_proj4(
    "+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs"
)
_TF = Transformer.from_crs(MOON_LONLAT, MOON_STEREO_SOUTH, always_xy=True)


def lonlat_to_xy(lon, lat):
    return _TF.transform(lon, lat)


def mds_search(west, east, south, north):
    payload = {
        "datasets": ["luna_shadowcam_pds"],
        "query": {"common-geography-pgg_search": f"{west},{east},{south},{north}"},
        "map": {},
    }
    qs = "MDS_SEARCH=" + urllib.parse.quote(json.dumps(payload))
    url = f"https://data.im-ldi.com/mds/search?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def find_covering_frames(lat, lon, box_deg=2.0):
    d = mds_search(lon - box_deg, lon + box_deg, lat - 0.4, lat + 0.4)
    recs = d[0]["data"]
    cx, cy = lonlat_to_xy(lon, lat)
    hits = []
    for r in recs:
        geom = wkb.loads(bytes.fromhex(r["pgg_search"]))
        proj_coords = [lonlat_to_xy(px, py) for px, py in geom.exterior.coords]
        poly = Polygon(proj_coords)
        if not poly.contains(Point(cx, cy)):
            continue
        good = (
            r["status_corrupt"] == "f"
            and r["dqi_missing_data"] == "f"
            and r["dqi_uncalibratable"] == "f"
        )
        if good:
            hits.append(r)
    hits.sort(key=lambda r: float(r["incidence_angle"]))
    return hits


def get_cog_url(record_url):
    detail = f"https://data.im-ldi.com{record_url}"
    req = urllib.request.Request(detail, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    import re
    m = re.search(r'href="(https://pds\.shadowcam\.im-ldi\.com/[^"]*_map_raw\.tif)"', html)
    return m.group(1) if m else None


def extract_and_verify(cog_url, lat, lon, half_m, out_tif):
    vsi_url = "/vsicurl/" + cog_url
    with rasterio.open(vsi_url) as ds:
        src = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")
        tf = Transformer.from_crs(src, ds.crs, always_xy=True)
        cx, cy = tf.transform(lon, lat)
        win = from_bounds(cx - half_m, cy - half_m, cx + half_m, cy + half_m, ds.transform)
        data = ds.read(1, window=win)
        profile = {
            "driver": "GTiff", "height": data.shape[0], "width": data.shape[1],
            "count": 1, "dtype": data.dtype, "crs": ds.crs,
            "transform": rasterio.windows.transform(win, ds.transform),
        }
        os.makedirs(os.path.dirname(out_tif), exist_ok=True)
        with rasterio.open(out_tif, "w", **profile) as dst:
            dst.write(data, 1)

    masked = np.where(data > -1e30, data, np.nan)
    valid = masked[np.isfinite(masked)]
    a = masked[:, :-1].ravel()
    b = masked[:, 1:].ravel()
    m = np.isfinite(a) & np.isfinite(b)
    corr = float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 100 else float("nan")
    return {
        "n_valid": int(valid.size),
        "pct_valid": round(100 * valid.size / data.size, 2) if data.size else 0,
        "mean": float(np.nanmean(valid)) if valid.size else None,
        "std": float(np.nanstd(valid)) if valid.size else None,
        "adjacent_pixel_correlation": corr,
        "shape": list(data.shape),
    }


if __name__ == "__main__":
    candidates = {
        "SP_832640_0090770": (-83.264, 9.077),
        "SP_830080_0535120": (-83.008, 53.512),
        "SP_842420_0421060": (-84.242, 42.106),
        "SP_817950_1586580": (-81.795, 158.658),
        "SP_819860_1568660": (-81.986, 156.866),
        "SP_809570_2454450": (-80.957, 245.445),
    }
    results = {}
    for cid, (lat, lon) in candidates.items():
        print(f"\n=== {cid} ({lat},{lon}) ===", flush=True)
        try:
            hits = find_covering_frames(lat, lon)
        except Exception as e:
            print("  search failed:", e, flush=True)
            results[cid] = {"error": str(e)}
            continue
        print(f"  {len(hits)} true-polygon-verified frames", flush=True)
        if not hits:
            results[cid] = {"n_frames": 0}
            continue
        picked = hits[:2]
        frame_results = []
        for i, r in enumerate(picked):
            try:
                cog = get_cog_url(r["url"])
                if not cog:
                    print(f"  {r['identifier']}: no map_raw COG link found", flush=True)
                    continue
                out_tif = f"PRISM/outputs/objective_optical/shortlist_shadowcam/{cid}_{r['identifier']}.tif"
                stats = extract_and_verify(cog, lat, lon, 1500, out_tif)
                stats["identifier"] = r["identifier"]
                stats["incidence_angle"] = r["incidence_angle"]
                stats["resolution"] = r["resolution"]
                stats["cog_url"] = cog
                print(f"  {r['identifier']}: incidence={r['incidence_angle']} corr={stats['adjacent_pixel_correlation']:.3f}", flush=True)
                frame_results.append(stats)
            except Exception as e:
                print(f"  {r['identifier']}: FAILED {e}", flush=True)
        results[cid] = {"n_frames": len(hits), "extracted": frame_results}

    with open("PRISM/outputs/objective_optical/shortlist_shadowcam/summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDONE")
