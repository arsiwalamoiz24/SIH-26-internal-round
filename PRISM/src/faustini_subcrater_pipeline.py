"""
Faustini validation case, part 2 -- localized Pv/CPR/SERD/T-Ratio at the exact
F2/F3 sub-craters Sinha et al. 2026 report ice evidence for (1100m and 700m
doubly-shadowed features inside Faustini's much larger PSR), instead of
averaging over Faustini's whole 664 km^2 PSR (radar_pipeline.py's
FULL_RES_IDS run, which dilutes a small localized signal to near
mid-pack -- rank 116/336 by high_tier_fraction, per
PRISM/outputs/objective1/candidate_table_overview.csv).

Coordinates and diameters from PRISM/docs/DOP_GROUND_TRUTH_INVESTIGATION.md
(already independently re-geolocated and footprint-verified in that
investigation, for the DOP/CPR analysis -- reused here for Pv/CPR/SERD/T-Ratio
using the same Y4R/CPR mosaic radar_pipeline.py already uses for the 7
screened candidates, so results are directly comparable to them).

"Inside" = the sub-crater's own disk (its own radius around its center).
"Outside" = an annulus immediately around it out to 2x its radius -- the
local surrounding terrain a lander would cross, same interior-vs-approach
framing used throughout this project's other candidates.
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from radar_pipeline import Y4R_PATHS, CPR_PATHS, read_full_res_window, OUT_DIR

MOON_RADIUS = 1737400

SUBCRATERS = [
    {"id": "F2", "lat": -87.39, "lon": 82.31, "diameter_m": 1100},
    {"id": "F3", "lat": -87.31, "lon": 86.333, "diameter_m": 700},
]


def analyze(sc, transformer):
    cx, cy = transformer.transform(sc["lon"], sc["lat"])
    radius = sc["diameter_m"] / 2
    buffer = radius * 2  # generous margin: interior disk + surrounding annulus
    bounds = (cx - buffer, cy - buffer, cx + buffer, cy + buffer)

    evn, tr = read_full_res_window(Y4R_PATHS["evn"], bounds)
    vol, _ = read_full_res_window(Y4R_PATHS["vol"], bounds)
    odd, _ = read_full_res_window(Y4R_PATHS["odd"], bounds)
    hlx, _ = read_full_res_window(Y4R_PATHS["hlx"], bounds)
    cpr, _ = read_full_res_window(CPR_PATHS["cpr"], bounds)
    srd, _ = read_full_res_window(CPR_PATHS["srd"], bounds)
    trt, _ = read_full_res_window(CPR_PATHS["trt"], bounds)

    total = evn + vol + odd + hlx
    valid_pv = np.isfinite(total) & (total > 0)
    pv = np.where(valid_pv, vol / np.where(valid_pv, total, np.nan), np.nan)

    h, w = evn.shape
    rows, cols = np.indices((h, w))
    xs = tr.c + tr.a * (cols + 0.5) + tr.b * (rows + 0.5)
    ys = tr.f + tr.d * (cols + 0.5) + tr.e * (rows + 0.5)
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    inside = dist <= radius
    outside = (dist > radius) & (dist <= buffer)

    def stat(arr, valid_mask):
        out = {}
        for name, region in [("inside", inside), ("outside", outside)]:
            m = region & valid_mask
            vals = arr[m]
            out[f"{name}_mean"] = float(vals.mean()) if vals.size else None
            out[f"{name}_n"] = int(vals.size)
        return out

    result = {
        "id": sc["id"], "lat": sc["lat"], "lon": sc["lon"], "diameter_m": sc["diameter_m"],
        "window_shape": list(evn.shape),
        "pv": stat(pv, valid_pv),
        "cpr": stat(cpr, np.isfinite(cpr) & (cpr != 0)),
        "srd": stat(srd, np.isfinite(srd)),
        "trt": stat(trt, np.isfinite(trt) & (trt != 0)),
        "note": "inside = the sub-crater's own disk (its published radius); outside = surrounding annulus "
                "out to 2x that radius. Same Y4R/CPR mosaic and methodology as the 7 PRISM-screened candidates.",
    }

    def norm_db(arr):
        with np.errstate(divide="ignore", invalid="ignore"):
            db = 10 * np.log10(arr)
        finite = db[np.isfinite(db)]
        if finite.size == 0:
            return np.zeros_like(arr)
        vmin, vmax = np.percentile(finite, [2, 98])
        return np.clip((db - vmin) / (vmax - vmin), 0, 1)

    rgb = np.dstack([norm_db(evn), norm_db(vol), norm_db(odd)])
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].imshow(rgb)
    axes[0].set_title(f"{sc['id']} Y4R RGB (R=even,G=vol,B=odd)")
    im1 = axes[1].imshow(np.where(valid_pv, pv, np.nan), cmap="viridis", vmin=0, vmax=1)
    axes[1].set_title("Pv"); plt.colorbar(im1, ax=axes[1], shrink=0.7)
    im2 = axes[2].imshow(np.where(np.isfinite(cpr), cpr, np.nan), cmap="inferno", vmin=0, vmax=1)
    axes[2].set_title("CPR"); plt.colorbar(im2, ax=axes[2], shrink=0.7)
    for ax in axes:
        circle = plt.Circle((w / 2, h / 2), radius / abs(tr.a), fill=False, color="cyan", linewidth=1.5)
        ax.add_patch(circle)
    plt.suptitle(f"Faustini {sc['id']} -- {sc['diameter_m']}m feature, Sinha et al. 2026 published ice evidence")
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"faustini_{sc['id']}_pv_cpr.png"), dpi=150)
    plt.close(fig)

    return result


def main():
    dst_proj = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"
    transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", dst_proj, always_xy=True)

    results = []
    for sc in SUBCRATERS:
        print(f"\n=== {sc['id']} ({sc['lat']}, {sc['lon']}, {sc['diameter_m']}m) ===")
        r = analyze(sc, transformer)
        results.append(r)
        print(json.dumps(r, indent=2))

    with open(os.path.join(OUT_DIR, "faustini_subcrater_pv_cpr.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
