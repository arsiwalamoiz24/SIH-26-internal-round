"""PRISM_NEXT_PHASE_PLAN.md Phase 2 deliverable -- the Diviner thermal gate.

Per Li et al. 2018's cold-trap criterion, water ice is only
thermodynamically plausible below ~110 K. This module applies that as a
hard PASS/FAIL/NO_DATA gate per site, using a fresh re-extraction from
the re-acquired dlre_prp_south.tab (docs/DIVINER_DATA_ACQUISITION.md),
independent of the hardcoded TEMPERATURE_K dict in pm4w_detector_v2.py.

Does NOT modify pm4w_detector_v2.py or pm4w_faustini_extension.py --
this is a separate, standalone Phase-2 consumer that happens to reuse
the same threshold and coordinates ("Supersedes NOTHING").
"""
import json
import os
from datetime import datetime, timezone

import pandas as pd

from diviner_extract import load_diviner_prp, batch_lookup, resolve_diviner_path

# Duplicated-with-comment from pm4w_detector_v2.py line 101 -- not imported,
# since importing that module would pull in rasterio/pyproj as hard
# dependencies of a thermal-only script.
TEMPERATURE_THRESHOLD_K = 110.0

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(REPO, "PRISM", "outputs", "objective1", "thermal_gate")

# 7 PRISM candidates (src/radar_pipeline.py SHORTLIST_IDS coordinates, as
# used consistently across pm4w_detector_v2.py's SITES dict) + Faustini +
# Cabeus (canonical PSR-ID centroid coordinates) + Wiechert (bonus
# negative control, outside Phase 2's formal 9-site scope).
SITES = {
    "SP_840980_0797630": {"lat": -84.098, "lon": 79.764, "role": "PRISM candidate (primary)"},
    "SP_832640_0090770": {"lat": -83.264, "lon": 9.077, "role": "PRISM candidate"},
    "SP_830080_0535120": {"lat": -83.008, "lon": 53.512, "role": "PRISM candidate"},
    "SP_842420_0421060": {"lat": -84.242, "lon": 42.106, "role": "PRISM candidate"},
    "SP_817950_1586580": {"lat": -81.795, "lon": 158.658, "role": "PRISM candidate"},
    "SP_819860_1568660": {"lat": -81.986, "lon": 156.866, "role": "PRISM candidate"},
    "SP_809570_2454450": {"lat": -80.957, "lon": 245.445, "role": "PRISM candidate"},
    "Faustini": {"lat": -87.146, "lon": 84.075, "role": "M3-positive reference (Sinha et al. 2026), canonical PSR-ID centroid"},
    "LCROSS_Cabeus": {"lat": -84.458, "lon": -46.568, "role": "POSITIVE CONTROL (LCROSS), canonical PSR-ID centroid"},
    "Wiechert": {"lat": -84.5, "lon": 165.0, "role": "NEGATIVE CONTROL (M3), bonus -- outside Phase 2's formal 9-site scope"},
}

# Existing hardcoded values this module is validated against (never
# overwritten by this script -- read-only comparison targets).
EXISTING_TEMPERATURE_K = {
    "SP_840980_0797630": 84.3, "SP_832640_0090770": 135.0, "SP_830080_0535120": 156.7,
    "SP_842420_0421060": 134.1, "SP_817950_1586580": 118.9, "SP_819860_1568660": 102.7,
    "SP_809570_2454450": 144.3, "LCROSS_Cabeus": 45.8, "Wiechert": 267.2,
    "Faustini": 51.833,
}
EXISTING_SOURCE_FILE = {
    site: ("outputs/objective1/pm4w_v2/faustini_results.json" if site == "Faustini"
           else "outputs/objective1/pm4w_v2/site_summary.csv")
    for site in EXISTING_TEMPERATURE_K
}

# Legacy ad hoc coordinates that actually produced the existing
# 51.833K / 45.8K values (distinct from the canonical PSR-ID centroids
# above) -- see pm4w_faustini_extension.py FAUSTINI_LAT/LON and
# pm4w_detector_v2.py SITES["LCROSS_Cabeus"].
LEGACY_COORDS = {
    "Faustini": {"lat": -87.3, "lon": 77.0, "provenance": "legacy_pm4w_v2_faustini_adhoc"},
    "LCROSS_Cabeus": {"lat": -84.6796, "lon": -48.7093, "provenance": "legacy_pm4w_v2_lcross_impact_point"},
}

DISTANCE_BOUND_KM = 0.26
MATCH_TOLERANCE_K = 0.05


def gate_status(temp_max_k, threshold=TEMPERATURE_THRESHOLD_K) -> str:
    if temp_max_k is None:
        return "NO_DATA"
    return "PASS" if temp_max_k < threshold else "FAIL"


def rationale(site_id, temp_max_k, distance_km, status) -> str:
    if status == "NO_DATA":
        return (
            f"{site_id}: Diviner temperature unavailable -- see "
            "docs/DIVINER_DATA_ACQUISITION.md and run src/acquire_diviner_prp.py."
        )
    verdict = "below" if status == "PASS" else "at/above"
    return (
        f"{site_id}: Tmax={temp_max_k:.1f}K is {verdict} the "
        f"{TEMPERATURE_THRESHOLD_K:.0f}K cold-trap threshold (Li et al. 2018) "
        f"-> {status}. Nearest Diviner mesh centroid {distance_km:.3f} km away."
    )


def _cross_check_threshold():
    """Optional, lazy cross-check against pm4w_detector_v2.py's own
    threshold constant, to catch drift without forcing rasterio/pyproj
    as hard dependencies of this thermal-only script."""
    try:
        import pm4w_detector_v2 as p
        assert p.TEMPERATURE_THRESHOLD_K == TEMPERATURE_THRESHOLD_K, (
            f"Threshold drift: pm4w_detector_v2.py has "
            f"{p.TEMPERATURE_THRESHOLD_K}, thermal_gate_pipeline.py has "
            f"{TEMPERATURE_THRESHOLD_K}"
        )
    except ImportError:
        pass


def run():
    _cross_check_threshold()
    os.makedirs(OUT_DIR, exist_ok=True)

    diviner_path = resolve_diviner_path()
    print(f"Loading Diviner PRP from {diviner_path} ...", flush=True)
    df = load_diviner_prp(diviner_path)
    print(f"Loaded {len(df):,} mesh rows.", flush=True)

    now = datetime.now(timezone.utc).isoformat()

    # --- site_summary.csv / thermal_gate_results.json --------------------
    lookup = batch_lookup(df, SITES)
    records = []
    for site_id, meta in SITES.items():
        r = lookup[site_id]
        status = gate_status(r["temp_max_K"])
        rec = {
            "site_id": site_id,
            "role": meta["role"],
            "lat_deg": meta["lat"],
            "lon_deg": meta["lon"],
            "temp_max_K": r["temp_max_K"] if r["temp_max_K"] is not None else "NO_DATA",
            "temperature_threshold_K": TEMPERATURE_THRESHOLD_K,
            "distance_to_nearest_centroid_km": r["distance_km"] if r["distance_km"] is not None else "NO_DATA",
            "n_mesh_rows_searched": r["n_mesh_rows"],
            "gate_status": status,
            "rationale": rationale(site_id, r["temp_max_K"], r["distance_km"], status),
            "source_product": "LRO-L-DLRE-4-RDR-V1 (Polar Resource Product, south)",
            "source_file": "data/raw/diviner/dlre_prp_south.tab",
            "extracted_at_utc": now,
        }
        records.append(rec)

    site_summary = pd.DataFrame(records)
    site_summary_path = os.path.join(OUT_DIR, "site_summary.csv")
    site_summary.to_csv(site_summary_path, index=False)

    results_json_path = os.path.join(OUT_DIR, "thermal_gate_results.json")
    with open(results_json_path, "w") as f:
        json.dump(records, f, indent=2, default=str)

    print(f"Wrote {site_summary_path}", flush=True)
    print(f"Wrote {results_json_path}", flush=True)

    # --- cross_validation.csv ---------------------------------------------
    cv_sites = {}
    for site_id, meta in SITES.items():
        cv_sites[(site_id, "canonical_site_id")] = {"lat": meta["lat"], "lon": meta["lon"]}
    for site_id, legacy in LEGACY_COORDS.items():
        cv_sites[(site_id, legacy["provenance"])] = {"lat": legacy["lat"], "lon": legacy["lon"]}

    cv_lookup_input = {f"{sid}|||{prov}": coords for (sid, prov), coords in cv_sites.items()}
    cv_lookup = batch_lookup(df, cv_lookup_input)

    cv_records = []
    for (site_id, provenance), coords in cv_sites.items():
        key = f"{site_id}|||{provenance}"
        r = cv_lookup[key]
        new_temp = r["temp_max_K"]
        new_status = gate_status(new_temp)
        existing_temp = EXISTING_TEMPERATURE_K.get(site_id)
        existing_status = gate_status(existing_temp) if existing_temp is not None else "NO_DATA"
        delta = (new_temp - existing_temp) if (new_temp is not None and existing_temp is not None) else None

        if provenance == "canonical_site_id" and site_id in LEGACY_COORDS:
            note = "Canonical PSR-ID centroid differs from the legacy ad hoc coordinate that produced the existing value -- delta expected, not a bug."
            match = "N/A (different coordinate, see note)"
        else:
            is_match = delta is not None and abs(delta) <= MATCH_TOLERANCE_K
            match = "MATCH" if is_match else "DISCREPANCY — investigate"
            note = ""
            if r["distance_km"] is not None and r["distance_km"] >= DISTANCE_BOUND_KM:
                note = f"distance_km={r['distance_km']:.3f} >= {DISTANCE_BOUND_KM} bound -- flagged"

        cv_records.append({
            "site_id": site_id,
            "lookup_lat": coords["lat"],
            "lookup_lon": coords["lon"],
            "coord_provenance": provenance,
            "new_temp_max_K": new_temp if new_temp is not None else "NO_DATA",
            "new_gate_status": new_status,
            "existing_temp_max_K": existing_temp if existing_temp is not None else "NO_DATA",
            "existing_temperature_status": existing_status,
            "existing_source_file": EXISTING_SOURCE_FILE.get(site_id, ""),
            "delta_K": delta if delta is not None else "NO_DATA",
            "match": match,
            "note": note,
        })

    cross_validation = pd.DataFrame(cv_records)
    cv_path = os.path.join(OUT_DIR, "cross_validation.csv")
    cross_validation.to_csv(cv_path, index=False)
    print(f"Wrote {cv_path}", flush=True)

    return site_summary, cross_validation


if __name__ == "__main__":
    run()
