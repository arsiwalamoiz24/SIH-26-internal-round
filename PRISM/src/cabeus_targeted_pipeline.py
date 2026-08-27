"""
Cabeus validation case -- localized Pv/CPR/SERD/T-Ratio at the exact LCROSS
impact point (Marshall et al. 2011 coordinate, and the Fassett et al. 2024
refined coordinate), using the same DFSAR Y4R/CPR mosaic and inside-vs-
surroundings methodology as the 7 screened candidates and Faustini's F2/F3
(faustini_subcrater_pipeline.py) -- so results are directly comparable to them.

Note (read alongside PRISM/docs/MINIRF_CABEUS_CPR_RECONCILIATION.md): a
SEPARATE real Mini-RF (S-band) analysis at this same coordinate found an
elevated CPR>1 pixel fraction there, but traced it to a documented fresh-
crater ejecta ray (a real, non-ice mechanism), not ice. This script uses a
DIFFERENT instrument (Chandrayaan-2 DFSAR, L-band) and PRISM's own Pv/CPR/
SERD/T-Ratio formulas -- the same ones used for every other candidate in
this project -- so it is a fair, independent, apples-to-apples comparison,
not a re-run of the Mini-RF result.
"""

import json
import os

from faustini_subcrater_pipeline import analyze
from pyproj import Transformer

MOON_RADIUS = 1737400

SITES = [
    {"id": "Cabeus_LCROSS_Marshall2011", "lat": -84.6796, "lon": -48.7093, "diameter_m": 2000},
    {"id": "Cabeus_LCROSS_Fassett2024", "lat": -84.6780, "lon": -48.6926, "diameter_m": 900},
]


def main():
    from radar_pipeline import OUT_DIR
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)

    results = []
    for site in SITES:
        print(f"\n=== {site['id']} ({site['lat']}, {site['lon']}, {site['diameter_m']}m) ===")
        r = analyze(site, transformer)
        results.append(r)
        print(json.dumps(r, indent=2))

    with open(os.path.join(OUT_DIR, "cabeus_targeted_pv_cpr.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
