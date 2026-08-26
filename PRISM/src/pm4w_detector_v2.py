"""
PRISM -- PM4W detector V2: real Mini-RF native-instrument reproduction.

Supersedes NOTHING -- src/pm4w_detector.py (v1, DFSAR-analogue-only) is
left untouched. This is the first PM4W implementation using PM4W's own
native instrument (Mini-RF), not an ISRO/DFSAR analogue.

DATA SOURCES, ALL REAL, ALL ACTUALLY OPENED THIS INVESTIGATION:
  - Mini-RF S1,S2,S3,S4: NASA PDS LRO-L-MRFLRO-5-GLOBAL-MOSAIC-V1.0,
    128 PPD, real /vsicurl/ windowed reads (docs/MINIRF_DATA_ACQUISITION.md).
    CPR and M(DOP) bands independently re-derived from S1-S4 and verified
    to exactly match the archive's own precomputed cpr/m bands.
  - Diviner annual max temperature: NASA PDS LRO-L-DLRE-4-RDR-V1 Polar
    Resource Product (PRP), south, real full download (604,800,210 bytes,
    2,880,000 triangular mesh elements), nearest-centroid lookup per site
    (haversine, <0.26 km for every site).
  - Illumination: PRISM's own already-validated LOLA-DEM cumulative
    illumination model (src/terrain_algorithms.py, real values from
    src/ice_evidence_pipeline_v2.py's SITES dict).

METHODOLOGICAL HONESTY, PER EXPLICIT INSTRUCTION:
  - CPR/DOP/phase/backscatter are evaluated PER PIXEL on the real Mini-RF
    61x61 window (genuine spatial variation captured).
  - Illumination and temperature are SINGLE REAL VALUES per site (PRISM's
    illumination model and the nearest Diviner mesh triangle respectively)
    applied UNIFORMLY across that site's pixel grid -- this is a real,
    disclosed resolution-matching limitation (Diviner's mesh and PRISM's
    illumination model are not natively gridded at Mini-RF's pixel scale),
    not a fabrication of pixel-level variation that doesn't exist in the
    source data.
  - w (weighted power enhancement) and the m-chi/m-alpha volume-scattering
    decomposition are NO_DATA for every pixel, every site -- NOT estimated,
    NOT substituted. See docs/PM4W_VALIDATION_RESULTS.md for the full,
    literature-sourced explanation of why each is structurally unavailable
    (w requires a regional incidence-angle-dependent baseline model per
    Thompson, Ustinov & Heggy 2011, not a per-pixel quantity at all; the
    chi/alpha angle formulas feeding the decomposition are genuinely
    unresolved/conflicting in the two independent extraction passes of
    Wang et al. 2025 performed this investigation).
  - Fractal roughness (D_s1): NOT implemented -- PM4W's own paper states
    no PASS/FAIL threshold for this quantity exists anywhere in its
    accessible text (confirmed by 2 independent extraction passes), so
    computing D_s1 would produce a number with nothing to classify it
    against. NO_DATA, not a fabricated threshold.

NO THRESHOLD IN THIS FILE WAS TUNED. Every threshold is exactly as stated
in docs/PM4W_COMPLETE_METHOD_REPRODUCTION.md / docs/PM4W_VALIDATION_RESULTS.md,
transcribed from Wang et al. 2025, unchanged regardless of what result it
produces for any site.
"""

import json
import os

import numpy as np
import pandas as pd
import rasterio
from rasterio.env import Env
from rasterio.windows import Window
from pyproj import Transformer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "pm4w_v2")
os.makedirs(OUT_DIR, exist_ok=True)

BASE = "/vsicurl/https://pds-geosciences.wustl.edu/lro/lro-l-mrflro-5-global-mosaic-v1/lromrf_1001/data/128ppd/global_{band}_128ppd_simp_0c.lbl"
BANDS = ["s1", "s2", "s3", "s4"]
WIN_PX = 61

SITES = {
    "SP_840980_0797630": {"lat": -84.098, "lon": 79.764, "role": "PRISM candidate (primary)"},
    "SP_832640_0090770": {"lat": -83.264, "lon": 9.077, "role": "PRISM candidate"},
    "SP_830080_0535120": {"lat": -83.008, "lon": 53.512, "role": "PRISM candidate"},
    "SP_842420_0421060": {"lat": -84.242, "lon": 42.106, "role": "PRISM candidate"},
    "SP_817950_1586580": {"lat": -81.795, "lon": 158.658, "role": "PRISM candidate"},
    "SP_819860_1568660": {"lat": -81.986, "lon": 156.866, "role": "PRISM candidate"},
    "SP_809570_2454450": {"lat": -80.957, "lon": 245.445, "role": "PRISM candidate"},
    "LCROSS_Cabeus": {"lat": -84.6796, "lon": -48.7093, "role": "POSITIVE CONTROL (LCROSS)"},
    "Wiechert": {"lat": -84.5, "lon": 165.0, "role": "NEGATIVE CONTROL (M3)"},
}

# Real illumination fraction, PRISM's own LOLA-illumination model
# (src/ice_evidence_pipeline_v2.py SITES dict / shortlist_hazard_summary.csv)
ILLUMINATION = {
    "SP_840980_0797630": 0.0, "SP_832640_0090770": 0.0, "SP_830080_0535120": 0.0,
    "SP_842420_0421060": 0.0, "SP_817950_1586580": 0.0, "SP_819860_1568660": 0.0,
    "SP_809570_2454450": 0.0, "LCROSS_Cabeus": 0.0022422, "Wiechert": 0.0531030,
}

# Real Diviner annual-max temperature, nearest mesh-triangle centroid
# (this session's own dlre_prp_south.tab extraction; distances all <0.26 km)
TEMPERATURE_K = {
    "SP_840980_0797630": 84.3, "SP_832640_0090770": 135.0, "SP_830080_0535120": 156.7,
    "SP_842420_0421060": 134.1, "SP_817950_1586580": 118.9, "SP_819860_1568660": 102.7,
    "SP_809570_2454450": 144.3, "LCROSS_Cabeus": 45.8, "Wiechert": 267.2,
}

CPR_THRESHOLD = 1.0
DOP_THRESHOLD = 0.2
BACKSCATTER_THRESHOLD_DB = -15.0
TEMPERATURE_THRESHOLD_K = 110.0
ILLUMINATION_THRESHOLD = 0.2


def is_nodata(arr):
    return ~np.isfinite(arr) | (arr <= -3.0e38)


def fetch_site_stokes(lat, lon):
    geog_crs = "+proj=longlat +R=1737400 +no_defs"
    out = {}
    with Env(GDAL_HTTP_TIMEOUT=30, GDAL_HTTP_CONNECTTIMEOUT=15,
             CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".lbl,.img", GDAL_DISABLE_READDIR_ON_OPEN="YES"):
        for band in BANDS:
            with rasterio.open(BASE.format(band=band)) as src:
                if band == BANDS[0]:
                    fwd = Transformer.from_crs(geog_crs, src.crs, always_xy=True)
                    x, y = fwd.transform(lon, lat)
                    col, row = ~src.transform * (x, y)
                    col, row = int(round(col)), int(round(row))
                    c0, r0 = max(0, col - WIN_PX // 2), max(0, row - WIN_PX // 2)
                w = min(WIN_PX, src.width - c0)
                h = min(WIN_PX, src.height - r0)
                out[band] = src.read(1, window=Window(c0, r0, w, h)).astype(np.float64)
    return out


def evaluate_site(site_id, meta):
    S1, S2, S3, S4 = (meta["stokes"][b] for b in BANDS)
    nodata = is_nodata(S1) | is_nodata(S2) | is_nodata(S3) | is_nodata(S4)
    valid = ~nodata
    shape = S1.shape

    with np.errstate(divide="ignore", invalid="ignore"):
        cpr = (S1 - S4) / (S1 + S4)
        dop_m = np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1
        phase_deg = np.degrees(np.arctan2(S4, S3)) % 360
        sigma_lh_lin = (S1 + S2) / 2.0
        sigma_lh_db = 10.0 * np.log10(np.where(sigma_lh_lin > 0, sigma_lh_lin, np.nan))

    def cond_array(pass_mask):
        """PASS where valid&pass, FAIL where valid&~pass, NO_DATA where ~valid."""
        arr = np.full(shape, "NO_DATA", dtype=object)
        arr[valid & pass_mask] = "PASS"
        arr[valid & ~pass_mask] = "FAIL"
        return arr

    cpr_cond = cond_array(cpr > CPR_THRESHOLD)
    dop_cond = cond_array(dop_m < DOP_THRESHOLD)
    backscatter_cond = cond_array(sigma_lh_db < BACKSCATTER_THRESHOLD_DB)
    phase_pass = ((phase_deg > 0) & (phase_deg < 80)) | ((phase_deg > 100) & (phase_deg < 180))
    phase_cond = cond_array(phase_pass)

    # Site-level, real, uniform across the grid (see module docstring)
    illum_val = ILLUMINATION[site_id]
    temp_val = TEMPERATURE_K[site_id]
    illum_status = "PASS" if illum_val < ILLUMINATION_THRESHOLD else "FAIL"
    temp_status = "PASS" if temp_val < TEMPERATURE_THRESHOLD_K else "FAIL"
    illum_cond = np.full(shape, illum_status, dtype=object)
    temp_cond = np.full(shape, temp_status, dtype=object)

    w_cond = np.full(shape, "NO_DATA", dtype=object)
    volume_cond = np.full(shape, "NO_DATA", dtype=object)
    roughness_cond = np.full(shape, "NO_DATA", dtype=object)

    all_conditions = {
        "cpr": cpr_cond, "dop": dop_cond, "backscatter": backscatter_cond, "phase": phase_cond,
        "weighted_power": w_cond, "volume_scattering": volume_cond, "roughness": roughness_cond,
        "temperature": temp_cond, "illumination": illum_cond,
    }

    classification = np.full(shape, "ICE", dtype=object)
    for name, arr in all_conditions.items():
        classification = np.where(arr == "FAIL", "NON_ICE", classification)
    any_nodata = np.zeros(shape, dtype=bool)
    for name, arr in all_conditions.items():
        any_nodata |= (arr == "NO_DATA")
    classification = np.where((classification != "NON_ICE") & any_nodata, "UNRESOLVED", classification)
    classification[~valid] = "NO_DATA_PIXEL"

    # Diagnostic-only partial AND-gate: real-data conditions only (cpr, dop,
    # backscatter, phase, temperature, illumination) -- excludes the 3
    # structurally-NO_DATA conditions, so it CAN resolve to a real ICE-like
    # result. Explicitly labeled diagnostic, never presented as the official
    # PM4W classification, per the module docstring.
    partial_classification = np.full(shape, "PARTIAL_ICE_CONSISTENT", dtype=object)
    for name in ["cpr", "dop", "backscatter", "phase", "temperature", "illumination"]:
        partial_classification = np.where(all_conditions[name] == "FAIL", "PARTIAL_NON_ICE", partial_classification)
    partial_classification[~valid] = "NO_DATA_PIXEL"

    n_valid = int(valid.sum())
    n_total = int(S1.size)
    n_ice = int((classification == "ICE").sum())
    n_non_ice = int((classification == "NON_ICE").sum())
    n_unresolved = int((classification == "UNRESOLVED").sum())
    n_partial_ice = int((partial_classification == "PARTIAL_ICE_CONSISTENT").sum())

    def rate(arr):
        vals, counts = np.unique(arr[valid], return_counts=True)
        return {v: int(c) for v, c in zip(vals, counts)}

    summary = {
        "site_id": site_id, "role": meta["role"],
        "illumination_value": illum_val, "illumination_status": illum_status,
        "temperature_K": temp_val, "temperature_status": temp_status,
        "n_total_px": n_total, "n_valid_px": n_valid,
        "n_ICE": n_ice, "n_NON_ICE": n_non_ice, "n_UNRESOLVED": n_unresolved,
        "pct_ICE": round(100 * n_ice / n_valid, 3) if n_valid else None,
        "pct_NON_ICE": round(100 * n_non_ice / n_valid, 3) if n_valid else None,
        "pct_UNRESOLVED": round(100 * n_unresolved / n_valid, 3) if n_valid else None,
        "n_PARTIAL_ICE_CONSISTENT_diagnostic_only": n_partial_ice,
        "pct_PARTIAL_ICE_CONSISTENT_diagnostic_only": round(100 * n_partial_ice / n_valid, 3) if n_valid else None,
        "condition_pass_rates": {name: rate(arr) for name, arr in all_conditions.items()},
        "cpr_mean": float(cpr[valid].mean()), "cpr_median": float(np.median(cpr[valid])),
        "dop_mean": float(dop_m[valid].mean()), "dop_median": float(np.median(dop_m[valid])),
        "backscatter_db_mean": float(np.nanmean(sigma_lh_db[valid])),
        "final_classification": "NON_ICE" if n_non_ice == n_valid else ("UNRESOLVED" if n_unresolved > 0 or n_ice == 0 else "ICE"),
    }
    pixel_records = []
    rows, cols = np.indices(shape)
    for r, c in zip(rows.ravel(), cols.ravel()):
        if not valid[r, c]:
            continue
        pixel_records.append({
            "site_id": site_id, "row": int(r), "col": int(c),
            "cpr": float(cpr[r, c]), "dop": float(dop_m[r, c]),
            "phase_deg": float(phase_deg[r, c]), "backscatter_db": float(sigma_lh_db[r, c]),
            "cpr_status": cpr_cond[r, c], "dop_status": dop_cond[r, c],
            "phase_status": phase_cond[r, c], "backscatter_status": backscatter_cond[r, c],
            "weighted_power_status": "NO_DATA", "volume_scattering_status": "NO_DATA", "roughness_status": "NO_DATA",
            "temperature_status": temp_status, "illumination_status": illum_status,
            "final_classification": classification[r, c],
            "partial_diagnostic_classification": partial_classification[r, c],
        })
    return summary, pixel_records


def main():
    print("Fetching real Mini-RF S1-S4 for all 9 sites (61x61 px each)...", flush=True)
    all_summaries, all_pixels = [], []
    for site_id, meta in SITES.items():
        print(f"  {site_id}...", flush=True)
        meta["stokes"] = fetch_site_stokes(meta["lat"], meta["lon"])
        summary, pixels = evaluate_site(site_id, meta)
        all_summaries.append(summary)
        all_pixels.extend(pixels)
        print(f"    -> final={summary['final_classification']}  ICE={summary['pct_ICE']}%  "
              f"NON_ICE={summary['pct_NON_ICE']}%  UNRESOLVED={summary['pct_UNRESOLVED']}%  "
              f"(diagnostic partial-ICE-consistent={summary['pct_PARTIAL_ICE_CONSISTENT_diagnostic_only']}%)", flush=True)

    with open(os.path.join(OUT_DIR, "pm4w_results.json"), "w") as f:
        json.dump(all_summaries, f, indent=2, default=str)

    pixel_df = pd.DataFrame(all_pixels)
    pixel_df.to_parquet(os.path.join(OUT_DIR, "pm4w_pixel_results.parquet"), index=False)

    site_df = pd.DataFrame(all_summaries)
    cols = ["site_id", "role", "final_classification", "pct_ICE", "pct_NON_ICE", "pct_UNRESOLVED",
            "pct_PARTIAL_ICE_CONSISTENT_diagnostic_only", "cpr_mean", "dop_mean", "backscatter_db_mean",
            "temperature_K", "temperature_status", "illumination_value", "illumination_status", "n_valid_px"]
    site_df[cols].to_csv(os.path.join(OUT_DIR, "site_summary.csv"), index=False)

    print(f"\nSaved: {OUT_DIR}/pm4w_results.json, pm4w_pixel_results.parquet, site_summary.csv", flush=True)


if __name__ == "__main__":
    main()
