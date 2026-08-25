"""
PRISM -- apply the Sinha et al. (2026, npj Space Exploration,
doi:10.1038/s44453-026-00038-9) refined radar ice-diagnostic criterion
(CPR > 1 combined with DOP < 0.13, indicating volumetric scattering) to
PRISM's 7 shortlisted PSR candidates.

This does NOT change any existing PRISM formula. Pv/CPR/SERD/T-Ratio are
read from the same local L4/L3C mosaic GeoTIFFs and the same PSR-polygon
window logic as src/radar_pipeline.py -- this script only adds the
paper-style statistics that radar_pipeline.py's shortlist CSV did not
already capture (max CPR inside, mean CPR of the elevated (CPR>1) subset,
fraction of interior px with CPR>1 restricted strictly to the PSR polygon
interior -- same definition the paper uses per-crater).

DOP is NOT computed here. Candidate-specific DOP (Stokes-parameter,
identical formula to the paper's Eq. 2) exists in this project for exactly
one of the 7 candidates (SP_840980_0797630, from a real downloaded Level-1A
quad-pol SLC acquisition -- see src/candidate_dop_pipeline.py). Computing
DOP for the other 6 requires finding and downloading a covering Level-1A
SLC acquisition per candidate from PRADAN (authenticated, not attempted
here) -- flagged explicitly in the output, not fabricated.
"""

import json
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds as window_from_bounds

L4_DIR = r"C:\Users\radhe\PRISM_local_data\l4_mosaic"
L3C_DIR = r"C:\Users\radhe\PRISM_local_data\l3c_cpr"
PSR_SHP = r"C:\Users\radhe\PRISM_local_data\psr_south\LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL.shp"

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "paper_criterion")
os.makedirs(OUT_DIR, exist_ok=True)

SHORTLIST_IDS = [
    "SP_832640_0090770", "SP_830080_0535120", "SP_842420_0421060",
    "SP_817950_1586580", "SP_840980_0797630", "SP_819860_1568660",
    "SP_809570_2454450",
]

Y4R_PATHS = {
    L: os.path.join(L4_DIR, f"ch2_sar_ndxl_20250630my4rspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["evn", "vol", "odd", "hlx"]
}
CPR_PATHS = {
    L: os.path.join(L3C_DIR, f"ch2_sar_ndxl_20250630mpcpspwest_d_{L}_xx_fp_xx_xxx.tif")
    for L in ["cpr", "srd", "trt"]
}

# Real candidate-specific DOP, from src/candidate_dop_pipeline.py output
# (outputs/objective1/dop/candidate_dop.json) -- linear-pol (HH/VV) Stokes
# DOP, identical formula to the paper's Eq. 2. Real acquisition
# ch2_sar_ncxl_20220318t135736694_d_fp_d18, confirmed covering by true
# footprint corners + Grid CSV (91 m). NOT computed for the other 6.
KNOWN_DOP = {
    "SP_840980_0797630": {
        "dop_mean": 0.680, "dop_median": 0.708, "n_px": 488000, "pct_nan": 0.0,
        "source": "outputs/objective1/dop/candidate_dop.json (real, candidate-specific)",
        "note": "Window is a ~1x2.3km strip centered on the nearest confirmed Grid-CSV "
                "point, NOT restricted to the PSR polygon interior or to the elevated-CPR "
                "subset -- so this is not a strict apples-to-apples match to the paper's "
                "per-crater 'average DOP of the elevated-CPR region' statistic.",
    },
}


def read_full_res_window(path, bounds):
    with rasterio.open(path) as src:
        window = window_from_bounds(*bounds, transform=src.transform)
        arr = src.read(1, window=window)
        win_transform = src.window_transform(window)
    return arr.astype(np.float32), win_transform


def main():
    with rasterio.open(Y4R_PATHS["evn"]) as src:
        full_crs = src.crs

    psr = gpd.read_file(PSR_SHP).to_crs(full_crs)

    rows = []
    for psr_id in SHORTLIST_IDS:
        row = psr[psr.PSR_ID == psr_id].iloc[0]
        minx, miny, maxx, maxy = row.geometry.bounds
        buffer = 1000
        bounds = (minx - buffer, miny - buffer, maxx + buffer, maxy + buffer)

        evn_fr, tr = read_full_res_window(Y4R_PATHS["evn"], bounds)
        vol_fr, _ = read_full_res_window(Y4R_PATHS["vol"], bounds)
        odd_fr, _ = read_full_res_window(Y4R_PATHS["odd"], bounds)
        hlx_fr, _ = read_full_res_window(Y4R_PATHS["hlx"], bounds)
        cpr_fr, _ = read_full_res_window(CPR_PATHS["cpr"], bounds)
        srd_fr, _ = read_full_res_window(CPR_PATHS["srd"], bounds)
        trt_fr, _ = read_full_res_window(CPR_PATHS["trt"], bounds)

        total_fr = evn_fr + vol_fr + odd_fr + hlx_fr
        valid_pv = np.isfinite(total_fr) & (total_fr > 0)
        pv_fr = np.where(valid_pv, vol_fr / np.where(valid_pv, total_fr, np.nan), np.nan)

        psr_mask = geometry_mask([row.geometry], out_shape=evn_fr.shape, transform=tr, invert=True)

        valid_cpr = np.isfinite(cpr_fr) & (cpr_fr != 0)
        inside_cpr_mask = psr_mask & valid_cpr
        cpr_inside_vals = cpr_fr[inside_cpr_mask]

        valid_srd = np.isfinite(srd_fr)
        inside_srd = psr_mask & valid_srd
        valid_trt = np.isfinite(trt_fr) & (trt_fr != 0)
        inside_trt = psr_mask & valid_trt
        inside_pv = psr_mask & valid_pv

        elevated_mask_inside = inside_cpr_mask & (cpr_fr > 1)
        n_elevated = int(elevated_mask_inside.sum())
        n_cpr_inside = int(inside_cpr_mask.sum())

        dop_info = KNOWN_DOP.get(psr_id)

        rec = {
            "PSR_ID": psr_id,
            "lat": float(row.latitude), "lon": float(row.longitude),
            "area_km2": float(row.area),
            "n_valid_cpr_inside": n_cpr_inside,
            "pv_mean_inside": float(pv_fr[inside_pv].mean()) if inside_pv.sum() else np.nan,
            "cpr_mean_inside": float(cpr_inside_vals.mean()) if n_cpr_inside else np.nan,
            "cpr_max_inside": float(cpr_inside_vals.max()) if n_cpr_inside else np.nan,
            "cpr_pct_gt1_inside": round(100.0 * n_elevated / n_cpr_inside, 4) if n_cpr_inside else np.nan,
            "cpr_mean_of_elevated_gt1_inside": float(cpr_fr[elevated_mask_inside].mean()) if n_elevated else np.nan,
            "srd_mean_inside": float(srd_fr[inside_srd].mean()) if inside_srd.sum() else np.nan,
            "trt_mean_inside": float(trt_fr[inside_trt].mean()) if inside_trt.sum() else np.nan,
            "paper_criterion_1_cpr_gt1_present": bool(n_elevated > 0),
            "dop_mean": dop_info["dop_mean"] if dop_info else None,
            "dop_status": "REAL, candidate-specific" if dop_info else "NOT COMPUTED (no covering Level-1A SLC acquisition downloaded for this candidate yet)",
            "paper_criterion_2_dop_lt_0p13": (dop_info["dop_mean"] < 0.13) if dop_info else None,
            "meets_full_paper_criterion": (
                (n_elevated > 0) and dop_info is not None and dop_info["dop_mean"] < 0.13
            ) if dop_info is not None else None,
        }
        rows.append(rec)
        print(psr_id, {k: v for k, v in rec.items() if k not in ("PSR_ID",)})

    df = pd.DataFrame(rows).sort_values("cpr_pct_gt1_inside", ascending=False)
    out_csv = os.path.join(OUT_DIR, "seven_candidates_paper_criterion.csv")
    df.to_csv(out_csv, index=False)

    summary = {
        "paper": "Sinha et al. 2026, npj Space Exploration 2:22, doi:10.1038/s44453-026-00038-9",
        "paper_refined_criterion": "CPR > 1 (interior pixels) combined with DOP < 0.13 (Stokes-parameter degree of polarization) = strong evidence of volumetric scattering / subsurface ice",
        "important_scale_caveat": (
            "The paper's craters are small doubly-shadowed sub-features (700-3000 m diameter) inside "
            "larger PSRs (Faustini/Haworth/Shoemaker), with CPR/DOP averaged over the crater interior "
            "specifically. PRISM's 7 shortlisted candidates are themselves PSR-scale (9-43 km2) LOLA "
            "catalog polygons -- the interior CPR/DOP stats below are PSR-polygon averages, not a "
            "doubly-shadowed-crater-scale measurement. This is a genuine scale mismatch, stated not "
            "hidden -- applying the paper's threshold here is a reasonable but not literally validated "
            "extrapolation."
        ),
        "results": df.to_dict(orient="records"),
        "dop_availability": "Real, candidate-specific DOP exists for only 1 of 7 candidates (SP_840980_0797630). "
                             "The other 6 require downloading a covering Level-1A quad-pol SLC acquisition each "
                             "from PRADAN (authenticated ISSDC login required) -- not attempted in this run.",
        "headline_finding": None,
    }

    # headline: does ANY candidate currently satisfy the FULL paper criterion (both parts, real data)?
    full_pass = [r for r in rows if r["meets_full_paper_criterion"] is True]
    if full_pass:
        summary["headline_finding"] = f"{len(full_pass)} candidate(s) currently meet the FULL paper criterion (real CPR + real DOP): " + ", ".join(r["PSR_ID"] for r in full_pass)
    else:
        summary["headline_finding"] = "No candidate currently meets the FULL paper criterion with real data for both CPR and DOP -- either CPR>1 pixels are absent/negligible, DOP has not been computed yet, or (for the one candidate with real DOP) DOP fails the <0.13 threshold."

    with open(os.path.join(OUT_DIR, "seven_candidates_paper_criterion.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n" + json.dumps(summary["headline_finding"], indent=2))
    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
