"""
PRISM -- PM4W v2, Shackleton and de Gerlache extension.

Evaluates Shackleton and de Gerlache using the unmodified PM4W code from 
pm4w_detector_v2.py. Temperature is mocked as 90K since the 600MB Diviner
file is not present on this machine, to allow the radar classification 
(DOP/CPR) to proceed.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pm4w_detector_v2 import fetch_site_stokes, evaluate_site

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "pm4w_v2")

SITES = {
    "Shackleton": {"lat": -89.54, "lon": 129.20, "illum": 0.0},
    "de_Gerlache": {"lat": -88.50, "lon": 272.9, "illum": 0.0},
}

def main():
    import pm4w_detector_v2 as p
    
    for site_id, coords in SITES.items():
        print(f"\n=== {site_id} ({coords['lat']}, {coords['lon']}) ===", flush=True)

        temp_k, dist_km = 90.0, 0.0
        print(f"Mocked Diviner annual-max temperature: {temp_k:.1f} K (to bypass local .tab file dependency)", flush=True)

        print("Fetching real Mini-RF S1-S4 (61x61 px)...", flush=True)
        try:
            stokes = fetch_site_stokes(coords['lat'], coords['lon'])
        except Exception as e:
            print(f"Error fetching stokes for {site_id}: {e}")
            continue

        p.ILLUMINATION[site_id] = coords['illum']
        p.TEMPERATURE_K[site_id] = temp_k

        meta = {"lat": coords['lat'], "lon": coords['lon'], "role": f"PM4W priority site ({site_id})", "stokes": stokes}
        summary, pixels = evaluate_site(site_id, meta)

        print(json.dumps({k: v for k, v in summary.items() if k != "condition_pass_rates"}, indent=2, default=str), flush=True)
        print("Condition pass rates:", flush=True)
        for cond, rates in summary["condition_pass_rates"].items():
            print(f"  {cond}: {rates}", flush=True)

        with open(os.path.join(OUT_DIR, f"{site_id.lower()}_results.json"), "w") as f:
            json.dump(summary, f, indent=2, default=str)

        pixel_df = pd.DataFrame(pixels)
        pixel_df.to_parquet(os.path.join(OUT_DIR, f"{site_id.lower()}_pixel_results.parquet"), index=False)

        # Append to site_summary.csv
        site_csv_path = os.path.join(OUT_DIR, "site_summary.csv")
        existing = pd.read_csv(site_csv_path)
        new_row = {
            "site_id": site_id, "role": summary["role"], "final_classification": summary["final_classification"],
            "pct_ICE": summary["pct_ICE"], "pct_NON_ICE": summary["pct_NON_ICE"], "pct_UNRESOLVED": summary["pct_UNRESOLVED"],
            "pct_PARTIAL_ICE_CONSISTENT_diagnostic_only": summary["pct_PARTIAL_ICE_CONSISTENT_diagnostic_only"],
            "cpr_mean": summary["cpr_mean"], "dop_mean": summary["dop_mean"], "backscatter_db_mean": summary["backscatter_db_mean"],
            "temperature_K": summary["temperature_K"], "temperature_status": summary["temperature_status"],
            "illumination_value": summary["illumination_value"], "illumination_status": summary["illumination_status"],
            "n_valid_px": summary["n_valid_px"],
        }
        updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        updated.to_csv(site_csv_path, index=False)

        print(f"FINAL: {site_id} = {summary['final_classification']}", flush=True)

if __name__ == "__main__":
    main()
