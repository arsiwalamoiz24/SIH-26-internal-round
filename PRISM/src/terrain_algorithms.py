"""
PRISM Objective 2 -- shared terrain/hazard algorithms, ported from
notebooks/obj2_probably.ipynb (formulas unchanged) and used by both
hazard_map_pipeline.py (single-candidate, full-res) and
hazard_map_regional_pipeline.py (whole-south-pole, overview-res).

All functions operate on a real elevation array (meters). Callers are
responsible for passing the correct DEM (LDEM_80S_20MPP_ADJ.TIF, not the
LDSM slope product -- see hazard_map_pipeline.py's docstring for the bug this
project found and fixed in the source notebook).
"""

import numpy as np
from scipy.ndimage import sobel, uniform_filter, rotate


def compute_slope(dem, pixel_size):
    dz_dx = sobel(dem, axis=1) / (8.0 * pixel_size)
    dz_dy = sobel(dem, axis=0) / (8.0 * pixel_size)
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    return np.degrees(slope_rad)


def compute_roughness_rms(dem, window_size=5):
    local_mean = uniform_filter(dem, size=window_size)
    local_mean_sq = uniform_filter(dem**2, size=window_size)
    variance = np.maximum(local_mean_sq - local_mean**2, 0.0)
    return np.sqrt(variance)


def compute_illumination(dem, sun_elevation_deg, sun_azimuth_deg, pixel_size):
    rows, cols = dem.shape
    tan_elev = np.tan(np.radians(sun_elevation_deg))
    angle = 270.0 - sun_azimuth_deg
    dem_rot = rotate(dem, angle, reshape=True, mode="nearest")
    cols_rot = dem_rot.shape[1]
    x_coords = np.arange(cols_rot) * pixel_size
    H_eff = dem_rot - x_coords[np.newaxis, :] * tan_elev
    H_max = np.maximum.accumulate(H_eff, axis=1)
    shadow_rot = H_eff < (H_max - 1e-4)
    shadow_full = rotate(shadow_rot, -angle, reshape=False, order=0)
    r_center, c_center = shadow_full.shape[0] / 2.0, shadow_full.shape[1] / 2.0
    r_start = int(round(r_center - rows / 2.0))
    c_start = int(round(c_center - cols / 2.0))
    shadow = shadow_full[r_start:r_start + rows, c_start:c_start + cols]
    return ~shadow


def compute_cumulative_illumination(dem, pixel_size, n_azimuths=8, sun_elevations=(5, 10, 15)):
    rows, cols = dem.shape
    accum = np.zeros((rows, cols), dtype=np.float64)
    azimuths = np.linspace(0, 360, n_azimuths, endpoint=False)
    count = 0
    for elev in sun_elevations:
        for az in azimuths:
            lit = compute_illumination(dem, elev, az, pixel_size)
            accum += lit.astype(np.float64)
            count += 1
    return accum / count if count > 0 else accum


def compute_hazard_map(slope, roughness, illumination_frac, weights=None):
    if weights is None:
        weights = {"slope": 1 / 3, "roughness": 1 / 3, "illumination": 1 / 3}

    def _normalise(arr):
        a_min, a_max = np.nanmin(arr), np.nanmax(arr)
        denom = a_max - a_min
        return np.zeros_like(arr) if denom == 0 else (arr - a_min) / denom

    slope_norm = _normalise(slope)
    rough_norm = _normalise(roughness)
    illum_inv = 1.0 - np.clip(illumination_frac, 0.0, 1.0)
    hazard = (weights["slope"] * slope_norm + weights["roughness"] * rough_norm + weights["illumination"] * illum_inv)
    return np.clip(hazard / sum(weights.values()), 0.0, 1.0)


def stats_block(arr, label):
    finite = arr[np.isfinite(arr)]
    return {
        "label": label,
        "n_px": int(finite.size),
        "min": float(finite.min()), "max": float(finite.max()),
        "mean": float(finite.mean()), "median": float(np.median(finite)), "std": float(finite.std()),
    }
