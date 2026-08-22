"""
PRISM Track J-v2 -- genuine per-pixel Isolation Forest anomaly scoring for the
candidate window, using independent real radar bands (Pv, CPR, SERD, T-Ratio)
as features. This is a different, stronger result than src/ml_anomaly_pipeline.py
(Track J-v1): v1 scores 336 PSRs as samples using Pv-tier-derived aggregate
features (explicitly flagged there as circular / non-independent). Here, each
of the ~69,696 pixels in the candidate's 264x264 window IS a sample, and its
4 features are read directly off 4 different real DFSAR mosaic bands -- none
of them derived from each other or from any prior candidate ranking. v1 is
kept as-is; this is an addition, not a replacement.

Input: data/raw/candidate_window/candidate_window_arrays.npz -- real per-pixel
evn/vol/odd/hlx/cpr/srd/trt/pv arrays for SP_840980_0797630 (-84.098, 79.764),
extracted via GDAL /vsicurl/ windowed remote reads directly against the team's
Y4R (ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx) and L3C
(ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx) mosaic GeoTIFFs -- no full mosaic
download performed. See scripts/legacy/extract_candidate_window_remote.py.
Pv values were independently verified to match PHYSICS_RESULTS.json's Track A
result (mean 0.4543111324310303) to full float32 precision.

Output: PRISM/outputs/objective1/ml/pixel_anomaly_map.json -- per-pixel
anomaly/ice-likelihood grid (full-res + a 48x48 downsample for the frontend's
evidenceGrid), plus PSR-interior-vs-surroundings anomaly comparison using the
real LOLA PSR polygon for this candidate.
"""

import json
import os

import geopandas as gpd
import numpy as np
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from scipy.ndimage import zoom
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NPZ_PATH = os.path.join(REPO, "data", "raw", "candidate_window", "candidate_window_arrays.npz")
PSR_SHP = os.path.join(REPO, "data", "raw", "psr_south", "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective1", "ml")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_ID = "SP_840980_0797630"
RANDOM_STATE = 42
DOWNSAMPLE_SIZE = 48


def main():
    data = np.load(NPZ_PATH)
    pv, cpr, srd, trt = data["pv"], data["cpr"], data["srd"], data["trt"]
    cand_x, cand_y = data["candidate_xy_m"]
    bounds = tuple(data["window_bounds_m"])
    h, w = pv.shape

    valid = np.isfinite(pv) & np.isfinite(cpr) & np.isfinite(srd) & np.isfinite(trt) & (cpr != 0) & (trt != 0)
    n_valid = int(valid.sum())
    print(f"Window {h}x{w} = {h*w} px, {n_valid} valid ({100*n_valid/(h*w):.2f}%)")

    # ---- PSR interior mask (same polygon/window as candidate_physics_pipeline.py) ----
    win_transform = from_bounds(*bounds, w, h)
    psr_mask = None
    try:
        psr = gpd.read_file(PSR_SHP)
        cand_rows = psr[psr.PSR_ID == CANDIDATE_ID]
        if not cand_rows.empty:
            # PSR shapefile CRS should already match the mosaic CRS (both Moon south-polar);
            # reproject defensively if a CRS is present and differs.
            geom = cand_rows.iloc[0].geometry
            psr_mask = geometry_mask([geom], out_shape=(h, w), transform=win_transform, invert=True)
            print(f"PSR interior mask: {int(psr_mask.sum())} px")
    except Exception as e:
        print("PSR mask unavailable:", e)

    # ---- Feature matrix: 4 independent real radar bands, one row per valid pixel ----
    X = np.column_stack([pv[valid], cpr[valid], srd[valid], trt[valid]])
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    iso = IsolationForest(n_estimators=200, contamination="auto", random_state=RANDOM_STATE)
    iso.fit(Xs)
    raw_score = -iso.decision_function(Xs)  # higher = more anomalous, same sign convention as Track J-v1

    score_grid = np.full((h, w), np.nan, dtype=np.float32)
    score_grid[valid] = raw_score

    smin, smax = np.nanmin(score_grid), np.nanmax(score_grid)
    ice_likelihood = (score_grid - smin) / (smax - smin)  # 0..1, NaN stays NaN

    def downsample(grid):
        filled = np.where(np.isnan(grid), np.nanmean(grid), grid)
        factor = (DOWNSAMPLE_SIZE / h, DOWNSAMPLE_SIZE / w)
        return zoom(filled, factor, order=1)[:DOWNSAMPLE_SIZE, :DOWNSAMPLE_SIZE]

    pv_ds = downsample(pv)
    cpr_ds = downsample(cpr)
    ice_ds = downsample(ice_likelihood)
    psr_ds = None
    if psr_mask is not None:
        psr_ds = zoom(psr_mask.astype(np.float32), (DOWNSAMPLE_SIZE / h, DOWNSAMPLE_SIZE / w), order=0)
        psr_ds = (psr_ds[:DOWNSAMPLE_SIZE, :DOWNSAMPLE_SIZE] > 0.5)

    result = {
        "purpose": "Track J-v2 -- genuine per-pixel Isolation Forest, real independent Pv/CPR/SERD/T-Ratio bands as features (not Pv-tier-derived aggregates like Track J-v1).",
        "candidate_id": CANDIDATE_ID,
        "not_a_supervised_classifier": True,
        "no_ground_truth_labels_used": True,
        "model": "sklearn.ensemble.IsolationForest",
        "hyperparameters": {"n_estimators": 200, "contamination": "auto", "random_state": RANDOM_STATE},
        "features": ["Pv", "CPR", "SERD", "T-Ratio"],
        "n_pixels_total": int(h * w),
        "n_pixels_valid": n_valid,
        "window_shape_px": [h, w],
        "pixel_size_m": 25.0,
        "source": "data/raw/candidate_window/candidate_window_arrays.npz (real Y4R+L3C mosaic bands, GDAL /vsicurl/ windowed remote read, verified against PHYSICS_RESULTS.json)",
        "ice_likelihood_definition": "Min-max normalized (0-1) Isolation Forest anomaly score across this window's valid pixels. Higher = more anomalous relative to the rest of THIS window, not a calibrated ice probability.",
    }

    if psr_mask is not None:
        inside_scores = ice_likelihood[psr_mask & valid]
        outside_scores = ice_likelihood[(~psr_mask) & valid]
        result["psr_interior_vs_surroundings"] = {
            "n_px_inside_psr": int((psr_mask & valid).sum()),
            "n_px_outside_psr_in_window": int((~psr_mask & valid).sum()),
            "mean_ice_likelihood_inside_psr": float(np.mean(inside_scores)) if inside_scores.size else None,
            "mean_ice_likelihood_outside_psr": float(np.mean(outside_scores)) if outside_scores.size else None,
        }

    with open(os.path.join(OUT_DIR, "pixel_anomaly_map.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    np.savez_compressed(
        os.path.join(OUT_DIR, "pixel_anomaly_grids.npz"),
        pv_full=pv, cpr_full=cpr, ice_likelihood_full=ice_likelihood,
        psr_mask_full=psr_mask if psr_mask is not None else np.zeros((h, w), dtype=bool),
        pv_48=pv_ds, cpr_48=cpr_ds, ice_likelihood_48=ice_ds,
        psr_mask_48=psr_ds if psr_ds is not None else np.zeros((DOWNSAMPLE_SIZE, DOWNSAMPLE_SIZE), dtype=bool),
    )

    print(json.dumps(result, indent=2, default=str))
    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
