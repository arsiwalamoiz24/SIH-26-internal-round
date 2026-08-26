"""
Export real, non-circular PSR rim boundary polygons for the 3D frontend.

The terrain page's 3D crater mesh (frontend2/src/app/terrain/page.tsx) currently
derives its crater rim as a perfect circle (pure function of radial distance
from center). Real, irregular PSR boundary polygons already exist locally in
data/raw/psr_south/LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp (653 polygons,
no network required) -- this script extracts the polygon for each of the 7
shortlisted candidates, reprojects it to the same south-polar-stereographic
CRS used elsewhere in this project, recenters it on the candidate's own
lat/lon-derived center, and writes one compact JSON per candidate for the
frontend to fetch directly.
"""

import json
import os

import geopandas as gpd
from pyproj import Transformer

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
OUT_DIR = os.path.join(REPO, "frontend2", "public", "assets", "prism", "psr_boundary")
os.makedirs(OUT_DIR, exist_ok=True)

MOON_RADIUS = 1737400

# Same 7-candidate shortlist as src/radar_pipeline.py / src/hazard_map_shortlist_pipeline.py
CANDIDATES = [
    {"id": "SP_840980_0797630", "lat": -84.098, "lon": 79.764},
    {"id": "SP_832640_0090770", "lat": -83.264, "lon": 9.077},
    {"id": "SP_809570_2454450", "lat": -80.957, "lon": 245.445},
    {"id": "SP_819860_1568660", "lat": -81.986, "lon": 156.866},
    {"id": "SP_842420_0421060", "lat": -84.242, "lon": 42.106},
    {"id": "SP_817950_1586580", "lat": -81.795, "lon": 158.658},
    {"id": "SP_830080_0535120", "lat": -83.008, "lon": 53.512},
]


def main():
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)

    psr = gpd.read_file(PSR_SHP)
    print(f"Loaded {len(psr)} PSR polygons, source CRS={psr.crs}")
    psr_proj = psr.to_crs(dst_proj)

    written = 0
    for cand in CANDIDATES:
        row = psr_proj[psr_proj.PSR_ID == cand["id"]]
        if row.empty:
            print(f"WARNING: {cand['id']} not found in PSR shapefile -- skipping")
            continue
        r = row.iloc[0]
        geom = r.geometry
        # Some PSR polygons are MultiPolygons -- use the largest ring.
        if geom.geom_type == "MultiPolygon":
            geom = max(geom.geoms, key=lambda g: g.area)

        cx, cy = transformer.transform(cand["lon"], cand["lat"])
        exterior = list(geom.exterior.coords)
        boundary_xy_m = [[round(x - cx, 2), round(y - cy, 2)] for x, y in exterior]

        out = {
            "candidate_id": cand["id"],
            "candidate_lat": cand["lat"],
            "candidate_lon": cand["lon"],
            "area_km2": float(r.area) if "area" in row.columns else None,
            "perimeter_km": float(r.perimeter) if "perimeter" in row.columns else None,
            "n_vertices": len(boundary_xy_m),
            "boundary_xy_m": boundary_xy_m,
        }
        out_path = os.path.join(OUT_DIR, f"{cand['id']}.json")
        with open(out_path, "w") as f:
            json.dump(out, f)
        print(f"{cand['id']}: {len(boundary_xy_m)} vertices, area={out['area_km2']} km^2 -> {out_path}")
        written += 1

    print(f"\nDone. Wrote {written}/{len(CANDIDATES)} boundary files to {OUT_DIR}")


if __name__ == "__main__":
    main()
