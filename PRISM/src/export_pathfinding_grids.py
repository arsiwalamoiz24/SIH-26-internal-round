"""
Real slope + illumination grids for rover pathfinding, derived from the real
LOLA elevation grids already fetched for the 3D terrain view (no new network
reads -- these are local JSON files under PRISM/outputs/objective_optical/ and
frontend2/public/assets/prism/elevation/).

Reuses PRISM's own already-validated compute_slope / compute_cumulative_
illumination functions (src/terrain_algorithms.py) -- same formulas the
hazard-map pipeline uses, just applied to the coarser (120x120, 9km-half)
wide grid instead of the native 20m/px DEM, since that's the resolution the
3D view and pathfinding both operate at.

Output: one JSON per candidate with slope_deg (grid), illumination_frac
(grid), pixel_size_m, window_half_m, grid_size -- aligned exactly with the
existing *_real_elevation_grid_wide.json for that candidate.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terrain_algorithms import compute_slope, compute_cumulative_illumination

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ELEV_DIR = os.path.join(REPO, "frontend2", "public", "assets", "prism", "elevation")
OUT_DIR = os.path.join(REPO, "frontend2", "public", "assets", "prism", "pathfinding")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_IDS = [
    "SP_840980_0797630", "SP_832640_0090770", "SP_809570_2454450",
    "SP_819860_1568660", "SP_842420_0421060", "SP_817950_1586580",
    "SP_830080_0535120", "SP_871460_0840750", "SP_844580_3134320",
]


def main():
    for cid in CANDIDATE_IDS:
        path = os.path.join(ELEV_DIR, f"{cid}_real_elevation_grid_wide.json")
        if not os.path.exists(path):
            print(f"{cid}: no wide elevation grid, skipping")
            continue
        with open(path) as f:
            d = json.load(f)

        grid = np.array(d["elevationGridRelativeM"], dtype=np.float64)
        grid_size = d["grid_size"]
        half_m = d["window_half_m"]
        pixel_size_m = (2 * half_m) / (grid_size - 1)

        print(f"\n=== {cid} === grid={grid_size}x{grid_size} pixel_size={pixel_size_m:.1f}m")

        slope = compute_slope(grid, pixel_size_m)
        # 8 azimuths x 3 sun elevations = 24 positions, same convention as
        # hazard_map_shortlist_pipeline.py's real illumination model.
        illum = compute_cumulative_illumination(grid, pixel_size_m, n_azimuths=8, sun_elevations=[5, 10, 15])

        print(f"  slope: mean={slope.mean():.2f} max={slope.max():.2f} deg")
        print(f"  illumination: mean={illum.mean():.4f}")

        out = {
            "candidate_id": cid,
            "grid_size": grid_size,
            "window_half_m": half_m,
            "pixel_size_m": pixel_size_m,
            "slopeDeg": np.round(slope, 3).tolist(),
            "illuminationFrac": np.round(illum, 4).tolist(),
        }
        out_path = os.path.join(OUT_DIR, f"{cid}_pathfinding_grid.json")
        with open(out_path, "w") as f:
            json.dump(out, f)
        print(f"  saved -> {out_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
