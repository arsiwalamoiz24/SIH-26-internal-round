"""
PRISM -- PM4W v2, Faustini extension.

Imports the real, unmodified functions from src/pm4w_detector_v2.py
(fetch_site_stokes, evaluate_site, and the same threshold constants) and
runs them against Faustini -- a new data point, same code, same
thresholds, no tuning. Does NOT modify pm4w_detector_v2.py or any other
existing pipeline file.

Illumination: reused from src/ice_evidence_pipeline_v2.py's real,
already-validated SITES["Faustini"] value (PRISM's own LOLA cumulative
illumination model), not recomputed.

Temperature: parsed fresh from the already-downloaded Diviner PRP south
file (dlre_prp_south.tab, 604,800,210 bytes, confirmed present from the
prior session's real download), same nearest-mesh-centroid haversine
method already used for the other 9 sites.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pm4w_detector_v2 import (
    fetch_site_stokes, evaluate_site,
    CPR_THRESHOLD, DOP_THRESHOLD, BACKSCATTER_THRESHOLD_DB,
    TEMPERATURE_THRESHOLD_K, ILLUMINATION_THRESHOLD,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "pm4w_v2")

FAUSTINI_LAT, FAUSTINI_LON = -87.3, 77.0
FAUSTINI_ILLUM = 0.023  # real, from ice_evidence_pipeline_v2.py SITES["Faustini"]

DIVINER_PRP_PATH = r"C:\Users\sohan\AppData\Local\Temp\claude\D--SIH-SIH-26-internal-round\dd055cf7-d547-4492-bef2-d6f63016422f\scratchpad\dlre_prp_south.tab"


def real_diviner_temperature(lat, lon):
    """Same nearest-centroid haversine lookup used for the other 9 sites
    (diviner_extract.py), re-implemented here since that was a scratch
    script, not a repo module."""
    cols = ["tri1_x", "tri1_y", "tri1_z", "tri2_x", "tri2_y", "tri2_z",
            "tri3_x", "tri3_y", "tri3_z", "tri_clon", "tri_clat", "tri_calt",
            "temp_avg", "temp_max", "ice_depth"]
    print("Loading real Diviner PRP south file (~600MB, ~2.88M rows)...", flush=True)
    df = pd.read_csv(DIVINER_PRP_PATH, skiprows=1, names=cols,
                      usecols=["tri_clon", "tri_clat", "temp_max"])
    tlon = df["tri_clon"].to_numpy()
    tlat = df["tri_clat"].to_numpy()
    tlon_norm = np.where(tlon < 0, tlon + 360, tlon)
    lon_norm = lon + 360 if lon < 0 else lon
    R = 1737.4
    dlat = np.radians(tlat - lat)
    dlon = np.radians(tlon_norm - lon_norm)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat)) * np.cos(np.radians(tlat)) * np.sin(dlon / 2) ** 2
    dist_km = 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    idx = np.argmin(dist_km)
    return float(df["temp_max"].iloc[idx]), float(dist_km[idx])


def main():
    print(f"=== Faustini ({FAUSTINI_LAT}, {FAUSTINI_LON}) ===", flush=True)

    temp_k, dist_km = real_diviner_temperature(FAUSTINI_LAT, FAUSTINI_LON)
    print(f"Real Diviner annual-max temperature: {temp_k:.1f} K (nearest mesh centroid {dist_km:.3f} km away)", flush=True)

    print("Fetching real Mini-RF S1-S4 (61x61 px)...", flush=True)
    stokes = fetch_site_stokes(FAUSTINI_LAT, FAUSTINI_LON)

    # evaluate_site expects meta with lat/lon/role/stokes, and reads
    # module-level ILLUMINATION/TEMPERATURE_K dicts by site_id -- patch
    # those dicts (imported by reference) rather than modifying the file.
    import pm4w_detector_v2 as p
    p.ILLUMINATION["Faustini"] = FAUSTINI_ILLUM
    p.TEMPERATURE_K["Faustini"] = temp_k

    meta = {"lat": FAUSTINI_LAT, "lon": FAUSTINI_LON, "role": "M3-positive reference site (Li et al. 2018); PM4W's own paper flags Faustini for follow-up", "stokes": stokes}
    summary, pixels = evaluate_site("Faustini", meta)

    print(json.dumps({k: v for k, v in summary.items() if k != "condition_pass_rates"}, indent=2, default=str), flush=True)
    print("Condition pass rates:", flush=True)
    for cond, rates in summary["condition_pass_rates"].items():
        print(f"  {cond}: {rates}", flush=True)

    with open(os.path.join(OUT_DIR, "faustini_results.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    pixel_df = pd.DataFrame(pixels)
    pixel_df.to_parquet(os.path.join(OUT_DIR, "faustini_pixel_results.parquet"), index=False)

    # Append to the existing site_summary.csv (real, additive, does not
    # remove or alter the existing 9 rows)
    site_csv_path = os.path.join(OUT_DIR, "site_summary.csv")
    existing = pd.read_csv(site_csv_path)
    new_row = {
        "site_id": "Faustini", "role": summary["role"], "final_classification": summary["final_classification"],
        "pct_ICE": summary["pct_ICE"], "pct_NON_ICE": summary["pct_NON_ICE"], "pct_UNRESOLVED": summary["pct_UNRESOLVED"],
        "pct_PARTIAL_ICE_CONSISTENT_diagnostic_only": summary["pct_PARTIAL_ICE_CONSISTENT_diagnostic_only"],
        "cpr_mean": summary["cpr_mean"], "dop_mean": summary["dop_mean"], "backscatter_db_mean": summary["backscatter_db_mean"],
        "temperature_K": summary["temperature_K"], "temperature_status": summary["temperature_status"],
        "illumination_value": summary["illumination_value"], "illumination_status": summary["illumination_status"],
        "n_valid_px": summary["n_valid_px"],
    }
    updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
    updated.to_csv(site_csv_path, index=False)

    print(f"\nSaved: {OUT_DIR}/faustini_results.json, faustini_pixel_results.parquet; appended to site_summary.csv", flush=True)
    print(f"\nFINAL: Faustini = {summary['final_classification']}", flush=True)


if __name__ == "__main__":
    main()
