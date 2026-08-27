"""
PRISM -- DFSAR Ice Evidence (separate radar layer, NOT PM4W).

Chandrayaan-2 DFSAR is a quad-pol instrument; LRO Mini-RF (PM4W's native
data source, src/pm4w_detector.py) is a hybrid-pol instrument. These are
NOT the same physical measurement, per docs/PM4W_SINHA_PRISM_COMPARISON.md
Sec 2's central finding: "CPR" means three different formulas across
PM4W, Sinha et al. 2026, and PRISM's own ISRO-precomputed band. This
module preserves and reports DFSAR-derived quantities (Sinha's CPR/DOP
formulation, DFSAR DOP, Stokes parameters where genuinely computed,
PRISM's own CPR product, Verma et al. 2025 cross-checks) as their own,
clearly-labeled evidence layer -- DFSAR_ICE_EVIDENCE, never PM4W_ICE_
EVIDENCE, and never averaged, summed, or reconciled with PM4W's output.

Does not modify src/ice_evidence_pipeline_v2.py or src/ice_radar_
characterization_v3.py. This module is a thin, clearly-labeled reporting
wrapper around results those two modules (and the earlier DOP/Sinha
investigation) already established -- no new physics is computed here.
"""

import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "dfsar_ice_evidence")
os.makedirs(OUT_DIR, exist_ok=True)

# Real, already-established DFSAR-side quantities per site. Sources cited
# per field; nothing here is estimated or shared with pm4w_detector.py.
DFSAR_SITES = {
    "SP_840980_0797630": {
        "prism_cpr_L3C_MOSAIC": 0.6303874, "prism_cpr_formula": "ISRO-internal, undocumented (docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md Sec 1-2)",
        "dfsar_dop": 0.680, "dfsar_dop_basis": "quad-pol HH/VV pairing, self-acknowledged non-standard (docs/DOP_SINHA_2026_RESEARCH.md Sec 5.1)",
        "dfsar_dop_meets_sinha_threshold_0p13": False,
        "sinha_cpr_formula_applicable": "Sinha's Eq.1 (power-only sigmaHH/sigmaVV) NOT independently computed for this site -- only PRISM's own L3C-MOSAIC CPR band is available (docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md Sec 2)",
        "verma_cross_check": "Verma et al. 2025's craters (Faustini/Haworth/Shoemaker) do not spatially overlap this candidate (docs/LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md Sec 6.2)",
    },
    "SP_832640_0090770": {"prism_cpr_L3C_MOSAIC": 0.7104936, "dfsar_dop": 0.8410894, "dfsar_dop_meets_sinha_threshold_0p13": False},
    "SP_830080_0535120": {"prism_cpr_L3C_MOSAIC": 0.6684831, "dfsar_dop": 0.6303498, "dfsar_dop_meets_sinha_threshold_0p13": False},
    "SP_842420_0421060": {"prism_cpr_L3C_MOSAIC": 0.5563170, "dfsar_dop": None, "dfsar_dop_meets_sinha_threshold_0p13": None},
    "SP_817950_1586580": {"prism_cpr_L3C_MOSAIC": 0.5183735, "dfsar_dop": None, "dfsar_dop_meets_sinha_threshold_0p13": None},
    "SP_819860_1568660": {"prism_cpr_L3C_MOSAIC": 0.6359729, "dfsar_dop": 0.8270149, "dfsar_dop_meets_sinha_threshold_0p13": False},
    "SP_809570_2454450": {"prism_cpr_L3C_MOSAIC": 0.3954223, "dfsar_dop": None, "dfsar_dop_meets_sinha_threshold_0p13": None},
    "LCROSS_Cabeus": {"prism_cpr_L3C_MOSAIC": 0.1662777, "dfsar_dop": None, "dfsar_dop_meets_sinha_threshold_0p13": None,
                       "note": "Lowest PRISM CPR of all 18 sites tested -- independently consistent with Neish et al. 2011's real Mini-RF finding that Cabeus's CPR sits below the south-polar regional average despite confirmed water (docs/ICE_RADAR_V3_REDESIGN.md Sec 3)."},
    "Wiechert": {"prism_cpr_L3C_MOSAIC": 0.3109077, "dfsar_dop": None, "dfsar_dop_meets_sinha_threshold_0p13": None},
}

PIPELINE_VALIDATION_STOKES_CPR = {
    "note": "Genuine Stokes parameters and Neish-formula CPR WERE computed from real decoded raw DFSAR pixels this investigation -- but only for a non-candidate, northern-hemisphere acquisition (2021-04-14), confirmed not to cover any site above. See src/ice_radar_characterization_v3.py and docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md Sec 5.",
    "hh_vv_basis_neish_cpr": 1.443, "hh_hv_basis_neish_cpr": 0.979, "vh_vv_basis_neish_cpr": 1.017,
    "candidate_relevance": "NONE -- pipeline validation only, reported here for completeness of the DFSAR evidence layer, not as candidate-specific evidence.",
}


def build_dfsar_ice_evidence():
    """Returns the DFSAR_ICE_EVIDENCE structure -- explicitly NOT named or
    treated as PM4W_ICE_EVIDENCE anywhere."""
    out = {"DFSAR_ICE_EVIDENCE": {}}
    for sid, d in DFSAR_SITES.items():
        out["DFSAR_ICE_EVIDENCE"][sid] = {
            **d,
            "sinha_dop_threshold_reproduced": "NO -- unresolved after 8 independent hypotheses, docs/DOP_SINHA_2026_RESEARCH.md. Not forced to match here.",
            "instrument": "Chandrayaan-2 DFSAR (quad-pol)",
            "distinct_from": "PM4W_ICE_EVIDENCE (src/pm4w_detector.py) -- different instrument (Mini-RF, hybrid-pol), different CPR formula, never combined with this layer.",
        }
    out["pipeline_validation_stokes_cpr_non_candidate"] = PIPELINE_VALIDATION_STOKES_CPR
    out["verma_2025_cross_check"] = {
        "access_status": "ScienceDirect fully blocked, two independent investigation attempts -- search-summary confidence only",
        "qualitative_finding_used": "Roughness can explain some CPR>1 occurrences; CPR/DOP reportedly anti-correlate",
        "specific_unverified_number_NOT_used": "R^2~0.99 CPR-DOP correlation figure -- explicitly not cited as fact anywhere in PRISM's codebase or docs",
    }
    return out


def main():
    evidence = build_dfsar_ice_evidence()
    print(json.dumps(evidence, indent=2, default=str))
    with open(os.path.join(OUT_DIR, "dfsar_ice_evidence.json"), "w") as f:
        json.dump(evidence, f, indent=2, default=str)
    print(f"\nSaved: {os.path.join(OUT_DIR, 'dfsar_ice_evidence.json')}")
    print("\nThis output is DFSAR_ICE_EVIDENCE. It is a separate layer from PM4W_ICE_EVIDENCE")
    print("(src/pm4w_detector.py output) and is never combined with it in this task.")


if __name__ == "__main__":
    main()
