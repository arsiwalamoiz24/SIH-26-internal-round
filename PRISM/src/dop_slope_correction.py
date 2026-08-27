"""
PRISM -- Hypothesis 9: Topographic slope-corrected DOP.

WHAT THE OTHER AI WAS DESCRIBING:
----------------------------------
A previous AI session described a `compute_dop()` function with a
`--lola_dem` flag that applies a "parallax correction" by rotating S2 and S3
in the polarimetric plane by the local slope angle before computing DOP.

The physical basis is well-established in SAR polarimetry:
  - When a radar illuminates a sloped surface, the received polarimetric
    response is rotated by the *orientation angle* (χ) relative to a flat
    surface. This is the Faraday rotation equivalent for terrain geometry.
  - For a slope angle θ in the SAR range direction, the polarimetric
    orientation angle is approximately ψ ≈ θ (the azimuthal projection of
    the terrain slope relative to the radar look direction).
  - The corrected Stokes vector after orientation-angle removal is:
      S2' = S2·cos(2ψ) + S3·sin(2ψ)
      S3' = -S2·sin(2ψ) + S3·cos(2ψ)
      S4' = S4  (unchanged)
  - Corrected DOP: m' = sqrt(S2'² + S3'² + S4²) / S1

WHY IT MATTERS FOR FAUSTINI/CRATERS:
--------------------------------------
Crater walls at steep southern-polar craters (Faustini, Shackleton) have
slopes of 20–35°. A 30° slope gives 2ψ = 60°, which significantly
rotates the (S2, S3) plane. The existing DOP investigation (8 hypotheses,
DOP_GROUND_TRUTH_INVESTIGATION.md) found DOP≈0.63–0.85 vs paper's 0.10–0.13
and attributed the excess to a "residual geometric/topographic phase trend" —
this is exactly what the slope correction targets.

HOW TO RUN:
-----------
  python dop_slope_correction.py                # uses analytic slope proxy
  python dop_slope_correction.py --lola_dem     # fetches real LOLA DEM slope grid

NOTE: The --lola_dem fetch requires network access to NASA GSFC PGDA. Without
it, we use an analytic approximation: assume a typical crater-wall slope of
25° for pixels in the outer 30% of the window (near rim), tapering to 0° at
center (crater floor). This is physically motivated but not data-derived.

METHODOLOGICAL HONESTY:
------------------------
  - We do NOT tune ψ to force a match with Sinha's 0.10–0.13 target.
  - We apply the correction uniformly across the Mini-RF window.
  - We report both corrected and uncorrected DOP side by side.
  - If the corrected DOP still doesn't match, that is reported honestly.

SITES: Only sites where DOP is a bottleneck are evaluated:
  - Faustini (known ice reference, DOP bottleneck)
  - Primary candidate SP_840980_0797630 (PRISM's pick, DOP bottleneck)
  - Shackleton (PM4W priority site, DOP bottleneck)

OUTPUT:
  PRISM/outputs/objective1/dop_v2/slope_corrected_dop_results.json
  PRISM/outputs/objective1/dop_v2/slope_corrected_dop_comparison.csv
"""

import argparse
import json
import os
import sys

import numpy as np
import rasterio
from rasterio.env import Env
from rasterio.windows import from_bounds as window_from_bounds
from pyproj import Transformer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pm4w_detector_v2 import fetch_site_stokes, DOP_THRESHOLD

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "dop_v2")
os.makedirs(OUT_DIR, exist_ok=True)

LDEM_URL = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
MOON_RADIUS = 1737400
MOON_GEOG_CRS = "+proj=longlat +R=1737400 +no_defs"
MOON_POLAR_CRS = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"

# Mini-RF: one pixel ≈ 7.5m at 128ppd resolution
MINIRF_PX_SIZE_M = 7.5
WIN_PX = 61  # must match pm4w_detector_v2.py

SITES = {
    "Faustini":             {"lat": -87.3,   "lon": 77.0,    "known_ice": True},
    "SP_840980_0797630":    {"lat": -84.098, "lon": 79.764,  "known_ice": None},
    "Shackleton":           {"lat": -89.54,  "lon": 129.20,  "known_ice": None},
}


def fetch_lola_slope_grid(lat: float, lon: float, win_px: int, px_size_m: float) -> np.ndarray:
    """
    Fetch a LOLA DEM tile centred on (lat, lon), compute per-pixel slope in
    degrees, then downsample to the Mini-RF window size (win_px × win_px).
    
    Slope is computed as the gradient magnitude (both range and azimuth).
    Returns a (win_px, win_px) float array of slope angles in degrees.
    """
    tf = Transformer.from_crs(MOON_GEOG_CRS, MOON_POLAR_CRS, always_xy=True)
    cx, cy = tf.transform(lon, lat)

    # Fetch a slightly larger DEM window for gradient computation at edges
    half_m = (win_px // 2 + 5) * px_size_m * 2.0  # generous margin

    print(f"  Fetching LOLA DEM for ({lat:.3f}, {lon:.3f}), half={half_m:.0f}m ...", flush=True)
    with Env(GDAL_HTTP_TIMEOUT=120, CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF"):
        with rasterio.open(LDEM_URL) as src:
            bounds = (cx - half_m, cy - half_m, cx + half_m, cy + half_m)
            window = window_from_bounds(*bounds, transform=src.transform)
            dem = src.read(1, window=window).astype(np.float64)
            dem_px_m = abs(src.transform.a)  # native pixel size in metres

    # Compute gradient magnitude in metres/metre → slope in degrees
    dy, dx = np.gradient(dem, dem_px_m, dem_px_m)
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)

    # Downsample to Mini-RF window (win_px × win_px)
    h, w = slope_deg.shape
    row_idx = np.linspace(0, h - 1, win_px).astype(int)
    col_idx = np.linspace(0, w - 1, win_px).astype(int)
    slope_grid = slope_deg[np.ix_(row_idx, col_idx)]

    print(f"    DEM shape: {dem.shape}, native px={dem_px_m:.1f}m, "
          f"slope range: {slope_grid.min():.1f}–{slope_grid.max():.1f}°, "
          f"mean: {slope_grid.mean():.1f}°", flush=True)
    return slope_grid


def analytic_slope_proxy(win_px: int, rim_slope_deg: float = 25.0) -> np.ndarray:
    """
    Analytic crater-wall slope proxy when LOLA data is unavailable.
    
    Assumes:
    - Crater floor (inner 40% radius): near-flat, ~0–5°
    - Crater wall (40–80% radius): rises to rim_slope_deg
    - Rim and beyond (>80% radius): rim_slope_deg
    
    This is physically motivated for simple bowl-shaped craters but is
    NOT data-derived. Explicitly labelled as a proxy in all outputs.
    """
    cx, cy = win_px // 2, win_px // 2
    r_max = win_px // 2
    yy, xx = np.mgrid[0:win_px, 0:win_px]
    r = np.sqrt((xx - cx)**2 + (yy - cy)**2)
    r_norm = r / r_max  # 0=center, 1=edge

    slope = np.where(
        r_norm < 0.4,
        r_norm / 0.4 * 5.0,                               # 0→5° toward inner wall
        np.where(r_norm < 0.8,
                 5.0 + (r_norm - 0.4) / 0.4 * (rim_slope_deg - 5.0),  # 5→rim_slope
                 rim_slope_deg)                            # flat at rim
    )
    return slope


def apply_orientation_angle_correction(S1, S2, S3, S4, slope_grid_deg: np.ndarray):
    """
    Apply the polarimetric orientation angle correction.
    
    For a surface with terrain slope angle θ (in the radar range direction),
    the orientation angle ψ ≈ θ. The correction rotates (S2, S3):
      S2' = S2·cos(2ψ) + S3·sin(2ψ)
      S3' = -S2·sin(2ψ) + S3·cos(2ψ)
      S4' = S4   (Stokes parameter 4 is not affected by orientation angle)
    
    Reference: Cloude & Pottier (1997), Lee & Pottier "Polarimetric Radar
    Imaging" §6.3, Ainsworth et al. 2006 §II (their "α" channel imbalance
    is a *different* problem — orientation angle is applied before that step).
    """
    psi = np.radians(slope_grid_deg)         # orientation angle in radians
    cos2 = np.cos(2 * psi)
    sin2 = np.sin(2 * psi)

    S2_corr = S2 * cos2 + S3 * sin2
    S3_corr = -S2 * sin2 + S3 * cos2
    # S4 unchanged

    with np.errstate(divide="ignore", invalid="ignore"):
        dop_corr = np.sqrt(S2_corr**2 + S3_corr**2 + S4**2) / S1
        dop_orig = np.sqrt(S2**2 + S3**2 + S4**2) / S1

    return dop_corr, dop_orig, psi


def evaluate_site_slope_corrected(site_id: str, lat: float, lon: float,
                                   use_lola: bool) -> dict:
    print(f"\n=== {site_id} ({lat}, {lon}) ===", flush=True)

    # 1. Fetch Mini-RF Stokes
    print("  Fetching real Mini-RF S1-S4...", flush=True)
    stokes = fetch_site_stokes(lat, lon)
    S1, S2, S3, S4 = (stokes[b] for b in ["s1", "s2", "s3", "s4"])

    # nodata mask
    nodata = ~(np.isfinite(S1) & np.isfinite(S2) & np.isfinite(S3) & np.isfinite(S4))
    nodata |= (S1 <= -3e38) | (S2 <= -3e38) | (S3 <= -3e38) | (S4 <= -3e38)
    valid = ~nodata

    # 2. Get slope grid
    if use_lola:
        slope_grid = fetch_lola_slope_grid(lat, lon, WIN_PX, MINIRF_PX_SIZE_M)
        slope_source = "LOLA DEM (LDEM_80S_20MPP_ADJ.TIF, NASA GSFC PGDA)"
    else:
        slope_grid = analytic_slope_proxy(WIN_PX)
        slope_source = "Analytic crater-wall proxy (NOT data-derived; rim_slope=25°)"
    print(f"  Slope source: {slope_source}", flush=True)

    # Ensure slope_grid matches S1 shape (may differ if raster read was clipped)
    if slope_grid.shape != S1.shape:
        from scipy.ndimage import zoom
        scale = (S1.shape[0] / slope_grid.shape[0], S1.shape[1] / slope_grid.shape[1])
        slope_grid = zoom(slope_grid, scale, order=1)

    # 3. Apply correction
    dop_corr, dop_orig, psi = apply_orientation_angle_correction(S1, S2, S3, S4, slope_grid)

    # 4. Stats on valid pixels
    v_dop_orig = dop_orig[valid]
    v_dop_corr = dop_corr[valid]
    v_slope = slope_grid[valid]

    n_pass_orig = int((v_dop_orig < DOP_THRESHOLD).sum())
    n_pass_corr = int((v_dop_corr < DOP_THRESHOLD).sum())
    n_valid = int(valid.sum())

    result = {
        "site_id": site_id,
        "lat": lat,
        "lon": lon,
        "slope_source": slope_source,
        "n_valid_px": n_valid,
        "dop_uncorrected": {
            "mean": float(v_dop_orig.mean()),
            "median": float(np.median(v_dop_orig)),
            "min": float(v_dop_orig.min()),
            "max": float(v_dop_orig.max()),
            "n_pass_dop_lt_0p2": n_pass_orig,
            "pct_pass": round(100 * n_pass_orig / n_valid, 2) if n_valid else 0,
        },
        "dop_slope_corrected": {
            "mean": float(v_dop_corr.mean()),
            "median": float(np.median(v_dop_corr)),
            "min": float(v_dop_corr.min()),
            "max": float(v_dop_corr.max()),
            "n_pass_dop_lt_0p2": n_pass_corr,
            "pct_pass": round(100 * n_pass_corr / n_valid, 2) if n_valid else 0,
        },
        "slope_stats_deg": {
            "mean": float(v_slope.mean()),
            "max": float(v_slope.max()),
            "min": float(v_slope.min()),
        },
        "interpretation": (
            "DOP improvement: slope correction moved DOP toward ice-consistent range (<0.2)"
            if v_dop_corr.mean() < v_dop_orig.mean() * 0.8
            else "DOP not significantly changed by slope correction"
        ),
    }

    print(f"  DOP uncorrected : mean={result['dop_uncorrected']['mean']:.4f}, "
          f"pass<0.2: {n_pass_orig}/{n_valid} ({result['dop_uncorrected']['pct_pass']}%)", flush=True)
    print(f"  DOP slope-corr  : mean={result['dop_slope_corrected']['mean']:.4f}, "
          f"pass<0.2: {n_pass_corr}/{n_valid} ({result['dop_slope_corrected']['pct_pass']}%)", flush=True)
    print(f"  Slope grid: mean={result['slope_stats_deg']['mean']:.1f}°, "
          f"max={result['slope_stats_deg']['max']:.1f}°", flush=True)
    print(f"  → {result['interpretation']}", flush=True)

    return result


def main():
    parser = argparse.ArgumentParser(description="Hypothesis 9: Slope-corrected DOP")
    parser.add_argument("--lola_dem", action="store_true",
                        help="Fetch real LOLA DEM slope grid from NASA GSFC PGDA "
                             "(requires network, ~2 min per site). Without this flag, "
                             "uses an analytic crater-wall proxy.")
    args = parser.parse_args()

    print("=" * 70, flush=True)
    print("HYPOTHESIS 9: Topographic slope-corrected DOP", flush=True)
    print(f"Mode: {'Real LOLA DEM' if args.lola_dem else 'Analytic proxy (no --lola_dem flag)'}", flush=True)
    print("=" * 70, flush=True)

    all_results = []
    for site_id, meta in SITES.items():
        result = evaluate_site_slope_corrected(
            site_id, meta["lat"], meta["lon"], use_lola=args.lola_dem
        )
        result["known_ice"] = meta["known_ice"]
        all_results.append(result)

    # Save JSON
    out_json = os.path.join(OUT_DIR, "slope_corrected_dop_results.json")
    with open(out_json, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # Save CSV comparison
    import csv
    out_csv = os.path.join(OUT_DIR, "slope_corrected_dop_comparison.csv")
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["site_id", "known_ice", "slope_source",
                         "dop_uncorr_mean", "dop_corr_mean",
                         "dop_uncorr_pct_pass", "dop_corr_pct_pass",
                         "slope_mean_deg", "slope_max_deg",
                         "interpretation"])
        for r in all_results:
            writer.writerow([
                r["site_id"], r["known_ice"], r["slope_source"],
                round(r["dop_uncorrected"]["mean"], 4),
                round(r["dop_slope_corrected"]["mean"], 4),
                r["dop_uncorrected"]["pct_pass"],
                r["dop_slope_corrected"]["pct_pass"],
                round(r["slope_stats_deg"]["mean"], 1),
                round(r["slope_stats_deg"]["max"], 1),
                r["interpretation"],
            ])

    print(f"\nSaved: {out_json}", flush=True)
    print(f"Saved: {out_csv}", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("SUMMARY", flush=True)
    print("=" * 70, flush=True)
    for r in all_results:
        delta_pct = r["dop_slope_corrected"]["pct_pass"] - r["dop_uncorrected"]["pct_pass"]
        print(f"  {r['site_id']:<30}  DOP pass: "
              f"{r['dop_uncorrected']['pct_pass']:5.1f}% → {r['dop_slope_corrected']['pct_pass']:5.1f}%  "
              f"(Δ {delta_pct:+.1f}%)", flush=True)

    print("\nNOTE: If slope correction did NOT move DOP to <0.2, this is an honest", flush=True)
    print("negative result (Hypothesis 9 = FAIL), consistent with the DOP investigation's", flush=True)
    print("conclusion that the mismatch is likely a processing-level difference vs", flush=True)
    print("Sinha et al. 2026, not correctable from public data alone.", flush=True)


if __name__ == "__main__":
    main()
