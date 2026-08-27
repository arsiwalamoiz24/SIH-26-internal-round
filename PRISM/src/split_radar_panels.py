"""
Individual single-panel crops (no title/colorbar) for Pv, CPR, and SERD --
currently only visible as 3 of the 4 panels inside radar_composite.png's
wide multi-panel strip (the 4th, Y4R RGB, already has its own crop as
radar_only.png). Same real local DFSAR Y4R/L3C mosaic files, same per-site
PSR-bbox+1000m window, same formulas as radar_pipeline.py -- no new network
read, no new computation, just individual crops of data already computed
there for all 9 sites (7 screened candidates + Faustini + Cabeus).
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from radar_pipeline import Y4R_PATHS, CPR_PATHS, PSR_SHP, FULL_RES_IDS, CANDIDATE_ID, read_full_res_window

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(REPO, "frontend2", "public", "assets", "prism", "panels")
os.makedirs(OUT_DIR, exist_ok=True)

ALL_IDS = FULL_RES_IDS if CANDIDATE_ID in FULL_RES_IDS else FULL_RES_IDS + [CANDIDATE_ID]


def save_panel(arr, cmap, out_path, vmin=None, vmax=None, contour_mask=None):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
    if contour_mask is not None:
        ax.contour(contour_mask, colors="cyan", linewidths=1.0)
    ax.axis("off")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def main():
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        full_crs = src.crs
    psr = gpd.read_file(PSR_SHP).to_crs(full_crs)

    for psr_id in ALL_IDS:
        row = psr[psr.PSR_ID == psr_id]
        if row.empty:
            print(f"{psr_id}: not found in PSR shapefile, skipping")
            continue
        row = row.iloc[0]
        minx, miny, maxx, maxy = row.geometry.bounds
        buffer = 1000
        bounds = (minx - buffer, miny - buffer, maxx + buffer, maxy + buffer)
        print(f"\n=== {psr_id} ===", flush=True)

        vol_fr, tr = read_full_res_window(Y4R_PATHS["vol"], bounds)
        evn_fr, _ = read_full_res_window(Y4R_PATHS["evn"], bounds)
        odd_fr, _ = read_full_res_window(Y4R_PATHS["odd"], bounds)
        hlx_fr, _ = read_full_res_window(Y4R_PATHS["hlx"], bounds)
        cpr_fr, _ = read_full_res_window(CPR_PATHS["cpr"], bounds)
        srd_fr, _ = read_full_res_window(CPR_PATHS["srd"], bounds)
        trt_fr, _ = read_full_res_window(CPR_PATHS["trt"], bounds)

        total_fr = evn_fr + vol_fr + odd_fr + hlx_fr
        valid_fr = np.isfinite(total_fr) & (total_fr > 0)
        pv_fr = vol_fr / np.where(valid_fr, total_fr, np.nan)
        valid_cpr = np.isfinite(cpr_fr) & (cpr_fr != 0)
        valid_srd = np.isfinite(srd_fr)
        valid_trt = np.isfinite(trt_fr) & (trt_fr != 0)

        psr_mask_fr = geometry_mask([row.geometry], out_shape=evn_fr.shape, transform=tr, invert=True)

        save_panel(np.where(valid_fr, pv_fr, np.nan), "viridis", f"{OUT_DIR}/{psr_id}_pv_only.png", 0, 1, psr_mask_fr)
        save_panel(np.where(valid_cpr, cpr_fr, np.nan), "inferno", f"{OUT_DIR}/{psr_id}_cpr_only.png", 0, 1, psr_mask_fr)
        save_panel(np.where(valid_srd, srd_fr, np.nan), "viridis", f"{OUT_DIR}/{psr_id}_serd_only.png", 0, 1, psr_mask_fr)
        save_panel(np.where(valid_trt, trt_fr, np.nan), "cividis", f"{OUT_DIR}/{psr_id}_tratio_only.png", 0, 1, psr_mask_fr)
        print(f"  saved pv/cpr/serd/tratio panels -> {OUT_DIR}/{psr_id}_*.png", flush=True)

    print("\nDone.")


if __name__ == "__main__":
    main()
