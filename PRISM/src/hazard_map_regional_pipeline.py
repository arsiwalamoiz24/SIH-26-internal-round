"""
PRISM Objective 2 -- Track G-v2 regional: overview-resolution hazard map across
the full south-polar extent (same footprint as Objective 1's own Y4R radar
screening and the LOLA PSR catalog), covering all 336 radar-covered PSRs, not
just the primary candidate.

Scope decision (see DECISIONS.md for the full reasoning): full native-resolution
(20 m/px) mapping of the entire 30400x30400 px LOLA grid was timed and would
take 2+ hours for the illumination ray-cast alone, plus require fetching most
of a multi-GB remote file -- not worth it, since most of that area is nowhere
near a PSR. Instead this mirrors Objective 1's own "screen wide at overview
resolution, go full-res only for the shortlist" pattern
(src/radar_pipeline.py's 1500x1500 overview of the Y4R mosaic).

A real (non-extrapolated) timing test of a decimated full-extent GDAL read
confirmed this is fast: reading the whole LDEM grid down to 1500x1500 took
27.7s over the network. Combined with the illumination ray-cast (~19s at this
resolution, timed separately), the whole regional run is a couple of minutes,
not hours.

Output: per-PSR mean hazard/illumination/slope/roughness for all 336 PSRs with
radar coverage (src/radar_pipeline.py's own candidate_table_overview.csv),
plus a regional composite figure.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
from rasterio.env import Env
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terrain_algorithms import compute_slope, compute_roughness_rms, compute_cumulative_illumination, compute_hazard_map, stats_block

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
CANDIDATE_TABLE = os.path.join(REPO, "PRISM", "outputs", "objective1", "candidate_table_overview.csv")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective2")
os.makedirs(OUT_DIR, exist_ok=True)

LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
OVERVIEW_SIZE = 1500  # matches Objective 1's own Y4R overview convention
NATIVE_PX_SIZE = 20.0
PRIMARY_CANDIDATE_ID = "SP_840980_0797630"


def main():
    t_start = time.time()

    with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(LDEM_URL) as src:
            full_bounds = src.bounds
            full_crs = src.crs
            full_w, full_h = src.width, src.height
            nodata = src.nodata
            print(f"Native grid: {full_w}x{full_h} @ {NATIVE_PX_SIZE}m/px, bounds {full_bounds}")
            t0 = time.time()
            elev = src.read(1, out_shape=(1, OVERVIEW_SIZE, OVERVIEW_SIZE), resampling=Resampling.average).astype(np.float64)
            print(f"Decimated read to {OVERVIEW_SIZE}x{OVERVIEW_SIZE}: {time.time()-t0:.1f}s")

    overview_px_size_m = (full_bounds.right - full_bounds.left) / OVERVIEW_SIZE
    print(f"Overview pixel size: {overview_px_size_m:.1f} m/px (native is {NATIVE_PX_SIZE} m/px, {overview_px_size_m/NATIVE_PX_SIZE:.0f}x decimation)")

    valid = np.isfinite(elev)
    if nodata is not None:
        valid &= (elev != nodata)
    elev_valid = np.where(valid, elev, np.nan)

    print("Computing regional slope...")
    slope = compute_slope(elev_valid, overview_px_size_m)
    print("Computing regional roughness...")
    roughness = compute_roughness_rms(elev_valid)
    print("Computing regional illumination (24 ray-cast passes at overview res)...")
    t0 = time.time()
    illum_frac = compute_cumulative_illumination(elev_valid, overview_px_size_m, n_azimuths=8, sun_elevations=[5, 10, 15])
    print(f"Illumination: {time.time()-t0:.1f}s")
    print("Computing regional hazard...")
    hazard = compute_hazard_map(slope, roughness, illum_frac)

    overview_transform = from_bounds(*full_bounds, OVERVIEW_SIZE, OVERVIEW_SIZE)

    # ---- Per-PSR summary for all 336 radar-covered PSRs ----
    candidates = pd.read_csv(CANDIDATE_TABLE)
    psr = gpd.read_file(PSR_SHP).to_crs(full_crs)

    per_psr = []
    for _, row in candidates.iterrows():
        psr_id = row["PSR_ID"]
        match = psr[psr.PSR_ID == psr_id]
        if match.empty:
            continue
        geom = match.iloc[0].geometry
        try:
            mask = geometry_mask([geom], out_shape=(OVERVIEW_SIZE, OVERVIEW_SIZE), transform=overview_transform, invert=True)
        except Exception:
            continue
        px_valid = mask & valid
        n = int(px_valid.sum())
        if n == 0:
            continue
        per_psr.append({
            "PSR_ID": psr_id, "lat": row["lat"], "lon": row["lon"], "area_km2": row["area_km2"],
            "n_overview_px": n,
            "mean_slope_deg": float(slope[px_valid].mean()),
            "mean_roughness_rms_m": float(roughness[px_valid].mean()),
            "mean_illumination_fraction": float(illum_frac[px_valid].mean()),
            "mean_hazard_score": float(hazard[px_valid].mean()),
        })

    per_psr_df = pd.DataFrame(per_psr).sort_values("mean_hazard_score")
    per_psr_df.to_csv(os.path.join(OUT_DIR, "regional_hazard_per_psr.csv"), index=False)
    print(f"\nComputed per-PSR hazard for {len(per_psr_df)} of {len(candidates)} PSRs (some may fall outside the overview grid's finite-data area)")

    primary = per_psr_df[per_psr_df.PSR_ID == PRIMARY_CANDIDATE_ID]
    primary_rank = int((per_psr_df.mean_hazard_score.values < primary.mean_hazard_score.values[0]).sum() + 1) if not primary.empty else None

    result = {
        "purpose": "Track G-v2 regional -- overview-resolution hazard map across the full south-polar PSR-catalog extent, all 336 radar-covered PSRs.",
        "scope_decision": "Overview resolution (1500x1500, matching Objective 1's own Y4R screening convention), not full native 20m/px -- see DECISIONS.md for the timed cost/value tradeoff (full-res regional would take 2+ hours).",
        "overview_size_px": OVERVIEW_SIZE,
        "overview_px_size_m": overview_px_size_m,
        "native_px_size_m": NATIVE_PX_SIZE,
        "decimation_factor": overview_px_size_m / NATIVE_PX_SIZE,
        "n_psrs_evaluated": int(len(per_psr_df)),
        "n_psrs_in_candidate_table": int(len(candidates)),
        "regional_slope_deg": stats_block(slope[valid], "Sobel slope, overview resolution, whole south-polar extent"),
        "regional_roughness_rms_m": stats_block(roughness[valid], "RMS roughness, overview resolution"),
        "regional_illumination_fraction": stats_block(illum_frac[valid], "24-position sun ray-cast illumination fraction, overview resolution"),
        "regional_hazard_score": stats_block(hazard[valid], "Combined hazard score, overview resolution"),
        "primary_candidate": {
            "PSR_ID": PRIMARY_CANDIDATE_ID,
            "regional_hazard_rank": f"{primary_rank} of {len(per_psr_df)} (1 = lowest/safest hazard)" if primary_rank else None,
            "note": "This overview-resolution rank is a coarse regional screen, not a replacement for the full-res per-candidate result in SP_840980_0797630_hazard_map_v2.json.",
        },
        "runtime_seconds": round(time.time() - t_start, 1),
        "per_psr_csv": "regional_hazard_per_psr.csv",
    }
    with open(os.path.join(OUT_DIR, "regional_hazard_overview.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    # ---- Composite figure ----
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    im0 = axes[0, 0].imshow(np.where(valid, slope, np.nan), cmap="RdYlGn_r", vmin=0, vmax=30)
    axes[0, 0].set_title(f"Regional Slope (deg), {OVERVIEW_SIZE}px overview"); plt.colorbar(im0, ax=axes[0, 0], shrink=0.7)
    im1 = axes[0, 1].imshow(np.where(valid, roughness, np.nan), cmap="inferno")
    axes[0, 1].set_title("Regional RMS Roughness (m)"); plt.colorbar(im1, ax=axes[0, 1], shrink=0.7)
    im2 = axes[1, 0].imshow(np.where(valid, illum_frac, np.nan), cmap="gray", vmin=0, vmax=1)
    axes[1, 0].set_title("Regional Illumination Fraction"); plt.colorbar(im2, ax=axes[1, 0], shrink=0.7)
    im3 = axes[1, 1].imshow(np.where(valid, hazard, np.nan), cmap="RdYlGn_r", vmin=0, vmax=1)
    axes[1, 1].set_title("Regional Combined Hazard Score"); plt.colorbar(im3, ax=axes[1, 1], shrink=0.7)
    for ax in axes.flat:
        ax.set_xlabel("px"); ax.set_ylabel("px")
    plt.suptitle(f"South Pole Regional Terrain Hazard -- {OVERVIEW_SIZE}x{OVERVIEW_SIZE} overview ({overview_px_size_m:.0f} m/px), {len(per_psr_df)} PSRs evaluated")
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "regional_hazard_overview.png"), dpi=150)
    plt.close(fig)

    print("\nTotal runtime:", round(time.time() - t_start, 1), "s")
    print("Done. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
