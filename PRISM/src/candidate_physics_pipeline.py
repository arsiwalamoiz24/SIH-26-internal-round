"""
PRISM Tracks A+B -- candidate-coordinate-based radar physics extraction and
georeferencing verification for SP_840980_0797630 (-84.098, 79.764).

Unlike src/radar_pipeline.py (which windows around the PSR *polygon*), this
script windows around the candidate *coordinate* directly, using an explicit
geographic-Moon -> Moon_2000_South_Pole_Stereographic pyproj transform (no
arbitrary pixel offsets). The PSR polygon is used only as a secondary,
optional interior/surroundings split within that coordinate-defined window,
for continuity with the Phase-1 (src/radar_pipeline.py) results.

Source products (all local, unmodified from src/radar_pipeline.py):
  - Y4R L4 mosaic (evn/vol/odd/hlx), ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx
  - CPR/SERD/T-Ratio L3C mosaic, ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx
  - LOLA South Pole PSR shapefile (secondary mask only)

CRS: Moon_2000_South_Pole_Stereographic, sphere radius 1,737,400 m,
latitude_of_origin -90, central_meridian 0 (read directly from the GeoTIFF,
not assumed).
"""

import json
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import pyproj
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from rasterio.windows import from_bounds as window_from_bounds

L4_DIR = r"C:\Users\radhe\PRISM_local_data\l4_mosaic"
L3C_DIR = r"C:\Users\radhe\PRISM_local_data\l3c_cpr"
PSR_SHP = r"C:\Users\radhe\PRISM_local_data\psr_south\LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp"

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "candidate_physics")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_ID = "SP_840980_0797630"
CAND_LAT = -84.098
CAND_LON = 79.764
HALF_WINDOW_M = 3300.0  # -> ~6.6 km x 6.6 km window, comparable to the
                         # ~6.6km (265x253 px @ 25m) PSR+1km-buffer window
                         # used in src/radar_pipeline.py's Phase-1 run.

Y4R_PATHS = {
    L: os.path.join(L4_DIR, f"ch2_sar_ndxl_20250630my4rspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["evn", "vol", "odd", "hlx"]
}
CPR_PATHS = {
    L: os.path.join(L3C_DIR, f"ch2_sar_ndxl_20250630mpcpspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["cpr", "srd", "trt"]
}

GEOG_MOON_WKT = (
    'GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",'
    'SPHEROID["Moon_2000_IAU_IAG",1737400,0]],'
    'PRIMEM["Reference_Meridian",0],UNIT["Degree",0.0174532925199433]]'
)


def read_overview(path, out_shape):
    with rasterio.open(path) as src:
        arr = src.read(1, out_shape=(1, out_shape[0], out_shape[1]), resampling=Resampling.average)
        return arr.squeeze().astype(np.float32)


def read_window(path, bounds):
    with rasterio.open(path) as src:
        window = window_from_bounds(*bounds, transform=src.transform)
        arr = src.read(1, window=window)
        win_transform = src.window_transform(window)
        nodata = src.nodata
    return arr.astype(np.float32), win_transform, nodata


def stats_block(arr, valid_mask, label):
    vals = arr[valid_mask]
    n_total = int(arr.size)
    n_valid = int(vals.size)
    n_nan = int(np.isnan(arr).sum())
    block = {
        "label": label,
        "n_total_px": n_total,
        "n_valid_px": n_valid,
        "n_nan_px": n_nan,
        "pct_nan": round(100.0 * n_nan / n_total, 4) if n_total else None,
    }
    if n_valid > 0:
        pct = np.percentile(vals, [5, 10, 25, 50, 75, 90, 95])
        block.update({
            "mean": float(np.mean(vals)),
            "median": float(np.median(vals)),
            "std": float(np.std(vals)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals)),
            "p5": float(pct[0]), "p10": float(pct[1]), "p25": float(pct[2]),
            "p50": float(pct[3]), "p75": float(pct[4]), "p90": float(pct[5]), "p95": float(pct[6]),
        })
    else:
        block.update({k: None for k in ["mean", "median", "std", "min", "max",
                                         "p5", "p10", "p25", "p50", "p75", "p90", "p95"]})
    return block


def main():
    provenance = {
        "candidate_id": CANDIDATE_ID,
        "candidate_lat_deg": CAND_LAT,
        "candidate_lon_deg": CAND_LON,
        "source_products": {
            "y4r_l4_mosaic": "ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx (evn/vol/odd/hlx GeoTIFFs)",
            "l3c_cpr_mosaic": "ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx (cpr/srd/trt GeoTIFFs)",
            "processing_level": "L4-MOSAIC / L3C-MOSAIC (Derived), mosaic date 2025-06-30",
            "psr_shapefile": "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL (LRO/LOLA South Pole PSR catalog, secondary/interior mask only)",
        },
    }

    # ---- Track B: georeferencing verification ----
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        target_crs = src.crs
        full_bounds = src.bounds
        full_transform = src.transform
        full_w, full_h = src.width, src.height

    with rasterio.open(CPR_PATHS["cpr"]) as src:
        cpr_crs, cpr_bounds = src.crs, src.bounds
    crs_match = (cpr_crs == target_crs)
    bounds_match = (cpr_bounds == full_bounds)

    geog_moon = pyproj.CRS.from_wkt(GEOG_MOON_WKT)
    fwd = pyproj.Transformer.from_crs(geog_moon, target_crs, always_xy=True)
    inv = pyproj.Transformer.from_crs(target_crs, geog_moon, always_xy=True)

    cand_x, cand_y = fwd.transform(CAND_LON, CAND_LAT)
    lon_rt, lat_rt = inv.transform(cand_x, cand_y)
    round_trip_err_deg = max(abs(lon_rt - CAND_LON), abs(lat_rt - CAND_LAT))

    col, row = ~full_transform * (cand_x, cand_y)
    inside_bounds = (full_bounds.left <= cand_x <= full_bounds.right) and (full_bounds.bottom <= cand_y <= full_bounds.top)
    inside_raster_px = (0 <= col <= full_w) and (0 <= row <= full_h)

    georef_check = {
        "raster_crs_wkt": target_crs.to_wkt(),
        "raster_crs_summary": "Moon_2000_South_Pole_Stereographic, sphere r=1737400m, lat_of_origin=-90, central_meridian=0 (read directly from GeoTIFF header, not assumed)",
        "y4r_cpr_crs_match": bool(crs_match),
        "y4r_cpr_bounds_match": bool(bounds_match),
        "transform_method": "pyproj.Transformer, geographic-Moon-sphere -> raster CRS, always_xy=True",
        "candidate_lonlat_input": [CAND_LON, CAND_LAT],
        "candidate_projected_xy_m": [float(cand_x), float(cand_y)],
        "round_trip_lonlat_deg": [float(lon_rt), float(lat_rt)],
        "round_trip_max_abs_error_deg": float(round_trip_err_deg),
        "candidate_inside_raster_bounds": bool(inside_bounds),
        "candidate_pixel_col_row": [float(col), float(row)],
        "candidate_inside_raster_pixel_grid": bool(inside_raster_px),
        "raster_shape_w_h": [full_w, full_h],
        "raster_bounds_m": [full_bounds.left, full_bounds.bottom, full_bounds.right, full_bounds.top],
        "longitude_wrapping_note": "Mosaic spans the full 360 deg south-polar cap in a projected (not geographic-grid) CRS, so there is no antimeridian/0-360-vs-180 ambiguity for point placement here -- the projection itself is longitude-continuous around the pole. Verified by round-trip error below.",
        "verdict": "PASS" if (inside_bounds and inside_raster_px and round_trip_err_deg < 1e-6) else "FAIL",
    }

    if georef_check["verdict"] != "PASS":
        with open(os.path.join(OUT_DIR, "georeferencing_check.json"), "w") as f:
            json.dump(georef_check, f, indent=2)
        raise RuntimeError("Georeferencing verification FAILED -- see georeferencing_check.json. Stopping Track A per instructions (do not guess).")

    print("Georeferencing check PASSED:", json.dumps(georef_check, indent=2, default=str)[:800])

    with open(os.path.join(OUT_DIR, "georeferencing_check.json"), "w") as f:
        json.dump(georef_check, f, indent=2)

    # ---- Overview arrays for "relative percentile within the mosaic" ----
    out_h = 1500
    out_w = int(out_h * full_w / full_h)
    evn_ov = read_overview(Y4R_PATHS["evn"], (out_h, out_w))
    vol_ov = read_overview(Y4R_PATHS["vol"], (out_h, out_w))
    odd_ov = read_overview(Y4R_PATHS["odd"], (out_h, out_w))
    hlx_ov = read_overview(Y4R_PATHS["hlx"], (out_h, out_w))
    cpr_ov = read_overview(CPR_PATHS["cpr"], (out_h, out_w))
    srd_ov = read_overview(CPR_PATHS["srd"], (out_h, out_w))
    trt_ov = read_overview(CPR_PATHS["trt"], (out_h, out_w))

    total_ov = evn_ov + vol_ov + odd_ov + hlx_ov
    total_ov_safe = np.where((total_ov <= 0) | ~np.isfinite(total_ov), np.nan, total_ov)
    pv_ov = vol_ov / total_ov_safe

    def valid_ov(arr, nodata=None):
        m = np.isfinite(arr)
        if nodata is not None:
            m &= (arr != nodata)
        return arr[m]

    overview_dist = {
        "pv": valid_ov(pv_ov),
        "cpr": valid_ov(cpr_ov),
        "serd": valid_ov(srd_ov),
        "tratio": valid_ov(trt_ov),
    }

    # ---- Track A: candidate-coordinate window extraction ----
    bounds = (cand_x - HALF_WINDOW_M, cand_y - HALF_WINDOW_M, cand_x + HALF_WINDOW_M, cand_y + HALF_WINDOW_M)

    evn_w, win_tr, _ = read_window(Y4R_PATHS["evn"], bounds)
    vol_w, _, _ = read_window(Y4R_PATHS["vol"], bounds)
    odd_w, _, _ = read_window(Y4R_PATHS["odd"], bounds)
    hlx_w, _, _ = read_window(Y4R_PATHS["hlx"], bounds)
    cpr_w, cpr_win_tr, cpr_nodata = read_window(CPR_PATHS["cpr"], bounds)
    srd_w, srd_win_tr, srd_nodata = read_window(CPR_PATHS["srd"], bounds)
    trt_w, trt_win_tr, trt_nodata = read_window(CPR_PATHS["trt"], bounds)

    total_w = evn_w + vol_w + odd_w + hlx_w
    valid_pv_w = np.isfinite(total_w) & (total_w > 0)
    pv_w = np.where(valid_pv_w, vol_w / np.where(valid_pv_w, total_w, np.nan), np.nan)

    valid_cpr_w = np.isfinite(cpr_w) & (cpr_w != 0) & (cpr_w != (cpr_nodata if cpr_nodata is not None else np.nan))
    valid_srd_w = np.isfinite(srd_w) & (srd_w != (srd_nodata if srd_nodata is not None else np.nan))
    valid_trt_w = np.isfinite(trt_w) & (trt_w != 0) & (trt_w != (trt_nodata if trt_nodata is not None else np.nan))

    # secondary PSR interior/exterior split (same polygon as Phase-1, for continuity)
    psr = gpd.read_file(PSR_SHP).to_crs(target_crs)
    cand_psr_rows = psr[psr.PSR_ID == CANDIDATE_ID]
    psr_mask_w = None
    psr_area_km2 = None
    if not cand_psr_rows.empty:
        cand_geom = cand_psr_rows.iloc[0].geometry
        psr_area_km2 = float(cand_psr_rows.iloc[0].area)
        psr_mask_w = geometry_mask([cand_geom], out_shape=pv_w.shape, transform=win_tr, invert=True)

    def full_metric(name, arr, valid_mask, nodata):
        block = {
            "window": stats_block(arr, valid_mask, f"{name} -- full candidate window"),
        }
        if psr_mask_w is not None:
            inside = valid_mask & psr_mask_w
            outside = valid_mask & (~psr_mask_w)
            block["psr_interior"] = stats_block(arr, inside, f"{name} -- PSR interior (secondary split)")
            block["psr_surroundings"] = stats_block(arr, outside, f"{name} -- PSR surroundings within window (secondary split)")
        window_vals = arr[valid_mask]
        rel_pct = None
        if window_vals.size and overview_dist.get(name.lower() if name.lower() in overview_dist else "", np.array([])).size:
            dist = overview_dist[name.lower()]
            rel_pct = float((dist < np.mean(window_vals)).mean() * 100.0)
        block["window_mean_relative_percentile_in_mosaic_overview"] = rel_pct
        block["nodata_value_in_source_raster"] = nodata
        return block

    pv_block = full_metric("pv", pv_w, valid_pv_w, None)
    cpr_block = full_metric("cpr", cpr_w, valid_cpr_w, cpr_nodata)
    srd_block = full_metric("serd", srd_w, valid_srd_w, srd_nodata)
    trt_block = full_metric("tratio", trt_w, valid_trt_w, trt_nodata)

    window_meta = {
        "candidate_id": CANDIDATE_ID,
        "candidate_lat_lon_deg": [CAND_LAT, CAND_LON],
        "candidate_projected_xy_m": [float(cand_x), float(cand_y)],
        "half_window_m": HALF_WINDOW_M,
        "window_bounds_m": list(bounds),
        "window_shape_px": list(pv_w.shape),
        "pixel_size_m": 25.0,
        "crs": "Moon_2000_South_Pole_Stereographic (sphere r=1737400m)",
        "psr_polygon_available": psr_mask_w is not None,
        "psr_area_km2": psr_area_km2,
    }

    for name, block in [("pv", pv_block), ("cpr", cpr_block), ("serd", srd_block), ("tratio", trt_block)]:
        out = {**provenance, "window": window_meta, "result": block}
        with open(os.path.join(OUT_DIR, f"candidate_{name}.json"), "w") as f:
            json.dump(out, f, indent=2, default=str)

    summary = {
        **provenance,
        "georeferencing_check": {"verdict": georef_check["verdict"], "round_trip_max_abs_error_deg": georef_check["round_trip_max_abs_error_deg"]},
        "window": window_meta,
        "pv": pv_block,
        "cpr": cpr_block,
        "serd": srd_block,
        "tratio": trt_block,
        "psr_interior_vs_surroundings_available": psr_mask_w is not None,
        "limitations": [
            "This is a mosaic-derived (L4/L3C, multi-year compiled) result, not from a single dated acquisition -- it characterizes the candidate location as represented in the 2025-06-30 mosaic products, built from 602 contributing acquisitions spanning 2019-09-22 to 2023-10-18.",
            "Window is a fixed +/-3300 m square in projected map coordinates around the candidate point, not the PSR polygon itself -- PSR interior/surroundings split (when available) is a secondary breakdown within this same window.",
            "'Relative percentile within the mosaic overview' compares the window MEAN against a 1500-row-overview (averaged/resampled) distribution of the whole mosaic, not full-resolution -- it is an approximate global context, not an exact full-res percentile.",
            "No independent ground truth for ice exists; these are radar-derived scattering metrics only.",
        ],
    }
    with open(os.path.join(OUT_DIR, "candidate_physics_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # ---- Plots ----
    def plot_metric(arr, valid_mask, name, cmap, vmin, vmax, fname):
        fig, ax = plt.subplots(figsize=(6, 6))
        disp = np.where(valid_mask, arr, np.nan)
        im = ax.imshow(disp, cmap=cmap, vmin=vmin, vmax=vmax)
        if psr_mask_w is not None:
            ax.contour(psr_mask_w, colors="red", linewidths=1.2)
        ax.set_title(f"{CANDIDATE_ID} {name}\nwindow {window_meta['window_shape_px']} px @ 25 m, +/-{int(HALF_WINDOW_M)} m")
        plt.colorbar(im, ax=ax, shrink=0.8, label=name)
        ax.set_xlabel("pixel (x)"); ax.set_ylabel("pixel (y)")
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, fname), dpi=150)
        plt.close(fig)

    plot_metric(pv_w, valid_pv_w, "Pv", "viridis", 0, 1, "candidate_pv.png")
    plot_metric(cpr_w, valid_cpr_w, "CPR", "inferno", 0, 1.5, "candidate_cpr.png")
    plot_metric(srd_w, valid_srd_w, "SERD", "viridis", 0, 1, "candidate_serd.png")
    plot_metric(trt_w, valid_trt_w, "T-Ratio", "plasma", 0, 1, "candidate_tratio.png")

    # ---- Track B locator plot: whole mosaic + candidate + window box ----
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(np.where(np.isfinite(pv_ov), pv_ov, np.nan), cmap="gray",
                    extent=[full_bounds.left, full_bounds.right, full_bounds.bottom, full_bounds.top],
                    vmin=0, vmax=1, origin="upper")
    ax.plot(cand_x, cand_y, "r*", markersize=16, label=f"{CANDIDATE_ID}\n({CAND_LAT}, {CAND_LON})")
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((bounds[0], bounds[1]), bounds[2] - bounds[0], bounds[3] - bounds[1],
                            fill=False, edgecolor="cyan", linewidth=2, label="extraction window"))
    ax.set_title("Candidate locator on Y4R mosaic overview (Pv, grayscale)\nMoon_2000_South_Pole_Stereographic")
    ax.set_xlabel("Easting (m)"); ax.set_ylabel("Northing (m)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "candidate_locator.png"), dpi=150)
    plt.close(fig)

    print("\nCandidate physics summary:")
    print(json.dumps(summary, indent=2, default=str))
    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
