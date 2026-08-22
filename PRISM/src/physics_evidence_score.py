"""
PRISM Track I -- transparent Physics Evidence Score.

NOT a probability of ice. NOT a validated mission threshold. A normalized,
documented composite of the radar evidence this project actually has,
ranked across the 7-candidate shortlist that the original screening
pipeline already produced (notebooks/objective1_dfsar_validation.ipynb.ipynb),
so "score" means "relative standing within our own shortlist," not an
absolute, literature-calibrated ice probability.

Inputs (all already computed, real, candidate-specific or shortlist-specific
-- nothing here is fabricated):
  - outputs/objective1/shortlist_full_res_comparison.csv (7 PSRs, PSR-interior
    vs local-surroundings means for Pv/CPR/SERD/T-Ratio, from src/radar_pipeline.py)
  - outputs/objective1/candidate_physics/candidate_physics_summary.json
    (coordinate-window version for the primary candidate, Track A)
  - outputs/objective2/SP_840980_0797630_terrain_stats.json (Track G terrain,
    primary candidate only -- terrain is NOT available for the other 6
    shortlist PSRs, so it cannot be part of the 7-way ranking; it is reported
    separately for the primary candidate only)
  - outputs/objective1/dop/dop_validation_results.json (NON-CANDIDATE; DOP is
    explicitly excluded from the score -- no candidate DOP exists)

Method:
  1. For Pv, CPR, T-Ratio: delta_m = mean_inside_PSR - mean_local_surroundings,
     computed identically for all 7 shortlist PSRs (src/radar_pipeline.py
     Phase-1 output, not recomputed here).
  2. Min-max normalize each metric's delta across the 7-candidate shortlist
     to [0, 1] -- this is a RELATIVE ranking within our own known evidence
     set, not an absolute/literature-calibrated threshold (none exists).
  3. Composite radar score = unweighted mean of the 3 normalized deltas.
     Equal weighting is a documented DEFAULT, not a scientifically derived
     weighting scheme -- no literature source in this project justifies any
     other weighting.
  4. SERD is deliberately EXCLUDED from the composite sum: its
     interior-vs-surroundings sign is inconsistent with the "higher=more
     ice-favorable" direction assumed for Pv/CPR/T-Ratio (it is LOWER inside
     the PSR for the primary candidate -- see docs/CANDIDATE_PHYSICS_RESULTS.md
     Section 5) and is not resolved by any source in this project. It is
     reported alongside the score, not silently dropped, but is not summed
     into it.
  5. Terrain (slope hazard, roughness) is reported as a SEPARATE profile for
     the primary candidate only -- it answers a landing-SAFETY question, not
     an ice-EVIDENCE question, and is not combined into the Physics Evidence
     Score to avoid conflating two different physical questions.
"""

import json
import os

import numpy as np
import pandas as pd

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "evidence_score")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_ID = "SP_840980_0797630"


def minmax_norm(series):
    lo, hi = series.min(), series.max()
    if hi - lo < 1e-12:
        return pd.Series(0.5, index=series.index)  # degenerate case: all equal
    return (series - lo) / (hi - lo)


def main():
    df = pd.read_csv(os.path.join(REPO, "outputs", "objective1", "shortlist_full_res_comparison.csv"))

    df["delta_pv"] = df["pv_mean_inside"] - df["pv_mean_outside"]
    df["delta_cpr"] = df["cpr_mean_inside"] - df["cpr_mean_outside"]
    df["delta_tratio"] = df["trt_mean_inside"] - df["trt_mean_outside"]
    df["delta_serd"] = df["srd_mean_inside"] - df["srd_mean_outside"]  # reported, NOT summed

    df["norm_pv"] = minmax_norm(df["delta_pv"])
    df["norm_cpr"] = minmax_norm(df["delta_cpr"])
    df["norm_tratio"] = minmax_norm(df["delta_tratio"])

    df["physics_evidence_score"] = (df["norm_pv"] + df["norm_cpr"] + df["norm_tratio"]) / 3.0
    df["rank"] = df["physics_evidence_score"].rank(ascending=False).astype(int)
    df = df.sort_values("physics_evidence_score", ascending=False)

    ranking_cols = ["PSR_ID", "lat", "lon", "area_km2", "delta_pv", "delta_cpr", "delta_tratio",
                     "delta_serd", "norm_pv", "norm_cpr", "norm_tratio", "physics_evidence_score", "rank"]
    ranking_table = df[ranking_cols].to_dict(orient="records")

    cand_row = df[df.PSR_ID == CANDIDATE_ID].iloc[0]

    # ---- terrain profile (primary candidate only) ----
    terrain_path = os.path.join(REPO, "outputs", "objective2", f"{CANDIDATE_ID}_terrain_stats.json")
    terrain_profile = None
    if os.path.isfile(terrain_path):
        terrain = json.load(open(terrain_path))
        ss = terrain["slope_stats"]
        pia = ss.get("psr_interior_vs_approach", {})
        terrain_profile = {
            "source": "outputs/objective2/SP_840980_0797630_terrain_stats.json (Track G, real LOLA 20m/px DEM, vsicurl windowed read)",
            "slope_mean_deg_whole_window": ss["mean_deg"],
            "pct_hazard_gte20deg_whole_window": ss["pct_hazard_gte20deg"],
            "slope_mean_deg_psr_interior": pia.get("mean_deg_inside_psr"),
            "pct_hazard_gte20deg_psr_interior": pia.get("pct_hazard_gte20deg_inside_psr"),
            "pct_hazard_gte20deg_approach_terrain": pia.get("pct_hazard_gte20deg_outside_psr_in_window"),
            "roughness_tri_mean_m_psr_interior": terrain["roughness_tri_stats"].get("psr_interior_vs_approach", {}).get("mean_tri_m_inside_psr"),
            "threshold_source_caveat": ss["threshold_source"],
            "interpretation": (
                "This is a SAFETY/HAZARD profile, not ice evidence, and is deliberately NOT combined "
                "into the physics_evidence_score above. It is reported honestly even though it is "
                "UNFAVORABLE: 78.6% of the PSR interior itself exceeds the (unvalidated, author-flagged-"
                "as-crude) 20-degree hazard threshold, versus 10.5% of the surrounding approach terrain. "
                "A high radar ice-evidence score does not imply an easy landing site -- these are "
                "independent physical questions."
            ),
        }

    # ---- DOP status ----
    dop_status = {
        "candidate_specific_dop": "BLOCKED -- no acquisition covering the candidate has been confirmed (docs/CANDIDATE_ACQUISITION_SELECTION.md). Excluded from the score entirely, not estimated or substituted.",
        "non_candidate_dop_pipeline_validation": "COMPLETE (docs/DOP_VALIDATION_RESULTS.md) -- validates the computational method only, not usable as candidate evidence.",
    }

    summary = {
        "purpose": "Track I -- transparent, documented Physics Evidence Score. NOT a probability of ice. NOT a validated mission threshold.",
        "candidate_id": CANDIDATE_ID,
        "method": {
            "metrics_used_in_score": ["Pv (interior-surroundings delta)", "CPR (interior-surroundings delta)", "T-Ratio (interior-surroundings delta)"],
            "metrics_reported_but_excluded_from_score": {
                "SERD": "Interior-surroundings delta is NEGATIVE for the primary candidate (lower inside PSR) while Pv/CPR/T-Ratio are positive -- inconsistent directionality that this project's own analysis (docs/CANDIDATE_PHYSICS_RESULTS.md Section 5, PROJECT_STATUS.md Section 1) does not resolve. Reported per-candidate, not summed into the score.",
                "DOP": "No candidate-specific DOP exists (BLOCKED -- see dop_status). Not estimated or substituted.",
            },
            "normalization": "Min-max normalization of each metric's PSR-interior-minus-local-surroundings delta, ACROSS THE 7-CANDIDATE SHORTLIST (not against an absolute/literature threshold, since none was found for this product). This makes the score a RELATIVE ranking within PRISM's own known evidence set, not an absolute ice probability.",
            "weighting": "Unweighted (equal 1/3, 1/3, 1/3) mean of the 3 normalized deltas. This is a DOCUMENTED DEFAULT -- no literature source available to this project justifies a different weighting scheme. If a scientifically justified weighting becomes available, it should replace this default, not be layered on top of it silently.",
            "terrain_and_psr": "PSR membership is a binary precondition already satisfied by construction (all 7 shortlist candidates are LOLA-catalog PSRs). Terrain (slope/roughness) is reported separately for the primary candidate only (Track G) and is NOT combined into this score -- see terrain_profile below and its interpretation note.",
        },
        "shortlist_ranking": ranking_table,
        "primary_candidate": {
            "PSR_ID": CANDIDATE_ID,
            "physics_evidence_score": float(cand_row["physics_evidence_score"]),
            "rank_of_7": int(cand_row["rank"]),
            "delta_serd_excluded_from_score": float(cand_row["delta_serd"]),
            "terrain_profile": terrain_profile,
            "dop_status": dop_status,
        },
        "limitations": [
            "This is a RANKING within a 7-candidate shortlist that PRISM's own screening pipeline already produced -- it is not validated against any independent ice-confirmed site (no LCROSS/M3/MiniRF-style anchor data exists in this project; see docs/REFERENCE_PROJECT_COMPARISON.md Section 6).",
            "Equal-weight normalization is a default, not a derived or literature-calibrated weighting.",
            "SERD and DOP are excluded from the sum for stated, non-arbitrary reasons (directionality inconsistency; data unavailability) -- not because they were unfavorable.",
            "No statistical significance testing was performed on any interior-vs-surroundings delta.",
            "'Physics Evidence Score' is an explicit label choice -- this is NOT called a probability of ice, per task instruction, because no calibration against ground truth exists.",
        ],
    }

    with open(os.path.join(OUT_DIR, "physics_evidence_score.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(json.dumps(summary, indent=2, default=str))
    print("\nDone. Output in", OUT_DIR)


if __name__ == "__main__":
    main()
