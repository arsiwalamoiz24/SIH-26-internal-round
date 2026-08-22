"""
PRISM Track J -- unsupervised ML feature table + Isolation Forest anomaly
scoring. NO supervised ice classifier is built here -- there are no reliable
ground-truth lunar ice labels anywhere in this project (see
docs/REFERENCE_PROJECT_COMPARISON.md Section 6 for why PRISM does not
replicate the reference repo's supervised approach: it would need an
external, non-target-tile anchor-label dataset PRISM does not have).

Data / sample size: outputs/objective1/candidate_table_overview.csv, 336 PSRs
with any Y4R radar coverage (src/radar_pipeline.py Phase-1 output) -- a real,
substantial sample, large enough for Isolation Forest to be meaningful,
unlike the 7-candidate shortlist or the 1-candidate terrain set.

CIRCULARITY WARNING, addressed explicitly: all available features at this
336-PSR scale are Pv-tier-derived (high_tier_fraction, moderate_plus_fraction
are themselves computed FROM Pv, which is the same metric that produced the
7-candidate shortlist and this candidate's selection in the first place).
This is NOT an independent/complementary feature set in the sense the task
asks for (terrain/thermal/optical would be independent; they do not exist at
this scale in this project). This script does NOT claim the resulting
anomaly ranking "validates" the candidate's Pv-based selection -- an anomaly
found using Pv-derived features cannot independently confirm a Pv-based
selection. It is reported as a PLANNED-SCOPE / LIMITED-INDEPENDENCE result,
not a validation.
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "ml")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_ID = "SP_840980_0797630"
FEATURES = ["area_km2", "px_with_radar_data", "high_tier_fraction", "moderate_plus_fraction"]
RANDOM_STATE = 42


def main():
    df = pd.read_csv(os.path.join(REPO, "outputs", "objective1", "candidate_table_overview.csv"))
    n_rows = len(df)

    X = df[FEATURES].values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    iso = IsolationForest(n_estimators=200, contamination="auto", random_state=RANDOM_STATE)
    iso.fit(Xs)
    # more negative decision_function = more anomalous; flip sign so higher = more anomalous
    anomaly_score = -iso.decision_function(Xs)
    df["anomaly_score"] = anomaly_score
    df["is_anomaly_iforest_label"] = (iso.predict(Xs) == -1)

    df_sorted = df.sort_values("anomaly_score", ascending=False).reset_index(drop=True)
    df_sorted["anomaly_rank"] = np.arange(1, len(df_sorted) + 1)

    cand_row = df_sorted[df_sorted.PSR_ID == CANDIDATE_ID]
    cand_rank = int(cand_row["anomaly_rank"].iloc[0]) if not cand_row.empty else None
    cand_score = float(cand_row["anomaly_score"].iloc[0]) if not cand_row.empty else None
    cand_is_anomaly = bool(cand_row["is_anomaly_iforest_label"].iloc[0]) if not cand_row.empty else None

    result = {
        "purpose": "Track J -- unsupervised Isolation Forest anomaly scoring, feature-table skeleton for future multi-sensor ML.",
        "not_a_supervised_classifier": True,
        "no_ground_truth_labels_used": True,
        "model": "sklearn.ensemble.IsolationForest",
        "hyperparameters": {"n_estimators": 200, "contamination": "auto", "random_state": RANDOM_STATE},
        "n_samples": n_rows,
        "features": FEATURES,
        "circularity_warning": (
            "All 4 features are derived from the same Y4R Pv computation that already produced this "
            "candidate's shortlist ranking (src/radar_pipeline.py). This is NOT an independent evidence "
            "source -- an Isolation Forest anomaly finding here CANNOT be claimed to 'independently "
            "validate' the candidate's Pv-based selection, and this script makes no such claim. It is "
            "included to satisfy the task's request for an ML pipeline skeleton with a real, adequately "
            "sized sample (336 PSRs), not as independent confirmation."
        ),
        "candidate_result": {
            "PSR_ID": CANDIDATE_ID,
            "anomaly_score": cand_score,
            "anomaly_rank_of": f"{cand_rank} of {n_rows}" if cand_rank else None,
            "iforest_anomaly_label": cand_is_anomaly,
        },
        "top_10_anomalies": df_sorted.head(10)[["PSR_ID", "lat", "lon", "area_km2", "anomaly_score", "is_anomaly_iforest_label"]].to_dict(orient="records"),
        "what_would_make_this_independent": (
            "Adding terrain (slope/roughness), thermal (DIVINER-derived max temperature), or optical "
            "(OHRC/TMC brightness) features computed at this same 336-PSR scale would make this a "
            "genuinely independent/complementary feature set, per the task's own guidance. None of "
            "these currently exist at 336-PSR scale in this project -- terrain exists for exactly 1 PSR "
            "(the primary candidate, Track G), and no covering OHRC/thermal data exists for the "
            "candidate at all (PROJECT_STATUS.md Section 3.4)."
        ),
    }

    with open(os.path.join(OUT_DIR, "isolation_forest_results.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)

    df_sorted.to_csv(os.path.join(OUT_DIR, "anomaly_scores_all_psrs.csv"), index=False)

    print(json.dumps(result, indent=2, default=str)[:3000])
    print("\nDone. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
