"""
Individual single-panel crops (no title/axis/colorbar) for every real metric
that currently only exists inside a multi-panel matplotlib composite --
slope, RMS roughness, illumination fraction (hazard composite) and TRI
(terrain composite) -- for all 9 sites (7 screened candidates + Faustini +
Cabeus). Hazard's combined score and elevation already have "_only" crops
(hazard_map_pipeline.py / real_terrain_grid_pipeline.py); this fills in the
remaining panels so the frontend can lay out real per-metric plots in a grid
instead of stretching one wide multi-panel strip.

Reuses the exact same functions/buffers already validated per site (no new
algorithm, no new window sizes): 5000m for the 7 candidates (same as
hazard_map_pipeline.py / hazard_map_shortlist_pipeline.py), 20500m/20700m for
Faustini/Cabeus (see regenerate_featured_sites_full_extent.py). One LDEM
window read per site serves both the hazard-side and terrain-side panels.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
from rasterio.env import Env
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terrain_algorithms import compute_slope, compute_roughness_rms, compute_cumulative_illumination

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
OUT_DIR = os.path.join(REPO, "frontend2", "public", "assets", "prism", "panels")
os.makedirs(OUT_DIR, exist_ok=True)

LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
NATIVE_PX_SIZE = 20.0
MOON_RADIUS = 1737400

# (lat, lon, buffer_m) -- same real coordinates/buffers already established
# and used elsewhere in this repo for each site.
SITES = {
    "SP_840980_0797630": (-84.098, 79.764, 5000),
    "SP_832640_0090770": (-83.264, 9.077, 5000),
    "SP_830080_0535120": (-83.008, 53.512, 5000),
    "SP_842420_0421060": (-84.242, 42.106, 5000),
    "SP_817950_1586580": (-81.795, 158.658, 5000),
    "SP_819860_1568660": (-81.986, 156.866, 5000),
    "SP_809570_2454450": (-80.957, 245.445, 5000),
    "SP_871460_0840750": (-87.146, 84.075, 20500),
    "SP_844580_3134320": (-84.45787607588048, -46.5676458422382, 20700),
}


def tri_riley(elev):
    padded = np.pad(elev, 1, mode="constant", constant_values=np.nan)
    h, w = elev.shape
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    diffs = np.full((8, h, w), np.nan, dtype=np.float64)
    for k, (dy, dx) in enumerate(offsets):
        neighbor = padded[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
        diffs[k] = np.abs(neighbor - elev)
    with np.errstate(invalid="ignore"):
        tri = np.nanmean(diffs, axis=0)
    tri[~np.isfinite(elev)] = np.nan
    return tri


def save_panel(arr, cmap, out_path, vmin=None, vmax=None, contour_mask=None):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
    if contour_mask is not None:
        ax.contour(contour_mask, colors="cyan", linewidths=1.0)
    ax.axis("off")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def main():
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)

    with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(LDEM_URL) as src:
            crs = src.crs
    psr_gdf = gpd.read_file(PSR_SHP).to_crs(crs)

    for psr_id, (lat, lon, buffer_m) in SITES.items():
        print(f"\n=== {psr_id} ({lat},{lon}) buffer={buffer_m} ===", flush=True)
        cx, cy = transformer.transform(lon, lat)

        with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
            with rasterio.open(LDEM_URL) as src:
                bounds = (cx - buffer_m, cy - buffer_m, cx + buffer_m, cy + buffer_m)
                window = window_from_bounds(*bounds, transform=src.transform)
                elev = src.read(1, window=window).astype(np.float64)
                tr = src.window_transform(window)
                nodata = src.nodata

        valid = np.isfinite(elev)
        if nodata is not None:
            valid &= (elev != nodata)
        elev_valid = np.where(valid, elev, np.nan)

        slope = compute_slope(elev_valid, NATIVE_PX_SIZE)
        roughness = compute_roughness_rms(elev_valid)
        illum = compute_cumulative_illumination(elev_valid, NATIVE_PX_SIZE, n_azimuths=8, sun_elevations=[5, 10, 15])
        tri = tri_riley(elev_valid)

        psr_mask = None
        cand_row = psr_gdf[psr_gdf.PSR_ID == psr_id]
        if not cand_row.empty:
            geom = cand_row.iloc[0].geometry
            psr_mask = geometry_mask([geom], out_shape=elev.shape, transform=tr, invert=True)

        save_panel(np.where(valid, slope, np.nan), "RdYlGn_r", f"{OUT_DIR}/{psr_id}_slope_only.png", 0, 30, psr_mask)
        save_panel(np.where(valid, roughness, np.nan), "inferno", f"{OUT_DIR}/{psr_id}_roughness_only.png", contour_mask=psr_mask)
        save_panel(np.where(valid, illum, np.nan), "gray", f"{OUT_DIR}/{psr_id}_illum_only.png", 0, 1, psr_mask)
        save_panel(tri, "magma", f"{OUT_DIR}/{psr_id}_tri_only.png", contour_mask=psr_mask)
        print(f"  saved slope/roughness/illum/tri panels -> {OUT_DIR}/{psr_id}_*.png", flush=True)

    print("\nDone.")


if __name__ == "__main__":
    main()
