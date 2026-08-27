"""
Faustini and Cabeus (the two featured external-validation sites, not part of
PRISM's own 7-candidate screening) are both much larger real PSRs than any of
the 7 screened candidates -- real PSR polygon max radius is ~15.8km for both,
vs ~2.1-4.5km for the 7 candidates. But their hazard/terrain composites, the
single-panel crops used as 3D mesh textures, and the wide real elevation grid
used for the 3D mesh's height everywhere (not just the bowl) were all
generated reusing the same fixed window size tuned for the much smaller
7-candidate set (BUFFER_M=5000 for hazard/terrain, window_half_m=9000 for the
wide elevation grid). Real data, but real data covering less than half of
each site's actual extent -- everything beyond that radius fell back to a
synthetic placeholder in the 3D view.

This regenerates real data for both sites at a window sized to their own true
extent (~1.3x real PSR max radius), using the exact same functions already
validated for the 7 screened candidates -- no new algorithm, just a bigger
window for these two.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FAUSTINI_ID = "SP_871460_0840750"
FAUSTINI_LAT = -87.146
FAUSTINI_LON = 84.075
FAUSTINI_HALF_M = 20500  # real PSR max radius 15761m * 1.3

CABEUS_ID = "SP_844580_3134320"
CABEUS_LAT = -84.45787607588048  # true polygon centroid, not the LCROSS point
CABEUS_LON = -46.5676458422382
CABEUS_HALF_M = 20700  # real PSR max radius 15882m * 1.3


def main():
    import geopandas as gpd
    import rasterio
    from rasterio.env import Env

    import hazard_map_shortlist_pipeline as hazard_mod
    import terrain_shortlist_pipeline as terrain_mod
    import real_terrain_grid_pipeline as elev_mod

    with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(hazard_mod.LDEM_URL) as src:
            crs = src.crs
    psr_gdf = gpd.read_file(hazard_mod.PSR_SHP).to_crs(crs)

    for site_id, lat, lon, half_m in [
        (FAUSTINI_ID, FAUSTINI_LAT, FAUSTINI_LON, FAUSTINI_HALF_M),
        (CABEUS_ID, CABEUS_LAT, CABEUS_LON, CABEUS_HALF_M),
    ]:
        print(f"\n{'='*60}\n{site_id}  half_m={half_m}\n{'='*60}")

        hazard_mod.BUFFER_M = half_m
        print(f"\n=== {site_id} hazard map (full extent) ===")
        hazard_mod.run_for_candidate(site_id, lat, lon, psr_gdf)

        terrain_mod.BUFFER_M = half_m
        print(f"\n=== {site_id} terrain composite (full extent) ===")
        terrain_mod.run_for_candidate(site_id, lat, lon, psr_gdf)

        print(f"\n=== {site_id} real wide elevation grid (full extent) ===")
        elev_mod.process_candidate(site_id, lat, lon, half_m=half_m, grid_size=120, tag="_wide")

    print("\nDone.")


if __name__ == "__main__":
    main()
