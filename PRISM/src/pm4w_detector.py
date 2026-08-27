"""
PRISM -- PM4W detector (Wang et al. 2025 reproduction, feasible components only).

Reproduces ONLY the PM4W conditions that docs/PM4W_COMPLETE_METHOD_
REPRODUCTION.md's audit established can be evaluated with data PRISM
actually has -- illumination and a CPR>1-fraction ANALOGUE. Every other
PM4W condition (DOP, backscatter, phase, weighted power, volume-scattering
decomposition, fractal roughness, temperature) is reported as NO_DATA,
never estimated, never substituted from a different instrument's data.

CRITICAL DISTINCTION, per explicit instruction: PRISM's CPR (an ISRO
L3C-MOSAIC precomputed band of undocumented formula) is NEVER called
"PM4W CPR." PM4W's own CPR is a Stokes (S1-S4)/(S1+S4) construction from
Mini-RF's hardware-correct hybrid-pol receive pair (docs/DFSAR_
POLARIMETRIC_CHANNEL_AUDIT.md Sec 5). PRISM has no Mini-RF data ingested
anywhere -- see docs/PM4W_DATA_REQUIREMENTS.md for what would be needed.
Every condition below carries explicit `source_method`, `instrument`,
`formula`, and `comparability` (DIRECT / ANALOGUE / NOT_COMPARABLE)
metadata for exactly this reason.

METHODOLOGICAL HYGIENE (task-required): `classify_site()` takes ONLY
measured physical quantities as input -- no site identity, no "is this a
known positive/negative control" flag. Ground-truth labels (LCROSS, M3)
are attached SEPARATELY, only for reporting/validation purposes, never fed
into the classifier itself. This is enforced by the function signature
below, not just a comment.
"""

import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "pm4w")
os.makedirs(OUT_DIR, exist_ok=True)

ILLUMINATION_THRESHOLD = 0.2  # PM4W's own stated threshold, Wang et al. 2025


def evaluate_illumination(illum_fraction):
    """PM4W condition: annual average illumination < 0.2.
    source_method=PM4W, instrument=LOLA-illumination-model (PRISM's own
    ray-casting implementation, terrain_algorithms.compute_cumulative_
    illumination -- NOT verified identical to whichever illumination model
    PM4W's own paper used, but both are LOLA-DEM-derived cumulative
    sun-position models, the closest real analogue PRISM has).
    comparability=ANALOGUE (same physical quantity, independently
    implemented, not verified formula-identical to PM4W's own)."""
    meta = {
        "source_method": "PM4W", "instrument": "PRISM/LOLA-DEM illumination model (src/terrain_algorithms.py)",
        "formula": "PM4W: annual average illumination < 0.2 (their stated threshold). PRISM: fraction of 24 simulated sun positions (8 azimuths x 3 elevations) illuminated, terrain_algorithms.compute_cumulative_illumination -- an independently-implemented LOLA-DEM ray-casting model, not verified identical to PM4W's own illumination product.",
        "comparability": "ANALOGUE",
    }
    if illum_fraction is None:
        return {"condition": "illumination", "status": "NO_DATA", "value": None, **meta}
    status = "PASS" if illum_fraction < ILLUMINATION_THRESHOLD else "FAIL"
    return {"condition": "illumination", "status": status, "value": illum_fraction, "threshold": ILLUMINATION_THRESHOLD, **meta}


def evaluate_cpr_fraction_analogue(cpr_pct_gt1_inside):
    """PM4W condition: per-pixel CPR>1 (Stokes-based). PRISM ANALOGUE: does
    the ISRO L3C-MOSAIC CPR band (undocumented formula) contain ANY
    interior pixel exceeding CPR>1? PASS if pct_gt1_inside > 0 -- this
    aggregation convention (any qualifying pixel exists) is chosen because
    PM4W's own decision unit is per-pixel, not a site-level fraction
    threshold; no numeric fraction cutoff is invented here beyond ">0".
    comparability=ANALOGUE, NEVER "DIRECT" -- see module docstring and
    docs/PM4W_SINHA_PRISM_COMPARISON.md Sec 2 for why PRISM's CPR formula
    is not verified equivalent to PM4W's Stokes CPR."""
    meta = {
        "source_method": "PM4W (analogue only)", "instrument": "ISRO Chandrayaan-2 DFSAR L3C-MOSAIC (precomputed CPR band, formula undocumented)",
        "formula": "PM4W: per-pixel C=(S1-S4)/(S1+S4) > 1. PRISM analogue: >0% of interior pixels in the ISRO L3C-MOSAIC CPR band exceed 1.0 -- NOT the same formula, NOT verified equivalent, reported as an analogue statistic only.",
        "comparability": "ANALOGUE",
    }
    if cpr_pct_gt1_inside is None:
        return {"condition": "cpr", "status": "NO_DATA", "value": None, **meta}
    status = "PASS" if cpr_pct_gt1_inside > 0 else "FAIL"
    return {"condition": "cpr", "status": status, "value": cpr_pct_gt1_inside, **meta}


def _no_data(condition, required_instrument, formula, note):
    return {
        "condition": condition, "status": "NO_DATA", "value": None,
        "source_method": "PM4W", "instrument": required_instrument, "formula": formula,
        "comparability": "NOT_COMPARABLE", "note": note,
    }


def evaluate_dop():
    return _no_data(
        "dop", "Mini-RF (not ingested by PRISM)",
        "PM4W: m=sqrt(S2^2+S3^2+S4^2)/S1 < 0.2, from Mini-RF's hybrid-pol Stokes vector.",
        "PRISM has DFSAR-derived DOP for some sites (quad-pol HH/VV basis), but this is a DIFFERENT instrument and a DIFFERENT physical basis (linear-transmit quad-pol vs circular-transmit hybrid-pol) -- reported separately in src/dfsar_ice_evidence.py's DFSAR_ICE_EVIDENCE output, never substituted here.",
    )


def evaluate_backscatter():
    return _no_data(
        "backscatter", "Mini-RF (not ingested by PRISM)",
        "PM4W: sigma_LH = (S1+S2)/2 < -15 dB.",
        "PRISM's Y4R total power (evn+vol+odd+hlx) is theoretically convertible to dB, but this has never been demonstrated physically comparable to Mini-RF's own LH-channel radiometric scale (docs/PM4W_COMPLETE_METHOD_REPRODUCTION.md Sec 4) -- per explicit task instruction, not implemented as a real PASS/FAIL test until that comparability is established.",
    )


def evaluate_phase():
    return _no_data("phase", "Mini-RF (not ingested by PRISM)", "PM4W: delta=arctan(S4/S3), 0-80 or 100-180 deg.", "Requires genuine complex S3,S4 from Mini-RF's own Stokes vector -- no such data ingested.")


def evaluate_weighted_power():
    return _no_data("weighted_power", "Mini-RF (not ingested by PRISM)", "PM4W: w=0.12*alpha+0.88*gamma, 0.5-1.0.", "alpha/gamma terms remain unresolved from the source paper itself (docs/PM4W_COMPLETE_METHOD_REPRODUCTION.md Sec 1.6) -- scientifically unresolved, not just missing data.")


def evaluate_volume_scattering():
    return _no_data("volume_scattering", "Mini-RF (not ingested by PRISM)", "PM4W Eq 7: V_G > D_R + S_B (m-chi and m-alpha decompositions).", "Requires the same Mini-RF Stokes vector as DOP/CPR/phase -- not available.")


def evaluate_roughness():
    return _no_data("roughness", "Mini-RF S1 backscatter imagery (not ingested by PRISM)", "PM4W Eq 4: fractal dimension D_s1, 9x9 window on radar backscatter intensity (NOT a DEM roughness metric).", "PRISM's own roughness (terrain_algorithms.compute_roughness_rms) is DEM-elevation-derived -- a categorically different metric in a different domain. Not substituted here.")


def evaluate_temperature():
    return _no_data("temperature", "Diviner (not ingested by PRISM)", "PM4W: annual maximum temperature < 110 K.", "No per-site Diviner temperature data has been ingested by PRISM anywhere (confirmed repeatedly across this investigation).")


def classify_site(*, illum_fraction=None, cpr_pct_gt1_inside=None):
    """Pure function of measured physical quantities only -- no site
    identity, no ground-truth label as an input, per explicit task
    instruction (Task 6)."""
    conditions = {
        "illumination": evaluate_illumination(illum_fraction),
        "cpr": evaluate_cpr_fraction_analogue(cpr_pct_gt1_inside),
        "dop": evaluate_dop(),
        "backscatter": evaluate_backscatter(),
        "phase": evaluate_phase(),
        "weighted_power": evaluate_weighted_power(),
        "volume_scattering": evaluate_volume_scattering(),
        "roughness": evaluate_roughness(),
        "temperature": evaluate_temperature(),
    }
    statuses = {k: v["status"] for k, v in conditions.items()}
    if "FAIL" in statuses.values():
        classification = "NON_ICE"
        reason = f"At least one evaluated condition FAILed: {[k for k,v in statuses.items() if v=='FAIL']}. An AND-gate is violated regardless of other conditions' status."
    elif "NO_DATA" in statuses.values():
        classification = "UNRESOLVED"
        reason = f"No condition FAILed, but required condition(s) are NO_DATA: {[k for k,v in statuses.items() if v=='NO_DATA']}. Per explicit instruction, a site is never classified ICE while any required condition is unresolved."
    else:
        classification = "ICE"
        reason = "All evaluated conditions PASS and no condition is NO_DATA."
    return {"pm4w_conditions": conditions, "classification": classification, "reason": reason}


# ---------------------------------------------------------------------------
# Real, already-computed PRISM inputs (illumination fraction, CPR>1 fraction
# where available) for every site this investigation has touched. Sourced
# exactly as in ice_evidence_pipeline_v2.py -- not re-derived, not estimated.
# Ground-truth labels are attached SEPARATELY (ground_truth key) and are
# NEVER passed into classify_site().
# ---------------------------------------------------------------------------

SITES = {
    "SP_840980_0797630": {"illum_fraction": 0.0, "cpr_pct_gt1_inside": 7.3257, "ground_truth": "NONE (no independent evidence, PRISM candidate)"},
    "SP_832640_0090770": {"illum_fraction": 0.0, "cpr_pct_gt1_inside": 10.792, "ground_truth": "NONE"},
    "SP_830080_0535120": {"illum_fraction": 0.0, "cpr_pct_gt1_inside": 7.2185, "ground_truth": "NONE"},
    "SP_842420_0421060": {"illum_fraction": 0.0, "cpr_pct_gt1_inside": 0.140, "ground_truth": "NONE"},
    "SP_817950_1586580": {"illum_fraction": 0.0, "cpr_pct_gt1_inside": 0.00387, "ground_truth": "NONE"},
    "SP_819860_1568660": {"illum_fraction": 0.0, "cpr_pct_gt1_inside": 10.4116, "ground_truth": "NONE"},
    "SP_809570_2454450": {"illum_fraction": 0.0, "cpr_pct_gt1_inside": 0.0951, "ground_truth": "NONE"},
    "LCROSS_Cabeus": {"illum_fraction": 0.0022422, "cpr_pct_gt1_inside": None, "ground_truth": "POSITIVE (LCROSS direct water detection, Colaprete et al. 2010)"},
    "Wiechert": {"illum_fraction": 0.0531030, "cpr_pct_gt1_inside": None, "ground_truth": "NEGATIVE (M3 explicit non-detection, Li et al. 2018)"},
    "Faustini": {"illum_fraction": 0.023, "cpr_pct_gt1_inside": None, "ground_truth": "POSITIVE (M3); PM4W's own paper also flags Faustini for follow-up"},
    "De_Gerlache": {"illum_fraction": 0.0383, "cpr_pct_gt1_inside": None, "ground_truth": "POSITIVE (M3); PM4W's own paper also flags de Gerlache for follow-up"},
    "Haworth": {"illum_fraction": 0.126, "cpr_pct_gt1_inside": None, "ground_truth": "POSITIVE (M3)"},
    "Shoemaker": {"illum_fraction": 0.0015, "cpr_pct_gt1_inside": None, "ground_truth": "POSITIVE (M3)"},
    "Sverdrup": {"illum_fraction": 0.0047, "cpr_pct_gt1_inside": None, "ground_truth": "POSITIVE (M3)"},
    "Shackleton": {"illum_fraction": 0.0011, "cpr_pct_gt1_inside": None, "ground_truth": "POSITIVE (M3); PM4W's OWN paper reports its best M3 agreement (62% pixel/29% area) at this exact site"},
    "Amundsen": {"illum_fraction": 0.007, "cpr_pct_gt1_inside": None, "ground_truth": "NEGATIVE (M3), CONTESTED by Brown et al. 2022"},
    "Hedervari": {"illum_fraction": 0.013, "cpr_pct_gt1_inside": None, "ground_truth": "NEGATIVE (M3)"},
    "Idelson_L": {"illum_fraction": 0.0964, "cpr_pct_gt1_inside": None, "ground_truth": "NEGATIVE (M3)"},
}

VALIDATION_SITE_IDS = ["LCROSS_Cabeus", "Wiechert", "Faustini", "De_Gerlache", "Haworth", "Shoemaker", "Sverdrup", "Shackleton", "Amundsen", "Hedervari", "Idelson_L"]
CANDIDATE_IDS = ["SP_840980_0797630", "SP_832640_0090770", "SP_830080_0535120", "SP_842420_0421060", "SP_817950_1586580", "SP_819860_1568660", "SP_809570_2454450"]


def main():
    results = {}
    for sid, s in SITES.items():
        r = classify_site(illum_fraction=s["illum_fraction"], cpr_pct_gt1_inside=s["cpr_pct_gt1_inside"])
        r["ground_truth_for_reporting_only"] = s["ground_truth"]  # attached AFTER classification, not an input
        results[sid] = r

    print(f"{'Site':<22} {'Classification':<12} {'Ground truth (NOT an input)'}")
    for sid in VALIDATION_SITE_IDS + CANDIDATE_IDS:
        r = results[sid]
        print(f"{sid:<22} {r['classification']:<12} {r['ground_truth_for_reporting_only']}")

    with open(os.path.join(OUT_DIR, "pm4w_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved: {os.path.join(OUT_DIR, 'pm4w_results.json')}")

    n_ice = sum(1 for r in results.values() if r["classification"] == "ICE")
    n_non_ice = sum(1 for r in results.values() if r["classification"] == "NON_ICE")
    n_unresolved = sum(1 for r in results.values() if r["classification"] == "UNRESOLVED")
    print(f"\nSummary across all {len(results)} sites: ICE={n_ice}  NON_ICE={n_non_ice}  UNRESOLVED={n_unresolved}")
    print("(Every site is UNRESOLVED given current data -- see docs/PM4W_PRISM_IMPLEMENTATION.md for why this is the honest, expected result, not a bug.)")


if __name__ == "__main__":
    main()
