"""
PRISM Track L/M -- final consolidation (PHYSICS_RESULTS.json) and demo-ready
outputs (outputs/demo/). Pulls together every real result already computed by
the other Track scripts in this session -- does not compute anything new,
does not fabricate anything missing. Every field states its source.
"""

import json
import os
import shutil

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OBJ1 = os.path.join(REPO, "outputs", "objective1")
OBJ2 = os.path.join(REPO, "outputs", "objective2")
DEMO = os.path.join(REPO, "outputs", "demo")
os.makedirs(DEMO, exist_ok=True)

CANDIDATE_ID = "SP_840980_0797630"
CAND_LAT, CAND_LON = -84.098, 79.764


def load(path):
    full = os.path.join(REPO, path)
    if os.path.isfile(full):
        return json.load(open(full))
    return None


def main():
    physics_summary = load("outputs/objective1/candidate_physics/candidate_physics_summary.json")
    georef = load("outputs/objective1/candidate_physics/georeferencing_check.json")
    serd_nan = load("outputs/objective1/candidate_physics/serd_nan_analysis.json")
    dop_val = load("outputs/objective1/dop/dop_validation_results.json")
    acquisition_coverage = load("outputs/objective1/dop/acquisition_coverage_candidates.json")
    terrain = load("outputs/objective2/SP_840980_0797630_terrain_stats.json")
    evidence_score = load("outputs/objective1/evidence_score/physics_evidence_score.json")
    iforest = load("outputs/objective1/ml/isolation_forest_results.json")

    result = {
        "candidate_id": CANDIDATE_ID,
        "candidate_coordinate_deg": {"lat": CAND_LAT, "lon": CAND_LON},
        "generated": "2026-08-22, PRISM implementation session",
        "category_legend": "Every block below is labeled CANDIDATE-SPECIFIC or NON-CANDIDATE VALIDATION, per task instruction. Source file is always given.",

        "georeferencing_verification": {
            "category": "CANDIDATE-SPECIFIC",
            "source": "outputs/objective1/candidate_physics/georeferencing_check.json (Track B)",
            "verdict": georef["verdict"] if georef else "NOT RUN",
            "round_trip_error_deg": georef.get("round_trip_max_abs_error_deg") if georef else None,
        },

        "radar_physics": {
            "category": "CANDIDATE-SPECIFIC",
            "source": "outputs/objective1/candidate_physics/candidate_physics_summary.json (Track A), from Y4R L4-MOSAIC + CPR/SERD/T-Ratio L3C-MOSAIC (2025-06-30, 602 contributing acquisitions 2019-09-22 to 2023-10-18)",
            "Pv": physics_summary["pv"]["window"] if physics_summary else None,
            "CPR": physics_summary["cpr"]["window"] if physics_summary else None,
            "SERD": physics_summary["serd"]["window"] if physics_summary else None,
            "T_Ratio": physics_summary["tratio"]["window"] if physics_summary else None,
            "relative_percentiles_in_mosaic": {
                "Pv": physics_summary["pv"]["window_mean_relative_percentile_in_mosaic_overview"] if physics_summary else None,
                "CPR": physics_summary["cpr"]["window_mean_relative_percentile_in_mosaic_overview"] if physics_summary else None,
                "SERD": physics_summary["serd"]["window_mean_relative_percentile_in_mosaic_overview"] if physics_summary else None,
                "T_Ratio": physics_summary["tratio"]["window_mean_relative_percentile_in_mosaic_overview"] if physics_summary else None,
            },
        },

        "serd_nan_investigation": {
            "category": "CANDIDATE-SPECIFIC finding (candidate has 0% SERD NaN) + NON-CANDIDATE full-mosaic characterization",
            "source": "docs/SERD_NAN_ANALYSIS.md, outputs/objective1/candidate_physics/serd_nan_analysis.json (Track F)",
            "candidate_serd_nan_pct": 0.0,
            "global_mosaic_serd_nan_pct": serd_nan["global_stats"]["pct_nan"] if serd_nan else None,
            "verdict": serd_nan["verdict"] if serd_nan else None,
        },

        "dop_pipeline_validation": {
            "category": "NON-CANDIDATE VALIDATION -- 2025-10-25 acquisition does NOT cover the candidate",
            "source": "docs/DOP_VALIDATION_RESULTS.md, outputs/objective1/dop/dop_validation_results.json (Track C)",
            "linear_pol_dop_mean": dop_val["linear_pol_dop"]["mean"] if dop_val else None,
            "hybrid_pol_dop_mean": dop_val["hybrid_pol_dop"]["mean"] if dop_val else None,
            "eigenvalue_purity_whole_window": dop_val.get("eigenvalue_purity_whole_window") if dop_val else None,
            "best_supported_formulation": "linear-pol (HH/VV) Stokes-covariance DOP -- see formula_comparison in the source JSON",
        },

        "candidate_specific_dop": {
            "category": "CANDIDATE-SPECIFIC",
            "status": "BLOCKED",
            "reason": "No acquisition covering the candidate has been confirmed (Track D/E). PRADAN/ISSDC requires authenticated login not attempted per task instruction.",
            "source": "docs/CANDIDATE_ACQUISITION_SELECTION.md, outputs/objective1/dop/acquisition_coverage_candidates.json",
            "n_manifest_acquisitions": acquisition_coverage.get("n_manifest_acquisitions") if acquisition_coverage else None,
            "n_footprint_tested": acquisition_coverage.get("n_footprint_tested") if acquisition_coverage else None,
            "value": None,
        },

        "terrain": {
            "category": "CANDIDATE-SPECIFIC",
            "source": "outputs/objective2/SP_840980_0797630_terrain_stats.json (Track G, real LOLA 20m/px DEM via GDAL /vsicurl/ windowed remote read, no full download)",
            "slope_stats": terrain["slope_stats"] if terrain else None,
            "elevation_stats": terrain["elevation_stats"] if terrain else None,
            "roughness_tri_stats": terrain["roughness_tri_stats"] if terrain else None,
            "threshold_caveat": "Safe(<10)/caution(10-20)/hazard(>=20 deg) thresholds are carried over verbatim from obj2 (1).ipynb, author-flagged as 'crude' -- NOT validated mission thresholds.",
        },

        "psr_info": {
            "category": "CANDIDATE-SPECIFIC",
            "source": "LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL shapefile (LRO/LOLA South Pole PSR catalog)",
            "area_km2": 14.234,
        },

        "physics_evidence_score": {
            "category": "CANDIDATE-SPECIFIC (ranking within PRISM's own 7-candidate shortlist)",
            "source": "outputs/objective1/evidence_score/physics_evidence_score.json (Track I)",
            "score": evidence_score["primary_candidate"]["physics_evidence_score"] if evidence_score else None,
            "rank_of_7": evidence_score["primary_candidate"]["rank_of_7"] if evidence_score else None,
            "note": "NOT a probability of ice. Unweighted mean of min-max-normalized Pv/CPR/T-Ratio interior-surroundings deltas, ranked across the 7-candidate shortlist. SERD and DOP explicitly excluded (see source JSON).",
        },

        "ml_anomaly_score": {
            "category": "CANDIDATE-SPECIFIC ranking, NON-INDEPENDENT features (circularity caveat)",
            "source": "outputs/objective1/ml/isolation_forest_results.json (Track J)",
            "status": "IMPLEMENTED (unsupervised, Isolation Forest, N=336 PSRs)",
            "anomaly_rank": iforest["candidate_result"]["anomaly_rank_of"] if iforest else None,
            "circularity_warning": iforest["circularity_warning"] if iforest else None,
        },

        "cnn_yolo_status": {
            "category": "N/A -- not run",
            "yolov8": "PLANNED / NOT TRAINED",
            "cnn": "PLANNED / NOT TRAINED",
            "source": "src/cnn_yolo_interface.py (Track K)",
        },

        "data_confidence_summary": {
            "radar_physics_Pv_CPR_SERD_TRatio": "HIGH -- real ISRO PDS4 mosaic products, verified georeferencing, reproduces prior independent run to within ~0.01-0.02",
            "candidate_specific_DOP": "NONE -- blocked, not estimated",
            "DOP_pipeline_method": "MODERATE-HIGH -- formulas transcribed verbatim, channel mapping mostly CONFIRMED (HH is LIKELY, weaker fit), no phase/gain calibration applied",
            "terrain": "HIGH -- real NASA LOLA 20m/px DEM, but hazard THRESHOLDS are explicitly unvalidated",
            "physics_evidence_score": "MODERATE -- real inputs, transparent method, but equal-weighting is a documented default, not literature-derived; ranking is only within PRISM's own 7-candidate shortlist",
            "ml_anomaly_score": "LOW-MODERATE -- real Isolation Forest on real data, but features are not independent of the candidate's own selection criterion (circularity caveat)",
        },

        "limitations": [
            "No independent ground-truth ice confirmation exists for this candidate.",
            "Candidate-specific DOP is unavailable -- physics evidence score and ML score do not include any DOP term.",
            "SERD is excluded from the evidence-score sum due to inconsistent (negative) directionality relative to Pv/CPR/T-Ratio, not resolved by any source in this project.",
            "Terrain hazard thresholds are explicitly unvalidated (author-flagged 'crude').",
            "Physics evidence score equal-weighting is a documented default absent a literature-justified weighting scheme.",
            "ML anomaly score uses features that are not independent of the Pv-based candidate selection (circularity caveat, explicitly not claimed as validation).",
        ],
    }

    with open(os.path.join(OBJ1, "PHYSICS_RESULTS.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    print("Wrote", os.path.join(OBJ1, "PHYSICS_RESULTS.json"))

    # =========================== DEMO OUTPUTS ===========================

    # 1. candidate_overview.png <- candidate_locator.png
    src = os.path.join(OBJ1, "candidate_physics", "candidate_locator.png")
    if os.path.isfile(src):
        shutil.copy(src, os.path.join(DEMO, "candidate_overview.png"))

    # 2. candidate_radar_metrics.png -- 4-panel Pv/CPR/SERD/T-Ratio composite
    fig, axes = plt.subplots(1, 4, figsize=(22, 5.5))
    panels = [("pv", "Pv", "viridis", 0, 1), ("cpr", "CPR", "inferno", 0, 1.5),
              ("serd", "SERD", "viridis", 0, 1), ("tratio", "T-Ratio", "plasma", 0, 1)]
    for ax, (key, label, cmap, vmin, vmax) in zip(axes, panels):
        img_path = os.path.join(OBJ1, "candidate_physics", f"candidate_{key}.png")
        if os.path.isfile(img_path):
            img = plt.imread(img_path)
            ax.imshow(img)
            ax.axis("off")
            ax.set_title(label)
    plt.suptitle(f"{CANDIDATE_ID} -- candidate-specific radar metrics (Y4R/L3C-MOSAIC, coordinate-window)")
    plt.tight_layout()
    fig.savefig(os.path.join(DEMO, "candidate_radar_metrics.png"), dpi=130)
    plt.close(fig)

    # 3. candidate_terrain.png <- objective2 composite
    src = os.path.join(OBJ2, f"{CANDIDATE_ID}_terrain_composite.png")
    if os.path.isfile(src):
        shutil.copy(src, os.path.join(DEMO, "candidate_terrain.png"))

    # 4. candidate_dop.png -- NOT generated (no candidate-specific DOP). Instead: dop_validation.png
    src = os.path.join(OBJ1, "dop", "dop_histogram.png")
    if os.path.isfile(src):
        shutil.copy(src, os.path.join(DEMO, "dop_validation.png"))

    # 5. physics_summary.json <- copy of PHYSICS_RESULTS.json
    shutil.copy(os.path.join(OBJ1, "PHYSICS_RESULTS.json"), os.path.join(DEMO, "physics_summary.json"))

    # 6. candidate_evidence_map.png -- bar chart of 7-candidate shortlist physics evidence scores
    if evidence_score:
        rows = evidence_score["shortlist_ranking"]
        ids = [r["PSR_ID"] for r in rows]
        scores = [r["physics_evidence_score"] for r in rows]
        colors = ["crimson" if i == CANDIDATE_ID else "steelblue" for i in ids]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(ids, scores, color=colors)
        ax.set_xlabel("Physics Evidence Score (0-1, relative ranking within shortlist -- NOT a probability of ice)")
        ax.set_title(f"7-candidate shortlist ranking\n(red = primary candidate {CANDIDATE_ID}, rank {evidence_score['primary_candidate']['rank_of_7']} of 7)")
        ax.invert_yaxis()
        fig.tight_layout()
        fig.savefig(os.path.join(DEMO, "candidate_evidence_map.png"), dpi=150)
        plt.close(fig)

    print("Demo outputs written to", DEMO)
    print(sorted(os.listdir(DEMO)))


if __name__ == "__main__":
    main()
