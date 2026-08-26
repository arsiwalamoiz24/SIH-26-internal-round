"""
Tight, single-panel "elevation only" crop (no title/axis/colorbar) for each of
the 7 candidates, for use as a 3D mesh texture on the frontend terrain page.

Built entirely offline from the real elevation grids already fetched by
real_terrain_grid_pipeline.py (PRISM/outputs/objective_optical/*_real_elevation_grid.json)
-- no network read, so it sidesteps a corrupted remote byte-range that made
terrain_pipeline.py's own direct-from-DEM crop attempt fail repeatedly at the
same offset for the 5000m-buffer window.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRID_DIR = os.path.join(REPO, "PRISM", "outputs", "objective_optical")
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective2", "elevation_only")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_IDS = [
    "SP_840980_0797630", "SP_832640_0090770", "SP_809570_2454450",
    "SP_819860_1568660", "SP_842420_0421060", "SP_817950_1586580",
    "SP_830080_0535120",
]


def main():
    for cid in CANDIDATE_IDS:
        path = os.path.join(GRID_DIR, f"{cid}_real_elevation_grid.json")
        with open(path) as f:
            data = json.load(f)
        grid = np.array(data["elevationGridRelativeM"])

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(grid, cmap="terrain")
        ax.axis("off")
        out_path = os.path.join(OUT_DIR, f"{cid}.png")
        fig.savefig(out_path, dpi=150, bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        print(f"{cid}: {grid.shape} -> {out_path}")

    print("\nDone.", len(CANDIDATE_IDS), "crops written to", OUT_DIR)


if __name__ == "__main__":
    main()
