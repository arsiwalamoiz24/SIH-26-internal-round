"""
PRISM -- validate the CPR pipeline against Sinha et al. 2026's OWN nine doubly
shadowed craters, using the paper's own internal positive/negative split.

WHY THIS TEST AND NOT THE EARLIER ONES
--------------------------------------
Two ice validations already exist in this project and they appear to disagree:

  * docs/INDEPENDENT_ICE_VALIDATION.md (2026-08-22) sampled whole crater disks
    (Faustini = 39 km diameter, a 1,195 km2 disk) and found NO separation
    between M3-positive craters and checked-negative controls.
  * outputs/objective1/paper_crater_validation/ (2026-08-25) sampled the paper's
    own 700-1100 m sub-features F2/F3 and DID reproduce the paper's CPR numbers.

Same craters, same mosaics, same formulas. The difference is sampling scale, and
the gradient inside Faustini is monotonic:

    whole 39 km crater disk .......... CPR mean 0.297
    F2's ~4 km neighbourhood ......... CPR mean 0.567
    F2 ice-feature interior (r=550m) . CPR mean 0.967

The ice signal lives in features ~0.08% the area of a whole-crater window, so
whole-crater averaging destroys it. That explains the null result, but it does
NOT establish that PRISM separates ice from anything: F2 and F3 are small
craters, and small craters have rough blocky interiors that raise CPR with or
without ice. Sinha et al.'s own Supplementary Figure 6 makes exactly this point
(rough exterior terrain: CPR 1.1 but DOP 0.17) and concludes that "high CPR
alone is insufficient and that the combined CPR-DOP criterion is required to
distinguish roughness driven scattering from subsurface volumetric scattering."

This script runs the test that can actually distinguish those cases with the
data PRISM has. Supplementary Figure 5 gives per-crater interior CPR histograms
for all nine doubly shadowed craters and annotates in red those "having
relatively higher number of CPR elevated pixels": F2, F3, H3, S1 -- against
F1, H1, H2, S2, S3 which are not annotated. All nine are small, doubly
shadowed, inside PSRs, in the same thermal environment, of the same
morphological class. That 4-vs-5 split therefore controls for sampling scale,
shadowing and crater morphology BY CONSTRUCTION, which no control set PRISM
could assemble from a crater catalogue does.

The question this script answers: does PRISM's own CPR, computed from its own
mosaics, reproduce the paper's 4-vs-5 ordering?

WHAT THIS SCRIPT CANNOT DO -- STATED UP FRONT
---------------------------------------------
It tests CPR ordering ONLY. PRISM's DOP needs Level-1A SLC (phase-preserving)
data; the L4/L3C mosaics read here are amplitude-derived products. So this
cannot evaluate the combined CPR-DOP criterion the paper says is required. A
positive result here is necessary-but-not-sufficient evidence, and must be
reported that way. See docs/SINHA_SUPPLEMENTARY_FINDINGS.md.

FORMULAS ARE UNCHANGED. Pv, CPR, SERD and T-Ratio are read/derived exactly as
in src/paper_crater_pipeline.py and src/candidate_physics_pipeline.py. Only the
site list and the group-level statistics are new. read_window/stats_block are
intentionally identical to src/paper_crater_pipeline.py -- each pipeline in
this directory is standalone by convention.

MISSING COORDINATES ARE A HARD STOP, NOT A GUESS
------------------------------------------------
Only F2 and F3 have published coordinates transcribed into this project (from
the main paper, via src/paper_crater_pipeline.py). The other seven craters and
Tooley are marked lat=None below. The script REFUSES TO RUN and prints exactly
what is missing rather than inventing positions -- a fabricated coordinate here
would silently produce a real-looking but meaningless validation result.

Fill them from the main paper (Sinha et al. 2026, npj Space Exploration 2:22),
which tabulates the craters. Do not source them from any PRISM output.

USAGE
    python src/nine_crater_validation_pipeline.py

Override the data locations without editing this file:
    PRISM_L4_DIR=/path/to/l4_mosaic PRISM_L3C_DIR=/path/to/l3c_cpr \
    PRISM_REPO=/path/to/repo/PRISM python src/nine_crater_validation_pipeline.py
"""

import json
import os
import sys

import numpy as np
import pyproj
import rasterio
from rasterio.windows import from_bounds as window_from_bounds

L4_DIR = os.environ.get("PRISM_L4_DIR", r"C:\Users\radhe\PRISM_local_data\l4_mosaic")
L3C_DIR = os.environ.get("PRISM_L3C_DIR", r"C:\Users\radhe\PRISM_local_data\l3c_cpr")
REPO = os.environ.get(
    "PRISM_REPO", r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
)
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "nine_crater_validation")

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

# ---------------------------------------------------------------------------
# Site table.
#
# paper_elevated_cpr is the LABEL BEING TESTED, taken from Supplementary
# Figure 5's red annotation ("craters ... having relatively higher number of
# CPR elevated pixels"). It is the paper's finding, never a PRISM output, and
# is never used to select or weight anything below -- only to score the result.
#
# half_window_m is set to ~3.6x the interior radius so the surroundings ring
# has comparable area to the interior, matching paper_crater_pipeline.py's
# F2 (r=550, hw=2000) and F3 (r=350, hw=1300) geometry.
# ---------------------------------------------------------------------------
CRATERS = [
    # --- Faustini ---
    dict(id="F1", host="Faustini", lat=None, lon=None, diameter_m=None,
         paper_elevated_cpr=False),
    dict(id="F2", host="Faustini", lat=-87.39, lon=82.31, diameter_m=1100,
         half_window_m=2000, paper_elevated_cpr=True),
    dict(id="F3", host="Faustini", lat=-87.31, lon=86.333, diameter_m=700,
         half_window_m=1300, paper_elevated_cpr=True),
    # --- Haworth ---
    dict(id="H1", host="Haworth", lat=None, lon=None, diameter_m=None,
         paper_elevated_cpr=False),
    dict(id="H2", host="Haworth", lat=None, lon=None, diameter_m=None,
         paper_elevated_cpr=False),
    dict(id="H3", host="Haworth", lat=None, lon=None, diameter_m=None,
         paper_elevated_cpr=True),
    # --- Shoemaker ---
    dict(id="S1", host="Shoemaker", lat=None, lon=None, diameter_m=None,
         paper_elevated_cpr=True),
    dict(id="S2", host="Shoemaker", lat=None, lon=None, diameter_m=None,
         paper_elevated_cpr=False),
    dict(id="S3", host="Shoemaker", lat=None, lon=None, diameter_m=None,
         paper_elevated_cpr=False),
]

# Control ROIs from Supplementary Figure 4. These are NOT doubly shadowed
# craters -- they are the paper's own negative regions. F2_exterior additionally
# has published values (Supplementary Figure 6: mean CPR 1.1, mean DOP 0.17,
# <2% of pixels with CPR>1), so PRISM's number for it is directly checkable.
CONTROLS = [
    dict(id="Tooley_floor", host="Tooley", lat=None, lon=None, diameter_m=None,
         kind="crater_floor", paper_reported=None),
    dict(id="H3_exterior", host="Haworth", lat=None, lon=None, diameter_m=None,
         kind="exterior_melt_flow", paper_reported=None,
         note="Supplementary Figure 3: exterior dominated by impact melt flow "
              "deposits extending 3-5 crater radii from the rim."),
    dict(id="F2_exterior", host="Faustini", lat=None, lon=None, diameter_m=None,
         kind="exterior_rough",
         paper_reported={"cpr_mean": 1.1, "dop_mean": 0.17, "pct_gt1_lt": 2.0},
         note="Supplementary Figure 6. The paper's roughness control: elevated "
              "CPR but DOP above the 0.13 threshold."),
]

# Tooley_wall is an arc-shaped ROI in Supplementary Figure 4, not a disk, so it
# cannot be reproduced by the circular-mask geometry used here. Excluded rather
# than approximated by a circle that would sample the floor as well as the wall.


def read_window(path, bounds):
    with rasterio.open(path) as src:
        window = window_from_bounds(*bounds, transform=src.transform)
        arr = src.read(1, window=window)
        win_transform = src.window_transform(window)
        nodata = src.nodata
    return arr.astype(np.float32), win_transform, nodata


def stats_block(arr, valid_mask):
    vals = arr[valid_mask]
    block = {"n_total_px": int(arr.size), "n_valid_px": int(vals.size)}
    if vals.size > 0:
        block.update({"mean": float(np.mean(vals)), "median": float(np.median(vals)),
                      "std": float(np.std(vals)), "min": float(np.min(vals)),
                      "max": float(np.max(vals))})
    else:
        block.update({k: None for k in ["mean", "median", "std", "min", "max"]})
    return block


def check_sites_complete(sites):
    """Refuse to run on placeholder coordinates. Never guess a position."""
    missing = [s["id"] for s in sites if s.get("lat") is None or s.get("lon") is None
               or s.get("diameter_m") is None]
    if missing:
        print("REFUSING TO RUN -- missing published coordinates/diameters for:")
        for mid in missing:
            print(f"  - {mid}")
        print(
            "\nThese are in the main paper (Sinha et al. 2026, npj Space Exploration\n"
            "2:22, doi:10.1038/s44453-026-00038-9), not in the Supplementary\n"
            "Information. Fill lat/lon/diameter_m in CRATERS/CONTROLS above from the\n"
            "paper's own table. Do NOT source them from any PRISM output, and do NOT\n"
            "estimate them from a figure -- a wrong position produces a real-looking\n"
            "but meaningless validation result.\n"
        )
        return False
    return True


def measure_site(site, fwd):
    """Interior/surroundings Pv, CPR, SERD, T-Ratio for one circular ROI."""
    cx, cy = fwd.transform(site["lon"], site["lat"])
    radius_m = site["diameter_m"] / 2.0
    hw = site.get("half_window_m") or int(round(3.6 * radius_m))
    bounds = (cx - hw, cy - hw, cx + hw, cy + hw)

    evn, win_tr, _ = read_window(Y4R_PATHS["evn"], bounds)
    vol, _, _ = read_window(Y4R_PATHS["vol"], bounds)
    odd, _, _ = read_window(Y4R_PATHS["odd"], bounds)
    hlx, _, _ = read_window(Y4R_PATHS["hlx"], bounds)
    cpr, _, cpr_nd = read_window(CPR_PATHS["cpr"], bounds)
    srd, _, srd_nd = read_window(CPR_PATHS["srd"], bounds)
    trt, _, trt_nd = read_window(CPR_PATHS["trt"], bounds)

    total = evn + vol + odd + hlx
    valid_pv = np.isfinite(total) & (total > 0)
    pv = np.where(valid_pv, vol / np.where(valid_pv, total, np.nan), np.nan)

    def valid_of(arr, nd, drop_zero):
        m = np.isfinite(arr)
        if drop_zero:
            m &= arr != 0
        if nd is not None:
            m &= arr != nd
        return m

    valid_cpr = valid_of(cpr, cpr_nd, True)
    valid_srd = valid_of(srd, srd_nd, False)
    valid_trt = valid_of(trt, trt_nd, True)

    h, w = pv.shape
    rows, cols = np.indices((h, w))
    col_c, row_c = ~win_tr * (cx, cy)
    px_size = abs(win_tr.a)
    interior = np.hypot(cols - col_c, rows - row_c) * px_size <= radius_m
    exterior = ~interior

    def block_for(arr, valid, is_cpr=False):
        inside = valid & interior
        rec = {"interior": stats_block(arr, inside),
               "surroundings": stats_block(arr, valid & exterior)}
        if is_cpr and int(inside.sum()) > 0:
            n_in = int(inside.sum())
            rec["interior"]["pct_gt1"] = round(100.0 * int((inside & (arr > 1)).sum()) / n_in, 3)
            elev = inside & (arr > 1)
            rec["interior"]["mean_of_elevated"] = (
                float(arr[elev].mean()) if int(elev.sum()) else None
            )
        return rec

    return {
        "id": site["id"], "host": site["host"],
        "lat_lon_deg": [site["lat"], site["lon"]],
        "projected_xy_m": [float(cx), float(cy)],
        "diameter_m": site["diameter_m"], "interior_radius_m": radius_m,
        "window_half_m": hw, "window_shape_px": list(pv.shape),
        "prism_pv": block_for(pv, valid_pv),
        "prism_cpr": block_for(cpr, valid_cpr, is_cpr=True),
        "prism_srd": block_for(srd, valid_srd),
        "prism_tratio": block_for(trt, valid_trt),
    }


def rank_separation(results, craters):
    """Does PRISM's own CPR reproduce the paper's 4-vs-5 elevated/not split?

    Reported as an exact rank test rather than a threshold comparison: the
    paper's label is relative ("relatively higher number of CPR elevated
    pixels"), so an absolute cutoff would not be a like-for-like test.
    """
    labelled = [(c["id"], c["paper_elevated_cpr"],
                 results[c["id"]]["prism_cpr"]["interior"].get("pct_gt1"))
                for c in craters if results[c["id"]]["prism_cpr"]["interior"].get("pct_gt1") is not None]
    pos = [v for _, lab, v in labelled if lab]
    neg = [v for _, lab, v in labelled if not lab]
    if not pos or not neg:
        return {"status": "INSUFFICIENT DATA", "n_positive": len(pos), "n_negative": len(neg)}

    # Mann-Whitney U / AUC: fraction of positive-negative pairs ordered correctly.
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    auc = wins / (len(pos) * len(neg))
    ordered = sorted(labelled, key=lambda t: -t[2])
    return {
        "metric": "interior pct of pixels with CPR>1",
        "n_positive": len(pos), "n_negative": len(neg),
        "positive_mean": float(np.mean(pos)), "negative_mean": float(np.mean(neg)),
        "auc_paper_label_vs_prism_cpr": round(auc, 4),
        "auc_interpretation": (
            "1.0 = PRISM reproduces the paper's ordering exactly; 0.5 = no better "
            "than chance; <0.5 = PRISM orders them backwards."
        ),
        "prism_ranking_high_to_low": [
            {"id": i, "paper_says_elevated": lab, "prism_pct_gt1": v} for i, lab, v in ordered
        ],
        "verdict": (
            "PRISM's CPR reproduces the paper's split" if auc >= 0.9 else
            "PRISM's CPR partially reproduces the paper's split" if auc >= 0.7 else
            "PRISM's CPR does NOT reproduce the paper's split"
        ),
    }


def main():
    all_sites = CRATERS + CONTROLS
    if not check_sites_complete(all_sites):
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        target_crs = src.crs
    fwd = pyproj.Transformer.from_crs(
        pyproj.CRS.from_wkt(GEOG_MOON_WKT), target_crs, always_xy=True
    )

    results = {}
    for site in all_sites:
        results[site["id"]] = measure_site(site, fwd)
        pct = results[site["id"]]["prism_cpr"]["interior"].get("pct_gt1")
        print(f"{site['id']:<14} CPR>1 interior: {pct}%")

    separation = rank_separation(results, CRATERS)

    summary = {
        "purpose": (
            "Does PRISM's CPR reproduce Sinha et al. 2026's own 4-vs-5 split across "
            "their nine doubly shadowed craters? Their labels come from Supplementary "
            "Figure 5 and are never used to select or weight anything -- only to score."
        ),
        "paper": "Sinha et al. 2026, npj Space Exploration 2:22, doi:10.1038/s44453-026-00038-9",
        "paper_label_source": "Supplementary Figure 5 (red annotation: F2, F3, H3, S1)",
        "scope_limit": (
            "CPR ordering ONLY. PRISM's DOP requires Level-1A SLC phase-preserving data; "
            "these are amplitude-derived L4/L3C mosaics. The paper states that high CPR "
            "alone is insufficient and that the combined CPR-DOP criterion is required to "
            "separate roughness-driven from volumetric scattering (Supplementary Figure 6). "
            "A positive result here is necessary-but-not-sufficient and must be reported so."
        ),
        "separation_test": separation,
        "per_site": results,
    }
    out = os.path.join(OUT_DIR, "nine_crater_validation.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n" + json.dumps(separation, indent=2, default=str))
    print("\nWrote", out)


if __name__ == "__main__":
    main()
