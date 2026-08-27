"""
Faustini validation case, part 1 -- hazard map, terrain composite, and real
elevation grids for Faustini's own PSR (SP_871460_0840750), using the exact
same functions already validated for the 7 screened candidates. No new
algorithm code -- just calling the existing per-candidate functions with
Faustini's own lat/lon.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FAUSTINI_ID = "SP_871460_0840750"
FAUSTINI_LAT = -87.146
FAUSTINI_LON = 84.075


def main():
    import hazard_map_shortlist_pipeline as hazard_mod
    import terrain_shortlist_pipeline as terrain_mod
    import real_terrain_grid_pipeline as elev_mod
    import geopandas as gpd
    import rasterio
    from rasterio.env import Env

    print("=== Faustini hazard map ===")
    with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(hazard_mod.LDEM_URL) as src:
            crs = src.crs
    psr_gdf = gpd.read_file(hazard_mod.PSR_SHP).to_crs(crs)
    hazard_mod.run_for_candidate(FAUSTINI_ID, FAUSTINI_LAT, FAUSTINI_LON, psr_gdf)

    print("\n=== Faustini terrain composite ===")
    terrain_mod.run_for_candidate(FAUSTINI_ID, FAUSTINI_LAT, FAUSTINI_LON, psr_gdf)

    print("\n=== Faustini real elevation grids (narrow + wide) ===")
    elev_mod.process_candidate(FAUSTINI_ID, FAUSTINI_LAT, FAUSTINI_LON, half_m=3300, grid_size=48, tag="")
    elev_mod.process_candidate(FAUSTINI_ID, FAUSTINI_LAT, FAUSTINI_LON, half_m=9000, grid_size=120, tag="_wide")

    print("\nDone.")


if __name__ == "__main__":
    main()
